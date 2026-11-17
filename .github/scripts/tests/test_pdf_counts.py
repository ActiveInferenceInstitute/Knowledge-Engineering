"""Keyword/count/export contracts with controlled CSV and extracted-text inputs."""

from __future__ import annotations

import csv
import sys
import unittest
from pathlib import Path
from unittest import mock

SCRIPTS = Path(__file__).resolve().parents[1]
if str(SCRIPTS) not in sys.path:
    sys.path.insert(0, str(SCRIPTS))

from tests.pdf_fixtures import PdfScraperCase


class KeywordCountTests(PdfScraperCase):
    def result_row(self, file_id: str = "00007") -> list[str]:
        result = self.doc_results.docResults(self.data_import.FileInfoList[file_id])
        return next(csv.reader([result.toCSV()]))

    def test_multiword_keywords_and_both_sources_share_normalization(self) -> None:
        self.load_scraper(
            ["Ac tive\nInference", "Inference"],
            [
                (
                    "7",
                    "active inference ACTIVE\nINFERENCE activeinference",
                    "ACTIVE INFERENCE active\ninference activeinference",
                )
            ],
        )
        self.assertEqual(self.result_row(), ["00007", "3", "3", "3", "3", ""])

    def test_substrings_remain_case_insensitive_and_nonoverlapping(self) -> None:
        text = "aAaAa BANANA preINFERENCEpost"
        self.load_scraper(["aa", "ana", "Inference"], [("7", text, text)])
        self.assertEqual(
            self.result_row(), ["00007", "2", "1", "1", "2", "1", "1", ""]
        )

    def test_tabs_punctuation_and_unicode_keep_historical_character_semantics(self) -> None:
        text = "active\tinference active-inference active inference STRASSE Straße"
        self.load_scraper(["Active Inference", "Straße"], [("7", text, text)])
        self.assertEqual(self.result_row(), ["00007", "1", "1", "1", "1", ""])

    def test_empty_full_text_and_abstract_export_zero_counts(self) -> None:
        self.load_scraper(["active inference", "aa"], [("7", "", "")])
        self.assertEqual(self.result_row(), ["00007", "0", "0", "0", "0", ""])

    def test_normalized_duplicates_preserve_first_column_order_and_csv_shape(self) -> None:
        self.load_scraper(
            ["Beta term", "Active Inference", "BETA TERM", "aa"],
            [("7", "aa Beta term", "Active Inference beta term beta term aaaa")],
        )
        self.assertEqual(
            next(csv.reader([self.data_import.outputFileHeader])),
            [
                "FileId",
                "ft_betaterm",
                "ft_activeinference",
                "ft_aa",
                "ab_betaterm",
                "ab_activeinference",
                "ab_aa",
                "",
            ],
        )
        self.assertEqual(
            self.result_row(), ["00007", "2", "1", "2", "1", "0", "1", ""]
        )

    def test_import_reads_parameters_without_prompting_or_creating_exports(self) -> None:
        with mock.patch("builtins.input", side_effect=AssertionError("unexpected prompt")):
            self.load_scraper(["active inference"], [("7", "abstract fixture", "text")])
        self.assertEqual(self.data_import.FileInfoList["00007"].abstract, "abstract fixture")
        self.assertEqual(list(self.data_import.KwList), ["activeinference"])
        self.assertEqual(list(self.root.glob("*-Results.csv")), [])
        self.assertEqual(list(self.root.glob("*-Log.csv")), [])


if __name__ == "__main__":
    unittest.main()
