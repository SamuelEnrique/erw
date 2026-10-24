# EIA-930's daily interchange of every directed pair EIA reports, balancing authorities, regions and neighbours abroad, Eastern days from 1 January 2019

Energy Research Warehouse (ERW), method note written in session 2284 (chain 104) for a table first written on 2 October 2026 (session 62, `archive/sessions/SESSION_62_REPORT.md`, "where the next gigawatts for AI can come from", an approved pull; commit `ca0250e9`). The network's replay that reads it is described in `docs/methods/grid_network_v3.md`; EIA's own total interchange of each respondent is `eia930_daily_total_interchange` (`docs/methods/eia930_daily_total_interchange.md`); the hourly pairs, from September 2026, are `eia930_all_interchange` (`docs/methods/grid_network.md`).

Tables: `eia930_daily_interchange`

## Publisher and address

U.S. Energy Information Administration (EIA), Form EIA-930 (Hourly Electric Grid Monitor), `https://www.eia.gov/electricity/gridmonitor/`, through EIA's API v2, route `electricity/rto/daily-interchange-data` (`https://api.eia.gov/v2/electricity/rto/daily-interchange-data/data/`), frequency daily, facet `timezone` Eastern, a calendar month a request, sorted by period, `fromba` and `toba`, paged by 5,000. The key is replaced by `REDACTED` in every stored URL. Source id `eia930:daily_interchange`. Raw files under `warehouse/raw/eia930_daily_interchange/` (pages and month checkpoints; none on this machine).

Connector: `warehouse/connectors/eia930_daily_interchange.py` (session 62), ceiling 3,000,000 rows, with the helper `eia930_daily_interchange_fill.py`, which filled past months' checkpoints in parallel during the first pull. As for the daily demand table: the full pull counts EIA's rows first and stops above the ceiling; `--days N` (session 114) asks again for the newest days and merges by (entity, variable, ts_utc), and never starts a table. Entity `eia930:<FROM>-<TO>`; `ba` is EIA's `fromba` (the reporting party) and `x_to_ba` its `toba`, both in lower case; a value that is not a number is not written. "Hourly data for the same span would be about 23 million rows, over the ceiling; the daily route is about 1 million."

Schedule: the daily run, `warehouse/run_daily.sh`: `soft_step eia930_daily_interchange ... warehouse/scheduled.py eia930_daily_interchange`, which runs `eia930_daily_interchange.py --days 5` after rebuilding the table from the ERW's archive on the runner; the `network_replay` step then reads it. GitHub runner, `.github/workflows/daily-prices.yml` (cron `0 14 * * *`, started by pg_cron through `workflow_dispatch`). No step of `run_data_machine.sh`, `run_data_machine_tables.sh`, `run_monthly.sh` or `refresh_supply.sh` runs it. `run_status.csv`: 15 rows, all ok. `archive_manifest.csv`: 952,530 rows as of run `20261023T152740Z-github`. Not in the Supabase live set (no line of `live_set.yaml` names it; the docstring: "history (not in the Supabase live set)"). Readers: `warehouse/derived/ba_supply.py`, `network_daily.py` (the replay, which leaves EIA's regions out, `grid_network.REGIONS`), `ai_power_regions.py`, `eia930_daily_total_interchange.py`, the finding `who_rescues_whom.py`, `warehouse/analysis/watch.py`, `site/lib/gridtables.ts` and the draft report page `site/app/reports/draft/ai-gigawatts/`.

## Vintage and revision

The copy here was rebuilt from the archive "as of run 20261023T152740Z-github" (header line 1); the newest run is `20261023T150934Z` (`--days 5`): "this run asked for 2026-10-18 to EIA's newest day (2026-10-21)", "This run wrote 1372 rows: 356 new, 1016 replacing earlier rows". `vintage` is blank in every row. `retrieved_at`: 945,098 rows from session 62's pull on 2 October 2026; the rest from the daily runs of 5 to 23 October, about 325 to 345 rows a run (1,367 on the 15th and 1,372 on the 23rd). A day is asked for again on five daily runs, then kept.

## Shape and variables

Series, 952,530 rows, 16 columns: the series columns, `ba`, `x_to_ba` and `x_timezone` (Eastern in every row). One variable, `interchange_mwh`, unit MWh, `freq` P1D; `geo`, `market`, `node` and `vintage` blank in every row. 390 directed pairs, 83 reporting codes, 93 neighbour codes; 2,804 days from 2019-01-01 to 2026-10-21, 248 to 355 rows a day (341 on the newest).

