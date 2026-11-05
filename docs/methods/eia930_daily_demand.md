# EIA-930's daily demand of every respondent, balancing authorities and EIA's regions, Eastern days from 1 January 2019

Energy Research Warehouse (ERW), method note written in session 2284 (chain 104) for a table first written on 4 October 2026 (session 109, `archive/sessions/SESSION_109_REPORT.md`, "The network, version 3, finished", an approved pull; commit `ee6954ba`). Its first use, the share of demand in the network's replay, is described in `docs/methods/grid_network_v3.md`, "The replay's share of demand (session 109)"; this note describes the table.

Tables: `eia930_daily_demand`

## Publisher and address

U.S. Energy Information Administration (EIA), Form EIA-930 (Hourly Electric Grid Monitor), `https://www.eia.gov/electricity/gridmonitor/`, through EIA's API v2, route `electricity/rto/daily-region-data` (`https://api.eia.gov/v2/electricity/rto/daily-region-data/data/`), frequency daily, facets `timezone` Eastern and `type` D, a calendar month a request, paged by 5,000. The key comes from `EIA_API_KEY` and is replaced by `REDACTED` in every stored URL (all 191,785 rows). Source id `eia930:daily_demand`. Raw files on this machine: `warehouse/raw/eia930_daily_demand/checkpoints/` (93 months, 2019-01 to 2026-09) and the run folder `20261004T215035Z/` (98 files).

Connector: `warehouse/connectors/eia930_daily_demand.py` (session 109), ceiling 300,000 rows. The full pull counts the rows EIA reports for the whole span first and stops if they pass the ceiling; it goes a month at a time, keeping a past month as a checkpoint. `--days N` (session 114) asks for the days from N days before today to EIA's newest day and merges them by (entity, variable, ts_utc); it never starts a table (where the table is absent it asks EIA for nothing). Entity `eia930:<respondent>`, `ba` the respondent in lower case; a value that is not a number is not written.

Schedule: the daily run, `warehouse/run_daily.sh`: `soft_step eia930_daily_demand ... warehouse/scheduled.py eia930_daily_demand`, which runs `eia930_daily_demand.py --days 5` (`REPLAY_DAYS`, "EIA revises a day for a few days after it"), the table first rebuilt from the ERW's archive on the runner (`restore`); then the `network_replay` step reads it. GitHub runner, `.github/workflows/daily-prices.yml` (cron `0 14 * * *`, started by pg_cron through `workflow_dispatch`). No step of `run_data_machine.sh`, `run_data_machine_tables.sh`, `run_monthly.sh` or `refresh_supply.sh` runs it. `run_status.csv`: 15 rows, all ok. `archive_manifest.csv`: 191,785 rows as of run `20261023T152740Z-github`. Live set: held from it (`live_set.yaml`, `catalogue_hold`: "nothing reads it from Supabase"). Readers: `warehouse/derived/network_daily.py` (the replay's files), the findings `batteries_lunch_grids.py`, `hunt_measures.py` and `impact_study.py`, `warehouse/analysis/watch.py`, `site/lib/gridtables.ts`.

## Vintage and revision

The copy here was rebuilt from the archive "as of run 20261023T152740Z-github" (header line 1); the newest run is `20261023T150953Z` (`--days 5`): "this run asked for 2026-10-18 to EIA's newest day (2026-10-22)", "This run wrote 334 rows: 67 new, 267 replacing earlier rows". `vintage` is blank in every row. `retrieved_at` has 109 values: 190,248 rows from session 109's pull on 4 October 2026, then about 67 rows a day from the daily runs of 5 to 23 October (268 on the 15th, 334 on the 23rd). A day is asked for again on five daily runs, then kept as it was.

## Shape and variables

Series, 191,785 rows, 15 columns: the series columns, `ba` and `x_timezone` (Eastern in every row). One variable, `demand_mwh`, unit MWh, `freq` P1D. `geo`, `market`, `node` and `vintage` are blank in every row. 71 respondents, 2,852 days from 2019-01-01 to 2026-10-22; 62 to 69 respondents a day (66 on the newest day).

