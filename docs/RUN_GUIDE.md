# Gate and CI run guide

One entry point, `.github/scripts/gate.py`, owns every repository check. The
workflow references it and nothing else, so a local run and a CI run execute the
same command. Everything below is copied from the script's `--list` and from
`.github/workflows/ci.yml`; if they disagree, the code is right and this page is
stale.

```console
$ python .github/scripts/gate.py --list
```

## Arms

| Arm | Command | What it checks |
| --- | --- | --- |
| `links` | `python .github/scripts/gate.py links` | Relative Markdown link and image targets resolve inside the repository; Publishing artifact digests match. |
| `python` | `python .github/scripts/gate.py python` | Tracked Python files compile under the running interpreter. |
| `notebooks` | `python .github/scripts/gate.py notebooks` | Tracked notebooks are valid JSON with no committed cell outputs. |
| `checkpoints` | `python .github/scripts/gate.py checkpoints` | No Jupyter checkpoint file is tracked. |
| `archive` | `python .github/scripts/gate.py archive` | The four archive checks over one `git ls-files` read. |
| `tests` | `python .github/scripts/gate.py tests` | The gate's own dependency-free unit tests. |
| `gnn` | `python .github/scripts/gate.py gnn --install` | The pinned GNN parser, sketch parsing, and type checking. |
| `fast` (default) | `python .github/scripts/gate.py fast` | `archive` + `tests`; CI's docs job runs exactly this. |
| `full` | `python .github/scripts/gate.py full` | `fast` + `gnn`; the whole gate. |
| `timings` | `python .github/scripts/gate.py timings` | Measure each offline arm once and rewrite the timings page. |

`links`, `python`, `notebooks`, `checkpoints`, and `archive` share one
implementation in `.github/scripts/archive_checks.py`; running `archive` reads
`git ls-files` once instead of four times. `gnn` lives in
`.github/scripts/gnn_conformance.py` and is the only arm that needs the network.

The `links` check also invokes the byte-identical Publishing checker with
`--verify-copy` for the schema, checker module, and GNN pin recorded in the
[member contract](workflows/publishing.md). This runs through `archive`, `fast`,
and `full` too; no additional gate arm or corpus is introduced.

## Where the arms are measured

[`gate-timings.md`](gate-timings.md) is generated; never edit it by hand. It
records one local sample per offline arm on the host that ran

```bash
python .github/scripts/gate.py timings --include-gnn
```

`--include-gnn` adds the `gnn` measurement and needs the pinned parser already
importable in the measuring interpreter. `gnn` and `full` never appear in the
table, because both need the pinned parser and the network; `--include-gnn`
records `gnn` alone in the page's separate section, and `full` adds nothing a
reader cannot get by adding the fast table to that number. The `tests` arm fails
when the page stops listing every measured arm with its current command, so a
new arm cannot land without refreshing it.

## CI

[`.github/workflows/ci.yml`](../.github/workflows/ci.yml) has two jobs. Neither
job contains a check body of its own.

| Job key | Display name | Command |
| --- | --- | --- |
| `docs-and-scripts` | `docs and scripts` | `python .github/scripts/gate.py fast` |
| `gnn-conformance` | `gnn conformance (pinned)` | `python .github/scripts/gate.py gnn --install` |

Both jobs check out the repository and install CPython 3.12. The job keys and
display names are unchanged from the previous workflow, because the failure
evidence recorded in [`docs/README.md`](README.md#gate-failure-mode) and
`.github/GNN.md` cites `docs and scripts` and `gnn conformance (pinned)`; `main`
carries no branch protection, so no required status check constrains them. The
two jobs stay separate so a pinned-parser install failure cannot mask the fast
archive verdict, and so a GNN outage cannot fail the fast lane.

The interpreter pin and the dependency installs need no project environment:
this repository has no `pyproject.toml`, `requirements.txt`, or lockfile, so
each job uses `actions/setup-python` pinned by commit. The Active Inference
Institute composite action
`ActiveInferenceInstitute/.github/.github/actions/setup-python-uv@7159e67315330aac8e414aebae0ad1e999a41448`
exists and is the organisation's pinned way to install uv plus CPython, but this
workflow does not use it: there is no uv project to sync, so it would add a
toolchain the gate never calls. Adopt it (with `python-version: "3.12"`) if an
arm gains a locked dependency set.

## The GNN pin

| Fact | Value |
| --- | --- |
| Pin file | `.github/gnn-pin.json` |
| Schema | `gnn-importer-pin/v1` |
| Repository | `ActiveInferenceInstitute/Generalized_Notation_Notation` |
| Tag | `v5.0.3` |
| Revision | `8f293d9ba810e6eda5c09842d9c7ed9ffa5f92c1` |
| Recorded | `2026-11-12` |

`.github/GNN.md` records what the conformance arm parses. The arm validates the
schema and repository identity, installs
`generalized-notation-notation @ git+https://github.com/<repository>.git@<revision>`
with `--no-deps` plus the runtime dependencies `defusedxml`, `psutil`, and
`pyyaml`, then checks that the installed `gnn.__version__` equals the tag
without its `v`. Parsing then covers every `*.gnn.md` sketch in the repository
(full parse, syntax validation, type checking). This archive carries none, so
the arm validates the pinned upstream exemplar
`input/gnn_files/basics/static_perception.md` at the pinned revision and prints
a JSON receipt naming `"source": "pinned-exemplar"`.

### Running the GNN arm locally

The pinned release declares Python `>=3.11,<3.15`; pip refuses to install it on
a newer interpreter (`3.15.2 not in '<3.15,>=3.11'`). CI uses 3.12. Use a
throwaway environment at a supported version so the arm does not modify your
default interpreter:

```bash
python3.12 -m venv ~/.cache/gnn-venv
~/.cache/gnn-venv/bin/python .github/scripts/gate.py gnn --install
```

Both steps need network access to PyPI and GitHub.

## Why no lint or type arm

The repository has no lint, type-check or packaging configuration: its Python is
six exploratory scripts under `Literature_Analysis/PDF_Scrape/` plus this gate's
own modules and tests, and it ships no package. The archive checks are the only
static analysis it defines, so `links`/`python`/`notebooks`/`checkpoints` are its
lint surface. Adding Ruff or mypy without a project to configure them for would
report on files whose execution depends on an uncommitted PDF corpus, not on this
repository's contract. If the scraper becomes an installable package, add a
`pyproject.toml` first and then a `lint` arm that CI calls by the same name.

## What the gate does not prove

- External URLs are never fetched; a dead external link passes `links`.
- `notebooks` checks JSON structure and output emptiness, not that a notebook
  runs; the PubMed notebook needs `pandas`, `biopython`, and network Entrez
  access, none of which this host or CI provides here.
- `gnn` proves parser and pin conformance. With no committed sketch it says
  nothing about a model of this repository's own.
