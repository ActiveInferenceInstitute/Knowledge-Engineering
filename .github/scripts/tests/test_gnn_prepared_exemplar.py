"""Acquisition-boundary fixtures, not installed-parser or scientific proof."""
from __future__ import annotations

import hashlib
import io
import json
import os
import tempfile
import unittest
from pathlib import Path
from unittest import mock

import gnn_conformance

PIN = json.loads(
    (Path(__file__).resolve().parents[2] / "gnn-pin.json").read_text(encoding="utf-8")
)


class PreparedExemplarTests(unittest.TestCase):
    def setUp(self) -> None:
        temporary = tempfile.TemporaryDirectory()
        self.addCleanup(temporary.cleanup)
        self.directory = Path(temporary.name)
        self.path = self.directory / "static_perception.md"
        self.data = b"controlled acquisition-boundary bytes\n"
        self.path.write_bytes(self.data)
        digest = mock.patch.object(
            gnn_conformance, "EXEMPLAR_SHA256", hashlib.sha256(self.data).hexdigest()
        )
        digest.start()
        self.addCleanup(digest.stop)
        environment = mock.patch.dict(os.environ, {}, clear=True)
        environment.start()
        self.addCleanup(environment.stop)
        network = mock.patch.object(gnn_conformance.urllib.request, "urlopen")
        self.network = network.start()
        self.addCleanup(network.stop)

    def read_prepared(self, path: Path | str) -> bytes:
        with mock.patch.dict(os.environ, {"GNN_PREPARED_EXEMPLAR": str(path)}):
            return gnn_conformance._exemplar_bytes(PIN)

    def test_prepared_exact_bytes_need_no_network(self) -> None:
        self.assertEqual(self.read_prepared(self.path), self.data)
        self.network.assert_not_called()

    def test_changed_prepared_bytes_refuse_without_download_fallback(self) -> None:
        self.path.write_bytes(self.data + b"drift")
        with self.assertRaisesRegex(ValueError, "digest mismatch"):
            self.read_prepared(self.path)
        self.network.assert_not_called()

    def test_missing_prepared_path_refuses_without_download_fallback(self) -> None:
        with self.assertRaisesRegex(ValueError, "ordinary existing file"):
            self.read_prepared(self.directory / "missing.md")
        self.network.assert_not_called()

    def test_empty_prepared_selector_is_not_network_selection(self) -> None:
        with self.assertRaisesRegex(ValueError, "must name"):
            self.read_prepared("")
        self.network.assert_not_called()

    def test_prepared_symlink_is_refused(self) -> None:
        link = self.directory / "linked.md"
        link.symlink_to(self.path)
        with self.assertRaisesRegex(ValueError, "ordinary existing file"):
            self.read_prepared(link)
        self.network.assert_not_called()

    def test_unapproved_revision_cannot_reuse_exemplar_authority(self) -> None:
        with self.assertRaisesRegex(ValueError, "no independently frozen"):
            gnn_conformance._exemplar_bytes(dict(PIN, revision="0" * 40))
        self.network.assert_not_called()

    def test_default_download_retains_exact_upstream_url_and_bytes(self) -> None:
        self.network.return_value = io.BytesIO(self.data)
        self.assertEqual(gnn_conformance._exemplar_bytes(PIN), self.data)
        self.network.assert_called_once_with(
            "https://raw.githubusercontent.com/"
            f"{PIN['repository']}/{PIN['revision']}/{gnn_conformance.EXEMPLAR_PATH}",
            timeout=gnn_conformance.FETCH_TIMEOUT,
        )

    def test_changed_download_is_not_a_verified_exemplar(self) -> None:
        self.network.return_value = io.BytesIO(self.data + b"drift")
        with self.assertRaisesRegex(ValueError, "digest mismatch"):
            gnn_conformance._exemplar_bytes(PIN)


if __name__ == "__main__":
    unittest.main()
