# Session 2961 report: method notes for the tables without one (with sessions 2960 to 2962)

6 November 2026, about 08:47 to 08:51 UTC, on lab-desktop (the data machine), chain 157 (the owner's), unattended. Model spend USD 0. Pulls: none.

## Read these first

- **No table is without a method note any more:** all 637 tables of coverage are named in some note under `docs/methods/` (the "roughly 40 of 21 October" have been written since).
- **20 tables were described in a note but named on no `Table:` or `Tables:` line,** which the chain asks for. Each now has one, in the note that describes it (commit `ea9b180b6`):
  - in their own notes: `api_cost_ledger`, `caiso_curtailment_intervals`, `energy_projects`, `ercot_grid_notices`, `ercot_hub_prices_daily`, `ercot_large_load_status`, `ferc_eqr_contracts`, `grid_peak_vs_capacity`, `hub_price_comparison`, `interconnection_queue_summary`, `known_data_faults`, `large_load_waits`, `scarcity_hours_by_grid`, `subregion_demand_growth`;
  - `ercot_wind_solar_hsl_monthly` in `ercot_wind_solar_hsl_hourly.md`;
  - `policy_reads_evidence` in `policy_monitor.md`;
  - `cost_of_power_monthly` in `cost_of_power.md` (its builder's note);
  - `iso_rtm_hub_prices`, `ercot_all_hub_prices_history` and `iso_hub_prices_history` in `iso_dam_hub_prices.md`, which describes the consolidated hub tables.
  - A note that had a `Tables:` line gained "Also: ..."; a note without one gained a line under its first paragraph.
- **Tests that read the method notes:** 759 passed, 25 skipped.
- **Sessions 2961 and 2962** had nothing left: the 20 were done in one pass.

## Decisions made without you

- **`cost_of_power_monthly` named in its builder's note** (`cost_of_power.md`), though the note's prose does not mention the table by name.

## For Samuel's ruling

- None.
