"""Real scraper batch/CLI/export behavior without a private PDF corpus."""

from __future__ import annotations

import contextlib
import io
import runpy
import sys
import unittest
from pathlib import Path
from unittest import mock

SCRIPTS = Path(__file__).resolve().parents[1]
if str(SCRIPTS) not in sys.path:
    sys.path.insert(0, str(SCRIPTS))

from tests.pdf_fixtures import PdfScraperCase, SCRAPER


class BatchTests(PdfScraperCase):
    def load_three_documents(self) -> None:
        self.load_scraper(
            ["active inference"],
            [
                ("1", "active inference", "Active Inference"),
                ("2", "active inference", "activeinference"),
                ("3", "", "activeinference ACTIVE\nINFERENCE"),
            ],
        )

    def run_cli(self):
        stdout, stderr = io.StringIO(), io.StringIO()
        with (
            mock.patch("builtins.input", return_value="batch"),
            contextlib.redirect_stdout(stdout),
            contextlib.redirect_stderr(stderr),
            self.assertRaises(SystemExit) as raised,
        ):
            runpy.run_path(str(SCRAPER / "manager.py"), run_name="__main__")
        return raised.exception.code, stdout.getvalue(), stderr.getvalue()

    def test_successful_batch_returns_totals_and_preserves_result_columns(self) -> None:
        self.load_scraper(
            ["active inference", "aa"],
            [
                ("1", "Active Inference aa", "ACTIVE\nINFERENCE aaaa"),
                ("2", "activeinference active inference", "aaaa"),
            ],
        )
        totals, _, stderr = self.run_batch()
        self.assert_totals(totals, (2, 2, 0, 0, 0))
        self.assertEqual(stderr, "")
        self.assertEqual(
            self.read_rows("Results"),
            [
                ["FileId", "ft_activeinference", "ft_aa", "ab_activeinference", "ab_aa", ""],
                ["00001", "1", "2", "1", "1", ""],
                ["00002", "0", "2", "2", "0", ""],
            ],
        )
        self.assertEqual(self.read_rows("Log"), [])

    def test_processing_failure_is_one_quoted_record_and_later_documents_run(self) -> None:
        self.load_three_documents()
        message = 'bad input, "quoted"\nnext line\rcafé Ω'
        self.extraction_errors["00002"] = ValueError(message)
        totals, _, stderr = self.run_batch()
        self.assert_totals(totals, (3, 2, 1, 0, 1))
        self.assertEqual(stderr, "")
        self.assertEqual(
            self.read_rows("Results")[1:],
            [["00001", "1", "1", ""], ["00003", "2", "0", ""]],
        )
        self.assertEqual(self.read_rows("Log"), [["00002", "failed", message]])

    def test_failure_log_round_trips_each_csv_separator_and_unicode(self) -> None:
        self.load_scraper(
            ["active inference"],
            [("1", "", "unused after failure"), ("2", "", "active inference")],
        )
        messages = ["comma, detail", 'a "quote"', "\r", "\n", "\r\n", "café Ω", ""]
        for message in messages:
            with self.subTest(message=message):
                self.extraction_errors["00001"] = ValueError(message)
                totals, _, _ = self.run_batch()
                self.assert_totals(totals, (2, 1, 1, 0, 1))
                self.assertEqual(self.read_rows("Log"), [["00001", "failed", message]])
                self.assertEqual(
                    self.read_rows("Results")[1:], [["00002", "1", "0", ""]]
                )

    def test_result_export_failure_is_counted_without_stopping_later_documents(self) -> None:
        self.load_three_documents()
        append = self.export.appendToResultsCsv

        def fail_second_export(row):
            if row.startswith("00002,"):
                raise OSError("result medium unavailable")
            append(row)

        with mock.patch.object(self.export, "appendToResultsCsv", side_effect=fail_second_export):
            totals, _, _ = self.run_batch()
        self.assert_totals(totals, (3, 2, 1, 0, 1))
        self.assertEqual(
            self.read_rows("Results")[1:],
            [["00001", "1", "1", ""], ["00003", "2", "0", ""]],
        )
        self.assertEqual(
            self.read_rows("Log"), [["00002", "failed", "result medium unavailable"]]
        )

    def test_all_missing_documents_fail_but_each_is_attempted_and_logged(self) -> None:
        self.load_scraper(["active inference"], [("1", "", None), ("2", "", None)])
        totals, _, _ = self.run_batch()
        self.assert_totals(totals, (2, 0, 2, 0, 1))
        self.assertEqual(
            self.read_rows("Results"), [["FileId", "ft_activeinference", "ab_activeinference", ""]]
        )
        records = self.read_rows("Log")
        self.assertEqual([row[:2] for row in records], [["00001", "failed"], ["00002", "failed"]])
        self.assertIn("00001.txt", records[0][2])
        self.assertIn("00002.txt", records[1][2])

    def test_failed_failure_log_is_reported_and_does_not_stop_later_documents(self) -> None:
        self.load_scraper(
            ["active inference"], [("1", "", None), ("2", "", "active inference")]
        )
        with mock.patch.object(self.export, "appendToLogCsv", side_effect=OSError("log full")):
            totals, _, stderr = self.run_batch()
        self.assert_totals(totals, (2, 1, 1, 1, 1))
        self.assertEqual(self.read_rows("Results")[1:], [["00002", "1", "0", ""]])
        self.assertEqual(self.read_rows("Log"), [])
        self.assertIn("log full", stderr)
        self.assertIn("00001.txt", stderr)

    def test_unknown_selected_key_fails_without_preventing_a_later_known_key(self) -> None:
        self.load_scraper(["active inference"], [("2", "", "active inference")])
        totals, _, _ = self.run_batch(["missing", "00002"])
        self.assert_totals(totals, (2, 1, 1, 0, 1))
        self.assertEqual(self.read_rows("Results")[1:], [["00002", "1", "0", ""]])
        self.assertEqual(self.read_rows("Log"), [["missing", "failed", "'missing'"]])

    def test_reused_callsign_truncates_prior_results_and_failure_log(self) -> None:
        self.load_three_documents()
        self.extraction_errors["00002"] = ValueError("old failure")
        first, _, _ = self.run_batch(["00001", "00002"])
        self.assert_totals(first, (2, 1, 1, 0, 1))
        self.assertEqual(self.read_rows("Log"), [["00002", "failed", "old failure"]])
        second, _, _ = self.run_batch(["00003"])
        self.assert_totals(second, (1, 1, 0, 0, 0))
        self.assertEqual(self.read_rows("Results")[1:], [["00003", "2", "0", ""]])
        self.assertEqual(self.read_rows("Log"), [])

    def test_empty_batch_truncates_existing_callsign_files_too(self) -> None:
        self.load_three_documents()
        self.extraction_errors["00002"] = ValueError("discarded failure")
        self.run_batch(["00001", "00002"])
        totals, _, _ = self.run_batch([])
        self.assert_totals(totals, (0, 0, 0, 0, 0))
        self.assertEqual(
            self.read_rows("Results"), [["FileId", "ft_activeinference", "ab_activeinference", ""]]
        )
        self.assertEqual(self.read_rows("Log"), [])

    def test_cli_returns_nonzero_after_processing_failure_and_continues(self) -> None:
        self.load_three_documents()
        self.extraction_errors["00002"] = ValueError("controlled CLI failure")
        code, _, _ = self.run_cli()
        self.assertEqual(code, 1)
        self.assertEqual(
            self.read_rows("Results")[1:],
            [["00001", "1", "1", ""], ["00003", "2", "0", ""]],
        )
        self.assertEqual(
            self.read_rows("Log"), [["00002", "failed", "controlled CLI failure"]]
        )

    def test_cli_returns_nonzero_after_result_export_failure(self) -> None:
        self.load_three_documents()
        append = self.export.appendToResultsCsv

        def fail_second_export(row):
            if row.startswith("00002,"):
                raise OSError("controlled CLI export failure")
            append(row)

        with mock.patch.object(self.export, "appendToResultsCsv", side_effect=fail_second_export):
            code, _, _ = self.run_cli()
        self.assertEqual(code, 1)
        self.assertEqual(
            self.read_rows("Results")[1:],
            [["00001", "1", "1", ""], ["00003", "2", "0", ""]],
        )
        self.assertEqual(
            self.read_rows("Log"), [["00002", "failed", "controlled CLI export failure"]]
        )

    def test_cli_success_returns_zero_and_exports_the_document(self) -> None:
        self.load_scraper(["active inference"], [("1", "", "active inference")])
        code, _, stderr = self.run_cli()
        self.assertEqual(code, 0)
        self.assertEqual(stderr, "")
        self.assertEqual(self.read_rows("Results")[1:], [["00001", "1", "0", ""]])
        self.assertEqual(self.read_rows("Log"), [])

    def test_cli_empty_csv_batch_returns_zero_with_header_only_outputs(self) -> None:
        self.load_scraper(["active inference"], [])
        code, _, stderr = self.run_cli()
        self.assertEqual(code, 0)
        self.assertEqual(stderr, "")
        self.assertEqual(
            self.read_rows("Results"), [["FileId", "ft_activeinference", "ab_activeinference", ""]]
        )
        self.assertEqual(self.read_rows("Log"), [])


if __name__ == "__main__":
    unittest.main()
