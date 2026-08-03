# TO-DO — Knowledge-Engineering documentation pass

Last reviewed: 2026-08-02 (docs-deep review; see `REVIEW_LOG_2026-08-02.md`)

Sections:
- **Minor** — typo, broken link, formatting, small cleanups.
- **Medium** — stale section rewrite, doc restructure, added missing guide, file hygiene.
- **Major** — large doc system overhaul, cross-cutting refactors.

---

## Minor

- [x] **Remove stray bare-URL/DOI lines in README** — `README.md` lines 5–6 were loose artifacts; folded into a proper Citation section. ✓ commit `94ff9a7` (docs: add repository and area documentation)
- [x] **Markdown formatting/lint on README** — README had no structure (no headings beyond title, no license/citation clarity). ✓ commit `94ff9a7`
- [x] **Document the empty `utilCSV.py` stub** — unused placeholder; now described in `Literature_Analysis/PDF_Scrape/README.md`. ✓ commit `94ff9a7`
- [x] **Add `.gitignore`** — repo had none; adds `__pycache__/`, `*.py[cod]`, `.venv/`, `.ipynb_checkpoints/`, `.DS_Store`, and PDF_Scrape runtime output CSVs. ✓ commit `29751b4` (chore: strip notebook outputs, drop Jupyter checkpoint artifact, add .gitignore)
- [x] **Duplicate/odd keyword entries** — `resc/params/keywords.csv` contained duplicated lines (e.g. "Homeostatic system", "Sensory attenuation"), case-variants, and the misspelling "Dissisipation". Resolved in the comprehensive follow-up: 4 duplicate rows removed and the typo fixed; the normalized keyword dict used by `dataImport.py` is provably unchanged except the intended `Dissipation` key. ✓ commit `e3fc7ca` (chore: deduplicate keyword parameter list and fix misspelling)
- [x] **Rename `Ontology snapshot/` folder** — space in folder name was awkward for tooling and links. Migrated to `Ontology_Snapshot/` via `git mv` (history preserved); all references updated (README, AGENTS.md, .aii sidecar, area README). Note: this changes the public file layout; pre-2026-08-02 links to the space-containing path (including the frozen Zenodo record) point at the old layout. ✓ commit `93deb5c` (chore: rename Ontology snapshot directory to Ontology_Snapshot)

## Medium

- [x] **Strip notebook outputs** — `Pubmed_Query.ipynb` was 964 KB, ~941 KB of it stale cell outputs (97%). Outputs/execution counts removed; 38 code cells verified byte-identical. ✓ commit `29751b4`
- [x] **Remove tracked Jupyter checkpoint** — `.ipynb_checkpoints/Pubmed_Query-checkpoint.ipynb` auto-save artifact deleted; pattern gitignored. ✓ commit `29751b4`
- [x] **Fix `pdfReader.py` PyPDF2 compatibility** — imported `PdfFileReader` (PyPDF2 < 3 only; removed in PyPDF2 ≥ 3 and pypdf), so the documented pipeline was unrunnable on modern installs. Now tries `pypdf` → `PyPDF2` (new class) → legacy class; verified against modern pypdf in a throwaway venv. ✓ commit `ec7b35a` (fix: support current pypdf and PyPDF2 reader APIs)
- [x] **Add usage/dependency docs for PDF_Scrape** — no README, no requirements, no run instructions existed; scripts read `resc/params/*.csv` relative to CWD. All documented in `Literature_Analysis/PDF_Scrape/README.md`. ✓ commit `94ff9a7`
- [x] **Document Pubmed_to_Coda inputs/outputs** — notebook purpose, Entrez.email requirement, dependency list (pandas, biopython), and the 331-record `FEP_ActInf.csv` output now documented in `Literature_Analysis/Pubmed_to_Coda/README.md`. ✓ commit `94ff9a7`
- [x] **Improve `.aii/config.yaml` description** — `repo.description` was a bare Zenodo URL + DOI; replaced with a human-readable description and registered all top-level and area doc artifacts. ✓ commits `94ff9a7`, `2c2660d`
- [x] **Harden PDF_Scrape entrypoint behavior** — `streamingExport.py` prompted at import time and `manager.py` executed at import. Now: lazy export configuration (import-safe), `if __name__ == "__main__"` guard, and failure logs include the exception message. Verified end-to-end in a throwaway venv (257-record run via stdin). ✓ commit `5bb023f` (fix: guard manager entrypoint and make streaming export configuration lazy)

## Major

- [x] **Rewrite the README** — was 6 lines with zero content. Now a full repository overview: purpose, contents table, quickstarts per area, citation, license, contributing, audit trail. ✓ commit `94ff9a7`
- [x] **Document every content area** — five area READMEs added (PDF_Scrape, Pubmed_to_Coda, ResearchRabbit, CitationSearch_PublishOrPerish, Ontology_Snapshot), each grounded in the actual files. ✓ commit `94ff9a7`
- [x] **Add governance/contributor docs** — `CONTRIBUTING.md` (how to contribute, CC BY 4.0, no-secrets/no-fabrication rules), `CITATION.cff` (machine-readable citation with DOI 10.5281/zenodo.7449027), `AGENTS.md` (agent-facing conventions: repo layout, frozen data artifacts, docs-accuracy rule). ✓ commit `94ff9a7`
- [x] **Docs site / rendered documentation** — implemented as a lightweight markdown hub under `docs/` (rendered by GitHub with no build toolchain): `index.md` (hub + reference map), `quickstart.md`, `provenance.md` (measured per-dataset inventory), `architecture.md` (pipelines, module flow, cross-area links). README links the hub. A Jekyll/MkDocs site with CI was considered and rejected as disproportionate for a data archive. ✓ commit `2c2660d` (docs: add documentation hub with quickstart, provenance, and architecture)

---

## Open / deferred (unchanged items)

None — every scoped finding from the 2026-08-02 review has been implemented. Future candidates (not scoped, noted for owners):

1. Rendered docs site with a static-site generator and CI (MkDocs/Jekyll) if the repo grows a library component.
2. Code modernization beyond the entrypoint fix: `dataImport.py`/`docResults.py` module-level file reads (relative paths by design), `formatFileId` edge cases, `docResults1` legacy variant removal.
3. A `requirements.txt`/`pyproject.toml` for the PDF_Scrape tool if it is revived for active use.
