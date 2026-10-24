# Mongolia's electricity a year, 2015 to 2020, from the Energy Regulatory Commission's Statistics on Energy Performance (English, 2020 edition): generation by type of plant and imports, installed capacity, and sales by grid and class of consumer

Energy Research Warehouse (ERW), method note written in session 2429 (chain 115) for a table first written on 24 October 2026 (session 2422 of chain 115, `archive/sessions/SESSION_2422_REPORT.md`, commit `9a2d6984`). Session 2425 (`archive/sessions/SESSION_2425_REPORT.md`) recorded no license verdict for the publisher. Ember's yearly demand for Mongolia, against which session 2422 compared it, is in `owid_ember_electricity_annual` (entity `owid_energy:MNG`).

Tables: `erc_mongolia_electricity_annual`

## Publisher and address

Energy Regulatory Commission of Mongolia (ERC), "Statistics on Energy Performance", English edition of 2020, linked from `https://erc.gov.mn/mn/statistic`, one PDF asked by GET without a key:

- `http://admin.erc.gov.mn/uploads/files/statisticseng.pdf` (answered at the `https://` address)

Source id `erc_mn:statistics_on_energy_performance` (`sources.csv`: license internal, first and last seen 2026-10-24). Read: three tables among the first 30 pages' tables, as pdfplumber's table extraction gives them, each found by its header: electricity generation ("Generation set"), installed capacity ("Generation sets") and electricity sales volume ("Grid" with a second column "Classification"; two other tables on the pages are also headed "Grid"). The percentage rows are not taken.

Saved report: `warehouse/raw/erc_mongolia/20261024T105515Z_probe/probe_06_http_admin_erc_gov_mn_uploads_files_statisticseng_pdf.bin`, 11,904,977 bytes, sha256 `e80494a4...`. Its manifest has two rows for the one file, the `http://` and the `https://` address, both HTTP 200 at 2026-10-24T10:56:06Z with Last-Modified "Mon, 31 May 2021 06:19:41 GMT". It was fetched by session 2422's probe, not by the connector: the connector's run folders (`20261024T105909Z`, an empty manifest, and `20261024T105920Z`) hold only the data-lock check.

Reads in `docs/licenses.md`: erc.gov.mn's and admin.erc.gov.mn's robots files (711, 774) have every line a comment and disallow nothing; the home page (772) shows a copyright sign and links no terms of reuse; the statistics page (773) gives 2021 to 2025 as pictures and 2020 as a PDF. Statistics Mongolia was not read: www.1212.mn's certificate failed verification and was not worked around (770), and opendata.1212.mn does not resolve (775). Session 2422 made 7 requests of 15 (the report).

Connector: `warehouse/connectors/erc_mongolia.py` (session 2422), `[--offline] [--out-dir DIR]`.
- **Ceiling:** one request. The report is not asked again once saved (`fetch_raw` without `fresh`), online or offline. A paused `erc_mn` or host admin.erc.gov.mn is never asked.
- **Values:** generation, imports and sales are ERC's GWh times 1,000, written as MWh rounded to 0.001. The capacity table's unit label reads "GWh"; its figures are MW (1,485.3 in 2020) and are written as MW. CRIPG's 2019 sales total, printed "5,033 .2", is read as 5,033.2.
- **Stops:** a table not found exactly once, years not consecutive, a row, grid or class not in the map, a value that is not a number, the five types not adding to total generation within 1 GWh, the capacity types not adding to the installed capacity within 0.15, a grid's classes not adding to its total or the five grids not adding to the sector's within 0.6, or a key given twice. A generation gap over 0.15 GWh is written into the header.

## Schedule and records

Schedule: none. No shell script under `warehouse/`, no workflow in `.github/workflows/`, no file in `scripts/` and not `warehouse/scheduled.py` names it.

