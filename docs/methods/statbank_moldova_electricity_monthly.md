# Moldova's electricity balance a month, January 2015 to August 2026 (StatBank table ENE010100)

Energy Research Warehouse (ERW), method note written in session 2366 (chain 110) for a table first written on 24 October 2026 (session 2358, `archive/sessions/SESSION_2358_REPORT.md`, "Bangladesh closed, Moldova's electricity in its place (StatBank)", commit `b98a2967`). Session 2362 (`archive/sessions/SESSION_2362_REPORT.md`, "the licenses' thirty-third round", commit `76809bc3`) made it public under the bureau's CC BY 4.0 terms and wrote it again offline, the same 980 rows. Eurostat's monthly figures for Moldova, the table this one is checked against, are in `eurostat_electricity_monthly` (`docs/methods/eurostat_electricity_monthly.md`). North Macedonia's monthly balance, read the same way in the session before, is `makstat_macedonia_electricity_monthly` (`docs/methods/makstat_macedonia_electricity_monthly.md`).

Tables: `statbank_moldova_electricity_monthly`

## Publisher and address

National Bureau of Statistics of the Republic of Moldova, StatBank (PxWeb), Energy resources, monthly series, table ENE010100, "Stocks, inputs and electricity consumption by Indicators, Years and Months", page `https://statbank.statistica.md/PxWeb/pxweb/en/40%20Statistica%20economica/40%20Statistica%20economica__15%20ENE__serii%20lunare/ENE010100.px/`. Read through the PxWeb API (no key) at `https://statbank.statistica.md/PxWeb/api/v1/en/40%20Statistica%20economica/15%20ENE/serii%20lunare/ENE010100.px`: the metadata by GET (811 bytes) and one JSON-stat 2.0 query by POST for every cell. The metadata has three variables: `Indicatori` (Indicators, codes 1 to 7), `Ani` (Years, 2015 to 2026, the time variable) and `Luni` (Months, 01 to 12; StatBank spells October "Octomber"). The answer's `source` is "National Bureau of Statistics of the Republic of Moldova", its `extension` `{'px': {'infofile': 'Energetica_TS_en', 'decimals': 1}}`, and no dimension states a unit. Source id `statbank_md:ENE010100`; `sources.csv`: publisher "National Bureau of Statistics of the Republic of Moldova (StatBank)", report "StatBank table ENE010100: Stocks, inputs and electricity consumption, monthly", license public, first and last seen 2026-10-24.

The requests, both of 24 October 2026, were not the connector's:

- session 2358's probe read the metadata at 08:29:41Z (request 9, read 602; copy `runs/license_reads/s2358/09_...ene010100_px.bin`);
- `runs/c110/s2358/query.py` built the query from that copy, sent it by POST (request 10) and saved the query, the metadata and the answer, with `retrieved_at` 2026-10-24T08:30:00Z, as `warehouse/raw/statbank_moldova/query_ENE010100.json`, with the same file in `runs/c110/s2358/`.

The two copies are equal, and the probe's copy equals the saved metadata. Every connector run read the saved file offline: the trial `20261024T083058Z` (its raw folder an empty manifest), session 2358's write `20261024T083120Z` and session 2362's write `20261024T084252Z` (each raw folder only the data lock's check; logs in `warehouse/output/logs/`). statbank.statistica.md has no robots file (HTTP 404 from `https://statbank.statistica.md/pxweb/robots.txt`, read 597).

Connector: `warehouse/connectors/statbank_moldova.py` (session 2358; its license lines changed in session 2362), `--offline` and `--out-dir`. It asks `iso_prices.paused` and `iso_prices.paused_host("statbank.statistica.md")` first; neither names StatBank. It stops if the metadata's variables are not `Indicatori`, `Ani` and `Luni`, if the seven indicators' codes and texts are not those expected, if the months are not 01 to 12, if the answer's dimensions are not the three or its values not their size, or if an indicator and month come twice. Each value is StatBank's figure as published; `vintage` is blank. The file is a snapshot (`write_snapshot`). Ceiling: two requests a run, which no run has made.

