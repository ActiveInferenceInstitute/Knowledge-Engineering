# Contributing

Thank you for improving this research archive.

## Before opening a change

1. Read the repository [README](README.md) and the relevant area README.
2. Confirm every documentation statement against a file, script, notebook cell, or recorded source field in this repository.
3. Keep historical exports reproducible: do not silently rewrite or normalize committed CSV, spreadsheet, JSON, image, or notebook data.
4. Do not commit secrets, credentials, private datasets, generated local paths, or unrelated repository files.

## Documentation changes

- Prefer small, focused changes with clear Markdown headings and relative links.
- Document limitations and historical dates rather than presenting snapshots as live services.
- If a command is documented, run it when practical or state why it could not be run.
- Update `TO-DO.md` and the dated review log when performing a documentation audit.

## Code and notebook changes

- Preserve the existing exploratory behavior unless a change is explicitly intended and verified.
- For Python edits, run `python -m py_compile` on the changed scripts and describe any unavailable dependency or data corpus.
- Do not commit Jupyter outputs or checkpoint files. Keep notebook source changes reviewable.
- The PDF scraper expects local inputs that are intentionally not committed; do not add a private corpus.

## Pull requests

Run the repository gate before opening a pull request; CI runs the same
commands:

```bash
python .github/scripts/gate.py fast
```

Add the GNN arm (`python .github/scripts/gate.py gnn --install`) when you change
`.github/gnn-pin.json` or the conformance script. Arms and their measured wall
times are in [docs/RUN_GUIDE.md](docs/RUN_GUIDE.md) and
[docs/gate-timings.md](docs/gate-timings.md).

Describe the files changed, the verification performed, and any remaining limitations. Keep data provenance clear: include source, query date, filters, and transformations for newly generated exports where known.

## License

Unless an artifact has a different upstream notice, contributions are released under [CC BY 4.0](LICENSE). By contributing, you agree that your contribution may be distributed under that license.
