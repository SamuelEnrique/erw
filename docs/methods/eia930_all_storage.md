# EIA-930's hourly battery net generation (fuel type BAT) for ERCOT, ISO-NE, MISO, SPP and the Lower 48, from November 2024

Energy Research Warehouse (ERW), method note written in session 2298 (chain 105) for a table first written on 29 September 2026 (session 31, `archive/sessions/SESSION_31_REPORT.md`, "Battery storage (B1): a pull", commit `707a3715`). Its section in `docs/methods/storage.md` ("eia930_all_storage (source)") gives the route, the sign, the partition and which respondents report BAT, beside the daily cycle and the fleet built from it; this note does not repeat them. The same series for the newest weeks is `net_generation_battery_mw` in `eia930_all_generation`; CAISO's own battery output is `caiso_battery_storage`.

Tables: `eia930_all_storage`

## Publisher and address

U.S. Energy Information Administration (EIA), Form EIA-930 (Hourly Electric Grid Monitor), `https://www.eia.gov/electricity/gridmonitor/`, through EIA's API v2, route `electricity/rto/fuel-type-data` (`https://api.eia.gov/v2/electricity/rto/fuel-type-data/data/`), frequency hourly, facets `respondent` (ERCO, ISNE, MISO, SWPP, US48) and `fueltype` BAT, one respondent and calendar month a request, sorted by period and respondent, paged by 5,000 (`eia930.fetch_route`). The key comes from `EIA_API_KEY` and is replaced by `REDACTED` in every stored URL (all 73,224 rows, each with the BAT facet). Source id `eia:electricity/rto/fuel-type-data`, which `sources.csv` shares with the eight `eia930_<ba>_generation` members and `eia930_generation_latest`. Raw files under `warehouse/raw/eia930_storage/<run_id>/`: four run folders on this machine, all of 19 October 2026, and 65 month checkpoints (`<ba>_<YYYY-MM>.csv`) under `.../checkpoints/`; their four run logs are in `warehouse/output/logs/`.

Connector: `warehouse/connectors/eia930_storage.py` (session 31), `--days N` or `--since YYYY-MM-DD`, and `--ba` to narrow the five. `NO_BAT = ["ciso", "nyis", "pjm"]` are never asked. A past month is kept as a checkpoint and read from it on the next run; a month that ends within the last 40 days is always asked again. Completeness per BA and UTC day: "a day is written only when every one of its 24 hours has a value"; each day from the first hour the run received to the window's end that falls short is a gap row ("net_generation_battery_mw: k of 24 hours; day not written"). The run merges by (entity, variable, ts_utc) into the file; nothing trims it.

Schedule: the daily run, `warehouse/run_daily.sh`: `pull eia930_storage "$PYTHON" warehouse/connectors/eia930_storage.py --days "$DAYS"` (3 days by default) right after `eia930.py`; `run_other storage_daily_cycle` reads it later in the run. GitHub runner, `.github/workflows/daily-prices.yml` (cron `0 14 * * *`, started by pg_cron through `workflow_dispatch`). The table is restored before the run (`warehouse/redivis/config.yaml`, `'^eia930_all_storage$'`, "EIA-930 battery storage keeps its history from 2024 by merging"). No step of `run_data_machine.sh`, `run_data_machine_tables.sh`, `run_monthly.sh`, `refresh_supply.sh` or `warehouse/scheduled.py` runs it.

`run_status.csv`: 263 rows, 21 ok and 242 gap (233 local, 30 GitHub). `archive_manifest.csv`: 73,224 rows as of run `20261023T152740Z-github`. Live set: `recent` (35 days), `'^eia930_all_storage$'`. Readers: `warehouse/derived/storage_daily_cycle.py`, `warehouse/derived/network_stories.py`, `warehouse/analysis/findings/hunt_measures.py` (ERCO), `warehouse/analysis/watch.py`, the chat's tools (`warehouse/chat/tools.py`, `ercot.py`, `look_tables.py`, `site/lib/chat/forms.ts`), `site/app/storage/page.tsx` (the last 31 days), `site/app/network/data.ts`, `site/lib/gridtables.ts` and `package/llms.txt`.

## Vintage and revision

The copy here was rebuilt from the ERW's archive "as of run 20261023T152740Z-github" (header line 1); the newest run is `20261023T143139Z`: "This run wrote 360 rows: 120 new, 240 replacing earlier rows with the same (entity, variable, ts_utc); 72864 rows are kept from earlier runs." `vintage` is blank in every row. A daily run asks for three UTC days of five respondents (360 hours) and has found them whole on every run but two, so each day is asked on three runs. The archive keeps a row's `retrieved_at` from the run that first archived its value.

`retrieved_at` has 176 values. 69,535 rows carry session 31's pull of 29 September 2026 (2024-11-01 to 2026-09-26; the rest of that pull's 70,416 rows have since been replaced by revised values). 1,233 rows carry 19 October: 1,113 of US48 from session 309's re-ask from 2024-07-15 (`--since 2024-07-15 --ba us48`, which "added 72 rows and filled none" of the missing days), ERCO's 2026-10-15 from session 325's `--since 2025-12-01 --ba erco`, and 2026-10-16 from that day's daily run. The rest come from the daily runs, 96 to 360 rows a run.

