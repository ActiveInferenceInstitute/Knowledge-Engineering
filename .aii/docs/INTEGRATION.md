# InstituteOS integration — Knowledge-Engineering

## Identity

| Field | Value |
| --- | --- |
| Repository | `ActiveInferenceInstitute/Knowledge-Engineering` |
| Affiliation | `institute` |
| Category | `research` |
| Status | `active` |
| Maturity | `released` |
| Steward | Active Inference Institute |
| Default branch | `main` |
| Current release | — |
| License | `CC-BY-4.0` |
| Citation | Active Inference Institute — Knowledge-Engineering. |

## Federation

| Setting | Value |
| --- | --- |
| Dashboard mode | `repos` |
| Analytics | `true` |
| Dashboard | `true` |
| Sync policy | `pull` |
| Registries | — |
| Tags | knowledge-engineering, knowledge-graph, ontology, literature, jupyter |

## Ecosystem relations

| Repository | Relation | Note |
| --- | --- | --- |
| `ActiveInferenceInstitute/InstituteOS` | `referenced-by` | Federated via the InstituteOS .aii manifest. |

## Key artifacts

| Path | Kind | Description |
| --- | --- | --- |
| `README.md` | `doc` | Repository overview and documentation index. |
| `docs/index.md` | `doc` | Documentation hub (guides and reference map). |
| `docs/quickstart.md` | `doc` | Quickstart guide for the notebook and PDF tooling. |
| `docs/provenance.md` | `doc` | Dataset inventory and provenance notes. |
| `docs/architecture.md` | `doc` | Pipelines, module flow, and cross-area references. |
| `CONTRIBUTING.md` | `doc` | Public contribution and provenance guidance. |
| `CITATION.cff` | `metadata` | Machine-readable citation metadata. |
| `AGENTS.md` | `doc` | Repository conventions for automated contributors. |
| `Literature_Analysis/README.md` | `doc` | Folder-level guide to the four literature-analysis subareas. |
| `Literature_Analysis/PDF_Scrape/README.md` | `doc` | PDF keyword extraction usage and limitations. |
| `Literature_Analysis/Pubmed_to_Coda/README.md` | `doc` | PubMed notebook usage and provenance. |
| `Literature_Analysis/ResearchRabbit/README.md` | `doc` | ResearchRabbit export inventory. |
| `Literature_Analysis/CitationSearch_PublishOrPerish/README.md` | `doc` | Publish-or-Perish export inventory. |
| `Ontology_Snapshot/README.md` | `doc` | Ontology snapshot inventory. |
| `LICENSE` | `doc` | License. |
| `docs` | `doc` | Documentation tree. |

## Portable tasks

| Task | Command | Working directory | Description |
| --- | --- | --- | --- |
| `links` | `python .github/scripts/gate.py links` | `.` | Check documentation links and Publishing digests; docs index is docs/documentation-index.md. |
| `python` | `python .github/scripts/gate.py python` | `.` | Compile tracked Python sources. |
| `notebooks` | `python .github/scripts/gate.py notebooks` | `.` | Check notebook JSON and absence of outputs. |
| `checkpoints` | `python .github/scripts/gate.py checkpoints` | `.` | Reject tracked Jupyter checkpoints. |
| `archive` | `python .github/scripts/gate.py archive` | `.` | Run the archive checks and Publishing digest checks. |
| `tests` | `python .github/scripts/gate.py tests` | `.` | Run dependency-free gate tests. |
| `gnn` | `python .github/scripts/gate.py gnn` | `.` | Check GNN conformance using .github/gnn-pin.json. |
| `fast` | `python .github/scripts/gate.py fast` | `.` | Run archive checks and tests; no manuscript command exists. |
| `full` | `python .github/scripts/gate.py full` | `.` | Run fast and GNN conformance. |
| `timings` | `python .github/scripts/gate.py timings` | `.` | Measure offline arms and regenerate docs/gate-timings.md. |

## Validation

```bash
python -m aii_platform.aii_sidecar.validate <repo> --completeness
python -m aii_platform.aii_sidecar docs <repo> --overwrite
python -m aii_platform.aii_sidecar.run <repo> --list
```

The sidecar is valid when `validate` prints `OK` and reports no missing artifact,
manifest, link, or declared-doc path. Completeness is a curation target, not a
runtime requirement.

## Data boundary

This sidecar carries metadata only. It does not grant execution permission, does not
replace the repository's own documentation, and must not be used to move private
content into a public repository. Task execution is limited to trusted checkouts.
