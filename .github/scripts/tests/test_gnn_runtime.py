"""Consumer admission regressions; no installed metadata or scientific proof.

The real frozen bootstrap guards a deliberately tiny source fixture. Expected
file bytes are declared before materializing the target; they are not learned
from that target. Only test-local manifest authority is replaced. Installed
success must be accepted separately against real PEP610 metadata by the owner.
"""

from __future__ import annotations

import contextlib
import hashlib
import importlib.abc
import importlib.metadata
import importlib.util
import io
import json
import marshal
import struct
import subprocess
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

import gate
import gnn_conformance
import gnn_runtime

PIN = json.loads((ROOT / gnn_conformance.PIN_PATH).read_text(encoding="utf-8"))


class CheckedBootstrapTests(unittest.TestCase):
    def setUp(self) -> None:
        self.stack = contextlib.ExitStack()
        self.addCleanup(self.stack.close)
        self.root = Path(self.stack.enter_context(tempfile.TemporaryDirectory()))
        self.bootstrap = self.root / "bootstrap.py"
        self.manifest = self.root / "manifest.json"
        self.marker = self.root / "executed.txt"
        self.checked_bytes = b"VALUE = 'checked'\n"
        self.manifest_bytes = b"{}\n"
        self.bootstrap.write_bytes(self.checked_bytes)
        self.manifest.write_bytes(self.manifest_bytes)
        self.stack.enter_context(
            mock.patch.multiple(
                gnn_runtime,
                BOOTSTRAP_PATH=self.bootstrap,
                MANIFEST_PATH=self.manifest,
                BOOTSTRAP_SHA256=hashlib.sha256(self.checked_bytes).hexdigest(),
                MANIFEST_SHA256=hashlib.sha256(self.manifest_bytes).hexdigest(),
            )
        )

    def _malicious_bytes(self) -> bytes:
        return (
            "from pathlib import Path\n"
            f"Path({str(self.marker)!r}).write_text('executed', encoding='utf-8')\n"
            "VALUE = 'unchecked'\n"
        ).encode("utf-8")

    def test_changed_bootstrap_cannot_execute(self) -> None:
        self.bootstrap.write_bytes(self._malicious_bytes())
        with self.assertRaisesRegex(ValueError, "bootstrap-digest-mismatch"):
            with gnn_runtime.checked_bootstrap():
                self.fail("changed bootstrap was admitted")
        self.assertFalse(self.marker.exists())

    def test_manifest_is_bound_before_bootstrap_execution(self) -> None:
        bootstrap_bytes = self._malicious_bytes()
        self.bootstrap.write_bytes(bootstrap_bytes)
        self.manifest.write_bytes(self.manifest_bytes + b" ")
        with mock.patch.object(
            gnn_runtime, "BOOTSTRAP_SHA256", hashlib.sha256(bootstrap_bytes).hexdigest()
        ):
            with self.assertRaisesRegex(ValueError, "manifest-digest-mismatch"):
                with gnn_runtime.checked_bootstrap():
                    self.fail("changed manifest was admitted")
        self.assertFalse(self.marker.exists())

    def test_exec_uses_checked_snapshot_not_a_later_file_read(self) -> None:
        original_read = Path.read_bytes
        reads: list[Path] = []

        def replace_after_read(path: Path) -> bytes:
            value = original_read(path)
            if path == self.bootstrap:
                reads.append(path)
                path.write_bytes(self._malicious_bytes())
            return value

        with mock.patch.object(Path, "read_bytes", replace_after_read):
            with gnn_runtime.checked_bootstrap() as (module, manifest):
                self.assertEqual(module.VALUE, "checked")
                self.assertEqual(manifest, self.manifest_bytes)
        self.assertEqual(reads, [self.bootstrap])
        self.assertFalse(self.marker.exists())


