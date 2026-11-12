"""Tests for the repository gate.

These exercise the checkers against synthetic trees, so a green run means the
gate still catches the failures its documentation names. They run as the
`tests` arm and as part of `fast`.
"""

from __future__ import annotations

import json
import sys
import tempfile
import unittest
from pathlib import Path

SCRIPTS = Path(__file__).resolve().parents[1]
ROOT = SCRIPTS.parents[1]
if str(SCRIPTS) not in sys.path:
    sys.path.insert(0, str(SCRIPTS))

import archive_checks
import gate
import gnn_conformance


class TreeCase(unittest.TestCase):
    """Base case providing a throwaway repository root."""

    def setUp(self) -> None:
        self._temp = tempfile.TemporaryDirectory()
        self.root = Path(self._temp.name).resolve()

    def tearDown(self) -> None:
        self._temp.cleanup()

    def write(self, relative: str, text: str) -> Path:
        path = self.root / relative
        path.parent.mkdir(parents=True, exist_ok=True)
        path.write_text(text, encoding="utf-8")
        return path


class LinkTargetTests(unittest.TestCase):
    def test_bare_path(self) -> None:
        self.assertEqual(archive_checks.link_target("docs/a.md"), "docs/a.md")

    def test_angle_brackets_and_title(self) -> None:
        self.assertEqual(
            archive_checks.link_target("<docs/a b.md> \"a title\""), "docs/a b.md"
        )

    def test_title_is_dropped(self) -> None:
        self.assertEqual(archive_checks.link_target('a.md "title"'), "a.md")


class LinkCheckTests(TreeCase):
    def test_resolving_and_ignored_targets(self) -> None:
        self.write("docs/target.md", "# target\n")
        page = self.write(
            "docs/page.md",
            "[ok](target.md)\n"
            "[fragment](target.md#section)\n"
            "[anchor](#section)\n"
            "[external](https://example.org/x)\n"
            "[mail](mailto:a@example.org)\n",
        )
        self.assertEqual(archive_checks.check_links([page], self.root), [])

    def test_missing_target_is_reported(self) -> None:
        page = self.write("docs/page.md", "[gone](does-not-exist.md)\n")
        errors = archive_checks.check_links([page], self.root)
        self.assertEqual(len(errors), 1)
        self.assertIn("docs/page.md: missing link target: does-not-exist.md", errors[0])

    def test_escaping_target_is_reported(self) -> None:
        outside = self.root.parent / f"{self.root.name}-outside.md"
        outside.write_text("# outside\n", encoding="utf-8")
        try:
            page = self.write("page.md", "[out](../outside.md)\n")
            errors = archive_checks.check_links([page], self.root)
            self.assertEqual(len(errors), 1)
            self.assertIn("link escapes repository", errors[0])
        finally:
            outside.unlink()

    def test_reference_definition_below_first_line_is_checked(self) -> None:
        page = self.write(
            "docs/page.md",
            "# Guide\n"
            "\n"
            "See [the appendix][appendix].\n"
            "\n"
            "[appendix]: missing.md\n",
        )
        errors = archive_checks.check_links([page], self.root)
        self.assertEqual(len(errors), 1)
        self.assertIn("docs/page.md: missing link target: missing.md", errors[0])

    def test_resolving_reference_definition_passes(self) -> None:
        self.write("docs/appendix.md", "# appendix\n")
        page = self.write(
            "docs/page.md",
            "# Guide\n"
            "\n"
            "See [the appendix][appendix].\n"
            "\n"
            "[appendix]: appendix.md\n",
        )
        self.assertEqual(archive_checks.check_links([page], self.root), [])

    def test_non_markdown_files_are_skipped(self) -> None:
        script = self.write("docs/note.txt", "[gone](does-not-exist.md)\n")
        self.assertEqual(archive_checks.check_links([script], self.root), [])


class PythonCheckTests(TreeCase):
    def test_valid_and_invalid_sources(self) -> None:
        good = self.write("a.py", "def ok() -> int:\n    return 1\n")
        bad = self.write("b.py", "def broken(:\n")
        errors = archive_checks.check_python([good, bad], self.root)
        self.assertEqual(len(errors), 1)
        self.assertIn("b.py: Python syntax error", errors[0])


