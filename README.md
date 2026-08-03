# Knowledge-Engineering

[![DOI](https://zenodo.org/badge/457362490.svg)](https://zenodo.org/badge/latestdoi/457362490)

A public research-data and exploratory tooling archive from the Active Inference Institute. The repository brings together literature searches, PDF keyword extraction scripts, a PubMed query notebook, ResearchRabbit exports, and an ontology snapshot related to active inference and the free energy principle.

This is an archive of research inputs and exploratory analysis artifacts rather than a packaged Python library. The data files are preserved as collected snapshots; scripts and notebooks may require adjustment for current APIs and dependencies.

## Contents

| Area | What it contains |
| --- | --- |
| [`Literature_Analysis/PDF_Scrape/`](Literature_Analysis/PDF_Scrape/) | Python scripts and CSV parameters for counting keywords in a local PDF corpus. |
| [`Literature_Analysis/Pubmed_to_Coda/`](Literature_Analysis/Pubmed_to_Coda/) | A PubMed/NCBI Entrez notebook plus PMID, DOI, and exported article metadata CSVs. |
| [`Literature_Analysis/ResearchRabbit/`](Literature_Analysis/ResearchRabbit/) | ResearchRabbit graph data, DOI mapping, image export, and the original bundle archive. |
| [`Literature_Analysis/CitationSearch_PublishOrPerish/`](Literature_Analysis/CitationSearch_PublishOrPerish/) | Publish-or-Perish Google Scholar export in TSV, ODS, and XLSX formats. |
| [`Ontology_Snapshot/`](Ontology_Snapshot/) | CSV snapshots of ontology terms and proposed definitions/connections. |

## Quick start

### Browse the archive

The repository has no build step. Start with the area README files above, then inspect the CSV, spreadsheet, JSON, PNG, and notebook artifacts directly.

### Run the PubMed notebook

The notebook uses `pandas` and Biopython's `Bio.Entrez` client. Open `Literature_Analysis/Pubmed_to_Coda/Pubmed_Query.ipynb` in Jupyter, replace the example `Entrez.email` value with an email address for your NCBI requests, and execute the cells in order. See the [Pubmed_to_Coda README](Literature_Analysis/Pubmed_to_Coda/README.md) for inputs and outputs.

### Run PDF keyword extraction

The PDF scraper expects a local PDF corpus at `Literature_Analysis/PDF_Scrape/resc/pdfList/`, which is not included in this repository. Its parameter files and invocation details are documented in the [PDF_Scrape README](Literature_Analysis/PDF_Scrape/README.md).

## Documentation

The [documentation hub](docs/) provides a [quickstart](docs/quickstart.md), a [data provenance inventory](docs/provenance.md), and an [architecture overview](docs/architecture.md) alongside the area READMEs above.

## Reproducibility and data provenance

The committed literature files are dated exports and snapshots. Their exact query settings and source metadata are not fully recorded in the repository, so they should not be treated as a continuously updated literature index. Preserve the original files when producing a new analysis and record any new query date, filters, or transformations alongside the result.

The PubMed notebook queries NCBI's public Entrez API and writes `FEP_ActInf.csv`. NCBI service usage should follow the current [Entrez documentation](https://www.ncbi.nlm.nih.gov/books/NBK25497/).

## Citation

Use the archived Zenodo record and DOI when citing this repository:

- DOI: [10.5281/zenodo.7449027](https://doi.org/10.5281/zenodo.7449027)
- Record: [Zenodo 7449027](https://zenodo.org/records/7449027)

A machine-readable citation is also provided in [`CITATION.cff`](CITATION.cff).

## License

Unless a source artifact states otherwise, repository documentation and research artifacts are made available under [CC BY 4.0](LICENSE). Attribution and indication of changes are required. Upstream source services and exported records may have their own terms.

## Contributing

See [`CONTRIBUTING.md`](CONTRIBUTING.md). In particular, do not commit credentials or private datasets, do not silently rewrite frozen data exports, and verify documentation against the files and code that actually exist.

## Audit trail

The current documentation review is recorded in [`REVIEW_LOG_2026-08-02.md`](REVIEW_LOG_2026-08-02.md), with outstanding work in [`TO-DO.md`](TO-DO.md).
