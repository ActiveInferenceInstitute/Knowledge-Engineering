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
| `tests` | `python .github/scripts/gate.py tests` | Dependency-free gate contracts and controlled scraper regressions. |
| `gnn` | `python .github/scripts/gate.py gnn` | Qualified installed parser origin/content, sketch parsing, syntax and type checking; installation requires explicit `--install`. |
| `fast` (default) | `python .github/scripts/gate.py fast` | `archive` + `tests`; CI's docs job runs exactly this. |
| `full` | `python .github/scripts/gate.py full` | `fast` + `gnn`; the whole gate. |
| `timings` | `python .github/scripts/gate.py timings` | Measure each offline arm once and rewrite the timings page. |

`links`, `python`, `notebooks`, `checkpoints`, and `archive` share one
implementation in `.github/scripts/archive_checks.py`; running `archive` reads
`git ls-files` once instead of four times. `gnn` lives in
`.github/scripts/gnn_conformance.py`; installation and empty-model exemplar fetching need network access.

The `links` check invokes the recorded Publishing checker with `--verify-copy` for the schema, checker, and member-owned GNN pin in the [member contract](workflows/publishing.md). `archive`, `fast`, and `full` include it. This proves local digest agreement, not authenticated producer freshness or corpus identity coverage.

## Where the arms are measured

[`gate-timings.md`](gate-timings.md) is generated; never edit it by hand. It
records one local sample per offline arm on the host that ran

```bash
python .github/scripts/gate.py timings --include-gnn
```

`--include-gnn` adds a separate GNN measurement, requiring its actual selected parser/runtime and, for this empty-model archive, network access. Historical samples remain historical. New timings must come from the source-owned generator after inputs settle; a successful subset does not qualify a new full measurement.

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

The conformance arm checks independently frozen reviewed bootstrap and complete manifest bytes before importing the unchanged pinned parser. Default installed mode requires matching PEP610 Git origin and complete package content. Explicit source mode uses the same authority with a deliberately selected `src/gnn` root, without claiming installed/VCS provenance. No failed-installed-to-source fallback exists.

Parser/version/syntax/type-check calls and delayed imports remain guarded through final content/origin rechecks. Only literal `True` from `validate_gnn_files` passes. Sorted tracked sketches are selected; inventory failures refuse. This archive has none, so the complete arm fetches the pinned upstream exemplar and labels its model source separately from parser qualification.

### Running the GNN arm locally

Use an already provisioned Python `>=3.11,<3.15` runtime (CI uses 3.12), and a fresh process per verdict:

```bash
python .github/scripts/gate.py gnn
python .github/scripts/gate.py gnn --gnn-source-root /exact/checkout/src/gnn
python .github/scripts/gate.py full --gnn-source-root /exact/checkout/src/gnn
python .github/scripts/gate.py timings --include-gnn --gnn-source-root /exact/checkout/src/gnn
```

`--gnn-source-root` is incompatible with `--install` and unrelated arms; relative paths are resolved before timing children change CWD. `--install` is an explicitly authorized separate installation, not automatic runtime selection. Installation and the empty-selection exemplar need network authority.

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
- Controlled CSV/text fixtures do not parse real PDFs or qualify the private corpus.
- Controlled GNN fixtures do not qualify an installed parser; explicit source qualification is a separate, narrower origin claim.
- With no tracked authored sketch, the upstream exemplar says nothing about an archive-specific model or scientific semantics.
