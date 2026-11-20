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

A real sample (the file built on 20 November 2026 at 12:13 UTC; lists cut) is at the end of this contract.

## 2. `site/data/conditions/<operator>.json` and `index.json` (part G, the page `/conditions`)

Builder: `warehouse/derived/conditions_page.py`. Method: `docs/methods/grid_conditions.md`. One file for each of `caiso`, `ercot`, `spp`, `miso`, `pjm`, `nyiso`, `isone`, and `index.json`.

| Key | Unit | What |
|---|---|---|
| `built`, `method`, `license`, `op`, `name`, `ba`, `time` | | when written, the method note, `public`, the grid's id, name and EIA-930 code, its clock |
| `strips.<demand, out, constraints, scarcity, alerts, reserves>` | | `status` (`shown`, `license needed`, `source needed`, `paused`, `not published`, `not read`), `source` when shown, `why` when not, `note` |
| `first_day`, `last_day` | | the first and last local day held |
| `daily_columns`, `daily[]` | MW, count, USD/MWh, hours | `[day, demand_peak, demand_min, forecast_peak, out_mean, out_max, cons_hours, cons_max, adder_hours, adder_max, alerts]`, one row a local day from 2018-07-01; `null` where a strip is not held that day |
| `windows[]` | | `id` (`recent` or an event id), `title`, `start`, `end` (local days, both included) |
| `hourly_columns`, `hourly.<window id>[]` | MW, count, USD/MWh | `[ts_utc, demand, forecast, out_total, out_planned, out_forced, cons_n, cons_max, adder]`, one row an hour of the window |
| `alert_columns`, `alerts[]` | | `[date, kind, start, end, source_url]`, CAISO and ERCOT |
| `index.json` | | `built`, `method`, `contract`, `license`, `recent_days` (35), `events[]` (`id`, `title`, `start`, `end`, from `site/data/regions/events/`), `operators[]` (`op`, `name`, `ba`, `strips` status by strip, `first_day`, `last_day`) |

## Real samples (built 20 November 2026; lists cut to their first entries)

`congestion.json`, CAISO's constraint whose shadow price summed highest in 2025, and its first place:

```json
{"constraints": {"caiso": {"years": ["2025", "2026"], "top": {"2025": {"by_cost": ["caiso:39021_SC21ATP _70.0_34888_ARVIN   _70.0_BR_1 _1|PG1 WHELRG-WEEDPC 70", "caiso:24723_CONTROL _115_24865_TAP188  _115_BR_2 _1|Base Case"]}}, "constraints": {"caiso:39021_SC21ATP _70.0_34888_ARVIN   _70.0_BR_1 _1|PG1 WHELRG-WEEDPC 70": {"name": "39021_SC21ATP _70.0_34888_ARVIN   _70.0_BR_1 _1", "contingency": "PG1 WHELRG-WEEDPC 70", "monitored": null, "type": null, "nerc_id": null, "first": "2021-05-11T19:00:00Z", "last": "2026-10-09T00:00:00Z", "hours": 3530, "abs_mean": 223.44, "abs_max": 4418.41, "cost": 788752.0, "by_year": {"2025": {"hours": 1785, "abs_mean": 310.3, "abs_max": 2220.31, "cost": 553893.0}}, "monthly": [["2021-05", 7, 58.42, 133.77, 58.42], ["2021-06", 40, 98.78, 1950.59, 98.78]], "hod_month": [[30, 33, 28, 41, 64, 66]]}}}}, "places": {"caiso": [{"id": "caiso:DLAP_PGAE-APND", "node": "DLAP_PGAE-APND", "name": "PG&E default load area", "time": "Pacific clock time (CAISO's operating day)", "years": ["2023", "2024", "2025", "2026"], "first": "2023-08-10T07:00:00Z", "last": "2026-11-21T07:00:00Z", "monthly_columns": ["month", "hours", "lmp_mean", "energy_mean", "congestion_mean", "loss_mean", "ghg_mean", "congestion_share_pct"], "monthly": [["2023-08", 528, 71.64, 75.53, -3.47, -0.42, 0.0, -4.8], ["2023-09", 720, 43.79, 41.03, 2.64, 0.12, 0.0, 6.0]], "by_year": {"2025": {"hours": 8760, "lmp_mean": 40.62, "congestion_mean": 2.65, "congestion_share_pct": 6.5, "hours_congestion_up": 5675, "hours_congestion_down": 2622, "congestion_max": 38.14, "congestion_min": -16.16}}}]}}

```

`ercot.json` on 15 February 2021 (Winter Storm Uri), and two of its hours:

```json
{"op": "ercot", "strips": {"out": {"status": "source needed", "why": "ERCOT publishes this only on paths its robots file disallows, or through an API whose key has not been made (the owner's ruling of 6 November 2026)"}, "scarcity": "shown"}, "daily_columns": ["day", "demand_peak", "demand_min", "forecast_peak", "out_mean", "out_max", "cons_hours", "cons_max", "adder_hours", "adder_max", "alerts"], "daily": [["2021-02-15", 65255.0, 43776.0, 76783.0, null, null, null, null, 22, 3185.5, 2]], "hourly_columns": ["t", "demand", "forecast", "out_total", "out_planned", "out_forced", "cons_n", "cons_max", "adder"], "hourly": {"uri_2021": [["2021-02-15T14:00:00Z", 49849.0, 74356.0, null, null, null, null, null, 3112.0], ["2021-02-15T15:00:00Z", 49597.0, 75857.0, null, null, null, null, null, 3185.5]]}}

```
