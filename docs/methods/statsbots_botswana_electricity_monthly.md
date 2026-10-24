# Botswana's electricity a month from Statistics Botswana's Electricity Generation and Distribution Stats Brief: local generation, imports and distribution, January 2016 to June 2026, and the second quarter of 2026 by source

Energy Research Warehouse (ERW), method note written in session 2429 (chain 115) for a table first written on 24 October 2026 (session 2421 of chain 115, `archive/sessions/SESSION_2421_REPORT.md`, commit `2e433a31`), and written again offline in session 2425 when its license became public (`archive/sessions/SESSION_2425_REPORT.md`, commit `04ce76cf`). Ember's yearly demand for Botswana, against which session 2421 compared it, is in `owid_ember_electricity_annual` (entity `owid_energy:BWA`).

Tables: `statsbots_botswana_electricity_monthly`

## Publisher and address

Statistics Botswana, "Electricity Generation and Distribution Stats Brief", the second quarter of 2026 when written. The connector reads the home page, takes the newest brief it links, and reads that PDF, both by GET without a key:

- `https://www.statsbots.org.bw/`
- `https://www.statsbots.org.bw/sites/default/files/Electricity%20Generation%20and%20Distribution%20Stats%20Brief%2C%20Second%20Quarter%202026.pdf`

Source id `statsbots:electricity_stats_brief` (`sources.csv`: license public, first and last seen 2026-10-24). Read: the brief's tables 3, 7 and 11 (generation, imports and distribution a month, with quarter and year totals) and tables 2 and 10 (the quarter's generation and imports by source), with pdfplumber's text, each from its last title (the table of contents comes first). The indices and percentage changes (tables 1, 4 to 6, 8, 9, 12 to 14) are not taken.

Saved files, in `warehouse/raw/statsbots_botswana/20261024T104905Z_probe/`, fetched by session 2421's probe, not by the connector:
- the home page, 194,858 bytes, sha256 `9ebcd7c3...`, at 2026-10-24T10:49:26Z;
- the brief, 2,384,893 bytes, sha256 `9ba2a347...`, at 2026-10-24T10:49:35Z, Last-Modified "Tue, 29 Sep 2026 07:03:14 GMT".

The connector's run folders (`20261024T105340Z`, an empty manifest; `20261024T105351Z` and `20261024T111816Z`) hold only the data-lock check, so its runs were offline. www.statsbots.org.bw's robots file (read 767) asks a crawl delay of 10 seconds, disallows Drupal's system paths and `/search/`, and names no AI agent. Session 2421 made 4 requests of 15 (the robots file, the home page, the brief, the terms of use) and reports them 10 seconds apart; the manifest's whole-second stamps for the home page and the brief are 9 seconds apart (what instant the probe stamps, the request or the end of the answer, is not read here).

Connector: `warehouse/connectors/statsbots_botswana.py` (session 2421, license lines changed in session 2425), `[--offline] [--out-dir DIR]`.
- **Ceiling:** two requests, 10 seconds apart online. The home page is fetched again on every online run (`fresh`); the brief is reused when a file for its address is saved, and a new quarter's brief has a new address. A paused `statsbots` or host www.statsbots.org.bw is never asked.
- **Values:** MWh as printed; nothing is converted.
- **Stops:** a header not the brief's, a value that is not a number, a month not read or twice, a year's months not adding to its printed quarters and total within 2 MWh, a month's distribution not equal to generation plus imports within 1.5 MWh (one exception, below), a quarter's sources not adding to its total within 1 MWh, or those totals not equal to the monthly tables' quarter within 1 MWh.
- **The one exception:** a month whose printed distribution equals its generation, with imports above 0, is not written and is named in the header; the printed quarter and year totals are then checked against generation plus imports for that month.

## Schedule and records

Schedule: none. No shell script under `warehouse/`, no workflow in `.github/workflows/`, no file in `scripts/` and not `warehouse/scheduled.py` names it.

