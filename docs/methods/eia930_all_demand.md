# EIA-930's hourly demand and day-ahead demand forecast for the seven ISO balancing authorities and the Lower 48, from 26 August 2026

Energy Research Warehouse (ERW), method note written in session 2284 (chain 104) for a table first written on 29 September 2026 (session 29, `archive/sessions/SESSION_29_REPORT.md`, the consolidation of eight tables into one, commit `5dc81a19`); its members `eia930_<ba>_demand` were first written on 25 September 2026 (session 5, `archive/sessions/SESSION_5_REPORT.md`, Task 2, commit `11dd8942`). The net generation of the same respondents is `eia930_all_generation`; EIA's daily demand of every respondent since 2019 is `eia930_daily_demand`.

Tables: `eia930_all_demand`

## Publisher and address

U.S. Energy Information Administration (EIA), Form EIA-930 (Hourly Electric Grid Monitor), `https://www.eia.gov/electricity/gridmonitor/`, read through EIA's API v2, route `electricity/rto/region-data` (`https://api.eia.gov/v2/electricity/rto/region-data/data/`), frequency hourly, types D (demand) and DF (day-ahead demand forecast), respondents CISO, ERCO, ISNE, MISO, NYIS, PJM, SWPP and US48. The key comes from `EIA_API_KEY` and is replaced by `REDACTED` in every stored URL (all 21,792 rows). Source id `eia:electricity/rto/region-data`. Raw files under `warehouse/raw/eia930/<run_id>/` (four run folders on this machine, 9 to 19 October 2026).

Connector: `warehouse/connectors/eia930.py` (session 5), `--days N [--ba <code>]`. It writes one member a respondent, `eia930_<ba>_demand`, and `warehouse/consolidate.py build` writes the eight into this table with the partition column `ba` (`warehouse/metadata/table_migrations.csv` rows 8 to 15, session 29). The window is the last N complete UTC days; since session 336 a demand table's window ends at the last midnight EIA has published demand to (one day back at most). Completeness: `demand_mw` and `demand_forecast_mw` must have every hour of the window, or the member is not written; for ERCO, NYIS and SWPP demand (`PER_DAY`, sessions 13 and 36A) the rule is applied to each UTC day, so a complete day is written and an incomplete one is left out and recorded as a gap row in `run_status.csv`.

Schedule: the daily run, `warehouse/run_daily.sh` (`pull eia930 ... eia930.py --days "$DAYS"`, 3 days), between `consolidate.py split` and `build`, on the GitHub runner (`.github/workflows/daily-prices.yml`, cron `0 14 * * *`, started on time by pg_cron through `workflow_dispatch`). The table is restored before the run (`warehouse/redivis/config.yaml`, `'^eia930_[a-z0-9]+_(demand|generation)$'`, for the members). No step of `run_data_machine.sh`, `run_data_machine_tables.sh`, `run_monthly.sh`, `refresh_supply.sh` or `warehouse/scheduled.py` runs the connector. `run_status.csv`, the eight demand members together: 263 rows ok, 37 gap, 11 failed. `archive_manifest.csv`: 21,792 rows as of run `20261023T152740Z-github`. Live set: `recent` (35 days), `'^eia930_(?!daily_)[a-z0-9]+_(demand|generation)$'`. Readers: `carbon_intensity.py`, `caiso_reliability.py`, `caiso_join.py`, `cost_of_power.py`, `grid_network.py`, `flex_alert_scorecard.py`, `ai_power_regions.py`, `eia930_subba.py` (a check), the chat's tools, `site/lib/grid.ts`, `gridday.ts` and `gridtables.ts`, the network page, the home page and the `erw` package.

## Vintage and revision

The copy here was rebuilt from the ERW's archive "as of run 20261023T152740Z-github" (header line 1); the newest member retrieval is `20261023T143121Z` (US48). `vintage` is blank in every row: "EIA does not publish a release time per value, and EIA-930 values are revised; the latest retrieval replaces earlier ones" (each member's header). A run merges its window by (entity, variable, ts_utc), so an hour EIA revises is taken again for about three daily runs and then kept.