class NotebookCheckTests(TreeCase):
    def test_output_free_notebook_passes(self) -> None:
        notebook = self.write(
            "n.ipynb",
            json.dumps({"cells": [{"cell_type": "code", "outputs": []}], "nbformat": 4}),
        )
        self.assertEqual(archive_checks.check_notebooks([notebook], self.root), [])

    def test_committed_outputs_are_reported(self) -> None:
        notebook = self.write(
            "n.ipynb",
            json.dumps({"cells": [{"cell_type": "code", "outputs": [{"a": 1}]}]}),
        )
        errors = archive_checks.check_notebooks([notebook], self.root)
        self.assertEqual(len(errors), 1)
        self.assertIn("cell 0 carries committed outputs", errors[0])

    def test_invalid_json_is_reported(self) -> None:
        notebook = self.write("n.ipynb", "{not json")
        errors = archive_checks.check_notebooks([notebook], self.root)
        self.assertEqual(len(errors), 1)
        self.assertIn("invalid notebook JSON", errors[0])


class CheckpointCheckTests(TreeCase):
    def test_nested_checkpoint_is_reported(self) -> None:
        tracked = [
            self.write("a/.ipynb_checkpoints/n-checkpoint.ipynb", "{}"),
            self.write("b/n.ipynb", "{}"),
        ]
        errors = archive_checks.check_checkpoints(tracked, self.root)
        self.assertEqual(len(errors), 1)
        self.assertIn("a/.ipynb_checkpoints/n-checkpoint.ipynb", errors[0])


class PinTests(unittest.TestCase):
    def test_repository_pin_satisfies_the_contract(self) -> None:
        pin = gnn_conformance.load_pin(ROOT)
        self.assertEqual(gnn_conformance.validate_pin(pin), [])
        self.assertTrue(gnn_conformance.REVISION.match(pin["revision"]))
        self.assertIn(
            f"git+https://github.com/{pin['repository']}.git@{pin['revision']}",
            gnn_conformance.install_spec(pin),
        )

    def test_broken_pins_are_rejected(self) -> None:
        pin = gnn_conformance.load_pin(ROOT)
        cases = {
            "schema": {**pin, "schema": "gnn-importer-pin/v2"},
            "repository": {**pin, "repository": "someone/else"},
            "tag": {**pin, "tag": "5.0.3"},
            "revision": {**pin, "revision": pin["revision"][:12]},
            "recorded": {**pin, "recorded": "12-11-2026"},
        }
        for field, broken in cases.items():
            with self.subTest(field=field):
                self.assertTrue(
                    any(field in error for error in gnn_conformance.validate_pin(broken)),
                    f"{field} mutation was accepted",
                )


class CommandContractTests(unittest.TestCase):
    """CI must invoke the same commands the documentation names."""

    def test_workflow_calls_the_documented_arms(self) -> None:
        workflow = (ROOT / ".github" / "workflows" / "ci.yml").read_text(encoding="utf-8")
        self.assertIn(gate.command_for("fast"), workflow)
        self.assertIn(f"{gate.command_for('gnn')} --install", workflow)

    def test_every_arm_has_a_description_and_command(self) -> None:
        self.assertEqual(set(gate.ARM_ORDER), set(gate.DESCRIPTIONS))
        for arm in gate.ARM_ORDER:
            self.assertTrue(gate.command_for(arm).startswith("python .github/scripts/"))

    def test_timings_page_lists_every_measured_arm(self) -> None:
        page = ROOT / gate.TIMINGS_DOC
        self.assertTrue(page.is_file(), f"{gate.TIMINGS_DOC} is missing")
        text = page.read_text(encoding="utf-8")
        self.assertIn(gate.TIMINGS_MARKER, text)
        for arm in gate.timings_arms():
            self.assertIn(f"| `{arm}` | `{gate.command_for(arm)}` |", text)
        self.assertNotIn(f"| `gnn` | `{gate.command_for('gnn')}` |", text)


if __name__ == "__main__":
    unittest.main()