Schedule: none. No run script, workflow, step of `warehouse/scheduled.py` or file in `scripts/` names the connector.

`run_status.csv`: no row (the newest run wrote `runs/status/statbank_moldova.json`, run `20261024T084252Z`, "ok", "980 rows"; disagreement 7). `archive_manifest.csv`: 980 rows, run `20261024T084256Z-local`, data hash `5bff28d1...`, which equals the hash of the file on this machine. `redivis_uploads.csv` and `redivis_uploads_stanford.csv`: no row (session 2362: "not yet in the Stanford draft"). Release package: in `STORAGE_HELD` of `warehouse/redivis/release_v1.py` and "held" in `docs/redivis/release-v1/tables.csv` (disagreement 6). Live set: in `catalogue_hold` of `warehouse/supabase/live_set.yaml` (not loaded). Readers: none. `build_coverage.py` gives it the sector `power`, and `tests/test_session2358.py` tests the parse (3 tests).

## Vintage and revision

One retrieval: every row's `retrieved_at` is 2026-10-24T08:30:00Z. `vintage` is blank in every row. The answer's `updated` field reads 2015-06-19T08:12:00Z, a date before every month from July 2015 to August 2026 that the table holds, so it is not when these figures were published, and the connector rightly leaves it out. StatBank's API gives no other date.

The file was written twice from the same saved answer: by session 2358 (run `20261024T083120Z`) and by session 2362 (run `20261024T084252Z`, header line 10: "the previous file held 980 rows"). Header line 1 still names session 2358 (disagreement 2). The file is a snapshot: StatBank's revisions of a month, if any, would show only by comparing with the archive's copy.

## Shape and variables

