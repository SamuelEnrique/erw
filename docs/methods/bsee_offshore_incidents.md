# Incidents on the Outer Continental Shelf, an incident, calendar years 2018 and 2020 to 2024 (BSEE, Offshore Incident Statistics)

Energy Research Warehouse (ERW), method note written in session 2185 (chain 097) for a table first written on 24 October 2026 (session 2177).

Tables: `bsee_offshore_incidents`

## Publisher and address

U.S. Department of the Interior, Bureau of Safety and Environmental Enforcement (BSEE), Offshore Incident Statistics. The connector reads the statistics page and, from it, the address of each calendar year's workbook "for public use" (an `.xlsx` whose file name begins `cy` and a year):

`https://www.bsee.gov/stats-facts/offshore-incident-statistics`

The workbooks read, as `source_url` gives them:

| Year | Workbook | Last-Modified |
|---|---|---|
| 2018 | `https://www.bsee.gov/sites/bsee.gov/files/cy2018-public-release-01-17-2020.xlsx` | 27 Jan 2020 |
| 2020 | `https://www.bsee.gov/sites/bsee.gov/files/cy-2020-offshore-incident-statistics-excel-spreadsheet.xlsx` | 17 Nov 2021 |
| 2021 | `https://www.bsee.gov/sites/bsee.gov/files/2023-03/cy-2021-excel-spreadsheet.xlsx` | 7 Apr 2023 |
| 2022 | `https://www.bsee.gov/sites/bsee.gov/files/2024-02/cy-2022-excel-spreadsheet.xlsx` | 22 Feb 2024 |
| 2023 | `https://www.bsee.gov/sites/bsee.gov/files/2024-10/cy-2023-excel-spreadsheet.xlsx` | 9 Oct 2024 |
| 2024 | `https://www.bsee.gov/sites/bsee.gov/files/2026-04/cy-2024-excel-spreadsheet.xlsx` | 7 Apr 2026 |

The Last-Modified times are from the raw files' manifests on the data machine. The User-Agent is "Mozilla/5.0 (compatible; ERW-connector/0.1; +https://github.com/SamuelEnrique/erw)". Source id `bsee:offshore_incidents`. Connector: `warehouse/connectors/bsee_incidents.py` (session 2177), its only table. www.bsee.gov's robots file (read 347) disallows the site's admin, search, user, core and profile paths, not /sites/ or /stats-facts/.

The table is not scheduled: no line of `warehouse/run_daily.sh`, the other `warehouse/*.sh` scripts, `warehouse/scheduled.py`, `scripts/` or `.github/workflows/` names the connector (searched in session 2185), and `run_status.csv` holds no row for it. It was written once, by run `20261024T012138Z` on the data machine, offline from the saved workbooks.

## Vintage and revision