Records:
- `runs/status/statsbots_botswana.json` (main checkout): run `20261024T111816Z`, ok, "383 rows". `run_status.csv`: no row.
- `archive_manifest.csv`: 383 rows, run `20261024T111822Z-local` (session 2425's rewrite), `data_sha256` `e38cec47...`, which is the data hash of the file in the main checkout (recomputed in session 2429).
- `coverage.csv`: iso `statsbots`, 1 node, interval `P1M;P3M`, 2016-01-01 to 2026-06-01, 383 rows, last run 2026-10-24T11:18:16Z, validator pass, license public, sector power, tier source.
- Live set: listed under `catalogue_hold` in `warehouse/supabase/live_set.yaml`, not loaded.
- Release: `docs/redivis/release-v1/tables.csv` lists it as held ("not yet on Redivis"; in `STORAGE_HELD` in `warehouse/redivis/release_v1.py`), with its 9 variables in `variables.csv`. No row in `redivis_uploads.csv` or `redivis_uploads_stanford.csv` when this note was written; session 2425's report names session 2429 for the Stanford upload.
- Package: `package/src/erw/data/tables.csv` (public), `site/data/table_citations.json` and `table_verdicts.json` have its rows since session 2431.
- `license_tables.csv`: Statistics Botswana, "the source registry".

Readers: none. `tests/test_session2421.py` (5 tests) tests the reader on text built in the test.

License: `license_verdicts.csv`, read 769 (session 2421's read of the terms of use, `https://www.statsbots.org.bw/terms-use`): "users may utilise the information as they wish, provided that they acknowledge Statistics Botswana as the source of the basic data wherever they process, apply, utilise, publish or distribute the data", verdict "may be public", the same if the ERW sells anything (session 2425); the note adds that users must say an application or analysis is their own processing. Header line 9 states this. `docs/licenses.md`, the table's row: "may be public", flag public, "agrees", ERW verdict public.

## Vintage and revision

Two writes, both offline from the saved files: session 2421's (run `20261024T105351Z`; its header is not kept) and session 2425's (run `20261024T111816Z`), whose header line 10 reads "This run wrote 383 rows: 0 new, 383 replacing earlier rows ...; 0 rows are kept from earlier runs." `retrieved_at` is 2026-10-24T10:49:35Z in every row, the probe's fetch of the brief. `vintage` is 2026-09-29T07:03:14Z in every row, the brief's Last-Modified.

The brief is quarterly and repeats the months since January 2016; a run after the next brief is linked reads it and replaces rows by (entity, variable, ts_utc). A figure the bureau revises is replaced; no earlier version is kept. The by-source rows are the one quarter of the brief read.

## Shape and variables

Series, 383 rows, 13 columns (`entity, variable, ts_utc, value, unit, freq, geo, market, node, source, source_url, retrieved_at, vintage`), 10 header lines. `entity` `statsbots_bw:BW` in every row; `node` Botswana; `geo` BW; `unit` MWh; `market` blank.

| Variable | freq | Rows | From | To | Lowest | Highest |
|---|---|---|---|---|---|---|
| generation (generated locally) | P1M | 126 | 2016-01 | 2026-06 | 73,018 (2018-10) | 395,124 (2026-06) |
| imports | P1M | 126 | 2016-01 | 2026-06 | 34,746 (2017-07) | 249,014.7 (2018-10) |
| distribution | P1M | 125 | 2016-01 | 2026-06 | 259,418 (2020-04) | 460,018 (2023-07) |
| generation_coal, generation_diesel, generation_solar | P3M | 1 each | 2026-04 | 2026-04 | | |
| imports_eskom, imports_sapp_markets, imports_cross_border | P3M | 1 each | 2026-04 | 2026-04 | | |

- **`ts_utc`:** the month's 1st at 00:00:00Z for P1M; the quarter's first day (2026-04-01) for P3M. The P3M rows share the entity and the key space with the monthly rows, under other variable names.
- **The quarter by source,** April to June 2026, MWh: coal 894,024.9, diesel 3,136.5, solar 97,361.0 (994,522.4); Eskom 135,444.0, the SAPP markets 18,889.0, cross-border 28,858.0 (183,191.0).
- **Values:** no zero, no negative. Generation and distribution are whole numbers; 64 import rows, from August 2017 on but not every month, carry one decimal, as printed.
- **The missing distribution month:** February 2026 (below).
- **Years,** GWh (sums of the months written): generation, imports, distribution: 2016 2,374.2, 1,554.5, 3,928.7; 2017 3,020.2, 752.1, 3,772.3; 2018 2,729.9, 1,189.5, 3,919.3; 2019 2,204.8, 1,746.2, 3,951.0; 2020 2,004.2, 1,837.7, 3,841.9; 2021 2,143.6, 1,784.5, 3,928.1; 2022 3,173.4, 1,091.8, 4,265.2; 2023 3,094.8, 1,640.7, 4,735.5; 2024 3,428.9, 1,384.5, 4,813.5; 2025 2,515.2, 1,863.9, 4,379.1; January to June 2026 1,896.4, 403.5, 1,955.1 (five months of distribution). Imports are 19.9 (2017) to 47.8 percent (2020) of generation plus imports in the full years, and 17.5 percent in January to June 2026.

## Checks

Counted in session 2429 from the table in the main checkout (`C:\Users\Shared\Documents\erw\warehouse\output`), read past its 10 header lines with `keep_default_na=False`, by scripts outside the repository. No request was made, and the brief's PDF was not read again.

- 383 rows, 2016-01-01 to 2026-06-01, as header line 10 states; no (entity, variable, ts_utc) twice; no blank value; one `retrieved_at`, one `vintage` and one `source_url` in every row.
- **Distribution equals generation plus imports** in all 125 months written: 52 to the MWh, 104 within 0.5 MWh, the largest difference 1.0 MWh (in 9 months, from November 2023 on).
- **February 2026:** generation 292,427 MWh and imports 52,412, so generation plus imports is 344,839; the brief's distribution, 292,427 (header line 3), is the generation figure again and has no row. The first quarter's printed distribution total, 1,122,208 MWh (the docstring and the report), equals January's 363,512 plus 344,839 plus March's 413,857 exactly.
- **The quarter by source against the months:** generation's sources add to 994,522.4 MWh against 994,522.0 for April to June in the monthly rows; imports' to 183,191.0, equal.
- **The printed quarter and year totals** are not in the table, so the connector's check of the months against them is not repeated here.
- **Against Ember** (`owid_ember_electricity_annual`, `owid_energy:BWA`, `electricity_demand`, MWh, to 2024): distribution summed over the year is 0.890 (2017) to 1.122 (2019) times Ember's demand over 2016 to 2024, and 0.999 in 2023, as the report says.

## What it cannot say

- **Sources a month:** the split by coal, diesel and solar and by Eskom, the SAPP markets and cross-border supply is for the brief's one quarter only; the earlier quarters' splits are in earlier briefs, not read.
- **Distribution for February 2026,** left out as printed; generation plus imports is the figure the brief's totals imply, and it is not filled.
- **Consumption by sector, customers, tariffs, exports and peak demand:** not taken from the tables read; whether the brief gives exports is not read here.
- **Months before 2016,** and the bureau's earlier versions of a month.
- **What "distribution" measures:** in the table it equals generation plus imports; whether the brief means power sent to the network or power sold, and where losses and own use fall, is not read here.

## Acted on in session 2429

The two helpers who drafted this chain's notes made no request and changed no other file; every point was read and acted on or recorded:

- **The crawl delay:** session 2421's own probe asked the home page (10:49:26Z) and the brief (10:49:35Z) 9 seconds apart, one second short of the robots file's 10. The probe's pause applied only within one run, and the two requests were two runs. The connector itself waits 10 seconds between them. Session 2421's report is corrected, saying so.
- **Nothing else to act on:** the checks agree with the connector, its header and session 2421's and 2425's reports.
