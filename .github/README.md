# `.github/`

- [`workflows/ci.yml`](workflows/ci.yml) — CI: the dependency-free archive gate
  and the pinned GNN conformance job.
- [`scripts/check_archive.py`](scripts/check_archive.py) — the repository's
  archive gate: relative Markdown links, tracked-Python syntax, notebook JSON
  and committed outputs, and tracked Jupyter checkpoints.
- [`dependabot.yml`](dependabot.yml) — dependency update configuration.
- [`gnn-pin.json`](gnn-pin.json) — the pinned Generalized Notation Notation
  revision (v5.0.3, commit `8f293d9ba810e6eda5c09842d9c7ed9ffa5f92c1`) used by
  the conformance job.
- [`GNN.md`](GNN.md) — what the pinned GNN conformance job checks.

Repository change rules and conventions are in [`../AGENTS.md`](../AGENTS.md);
the documentation hub is [`../docs/index.md`](../docs/index.md).