## Shape and variables

Series, 73,224 rows, 14 columns: the series columns and `ba`. One variable, `net_generation_battery_mw`, unit MW, `freq` PT1H; entity `eia930:<respondent>`; `geo` the respondent's states (US for US48); `market`, `node` and `vintage` blank in every row. Every value a whole number.

| ba | Rows | First hour | Days held | Days missing inside | Mean | Lowest (hour) | Highest (hour) | Hours positive, negative, zero |
|---|---|---|---|---|---|---|---|---|
| erco | 17,112 | 2024-11-07T00 | 713 | 2025-12-05, 2025-12-06 | 237.1 | -11,553 (2026-09-10T14) | 11,928 (2026-09-03T00) | 12,268, 4,841, 3 |
| isne | 17,136 | 2024-11-07T00 | 714 | 2026-10-15 | 25.1 | 0 | 516 (2026-03-02T23) | 17,027, 0, 109 |
| miso | 15,456 | 2025-01-16T00 | 644 | 2026-10-15 | -12.2 | -867 (2026-07-07T07) | 931 (2026-10-13T22) | 6,681, 8,671, 104 |
| swpp | 6,216 | 2026-02-05T00 | 259 | 2026-10-15 | 36.2 | 0 | 447 (2026-09-29T22) | 3,418, 0, 2,798 |
| us48 | 17,304 | 2024-11-01T00 | 721 | none | 656.3 | -12,500 (2026-09-10T14) | 16,063 (2026-09-04T00) | 10,357, 6,872, 75 |

MW; every series ends at 2026-10-22T23:00:00Z; hours are UTC hour starts of 2024 to 2026. Rows a year: 4,104 (2024), 34,632 (2025) and 34,488 (2026 to 22 October).

- **Charging is not in every series.** ISNE's and SWPP's values are never negative. ERCO's are never negative before 2025-12-15T06:00Z (9,432 hours before 5 December 2025, the lowest 1 MW); from that day ERCO has 4,841 negative hours. MISO is negative from its first day, US48 from 2024-11-05. So ERCO's MWh charged is 0 in November 2025 (539,216 MWh discharged) and 671,660 MWh in January 2026 (522,770 discharged). From 1 January 2026 to the newest hour, MWh discharged over MWh charged: ERCO 0.789 (6,188,363 against 7,840,267), MISO 0.812, US48 1.353.
- **Growth.** ERCO's highest hour a month rose from 3,695 MW (November 2024) to 11,928 MW (September 2026); US48's from 3,844 to 16,063 MW.
- **US48 is not the sum of the four.** Over the 6,216 hours all five hold (from 2026-02-05), where US48 discharges more than 500 MW (2,590 hours) the four ISOs' sum is a median 0.469 of it (10th percentile -0.238, 90th 0.842); the four's sum exceeds US48 in 2,271 of the 6,216 hours.

## Placing values in time, and what is filled

