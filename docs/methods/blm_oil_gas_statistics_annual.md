# Federal onshore oil and gas leases, acreage, permits and wells, by state and fiscal year (BLM, Oil and Gas Statistics)

Energy Research Warehouse (ERW), method note written in session 2116 (chain 069) for a table first written on 23 October 2026 (session 2106).

Tables: `blm_oil_gas_statistics_annual`

## Publisher and address

U.S. Department of the Interior, Bureau of Land Management (BLM), Oil and Gas Statistics, the workbook "All Fed O&G Statistics by Year by State" (Tables 1 to 10 and a Summary sheet). The connector reads the statistics page,

`https://www.blm.gov/programs/energy-and-minerals/oil-and-gas/oil-and-gas-statistics`

and takes from it the one link to the latest fiscal year's "All Fed" workbook, which was, for the run of 23 October 2026,

`https://www.blm.gov/sites/default/files/docs/2026-04/All%20Fed%20O_G%20Statistics%20by%20Year%20by%20State_Web%20Stats_Tabs%20w%20Table%20Numbers_FY25.xlsx`

The User-Agent is "Mozilla/5.0 (compatible; ERW-connector/0.1; +https://github.com/SamuelEnrique/erw)". Source id `blm:oil_gas_statistics`. Connector: `warehouse/connectors/blm_oil_gas_stats.py` (session 2106), its only table. Session 2106's report: three requests to www.blm.gov (the robots file in a call of its own, the page, the workbook); the robots file disallows `/core/`, `/profiles/`, `/search/`, `/admin/` and the user pages, not `/programs/` or `/sites/default/files/` (the docstring).

The table is not scheduled: no line of `warehouse/run_daily.sh`, the other `warehouse/*.sh` scripts, `scripts/` or `.github/workflows/` names the connector (searched in session 2116), and `run_status.csv` holds no row for it. It was written once, by run `20261023T212611Z` on the data machine.

## Vintage and revision

Fiscal years 2001 to 2025 (`ts_utc` 1 October 2000 to 1 October 2024). The workbook was retrieved at 2026-10-23T21:20:34Z by the session's probe and reused by the write run; its Last-Modified, the rows' `vintage`, is 2026-04-08T14:16:52Z; every sheet says "As of 10/1/2025" (`x_as_of` 2025-10-01). `coverage.csv` gives the same 12,500 rows, 50 entities and the same first and last `ts_utc`.

Each run writes the whole table again (`ip.write_snapshot`): a later workbook replaces every row. BLM's notes, quoted in the header: the well and permit figures come from its Automated Fluid Minerals Support System, which updates often, and earlier years from Public Land Statistics, so a year's figure can change between workbooks.

## Shape and variables

Series, 12,500 rows: 50 states, 10 variables, 25 fiscal years, every cell present. `entity` `blm_oil_gas:<postal code, lower case>`; `ts_utc` 1 October of the year before the fiscal year (FY 2025 begins 1 October 2024); `freq` P1Y; `geo` US-<state>; `market` empty; `node` the state as BLM names it; `x_fiscal_year` BLM's year; `x_table` BLM's table; `x_as_of` the sheets' date. Tables 1, 2, 5, 6, 9 and 10 stand on the fiscal year's last day; Tables 3, 4, 7 and 8 count what happened during it. Federal only: BLM's notes say Indian leases and wells are not included.

| Variable (table) | Unit | Rows | Mean a state-year | Zeros | Highest |
|---|---|---|---|---|---|
| `leases_in_effect` (1) | count | 1,250 | 888.9 | 432 | 21,525 (Wyoming, FY 2002) |
| `acres_under_lease` (2) | acre | 1,250 | 673,653.7 | 432 | 15,359,523 (Wyoming, FY 2002) |
| `new_leases_issued` (3) | count | 1,250 | 32.7 | 810 | 1,123 (Wyoming, FY 2001) |
| `acres_newly_leased` (4) | acre | 1,250 | 37,534.5 | 810 | 1,403,561 (Alaska, FY 2004) |
| `producing_leases` (5) | count | 1,250 | 462.8 | 543 | 7,924 (Wyoming, FY 2005) |
| `producing_acres` (6) | acre | 1,250 | 248,958.8 | 543 | 5,027,052 (Wyoming, FY 2008) |
| `apds_approved` (7) | count | 1,250 | 84.5 | 845 | 4,327 (New Mexico, FY 2025) |
| `wells_spud` (8) | count | 1,250 | 53.1 | 857 | 2,740 (Wyoming, FY 2007) |
| `producible_service_well_bores` (9) | count | 1,250 | 1,692.1 | 529 | 34,874 (New Mexico, FY 2025) |
| `producible_service_completions` (10) | count | 1,250 | 1,805.9 | 529 | 39,944 (New Mexico, FY 2025) |

