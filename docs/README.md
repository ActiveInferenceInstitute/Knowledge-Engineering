# Knowledge-Engineering documentation hub

This directory holds the repository-level guides for the archive. Start with
[index.md](index.md), then follow the area READMEs linked there.

- [index.md](index.md) — hub and reference map.
- [quickstart.md](quickstart.md) — browse the archive, run the PubMed notebook,
  and run PDF keyword extraction.
- [provenance.md](provenance.md) — per-dataset inventory: formats, dates, sizes,
  and caveats.
- [architecture.md](architecture.md) — how the literature-analysis components
  fit together and cross-reference each other.

This is a documentation hub over a research-data archive: there is no build step
or package to install. The canonical per-area documentation remains the README
in each area directory under `Literature_Analysis/` and `Ontology_Snapshot/`.

See the repository [README](../README.md) for the contents table, citation, and
license, and [AGENTS.md](../AGENTS.md) for contribution and preservation rules.

## Gate failure mode

[`.github/workflows/ci.yml`](../.github/workflows/ci.yml) runs
[`.github/scripts/check_archive.py`](../.github/scripts/check_archive.py) on
every pull request and on pushes to `main`. The gate fails, with exit code 1,
when a relative link does not resolve, a tracked Python file does not compile, a
notebook is not valid JSON, a notebook carries committed outputs, or an
`.ipynb_checkpoints` directory is tracked. The proof is run 41719405985, job
`docs and scripts`: the log line
`- docs/README.md: missing link target: does-not-exist.md` is followed by
`##[error]Process completed with exit code 1.` Reproduce it locally with
`python .github/scripts/check_archive.py`.