`ts_utc` is the start of the hour in UTC (EIA's `period`, the end of the hour, less one hour). Days are UTC days: all 3,051 BA-days held have 24 hours. Nothing is filled: a day with a missing hour has no row.

Days not held inside each series: ERCO's 2025-12-05 and 2025-12-06 (gap rows; session 325: "EIA's API still lacks hours"), and 2026-10-15 for ISNE, MISO and SWPP, with no gap row. The run of 15 October wrote 12 to 14 October; no run pulled the table again until 19 October, whose window began on 2026-10-16. ERCO's and US48's 15 October came from the re-asks of sessions 325 and 309. EIA has those hours: `eia930_all_generation` holds the 72.

Before each series' first day held: US48's 109 days from 2024-07-15 to 2024-10-31 and each BA's first BAT day (ERCO and ISNE 2024-11-06, MISO 2025-01-15, SWPP 2026-02-04), which EIA reports only in part. Session 325 closed these 113 as known gaps.

## License

The header has no License line. `coverage.csv` and `sources.csv`: public. `warehouse/metadata/license_verdicts.csv`, EIA (read 1): "U.S. government publications are in the public domain and are not subject to copyright protection. You may use and/or distribute any of our data, files, databases, reports, graphs, charts, and other information products that are on our website or that you receive through our email distribution service.", verdict "may be public", if the ERW sells anything "may be public"; the note asks for the acknowledgment "Source: U.S. Energy Information Administration". `docs/licenses.md`, the table's row: EIA, "may be public", flag public, "agrees", ERW verdict public. `license_tables.csv`: EIA, "the source registry". No row in `license_status.csv`.

## Checks (session 2298)

The figures in this note were computed from the rows of `warehouse/output/eia930_all_storage.csv`, read past its 11 header lines (counted), streamed by `runs/c105/s2298/check_eia930_all_storage.py` (output `check_eia930_all_storage.out` beside it).

- 73,224 rows and the range 2024-11-01T00:00:00Z to 2026-10-22T23:00:00Z, as header line 11 states; no (entity, variable, ts_utc) twice; no blank value and none that is not a number; every `ts_utc` on the hour; `coverage.csv` agrees (73,224 rows, 5 entities, the same range, validator pass).
- **Against `eia930_all_generation`** (the same route and fuel type, pulled by `eia930.py`): it holds `net_generation_battery_mw` for the same five respondents, 1,392 hours each, 2026-08-26 to 2026-10-22. 6,888 hours are in both: 6,866 equal. The 22 that differ are 20 US48 hours of 8 and 9 October (the largest 101 MW: -1,209 here, retrieved 2026-10-19T10:55:53Z, against -1,310 there, retrieved 10:51:57Z the same morning) and 2 ISNE hours of 14 October. Every hour here from 26 August is there; the 72 there and not here are ISNE's, MISO's and SWPP's 2026-10-15.
- **`run_status.csv`:** 120 distinct BA-days have gap rows: the 115 above (from session 31's pull, and again from session 309's re-ask) and each BA's 2026-10-19, short (3 or 4 of 24 hours) on the two runs of 20 October and held since.

## Where the description and the data disagree

1. **"The rolling 30 days" of the generation table.** The connector's docstring ("eia930_all_generation carries the same series, but only for the rolling 30 days of that table"), `docs/methods/storage.md` ("only for its rolling 30 days") and `SESSION_31_REPORT.md` ("only for its rolling 30 days"). Nothing trims `eia930_all_generation`: it holds 58 days, from 2026-08-26, 1,392 battery hours a respondent.
2. **US48 "from 2024-07-15" and "every hour from the series start".** The docstring, header line 9 ("their BAT series start ... 2024-07-15") and `storage.md` ("This table keeps every hour from the series start") give EIA's first BAT hour. The table holds US48 from 2024-11-01, ERCO and ISNE from 2024-11-07, MISO from 2025-01-16 and SWPP from 2026-02-05; `package/llms.txt` ("2024-11 for ERCO, ISNE and US48") and `warehouse/chat/ercot.py` ("since 2024-11-07") are right.
3. **The span of US48's 109 days.** `SESSION_309_REPORT.md` ("The 109 US48 days of July 2024 to January 2026") and `SESSION_325_REPORT.md` ("US48 2024-07-01 to 2026-01-31"). The 109 days are 2024-07-15 to 2024-10-31; US48 misses no day from 2024-11-01.
4. **"Negative while charging."** Header line 3, the docstring, `storage.md` and `warehouse/chat/ercot.py` ("negative when it charges", for ERCO). ISNE and SWPP are never negative, and ERCO never before 2025-12-15T06:00Z: for them, over those spans, charging is not in the series, and a zero or small positive hour is not an idle battery.
5. **"Each is a gap row."** Header line 10 and the docstring say every day not written is a gap row. 2026-10-15 is missing for ISNE, MISO and SWPP and no row names it; the daily runs of 15 and 19 October whose rows the table holds have no row in `run_status.csv`.
6. **"EIA-930 carries no battery series."** The comment above `caiso_outlook` in `warehouse/run_daily.sh` ("Session 23: CAISO battery storage output ... (EIA-930 carries no battery series)"). EIA-930 carries BAT for the five respondents here; it is CAISO (with NYISO and PJM) that reports none.
7. **"The hourly series below, last 90 days."** `warehouse/supabase/live_set.yaml`'s comment for `/storage` and `SESSION_31_REPORT.md` ("the last 90 days: 10,735 rows"). The rule that loads the table is `recent`, 35 days since session 36C.

Not acted on: this note changes no file but itself. The missing days are EIA's or the schedule's, recorded, not changed.

## The session report against the table

`SESSION_31_REPORT.md`: "70,416 new rows", hours written US48 16,728, ERCO 16,536, ISNE 16,584, MISO 14,904, SWPP 5,664, with 115 BA-days left out, and "CISO, NYIS, PJM: none (the API returns 0 rows)". The table's rows before 2026-09-29, the end of that pull, are exactly those five counts (70,416). Its check against `eia930_all_generation`, "120 overlapping hours ... 119 equal", reads 6,866 of 6,888 today. The live set's 90 days are 35 now.

## What it does not hold

- CISO, NYIS and PJM (no BAT series in EIA-930; CAISO's own batteries are `caiso_battery_storage`); any other respondent, which the connector does not ask; US48 before 2024-11-01 and each BA's first BAT day; the six missing BA-days named above; charging for ISNE and SWPP, and for ERCO before 15 December 2025; EIA-930's other storage types (pumped storage, solar or wind with battery, other and unknown storage), which are variables of `eia930_all_generation`; capacity (`storage_capacity`) and the daily cycle (`storage_daily_cycle`); EIA's earlier versions of a revised hour.
