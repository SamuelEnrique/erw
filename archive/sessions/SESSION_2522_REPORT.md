# Session 2522 report: two more held tables linked to the notes that describe them (capacity prices, merchant revenue)

24 October 2026, about 19:16 UTC, on lab-desktop (the data machine), chain 123, unattended. Precheck passed (`runs/c123/pre2522.out`). Model spend USD 0. Pulls: none.

## Read these first

- **Of the 13 tables session 2508 left, two have a note that plainly owns them:**
  - `iso_all_capacity_prices` → `capacity_and_ancillary.md`, whose section "Capacity prices: `iso_all_capacity_prices`" describes its rows, its markets and its units;
  - `merchant_revenue_monthly` → `cost_of_power.md`, whose section "The table: `merchant_revenue_monthly`" gives its entity, partition, timestamp and variables.
- **A `Tables:` line after each note's title,** and the two Method cells set in `docs/coverage.md` (`runs/c123/cells.py`).
- **Left (11), each named in notes only as an input or in passing:** `ai_power_regions` and `ba_supply_monthly` (listed in `impossible_hours.md` among the tables its corrections touch), `datacenter_queue_positions`, `ercot_all_hub_prices_history` and `iso_hub_prices_history` (inputs of `hub_price_comparison.md`, `ercot_hub_prices_daily.md` and others), `iso_rtm_hub_prices` (named in `iso_dam_hub_prices.md` among what it does not hold), `news_index`, `news_stories`, and the three large-load tables (`large_load_rules`, `large_load_rules_internal`, `large_load_statements`, left to chain 120's landing). Each needs a note of its own, written from its builder.
- Tests: the seven files that read the notes and cells pass (`runs/c123/s2522_tests.out`).

## Decisions made without you

- **Only tables a note owns are linked;** a table a note names as an input is left for a note of its own.

## For Samuel's ruling

- None.

## Files

- Changed: `docs/methods/capacity_and_ancillary.md`, `docs/methods/cost_of_power.md`, `docs/coverage.md` (two Method cells). New: this report.
- On the data machine only: `runs/c123/s2522_tables.py`, `runs/c123/cells.py`.
