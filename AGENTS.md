# AGENTS.md

## Repository purpose

Knowledge-Engineering is a public research-data and exploratory tooling archive. It contains dated literature exports, a PubMed notebook, a small PDF keyword-counting script set, a ResearchRabbit graph export, and an ontology snapshot.

## Layout

- `README.md` — public overview and documentation index.
- `Literature_Analysis/*/README.md` — area-specific documentation.
- `Literature_Analysis/PDF_Scrape/` — scripts and parameter CSVs; the expected PDF corpus is not committed.
- `Literature_Analysis/Pubmed_to_Coda/` — historical PubMed notebook and outputs.
- `Literature_Analysis/ResearchRabbit/` — dated graph export.
- `Literature_Analysis/CitationSearch_PublishOrPerish/` — dated citation-search exports.
- `Ontology snapshot/` — term and proposed-definition CSV exports.

## Change rules

- Ground documentation in files and code that exist in this repository; do not invent counts, links, citations, or capabilities.
- Treat committed research exports as historical source artifacts. Do not normalize, deduplicate, or silently regenerate them during unrelated work.
- Do not add secrets, private paths, private datasets, credentials, or generated local outputs.
- Do not commit Jupyter checkpoint files or notebook outputs.
- Preserve the historical `Ontology snapshot/` path unless a deliberate migration includes link compatibility.

## Verification

For Python edits, run `python -m py_compile` on changed scripts. For notebook edits, verify JSON validity and compare code-cell sources before and after output cleanup. For documentation edits, check relative links and ensure dates/status claims match repository contents.

See `CONTRIBUTING.md` for public contribution guidance and `TO-DO.md` for the current audit state.
