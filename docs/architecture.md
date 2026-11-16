# Architecture

How the pieces of this archive relate. There is no application runtime; the "architecture" is the data flow between the export sources, the committed snapshots, and the two runnable tools.

## Repository layout

```
Knowledge-Engineering/
├── README.md                     # overview + contents table (docs index)
├── AGENTS.md                     # conventions for automated contributors
├── CONTRIBUTING.md               # contribution + provenance guidance
├── CITATION.cff                  # machine-readable citation (Zenodo DOI)
├── LICENSE                       # CC BY 4.0
├── TO-DO.md, REVIEW_LOG_*.md     # audit trail of the 2026-08-02 pass
├── docs/                         # documentation hub (this site)
├── .aii/config.yaml              # InstituteOS sidecar metadata
├── Literature_Analysis/
│   ├── PDF_Scrape/               # keyword-counting tool (Python)
│   ├── Pubmed_to_Coda/           # PubMed notebook + CSV outputs
│   ├── ResearchRabbit/           # literature-graph export + DOI mapping
│   └── CitationSearch_PublishOrPerish/  # Google Scholar export (3 formats)
└── Ontology_Snapshot/            # ontology term + definition snapshots
```

## The two runnable pipelines

### PubMed → FEP/ActInf dataset

The preserved notebook fetches abstracts, authors, and titles from live Entrez query identifiers. It separately reads frozen `ids.csv` for author dictionaries and frozen `PMIDS2.csv` for DOI joins; the displayed `ids` DataFrame does not write either input. Left joins assemble metadata before a relative write to `FEP_ActInf.csv`.

This mixes live responses and frozen cohorts and can overwrite the archived export. It is a historical flow description, not proof of reproducibility; see the [PubMed warnings](../Literature_Analysis/Pubmed_to_Coda/README.md).

### PDF corpus → keyword counts

```
resc/params/fileInfo.csv (257 papers: COGSEC_ID, Title, Abstract)
resc/params/keywords.csv (331 keywords)
resc/pdfList/<id>.pdf     (corpus — NOT committed)
        │
        ▼
manager.py (entrypoint, prompts for callsign)
   ├── dataImport.py      formats IDs (zero-padded), builds docImport entries
   ├── docResults.py      extracts PDF text (pdfReader.py → pypdf/PyPDF2),
   │                      counts keywords in full text and abstract
   └── streamingExport.py writes <callsign>-Results.csv + <callsign>-Log.csv
```

Module dependency graph (imports):

```
manager.py ──► dataImport.py
   │          docResults.py ──► pdfReader.py (pypdf/PyPDF2)
   └────────► streamingExport.py ──► dataImport.py
```

`utilCSV.py` is an unused placeholder.

`dataImport.normalizeText()` lowercases and removes literal spaces/newlines for keywords, full text, and abstracts. Text is normalized once per document. Counting remains nonoverlapping substring search; normalized-key insertion order determines result columns. Parameter CSV reads occur at import relative to CWD. The recorded 2026-08-02 deduplication remains historical maintenance, not a new measurement.

## Cross-references between areas

- `PDF_Scrape/resc/params/fileInfo.csv` and `ResearchRabbit/ID_DOI_3_28_2022.xlsx` share the `COGSEC_ID` key: all 257 fileInfo IDs appear in the DOI mapping, so the scraped corpus is DOI-resolvable through the ResearchRabbit export.
- `PDF_Scrape/resc/params/keywords.csv` and `Ontology_Snapshot/Ontology_TermsOnly.csv` share 314 terms verbatim (case-sensitive); the keyword list extends the ontology terms with abstract-scope variants.
- `Pubmed_to_Coda/FEP_ActInf.csv` is the only cross-area *generated* dataset — it is derived from the notebook's Entrez queries plus the two committed ID/DOI inputs.

## Provenance boundary

The archive is snapshot-only: no script in this repository regenerates the ResearchRabbit JSON, the Publish-or-Perish export, or the ontology CSVs. Only the notebook and the PDF scraper produce outputs, and both are time- or corpus-dependent. See [provenance.md](provenance.md) for per-file details.
