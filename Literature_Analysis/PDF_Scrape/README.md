# PDF_Scrape

Exploratory Python tooling that counts configured keywords in a local PDF corpus and in the corresponding abstracts from `resc/params/fileInfo.csv`.

## Inputs

- `resc/params/keywords.csv` — 331 keyword rows under `Kw`. `dataImport.normalizeText()` lowercases and removes literal ASCII spaces and newline characters from keywords, full text, and abstracts. Each text is normalized once per document; matching remains nonoverlapping substring counting, not token-aware search.
- `resc/params/fileInfo.csv` — 257 paper records with `COGSEC_ID`, `Title`, and `Abstract` columns. IDs are zero-padded to five digits.
- `resc/pdfList/` — expected PDF directory. It is not committed to this repository.

## How it works

Importing `dataImport.py`, including through `manager.py`, reads both CWD-relative parameter CSVs and constructs keyword/document mappings; the manager also imports the PDF-reader dependency. Import alone does not prompt, extract PDFs, run a batch, or create exports. Running the manager initializes callsign outputs and writes full-text columns before abstract columns.

Run from this directory so the existing relative paths resolve:

```bash
cd Literature_Analysis/PDF_Scrape
python manager.py
```

The script prompts for a callsign/export ID. The PDF corpus must be supplied separately at `resc/pdfList/00001.pdf`-style paths matching `fileInfo.csv`.

## Dependencies

The scripts import a PDF reader compatible with the `pypdf` API, or PyPDF2 as a fallback. Install one in an isolated environment, for example:

```bash
python -m pip install pypdf
```

Beyond its PDF-reader dependency and local modules, the scraper uses the standard library. Controlled CSV/text regressions live in `.github/scripts/tests/`; they replace the PDF-extraction boundary and do not qualify a real PDF parser, private corpus, or scientific result. This archive has no dependency manifest or packaging configuration.

## Caveats

- Parameter CSV reads occur at import time and remain CWD-relative. Lazy export prompting does not make imports free of input I/O or dependency requirements.
- Normalized-key insertion order and the result column/trailing-field layout are retained. Substrings can match inside larger words; tabs and punctuation are not broadly stripped.
- `mrManager.run()` returns `BatchTotals(attempted, succeeded, failed, log_failures)`, with `attempted = succeeded + failed`. Processing or result-write errors fail that document while later documents continue. A failure-log error is additionally reported to stderr; either failure makes the CLI exit nonzero.
- Failure logs are CSV records containing file ID, `failed`, and exception message. Use a CSV reader so quoted commas and embedded line breaks remain one field.
- Every run truncates both callsign files before processing, including empty batches. Reusing a callsign discards its prior contents. Streaming writes are not transactional or retry/resume behavior.
- For separately approved revival, prepare a separate workspace with its own `resc/params/` and `resc/pdfList/`, invoke this script by its full path, and choose a fresh callsign. Preserve historical inputs and exports. Other workspaces are not automatically covered by this repository's ignore rules.
- `utilCSV.py` remains an unused empty placeholder. The uncommitted PDF corpus and generated scraper outputs remain outside the historical archive.
