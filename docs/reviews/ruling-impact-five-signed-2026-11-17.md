# Ruling impact: across the five signed tools (17 November 2026)

Session 7598 (samueloldlaptop). The one line marked "Changes a figure" under "Across the five signed tools (battery, generator, datacenter, Research, Grid)" in `docs/reviews/rulings-for-samuel-2026-11-17.md` (branch `wip/7560-six-reads`). No page and no default was changed.

- **Script:** `runs/ruling_impact/five-signed_impact.py`, its printout `five-signed_impact.out`. It reads this machine's copy of `price_years_by_window` (the run of 20 October 2026: battery 234 rows, generator 108, datacenter 2,412) for each window's last month, beside the newest month the pages' monthly tables hold (`battery_stack_monthly`; `cost_of_power_monthly` as the live set served it on 16 November).
- **What could not be computed:** the rebuilt values themselves. The table is computed by the pages' own code (`site/scripts/price-years.mjs`) over what each page reads from the live set; this machine cannot build the site or hold a copy of the live set, so the lag the signature pack measured is quoted, not recomputed.
- **No model call** (spend USD 0).

| # | Line (the question) | Pages and cells | Default | Other choice | Change |
|---|---|---|---|---|---|
| 1 | Rebuild the "Price years" table in the data machine's daily run, so each page's "Price years" default keeps up with its headline | `/cost-of-power/battery`, `/cost-of-power/seller`, `/cost-of-power`: the "Price years" selector's default figure (and every window ending in the newest months) | Rebuilt by hand on the data machine | Rebuilt daily | Before the hand rebuild of 14 November the default lagged its headline by 0.6 to 1.0 percent: CAISO's battery 79.31 against 79.80 (-0.49), the datacenter page 33.73 against 34.07 (-0.34). On this machine's copy every rolling window ends in September 2026 (battery 144 rows, datacenter 1,044, generator 24) while the monthly tables the headlines read already hold October 2026, so between hand rebuilds the default lags by at least one month; a daily rebuild would close it each day. The size of the lag in any month depends on that month's prices; the next one is not computed here |
