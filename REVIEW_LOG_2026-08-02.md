# Review Log — 2026-08-02

Docs-deep review pass of `ActiveInferenceInstitute/Knowledge-Engineering`.

## Phase 0 — Preflight

- Branch: `main` (origin/main); HEAD before pass: `d438667` ("add .aii sidecar (100% complete) + CC-BY-4.0 LICENSE").
- Working tree clean at start. No uncommitted changes.
- Default branch confirmed: `origin/main` via `git symbolic-ref --short refs/remotes/origin/HEAD`.
- Repo is a public GitHub submodule of the ActiveInferenceInstitute org. Remote: https://github.com/ActiveInferenceInstitute/Knowledge-Engineering.git

### Inventory (26 tracked files)

- `README.md` — 6 lines: title, Zenodo DOI badge, a bare URL line, a bare DOI line. No content description.
- `LICENSE` — CC BY 4.0 (SPDX: CC-BY-4.0).
- `.aii/config.yaml` — InstituteOS sidecar; `repo.description` field is a bare Zenodo URL + DOI.
- `Literature_Analysis/`
  - `CitationSearch_PublishOrPerish/` — Publish-or-Perish Google Scholar export in 3 formats (TSV/ODS/XLSX); 2,894 papers (TSV), columns Cites/Authors/Title/Year/Source/Publisher/ArticleURL/CitesURL/GSRank/QueryDate/Type/DOI.
  - `PDF_Scrape/` — Python keyword-counting toolkit (2022): `manager.py`, `dataImport.py`, `docResults.py`, `pdfReader.py`, `streamingExport.py`, `utilCSV.py` (empty stub), plus `resc/params/keywords.csv` (335 keywords) and `resc/params/fileInfo.csv` (257 paper records: COGSEC_ID/Title/Abstract). `resc/pdfList/` (the PDF corpus) is NOT committed.
  - `Pubmed_to_Coda/` — `Pubmed_Query.ipynb` (authored by Bleu Knight, Feb 2022; 38 code cells, nbformat 4.2), `ids.csv` (258 PMIDs), `PMIDS2.csv` (168 PMID/DOI pairs), `FEP_ActInf.csv` (331 records), `pubmed_230101.dtd`, and a tracked `.ipynb_checkpoints/Pubmed_Query-checkpoint.ipynb` artifact.
  - `ResearchRabbit/` — `daniel_friedman_raw_data.json` (250 nodes + edges), `ID_DOI_3_28_2022.xlsx` (COGSEC_ID + DOI columns), `ResearchRabbit-20221212T224443Z-001.zip` (bundle of the other three), `ResearchRabbit_HALF22_image.png`.
- `Ontology snapshot/` — `Ontology_TermsOnly.csv` (408 terms) and `Ontology _ Definitions, Examples, Connections view.csv` (List/Term/Proposed Definition 1/Proposed Definition 2).
- No docs/ folder, no CI, no `.github/`, no CONTRIBUTING.md, no CITATION.cff, no AGENTS.md, no `.gitignore`, no requirements files, no TODO files.

### Verified facts

- DOI `10.5281/zenodo.7449027` resolves (HTTP 200 via doi.org → zenodo.org/records/7449027).
- Badge `https://zenodo.org/badge/457362490.svg` resolves (302 → SVG served).
- Notebook is 964,828 bytes; cell source is only ~11 KB — ~941 KB is stale cell outputs (97% of file).
- Contributors from git history: ActiveInferenceLab (initial), Cordes-RJ (PDF_Scrape tooling, 2022-03→10), Active Inference Institute (ResearchRabbit, ontology snapshot, DOI, 2022-12), Bleu Knight (notebook, 2022-12), Daniel Ari Friedman (sidecar/LICENSE, 2026-06).

## Phase 1 — Findings (scoped into TO-DO.md)

See `TO-DO.md` (repo root) for the full scoped list with severities. Summary:

- **Major (3):** README is effectively empty; no documentation exists for any of the five content areas; standard public-repo governance docs (CONTRIBUTING, CITATION.cff, AGENTS.md, .gitignore) are absent.
- **Medium (4):** `pdfReader.py` imports the PyPDF2 v2-only `PdfFileReader` (removed in PyPDF2 ≥ 3 / pypdf), so the documented pipeline cannot run on modern installs; 964 KB notebook is 97% stale outputs with a tracked checkpoint artifact; `.aii` sidecar description is a bare URL; no dependency/usage documentation anywhere.
- **Minor (6):** stray bare URL + DOI lines in README; `utilCSV.py` is an undocumented empty stub; duplicate/odd entries in `keywords.csv` (data artifact — left untouched, see TO-DO open items); folder name with a space (`Ontology snapshot`) — rename deferred to avoid breaking external links; no .gitignore; no cross-links between areas.

## Phase 3 — Implemented

All scoped items implemented across four commits (see `TO-DO.md` for per-item refs):

- `29751b4` chore: strip notebook outputs, drop Jupyter checkpoint artifact, add .gitignore
- `ec7b35a` fix: support current pypdf and PyPDF2 reader APIs
- `374d303` docs: add repository and area documentation (README rewrite + 5 area READMEs)
- `94ff9a7` docs: add contribution, citation, and agent guidance (CONTRIBUTING.md, CITATION.cff, AGENTS.md, .aii sidecar update)

## Phase 4 — Verification

- Markdown relative links and in-page anchors checked with a link-check script (10 markdown files; the single `%20`-encoded link to `Ontology snapshot/` decodes to an existing path — valid URL encoding for a space-containing path).
- `python -m py_compile` passes on all PDF_Scrape scripts.
- `pdfReader.py` import verified against modern `pypdf` in a throwaway venv (`/tmp/ke-docs-venv`): resolves to `pypdf._reader.PdfReader`.
- Notebook code cells verified byte-identical after output stripping (script-compared sources before/after; JSON re-validated with `json.tool`).
- `.aii/config.yaml` parses cleanly (ruby yaml).
- No test suite exists in this repo; heavy test runs not applicable. PDF_Scrape end-to-end run not executed (requires an interactive input prompt and an uncommitted PDF corpus in `resc/pdfList/`).
