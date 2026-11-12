# .aii — InstituteOS sidecar

This folder is the committed [InstituteOS](https://github.com/ActiveInferenceInstitute/InstituteOS)
sidecar for **`ActiveInferenceInstitute/Knowledge-Engineering`**. It records curated institutional metadata that the GitHub
API cannot provide — identity, category, maturity, ecosystem relations, key artifacts,
provenance, and portable tasks — so InstituteOS can federate a unified view across
Institute repositories without touching this project's own content. The schema is
`aii-sidecar/v1`.

## Contents

| File | Purpose |
| --- | --- |
| [`config.yaml`](config.yaml) | Machine-readable metadata; the single source of truth. |
| [`readiness.json`](readiness.json) | Declared tier, baseline commit, and waivers for the AII readiness standard. |
| [`docs/`](docs/README.md) | Sidecar documents: the [`README.md`](docs/README.md) · [`AGENTS.md`](docs/AGENTS.md) folder guides, and [`INTEGRATION.md`](docs/INTEGRATION.md) — how this repository is federated, validated, and operated through InstituteOS. |
| [`README.md`](README.md) · [`AGENTS.md`](AGENTS.md) | Human and agent guidance for this folder. |

## Repository profile

| Field | Value |
| --- | --- |
| Repository | `ActiveInferenceInstitute/Knowledge-Engineering` |
| Category | `research` |
| Status | `active` |
| Maturity | `released` |
| License | `CC-BY-4.0` |
| Default branch | `main` |
| Homepage | — |
| Tags | `knowledge-engineering`, `knowledge-graph`, `ontology`, `literature`, `jupyter` |

## Capabilities

- notebooks
- documentation
- ci
- citation

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

## Links

- **github:** https://github.com/ActiveInferenceInstitute/Knowledge-Engineering
- **website:** https://www.activeinference.org

## Validate

The authoritative validator ships in the private `aii-platform` kernel:

```bash
python -m aii_platform.aii_sidecar.validate <repo> --completeness
python -m aii_platform.aii_sidecar docs <repo> --overwrite
python -m aii_platform.aii_sidecar.run <repo> --list
```

If the private environment is unavailable, review `config.yaml` as plain YAML and
check that every declared path exists in the repository.
