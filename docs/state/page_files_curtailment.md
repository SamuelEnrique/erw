# Page files of the curtailment tool's "Where and when" view (contract)

Written by session 8014 (chain 581, part C, step 2) before the file lands. The builder: `warehouse/derived/where_when.py`. The method: `docs/methods/where_when.md`. The view: `/curtailment/where-when` (new; the page `/curtailment` as it is does not change). A shape that later has to change is changed here first, with a dated line saying what moved.

## The file: `site/data/curtailment/where_when.json`

One file, written whole by the builder. No warehouse table of its own: it reads `caiso_curtailment_profile` (through `site/data/curtailment_profile.json`, the same figures), `spp_curtailment_daily`, and the public hub and zone price tables that `free_energy.py` reads, with its reader and its hour rule.

| Key | Unit | What |
|---|---|---|
| `built`, `method`, `contract`, `license`, `tables`, `internal_tables`, `near`, `hour_rule`, `whole_year_rule` | | when written, the method note, this file, `public`, every table read, any table left unread for its license, the 95 percent rule, the rules in words |
| `curtailment[]` | | one entry a place that publishes curtailment: `id`, `name`, `grid`, `kind` (`curtailment`), `table`, `vintage`, `unit` (MWh), `time`, `source`, `years` |
| `curtailment[].matrix.<year>.<fuel>` | MWh | CAISO only (`by_hour` true): twelve rows (January to December, `null` for a month not held), each 24 numbers, the hours of the day in Pacific clock time |
| `curtailment[].by_year.<year>` | MWh | the year's total by fuel or variable, `null` unless 90 percent of its days are held (`whole`) |
| `curtailment[].monthly.<variable>.<YYYY-MM>`, `.months`, `.variables`, `.entities` | MWh | SPP only (`by_hour` false, with `by_hour_reason`) |
| `curtailment[].days_held.<year>` | days | CAISO: `days_held`, `days_in_year` |
| `curtailment_not_held.<grid>` | | why a grid has no curtailment here (ERCOT publishes none; MISO paused; PJM, NYISO, ISO-NE none held) |
| `prices[]` | | one entry a hub or zone whose price a page may show: `id` (`grid:node`), `name`, `grid`, `grid_name`, `kind` (`hub`, `zone`, `average`), `unit` (hours), `time`, `tables`, `freq`, `years` |
| `prices[].matrix.<year>` | hours | `basis` (`rt` or `da`), `negative` and `held`: twelve rows of 24 counts, months and hours in the grid's standard time |
| `prices[].by_year.<year>` | hours, percent | `basis`, `hours_in_year`, `hours_held`, `negative`, `whole`, `share_negative_pct` (`null` unless whole) |
| `price_blank.<grid>` | | a grid whose prices are not drawn: `name`, `words` ("license needed: ..." or the pause), `regions` (its places, named) |
| `ranked_negative[]` | | the places (averages left out) by the share of hours below zero in each one's newest whole year, largest first: `id`, `name`, `grid`, `kind`, `year`, `share_negative_pct`, `negative`, `hours_held` |

A cell's share below zero is `negative` over `held` for that month and hour; a cell with no hour held has `held` 0 and no share.

## A real sample (from the trial of 20 November 2026; rows cut to their first two months; CAISO's solar row shows the hours 06 to 11, HB_WEST's rows the hours 00 to 05)

```json
{
 "license": "public", "near": 0.95,
 "curtailment": [
  {"id": "caiso", "name": "CAISO, the whole system", "grid": "caiso", "kind": "curtailment", "table": "caiso_curtailment_profile", "vintage": "2026-10", "unit": "MWh", "years": ["2019", "2020"], "by_hour": true,
   "matrix": {"2019": {"solar": [[0.0, 35.8, 861.6, 1504.6, 1920.1, 2058.0], [1.7, 268.4, 4950.0, 7573.0, 10536.3, 12519.8]]}},
   "by_year": {"2019": {"solar": 921684.4, "wind": 43557.0, "whole": true}, "2026": {"solar": null, "wind": null, "whole": false}}},
  {"id": "spp", "name": "SPP, the whole system", "grid": "spp", "table": "spp_curtailment_daily", "by_hour": false, "by_hour_reason": "SPP publishes its curtailment by day, not by hour, so it has no hour of the day",
   "by_year": {"2025": {"days_held": 365, "days_in_year": 365, "whole": true, "curtailed_wind_mwh": 13389377.7, "curtailed_solar_mwh": 107902.5}}}
 ],
 "prices": [
  {"id": "ercot:HB_WEST", "name": "HB_WEST", "grid": "ercot", "grid_name": "ERCOT", "kind": "hub", "unit": "hours", "years": ["2025"],
   "matrix": {"2025": {"basis": "rt", "negative": [[1, 1, 1, 1, 1, 1], [1, 1, 1, 2, 0, 0]], "held": [[31, 31, 31, 31, 31, 31], [28, 28, 28, 28, 28, 28]]}},
   "by_year": {"2025": {"basis": "rt", "hours_in_year": 8760, "hours_held": 8760, "negative": 637, "whole": true, "share_negative_pct": 7.27}}}
 ],
 "price_blank": {"nyiso": {"name": "NYISO", "words": "license needed: NYISO's own terms ask for written permission [cut]", "regions": ["CAPITL", "CENTRL"]}},
 "ranked_negative": [{"id": "spp:SPPNORTH_HUB", "grid": "spp", "kind": "hub", "year": "2025", "share_negative_pct": 11.92, "negative": 1044, "hours_held": 8760}]
}
```
