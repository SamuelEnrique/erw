# Session 8224 report (chain 502, lab-desktop second window)

19 November 2026, 13:16 to 13:19 UTC (read from the clock). Opus 5.5. Model spend: USD 0.

## Part D: oil_products_world, 3 drafts (the Gulf of America's federal waters)

- `boem_ogor_lease_production_monthly` (BOEM's OGOR-A, every lease's monthly oil and gas, 1996 to June 2026, 1.1 million rows; no draft had read it): the Gulf's federal offshore oil and gas production and its producing leases, by year (`deep/boem502.py`).
  - Oil: 1,948 thousand barrels a day in 2025 against 1,009 in 1996.
  - Gas: 2,079 million cubic feet a day in 2025 against 14,196 in 1996.
  - Producing leases: 526 in 2025 against 1,752 in 1996.
- The oil figures sit on EIA's published scale for the federal Gulf (about 1.0 million barrels a day in 1996, about 1.9 million in 2025).
- Every oil_products_world draft reproduces (33 of 33); 3 of 3 new do-files hold.

## Code

- `warehouse/analysis/findings/deep/boem502.py` on `wip/8202-findings` (`3b11b27e5`).

## Needs the key

- Nothing.
