# `.github/`

- [`workflows/ci.yml`](workflows/ci.yml) — CI: two jobs, `docs and scripts`
  (`python .github/scripts/gate.py fast`) and `gnn conformance (pinned)`
  (`python .github/scripts/gate.py gnn --install`). The workflow holds no check
  body of its own.
- [`scripts/gate.py`](scripts/gate.py) — the repository gate entry point: one
  command per arm (`links`, `python`, `notebooks`, `checkpoints`, `archive`,
  `tests`, `gnn`, `fast`, `full`, `timings`). Run
  `python .github/scripts/gate.py --list`.
- [`scripts/archive_checks.py`](scripts/archive_checks.py) — the dependency-free
  archive checks (relative Markdown links, tracked-Python compilation, notebook
  JSON and committed outputs, tracked Jupyter checkpoints).
- [`scripts/gnn_conformance.py`](scripts/gnn_conformance.py) — pin validation,
  pinned-parser install, and sketch/exemplar conformance.
- [`scripts/tests/test_gate.py`](scripts/tests/test_gate.py) — the gate's own
  tests, run by the `tests` arm.
- [`dependabot.yml`](dependabot.yml) — dependency update configuration.
- [`gnn-pin.json`](gnn-pin.json) — the `gnn-importer-pin/v1` pin used by the
  conformance arm: repository, tag `v5.0.3`, revision
  `8f293d9ba810e6eda5c09842d9c7ed9ffa5f92c1`, recorded `2026-11-12`.
- [`GNN.md`](GNN.md) — what the pinned GNN conformance arm parses.

Arms, job commands, and measured wall times are documented in
[`../docs/RUN_GUIDE.md`](../docs/RUN_GUIDE.md) and the generated
[`../docs/gate-timings.md`](../docs/gate-timings.md).

Repository change rules and conventions are in [`../AGENTS.md`](../AGENTS.md);
the documentation hub is [`../docs/index.md`](../docs/index.md).
