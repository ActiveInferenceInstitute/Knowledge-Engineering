"""Verdict tests for the pinned GNN conformance arm.

``GNNTypeChecker.validate_gnn_files`` is tri-state, not boolean: ``True`` when
every file validated, ``2`` when one or more files were invalid or no GNN file
was found, ``False`` on a hard failure. Only ``True`` may pass the arm, so the
arm must refuse ``2`` even though ``2`` is truthy — the regression these tests
pin down, because a truthiness test printed ``"result": "verified"`` for an
invalid model set.

The dependency-free verdict cases explicitly replace source admission and stub
the parser surface. They are not origin/content qualification. The separate
``test_gnn_runtime`` cases exercise the real checked bootstrap and guard.
"""

from __future__ import annotations

import contextlib
import io
import json
import sys
import tempfile
import types
import unittest
from pathlib import Path
from unittest import mock

SCRIPTS = Path(__file__).resolve().parents[1]
ROOT = SCRIPTS.parents[1]
if str(SCRIPTS) not in sys.path:
    sys.path.insert(0, str(SCRIPTS))

import gnn_conformance

PIN = json.loads((ROOT / gnn_conformance.PIN_PATH).read_text(encoding="utf-8"))


class _Parsed:
    """Stand-in for a parsed sketch with no parse errors."""

    parse_errors: list[str] = []


def _stub_modules(
    verdict: object, *, version: str = PIN["tag"].removeprefix("v")
) -> dict[str, object]:
    """Return ``sys.modules`` entries implementing the pinned parser surface."""
    gnn = types.ModuleType("gnn")
    gnn.__version__ = version  # type: ignore[attr-defined]

    parsers = types.ModuleType("gnn.parsers")
    basic = types.ModuleType("gnn.parsers.basic")
    basic.parsed_paths = []  # type: ignore[attr-defined]

    def _parse(path):
        basic.parsed_paths.append(Path(path))  # type: ignore[attr-defined]
        return _Parsed()

    basic.parse_gnn_formal = _parse  # type: ignore[attr-defined]
    basic.validate_gnn_syntax = lambda text, **kwargs: (True, [])  # type: ignore[attr-defined]

    checker_module = types.ModuleType("gnn.type_checker")

    class _Checker:
        """Records the model set it was handed, then returns the verdict."""

        def __init__(self) -> None:
            _Checker.last_calls = self.calls = []

        def validate_gnn_files(self, target_dir, output_dir, *args, **kwargs):
            Path(output_dir).mkdir(parents=True, exist_ok=True)
            self.calls.append(sorted(path.name for path in Path(target_dir).iterdir()))
            return verdict

    _Checker.last_calls = []  # type: ignore[attr-defined]
    checker_module.GNNTypeChecker = _Checker  # type: ignore[attr-defined]

    return {
        "gnn": gnn,
        "gnn.parsers": parsers,
        "gnn.parsers.basic": basic,
        "gnn.type_checker": checker_module,
    }


class TypeCheckVerdictTests(unittest.TestCase):
    """``_check_types`` may pass only on the literal ``True``."""

    def setUp(self) -> None:
        self._temp = tempfile.TemporaryDirectory()
        self.root = Path(self._temp.name).resolve()
        self.sketch = self.root / "m.gnn.md"
        self.sketch.write_text("# sketch\n", encoding="utf-8")

    def tearDown(self) -> None:
        self._temp.cleanup()

    def _run(self, verdict: object) -> None:
        with mock.patch.dict(sys.modules, _stub_modules(verdict)):
            gnn_conformance._check_types([self.sketch])

    def test_true_passes(self) -> None:
        stubs = _stub_modules(True)
        with mock.patch.dict(sys.modules, stubs):
            gnn_conformance._check_types([self.sketch])
        calls = stubs["gnn.type_checker"].GNNTypeChecker.last_calls  # type: ignore[attr-defined]
        self.assertEqual(calls, [["000_m.gnn.md"]])

    def test_two_is_refused_and_named(self) -> None:
        with self.assertRaises(SystemExit) as raised:
            self._run(2)
        self.assertIn("returned 2", str(raised.exception.code))

    def test_false_is_refused_and_named(self) -> None:
        with self.assertRaises(SystemExit) as raised:
            self._run(False)
        self.assertIn("returned False", str(raised.exception.code))

    def test_none_is_refused_and_named(self) -> None:
        with self.assertRaises(SystemExit) as raised:
            self._run(None)
        self.assertIn("returned None", str(raised.exception.code))

    def test_zero_is_refused_and_named(self) -> None:
        with self.assertRaises(SystemExit) as raised:
            self._run(0)
        self.assertIn("returned 0", str(raised.exception.code))

    def test_one_is_refused_and_named(self) -> None:
        with self.assertRaises(SystemExit) as raised:
            self._run(1)
        self.assertIn("returned 1", str(raised.exception.code))


