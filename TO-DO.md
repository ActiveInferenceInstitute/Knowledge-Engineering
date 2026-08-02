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
- [x] **Duplicate/odd keyword entries** — `resc/params/keywords.csv` contains duplicated lines (e.g. "Homeostatic system", "Sensory attenuation") and case-variants. **Data artifact: left untouched** (frozen research input; editing would silently change results). Noted here for future owners. ✓ documented (no commit)
- [ ] **Rename `Ontology snapshot/` folder** — space in folder name is awkward for tooling and links. **Deferred**: renaming a public path breaks existing external links and the Zenodo archive's file layout; not worth the risk in this pass.

## Medium

- [x] **Strip notebook outputs** — `Pubmed_Query.ipynb` was 964 KB, ~941 KB of it stale cell outputs (97%). Outputs/execution counts removed; 38 code cells verified byte-identical. ✓ commit `29751b4`
- [x] **Remove tracked Jupyter checkpoint** — `.ipynb_checkpoints/Pubmed_Query-checkpoint.ipynb` auto-save artifact deleted; pattern gitignored. ✓ commit `29751b4`
- [x] **Fix `pdfReader.py` PyPDF2 compatibility** — imported `PdfFileReader` (PyPDF2 < 3 only; removed in PyPDF2 ≥ 3 and pypdf), so the documented pipeline was unrunnable on modern installs. Now tries `pypdf` → `PyPDF2` (new class) → legacy class; verified against modern pypdf in a throwaway venv. ✓ commit `ec7b35a` (fix: support current pypdf and PyPDF2 reader APIs)
- [x] **Add usage/dependency docs for PDF_Scrape** — no README, no requirements, no run instructions existed; scripts read `resc/params/*.csv` relative to CWD and `streamingExport.py` prompts interactively at import. All documented in `Literature_Analysis/PDF_Scrape/README.md`. ✓ commit `94ff9a7`
- [x] **Document Pubmed_to_Coda inputs/outputs** — notebook purpose, Entrez.email requirement, dependency list (pandas, biopython), and the 331-record `FEP_ActInf.csv` output now documented in `Literature_Analysis/Pubmed_to_Coda/README.md`. ✓ commit `94ff9a7`
- [x] **Improve `.aii/config.yaml` description** — `repo.description` was a bare Zenodo URL + DOI; replaced with a human-readable description and registered the new top-level doc artifacts. ✓ commit `94ff9a7`

## Major

- [x] **Rewrite the README** — was 6 lines with zero content. Now a full repository overview: purpose, contents table, quickstarts per area, citation, license, contributing, audit trail. ✓ commit `94ff9a7`
- [x] **Document every content area** — five area READMEs added (PDF_Scrape, Pubmed_to_Coda, ResearchRabbit, CitationSearch_PublishOrPerish, Ontology snapshot), each grounded in the actual files. ✓ commit `94ff9a7`
- [x] **Add governance/contributor docs** — `CONTRIBUTING.md` (how to contribute, CC BY 4.0, no-secrets/no-fabrication rules), `CITATION.cff` (machine-readable citation with DOI 10.5281/zenodo.7449027), `AGENTS.md` (agent-facing conventions: repo layout, frozen data artifacts, docs-accuracy rule). ✓ commit `94ff9a7`
- [ ] **Docs site / rendered documentation** — repo is a small data/tooling archive; a rendered site is disproportionate. **Deferred** with reason: README + per-area READMEs serve as the documentation index; revisit if the repo grows a library component.

---

## Open / deferred (unchanged items)

1. Rename `Ontology snapshot/` directory (external-link risk) — see Minor.
2. Rendered docs site — see Major.
3. `manager.py` bare `except:` and module-level execution (`m.run()` at import): code behavior changes out of scope for a docs pass; flagged for future owners in `PDF_Scrape/README.md`.
4. Duplicate entries in `keywords.csv` — frozen data artifact, intentionally untouched.
