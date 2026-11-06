# Session 3109 report: the first daily runs with the guards

6 November 2026, about 14:01 to 14:12 UTC, on lab-desktop (the data machine, its first window), chain 177, unattended. Model spend USD 0. Pulls: GitHub's API (about 30 requests); Supabase reads of `erw_health` over `SUPABASE_DB_URL`.

## Read these first

- **The runner's 14:00 UTC run did not run the day's work.** Run 42230041327 (14:00:03 to 14:00:42 UTC, success) was gated: "the day's work is done: 1 runs today (2026-11-06) whose daily step passed".
  - The day's run was 42120465428. Its dispatch started at 22:19 UTC on 5 November; its daily step passed after midnight; it ended at 01:41 UTC on 6 November.
  - So the first run with chain 151's board guard is the runner's run of 7 November. That run's board steps (`eia_board`, `board validate`, `board_page`, `board`) were all `ok`; it has no `board_tests` line.
- **That run's one failed test step is already fixed on main.** At 01:41 UTC `package tests` failed on `test_derived_tables_flag_license_and_inputs`: `ercot_wind_solar_hsl_monthly`'s citation read "Energy Research Warehouse (ERW). ERW derived table: ..."
  - The run's own commit `e2794ff06` registered the publisher as "Energy Research Warehouse (ERW)".
  - Session 2884 (`1bd5d70c0`, about 01:49 UTC) changed the connector to register "Energy Research Warehouse (ERW), derived". It reached main after the run had checked out. Main's `sources.csv` row now carries ", derived".
  - No change is needed. The next runner run should pass the step.
- **Found on this machine, not on the runner: four old derived tables fail the same test.** The table files are only here. On this machine's full warehouse, `test_derived_tables_flag_license_and_inputs` fails on these sources rows, whose publisher is "Energy Research Warehouse (ERW)" without ", derived":
  - `eia930_demand_weather` (session 126, `warehouse/derived/demand_weather.py`);
  - `eia_annual_crosscheck_ba` (`warehouse/derived/eia_annual_crosscheck.py`);
  - `grid_stress_days` (session 306);
  - `iso_queue_statistics` (session 348).
  The runner holds none of the four, and this machine's own run does not run the package tests, so no scheduled step fails. The test of session 1001 (`package/tests/test_erw.py`, line 275) accepts those wordings; line 651 does not. The fix is session 2884's (the publisher ", derived" in each script's `update_sources` and its `sources.csv` row, with the package's records rebuilt). It goes to chain 181, so that it lands with the gate outside the closed window.
- **This machine's 17:00 UTC run** has not run. It is chain 180's to read (session 3105's form) and chain 181's.

## Decisions made without you

- **No fix for the runner's failure:** session 2884's was already on main.
- **The four old tables' fix put to chain 181** rather than built at 14:10 with the landing window closed.

## For Samuel's ruling

- **ERCOT `/misapp` on the runner:** `ercot_as_prices` and ten other connector files (`iso_prices.py` among them) ask `/misapp/servlets/IceDocListJsonWS`, which ERCOT's robots file disallows. `docs/methods/ercot_as_prices.md` has said so since session 2002. The chains' rule keeps sessions off those paths, but the daily run still asks them.
