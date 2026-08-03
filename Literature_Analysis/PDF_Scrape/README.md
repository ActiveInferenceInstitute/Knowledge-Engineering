# PDF_Scrape

Exploratory Python tooling that counts configured keywords in a local PDF corpus and in the corresponding abstracts from `resc/params/fileInfo.csv`.

## Inputs

- `resc/params/keywords.csv` — 331 keyword rows under the `Kw` column. `dataImport.py` lowercases terms and removes spaces before counting.
- `resc/params/fileInfo.csv` — 257 paper records with `COGSEC_ID`, `Title`, and `Abstract` columns. IDs are zero-padded to five digits.
- `resc/pdfList/` — expected PDF directory. It is not committed to this repository.

## How it works

`manager.py` loads every row from `fileInfo.csv`, prompts for an export ID through `streamingExport.py`, extracts PDF text, counts each keyword in full text and abstract, and writes `<ID>-Results.csv` plus `<ID>-Log.csv` in the current working directory. Result columns are generated as `ft_<keyword>` and `ab_<keyword>`.

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

`manager.py` also uses only Python standard-library functionality beyond the local modules. There is no requirements file or automated test suite in this archive.

## Caveats

- `streamingExport.py` prompts at import time, and `manager.py` runs immediately when imported; use the command above rather than importing these modules interactively.
- Keyword normalization removes spaces and searches with substring counts. This can produce matches inside larger words; it is the historical behavior of the script, not a token-aware search.
- `manager.py` catches all exceptions while processing a document and records only `failed` in the log. Inspect the source and inputs when diagnosing a failure.
- `utilCSV.py` is an empty placeholder and is not used by the current manager path.
- `resc/pdfList/` and generated `*-Results.csv`/`*-Log.csv` files are intentionally not part of the committed archive.
