# Session 8218 report (chain 502, lab-desktop second window)

19 November 2026, 12:49 to 12:53 UTC (read from the clock). Opus 5.5. Model spend: USD 0. Parts B and C checked at 12:49: both still waiting.

## Part D, second round: oil_products_world, 12 drafts (what the US exports)

- `eia_petroleum_exports_by_destination` (EIA, monthly from 2015; no draft had read it): US crude oil exports by destination and US exports of each product, thousand barrels a day (a year's barrels over its days), years with all twelve months listed (`deep/oilx502.py`).
- The table writes some zero months and leaves others out (South Korea's 2015 lists April only), so a month with no row is not taken for zero; a destination's sentence says "the first year with all twelve months listed".
- The three strongest:
  - US crude oil exports: 3,961 thousand barrels a day in 2025 against 465 in 2015.
  - US crude exports to the Netherlands: 862 thousand barrels a day in 2025 against 92 in 2017.
  - US ethane exports: 577 thousand barrels a day in 2025 against 65 in 2015.
- Every oil_products_world draft reproduces (30 of 30); 12 of 12 new do-files hold.

## Code

- `warehouse/analysis/findings/deep/oilx502.py` on `wip/8202-findings`.

## Needs the key

- Nothing.
