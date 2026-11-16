# GNN conformance

The gate command is `.github/scripts/gate.py gnn` (add `--install` to fetch the
pinned parser first). It is the same command the CI job
`gnn-conformance` — displayed as **`gnn conformance (pinned)`** — runs;
see [`docs/RUN_GUIDE.md`](../docs/RUN_GUIDE.md) for every arm.

The conformance arm reads `.github/gnn-pin.json` (`gnn-importer-pin/v1`), which
pins `ActiveInferenceInstitute/Generalized_Notation_Notation` at tag `v5.0.3`,
revision `8f293d9ba810e6eda5c09842d9c7ed9ffa5f92c1` (recorded `2026-11-12`).

What it validates, in order:

1. The pin's schema, repository identity, tag shape, 40-hex revision, and
   recorded date.
2. Independently frozen reviewed bootstrap and complete v5.0.3 manifest bytes, checked before any `gnn` import. Default installed mode additionally requires matching PEP610 Git origin and full package content, not just a version string.
3. Version, parser, syntax, and type-check imports/calls run within the canonical source-qualification guard, including final origin/content rechecks. A verified receipt can escape only after that guard exits successfully.
4. Sorted tracked `*.gnn.md` paths from Git inventory. Untracked/ignored sketches are excluded; inventory errors refuse. Only an empty tracked selection downloads the pinned `input/gnn_files/basics/static_perception.md` exemplar and reports `"source": "pinned-exemplar"`.

`--gnn-source-root /exact/checkout/src/gnn` explicitly selects the narrower independently manifested source mode (`vcs_verified=false`). It is incompatible with `--install`; installed refusal never falls back to source. Each verdict requires a fresh process. `source` describes model provenance; `source-qualification` describes parser provenance, not scientific validity.

The type checker's verdict is tri-state, not boolean: `validate_gnn_files`
returns `True` when every file validated, `2` when one or more files had
type/consistency problems **or when no GNN file was found**, and `False` on a
hard failure. Only the literal `True` passes the arm. `2` is truthy, so a
truthiness test would report an invalid model set as `"result": "verified"`;
instead any other value exits non-zero and the refusal names the value the
checker returned. Controlled fixtures also reject integer `1`, corrupted authority/content, cached or foreign modules, missing installed origin, and source drift across verdict execution. They do not establish installed-runtime provenance.

The pinned release supports Python `>=3.11,<3.15`; CI uses 3.12. Explicit installation and empty-selection exemplar fetching need network authority. Already prepared source mode does not remove the exemplar's network prerequisite from the complete gate. See the [run guide](../docs/RUN_GUIDE.md#running-the-gnn-arm-locally).

A green parser result is not a model of this archive, dependency-lock qualification, or scientific evidence.
