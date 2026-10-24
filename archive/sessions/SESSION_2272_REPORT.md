# Session 2272 report: a source of the session's own choosing (central Europe's grids, Energy-Charts)

24 October 2026, from 04:05 UTC to 04:25 UTC, on lab-desktop (the data machine), chain 103, unattended. Model spend USD 0. Pulls: 14 requests of 20 (2 by the probe, 12 by the trial, one for each country and year, 35 seconds apart; the write ran offline).

## Read these first

- **Why this source:** Austria, Switzerland and Czechia border Germany, whose grid the ERW holds (chain 099's SMARD table), and no ERW table held their hourly production. Their operators' own data refuse or bar the reader: APG's transparency platform did not answer (chain 102), and Swissgrid's legal information forbids public or commercial use without consent. Energy-Charts (Fraunhofer ISE) publishes all three under CC BY 4.0, in the form chain 102 read for Belgium. Chains 101 and 102 do not take these countries.
- **A new table, `energy_charts_central_europe`** (series, 1,419,805 rows, `power`): 43 series of hourly public net production by type, load, residual load and cross-border trading for AT, CH and CZ, from 31 December 2022 23:00 UTC (1 January 2023 in Central European time) to 23 October 2026. The values are in MW.
  - Austria's and some of Czechia's answers come every quarter hour. Those are averaged to the hour, and an hour is kept only when all four quarters are given. At full resolution the table held 3,685,971 rows and 1,006 MB, more than the largest held table (`ercot_sced_esr_hourly`, 553 MB). Hourly it holds 395 MB.
  - The answers' own spacing is kept in `x_resolution`.
  - Energy-Charts' renewable shares (496,062 figures) are not taken. Hours with a blank or a missing quarter have no row and are counted in the header, most of them Czechia's coal-derived gas (8,113 hours), oil (722) and hard coal (745).
  - Written, validated (0 errors, 0 warnings), archived, held from the Redivis storage and the live set.
- **The license:** the API's description (read 420): "Unless stated otherwise, the data provided by the Energy-Charts API is licensed under the CC BY 4.0 license". The registry says `internal` until the licenses round (session 2271) records the verdict, as for chain 102's Belgian table, so no release rows were added. The rate limit read there, 2 requests a minute, set the trial's pause.
- **Cross-checks against `eurostat_electricity_monthly`, full years 2023 to 2025** (production types summed without pumped storage's consumption, which Energy-Charts gives as a negative series):
  - Czechia: 1.008, 0.997 and 1.003 of Eurostat's net production. Nuclear is 28.72, 28.04 and 30.29 TWh against Eurostat's 28.73, 28.05 and 30.32, and wind in 2024 is 0.70 against 0.70.
  - Austria: 0.857, 0.864 and 0.797 of Eurostat's total. Energy-Charts' figures are public net production; Eurostat's total is all net production. Austria's wind in 2024 is 9.37 TWh against Eurostat's 9.13.
  - Switzerland: Eurostat's table holds no Swiss total. The table's Swiss load is 1.037 to 1.042 of Ember's demand (`owid_ember_electricity_annual`), against 0.781 to 0.821 for Austria and 0.914 to 0.921 for Czechia, so the load series is not the same quantity as Ember's demand.
  - Every year 2023 to 2025 has all its hours (8,760 or 8,784) in each country.

## Requests (14 of 20)

| n | What | Outcome |
|---|---|---|
| 1 | api.energy-charts.info/robots.txt | 404 |
| 2 | the API's description (openapi.json) | 200: CC BY 4.0, 2 requests a minute |
| 3 to 14 | public_power for at, ch and cz, 2023 to 2026 (the trial) | 200 |

Reads recorded: 419 and 420, each with a label of its own (test 205 holds one label a read).

## Decisions made without you

- **Hourly means in place of the quarter hours,** for the table's size, said in the docstring and header; the answers' spacing kept in `x_resolution`.
- **Registry license `internal` until the verdict,** as chain 102 did for Energy-Charts' Belgium.
- **Pumped storage's consumption kept as a production type, negative, as Energy-Charts gives it;** the cross-check leaves it out of the sums.

## For Samuel's ruling

- None new.

## Files

- New: `warehouse/connectors/energy_charts_central.py`, `tests/test_session2272.py`, this report.
- Changed: `warehouse/metadata/build_coverage.py`, `warehouse/redivis/release_v1.py`, `warehouse/supabase/live_set.yaml`, `docs/coverage.md`, `warehouse/metadata/coverage.csv`, `warehouse/metadata/sources.csv`, `warehouse/metadata/archive_manifest.csv`, the license record.
- On the data machine only: `runs/c103/s2272/`, `warehouse/raw/energy_charts_central/`, `warehouse/output/energy_charts_central_europe.csv`.
