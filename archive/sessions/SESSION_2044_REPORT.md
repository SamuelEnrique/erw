# Session 2044 report: LNG's export authorizations (DOE's summary of LNG export applications)

23 October 2026, from 18:41 UTC, on lab-desktop (the data machine), the third session of `queue/done/059-night-24-october-data-storms-reactor-events-lng-climate.md`. Model spend USD 0. Pulls: 4 requests of 15 (www.energy.gov's robots file, asked in a call of its own and read first; the summary's old address under `/fecm/`, which answered 404; its article page under `/fecm/articles/`; the PDF it links). The trial and the write reused the saved article page and PDF (`--offline`), put in the connector's raw store with `runs/c059/seed_raw.py`.

## Read these first

- **One table written, validated, archived, in coverage (sectors gas and LNG, public), in the release package, both holds:** `doe_lng_export_applications`, 135 applications in the Department's summary as of 30 September 2026, one row a row of its tables: 100 from the Lower 48, 12 to export U.S. gas as LNG from Canada and Mexico, and 23 small-scale. Each with its applicant as printed, the FTA and non-FTA quantities in Bcf/d (a design increase added to its part), the Department's status and docket for each part ("Approved (F)", "Under DOE Review", "Vacated", "In Abeyance" and the rest), whether it waits for its NEPA review, and a status of our own: active 91 (a part approved), planned 10 (under review), withdrawn 34.
- **The office has a new name:** the summary is now posted by DOE's Hydrocarbons and Geothermal Energy Office (formerly the Office of Fossil Energy and Carbon Management); the page keeps its `/fecm/articles/` address.
- **Not in the summary, so not in the table:** the order numbers, order dates and terms the chain file asked for. They are in each order, one document a docket.
- **The summary's footnote markers are 7-point blue link text printed over the names** ("Jordan Cove Energy Project(,b Lb).P(o.o(f)ff)" when read whole). Only text of 9 points or more is read, so the names come out as printed ("Jordan Cove Energy Project, L.P."); the markers in the names' own size ("(g)", "(h) (w)") go to `x_footnotes`.
- **The rows are split at the company column's ruling lines,** and each word is placed by its column's lines, so a name across two lines stays one row.

## The cross-checks

**The summary's own totals** (read from its "Total of all" rows) against the table's sums of the parts approved, under review or in abeyance:

| Table | FTA, summary | FTA, summed | Non-FTA, summary | Non-FTA, summed |
|---|---|---|---|---|
| Lower 48 | 88.00 | 87.63 | 73.40 | 76.87 |
| Canada and Mexico | 9.12 | 9.12 | 8.11 | 8.11 |
| Small-scale | 2.53 | 2.53 | 1.55 | 1.68 |

Two of the three tables agree to the hundredth. The Lower 48's totals follow the summary's notes, which the rows do not carry: the two Lake Charles applicants' filings for the same terminal count once (note **: 2.0 and 0.33 Bcf/d), Golden Pass's average and not its peak, and volumes "no longer included" after a vacatur or dismissal. Those adjustments are left to the notes, not applied to the rows.

**The terminals EIA reports exports from** (`eia_lng_exports_monthly`) against the applications naming them, 2025's exports in Bcf/d (the year's MMcf / 365 / 1000):

| Terminal | Applications | FTA approved | Non-FTA approved | Exports, 2025 |
|---|---|---|---|---|
| Sabine Pass | 7 | 7.16 | 4.56 | 4.05 |
| Corpus Christi | 9 | 10.75 | 4.46 | 2.30 |
| Cameron | 3 | 3.08 | 3.08 | 1.86 |
| Freeport | 5 | 2.80 | 3.10 | 2.10 |
| Cove Point | 1 | 1.00 | 0.77 | 0.74 |
| Elba Island | 2 | 0.50 | 0.44 | 0.25 |
| Calcasieu Pass | 3 | 1.76 | 1.76 | 1.44 |
| Plaquemines | 2 | 9.58 | 5.13 | 2.28 |
| Golden Pass | 1 | 2.57 | 2.56 | first exports April 2026 |

Every terminal EIA reports has an approved authorization, and each exported less in 2025 than its approved non-FTA quantity (most cargoes go to non-FTA countries). Corpus Christi's approved quantity is well above its exports: its Stage III and midscale trains were still ramping.

## Errors

- **The summary's old address answered 404** (one request); the article page was found at `/fecm/articles/`.
- **The first trial stopped on a status not in the map** ("In Abeyance", SeaOne Gulfport's non-FTA application) and then on a notes page that names "Company" in its text; both handled, the first as under review.
- **A quantity written "Non-FTA" was not read** (the first pattern was case-sensitive): three applications' non-FTA quantities were empty in the second trial; corrected and checked.
- **The section did not carry over a page:** the small-scale table's second page has no heading, and its rows and total were filed under the Lower 48 in the second trial; corrected.
- **The table first showed as "not settled" in the license record:** the registry named the office after the Department, a name with no verdict. The publisher is now "U.S. Department of Energy (DOE)" (read 54, as `doe_useer_employment`), the office named in the report column.

## Decisions made without you

- **One row a row of the summary,** its first docket as the identifier (`-2` for a docket a second row names first; none did).
- **A single quantity is the application's for each part it applies for;** a design increase printed beside FTA and non-FTA quantities without its part (Magnolia's 0.15 Bcf/d) is left in the printed text only.
- **Our status from the Department's two:** active, planned or withdrawn; its words kept.
- **The notes pages not taken,** nor the totals' adjustments applied.
- **No terms page asked:** DOE's web policies (read 54) hold for energy.gov.

## For Samuel's ruling

- None new.

## Files

- New: `warehouse/connectors/doe_lng_exports.py`, `tests/test_session2044.py` (3 tests), this report.
- Changed: `build_coverage.py`, `release_v1.py`, `live_set.yaml`, `docs/coverage.md`, `coverage.csv`, `archive_manifest.csv`, `sources.csv`, `license_tables.csv`, `docs/licenses.md`, `docs/redivis/release-v1/`.
- On the data machine only: `runs/c059/s2044/`, `runs/c059/seed_raw.py`, `runs/c059/resolve.sh`, `runs/license_reads/s2044/`, `runs/s2044*`, `warehouse/raw/doe_lng_exports/`.
