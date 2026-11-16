# Where power is cheap (/prices/compare): faults found by its replication, 16 November 2026

Energy Research Warehouse (ERW), chain 301, session 7012 (data machine). Found by `replication/compare/replicate.py`, which recomputes every figure of `site/data/price_compare.json` from the warehouse's tables by `docs/methods/hub_price_comparison.md` alone. States: `open`, `fixed (<commit>)`, `ruling`, `not a fault`.

| # | Where | The figure | The fault | The fix | State |
|---|---|---|---|---|---|
| 1 | Twelve months, ERCOT Houston, real time, share of hours below zero | 1.63 (143 of 8,760 hours) | An hour whose four 15-minute prices sum to exactly zero was counted as negative, or not, by the float sum's noise (a mean of -4e-19 or +1e-17): Houston counted one such hour, West did not. The method says "below zero" | `price_compare.hourly` rounds an hour's mean to 9 places before any comparison (test 7012); the table and the file rebuilt: 1.62 (142) | fixed (session 7012, wip/c301-next) |
| 2 | The whole file | built 5 October 2026, windows to September 2026 | Not a fault: the windows end with the last month every hub of the history holds to its end, and the histories do not hold October whole yet; the rebuild of 16 November moved 14 rows (CAISO's 25 hours added since 5 October) | none | not a fault |
