# GNN conformance

The gate command is `.github/scripts/gate.py gnn` (add `--install` to fetch the
pinned parser first). It is the same command the CI job
`gnn-conformance` — displayed as **`gnn conformance (pinned)`** — runs;
see [`docs/RUN_GUIDE.md`](../docs/RUN_GUIDE.md) for every arm.

The conformance arm reads `.github/gnn-pin.json` (`gnn-importer-pin/v1`), which
pins `ActiveInferenceInstitute/Generalized_Notation_Notation` at tag `v5.1.0`,
revision `75c834bd8519dc7b5adc4d24f16bf393cfd1ecdf` (recorded `2026-11-16`).

The checked bootstrap is the producer's [strict-origin artifact](https://raw.githubusercontent.com/ActiveInferenceInstitute/Generalized_Notation_Notation/5fb702ddd4b589b74baac86c86899bfaf4b9fffa/interop/gnn_bootstrap.py)
(SHA-256 `e04e9114c860a622f26ee8d323ac44b77c6484f5a29bdc7654fb298a9b58c3b2`).
That independently qualified resource revision is not the parser pin; the v5.1.0
manifest and parser revision above remain unchanged. Installed origins require
an exact parsed GitHub authority and complete repository path, without query,
fragment, credentials, or explicit port. Bare `org/repo` remains pin syntax
only, not installed-origin evidence. Controlled rejection fixtures are not
real installed-origin success proof.

What it validates, in order:

1. The pin's schema, repository identity, tag shape, 40-hex revision, and
   recorded date.
2. Independently frozen reviewed bootstrap and complete v5.1.0 manifest bytes, checked before any `gnn` import. Default installed mode additionally requires matching PEP610 Git origin and full package content, not just a version string.
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

The pinned release supports Python `>=3.11,<3.15`; CI uses 3.12. Explicit installation and exemplar acquisition need separate authority. Source mode alone does not prepare the exemplar; without the explicit prepared selector below, an empty tracked set still needs the pinned HTTPS download. See the [run guide](../docs/RUN_GUIDE.md#running-the-gnn-arm-locally).

For separately authorized offline qualification, prepare the authentic complete
pinned Git project, its locked declared dependencies, and an installer-generated
immutable VCS wheel cache in task-owned storage. Preserve the installer's real
origin metadata; a source-only export, copied installed package, or rewritten
`direct_url.json` is not a fresh installation. Bind the prepared artifacts in the
native execution inputs, use a fresh supported target environment, and keep
`gnn --install` as the actual gate command. Pip's ordinary offline/cache settings
may consume those exact resources; setup itself is not a conformance verdict.

`GNN_PREPARED_EXEMPLAR=/prepared/static_perception.md` explicitly separates
acquisition of the unchanged upstream exemplar from the offline verdict. Its
bytes must match SHA-256
`1ddd0fbde8155e2083d586a368503278373f26f6aae11dd4a2b4adfdf5ea7b8c`
at the pinned revision. Missing, empty, symlinked, or changed prepared inputs
refuse without a network fallback. With no selector, the same pinned HTTPS
download remains available and must match that digest. Tracked-model selection,
fresh installed-origin/full-content admission, parse/syntax/literal-`True` type
checks, and the `pinned-exemplar` receipt semantics are unchanged.

A green parser result is not a model of this archive, dependency-lock qualification, or scientific evidence.