- **Who reports.** 69 of the reporting codes are balancing authorities; 14 are EIA's regions and the Lower 48 (CAL, CAR, CENT, FLA, MIDA, MIDW, NE, NW, NY, SE, SW, TEN, TEX, US48), which report 124,400 rows over 45 pairs. 99,727 rows have a region as the neighbour. Eleven neighbour codes never report: AESO, BCHA, CAN, CEN, CFE, HQT, IESO, MEX, MHEB, NBSO and SPC (the Canadian and Mexican parties and others outside EIA's respondents). A sum over all rows counts a flow again in each region and in US48.
- **Sign.** Positive when the reporting party exports to the neighbour (the header). 441,791 pair-days are reported from both ends: on 246,508 the two values are exactly opposite, on 350,250 within 5 percent (or 1 MWh) of opposite, and the median of their sum is 0. 68,948 pair-days are reported from one end only.
- Values: 460,686 positive, 472,853 negative, 18,991 zero.
- **Values no tie can carry,** held as EIA reports them: SEC to FPL, 429,515,551 MWh on 2026-05-14; BANC to TIDC, 20,367,792 MWh (2019-05-04) and 17,938,110 MWh (2019-04-12); SWPP to AECI, -10,746,671 MWh, and CENT to MIDW, -10,708,368 MWh (both 2020-03-17). The readers screen such days by their own rules (`ba_supply.screen`, `docs/methods/grid_network_v3.md`, "Screened days").
- Rows a year: 128,049 (2019), 126,122, 126,917, 125,289, 123,698, 123,075, 104,865 (2025) and 94,515 (2026 to 21 October).

## Placing values in time, and what is filled

`ts_utc` is the day at 00:00:00Z (Decision 11), a label: the day is EIA's Eastern day for every pair (`x_timezone`), as in `eia930_daily_demand` and `eia930_daily_total_interchange`, not a UTC day nor a party's local day. Nothing is filled: a pair-day EIA does not report has no row. **47 days have no row at all:** 2025-11-05 to 2025-12-10 and 2025-12-21 to 2025-12-31, as `docs/methods/eia930_daily_total_interchange.md` found (that table lacks 46 of them; this one lacks 2025-11-05 too).

## License

Header: "License: public domain (U.S. Government data, EIA)." `license_verdicts.csv`, EIA (read 1): "U.S. government publications are in the public domain and are not subject to copyright protection. You may use and/or distribute any of our data, files, databases, reports, graphs, charts, and other information products that are on our website or that you receive through our email distribution service.", "may be public" (and if the ERW sells anything). `docs/licenses.md`, the table's row: EIA, "may be public", flag public, "agrees", ERW verdict public. No row in `license_status.csv`.

## Checks (session 2284)

The figures in this note were computed from the rows of `warehouse/output/eia930_daily_interchange.csv`, read past its 10 header lines (counted), streamed by `runs/c104/s2284/check_daily_interchange.py` and `check_regions.py` (outputs beside them).

- 952,530 rows and the range 2019-01-01 to 2026-10-21, as header line 10 states; no (pair, day) twice; no blank value; every `ts_utc` a midnight; `entity` is `eia930:<BA>-<X_TO_BA>` in capitals in every row; one unit and one variable.
- **Against EIA's total interchange** (`eia930_daily_total_interchange`, route `daily-region-data`, type TI): the sum of a respondent's rows here over a day, against EIA's own total: 211,310 respondent-days in both (the count that table's note gives), 139,273 equal, 170,931 within 1 percent; 1,296 respondent-days are here only and 1,151 there only.
- **Against the hourly pairs** (`eia930_all_interchange`, route `interchange-data`): the hourly values summed over each Eastern day held whole (24 hours, 13 September to 20 October 2026): 11,439 pair-days, 11,310 equal, 11,381 within 1 percent. The largest gaps are regions' rows on 2026-09-16 (NW to CAN: -43,365 MWh by the hours, 0 by the day).

## Where the description and the data disagree

1. **"Every pair of balancing authorities."** Header line 2 reads "daily interchange between every pair of balancing authorities" and the docstring "every directed pair EIA reports". The second is right: 14 of the 83 reporting codes are EIA's regions and the Lower 48 (124,400 rows), and 11 of the neighbours are parties outside the Lower 48's respondents, such as CAN and MEX. A reader who sums the table, or counts its "balancing authorities", takes those with the rest.
2. **Coverage names seven grids.** `coverage.csv` gives the table's ISOs as "CAISO;ERCOT;ISO-NE;MISO;NYISO;PJM;SPP"; it holds 390 pairs across the Lower 48 and its neighbours.

Not acted on: this note changes no file but itself. The impossible values and the 47 missing days are EIA's, recorded, not changed.

Acted on in session 2284: the connector's docstring and header now say every pair EIA-930 reports, Canadian and Mexican neighbours that do not report themselves among them. The rows are unchanged; the next write carries the header.

## The session report against the table

`SESSION_62_REPORT.md`: "945,130 pair-days" of 3,000,000, "EIA's Eastern day for every pair, 390 directed pairs, 2019-01-01 to 2026-09-30, 282 pages": the pairs, the day and the span hold. The table holds 945,435 rows to 2026-09-30 today: 945,098 from session 62's pull and 337 from the daily run of 5 October, which asked again for the last days of September (replacing 32 of session 62's rows and adding 305 pair-days EIA reported later).

## What it does not hold

- Hours (`eia930_all_interchange`, from 13 September 2026; `eia930_event_hourly_interchange`, two event windows); each respondent's total interchange as EIA states it (`eia930_daily_total_interchange`); days before 2019; UTC or local days; the 47 days of late 2025; EIA's earlier versions of a revised day; `geo` for any pair.
