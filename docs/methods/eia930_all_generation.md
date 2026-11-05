# EIA-930's hourly net generation, in all and by energy source, for the seven ISO balancing authorities and the Lower 48, from 26 August 2026

Energy Research Warehouse (ERW), method note written in session 2284 (chain 104) for a table first written on 29 September 2026 (session 29, `archive/sessions/SESSION_29_REPORT.md`, the consolidation of eight tables into one, commit `5dc81a19`); its members `eia930_<ba>_generation` were first written on 25 September 2026 (session 5, `archive/sessions/SESSION_5_REPORT.md`, Task 2, commit `11dd8942`). Demand for the same respondents is `eia930_all_demand` (`docs/methods/eia930_all_demand.md`); the battery series alone, back to November 2024, is `eia930_all_storage` (`docs/methods/storage.md`).

Tables: `eia930_all_generation`

## Publisher and address

U.S. Energy Information Administration (EIA), Form EIA-930 (Hourly Electric Grid Monitor), `https://www.eia.gov/electricity/gridmonitor/`, through EIA's API v2, two routes, frequency hourly, respondents CISO, ERCO, ISNE, MISO, NYIS, PJM, SWPP and US48:

- `electricity/rto/region-data`, type NG: `net_generation_mw` (11,136 rows, source `eia:electricity/rto/region-data`);
- `electricity/rto/fuel-type-data`, every energy source the respondent reports: `net_generation_<fuel>_mw` (104,136 rows, source `eia:electricity/rto/fuel-type-data`). EIA's codes and the ERW's names: COL coal, NG natural_gas, NUC nuclear, OIL oil, WAT hydro, SUN solar, WND wind, GEO geothermal, OTH other, UNK unknown, BAT battery, PS pumped_storage, SNB solar_with_battery, WNB wind_with_battery, OES other_storage, UES unknown_storage (`FUELS` in the connector).

The key is replaced by `REDACTED` in every stored URL (all 115,272 rows). Raw files under `warehouse/raw/eia930/<run_id>/` (four run folders on this machine, 9 to 19 October 2026).

Connector: `warehouse/connectors/eia930.py` (session 5), as for `eia930_all_demand`; members `eia930_<ba>_generation`, consolidated with the partition column `ba` (`warehouse/metadata/table_migrations.csv` rows 16 to 23). Since session 16 every generation member is under the per-day rule: `net_generation_mw` must have every hour of a UTC day or the day is not written (a gap row in `run_status.csv`); a fuel series missing any hour of a day that is written is dropped for that run and named in that run's header; a fuel the respondent does not report at all is not a variable.

Schedule: the daily run, `warehouse/run_daily.sh` (`pull eia930 ... --days "$DAYS"`, 3 days), on the GitHub runner (`.github/workflows/daily-prices.yml`, cron `0 14 * * *`, started by pg_cron through `workflow_dispatch`); restored before the run (`warehouse/redivis/config.yaml`). No other schedule (`run_data_machine.sh`, `run_data_machine_tables.sh`, `run_monthly.sh`, `refresh_supply.sh`, `warehouse/scheduled.py`, the other workflows) runs the connector. `run_status.csv`, the eight generation members together: 247 rows ok, 48 gap, 11 failed. `archive_manifest.csv`: 115,272 rows as of run `20261023T152740Z-github`. Live set: `recent` (35 days). Readers: `carbon_intensity.py`, `caiso_join.py`, `battery_levels.py`, `curtailment_shares.py`, `eia930_storage.py`, `warehouse/analysis/eia930_balance.py`, the chat's tools, `site/lib/grid.ts`, `gridday.ts`, `gridtables.ts`, `networkGravity.ts` and the network page.

## Vintage and revision

The copy here was rebuilt from the archive "as of run 20261023T152740Z-github" (header line 1); the newest member retrieval is `20261023T143121Z`. `vintage` is blank in every row (EIA publishes no release time; values are revised and the latest retrieval replaces the earlier). `retrieved_at` has 53 values; 94,512 rows carry 19 October 2026 (10:51:48Z to 10:51:58Z), the run that asked EIA again for the past weeks, as for the demand table. The gap days 26 and 28 September 2026 (net generation published for 3 or 4 hours of the day when first asked, `run_status.csv`) were written by later runs: every respondent now has all 1,392 hours.

