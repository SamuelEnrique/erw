# Session 8226 report (chain 502, lab-desktop second window)

19 November 2026, 13:24 to 13:27 UTC (read from the clock). Opus 5.5. Model spend: USD 0. Parts B and C checked at 13:18: both still waiting.

## Part D: oil_products_world 8 drafts, gas 8 drafts (by country)

- `eia_world_oil_gas_annual` (EIA's international data, 448,267 rows; no draft had read it), from 1980: crude oil production and petroleum consumption (oil_products_world), dry gas production and exports (gas); the world, then the United States, then the largest moves (`deep/worldoil.py`).
- The three strongest:
  - US crude oil production: 13,662 thousand barrels a day in 2025 against 8,597 in 1980.
  - US dry gas exports: 7,707 billion cubic feet in 2024 against 49 in 1980.
  - China's petroleum consumption: 16,371 thousand barrels a day in 2024 against 1,940 in 1980.
- Every draft of both families reproduces (41 and 35 of them); 16 of 16 new do-files hold.

## Code

- `warehouse/analysis/findings/deep/worldoil.py` on `wip/8202-findings` (`d71d3091a`).

## Needs the key

- Nothing.