`retrieved_at` has 12 values. 18,048 rows carry 2026-10-19T10:51:44Z to 10:51:47Z: a run of 19 October asked EIA again for the past weeks (the gap rows of session 309, run `20261019T111546Z`, say it asked "for the last 50 days"); the archive keeps a row's `retrieved_at` from the run that first archived its values. The rest are from 25 and 26 September (the oldest days) and 20 to 23 October. Nothing trims the table: it holds 58 days, from session 5's first window.

## Shape and variables

Series, 21,792 rows, 14 columns: the series columns and `ba`. Two variables, `demand_mw` and `demand_forecast_mw`, 10,896 rows each, unit MW, `freq` PT1H; entity `eia930:<respondent>`; `geo` the respondent's states (US for US48); `market`, `node` and `vintage` blank in every row. Every hour that has one variable has the other.

| ba | Rows | First hour | Hours held | Days missing | Demand mean | Lowest | Highest (hour) | Forecast mean | Forecast error |
|---|---|---|---|---|---|---|---|---|---|
| ciso | 2,784 | 2026-08-26T00 | 1,392 | none | 30,596.0 | 20,580 | 49,959 (2026-09-10T00) | 28,446.3 | 7.82 |
| erco | 2,544 | 2026-08-27T00 | 1,272 | 09-04, 09-05, 10-05, 10-06 | 65,381.7 | 41,024 | 90,116 (2026-08-27T21) | 65,269.0 | 1.43 |
| isne | 2,784 | 2026-08-26T00 | 1,392 | none | 12,082.8 | 7,741 | 19,017 (2026-08-28T22) | 11,826.9 | 2.96 |
| miso | 2,784 | 2026-08-26T00 | 1,392 | none | 79,506.3 | 57,964 | 119,227 (2026-09-02T21) | 80,812.3 | 1.91 |
| nyis | 2,640 | 2026-08-27T00 | 1,320 | 09-04, 09-05 | 15,980.4 | 11,394 | 24,562 (2026-09-03T22) | 15,631.3 | 2.64 |
| pjm | 2,784 | 2026-08-26T00 | 1,392 | none | 95,977.7 | 71,622 | 152,547 (2026-09-01T21) | 94,792.5 | 3.34 |
| swpp | 2,688 | 2026-08-26T00 | 1,344 | 09-28, 09-29 | 37,421.0 | 26,417 | 56,486 (2026-09-04T21) | 39,647.9 | 6.64 |
| us48 | 2,784 | 2026-08-26T00 | 1,392 | none | 518,297.7 | 371,718 | 735,139 (2026-09-01T21) | 510,036.8 | 1.80 |

MW; every series ends at 2026-10-22T23:00:00Z. Days missing are UTC days of 2026. "Forecast error" is the mean of |forecast less demand| over demand, in percent.

- The seven ISOs' demand is 0.652 of US48's (the median over the 1,224 hours all seven hold; 0.609 to 0.684).
- No value is zero or negative.

## Placing values in time, and what is filled

`ts_utc` is the start of the hour in UTC: EIA's `period` is the end of the hour, and one hour is subtracted (session 5). Days are UTC days. Nothing is filled: an hour EIA did not publish has no row. Under the per-day rule a day is left out whole when either variable lacks an hour, so on ERCO's and NYIS's 4 and 5 September and SWPP's 28 and 29 September EIA's demand was published but is not held, because the day-ahead forecast had missing hours (`run_status.csv`: "demand_forecast_mw: 5 of 24 hours", "19 of 24 hours" and so on). ERCO's 5 and 6 October are left out the same way and were asked again twice (sessions 309 and 325: "still incomplete").

## License

