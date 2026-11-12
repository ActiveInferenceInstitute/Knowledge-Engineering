# Publishing — Knowledge-Engineering member

The [Publishing contract](https://github.com/ActiveInferenceInstitute/ActiveInferenceJournal/blob/d8ec888a8f3051a66bed9af047ee4b206050bdce/docs/workflows/publishing.md)
in ActiveInferenceJournal owns the workflow and identity grammar. This member
points there rather than restating the schema or creating identities for historical
research exports.

## Member mapping

- Gate: `python .github/scripts/gate.py <arm>`; commands and arm descriptions live
  in the [run guide](../RUN_GUIDE.md) and [sidecar tasks](../../.aii/config.yaml).
- Docs index: [docs/documentation-index.md](../documentation-index.md).
- Manuscript command: none.
- GNN pin: [.github/gnn-pin.json](../../.github/gnn-pin.json).

The sidecar lists only documented gate-arm commands and uses existing sidecar
documentation paths. The archive's existing link, syntax, notebook, checkpoint,
test, timing and GNN checks remain authoritative for what they already prove,
as permitted by the contract; no parallel implementations are introduced.

## Canonical copies and drift checks

[identity.py](../../scripts/gate/identity.py) and
[record-identity.schema.json](record-identity.schema.json) are unchanged copies
from the lead revision linked above. The identity grammar is defined only in the
schema, not mirrored in prose here. The existing GNN pin is also digest-bound.

```text
record-identity.schema.json  84f6c4df6efc3f15f0d8a9a05c8aabd0cbdc08b0f4feac5fcc8ae860a81e306b
identity.py  847328ff163fa90c869495164869caf4e83313748e8a444dbab8d4e459b11074
gnn-pin.json  eb83f7f1b73eb31e116bd05b1f457dd07e6874a2a4ba0e9e95e5bc91f094cd55
```

The `links` arm invokes the canonical module's `--verify-copy` command for every
artifact above. `archive`, `fast`, and `full` include that check. Gate tests prove
that matching copies pass and changed copies fail. Checks are offline and
stdlib-only; no JSON Schema package, journal corpus, or fabricated record data is
required. These checks prove artifact agreement, not identity coverage of the
historical research exports.
