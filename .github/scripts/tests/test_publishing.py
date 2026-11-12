"""Publishing drift must fail the member's existing documentation gate."""

from pathlib import Path
import shutil
import tempfile
import unittest
from unittest.mock import patch

import gate


class PublishingDriftTests(unittest.TestCase):
    def setUp(self) -> None:
        self.directory = tempfile.TemporaryDirectory()
        self.addCleanup(self.directory.cleanup)
        self.root = Path(self.directory.name)
        for name in (
            "scripts/gate/identity.py",
            "docs/workflows/record-identity.schema.json",
            "docs/workflows/publishing.md",
            ".github/gnn-pin.json",
        ):
            destination = self.root / name
            destination.parent.mkdir(parents=True, exist_ok=True)
            shutil.copyfile(gate.ROOT / name, destination)

    def check_links(self) -> int:
        with patch.object(gate, "ROOT", self.root), patch.object(
            gate.archive_checks, "run", return_value=(0, [])
        ):
            return gate.arm_archive(("links",), "links")

    def test_matching_artifacts_pass(self) -> None:
        self.assertEqual(self.check_links(), 0)

    def test_changed_artifact_fails_docs_gate(self) -> None:
        for name in (
            "scripts/gate/identity.py",
            "docs/workflows/record-identity.schema.json",
            ".github/gnn-pin.json",
        ):
            with self.subTest(artifact=name):
                path = self.root / name
                original = path.read_bytes()
                try:
                    path.write_bytes(original + b"\n")
                    self.assertEqual(self.check_links(), 1)
                finally:
                    path.write_bytes(original)
