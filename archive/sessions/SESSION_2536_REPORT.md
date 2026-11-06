# Session 2536 report: six held tables linked to the notes that describe them, and two contradictions set right

24 October 2026, about 21:18 to 21:30 UTC, on lab-desktop (the data machine), chain 124, unattended. Precheck passed (`runs/c124/pre2536.out`). Model spend USD 0. Pulls: none.

## Read these first

- **26 tables in `coverage.csv` have no note** by `build_coverage.method_notes()` (a note named after the table, or a note's `Tables:` line). Three are this chain's own (session 2541 writes their notes). Besides session 2522's eleven, twelve more were found: tables that a note describes at length but whose name the note does not carry.
- **Six linked by a `Tables:` line,** each to the note that plainly owns it, and their Method cells set in `docs/coverage.md` (`runs/c124/s2536/notes.py`, `runs/c124/s2536/cells.py`):
  - `storage_buildout_monthly` → `storage_buildout.md` (its table of tables describes it);
  - `price_years_by_window` → `price_years.md` (its one derived table);
  - `grid_network_nodes` → `grid_network.md` (its section "Nodes");
  - `caiso_reliability_daily` → `california_reliability.md` (its section 2);
  - `cost_of_power_hourly_profile` and `cost_of_power_carbon` → `cost_of_power.md` (their sections; added to its `Tables:` line beside `merchant_revenue_monthly`).
- **Each note checked against its table** (session 960's form): the variables, entities and columns each note names are in the table (the storage build-out's 26 variables by duration and year online; the price years' windows; the grid network's 70 nodes with `x_name` and `x_iso`, `demand_mw` and `intensity_generation` for the seven ISO BAs only; the reliability table's 22 variables; the profile's `rt_mean_h00` to `rt_mean_h23` and `rt_days_*`; the carbon table's three). Two contradictions, each set right by a dated line in the note, the earlier text kept:
  - `california_reliability.md` says the table runs from 2018-07-01 (2,980 days). That window is the demand rows' (2,999 days now); the `notices_<type>` rows follow `caiso_grid_emergencies` back to its first notice, 1998-05-30, the table's first day.
  - `cost_of_power.md` says the hourly profile holds the last 12 local months. The table holds 13 (2025-10 to 2026-10): its header says 336 rows (October 2025) were carried over from the previous file, a month the rolling price tables no longer reach.
- **Left (17 besides this chain's three),** each named in notes as an input, in passing, or by a note that describes several tables at once: `ai_power_regions`, `ba_supply_monthly`, `cost_of_power_monthly` (named nowhere in `cost_of_power.md`, which calls it "the monthly table"), `datacenter_projects`, `datacenter_queue_positions`, `ercot_all_hub_prices_history`, `iso_hub_prices_history`, `iso_rtm_hub_prices`, `news_index`, `news_stories`, the policy monitor's `policy_actions`, `policy_reads`, `policy_reads_evidence` and `large_load_rule_reads` (described in `policy_monitor.md`'s table, a later session's link), and chain 120's large-load tables.
- **Tests:** the 107 test files that read the notes, the cells or `docs/methods` (1,385 tests) pass but for test 705, the known worktree artifact (`runs/c124/s2536/tests.out`).

## Decisions made without you

- **Six, not more:** the session's bound. The policy monitor's four tables are left whole for one later session.
- **A dated line, not a rewrite,** where a note and its table disagree.

## For Samuel's ruling

- None.

## Files

- Changed: `docs/methods/storage_buildout.md`, `price_years.md`, `grid_network.md`, `california_reliability.md`, `cost_of_power.md`; `docs/coverage.md` (six Method cells). New: this report.
- On the data machine only: `runs/c124/s2536/`.