The lowest of every variable is 0. Sixteen states are 0 in every variable and year (Connecticut, Delaware, Georgia, Hawaii, Iowa, Maine, Massachusetts, Minnesota, Missouri, New Hampshire, New Jersey, North Carolina, Rhode Island, South Carolina, Vermont, Wisconsin): BLM lists them and the table keeps its zeros. Summed over the states, wells spud were 5,343 in FY 2007 (the most), 847 in FY 2016 (the fewest) and 2,358 in FY 2025; permits approved 7,124 in FY 2007, 2,184 in FY 2016 and 5,740 in FY 2025; leases in effect fell from 55,085 (FY 2008) to 31,833 (FY 2025, the fewest). The counts above were computed in session 2116 from the rows, read past the 10 header lines; no (entity, variable, ts_utc) is given twice.

## Checks the connector makes

- Before any request, BLM is checked against `warehouse/metadata/paused_sources.csv` by connector and by host (`ip.paused`, `ip.paused_host`); a paused publisher stops the run with no request. BLM is not paused.
- The statistics page must link exactly one "All Fed" workbook for the latest fiscal year, or the run stops. The workbook's last fiscal year must be the one its name gives.
- The Summary sheet must hold one header row of "FY <year>" columns (one or more spaces) and one row for each of the ten tables; each table's sheet must begin "As of m/d/yyyy", hold one "Geographic State" header row with the Summary's years, a row for each of the 50 states in the map, and a TOTAL row.
- A state not in the map, a state given twice, figures with no state, a sheet not found, a year column missing, a cell that is not a number, or a key given twice stops the run, and nothing is written. Nothing is filled.
- In every table and year the states must sum to BLM's total, and each total must equal the Summary's, within 0.6; the total rows are checked and not kept.
- Ceiling: two requests a run (the page and the workbook), by the code's shape rather than a counter. Each address is tried up to four times, 5, 10 and 15 seconds apart (`ip.with_retries`); an HTTP 404 is not retried. One second after each request.

## The cross-check

Session 2106 set BLM's states against ONRR's federal onshore production by state (`onrr_production_annual`, oil and gas at 6 Mcf a barrel, for ranking only) in `runs/c069/s2106/cross.py` (on the data machine, not in git). BLM's producing leases rank the states as ONRR's production does (Spearman 0.95 in 2015, 0.96 in 2020, 0.95 in 2024), the well bores at 0.93 to 0.94 and the wells spud at 0.77 to 0.81, with New Mexico, Wyoming, Colorado, North Dakota and Utah leading both; the few states on one list and not the other are small.

## License

The header: "License: may be public (the Department of the Interior's notice: materials produced by federal agencies are generally in the public domain; see license_verdicts.csv). Cite the Bureau of Land Management as the source." `license_verdicts.csv` gives BLM "may be public" (read 159, session 956; the same if the ERW sells anything), and `docs/licenses.md` gives the ERW verdict public. `coverage.csv`: public. Session 2106's report holds the table in the live set's catalogue hold (`warehouse/supabase/live_set.yaml`) and the release's storage hold (`warehouse/redivis/release_v1.py`).

## Found while writing this note

- The docstring says the page and the workbook are "saved in warehouse/raw/blm_oil_gas_stats/ and reused offline". The code calls `ip.fetch_raw` without `fresh`, which reuses a saved copy on every run, offline or not, so a later run reads the saved FY 2025 workbook again and does not find a newer one until the raw files are moved.
**Acted on in session 2116:** the connector now asks for its documents again unless `--offline` (`fresh=not args.offline`), so a later run sees a newer workbook; the source registry's license word is now `public`, one of the standard's two.

## What it does not hold

- Indian (tribal and allotted) leases and wells: BLM leaves them out.
- Production: the oil and gas produced on these leases is ONRR's (`onrr_production_annual`, `onrr_production_monthly`).
- BLM's national total rows: checked as read and not kept (a sum over the states gives them).
- Fiscal years before 2001.
