# Session 519 report: coal production by mine, probed (its unit is not in the vocabulary); coal prices pulled in its place

21 October 2026, from 20:19 UTC, on lab-desktop (the data machine), the fourth session of `queue/done/027-night-22-october-sources.md`. Model spend USD 0.

## Read these first

- **Coal production by mine: probed, not pulled.** EIA's route `coal/mine-production` gives each mine's production in short tons a year (2001 to 2024), with labor hours, employees, location and operator. The unit vocabulary has `USD/short_ton` but no quantity in short tons.
  - By the chain's rule, the table waits for the unit (under "For Samuel's ruling"), as session 490's AEO rows in short tons do.
- **In its place: EIA's coal market sales price** (route `coal/market-sales-price`, the Annual Coal Report), whose unit, `USD/short_ton`, the vocabulary holds. `warehouse/connectors/eia_coal_prices.py` writes the series table `eia_coal_prices_annual`.
  - 2,781 rows: 145 series, by producing state or region and by market type (open market, captive, total), from 2001 to 2024.
  - EIA's sales tonnages are not taken, and a withheld price has no row.
- **Cross-check, an order of magnitude only** (`runs/s519/crosscheck.py` on the data machine): the mine price of each producing state against the delivered cost of coal at the same state's power plants (`eia_power_plant_fuel_costs`), 2019 to 2024.
  - North Dakota (mine-mouth, thermal coal only): median ratio 1.07; 2024: 23.70 at the mine and 25.05 delivered.
  - Elsewhere the mine price is often above the delivered cost: West Virginia 0.66, Pennsylvania 0.58, Kentucky 0.74. The mine prices include metallurgical coal, which power plants do not buy.
  - The check confirms the order of magnitude and the units, not each figure.
- **Robots and terms**: EIA's API is allowed (record 1, public).
- **Written under the data lock** (20:21 UTC) with `--offline` (0 requests). The validator, coverage and archive exited 0.
- **Held** from `/data`'s catalogue and Redivis v1 until uploaded. Sector rule (`coal`). Tests: `tests/test_session519.py`, 4.

## Pulls against their ceilings

| Host | Requests | What |
|---|---|---|
| api.eia.gov | 4 + 1 of 6 (price) | the coal routes, `mine-production`'s and `market-sales-price`'s metadata (one probe script failed on its printing after its request); the price's one page |

## For Samuel's ruling

- `short_ton` (a quantity) in the unit vocabulary, for coal production by mine, coal sales and AEO's coal rows (sessions 490 and 519).

## Files

- New: `warehouse/connectors/eia_coal_prices.py`, `tests/test_session519.py`, this report. Changed: `warehouse/metadata/build_coverage.py`, `warehouse/supabase/live_set.yaml`, `warehouse/redivis/release_v1.py`, `docs/redivis/release-v1/`, `docs/coverage.md`, `docs/licenses.md`, `warehouse/metadata/{coverage,archive_manifest,sources,license_tables}.csv`.