class GuardedCallerTests(unittest.TestCase):
    def setUp(self) -> None:
        self.stack = contextlib.ExitStack()
        self.addCleanup(self.stack.close)
        temporary = Path(self.stack.enter_context(tempfile.TemporaryDirectory()))
        # Restore all test-owned module imports, including after a failed guard.
        self.stack.enter_context(mock.patch.dict(sys.modules))
        self._clear_gnn_modules()
        self.root = temporary / "consumer"
        self.root.mkdir()
        pin_path = self.root / gnn_conformance.PIN_PATH
        pin_path.parent.mkdir()
        pin_path.write_text(json.dumps(PIN), encoding="utf-8")
        self.model = self.root / "model.gnn.md"
        self.model.write_text("# controlled source fixture\n", encoding="utf-8")
        self.package = temporary / "independent" / "src" / "gnn"
        self.import_marker = temporary / "imported.txt"
        self.parse_marker = temporary / "parsed.txt"
        self.attack_marker = temporary / "unchecked.txt"
        version = PIN["tag"].removeprefix("v")
        self.expected_bytes = {
            "__init__.py": (
                "from pathlib import Path\n"
                f"Path({str(self.import_marker)!r}).write_text('imported', encoding='utf-8')\n"
                f"__version__ = {version!r}\n"
            ).encode("utf-8"),
            "parsers/__init__.py": b"",
            "parsers/basic.py": (
                "from pathlib import Path\n"
                "from types import SimpleNamespace\n"
                "def parse_gnn_formal(path):\n"
                f"    Path({str(self.parse_marker)!r}).write_text(Path(path).read_text(encoding='utf-8'), encoding='utf-8')\n"
                "    return SimpleNamespace(parse_errors=[])\n"
                "def validate_gnn_syntax(text):\n"
                "    return True, []\n"
            ).encode("utf-8"),
            "type_checker.py": (
                "class GNNTypeChecker:\n"
                "    def validate_gnn_files(self, model_dir, output_dir):\n"
                "        from gnn.late import ACCEPT\n"
                "        return ACCEPT\n"
            ).encode("utf-8"),
            "late.py": b"ACCEPT = True\n",
            "fixture-data.txt": b"independently declared fixture data\n",
        }
        manifest = {
            "schema": "gnn-importer-source/v1",
            "repository": PIN["repository"],
            "commit": PIN["revision"],
            "files": {
                "src/gnn/" + name: hashlib.sha256(content).hexdigest()
                for name, content in self.expected_bytes.items()
            },
            "verdict_modules": ["gnn", "gnn.parsers.basic", "gnn.type_checker"],
        }
        self.manifest_bytes = (
            json.dumps(manifest, sort_keys=True, separators=(",", ":")) + "\n"
        ).encode("ascii")
        for name, content in self.expected_bytes.items():
            path = self.package / name
            path.parent.mkdir(parents=True, exist_ok=True)
            path.write_bytes(content)
        self.manifest_path = temporary / "trusted-fixture-manifest.json"
        self.manifest_path.write_bytes(self.manifest_bytes)
        self.manifest_sha256 = hashlib.sha256(self.manifest_bytes).hexdigest()
        self.stack.enter_context(
            mock.patch.multiple(
                gnn_runtime,
                MANIFEST_PATH=self.manifest_path,
                MANIFEST_SHA256=self.manifest_sha256,
            )
        )
        self.stack.enter_context(mock.patch.object(gate, "ROOT", self.root))
        self.stack.enter_context(
            mock.patch.object(gnn_conformance, "tracked_files", return_value=[self.model])
        )

    @staticmethod
    def _clear_gnn_modules() -> None:
        for name in tuple(sys.modules):
            if name == "gnn" or name.startswith("gnn."):
                sys.modules.pop(name)

    def _run(self, arguments: list[str]) -> tuple[int, str, str]:
        stdout, stderr = io.StringIO(), io.StringIO()
        with contextlib.redirect_stdout(stdout), contextlib.redirect_stderr(stderr):
            code = gate.main(arguments)
        return code, stdout.getvalue(), stderr.getvalue()

    def _source_arguments(self, arm: str = "gnn") -> list[str]:
        return [arm, "--gnn-source-root", str(self.package)]

    def _assert_qualified_receipt(self, output: str) -> None:
        receipt = json.loads(output)
        self.assertEqual(receipt["result"], "verified")
        self.assertEqual(receipt["source"], "repository")
        self.assertEqual(receipt["pin-revision"], PIN["revision"])
        qualification = receipt["source-qualification"]
        self.assertTrue(qualification["ok"])
        self.assertTrue(qualification["preimport"])
        self.assertTrue(qualification["imports_verified"])
        self.assertFalse(qualification["execution_verified"])
        self.assertEqual(qualification["origin"]["kind"], "explicit-source")
        self.assertFalse(qualification["origin"]["vcs_verified"])
        self.assertEqual(qualification["manifest_sha256"], self.manifest_sha256)
        self.assertTrue(
            {"gnn", "gnn.parsers.basic", "gnn.type_checker", "gnn.late"}.issubset(
                qualification["loaded_modules"]
            )
        )
        self.assertEqual(self.parse_marker.read_bytes(), self.model.read_bytes())

    def test_source_mode_guards_actual_parse_and_delayed_type_imports(self) -> None:
        previous_path = sys.path[:]
        code, stdout, stderr = self._run(self._source_arguments())
        self.assertEqual(code, 0, stderr)
        self._assert_qualified_receipt(stdout)
        self.assertEqual(sys.path, previous_path)

    def test_full_arm_keeps_source_admission_for_its_gnn_execution(self) -> None:
        with (
            mock.patch.object(gate, "arm_archive", return_value=0),
            mock.patch.object(gate, "arm_tests", return_value=0),
        ):
            code, stdout, stderr = self._run(self._source_arguments("full"))
        self.assertEqual(code, 0, stderr)
        self._assert_qualified_receipt(stdout)

    def _measured_child(self, command: list[str], **kwargs) -> subprocess.CompletedProcess:
        # In-process child harness preserves real argument parsing/admission.
        with contextlib.chdir(kwargs["cwd"]):
            code, stdout, stderr = self._run(command[2:])
        return subprocess.CompletedProcess(command, code, stdout, stderr)

    def test_timing_child_uses_explicit_source_and_labels_the_narrower_proof(self) -> None:
        output = self.root / "measurement.md"
        with (
            mock.patch.object(gate, "timings_arms", return_value=()),
            mock.patch.object(gate.subprocess, "run", side_effect=self._measured_child),
        ):
            code, stdout, stderr = self._run(
                ["timings", "--include-gnn", "--gnn-source-root", str(self.package),
                 "--output", str(output)]
            )
        self.assertEqual(code, 0, stderr)
        self.assertTrue(self.parse_marker.exists())
        self.assertIn("With explicit source admission", output.read_text(encoding="utf-8"))
        self.assertIn("not installed-origin proof", stdout)

    def test_timing_resolves_relative_source_before_the_child_changes_cwd(self) -> None:
        output = self.root / "measurement.md"
        with (
            contextlib.chdir(self.package.parent),
            mock.patch.object(gate, "timings_arms", return_value=()),
            mock.patch.object(gate.subprocess, "run", side_effect=self._measured_child),
        ):
            code, stdout, stderr = self._run(
                ["timings", "--include-gnn", "--gnn-source-root", "gnn",
                 "--output", str(output)]
            )
        self.assertEqual(code, 0, stderr)
        self.assertTrue(self.parse_marker.exists())
        self.assertIn("With explicit source admission", stdout)

    def test_refused_timing_preserves_previous_measurement_bytes(self) -> None:
        output = self.root / "measurement.md"
        previous = b"historical measured bytes\n"
        output.write_bytes(previous)
        (self.package / "fixture-data.txt").write_bytes(b"changed\n")
        with (
            mock.patch.object(gate, "timings_arms", return_value=()),
            mock.patch.object(gate.subprocess, "run", side_effect=self._measured_child),
            self.assertRaises(SystemExit),
        ):
            self._run(
                ["timings", "--include-gnn", "--gnn-source-root", str(self.package),
                 "--output", str(output)]
            )
        self.assertEqual(output.read_bytes(), previous)
        self.assertFalse(self.import_marker.exists())

    def test_installed_mode_refuses_missing_origin_without_source_fallback(self) -> None:
        with (
            mock.patch.object(sys, "path", [str(self.package.parent), *sys.path]),
            mock.patch.object(
                importlib.metadata,
                "distribution",
                side_effect=importlib.metadata.PackageNotFoundError(
                    "generalized-notation-notation"
                ),
            ),
        ):
            code, stdout, stderr = self._run(["gnn"])
        self.assertNotEqual(code, 0)
        self.assertEqual(stdout, "")
        self.assertIn("origin", stderr.lower())
        self.assertFalse(self.import_marker.exists())

    def test_installer_success_is_not_installed_origin_admission(self) -> None:
        with (
            mock.patch.object(sys, "path", [str(self.package.parent), *sys.path]),
            mock.patch.object(
                importlib.metadata,
                "distribution",
                side_effect=importlib.metadata.PackageNotFoundError(
                    "generalized-notation-notation"
                ),
            ),
            mock.patch.object(gnn_conformance, "install") as installer,
        ):
            code, stdout, stderr = self._run(["gnn", "--install"])
        self.assertNotEqual(code, 0)
        self.assertEqual(stdout, "")
        self.assertIn("origin", stderr.lower())
        installer.assert_called_once_with(PIN)
        self.assertFalse(self.import_marker.exists())

    def test_ambiguous_pin_identity_is_refused_before_installation(self) -> None:
        payloads = {
            "duplicate": json.dumps(PIN)[:-1]
            + ',"revision":' + json.dumps(PIN["revision"]) + "}",
            "disagreeing": json.dumps({**PIN, "commit": "0" * 40}),
        }
        with mock.patch.object(gnn_conformance, "install") as installer:
            for name, payload in payloads.items():
                with self.subTest(name=name):
                    (self.root / gnn_conformance.PIN_PATH).write_text(
                        payload, encoding="utf-8"
                    )
                    code, stdout, stderr = self._run(["gnn", "--install"])
                    self.assertNotEqual(code, 0)
                    self.assertEqual(stdout, "")
                    self.assertTrue(stderr)
                    installer.assert_not_called()
        self.assertFalse(self.import_marker.exists())

    def test_existing_parser_digest_is_not_waived_by_complete_manifest(self) -> None:
        pin = {
            **PIN,
            "parser_files": {"gnn/parsers/basic.py": "0" * 64},
        }
        (self.root / gnn_conformance.PIN_PATH).write_text(
            json.dumps(pin), encoding="utf-8"
        )
        code, stdout, stderr = self._run(self._source_arguments())
        self.assertNotEqual(code, 0)
        self.assertEqual(stdout, "")
        self.assertIn("parser digest", stderr.lower())
        self.assertFalse(self.import_marker.exists())

    def test_complete_frozen_manifest_is_not_rebuilt_from_the_target(self) -> None:
        with mock.patch.multiple(
            gnn_runtime,
            MANIFEST_PATH=gnn_runtime.ARTIFACTS / "v5.0.3-source-manifest.json",
            MANIFEST_SHA256="17a35bb2114e76a38119128d290d12377cb641652d70788000482366dca0a14a",
        ):
            code, stdout, stderr = self._run(self._source_arguments())
        self.assertNotEqual(code, 0)
        self.assertEqual(stdout, "")
        self.assertIn("inventory", stderr.lower())
        self.assertFalse(self.import_marker.exists())

    def test_missing_extra_and_changed_content_fail_before_target_import(self) -> None:
        for change in ("missing", "extra", "changed"):
            with self.subTest(change=change):
                victim = self.package / "fixture-data.txt"
                extra = self.package / "unexpected.txt"
                try:
                    if change == "missing":
                        victim.unlink()
                    elif change == "extra":
                        extra.write_bytes(b"unexpected\n")
                    else:
                        victim.write_bytes(b"changed\n")
                    code, stdout, stderr = self._run(self._source_arguments())
                    self.assertNotEqual(code, 0)
                    self.assertEqual(stdout, "")
                    self.assertIn("inventory", stderr.lower())
                    self.assertFalse(self.import_marker.exists())
                finally:
                    victim.write_bytes(self.expected_bytes["fixture-data.txt"])
                    extra.unlink(missing_ok=True)

    def test_foreign_resolution_is_refused_before_either_package_executes(self) -> None:
        foreign = self.root / "foreign" / "gnn"
        foreign.mkdir(parents=True)
        foreign_init = foreign / "__init__.py"
        foreign_init.write_text(
            f"from pathlib import Path\nPath({str(self.attack_marker)!r}).write_text('foreign')\n",
            encoding="utf-8",
        )

        class ForeignFinder(importlib.abc.MetaPathFinder):
            def find_spec(self, fullname, path=None, target=None):
                if fullname == "gnn":
                    return importlib.util.spec_from_file_location(
                        fullname, foreign_init, submodule_search_locations=[str(foreign)]
                    )
                return None

        before = sys.path[:]
        with mock.patch.object(sys, "meta_path", [ForeignFinder(), *sys.meta_path]):
            code, stdout, stderr = self._run(self._source_arguments())
        self.assertNotEqual(code, 0)
        self.assertEqual(stdout, "")
        self.assertIn("different GNN package root", stderr)
        self.assertFalse(self.import_marker.exists())
        self.assertFalse(self.attack_marker.exists())
        self.assertEqual(sys.path, before)

    def test_delayed_import_drift_cannot_execute_or_emit_verified(self) -> None:
        original = gnn_conformance._check_types

        def replace_before_type_check(sketches: list[Path]) -> None:
            (self.package / "late.py").write_text(
                f"from pathlib import Path\nPath({str(self.attack_marker)!r}).write_text('unchecked')\nACCEPT = True\n",
                encoding="utf-8",
            )
            original(sketches)

        with mock.patch.object(
            gnn_conformance, "_check_types", side_effect=replace_before_type_check
        ):
            code, stdout, stderr = self._run(self._source_arguments())
        self.assertNotEqual(code, 0)
        self.assertEqual(stdout, "")
        self.assertTrue(stderr)
        self.assertFalse(self.attack_marker.exists())

    def test_final_guard_refusal_cannot_escape_as_a_verified_receipt(self) -> None:
        original = gnn_conformance._check_types

        def change_after_verdict(sketches: list[Path]) -> None:
            original(sketches)
            (self.package / "fixture-data.txt").write_bytes(b"changed after verdict\n")

        with mock.patch.object(
            gnn_conformance, "_check_types", side_effect=change_after_verdict
        ):
            code, stdout, stderr = self._run(self._source_arguments())
        self.assertNotEqual(code, 0)
        self.assertEqual(stdout, "")
        self.assertTrue(self.parse_marker.exists())
        self.assertTrue(stderr)

    def test_cached_bytecode_cannot_replace_checked_package_source(self) -> None:
        source = self.package / "__init__.py"
        cache = Path(importlib.util.cache_from_source(str(source)))
        cache.parent.mkdir()
        attack = compile(
            f"from pathlib import Path\nPath({str(self.attack_marker)!r}).write_text('cached')\n__version__ = '5.0.3'\n",
            str(source), "exec",
        )
        stat = source.stat()
        cache.write_bytes(
            importlib.util.MAGIC_NUMBER
            + struct.pack("<III", 0, int(stat.st_mtime) & 0xFFFFFFFF, stat.st_size)
            + marshal.dumps(attack)
        )
        code, stdout, stderr = self._run(self._source_arguments())
        self.assertEqual(code, 0, stderr)
        self._assert_qualified_receipt(stdout)
        self.assertTrue(self.import_marker.exists())
        self.assertFalse(self.attack_marker.exists())

    def test_bad_authority_and_unapproved_pin_precede_any_installation(self) -> None:
        with mock.patch.object(gnn_conformance, "install") as installer:
            self.manifest_path.write_bytes(self.manifest_bytes + b" ")
            code, stdout, stderr = self._run(["gnn", "--install"])
            self.assertNotEqual(code, 0)
            self.assertEqual(stdout, "")
            self.assertIn("manifest-digest-mismatch", stderr)
            installer.assert_not_called()
            self.manifest_path.write_bytes(self.manifest_bytes)
            pin = {**PIN, "tag": "v5.1.0", "revision": "75c834bd8519dc7b5adc4d24f16bf393cfd1ecdf"}
            (self.root / gnn_conformance.PIN_PATH).write_text(json.dumps(pin), encoding="utf-8")
            code, stdout, stderr = self._run(["gnn", "--install"])
            self.assertNotEqual(code, 0)
            self.assertEqual(stdout, "")
            self.assertIn("no independently approved source manifest", stderr)
            installer.assert_not_called()
        self.assertFalse(self.import_marker.exists())

    def test_preloaded_package_cannot_trigger_installation_or_requalification(self) -> None:
        with (
            mock.patch.dict(sys.modules, {"gnn": types.ModuleType("gnn")}),
            mock.patch.object(gnn_conformance, "install") as installer,
        ):
            code, stdout, stderr = self._run(["gnn", "--install"])
        self.assertNotEqual(code, 0)
        self.assertEqual(stdout, "")
        self.assertIn("fresh", stderr)
        installer.assert_not_called()
        self.assertFalse(self.import_marker.exists())

    def test_stale_pin_argument_is_refused_before_installation(self) -> None:
        changed = {**PIN, "recorded": "2026-11-13"}
        (self.root / gnn_conformance.PIN_PATH).write_text(json.dumps(changed), encoding="utf-8")
        with mock.patch.object(gnn_conformance, "install") as installer:
            with self.assertRaisesRegex(ValueError, "pin changed"):
                gnn_conformance.verify(self.root, PIN, install_first=True)
            installer.assert_not_called()
        self.assertFalse(self.import_marker.exists())

    def test_missing_tracked_model_is_not_replaced_by_an_exemplar(self) -> None:
        self.model.unlink()
        with mock.patch.object(
            gnn_conformance,
            "_exemplar_bytes",
            side_effect=AssertionError("must not replace a tracked model"),
        ):
            code, stdout, stderr = self._run(self._source_arguments())
        self.assertNotEqual(code, 0)
        self.assertEqual(stdout, "")
        self.assertTrue(stderr)

    def test_source_install_and_non_gnn_selections_have_no_execution_effects(self) -> None:
        selections = [
            [*self._source_arguments(), "--install"],
            self._source_arguments("fast"),
            self._source_arguments("tests"),
            self._source_arguments("timings"),
        ]
        with (
            mock.patch.object(gnn_conformance, "install") as installer,
            mock.patch.object(gate, "arm_archive", side_effect=AssertionError("unexpected arm")),
            mock.patch.object(gate, "arm_tests", side_effect=AssertionError("unexpected tests")),
        ):
            for arguments in selections:
                with self.subTest(arguments=arguments):
                    code, stdout, stderr = self._run(arguments)
                    self.assertEqual(code, 2)
                    self.assertEqual(stdout, "")
                    self.assertTrue(stderr)
            installer.assert_not_called()
        self.assertFalse(self.import_marker.exists())


if __name__ == "__main__":
    unittest.main()
