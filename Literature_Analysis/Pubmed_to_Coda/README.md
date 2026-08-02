# Pubmed_to_Coda

A February 2022 Jupyter notebook for querying PubMed via NCBI Entrez for papers whose titles/abstracts contain `free energy principle` or `active inference`, restricted to the open-access filter used in the notebook.

## Files

- `Pubmed_Query.ipynb` — 38 code cells: query PMIDs, fetch abstracts/authors/titles, join DOI data, and write `FEP_ActInf.csv`.
- `ids.csv` — 258 PMID values used as an input when assembling author metadata.
- `PMIDS2.csv` — 168 PMID/DOI pairs.
- `FEP_ActInf.csv` — 331 exported records with abstract, author list, author count, first author, title, and DOI columns.
- `pubmed_230101.dtd` — a PubMed XML DTD snapshot.

## Requirements

The notebook imports `pandas` and `Bio.Entrez` from Biopython. Install them in an environment appropriate for your Jupyter kernel:

```bash
python -m pip install pandas biopython jupyter
```

Before running requests, replace the notebook's example `Entrez.email = 'you@email.com'` values with an address for NCBI request identification. The notebook calls the public Entrez `esearch` and `efetch` endpoints and may produce different results as PubMed changes.

## Run

Open `Pubmed_Query.ipynb` in Jupyter and execute cells in order. The notebook writes `FEP_ActInf.csv` in this directory. It uses `ids.csv` and `PMIDS2.csv` during the join stage; keep those files in the notebook's working directory or update the paths.

The notebook is retained as a historical exploratory artifact. It contains repeated author-unpacking cells and assumes at least 13 author positions in its intermediate DataFrame. No automated tests are included.

## Provenance

The checked-in CSVs are snapshots, not a live PubMed database. Record the execution date, query terms, and any changed filters when generating a replacement export. See the repository [README](../../README.md) for the citation and license.