The header has no License line (neither the consolidated header nor the members'). `coverage.csv`: public. `warehouse/metadata/license_verdicts.csv`, EIA (read 1): "U.S. government publications are in the public domain and are not subject to copyright protection. You may use and/or distribute any of our data, files, databases, reports, graphs, charts, and other information products that are on our website or that you receive through our email distribution service.", verdict "may be public", if the ERW sells anything "may be public"; the note asks for the acknowledgment "Source: U.S. Energy Information Administration". `docs/licenses.md`, the table's row: EIA, "may be public", flag public, "agrees", ERW verdict public. No row in `license_status.csv`.

## Checks (session 2284)

The figures in this note were computed from the rows of `warehouse/output/eia930_all_demand.csv`, read past its 99 header lines (counted), with `runs/c104/s2284/profile.py`, `check_eia930_hourly.py`, `eia_missing_days.py`, `check_daily_demand.py` and `cross_demand_iso.py` (outputs beside them).

- 21,792 rows, the sum the header gives; each member's rows and range equal its header's "File holds" line. No (entity, variable, ts_utc) twice; no blank value; unit MW throughout; no placeholder column (the blank `market`, `node` and `vintage` are as the code writes them).
- Every missing day is a whole UTC day, as the per-day rule makes it; the five respondents under the whole-window rule miss no hour.
- **Against EIA's daily route** (`eia930_daily_demand`, type D, EIA's Eastern day): the hourly `demand_mw` summed over each Eastern day held whole equals EIA's daily value exactly on every such day of the seven ISOs (CISO 57, ERCO 50, ISNE 57, MISO 57, NYIS 53, PJM 57, SWPP 54 days). US48 equals it on 2 days of 57 (median ratio 1.00000, largest gap 47,782 MWh on 2026-10-01).
- **Against the operators' own load:** NYISO's eleven zones summed (`nyiso_zone_load_hourly`) and NYIS's `demand_mw` differ by 0.2 MW on average over 1,022 hours (27 August to 10 October), against 526.9 and 526.3 MW with EIA's hour moved one hour either way. ERCOT's system load (`ercot_zone_load_hourly`): 95.3 MW over 797 hours, against 2,377.5 and 2,257.5 MW shifted; ratio of sums 0.9996. Both confirm the hour-start reading.

## Where the description and the data disagree

1. **"Every balancing authority."** The consolidated header's title reads "EIA-930 hourly demand and day-ahead demand forecast, every balancing authority". The table holds eight respondents: the seven ISOs and US48, which is not a balancing authority (the docstring says "the seven ISOs and the US Lower 48", which is right). EIA's other balancing authorities are in `eia930_daily_demand` and `eia930_subba_demand_hourly`, not here.
2. **"About 30 days."** `docs/methods/events.md` ("keep only about 30 days"), `emissions.md` ("which keep about 30 days") and `cost_of_power.md` ("keeps 30 days only") describe this table as a 30-day window. Nothing trims it; it holds 58 days, from 26 August 2026, and grows by a day a day.
3. **A missing day with no gap row.** The members' headers say "Each day not written is a gap row in warehouse/metadata/run_status.csv". ERCO and NYIS lack 26 August 2026, and no row of `run_status.csv` names that day: the runs of 25 September that covered it failed whole ("incomplete data, no file written"), before the per-day rule wrote these members, and the later windows began on 27 August. Every other missing day has its gap rows.

Not acted on: this note changes no file but itself.

Recorded, not changed in session 2284: the titles' "every balancing authority" (the seven ISOs and US48), the 26 August gap without a gap row, and the other notes' "about 30 days" are for the EIA-930 connector's next change; no request was made.

## The session report against the table

- `SESSION_5_REPORT.md`: EIA-930 hourly demand "for CISO, ERCO, ISNE, MISO, NYIS, PJM, SWPP and US48"; "EIA's hourly `period` is the hour END ... So `ts_utc = period - 1h`": both hold (the NYISO check above is closer now than session 5's 57.5 MW, on a different window).
- `SESSION_29_REPORT.md`: replaces `eia930_<ba>_demand` (8), partition `ba` (new), 12,720 rows, "8 of 8 equal": the members and the partition hold; the 12,720 rows were the table on 29 September, and it holds 21,792 now.

## What it does not hold

- EIA-930's other balancing authorities and regions (`eia930_daily_demand`, daily; `eia930_subba_demand_hourly` for sub-regions); hours before 26 August 2026 (EIA's six-month file for January to June 2018 is `eia930_all_history`); net generation (`eia930_all_generation`) and interchange (`eia930_all_interchange`); EIA's adjusted or imputed series apart from what the API serves; the ten missing BA-days named above (ERCO 5, NYIS 3, SWPP 2); a release time for any value.
