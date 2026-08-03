# Quickstart

There is no build step: every artifact in this repository is a data file, a notebook, or a small Python script set. This page covers the three ways to actually use the archive.

## 1. Browse the archive

Clone the repository and open the README contents table:

```bash
git clone https://github.com/ActiveInferenceInstitute/Knowledge-Engineering.git
cd Knowledge-Engineering
```

The repository has no runtime dependencies until you run the notebook or the PDF scraper. The data files (CSV, ODS, XLSX, JSON, PNG, ZIP) can be opened directly.

## 2. Run the PubMed query notebook

The notebook in `Literature_Analysis/Pubmed_to_Coda/` queries NCBI Entrez for open-access papers whose title/abstract mentions `free energy principle` or `active inference`, then joins author, title, and DOI metadata and writes `FEP_ActInf.csv`.

Requirements: Python 3, [Jupyter](https://jupyter.org/), `pandas`, and `biopython` (for `Bio.Entrez`).

```bash
python -m pip install pandas biopython jupyter
jupyter notebook Literature_Analysis/Pubmed_to_Coda/Pubmed_Query.ipynb
```

Before running the cells:

1. Replace every `Entrez.email = 'you@email.com'` line with an address NCBI can use to identify your requests (NCBI requires a contact address on E-utilities traffic).
2. Keep `ids.csv` and `PMIDS2.csv` in the notebook's working directory — they are consumed during the join stage.
3. Execute cells in order. The final cell writes `FEP_ActInf.csv` (331 records in the checked-in export).

Notes: PubMed results change over time, so a fresh run will differ from the committed snapshot. Record your query date and any changed filters alongside the new export.

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

The script prompts for a callsign/ID, then writes `<callsign>-Results.csv` and `<callsign>-Log.csv` in the current directory. Importing the modules without running `manager.py` is safe — nothing executes at import time.

Caveats: keyword counting is substring-based after lowercasing and removing spaces, so short terms can match inside larger words; every per-paper failure is recorded in the log with its exception message.

## Where outputs land

| Workflow | Output | Location |
| --- | --- | --- |
| PubMed notebook | `FEP_ActInf.csv` | `Literature_Analysis/Pubmed_to_Coda/` |
| PDF keyword extractor | `<callsign>-Results.csv`, `<callsign>-Log.csv` | current working directory at run time |

Both output files are gitignored so they cannot be committed accidentally.
