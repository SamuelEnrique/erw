# Ruling impact: /learn/problems, the problem sets (17 November 2026)

Session 7582 (samueloldlaptop). The one line marked "Changes a figure" under /learn/problems in `docs/reviews/rulings-for-samuel-2026-11-17.md` (branch `wip/7560-six-reads`). No page and no default was changed.

- **Script:** `runs/ruling_impact/problem-sets_impact.py`, its printout `problem-sets_impact.out`. Prices from `warehouse/output/eia_fuel_spot_prices.csv` (EIA, WTI Cushing, retrieved 13 November 2026); New Mexico's rates from `site/data/severance_rules.json`; the problem sets' rule (the month's mean before rounding) as `docs/reviews/severance-read-2026-11-16.md` row 13 states it, which reproduces the answer key's USD 7,287.54.
- **No model call** (spend USD 0).

| # | Line (the question) | Page and cell | Default | Other choice | Change |
|---|---|---|---|---|---|
| 1 | Read New Mexico's Taxation and Revenue Department table for September 2026 on and extend the rules file, so question 4 of "Storage and taxes" (1,000 bbl in October 2026) uses October's rates | `/learn/problems/storage-and-taxes`, question 4, the New Mexico step and its answer (and the edition's answer key) | The newest rates held, 1 April to 31 August 2026 (severance 3.75, emergency school 3.15, conservation 0.24 percent), with their period said | October's rates | The answer at the held rates: USD 7,287.54 (1,000 bbl at October's mean of USD 102.066364). October's own rates are data not held, so the true figure is not computed. The one rate the table changes by the price of oil is the conservation tax, 0.19 or 0.24 percent: at 0.19 the answer reads USD 7,236.51 (-51.03, -0.70 percent); at 0.24 it does not move. A change in the other two rates would move it by USD 10.21 for each 0.01 point |
