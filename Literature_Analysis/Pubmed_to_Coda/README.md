# Pubmed_to_Coda

A February 2022 Jupyter notebook for querying PubMed via NCBI Entrez for papers whose titles/abstracts contain `free energy principle` or `active inference`, restricted to the open-access filter used in the notebook.

## Files

- `Pubmed_Query.ipynb` — 38 code cells: query PMIDs, fetch abstracts/authors/titles, join DOI data, and write `FEP_ActInf.csv`.
- `ids.csv` — 258 PMID values used as an input when assembling author metadata.
- `PMIDS2.csv` — 168 PMID/DOI pairs.
- `FEP_ActInf.csv` — 331 exported records with abstract, author list, author count, first author, title, and DOI columns.
- `pubmed_230101.dtd` — a PubMed XML DTD snapshot.

## Requirements

The notebook imports `pandas` and `Bio.Entrez` from Biopython. Install them in an environment appropriate for your Jupyter kernel:

```bash
python -m pip install pandas biopython jupyter
```

An NCBI contact address identifies separately approved requests; it does not resolve the extraction or cohort limitations below.

## Historical status and rerun warning

This February 2022 notebook is preserved exploratory source, not a validated current extraction workflow. Keep the notebook and committed CSVs as historical artifacts. Inventory counts describe saved snapshots, not expected new query results. The following source risks do not establish that particular saved rows were affected.

Do not execute all cells in this checkout to reproduce the archive. The notebook makes live Entrez requests; zero-based cell 35 writes `FEP_ActInf.csv` in CWD and can overwrite the committed export. Ignore rules do not prevent that overwrite.

### Known source limitations

Cell numbers are zero-based.

- **Structured/missing abstracts:** cell 4 retains only `AbstractText[0]`; later sections are not assembled. Missing `Abstract` records are skipped; empty/missing `AbstractText` is unguarded. Cells 5 and 29 retain abstract-bearing records as the left-hand join set. The scratch missing-abstract list is reused, not retained as an exclusion report.
- **Tenth author:** cell 18 selects `Authors9` but builds `A9` from `Authors3`. It repeats fourth-author data and can add that duplicate even when a record has no tenth author.
- **Truncation/narrow frames:** cells 8–22 assemble positions 0–12, thirteen positions rather than the fourteen in a comment. Later authors are omitted. Unconditional positional-column selection can fail when the cohort's widest list has fewer than thirteen positions; this is a cohort-wide frame-width assumption.
- **Derived lists/counts:** cells 22 and 24–26 use those positional frames. Duplicated or omitted authors feed both lists and `num_authors`, which need not equal complete Entrez `AuthorList` lengths.
- **Final schema:** cell 34 names exactly six data columns: `abstract`, `authors`, `num_authors`, `first_author`, `title`, `DOI`. PMID remains the exported join index. Earlier affiliation fields and cohort provenance are not separate final fields; renaming assumes exactly six joined data columns.
- **Missing matches:** cell 27 selects the first-author match with `.values[0]`; an absent PMID can stop execution. Later left joins do not reconcile coverage/cardinality. Unmatched surviving rows may contain missing metadata; right-only identifiers add no rows.
- **Live/frozen mixing:** live queries/fetches are combined with frozen `ids.csv` author inputs and `PMIDS2.csv` DOI inputs. The displayed `ids` frame does not refresh either file. A rerun is not automatically a consistent new cohort or reproduction.

### Decisions before revival

Warning documentation does not authorize notebook edits or data regeneration. The research owner must select the PMID cohort, query/filter/date policy, structured/missing-abstract treatment, complete author extraction or labeled limit, missing-join behavior, required fields, provenance, and a non-overwriting destination.

Future offline acceptance must cover multi-section/missing/empty abstracts; zero/one/narrow author cohorts; fourth-author records without tenth authors; distinct fourth/tenth authors; lists longer than thirteen; missing author/first-author matches; query-only, author-input-only and DOI-input-only PMIDs; association/order/count/schema fidelity; and preservation of historical exports.

## Provenance

Committed CSVs are snapshots, not a live database. Separately approved new exports must record date, exact query/filters, selected PMID cohort, input versions, extraction policies, and destination without replacing archived exports. See the repository [README](../../README.md) for citation and license.
