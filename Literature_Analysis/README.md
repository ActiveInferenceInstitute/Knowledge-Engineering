# `Literature_Analysis/`

The literature-analysis half of the archive: dated citation exports, the PDF
keyword-counting tool, the PubMed query notebook, and ResearchRabbit graph
exports. Every subarea keeps its own README with the file inventory and usage
details; this guide explains how the pieces fit together and where their data
overlaps.

## Subareas

| Directory | What it contains |
| --- | --- |
| [`CitationSearch_PublishOrPerish/`](CitationSearch_PublishOrPerish/README.md) | Publish-or-Perish Google Scholar export for ActInf/FEP/Karl Friston papers, preserved in TSV, ODS, and XLSX (2,894 data rows). |
| [`PDF_Scrape/`](PDF_Scrape/README.md) | Python scripts and parameter CSVs that count configured keywords in a local PDF corpus. The corpus itself is not committed. |
| [`Pubmed_to_Coda/`](Pubmed_to_Coda/README.md) | A PubMed/NCBI Entrez notebook plus the PMID, DOI, and merged article-metadata CSVs it produced. |
| [`ResearchRabbit/`](ResearchRabbit/README.md) | A December 2022 ResearchRabbit graph export: raw JSON, `COGSEC_ID` → DOI mapping, graph image, and the original bundle ZIP. |

## Cross-references between subareas

- `PDF_Scrape/resc/params/fileInfo.csv` and
  `ResearchRabbit/ID_DOI_3_28_2022.xlsx` share the `COGSEC_ID` key: all 257
  `fileInfo` IDs appear in the DOI mapping.
- `PDF_Scrape/resc/params/keywords.csv` and
  `Ontology_Snapshot/Ontology_TermsOnly.csv` share 314 terms verbatim; the
  keyword list extends the ontology terms with abstract-scope variants.
- `Pubmed_to_Coda/FEP_ActInf.csv` is the only generated dataset in the folder;
  it derives from the notebook's Entrez queries plus the two committed ID/DOI
  inputs.

## Run the tooling

There is no build step. The two runnable workflows are:

```bash
# PDF keyword counts (needs a local corpus in PDF_Scrape/resc/pdfList/)
cd Literature_Analysis/PDF_Scrape
python manager.py

# PubMed query notebook (needs pandas, biopython, jupyter; network to NCBI)
jupyter notebook Literature_Analysis/Pubmed_to_Coda/Pubmed_Query.ipynb
```

The notebook run needs an `Entrez.email` value for NCBI, and its results change
over time. See [the quickstart](../docs/quickstart.md) for the full setup and
[data provenance](../docs/provenance.md) for per-file details and caveats.

## Preservation boundary

Treat every export here as a dated snapshot. No script in this repository
regenerates the ResearchRabbit JSON, the Publish-or-Perish export, or the
ontology CSVs; only the notebook and the PDF scraper produce outputs. Do not
normalize or silently regenerate committed exports during unrelated work.

## Gate

The repository gate is one script with separately runnable arms; the default
`fast` arm checks relative links, Python syntax, notebook JSON and outputs,
Jupyter checkpoints, and the gate's own tests:

```bash
python .github/scripts/gate.py fast
```

See [docs/RUN_GUIDE.md](../docs/RUN_GUIDE.md) for every arm.