Series, 980 rows, 14 columns (`entity, variable, ts_utc, value, unit, freq, geo, market, node, source, source_url, retrieved_at, vintage, x_code`), 10 header lines. One entity, `statbank_md:md`; unit MWh; `freq` P1M; `geo` MD; `market` blank; `node` StatBank's text, as written; `x_code` StatBank's code. Every value is written with one decimal (StatBank's decimals: 1); 631 of the 980 are not whole MWh. Seven variables of 140 months each, 2015-01 to 2026-08, no month missing inside:

| x_code | Variable | StatBank's text | Mean | Median | Lowest (month) | Highest (month) | Zero months |
|---|---|---|---|---|---|---|---|
| 1 | `production` | Production | 80,772.5 | 63,379.9 | 3,848.6 (2016-08) | 247,967.6 (2020-10) | 0 |
| 2 | `imports` | Import | 77,130.1 | 45,645.1 | 0.0 (2022-03) | 318,538.1 (2025-12) | 2 (2022-03, 2022-04) |
| 3 | `acquired_from_other_sources` | Acquired from other sources | 213,794.4 | 242,520.1 | 0.0 (2017-04) | 340,034.5 (2020-08) | 23 |
| 4 | `stock_change` | Stock change | 0.0 | 0.0 | 0.0 | 0.0 | 140 (every month) |
| 5 | `exports` | Export | 11,464.2 | 8.8 | 0.0 (2017-09) | 70,770.8 (2023-04) | 2 (2017-09, 2019-10) |
| 6 | `gross_inland_consumption` | Gross inland consumption | 360,232.9 | 355,269.4 | 236,484.5 (2026-05) | 583,245.2 (2018-12) | 0 |
| 7 | `residential_consumption` | of which: consumed in the residential sector | 143,800.0 | 140,533.0 | 114,167.0 (2015-06) | 204,999.0 (2026-01) | 0 |

MWh a month. No value is negative.

By year, TWh (2026 is January to August):

| | 2015 | 2016 | 2017 | 2018 | 2019 | 2020 | 2021 | 2022 | 2023 | 2024 | 2025 | 2026 |
|---|---|---|---|---|---|---|---|---|---|---|---|---|
| Production | 0.934 | 0.897 | 0.885 | 0.931 | 0.893 | 1.184 | 1.045 | 0.794 | 0.820 | 0.999 | 1.163 | 0.762 |
| Imports | 0.018 | 0.004 | 1.134 | 0.956 | 0.639 | 0.167 | 0.162 | 1.048 | 0.545 | 0.770 | 3.297 | 2.059 |
| Acquired from other sources | 3.304 | 3.318 | 2.324 | 2.965 | 2.825 | 3.251 | 3.005 | 2.596 | 3.278 | 3.065 | 0.000 | 0.000 |
| Exports | 0.000 | 0.000 | 0.000 | 0.000 | 0.000 | 0.000 | 0.000 | 0.094 | 0.465 | 0.465 | 0.348 | 0.232 |
| Gross inland consumption | 4.256 | 4.219 | 4.342 | 4.852 | 4.356 | 4.602 | 4.212 | 4.344 | 4.179 | 4.369 | 4.112 | 2.589 |
| Residential | 1.670 | 1.634 | 1.636 | 1.642 | 1.671 | 1.730 | 1.825 | 1.728 | 1.659 | 1.804 | 1.846 | 1.288 |

The production row equals header line 3's figures to two decimals.

- **The balance closes.** Gross inland consumption equals production plus imports plus acquired from other sources plus stock change less exports to 0.2 MWh in all 140 months (to the tenth in 137; 2018-05 0.2 MWh). Stock change is 0 in every month, so its sign is not tested.
- **"Acquired from other sources" stops in 2025.** It is 0 in every month from January 2025 to August 2026, and in 2017-04, 2017-05 and 2022-11; imports carry 3.297 TWh in 2025, against 0.004 to 1.134 TWh a year before. In November 2022 acquired is 0 and imports are 311.4 GWh. Over all months acquired is a median 0.654 of gross inland consumption (highest 0.989, 2016-08), imports a median 0.123 (highest 1.037, 2025-09, a month of exports).
- **Exports are almost nothing before 2022:** under 0.5 GWh a year from 2015 to 2021 (the median month is 8.8 MWh), then 0.094 to 0.465 TWh a year.
- **Residential consumption** is a median 0.394 of gross inland consumption (0.239 in 2020-10 to 0.650 in 2026-05), never above it.

## Placing values in time, and what is filled

StatBank gives years (2015 to 2026) and months (01 to 12) as two dimensions; `ts_utc` is the month's first day at 00:00Z. The figures are calendar months, and no hour is implied.

Of the answer's 1,008 cells (7 indicators by 12 years by 12 months), 28 are empty, each with status `..`: September to December 2026 for all seven indicators, not yet published. They have no row. Nothing is filled.

## License

Header line 9: "License: public, CC BY 4.0 (the bureau's terms of use of data, https://statistica.gov.md/en/terms-of-use-of-data-national-bureau-of-statistics-139_4417.html, session 2362). Source: National Bureau of Statistics of the Republic of Moldova, StatBank table ENE010100; reshaped by the ERW (renamed, the values unchanged)." `coverage.csv` and `sources.csv`: public. `license_tables.csv`: "National Bureau of Statistics of the Republic of Moldova (StatBank)", "the source registry".

`warehouse/metadata/license_verdicts.csv`, the bureau (read 621): "Reusing the content of this website, completely or partly, in original or modified, as well as its storage in a retrieval system, or transmitted, in any form and by any means, unless otherwise stated, will be made under the license Creative Commons Attribution 4.0 International License", verdict "may be public", if the ERW sells anything "may be public", contact "Dissemination and Communication Division, diseminare@statistica.gov.md". Its note: "The bureau's terms of use of data (updated 27 June 2022), covering StatBank: CC BY 4.0, commercial use allowed; the source named ("Source: National Bureau of Statistics of the Republic of Moldova") and a link to the material, and any change indicated." Header line 9 names the source, links the terms and states the change.

`docs/licenses.md`, the table's row: "may be public", flag public, "agrees", if the ERW sells anything "may be public", ERW verdict public. No row in `license_status.csv` or `paused_sources.csv`. `license_reads.csv`: reads 597 to 602 (session 2358: the robots address, HTTP 404; four listings of the API; the table's metadata) and 619 to 621 (session 2362: statistica.gov.md's robots file, "allows every path"; its English home page, which links the terms; the terms of use of data).

## Checks (session 2366)

The figures in this note were computed by `runs/c110/s2366/check_statbank_moldova_electricity_monthly.py` (output `check_statbank_moldova_electricity_monthly.out` beside it). It reads the rows of `warehouse/output/statbank_moldova_electricity_monthly.csv` in the main checkout past its 10 header lines (counted, never parsed as comments), the saved metadata and answer, session 2358's copies, and `eurostat_electricity_monthly` (entity `eurostat_elec:MD`, past its 11 header lines). No request was made.

- **The table:** 980 rows, 2015-01-01T00:00:00Z to 2026-08-01T00:00:00Z, as header lines 1 and 3 state; no (entity, variable, ts_utc) twice; rows in (variable, ts_utc) order; every `ts_utc` a month's first day; no blank value; `coverage.csv` agrees (980 rows, the same range, 7 nodes, validator pass, license public, last run 2026-10-24T08:42:52Z).
- **Against the saved answer:** 980 cells with a value and 980 rows, the same (code, month) pairs both ways; no value differs; every `node` is StatBank's text.
- **Eurostat holds Moldova from 2020-01 to 2026-07** (79 months of its flows and of its total net production), so each comparison covers those 79 months.
- **Exports against Eurostat's** (`flow:EXP`): within 0.6 MWh in all 79 months. The ratio's median is 1.0000, but the months are small (7.6 MWh against 7 MWh in 2020-01), so it runs from 0.9500 to 1.0857 and only 55 months are within 0.1 percent.
- **Imports plus acquired from other sources against Eurostat's imports** (`flow:IMP`): within 39.1 MWh in all 79 months, every month within 0.1 percent (0.9999 to 1.0001). This, more than the exports, fixes the unit as MWh. Imports alone are a median 0.1645 of Eurostat's and within 0.1 percent in only 20 months, those in which acquired is 0.
- **Production against Eurostat's net production** (`net_production:TOTAL`): median 1.1283 (10th percentile 1.0727, 90th 1.1694), by year from 1.1049 (2026) to 1.1521 (2023). Lowest 1.0006 (2024-05: 47,101.9 against 47,076 MWh), highest 1.2418 (2021-10). Five months are under 1.05: 2020-09 1.028, 2020-10 1.024, 2022-07 1.017, 2024-05 1.001 and 2025-06 1.042.

## Where the description and the data disagree

1. **"Retrieved: 20261024T084252Z ... by warehouse/connectors/statbank_moldova.py".** Header line 4 names the run that wrote the file as the retrieval. No connector run has made a request: the metadata was fetched at 08:29:41Z by session 2358's probe and the query sent by `runs/c110/s2358/query.py`, which wrote the saved file (`retrieved_at` 08:30:00Z). The docstring's "Ceiling: two requests (the metadata and the query), saved together in warehouse/raw/statbank_moldova/" describes a path no run has taken. Suggested: "Written: 20261024T084252Z (UTC), offline, by warehouse/connectors/statbank_moldova.py, from the metadata fetched at 08:29:41Z by session 2358's probe and the query answered at 08:30:00Z to runs/c110/s2358/query.py".
2. **"(session 2358)" on a file written in session 2362.** Header line 1, and `docs/redivis/release-v1/tables.csv`'s description, which copies it. The file on this machine is session 2362's run `20261024T084252Z`. Suggested: "(session 2358; written again offline in session 2362)".
3. **"Its production, gross".** The docstring ("its production, gross, is about 13 percent over Eurostat's net production") and `SESSION_2358_REPORT.md` ("its production, gross, is about 13 percent over"). StatBank's text is "Production", with neither gross nor net in the metadata or the answer. The ratio is 1.10 to 1.15 a year, as gross against net would be, but by month it runs from 1.0006 to 1.2418. Suggested: "production (StatBank does not say gross or net; it is 10 to 15 percent a year over Eurostat's net production, as gross production would be)".
4. **The Transnistrian plant.** The docstring and header line 3 ("The bureau's imports leave out the electricity bought from the Transnistrian region's plant, counted as acquired_from_other_sources") and the report. No such note is in the saved metadata or answer; the table's infofile (`Energetica_TS_en`) was not read. From January 2025 acquired from other sources is 0 in every month, and imports alone equal Eurostat's. Suggested: name where the bureau says it, and add "acquired_from_other_sources is 0 in every month from January 2025; from then imports alone equal Eurostat's".
5. **"The residential sector's share".** `SESSION_2358_REPORT.md` ("the residential sector's share"). The variable is consumption in MWh ("of which: consumed in the residential sector"), not a share. Suggested: "the residential sector's consumption".
6. **"Written 21 October 2026, session 489".** `docs/redivis/release-v1/tables.csv`, the table's reason ("held: not yet on Redivis (written 21 October 2026, session 489; the account's free 10 GB is full, session 363)"), the text `warehouse/redivis/release_v1.py` gives every table of its loop. This table was first written on 24 October 2026, in session 2358. Suggested: a reason of its own, "held: not yet on Redivis (written 24 October 2026, session 2358; public since session 2362)".
7. **No record of the run.** `CLAUDE.md` describes `run_status.csv` as "every run and every gap"; it holds no row of this table, only `runs/status/statbank_moldova.json`. Suggested: record the runs with `run_status.py record`.

