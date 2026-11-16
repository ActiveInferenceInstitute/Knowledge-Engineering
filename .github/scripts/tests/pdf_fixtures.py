"""Isolated CSV/text fixtures for the historical scraper's real local modules.

Only PDF extraction is replaced: a local module reads controlled UTF-8 text
beside the expected PDF path. These tests do not establish PDF-parser or
scientific-corpus correctness and do not require either dependency.
"""

from __future__ import annotations

import contextlib
import csv
import importlib
import io
import sys
import tempfile
import types
import unittest
from pathlib import Path
from unittest import mock

ROOT = Path(__file__).resolve().parents[3]
SCRAPER = ROOT / "Literature_Analysis" / "PDF_Scrape"


class PdfScraperCase(unittest.TestCase):
    """Restore CWD, import paths, and imported modules after every fixture."""

    def setUp(self) -> None:
        self.stack = contextlib.ExitStack()
        self.addCleanup(self.stack.close)
        self.root = Path(self.stack.enter_context(tempfile.TemporaryDirectory())).resolve()
        self.stack.enter_context(contextlib.chdir(self.root))
        self.stack.enter_context(mock.patch.object(sys, "path", [str(SCRAPER), *sys.path]))
        self.stack.enter_context(mock.patch.dict(sys.modules))
        for name in ("dataImport", "docResults", "streamingExport", "manager"):
            sys.modules.pop(name, None)
        self.extraction_errors: dict[str, Exception] = {}
        reader = types.ModuleType("pdfReader")
        reader.extractPDFtext = self.extract_text  # type: ignore[attr-defined]
        sys.modules["pdfReader"] = reader

    def extract_text(self, file_path: str) -> str:
        path = Path(file_path)
        if path.stem in self.extraction_errors:
            raise self.extraction_errors[path.stem]
        return path.with_suffix(".txt").read_text(encoding="utf-8")

    def load_scraper(
        self,
        keywords: list[str],
        documents: list[tuple[str, str, str | None]],
    ) -> None:
        """Load real parameter CSVs; each document is (ID, abstract, text)."""
        params = self.root / "resc" / "params"
        params.mkdir(parents=True)
        corpus = self.root / "resc" / "pdfList"
        corpus.mkdir()
        with (params / "keywords.csv").open("w", encoding="utf-8", newline="") as stream:
            writer = csv.writer(stream)
            writer.writerow(["Kw"])
            writer.writerows([[keyword] for keyword in keywords])
        with (params / "fileInfo.csv").open("w", encoding="utf-8", newline="") as stream:
            writer = csv.writer(stream)
            writer.writerow(["COGSEC_ID", "Title", "Abstract"])
            for file_id, abstract, text in documents:
                writer.writerow([file_id, f"Controlled document {file_id}", abstract])
                if text is not None:
                    (corpus / f"{file_id.zfill(5)}.txt").write_text(text, encoding="utf-8")
        self.data_import = importlib.import_module("dataImport")
        self.doc_results = importlib.import_module("docResults")
        self.export = importlib.import_module("streamingExport")
        self.manager = importlib.import_module("manager")

    def read_rows(self, kind: str) -> list[list[str]]:
        with (self.root / f"batch-{kind}.csv").open(
            encoding="utf-8", newline=""
        ) as stream:
            return list(csv.reader(stream))

    def run_batch(self, keys: list[str] | None = None):
        self.export.setExportId("batch")
        manager = self.manager.mrManager()
        if keys is None:
            manager.getKeys()
        else:
            manager.giveKeys(keys)
        stdout, stderr = io.StringIO(), io.StringIO()
        with contextlib.redirect_stdout(stdout), contextlib.redirect_stderr(stderr):
            totals = manager.run()
        return totals, stdout.getvalue(), stderr.getvalue()

    def assert_totals(self, totals, expected: tuple[int, int, int, int, int]) -> None:
        self.assertEqual(
            (
                totals.attempted,
                totals.succeeded,
                totals.failed,
                totals.log_failures,
                totals.exit_code,
            ),
            expected,
        )
