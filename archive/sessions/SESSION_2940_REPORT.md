# Session 2940 report: the siting gaps file and the records

6 November 2026, about 07:16 to 07:19 UTC, on lab-desktop (the data machine), chain 155, unattended. Model spend USD 0. Pulls: none.

## Read these first

- **`docs/reviews/siting-gaps.md`:** a new section, "State on 6 November 2026, morning (chain 155)", one line for every row this chain read or moved. The table above it is unchanged, so `gaps.json` stays as it is.
- **The records after `large_load_connection_rules` grew to 39 rows** (session 2938):
  - `licenses.py tables`, `write` and `check`: 633 tables, 0 problems.
  - `release_v1.py --check`: 0 differences. The release table's row count for the held table went from 26 to 39.
  - Tests 2924, 275, 410, 1001, 1008, 1009 and the siting gaps tests: 63 passed.
- **Not committed, on purpose:** `build_tables.py` and `licenses.py write` on this machine would change `ercot_wind_solar_hsl_monthly`'s publisher from "ERW" to "ERCOT". The cause is this machine's copy of the table, restored by sync, whose header names its input (`ercot_wind_solar_hsl_hourly`); the runner's copy does not. The same record would then differ by machine. Main's record (session 2884's, the ERW's derived table) was kept. For the same reason the release package's two weather rows were not rewritten from this machine's tables.
- **The method notes against their code:** `large_load_connection_rules.md` lists SPP's document (session 2938); the connector is unchanged.

## Decisions made without you

- **A record that would flip with the machine was left as main has it.**

## For Samuel's ruling

- **`ercot_wind_solar_hsl_monthly`'s publisher:** the ERW (its source registry row, session 2884) or ERCOT (its input's publisher, as the license record reads a derived table's header). The two machines' copies disagree; one header should be made the rule.
