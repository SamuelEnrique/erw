# Page files of grid conditions (contract)

Written by session 9000 (chain 601, parts C to G) before each file lands. A shape that later has to change is changed here first, with a dated line saying what moved. Every file is written whole by its builder, from warehouse tables only; no builder makes a request.

## 1. `site/data/conditions/congestion.json` (part C, the page `/congestion`)

Builder: `warehouse/derived/congestion_page.py`. Method: `docs/methods/grid_congestion.md`. Reads `constraints_binding_hourly` and `price_congestion_hourly`; writes beside it the tables `constraints_binding_monthly` and `price_congestion_monthly`.

| Key | Unit | What |
|---|---|---|
| `built`, `method`, `contract`, `license`, `tables`, `unit`, `market` | | when written (UTC), the method note, this file, `public`, the four tables, `USD/MWh`, `day-ahead` |
| `sign_rule`, `cost_rule`, `share_rule` | | the three rules in words, shown on hover |
| `operators[]` | | every operator of the seven grids: `id`, `name`, `status` (`shown`, `license needed`, `source needed`, `paused`), `why` (for any not shown) |
| `sources.<op>` | | `constraints` and `prices`: the operator's report in words |
| `constraints.<op>.time`, `.years`, `.first`, `.last` | | the clock of the hours, the years held, the first and last hour held (UTC) |
| `constraints.<op>.days_held.<year>`, `.constraints_by_year.<year>`, `.hours_by_year.<year>` | days, count, constraint-hours | days with any binding row; constraints that bound; rows |
| `constraints.<op>.top.<year or all>` | | `by_hours`, `by_cost`: the 25 constraint keys that bound most hours, and whose shadow price summed highest |
| `constraints.<op>.constraints.<key>` | | every constraint in any top list: `name`, `contingency`, `monitored`, `type`, `nerc_id` (the operator's columns, `null` where it prints none), `first`, `last`, `hours`, `abs_mean`, `abs_max` (USD/MWh), `cost` (USD/MWh times hours) |
| `...constraints.<key>.by_year.<year>` | | `hours`, `abs_mean`, `abs_max`, `cost` |
| `...constraints.<key>.monthly[]` | | `[month YYYY-MM, hours bound, mean size of the price, highest size, mean signed price]`, a month only when it bound |
| `...constraints.<key>.hod_month` | hours | twelve rows (January to December) of 24 counts (hours of the day in the operator's clock), every year held summed |
| `places.<op>[]` | | each hub and zone: `id` (`op:node`), `node`, `name`, `time`, `years`, `first`, `last` |
| `places.<op>[].monthly[]`, `.monthly_columns` | USD/MWh, hours, percent | `[month, hours, lmp_mean, energy_mean, congestion_mean, loss_mean, ghg_mean, congestion_share_pct]`; `ghg_mean` `null` where the operator prints none; the share `null` when the mean LMP is not above zero |
| `places.<op>[].by_year.<year>` | | `hours`, `lmp_mean`, `congestion_mean`, `congestion_share_pct`, `hours_congestion_up`, `hours_congestion_down`, `congestion_max`, `congestion_min` |
| `places.<op>[].hod_month_congestion_mean.<year>` | USD/MWh | twelve rows of 24 means of the congestion part, `null` for a cell with no hour held |

A real sample follows when the file is first built from the warehouse.
