# Electric emergency incidents and disturbances reported on Form DOE-417, one row a report (DOE's annual summaries)

Energy Research Warehouse (ERW), method note written in session 2038 (chain 058) for a table first written on 23 October 2026 (session 2028).

Tables: `doe_oe417_events`

## Publisher and address

U.S. Department of Energy (DOE), Office of Cybersecurity, Energy Security, and Emergency Response (CESER), Electric Emergency Incident and Disturbance Reports (Form DOE-417, formerly OE-417), the Annual Summaries, read from the form's site built by Pacific Northwest National Laboratory (`https://doe417.pnnl.gov/`, `HOST`). One workbook a year (`url_of`): `https://doe417.pnnl.gov/summaries/<year>_Annual_Summary.xls` to 2023 and `.xlsx` from 2024, as the site's own script names them. The default years are 2016 to 2025 (`YEARS`, `--years`). One request a year, a pause of 1 second after each, timeout 120 seconds, with the ERW's user agent (`UA`). Source id `doe:oe417`. Connector: `warehouse/connectors/doe_oe417.py` (session 2028).

The old host of the summaries, `www.oe.netl.doe.gov`, no longer resolves (session 2028, read 192 of `license_reads.csv`).

## Vintage and revision

The file on the data machine was written by run `20261023T182108Z` (23 October 2026), as its header says, from the ten workbooks the session's trial saved in `warehouse/raw/doe_oe417/` and the write reused offline. `retrieved_at` is one time a year, from 2026-10-23T18:15:05Z (2016) to 2026-10-23T18:15:16Z (2025); `vintage`, the files' Last-Modified, is 2026-10-08T14:56:58Z on all 3,313 rows.

Each run builds the table whole and replaces the file (`ip.write_snapshot`). The workbooks are asked for without `fresh` (`ip.fetch_raw`), so a year's file already saved in `warehouse/raw/doe_oe417/` is reused and a revision DOE makes to it is not read until that raw file is gone. No age check is made.

## Shape and variables

Events, 3,313 rows, one a report, `event_date` 4 January 2016 to 30 December 2025. By year: 2016 141, 2017 150, 2018 220, 2019 278, 2020 383, 2021 387, 2022 390, 2023 316, 2024 622, 2025 426. Every `event_date` falls in its row's `x_year`.

- `event_id` `doe417:<year>-<n>`, n the row's place in the year's summary with the rows left out counted (four digits), so an id does not shift when a row is left out; no id appears twice.
- `event_date` the day the event began; `x_begin_date` and `x_begin_time` as printed, local (the summaries name no zone).
- `event_type` the first type the row lists, lower case with underscores; 63 distinct values. The most frequent: `severe_weather` 673, `vandalism` 463, `system_operations` 381, `suspicious_activity` 305, `weather_or_natural_disaster` 229. The older years' combined names stay one type (`severe_weather_transmission_interruption` 48). `x_event_types` holds every type a row lists, in order, joined by "; " (325 rows list more than one, 162 in 2024 and 163 in 2025, up to eight); `x_event_type_as_published` the words.
- 36 rows (2024 9, 2025 27) list no type but the form's label for its comment box ("Additional Information/Comments (limit 250 characters):"), which is left out; their `event_type` is `not_given` and `x_event_types` is empty.
- `mw` the demand lost where the summary prints a plain number: 1,872 rows (1,153 of them 0). Where it prints "Unknown" (1,306 rows), nothing (135) or other words, `mw` is empty; `x_demand_loss_mw_as_published` keeps the text. On every row with `mw`, `mw` equals the printed figure without its commas.
- `status` `restored` where the restoration cell holds a day (2,619 rows), else empty (694: 363 empty cells, 326 "Unknown", 4 "- Unknown", 1 "Unkonwn"). `x_restoration_date` the day, or the words as printed; `x_restoration_time` as printed.
- `x_area_affected`, `x_alert_criteria` (never empty), `x_nerc_region` as printed. `x_nerc_region` is empty on 1,058 rows: every row of 2024 and 2025, whose summaries print no region, 9 of 2023 and 1 of 2016. The regions are as printed, not merged (`RF` 289 and `RFC` 24; `SPP RE` 41 and `SPP` 4; joint ones such as `SERC/RF` 13).
- `x_customers_affected_as_published` as printed; `x_customers_affected` the number where it is a plain number (2,460 rows).
- `parties`, `entity_ids`, `price` and `currency` empty. `x_year`, `x_row` the year and n.