- **57 balancing authorities and 14 of EIA's regions** (CAL, CAR, CENT, FLA, MIDA, MIDW, NE, NW, NY, SE, SW, TEN, TEX and US48; 39,928 rows). Five regions are one balancing authority and repeat its values exactly: MIDA is PJM (2,851 of 2,851 days), NE is ISNE, NY is NYIS, TEN is TVA and TEX is ERCO (2,852 of 2,852 each). A sum over entities counts those twice and counts every BA again in its region and in US48.
- **50 respondents hold every day** of the span. Those that start or stop: AEC ends 2021-09-01 (975 days); NSB holds 2019-01-01 to 2020-01-07 (363 days); WACM and WAUW end 2026-04-01; BHBA begins 2026-03-30 and SWPW 2026-04-02. SEC lacks 304 days, SPA 63 (and ends on 2026-10-21), GVL 55, SCEG 48, TEPC 38.
- Rows a year: 24,847 (2019), 24,863, 24,658, 24,448, 24,441, 24,514, 24,363 (2025) and 19,651 (2026 to 22 October).
- **Eight days of 0 MWh** are held as EIA reports them: SEC (2020-03-17, 2020-04-11 and 2020-04-12), TIDC (2019-11-29 to 2019-12-01), NWMT (2019-01-02) and PNM (2020-11-22). No value is negative.
- US48's highest day is 15,349,589 MWh (2025-07-29); its median 11,032,828.

## Placing values in time, and what is filled

`ts_utc` is the day at 00:00:00Z (Decision 11), a label: the day is EIA's Eastern day for every respondent (`x_timezone`), the same boundary as `eia930_daily_interchange` and `eia930_daily_total_interchange`, not a UTC day nor the respondent's own local day. EIA's value is its own sum of the hours it holds for the day, faulty hours included (the docstring; `docs/methods/impossible_hours.md`). Nothing is filled: a day EIA does not report has no row.

## License

Header: "License: public domain (U.S. Government data, EIA)." `license_verdicts.csv`, EIA (read 1): "U.S. government publications are in the public domain and are not subject to copyright protection. You may use and/or distribute any of our data, files, databases, reports, graphs, charts, and other information products that are on our website or that you receive through our email distribution service.", "may be public" (and if the ERW sells anything). `docs/licenses.md`, the table's row: EIA, "may be public", flag public, "agrees", ERW verdict public. No row in `license_status.csv`.

## Checks (session 2284)

The figures in this note were computed from the rows of `warehouse/output/eia930_daily_demand.csv`, read past its 10 header lines (counted), with `runs/c104/s2284/check_daily_demand.py` and `check_regions.py` (outputs beside them).

- 191,785 rows and the range 2019-01-01 to 2026-10-22, as header line 10 states; no (entity, variable, ts_utc) twice; no blank value; every `ts_utc` a midnight; `entity` is `eia930:` and `ba` in capitals in every row; one unit and one variable.
- **Against the hourly table** (`eia930_all_demand`, route `region-data`, type D): the hourly demand summed over each Eastern day that table holds whole equals this table's value exactly on every such day of the seven ISOs (CISO 57, ERCO 50, ISNE 57, MISO 57, NYIS 53, PJM 57, SWPP 54 days, 26 August to 22 October 2026). US48 equals on 2 of 57 days; the median ratio is 1.00000 and the largest gap 47,782 MWh (2026-10-01): EIA's daily US48 is not exactly the sum of its hourly US48 values.
- The five regions that are one BA equal that BA on every day both hold (above).

## Where the description and the data disagree

1. **"Demand of every balancing authority."** The docstring's first line and header line 2 say "demand of every balancing authority". 14 of the 71 entities are EIA's regions and the Lower 48, not balancing authorities, and five of them repeat a BA's figures. Session 109's report says it rightly: "71 respondents (balancing authorities and EIA's regions)".
2. **Coverage names seven grids.** `coverage.csv` gives the table's ISOs as "CAISO;ERCOT;ISO-NE;MISO;NYISO;PJM;SPP"; the table holds 71 respondents across the Lower 48.

Not acted on: this note changes no file but itself. The eight days of 0 MWh are EIA's values, recorded, not changed.

Acted on in session 2284: the connector's docstring and header now say every EIA-930 respondent, EIA's regions and US48 among them, five of which repeat a balancing authority's values, so a sum over entities double counts. The rows are unchanged; the next write carries the header.

## The session report against the table

`SESSION_109_REPORT.md`: "190,512 rows of the 300,000 ceiling", "2019-01-01 to 2026-10-03, 71 respondents (balancing authorities and EIA's regions)", route `electricity/rto/daily-region-data`, type D, Eastern day: all hold. The table holds 190,514 rows to 2026-10-03 today: the daily runs added two respondent-days EIA reported later. `docs/methods/grid_network_v3.md` gives the same 190,512 rows, the count of 4 October.

## What it does not hold

- Hours (`eia930_all_demand` for the seven ISOs and US48, from 26 August 2026; `eia930_subba_demand_hourly` for sub-regions); days before 2019; UTC or local days; EIA's forecast, net generation or interchange by day (the total interchange is `eia930_daily_total_interchange`, the pairs `eia930_daily_interchange`); `geo` for any respondent; EIA's earlier versions of a revised day.
