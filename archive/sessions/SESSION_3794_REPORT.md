# Session 3794 report: the hunt again where data moved

Energy Research Warehouse (ERW). Chain 215, data machine (lab-desktop), 12 November 2026 18:35 to 18:48 UTC. Opus 5.5. Model spend USD 0. Requests: none to any publisher.

## Read these first

- **No draft has a newer full year to compute, so nothing was recomputed.**
  - `check.py --tables <main checkout>/warehouse/output` was run again after the data machine's run of 17:00 had moved its tables: **185 of 185 drafts reproduce** from their own scripts.
  - Each script takes its table's last full year. A table that now held a newer full year would give a figure other than the draft's expected one, and the check would name it; none did.
- **The tables that moved today** (the data machine's: ERCOT's node prices, CARB's auction, EIA-930's interchange, the CAISO and ERCOT forecasts, the reactor status, ERCOT's large loads and hub history) moved within 2026, a year not yet full. The daily run's tables have not moved: the dispatched run (43276079255) had not committed when this was read.
- **The count by family is unchanged:** 185 (generation_pipeline 35, prices 33, queues_deals_datacenters 27, oil_products_world 18, tariffs_policy 12, demand 12, gas 11, cross_family 8, coal_uranium_metals 8, other_us 7, markets_operations 7, emissions_climate 7).
- **Nothing approved.**

## Decisions made without you

- **No `--replace` rerun of unchanged drafts.** A November refresh cannot complete a year; the next real recompute is in January, or when an annual table publishes a new year (EIA's annual releases), which the check finds.

## For Samuel's ruling

- None.