A row is a report: DOE's summaries can list one event under several reports, and the table does not join them.

## Reading the source

- A sheet's header row is found among its first 40 rows by its column names (`WANT`), never by position; a sheet without Date Event Began, Area Affected, Event Type, Demand Loss and Customers Affected (`NEEDED`) is passed over, and a year with no such sheet stops the run (`read_year`). A header with no row under it stops it too.
- A begin cell with no digit stops the run; a begin cell that is not a date in one of the forms `as_day` reads stops it.
- A row with no begin day is left out and counted, never given a day. 32 rows of 2023 are left out so (`x_row` 200 to 231 are missing from 2023, which runs to 348), and the header counts them. 2023 has no row in August.
- A total the summary prints ("End of report - 622 total incident(s) for 2024") must equal the rows read plus the rows left out, or the run stops; a total naming another year stops it. The 2024 and 2025 summaries print one (622 and 426); the earlier years print none.
- A blank line (no begin day, area or type) is passed over.
- A figure printed as "Unknown" or as a range stays in its `x_` column; nothing is filled.
- The request is tried up to 4 times (`iso_prices.with_retries`), waiting 5 seconds times the attempt number after each failure; HTTP 404 is a `SourceGap`, not retried; any answer but HTTP 200 is a failure.
- Ceiling: one request a year, ten for the default years. No row ceiling is set in the code.
- Any failure is recorded as a failure, and no file is written.
- The connector does not call `iso_prices.paused()`; DOE is not in `warehouse/metadata/paused_sources.csv`.

## License

Public. `sources.csv` has `public` for `doe:oe417`; the header: "License: public (DOE: "Government information at DOE websites is in the public domain"; cite "U.S. Department of Energy, Form DOE-417")." `license_verdicts.csv`, U.S. Department of Energy (DOE), read 54 (DOE's web policies, `https://www.energy.gov/about-us/web-policies`, read 19 October 2026): "Government information at DOE websites is in the public domain. [...] Public domain information may be freely distributed and copied, but it is requested that in any subsequent use the Department of Energy be given appropriate acknowledgement." Verdict: may be public, and may be public for commercial use.

Robots: reads 192 to 194 (session 2028). `www.oe.netl.doe.gov` does not resolve; `www.energy.gov`'s file disallows only site machinery, admin and search paths; `doe417.pnnl.gov` has no robots file (its address answers with the site's page).

## Cross-checks (session 2038)

- The counts above were computed from the rows, read past the header lines; no `event_id` appears twice, and the counts by year equal the header's.
- Session 2028 checked the rows read against the totals the 2024 and 2025 workbooks print (622 and 426; the connector stops on a difference), and the 2023 rows against the 2023 PDF summary: 348 rows that begin with a month, 316 in the table and the 32 left out. The six largest 2023 losses in the table are those the session found in the PDF: Michigan 6,200 MW (22 February) and 5,800 MW (25 March), Iowa and Minnesota 2,200 MW (24 May), Gallia County, Ohio 2,000 MW (4 February), Indiana County, Pennsylvania 1,711 MW (30 March), Shelby County, Tennessee 1,200 MW and 216,000 customers (18 July). The PDF was not read again here.
- The largest `mw` a year: 2016 9,232 (King County, Washington), 2017 4,500 (Florida), 2018 31,500, 2019 133,200 (North Carolina and South Carolina), 2020 33,480, 2021 9,000, 2022 14,000, 2023 6,200, 2024 160,000, 2025 20,000. 2024's two reports of 26 March (`doe417:2024-0196`, Hanover County, Virginia, and `doe417:2024-0197`, Virginia) each print 160,000 MW and 50,000 customers; the table keeps them as printed, and a reader should not add them to anything without reading the summary.

## What it does not hold

- The years before 2016; the site offers summaries from 2000, one request a year each.
- The 32 reports of 2023 whose begin day the summary does not print.
- Times in UTC: the days and times are local, and the summaries name no zone.
- One row an event: several reports of one event stay several rows.
- Reliability indices by utility: those are `eia861_utility_reliability`.
