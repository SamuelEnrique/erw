# Session 2494 report: six held tables linked to the notes that describe them (the energy mix by hour, curtailment, EIA's annual cross-check, the queue statistics)

24 October 2026, about 15:08 UTC, on lab-desktop (the data machine), chain 121, unattended. Precheck passed (`runs/c121/pre2494.out`). Model spend USD 0. Pulls: none.

## Read these first

- **37 of the 537 tables in `coverage.csv` have no method note** (`build_coverage.method_cell` empty on main). Twelve of them are linked on chain 120's branch (session 2480) or named on a `Tables:` line of chains 118's and 119's branches, so 25 were left. Six are linked here, each to a note that already describes it in its text:
  - `generation_mix_hourly_profile` and `generation_mix_records` → `generation_mix_hourly.md`. The note's table of tables and its two sections are theirs. The table's variables are the hour averages, MWh, shares and counts the section names (units MW, MWh, pct, count). The records table holds the five records, each for the whole history and for one local year (`year_` variables).
  - `caiso_curtailment_profile` → `caiso_curtailment_intervals.md`. The note's table lists it (`warehouse/derived/curtailment_profile.py`), and its section gives the hour-of-day profile by month and reason, with battery charging in the same hours. The table holds `avg_battery_charging_mw_hNN` among its variables.
  - `iso_curtailment_monthly` → `curtailment.md`. The note's opening line names it as a derived table, but mid-line, which `method_notes` does not read. Its "Monthly" section gives the variables, the `share_` five among them.
  - `eia_annual_crosscheck_ba` → `eia_annual_crosscheck.md`. The note names it as the second of its two tables. The table's variables are EIA-923's and EIA-930's net generation, the hours, the gap in MWh and in percent.
  - `iso_queue_statistics` → `energy_projects.md`. Its section "Queue statistics" (session 348) is the table's, and the variables it names (`mw_operating`, `positions_waiting`, `wait_years_mean` among them) are in the table.
- **A `Tables:` line after each note's title,** and the six Method cells set in `docs/coverage.md` from `build_coverage.method_cell` (`runs/c121/cells.py`, from session 2480's).
- **No contradiction** between the notes and the tables' coverage rows (all six derived, public, power).
- **Left for a later session (19):** `ai_power_regions`, `ba_supply_monthly`, `datacenter_queue_positions`, `eia930_demand_weather`, `eia930_generation_latest`, `ercot_all_hub_prices_history`, `iso_all_capacity_prices`, `iso_hub_prices_history`, `iso_rt_top_intervals`, `iso_rtm_hub_prices`, `large_load_rules`, `large_load_rules_internal`, `large_load_statements`, `merchant_revenue_monthly`, `news_index`, `news_stories`, `state_generation_mix_monthly`, `texas_delivery_charges` and `texas_transmission_matrix`. Most are named in several notes, so the note that owns each needs a reading of its own.
- Tests: the seven files that read the method notes and cells (sessions 152, 255, 273, 281, 500, 674 and 89's MISO pause): 68 tests, OK (`runs/c121/s2494_tests.out`).

## Decisions made without you

- **A `Tables:` line added to a note that already describes its tables,** as sessions 2389, 2438 and 2480 did.
- **The six chosen** where one note plainly owns the table; tables named in many notes are left.

## For Samuel's ruling

- None.

## Files

- Changed: `docs/methods/generation_mix_hourly.md`, `docs/methods/caiso_curtailment_intervals.md`, `docs/methods/curtailment.md`, `docs/methods/eia_annual_crosscheck.md`, `docs/methods/energy_projects.md`, `docs/coverage.md` (six Method cells). New: this report.
- On the data machine only: `runs/c121/s2494_tables.py`, `runs/c121/cells.py`.
