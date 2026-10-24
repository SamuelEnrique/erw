# EIA-930's total interchange of every balancing authority and region, a day, from 2019 (type TI, EIA's Eastern day)

Energy Research Warehouse (ERW), method note written in session 2242 (chain 101) for a table first written on 2 October 2026 (session 68, an approved pull under a ceiling of 300,000 rows, commit `ef3c1e8a`, `archive/sessions/SESSION_68_REPORT.md`). The derived table built from it, `ba_supply_monthly`, is described in `docs/methods/grid_network.md`, "Who supplies a grid".

Tables: `eia930_daily_total_interchange`

## Publisher and address

U.S. Energy Information Administration (EIA), Form EIA-930, Hourly Electric Grid Monitor (`https://www.eia.gov/electricity/gridmonitor/`), through the EIA API v2: route `electricity/rto/daily-region-data`, `frequency=daily`, facets `type` TI (total interchange) and `timezone` Eastern. Each row's `source_url` is the exact page asked (a calendar month, an offset of up to 5,000 rows), with the key written `api_key=REDACTED`. Source id `eia930:daily_total_interchange` (`sources.csv`, license public). Raw pages under `warehouse/raw/eia930_daily_total_interchange/<run_id>/`, month checkpoints under `.../checkpoints/<YYYY-MM>.csv`.

Connector: `warehouse/connectors/eia930_daily_total_interchange.py` (session 68), no arguments; the key from `EIA_API_KEY`. It first asks how many rows EIA reports from 2019-01-01 and stops if they pass 300,000; then it asks EIA's newest day and goes month by month. A past month whose checkpoint exists is read from the checkpoint and not asked again; the current month, and a month without a checkpoint, are asked (and a past, complete month is saved as a checkpoint). A balancing authority and day given twice, or a type other than TI, stops the run; a row without a number is not written. The file is deleted and written whole each run.

Schedule: the data machine's daily run, step `dm_eia930_total_interchange` of `warehouse/run_data_machine_tables.sh` ("every day ... EIA's API; resumes by month from its checkpoints"), which `warehouse/run_data_machine.sh` sources; that run is registered with the Windows Task Scheduler by `scripts/register_data_machine_daily.ps1` ("ERW data machine daily"). When the table moved, `warehouse/table_stores.py` runs the validator, its coverage row, the archive and the Redivis draft. It is in that file's weekly load list (`WEEKLY_LIVE`), but `live_set.yaml` has no rule for it, so it is not loaded (the docstring: "history (not in the Supabase live set)"). No step of `run_daily.sh`, `run_monthly.sh`, `refresh_supply.sh`, `scheduled.py` or `.github/workflows/` runs it. Run logs on this machine: 15, from 20261013T030402Z to 20261023T172958Z. `run_status.csv` holds no row of it; `runs/status/eia930_daily_total_interchange.json` records run 20261023T172958Z, ok, "212,461 rows of the 300,000 ceiling, 83 balancing authorities, 2019-01-01 to 2026-10-22; 1,615 rows pulled this run". Readers: `warehouse/derived/ba_supply.py`, `warehouse/derived/watch.py` and the chat's table list.

## Vintage and revision

The header is run `20261023T172958Z`: "1,615 rows pulled this run; earlier months from checkpoints". The run log: "EIA reports 212,463 rows (Eastern days) from 2019-01-01"; the header: "2 rows without a number not written"; 212,461 rows held. `retrieved_at`: 210,846 rows on 2026-10-13 (the run of 13 October that asked every month again and saved the checkpoints) and 1,615 on 2026-10-23 (October 2026). `vintage` is blank.

EIA revises EIA-930 after first publication. Only the current month is asked again: a revision EIA makes to an earlier month after its checkpoint was saved does not reach the table, and a day EIA adds to such a month later is not taken either (disagreement 2).

## Shape and variables

Series, 212,461 rows, 83 respondents: 69 balancing authorities and EIA's 14 regional sums (US48, CAL, CAR, CENT, FLA, MIDA, MIDW, NE, NW, NY, SE, SW, TEN, TEX). `entity` `eia930:<respondent>`, `variable` `total_interchange_mwh`, `unit` MWh, `freq` P1D, `geo`, `market`, `node` and `vintage` blank, `ba` the respondent's code in lower case, `x_timezone` Eastern. Positive when the respondent exports on the day (net flow out), negative when it imports.

- Every value is a whole number of MWh. Lowest -365,982 (US48, 2026-07-20), highest 324,750 (NW, 2020-02-05); 323 zeros. US48's median day is -58,110.5 MWh (a net import of the Lower 48).
- Rows a year: 2019 28,368; 2020 28,247; 2021 28,161; 2022 27,948; 2023 27,610; 2024 27,349; 2025 23,433; 2026 (to 22 October) 21,345. Rows a day held: 59 to 79.
- Respondents that end: AEC (to 2021-09-01), EEI (2019-07-15 to 2020-02-29), GLHB (2020-02-29 to 2022-09-01), GRIF (to 2023-11-02), HGMA (to 2025-06-01), NSB (to 2020-01-07), WACM and WAUW (to 2026-03-31), WWA (to 2026-07-20), SPA (to 2026-10-20). Respondents that begin late: SIKE (2025-06-04), BHBA (2026-03-30), SWPW (2026-04-01).
- **46 days have no row at all**: 2025-11-06 to 2025-12-10 and 2025-12-21 to 2025-12-31. Apart from them, US48, CAL, CAR, CENT, FLA, MIDW, NW, SE and SW have every day, and MIDA, NE, NY, TEN and TEX lack 4 to 21 days more; a balancing authority lacks from 0 (EEI, GRIF, HGMA) to 411 (WWA) days within its own span, the 46 included (CISO 84, ERCO 64, PJM 57, MISO 63).