## Shape and variables

Series, 115,272 rows, 14 columns (the series columns and `ba`); unit MW, `freq` PT1H; entity `eia930:<respondent>`; `geo` the respondent's states; `market`, `node` and `vintage` blank. Every respondent holds every hour from 2026-08-26T00:00:00Z to 2026-10-22T23:00:00Z (1,392 hours, 58 UTC days).

| ba | Rows | Variables | Net generation, mean | Gas | Coal | Nuclear | Wind | Solar | Hydro | Battery |
|---|---|---|---|---|---|---|---|---|---|---|
| ciso | 13,920 | 10 | 22,614.7 | 9,102.2 | 0.9 | 1,966.2 | 2,462.6 | 6,567.2 | 1,997.7 | not reported |
| erco | 12,528 | 9 | 65,403.2 | 30,661.3 | 7,937.6 | 4,878.7 | 11,476.1 | 10,613.2 | 36.7 | -262.7 |
| isne | 14,424 | 11 | 12,321.9 | 6,538.3 | not reported | 3,341.0 | 1,035.2 | 237.6 | 262.1 | 35.6 |
| miso | 12,528 | 9 | 78,296.1 | 30,533.9 | 20,517.6 | 10,646.6 | 9,389.9 | 5,671.1 | 936.5 | -19.1 |
| nyis | 12,528 | 9 | 13,930.6 | 7,389.4 | 0 | 2,924.5 | 623.4 | 0 | 2,638.1 | not reported |
| pjm | 12,528 | 9 | 99,030.1 | 41,222.5 | 16,065.0 | 29,714.8 | 2,666.2 | 3,741.4 | 1,678.7 | not reported |
| swpp | 13,920 | 10 | 38,163.9 | 11,306.1 | 10,354.6 | 1,570.2 | 13,108.9 | 861.4 | 882.1 | 43.2 |
| us48 | 22,896 | 17 | 510,738.0 | 216,485.0 | 86,139.4 | 88,510.1 | 48,243.8 | 39,619.8 | 21,397.1 | 591.7 |

Mean MW over the hours held. The other variables: `other` (all eight), `oil` (CISO, ISNE, NYIS, PJM, SWPP, US48), `geothermal` (CISO 763.8, US48 1,189.9), `pumped_storage` (ISNE 258.3, US48 75.7), `solar_with_battery` (ISNE 3.2, US48 668.3), and for US48 alone `unknown`, `wind_with_battery`, `other_storage` and `unknown_storage`.

- **Columns that are always zero:** NYIS's coal and solar (1,392 hours each, all 0), SWPP's oil (all 0), US48's `unknown` and `wind_with_battery` (all 0), and US48's `other_storage` (0 in 1,391 hours, -1 in one). EIA reports these values; the connector keeps them.
- **Two short series:** ISNE's oil has 504 hours, from 2026-09-22T00:00:00Z; US48's `unknown_storage` 624 hours, from 2026-09-26T00:00:00Z (always negative, -1 to -2,780 MW). Both were dropped from earlier runs as incomplete (for example `run_status.csv`, 25 September: "net_generation_oil_mw: 480 of 720 hours"), and those days were never asked again with the series whole.
- **Negative values.** Batteries charging (ERCO 866 hours, down to -11,553 MW; MISO 805; US48 696, down to -12,500); pumped storage pumping (US48 689 hours); solar at night (CISO 608 hours, at most -73 MW; US48 124, at most -91). CISO reports no battery series, and its `other` is negative in 695 hours, down to -10,928 MW, the charging of storage reported under other.
- The seven ISOs' net generation is 0.647 of US48's (median over 1,392 hours, 0.612 to 0.678). Net generation over demand, over the hours both tables hold: CISO 0.739, ERCO 0.999, ISNE 1.020, MISO 0.985, NYIS 0.864, PJM 1.032, SWPP 1.022, US48 0.985.

## Placing values in time, and what is filled