Not acted on: this note changes no file but itself.

## The session report against the table

`SESSION_2358_REPORT.md`:

- "980 figures, January 2015 to August 2026": holds.
- "Variables (7)": holds.
- "StatBank's exports equal Eurostat's for Moldova ... median ratio 1.000 over 79 months": holds, to 0.6 MWh, on months as small as 7 MWh.
- "Its production, gross, is about 13 percent over Eurostat's net production": the median is 12.8 percent; "gross" is a reading (disagreement 3).
- "Imports plus that line equal Eurostat's imports in all 79 months": holds, within 39.1 MWh.
- "The months of 2026 not yet published (September to December) have no row": holds, 28 empty cells.
- "The test is `tests/test_session2358.py` (3 tests)": holds.

`SESSION_2362_REPORT.md`: "the table was written again offline (the same 980 rows)": holds (header line 10); "public since session 2362": holds in `coverage.csv`, `sources.csv`, `docs/licenses.md` and header line 9.

## What it does not hold

- Consumption other than the residential sector's (industry, services, transport), production by kind of plant, losses and the energy branch's own use, none of which this StatBank table gives; Eurostat's net production by fuel for Moldova, from 2020, is in `eurostat_electricity_monthly`.
- Months before January 2015, and September to December 2026, not yet published.
- Stock change other than 0.
- StatBank's earlier figures for a month it has revised, and any publication date (`vintage` blank).

Acted on in session 2366, the table written again offline (the same 980 rows): the header and docstring no longer say what acquired_from_other_sources holds (the bureau's table does not say; it is 0 from January 2025), say that production is not called gross or net by the bureau, name the sessions that wrote the file, and say that an offline run reads the saved answer; session 2358's report is corrected (the residential line is consumption, not a share). Recorded, not changed: the release package's boilerplate reason for every table, and the run's status in `runs/status/` only.