Records:
- `runs/status/erc_mongolia.json` (main checkout): run `20261024T105920Z`, ok, "210 rows". `run_status.csv`: no row.
- `archive_manifest.csv`: 210 rows, run `20261024T105927Z-local`, `data_sha256` `2d2482f1...`, which is the data hash of the file in the main checkout (recomputed in session 2429).
- `coverage.csv`: iso `erc`, 6 nodes, P1Y, 2015-01-01 to 2020-01-01, 210 rows, last run 2026-10-24T10:59:20Z, validator pass, license internal, sector power, tier source.
- Live set: listed under `catalogue_hold` in `warehouse/supabase/live_set.yaml`, not loaded.
- Release: no row in `docs/redivis/release-v1/tables.csv`, `redivis_uploads.csv` or `redivis_uploads_stanford.csv`.
- Package: `package/src/erw/data/tables.csv` has its row since session 2431 (internal, "not settled (needs written permission by default)"); `site/data/table_citations.json` and `table_verdicts.json` have none.
- `license_tables.csv`: Energy Regulatory Commission of Mongolia (ERC), "the source registry".

Readers: none. `tests/test_session2422.py` (3 tests) tests the reader on tables built in the test.

License: no row for ERC in `license_verdicts.csv`. Session 2425 left it without a verdict: the pages show a copyright sign, no terms and no "all rights reserved". `docs/licenses.md`, the table's row: verdict "not settled (needs written permission by default)", not read: ERC, flag internal, "not settled", ERW verdict internal; it is listed under "Not settled: a publisher was not read". Header line 10: "internal until a ruling".

## Vintage and revision

One write, run `20261024T105920Z`, offline from the saved report; header line 11: "This run wrote 210 rows: 210 new, 0 replacing earlier rows ...; 0 rows are kept from earlier runs." `retrieved_at` is 2026-10-24T10:56:06Z in every row, the probe's fetch. `vintage` is 2021-05-31T06:19:41Z in every row, the PDF's Last-Modified.

This is the newest edition ERC publishes as a document (header line 4); the years 2021 to 2025 are on ERC's statistics page only as pictures, which are not read. Since the saved file is reused, a later run reads the same bytes; a new edition at the same address would not be seen without removing the saved file. Rows are replaced by (entity, variable, ts_utc); no earlier version is kept.

## Shape and variables

Series, 210 rows, 13 columns (`entity, variable, ts_utc, value, unit, freq, geo, market, node, source, source_url, retrieved_at, vintage`), 11 header lines. `ts_utc` the year's 1 January, six years 2015 to 2020; `freq` P1Y; `geo` MN; `market` blank.