Incidents dated 2 January 2018 to 31 December 2024 (`event_date`). The workbooks were retrieved from 2026-10-24T00:54:22Z (2024, the session's probe) to 01:00:09Z (2020 to 2023), with 2018's in two live trials (00:59:04Z and 00:59:41Z); the write reused the saved copies. The table has no `retrieved_at` or `vintage` column (below). `coverage.csv` gives the same 4,818 rows and the same first and last date.

Each run writes the whole table again (`ip.write_snapshot`); the page and each workbook are asked again unless `--offline`. A new calendar year enters when the page links its workbook. The page is read for the addresses on each run, so a workbook BSEE replaces at a new address is followed.

## Shape and variables

Events, 4,818 rows, one an incident: 2018 503, 2020 687, 2021 773, 2022 870, 2023 943, 2024 1,042. `event_id` `bsee_incident:<id>`: BSEE's serial (`SN_EV_MASTERS`) from 2020 on (4,312 negative numbers and 3 positive, 4539, 4540 and 4542), and for 2018, whose workbook has no serial, `h` and the first 12 hex digits of a SHA-1 hash of the incident's date, time, operator, area, block, lease and summary (503 rows). `event_date` the incident's date (`YYYY-MM-DD`); `event_type` `offshore_incident`; `parties` the operator as BSEE names it (95 names); `entity_ids` `lease:<lease number>` (683 leases; blank in 606 rows); `mw`, `price`, `currency`, `status` empty; `source` and `source_url` the year's workbook.

- `x_year` the workbook's year, which is the year of `event_date` in every row.
- `x_time` the time as BSEE writes it, a 24-hour hhmm number without leading zeros (`0`, `5`, `1505`); none is above 2359.
- `x_region`: Gulf of Mexico 3,600 (2018 to 2023), Gulf of America 1,006 (2024), Pacific 209, Alaska 3 (2018), kept as written.
- `x_district`: nine names, "California" in 2020 and "California District" in the other years; one row (2024, Pacific) blank.
- `x_area` (blank in 59 rows, all 2022 and 2023), `x_block`, `x_water_depth_ft` (feet, as BSEE gives it; blank in 104), `x_structure` and `x_structure_type` (each blank in 1,404 rows), `x_rig` (blank in 3,267). The structure types are BSEE's codes (FIXED, SEMI, SPAR, TLP, CAIS, CT, FPSO, MTLP, MOPU, WP) in every year but 2020, whose workbook writes them in words ("Fixed Leg Platform", "Spar Platform - Floating Production System").
- `x_fatalities` and `x_injuries`: every fatality column and every injury column of the workbook summed (operator and contractor, each injury class). Fatalities 19 (19 incidents of one: 2018 1, 2020 6, 2021 8, 2022 1, 2023 0, 2024 3); injuries 1,117 (1,057 incidents of one, 30 of two).
- Flags, Y or N: `x_fire` 716, `x_explosion` 11, `x_loss_of_well_control` 16 (any of BSEE's four kinds), `x_collision` 40 (major or minor), `x_lifting` 1,723 (crane or other lifting device), `x_gas_release` 422 (reportable H2S or shut-down gas release).
- `x_summary` BSEE's own words, spaces run together; blank in 11 rows (2021). 615 summaries of 2024 carry BSEE's redaction marks ("[REDACTED_NAME]"). 98 summaries hold characters outside ASCII as read from the workbooks, among them the inverted question mark (130 times) and pairs that look like text encoded twice (2020 holds 42 of the 98).

No `event_id` is given twice, and the rows are in (event_date, event_id) order. The counts were computed in session 2185 from the rows, read past the 10 header lines with pandas (every column as text); the header's own counts (fatalities 19, injuries 1,117, fires 716, losses of well control 16) agree.

## Checks the connector makes

- Before any request, the connector and www.bsee.gov are checked against `warehouse/metadata/paused_sources.csv`; a paused publisher stops the run with no request. It is not paused.
- The page must link at least one calendar-year workbook, and no year twice. Years before 2018 are not read: 2017's workbook holds its fourth quarter only. The page links no workbook for 2019.
- Each workbook must have one sheet whose name holds "incident", one header row in its first ten naming Date and Operator Name, the columns the connector reads, and at least one injury and one fatality column, or the run stops. Column names are normalised: 2018 brackets its descriptions, and 2020 calls the summary "Redacted Incident Summary".
- A date that does not read, a count that is not a whole number, a flag that is neither Y nor N, or a serial given twice stops the run; so does an incident in two years. Blank lines are passed over. 2018's notes, written in the date column under the incidents, end the sheet.
- BSEE's totals line, where a workbook has one, is checked: each Y/N column's count of Y and each count column's sum must equal it where the line gives a figure, or the run stops. The line is not kept. The header records no totals line in 2018, 2020 and 2021, so 2022, 2023 and 2024 are the years checked.
- Nothing is filled. Ceiling: the page and one request a year, a pause of 1 second after the page and 2 after each workbook.

## The cross-check

Session 2177 set the incidents beside the Gulf's oil production from BOEM's leases (`boem_ogor_lease_production_monthly`, oil in kbbl) in `runs/c097/s2177/cross.py` (on the data machine, not in git), reading the trial copy of the table:

| Year | Incidents | Fires | Injuries | Fatalities | Oil, million bbl | Incidents per 100 million bbl |
|---|---|---|---|---|---|---|
| 2018 | 503 | 77 | 168 | 1 | 642.20 | 78.33 |
| 2020 | 687 | 87 | 160 | 6 | 610.19 | 112.59 |
| 2021 | 773 | 117 | 164 | 8 | 623.25 | 124.03 |
| 2022 | 870 | 126 | 199 | 1 | 632.19 | 137.62 |
| 2023 | 943 | 149 | 203 | 0 | 680.85 | 138.50 |
| 2024 | 1,042 | 160 | 223 | 3 | 656.22 | 158.79 |

Incidents roughly doubled against production. Of the 683 leases the incidents name, 613 (90 percent) are among BOEM's production leases; the match compares lease numbers after stripping leading G and 0 characters from both sides. The regions are Gulf of Mexico 3,600, Gulf of America 1,006, Pacific 209 and Alaska 3.

## License

The header: "License: public (BSEE's workbooks: Public Access Level: Public; the Department of the Interior's notice, see license_verdicts.csv). Cite the Bureau of Safety and Environmental Enforcement." `license_verdicts.csv` gives BSEE "may be public", the same if the ERW sells anything (read 159, the Department of the Interior's notice, as for ONRR and BLM; recorded in session 2181): "Generally, materials produced by federal agencies are in the public domain and may be reproduced without permission." Its note: the incident workbooks are BSEE's own record, marked "Public Access Level: Public" on the statistics page (read 348). `coverage.csv`: public.

## Found while writing this note

- The code's comment says "2018 to 2020's workbooks have no serial". The rows show 2020's incidents with BSEE's serial; only 2018's carry hash ids, as session 2177's report says.
- The docstring says each workbook's last line holds BSEE's totals and that 2018's has none. The header records no totals line in 2018, 2020 and 2021, so only 2022 to 2024 are checked against BSEE's totals.
- The docstring says every count must equal the totals line. The code compares only where the totals line gives a figure; a blank cell in that line is not checked.
- Session 2177's report says "the header says which years carry BSEE's serial". The header's shape line gives only `bsee_incident:<serial>` and does not name the hash ids of 2018.
- The table has no `retrieved_at` column, though its last header line says "Per row, source, source_url and retrieved_at say where it came from". The code sets each row's `retrieved_at` and then drops it, since the events columns it writes do not include it.
- The cross-check script's docstring speaks of "oil in barrels-equivalent of gas at 6 Mcf"; the script sums `oil_production` alone.

Acted on in session 2185: the comment and the docstring now say only 2018 lacks a serial and only 2022 to 2024 have a totals line, checked where it gives a figure; `retrieved_at` is kept after `source_url` and the table was written again (the same 4,818 incidents); session 2177's report is corrected. The cross-check script is on the data machine only and is left as it is.

## What it does not hold

- 2019, for which the page links no workbook; 2017, whose workbook holds its fourth quarter only; and the fiscal-year files before it, which are in another form.
- BSEE's totals lines, its notes and its other sheets.
- The injury classes and the operator and contractor split, which are summed; the four kinds of loss of well control and the two kinds of collision, which are one flag each.
- Production, inspections or civil penalties: incidents only.
