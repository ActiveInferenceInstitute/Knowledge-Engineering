# Data provenance

Every dataset in the repository, with what it is, its format, measured size, and caveats. Sizes were counted from the checked-in files on 2026-08-02.

## CitationSearch_PublishOrPerish

Publish-or-Perish Google Scholar export for papers on active inference (ActInf), the free energy principle (FEP), or by Karl Friston. The same export is preserved in three formats:

| File | Format | Size |
| --- | --- | --- |
| `Publish or Perish dataset_ ... .tsv` | TSV | 2,894 data rows |
| `Publish or Perish dataset_ ... .ods` | OpenDocument spreadsheet | same export |
| `Publish or Perish dataset_ ... .xlsx` | Excel workbook | same export |

TSV columns: `Cites`, `Authors`, `Title`, `Year`, `Source`, `Publisher`, `ArticleURL`, `CitesURL`, `GSRank`, `QueryDate`, `Type`, `DOI`. The files preserve their original long names.

Caveats: Google Scholar citation counts change over time; treat this as a historical snapshot, not a live index. The `QueryDate` column is populated where supplied by the export tool.

## Pubmed_to_Coda

Outputs of the PubMed query notebook (authored by Bleu Knight, February 2022; committed December 2022):

| File | Contents | Size |
| --- | --- | --- |
| `Pubmed_Query.ipynb` | 38 code cells: Entrez esearch/efetch, joins, export | — |
| `ids.csv` | PMIDs returned by the open-access queries | 258 rows |
| `PMIDS2.csv` | PMID/DOI pairs | 168 rows |
| `FEP_ActInf.csv` | merged export: abstract, authors, num_authors, first_author, title, DOI | 331 rows |
| `pubmed_230101.dtd` | PubMed XML DTD snapshot | — |

Caveats: the notebook contains repeated author-unpacking cells and assumes at least 13 author positions in its intermediate DataFrame; it is a historical exploratory artifact, not a maintained library. NCBI results are time-dependent.

## PDF_Scrape

Tooling parameters, not research exports:

| File | Contents | Size |
| --- | --- | --- |
| `resc/params/keywords.csv` | ontology keyword list (deduplicated 2026-08-02; `Dissisipation` typo fixed to `Dissipation`) | 331 rows |
| `resc/params/fileInfo.csv` | `COGSEC_ID`, `Title`, `Abstract` per paper | 257 rows, IDs 1–300 with gaps |

The PDF corpus at `resc/pdfList/` is intentionally not committed. The `COGSEC_ID` values cross-reference the ResearchRabbit DOI mapping (see below): all 257 fileInfo IDs appear in `ID_DOI_3_28_2022.xlsx` (which additionally lists 2 IDs not present in fileInfo).

## ResearchRabbit

Dated literature-graph export (December 2022):

| File | Contents |
| --- | --- |
| `daniel_friedman_raw_data.json` | ResearchRabbit graph: `nodes` (250) and `edges`; node metadata includes ident (id/pmcid/doi), title, year, journal, abstract, metrics |
| `ID_DOI_3_28_2022.xlsx` | `COGSEC_ID` → DOI mapping, 259 IDs |
| `ResearchRabbit_HALF22_image.png` | exported graph image |
| `ResearchRabbit-20221212T224443Z-001.zip` | original bundle containing the image, spreadsheet, and JSON |

Caveats: the ZIP duplicates the three extracted files; the JSON and spreadsheet are dated snapshots with no regeneration script in this repository.

## Ontology_Snapshot

CSV snapshots of an ontology vocabulary (committed December 2022; directory renamed from `Ontology snapshot` on 2026-08-02):

| File | Contents | Size |
| --- | --- | --- |
| `Ontology_TermsOnly.csv` | one-column `Term` list | 408 non-empty terms |
| `Ontology _ Definitions, Examples, Connections view.csv` | `List`, `Term`, `Proposed Definition 1`, `Proposed Definition 2` | — |

314 of the 408 terms appear verbatim (case-sensitive) in the PDF_Scrape keyword list, and the keyword list includes abstract-scope variants of core terms. The definition columns are proposed text in the source export, not a validated ontology release.

## Reproducibility guidance

- Treat every export above as a dated snapshot. Record query date, filters, and transformations when generating replacements.
- Do not silently normalize, deduplicate, or regenerate committed exports; keep provenance notes with any new version.
- Source services (Google Scholar, NCBI, ResearchRabbit, Zenodo) govern the underlying records and their terms.
