# Applications to export LNG, an application (DOE's Summary of LNG Export Applications)

Energy Research Warehouse (ERW), method note written in session 2052 (chain 059) for a table first written on 23 October 2026 (session 2044).

Tables: `doe_lng_export_applications`

## Publisher and address

U.S. Department of Energy (DOE), Hydrocarbons and Geothermal Energy Office (formerly the Office of Fossil Energy and Carbon Management), Summary of LNG Export Applications of the Lower 48 States (`https://www.energy.gov/fecm/articles/summary-lng-export-applications-lower-48-states`). The connector reads the article page and the first PDF it links whose name holds "Summary" and "LNG"; this one is `https://www.energy.gov/sites/default/files/2026-09/Summary%20of%20LNG%20Export%20Applications_9.30.26_1.pdf`. Source id `doe:lng_export_applications`. Connector: `warehouse/connectors/doe_lng_exports.py` (session 2044).

## Vintage and revision

The summary as of 30 September 2026 (`status_date` and `x_as_of` in every row); the PDF last modified 2026-09-30T19:13:59Z, retrieved 2026-10-23T18:41:41Z, written by run `20261023T184648Z` from the saved copy. The table is a snapshot, written whole each run, so an application the Department drops leaves it. The article page is asked fresh each run; the PDF is reused from `warehouse/raw/doe_lng_exports/` when saved.

## Shape and variables

Entities, 135 rows, one a row of the summary's tables; `entity_type` project; `geo`, `lat`, `lon`, `capacity_mw`, `operator` empty.

| `x_section` | Rows | active | planned | withdrawn |
|---|---|---|---|---|
| lower48 | 100 | 65 | 7 | 28 |
| canada_mexico (U.S. gas exported as LNG from Canada and Mexico) | 12 | 8 | 2 | 2 |
| small_scale | 23 | 18 | 1 | 4 |

- `entity_id` `doe_lng:<docket>`, the row's FTA docket, else its non-FTA docket: 127 LNG, 4 CNG and 4 CGL dockets. No docket is first in two rows, so no `-2` suffix is used.
- `status`, ours: active when either part is approved (91), planned when a part is under review or in abeyance and none approved (10), withdrawn otherwise (34). The Department's words stay in `x_fta_status` (Approved 86, Vacated 28, n/a 9, Under DOE Review 6, blank 3, Withdrawn 2, Dismissed 1) and `x_non_fta_status` (Approved 35, Approved (F) 24, n/a 19, Under DOE Review 16, Withdrawn 13, Expired 8, Vacated (F) 7, Dismissed 7, Vacated 4, In Abeyance 1, blank 1).
- `x_fta_bcfd`, `x_non_fta_bcfd`: Bcf/d. A quantity marked ": FTA" or ": non-FTA" goes to its part, a design increase so marked is added (Golden Pass: 2.03 + 0.54 FTA, 2.21 + 0.35 non-FTA); a single quantity is the application's for each part it applies for. A design increase printed without its part beside FTA and non-FTA quantities stays in `x_quantity_as_published` only (Magnolia LNG, 13-131-LNG, 0.15 Bcf/d).
- `x_nepa_pending` yes in 12 rows (the summary's `*`); `x_page` the PDF page (1 to 6, 14 to 16).
- `x_footnotes` is empty in all 135 rows: a marker in the name's own size would go there, but in this edition every marker is 7-point text, which the reader drops (the docstring and session 2044's report, corrected by session 2052, say so).

## Reading the source

- Only text of 9 points or more is read (the 7-point footnote links printed over the names are not). Rows are cut at the company column's ruling lines; a page must show 5 column lines or the run stops.
- A row without a docket, or a status not in the connector's map, stops the run. The summary's "Total of all" rows are read into the header, not the table; its notes pages are not taken.
- Ceiling: two requests, the article page and the PDF.

## License

`license_verdicts.csv` records the U.S. Department of Energy (DOE), read 54: "may be public", for public and for commercial use: "Government information at DOE websites is in the public domain. [...] Public domain information may be freely distributed and copied, but it is requested that in any subsequent use the Department of Energy be given appropriate acknowledgement." `license_tables.csv` lists the table under DOE; `docs/licenses.md` as may be public, flagged public, agreeing.

## Cross-checks (session 2052)

- The counts above were computed from the rows, read past the header lines; no `entity_id` is given twice; the section and status counts match the header's.
- The parts approved, under review or in abeyance, summed, against the summary's totals in the header: canada_mexico FTA 9.12 and non-FTA 8.11 (the summary's 9.12 and 8.11); small_scale 2.53 and 1.68 (2.53 and 1.55); lower48 87.63 and 76.87 (88.00 and 73.40). Session 2044's report found the same and traces the Lower 48's gap to the summary's notes (the two Lake Charles applicants counted once, Golden Pass's average, volumes no longer included), which the rows do not carry.
- Session 2044's report sets each exporting terminal's approved quantities against 2025's exports in `eia_lng_exports_monthly`: every terminal exported less than its approved non-FTA quantity.

## What it does not hold

- The order numbers, order dates and terms: they are in each order, not in the summary.
- The summary's notes and its adjustments to the totals.
- The terminal's location, capacity in MW or operator.
- Earlier summaries: each run keeps the latest only.
