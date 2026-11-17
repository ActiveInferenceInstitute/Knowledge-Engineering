# Quickstart

There is no build step: every artifact in this repository is a data file, a notebook, or a small Python script set. This page covers the three ways to actually use the archive.

## 1. Browse the archive

Clone the repository and open the README contents table:

```bash
git clone https://github.com/ActiveInferenceInstitute/Knowledge-Engineering.git
cd Knowledge-Engineering
```

Browsing committed data/Markdown needs no project Python environment. Offline gate contracts and controlled CSV/text regressions use the standard library. Importing scraper modules can read CWD-relative parameters and import the PDF dependency; a real scraper run also needs its local corpus. The notebook has separate Jupyter, pandas, Biopython, network, and research-policy prerequisites.

## 2. Inspect the historical PubMed notebook

`Literature_Analysis/Pubmed_to_Coda/Pubmed_Query.ipynb` is preserved exploratory source, not a validated current extraction workflow. Inspect it without executing all cells in this checkout: its export cell can overwrite committed `FEP_ActInf.csv`.

Read the [preservation and revival warnings](../Literature_Analysis/Pubmed_to_Coda/README.md) before a separately approved run. Dependencies, an NCBI contact address, and saved inputs do not resolve abstract, author, join, schema, or live/frozen-cohort limitations. The saved 331-record inventory is historical, not a promised rerun result.

Revival requires research-owner decisions on cohort, missing data, complete author extraction, output schema, provenance, and a non-overwriting destination.

## 3. Run the PDF keyword extractor

The tool in `Literature_Analysis/PDF_Scrape/` counts configured keywords in a local PDF corpus and in the recorded abstracts, writing `ft_<keyword>`/`ab_<keyword>` columns per paper.

Requirements: Python 3 and a PDF library compatible with the `pypdf` API (PyPDF2 is accepted as a fallback):

```bash
python -m pip install pypdf
```

The PDF corpus itself is **not committed**. Populate `Literature_Analysis/PDF_Scrape/resc/pdfList/` with files named `00001.pdf`, `00002.pdf`, … matching the `COGSEC_ID` values in `resc/params/fileInfo.csv` (257 records; IDs run 1–300 with gaps).

Then run from the tool directory (paths in the scripts are relative to it):

```bash
cd Literature_Analysis/PDF_Scrape
python manager.py
```

The script requests a callsign only when export configuration is first needed. Importing modules does not start a batch or create exports, but `dataImport.py` reads parameter CSVs during import and the manager imports its PDF-reader dependency. Prepare CWD-relative inputs deliberately.

See the [PDF area guide](../Literature_Analysis/PDF_Scrape/README.md) for normalization, continuation, failure status, CSV logging, and callsign truncation. Controlled regressions do not establish real-corpus or scientific correctness.

## Where outputs land

| Workflow | Output | Location |
| --- | --- | --- |
| PubMed notebook | `FEP_ActInf.csv` | `Literature_Analysis/Pubmed_to_Coda/` |
| PDF keyword extractor | `<callsign>-Results.csv`, `<callsign>-Log.csv` | current working directory at run time |

Ignore rules cover scraper `*-Results.csv`/`*-Log.csv` only under `Literature_Analysis/PDF_Scrape/`, not arbitrary workspaces. PubMed `FEP_ActInf.csv` is tracked historical data; ignore rules do not protect it from overwrite. Use a separate destination for approved new research.
