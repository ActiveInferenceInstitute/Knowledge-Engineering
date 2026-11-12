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
2. The installed `gnn.__version__` against the tag without its `v`.
3. Every `*.gnn.md` sketch in the repository: full parse, syntax validation, and
   type checking of the collected models. When the repository has no sketch it
   downloads the pinned upstream `input/gnn_files/basics/static_perception.md`
   exemplar at the pin's revision and validates that instead, and the JSON
   receipt says `"source": "pinned-exemplar"`.

The type checker's verdict is tri-state, not boolean: `validate_gnn_files`
returns `True` when every file validated, `2` when one or more files had
type/consistency problems **or when no GNN file was found**, and `False` on a
hard failure. Only the literal `True` passes the arm. `2` is truthy, so a
truthiness test would report an invalid model set as `"result": "verified"`;
instead any other value exits non-zero and the refusal names the value the
checker returned. `.github/scripts/tests/test_gnn_conformance.py` pins all four
outcomes (`True`, `2`, `False`, `None`/`0`) without needing the parser
installed.

The arm needs network access and a Python version the pinned release supports
(`>=3.11,<3.15`); CI uses 3.12. The local recipe, including a throwaway virtual
environment, is in [`RUN_GUIDE.md`](../docs/RUN_GUIDE.md#running-the-gnn-arm-locally).
A green result is a pipeline and pin conformance baseline, not a claim that this
repository contains a model.
