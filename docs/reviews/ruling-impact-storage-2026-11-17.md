# Ruling impact: /storage, battery storage (17 November 2026)

Session 7590 (samueloldlaptop). The one line marked "Changes a figure" under /storage in `docs/reviews/rulings-for-samuel-2026-11-17.md` (branch `wip/7560-six-reads`). No page and no default was changed.

- **Script:** `runs/ruling_impact/storage_impact.py`, its printout `storage_impact.out`. Table: `storage_daily_cycle` (this machine's copy, to 7 October 2026), public grids only (CAISO's own data; EIA-930 for ERCOT and SPP).
- **No model call** (spend USD 0).

| # | Line (the question) | Page and cells | Default | Other choice | Change |
|---|---|---|---|---|---|
| 1 | Give the daily cycle a month's total discharge by grid (ERCOT's October 2026, for one) beside the newest day and the 30-day spark | `/storage`, the daily cycle panel (a new figure a grid; no figure that stands moves) | The newest day and the 30-day spark | A month's total too | September 2026, the latest whole month this machine holds: CAISO 1,335,586 MWh discharged (44,520 a day), ERCOT 787,056 MWh (26,235 a day), SPP 31,766 MWh (1,059 a day). August 2026: 1,462,303, 796,960 and 33,939 MWh. Beside them the panel now shows the newest day (ERCOT 28,606 MWh on 6 October) and the 30 days to it (767,302). ERCOT's October 2026 whole, the line's example, needs the rows after 7 October that the site's table holds and this copy does not: not computed here |
