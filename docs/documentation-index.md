# Documentation index

Flat index of this repository's long-lived documentation. `README.md` in each
directory is that directory's user-facing guide; this page lists them in one
place. Generated pages are marked as such and are refreshed by a script.

## Entry points

- [README.md](../README.md) — repository overview, contents table, citation, license.
- [AGENTS.md](../AGENTS.md) — agent-facing layout, change rules, verification.
- [CONTRIBUTING.md](../CONTRIBUTING.md) — contribution, provenance, and data-preservation rules.
- [CITATION.cff](../CITATION.cff) — machine-readable citation metadata (Zenodo DOI).

## Documentation hub

- [docs/README.md](README.md) — hub: guides, gate, and the recorded gate failure mode.
- [docs/index.md](index.md) — the same map rendered as guide and reference tables.
- [docs/RUN_GUIDE.md](RUN_GUIDE.md) — gate entry point, arms, CI jobs, GNN pin.
- [docs/gate-timings.md](gate-timings.md) — **generated** per-arm wall times.
- [docs/workflows/publishing.md](workflows/publishing.md) — member migration, canonical contract pointer, and artifact digests.
- [docs/workflows/record-identity.schema.json](workflows/record-identity.schema.json) — digest-pinned canonical Publishing identity schema.

## Guides

- [docs/quickstart.md](quickstart.md) — browse the archive, run the PubMed notebook, run the PDF extractor.
- [docs/provenance.md](provenance.md) — per-dataset inventory: formats, dates, sizes, caveats.
- [docs/architecture.md](architecture.md) — how the literature-analysis components relate.

## Area guides

- [Literature_Analysis/README.md](../Literature_Analysis/README.md) — folder-level guide to the four literature-analysis subareas.
- [Literature_Analysis/PDF_Scrape/README.md](../Literature_Analysis/PDF_Scrape/README.md) — keyword counting inputs, invocation, dependencies.
- [Literature_Analysis/Pubmed_to_Coda/README.md](../Literature_Analysis/Pubmed_to_Coda/README.md) — PubMed notebook, inputs, outputs, provenance.
- [Literature_Analysis/ResearchRabbit/README.md](../Literature_Analysis/ResearchRabbit/README.md) — ResearchRabbit export inventory.
- [Literature_Analysis/CitationSearch_PublishOrPerish/README.md](../Literature_Analysis/CitationSearch_PublishOrPerish/README.md) — Publish-or-Perish export inventory.
- [Ontology_Snapshot/README.md](../Ontology_Snapshot/README.md) — ontology term and definition snapshots.

## Continuous integration

- [.github/README.md](../.github/README.md) — workflow, gate scripts, Dependabot, pin file.
- [.github/GNN.md](../.github/GNN.md) — what the pinned GNN conformance arm validates.
- [.github/gnn-pin.json](../.github/gnn-pin.json) — the `gnn-importer-pin/v1` pin.

## InstituteOS sidecar

- [.aii/README.md](../.aii/README.md) — sidecar metadata overview.
- [.aii/docs/INTEGRATION.md](../.aii/docs/INTEGRATION.md) — integration notes and portable tasks.
- [.aii/docs/README.md](../.aii/docs/README.md) — sidecar documentation index.

## Audit trail

- [TO-DO.md](../TO-DO.md) — scoped findings and their completion state.
- [REVIEW_LOG_2026-08-02.md](../REVIEW_LOG_2026-08-02.md) — dated review and verification record.