`ts_utc` is the start of the hour in UTC (EIA's `period` less one hour); days are UTC days. Nothing is filled: a value EIA did not publish has no row, and a fuel dropped from a run leaves those hours without that fuel. **The energy sources do not always add up to `net_generation_mw`**, which comes from another route: the sum of the fuels less the total is within 4 MW in every hour for CISO, MISO and NYIS, and within 124 MW for ERCO; PJM's median is -273.5 MW (largest 4,889 on 2026-10-16T02:00:00Z, within 1 percent in 1,374 of 1,392 hours); SWPP's 16 MW (largest -2,918 on 2026-09-15T08:00:00Z); US48's 61.5 MW (largest 35,170 on 2026-09-17T23:00:00Z). In three hours (2026-09-11T17:00:00Z, 2026-10-14T19:00:00Z and 20:00:00Z) every ISNE fuel is 0 while its net generation is 11,433, 13,361 and 14,421 MW; US48's fuels fall short by about as much (10,011 and 13,942 MW in two of those hours).

## License

The header has no License line. `coverage.csv`: public. `license_verdicts.csv`, EIA (read 1): "U.S. government publications are in the public domain and are not subject to copyright protection. You may use and/or distribute any of our data, files, databases, reports, graphs, charts, and other information products that are on our website or that you receive through our email distribution service.", "may be public" (and if the ERW sells anything). `docs/licenses.md`, the table's row: EIA, "may be public", flag public, "agrees", ERW verdict public. No row in `license_status.csv`.

## Checks (session 2284)

The figures in this note were computed from the rows of `warehouse/output/eia930_all_generation.csv`, read past its 122 header lines (counted), with `runs/c104/s2284/profile.py`, `check_eia930_hourly.py`, `eia_missing_days.py`, `check_header_vars.py` and `cross_generation.py` (outputs beside them).

- 115,272 rows, the sum the header gives; each member's rows and range equal its header's "File holds" line (13,920, 12,528, 14,424, 12,528, 12,528, 12,528, 13,920, 22,896). No (entity, variable, ts_utc) twice; no blank value; unit MW throughout.
- Each member header's list of variables is the set its rows hold.
- **Against `eia930_all_storage`** (`eia930_storage.py`, the same route asked by another run): of the 6,960 battery hours here, 6,888 are there too and 6,866 are equal; the other 22 differ by a few MW (for example ISNE at 2026-10-14T22:00:00Z, 49 here and 0 there; US48 at 2026-10-08T08:00:00Z, -2,087 and -2,089), EIA's revisions between the two retrievals. 24 hours each of ISNE, MISO and SWPP are here and not there.
- Against `eia930_all_demand`: the ratios above; ERCO, the islanded grid, is 0.999.

## Where the description and the data disagree

1. **"Every balancing authority."** The consolidated header's title reads "EIA-930 hourly net generation, total and by energy source, every balancing authority". The table holds the seven ISOs and US48 (not a balancing authority), as the docstring says.
2. **"About 30 days."** `docs/methods/events.md` and `emissions.md` describe this table as keeping about 30 days; it holds 58 and nothing trims it.
3. **Complete, but not whole.** The headers say every written day passed the completeness rule. The rule sees a missing hour, not a zero: in three hours EIA published 0 for every ISNE energy source while ISNE's net generation was 11,433 to 14,421 MW, and those zeros are held as values.
4. **Variables listed without their start.** The members' headers list ISNE's `net_generation_oil_mw` and US48's `net_generation_unknown_storage_mw` among the variables without saying they begin on 22 and 26 September; the runs that dropped them said so in headers that later runs replaced.

Not acted on: this note changes no file but itself.

Recorded, not changed in session 2284: the three hours of all-zero ISNE fuels beside an ISNE total, and the late-starting series, are EIA's as published; the titles' "every balancing authority" is for the connector's next change.

## The session report against the table

- `SESSION_5_REPORT.md`: net generation for "CISO, ERCO, ISNE, MISO, NYIS, PJM, SWPP and US48", `ts_utc = period - 1h`: hold.
- `SESSION_29_REPORT.md`: replaces `eia930_<ba>_generation` (8), partition `ba` (new), 65,112 rows, "8 of 8 equal": the members and partition hold; the 65,112 rows were the table on 29 September, and it holds 115,272 now.

## What it does not hold

- EIA-930's other balancing authorities; hours before 26 August 2026 (net generation for January to June 2018 is in `eia930_all_history`, without the fuels); EIA's per-fuel values for the hours a fuel was dropped; generation by plant or unit; CISO's batteries apart from `other` (CAISO's own battery series is `caiso_battery_storage`); a release time for any value.