class RunVerdictTests(unittest.TestCase):
    """The arm must not print a ``verified`` receipt for a refused verdict."""

    def setUp(self) -> None:
        self._temp = tempfile.TemporaryDirectory()
        self.root = Path(self._temp.name).resolve()
        pin_path = self.root / gnn_conformance.PIN_PATH
        pin_path.parent.mkdir(parents=True)
        pin_path.write_text(json.dumps(PIN), encoding="utf-8")
        (self.root / "model.gnn.md").write_text("# sketch\n", encoding="utf-8")
        admission = mock.patch.object(
            gnn_conformance.gnn_runtime,
            "qualified_parser",
            side_effect=lambda *args, **kwargs: contextlib.nullcontext(
                {"evidence": "unit-verdict-fixture"}
            ),
        )
        admission.start()
        self.addCleanup(admission.stop)
        inventory = mock.patch.object(
            gnn_conformance,
            "tracked_files",
            return_value=[self.root / "model.gnn.md"],
        )
        self.inventory = inventory.start()
        self.addCleanup(inventory.stop)

    def tearDown(self) -> None:
        self._temp.cleanup()

    def _run(self, verdict: object) -> tuple[int | None, str]:
        stdout, stderr = io.StringIO(), io.StringIO()
        code: int | None = 0
        with mock.patch.dict(sys.modules, _stub_modules(verdict)):
            with contextlib.redirect_stdout(stdout), contextlib.redirect_stderr(stderr):
                code = gnn_conformance.run(self.root)
        return code, stdout.getvalue() + stderr.getvalue()

    def test_invalid_models_fail_the_arm_without_a_receipt(self) -> None:
        with self.assertRaises(SystemExit) as raised:
            self._run(2)
        self.assertIn("returned 2", str(raised.exception.code))

    def test_verified_models_print_the_receipt(self) -> None:
        code, output = self._run(True)
        self.assertEqual(code, 0)
        receipt = json.loads(output.strip().splitlines()[-1])
        self.assertEqual(receipt["result"], "verified")
        self.assertEqual(receipt["source"], "repository")
        self.assertEqual(receipt["models"], 1)
        self.assertEqual(receipt["gnn-version"], PIN["tag"].removeprefix("v"))

    def test_only_sorted_tracked_sketches_are_checked(self) -> None:
        nested = self.root / "models"
        nested.mkdir()
        first = nested / "a.gnn.md"
        last = self.root / "z.gnn.md"
        ignored = self.root / "ignored.gnn.md"
        readme = self.root / "README.md"
        for path in (first, last, ignored, readme):
            path.write_text("# controlled fixture\n", encoding="utf-8")
        self.inventory.return_value = [last, readme, first]
        stubs = _stub_modules(True)
        stdout = io.StringIO()
        with mock.patch.dict(sys.modules, stubs), contextlib.redirect_stdout(stdout):
            code = gnn_conformance.run(self.root)
        receipt = json.loads(stdout.getvalue())
        self.assertEqual(code, 0)
        self.assertEqual(receipt["source"], "repository")
        self.assertEqual(receipt["models"], 2)
        self.assertEqual(
            stubs["gnn.parsers.basic"].parsed_paths,  # type: ignore[attr-defined]
            [first, last],
        )

    def test_untracked_sketch_does_not_prevent_pinned_exemplar(self) -> None:
        self.inventory.return_value = []
        stubs = _stub_modules(True)
        stdout = io.StringIO()
        with (
            mock.patch.dict(sys.modules, stubs),
            mock.patch.object(
                gnn_conformance,
                "_exemplar_bytes",
                return_value=b"# controlled upstream fixture\n",
            ),
            contextlib.redirect_stdout(stdout),
        ):
            code = gnn_conformance.run(self.root)
        receipt = json.loads(stdout.getvalue())
        self.assertEqual(code, 0)
        self.assertEqual(receipt["source"], "pinned-exemplar")
        self.assertEqual(receipt["models"], 1)
        parsed = stubs["gnn.parsers.basic"].parsed_paths  # type: ignore[attr-defined]
        self.assertEqual([path.name for path in parsed], [Path(gnn_conformance.EXEMPLAR_PATH).name])

    def test_inventory_failure_cannot_emit_a_verified_receipt(self) -> None:
        self.inventory.side_effect = OSError("tracked inventory unavailable")
        stdout, stderr = io.StringIO(), io.StringIO()
        with (
            mock.patch.dict(sys.modules, _stub_modules(True)),
            mock.patch.object(
                gnn_conformance,
                "_exemplar_bytes",
                side_effect=AssertionError("must not substitute an exemplar"),
            ),
            contextlib.redirect_stdout(stdout),
            contextlib.redirect_stderr(stderr),
        ):
            code = gnn_conformance.run(self.root)
        self.assertNotEqual(code, 0)
        self.assertEqual(stdout.getvalue(), "")
        self.assertIn("tracked inventory unavailable", stderr.getvalue())

    def test_wrong_version_is_refused_before_parsing(self) -> None:
        stubs = _stub_modules(True, version=PIN["tag"].removeprefix("v") + "-mismatch")
        stdout = io.StringIO()
        with (
            mock.patch.dict(sys.modules, stubs),
            contextlib.redirect_stdout(stdout),
            self.assertRaises(SystemExit) as raised,
        ):
            gnn_conformance.run(self.root)
        self.assertIn("does not match", str(raised.exception.code))
        self.assertEqual(stdout.getvalue(), "")
        self.assertEqual(stubs["gnn.parsers.basic"].parsed_paths, [])  # type: ignore[attr-defined]


if __name__ == "__main__":
    unittest.main()