- **`entity`, 6:** `erc_mn:MN` (node Mongolia, ERC's "Total for the Sector"), 90 rows; and the five grids, 24 rows each: `erc_mn:cripg` (Central Region Integrated Power Grid), `wripg` (Western), `eripg` (Eastern), `auipg` (Altai-Uliastai Integrated Power Grid) and `srpdg` (Southern Region Power Distribution Network).
- **`variable`, 15:** for the country only, `generation_chp`, `generation_diesel`, `generation_solar`, `generation_hydro`, `generation_wind`, `generation_total` and `imports` (MWh), and `capacity_chp`, `capacity_renewable`, `capacity_diesel`, `capacity_total` (MW), 6 rows each; for the country and each grid, `sales_entity_industry`, `sales_apartment`, `sales_ger_district` and `sales_total` (MWh; ERC's E&I, Ap and GD), 36 rows each.
- **Units:** 186 rows MWh, 24 rows MW. Every MWh value is a whole number. No zero, no negative.

The country, GWh (capacity MW):

| | 2015 | 2016 | 2017 | 2018 | 2019 | 2020 |
|---|---|---|---|---|---|---|
| CHP | 5,415.8 | 5,555.9 | 5,826.8 | 6,152.4 | 6,346.6 | 6,493.6 |
| Wind | 152.5 | 157.5 | 154.4 | 339.0 | 459.3 | 457.2 |
| Solar | 0.5 | 0.3 | 19.6 | 51.5 | 109.0 | 108.6 |
| Hydro | 59.3 | 84.7 | 84.5 | 78.2 | 85.4 | 83.2 |
| Diesel | 6.0 | 3.8 | 3.7 | 3.6 | 3.0 | 2.3 |
| Total generation | 5,634.1 | 5,802.2 | 6,089.0 | 6,624.7 | 7,003.3 | 7,145.6 |
| Imports | 1,393.8 | 1,419.1 | 1,522.5 | 1,683.6 | 1,715.8 | 1,705.61 |
| Sales, total | 4,343.5 | 4,508.4 | 4,788.7 | 5,258.9 | 5,559.6 | 5,673.0 |
| Capacity, total (MW) | 1,108.5 | 1,108.5 | 1,236.5 | 1,306.5 | 1,366.3 | 1,485.3 |
| of it CHP, renewable, diesel | 1,029.8, 76.4, 2.3 | 1,029.8, 76.4, 2.3 | 1,087.8, 146.4, 2.3 | 1,087.8, 216.4, 2.3 | 1,122.8, 241.2, 2.3 | 1,211.8, 271.2, 2.3 |

- **Sales by grid,** total GWh in 2015 and 2020: CRIPG 4,010.4 and 5,129.0, ERIPG 147.8 and 244.7, WRIPG 104.1 and 137.1, SRPDG 33.3 and 102.5, AUIPG 47.9 and 59.7.
- **The largest value** is 2020's total generation, 7,145,600 MWh.
- **2020's imports** are the one MWh figure not a whole tenth of a GWh (1,705.61 GWh, written 1,705,610 MWh).

## Checks

Counted in session 2429 from the table in the main checkout (`C:\Users\Shared\Documents\erw\warehouse\output`), read past its 11 header lines with `keep_default_na=False`, by scripts outside the repository. No request was made, and the report's PDF was not read again.

- 210 rows, 2015-01-01 to 2020-01-01, as header line 11 states; no (entity, variable, ts_utc) twice; no blank value; one `retrieved_at`, one `vintage` and one `source_url` in every row.
- **The types add to total generation** to the MWh in 2015 to 2019. In 2020 they add to 7,144.9 GWh against the printed 7,145.6, 0.7 under, as header line 3 states; the report adds that ERC's text gives 7,145.7.
- **The capacity types add to the installed capacity** to the tenth of a MW in all six years.
- **Each grid's classes add to its total** in 29 of the 36 entity-years (the country and the five grids, six years) exactly; in the other 7 the classes are 0.1 to 0.4 GWh off the total (CRIPG 2016 +0.1, 2017 +0.4, 2018 -0.2, 2019 -0.1; AUIPG 2019 +0.1; ERIPG 2016 -0.1; WRIPG 2020 +0.1), within the connector's 0.6.
- **The five grids add to the sector's figure** in 18 of the 24 class-years exactly; the other 6 differ by 0.1 to 0.4 GWh (the largest, total sales in 2017, the grids 0.4 under the sector's 4,788.7).
- **Against Ember** (`owid_ember_electricity_annual`, `owid_energy:MNG`, `electricity_demand`, MWh): generation plus imports is 1.004 (2017) to 1.021 (2015) times Ember's demand over 2015 to 2019 and 1.069 in 2020; total sales are 0.631 to 0.685 of it. These are the report's figures (1.004 to 1.021, 1.069, 0.63 to 0.69), recomputed.
- The connector's docstring, the header, the report and the table agree on the figures above; nothing contradicts.

## What it cannot say

- **2021 on:** ERC publishes those years only as pictures, not read; Statistics Mongolia's hosts were not read (above).
- **Months, peak demand, exports, losses and own use:** not in the three tables read.
- **Generation by grid:** only sales are given by grid; generation, imports and capacity are the country's.
- **Heat:** the CHP plants' heat output is not taken.
- **What "renewable" capacity holds** by technology: ERC's "RE sources" line is one figure.
- **A later edition at the same address,** while the saved file is reused (above).

## Acted on in session 2429

The two helpers who drafted this chain's notes made no request and changed no other file; every point was read and acted on or recorded:

- **Nothing to act on:** the note's checks agree with the connector, its header and session 2422's report. The newer editions (2021 to 2025) stay unread while ERC publishes them only as pictures.