## Placing values in time, and what is filled

`ts_utc` is the day at 00:00:00Z (Decision 11), and the day is EIA's Eastern day for every respondent (`x_timezone`), as in `eia930_daily_interchange`, so the two tables share one day boundary. It is not a UTC day nor the respondent's own local day. A day EIA does not report has no row; nothing is filled, and no regional sum is recomputed from its members.

## License

Header: "License: public domain (U.S. Government data, EIA)." `license_verdicts.csv`, EIA (read 1): "U.S. government publications are in the public domain and are not subject to copyright protection. You may use and/or distribute any of our data, files, databases, reports, graphs, charts, and other information products that are on our website or that you receive through our email distribution service.", verdict "may be public"; EIA asks for the acknowledgment "Source: U.S. Energy Information Administration". `docs/licenses.md`, the table's row: EIA, "may be public", flag public, "agrees", ERW verdict public. No row in `license_status.csv`.

## Checks (session 2242)

The figures in this note were computed from the rows of `warehouse/output/eia930_daily_total_interchange.csv`, read past its 9 header lines (scripts `runs/c101/s2242/check_ti.py`, `check_ti_ciso.py` and `check_ti_gaps.py`, outputs beside them).

- 212,461 rows, 2019-01-01T00:00:00Z to 2026-10-22T00:00:00Z, as the header states; no (entity, variable, ts_utc) twice; every `ts_utc` at 00:00:00Z; `ba` is the lower-case code of `entity` in every row; no `source_url` carries a key.
- **The 46 days.** `eia930_daily_interchange` (the same EIA days, the pair report) lacks the same days and 2025-11-05 too; `eia930_daily_demand` (the same API route, type D) holds every day of November and December 2025. The checkpoints of 2025-11 and 2025-12 hold 1 to 5 November and 11 to 20 December only, and EIA's count on 23 October (212,463) equals the rows held plus the 2 without a number: on that day EIA's API itself gave no total interchange for the 46 days.
- **Against the sum of each respondent's own ties** (`eia930_daily_interchange`, 952,530 rows to 2026-10-21, its rows with `ba` the respondent, summed over the day): 211,310 respondent days in both; equal within 1 MWh on 146,208, within 1 percent of the total on 170,931. For the seven ISO balancing authorities, days equal within 1 MWh: ISNE 2,796 of 2,799, MISO 2,739 of 2,783, CISO 1,945 of 2,762, NYIS 987 of 2,796, ERCO 781 of 2,782, SWPP 20 of 2,533, PJM 8 of 2,787. 1,151 respondent days have a total and no tie of that respondent (SWPP 263, YAD 131, PSCO 103).
- **CAISO in detail.** Days equal within 1 MWh, by year: 2019 1 of 365, 2020 148 of 366, 2021 361 of 363, 2022 364 of 365, 2023 356 of 357, 2024 340 of 344, 2025 308 of 312, 2026 67 of 290. From 2025-12-17 the two differ by a few MWh on most days (median 4 MWh, at most 15 MWh on 2026-04-02, against totals near 200,000 MWh), with all eleven of CAISO's ties present every day. The pair table's CAISO rows were retrieved on 2 October (31,021 rows) and this table's on 13 October; neither table says whether EIA revised either report between.

## Where the description and the data disagree

1. **"Method: docs/methods/grid_network.md, 'Who supplies a grid'."** The docstring points there; that section is the method of `ba_supply_monthly` and names this table in one parenthesis, with session 68's 210,911 rows. This note is the table's own.
2. **"A day EIA does not report is absent."** It holds, but 46 days in November and December 2025 are absent for every respondent, and neither the header nor the docstring says so. Because a past month is read from its checkpoint and never asked again, those days will not be taken if EIA publishes them later; to take them, the checkpoints of 2025-11 and 2025-12 would have to be removed before a run.
3. **The metadata lag the table.** `coverage.csv` gives 212,384 rows to 2026-10-21 (last run 2026-10-22T17:30:20Z), and `archive_manifest.csv` 212,384 as of run 20261022T173105Z-local; the table holds 212,461 rows to 2026-10-22, written at 17:29:58Z on 23 October, whose stores had not yet been recorded when this note was written.

## The session report against the table

`SESSION_68_REPORT.md`, "The pulls, against their ceilings": "210,911 | 300,000 | 2019-01-01 to 2026-10-01, 83 respondents (EIA's regional sums among them)". The 83 respondents hold. The table now holds 210,920 rows dated 2019-01-01 to 2026-10-01, 9 more than session 68 wrote; it was pulled again whole on 13 October.

One claim does not hold in the table as it stands: "EIA's total interchange equals the sum of CAISO's ties to within 1 MWh on all 307 common days of the year" (September 2025 to August 2026). Over those twelve months the two tables share 311 CAISO days, and the total equals the sum of the ties within 1 MWh on 123; on the other 188, all from 2025-12-17 on, they differ by 2 to 15 MWh. Session 68 compared on `ba_supply_monthly`'s held days with the tables as they stood on 2 October; the difference is far too small to move the report's percentages (16.49 against 16.49 percent of demand), but "to within 1 MWh on all" is not what the rows now show.

## What it does not hold

- The hourly total interchange (EIA type TI by the hour is not pulled; the hourly pair interchange is `eia930_all_interchange`, a rolling window, and `eia930_event_hourly_interchange`, two event windows); the interchange of each pair (`eia930_daily_interchange`); UTC or local days; days before 2019; the 46 days of late 2025; EIA's earlier versions of a revised day.
