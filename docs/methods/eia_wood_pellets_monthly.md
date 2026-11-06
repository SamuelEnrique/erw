# Densified biomass (wood pellets): prices, feedstock cost, plants and employees, a month

Energy Research Warehouse (ERW), method note written in session 677 (chain 043) for tables first written on 21 or 22 October 2026.

Tables: `eia_wood_pellets_monthly`

Connector: `warehouse/connectors/eia_wood_pellets.py` (session 558; the feedstock cost added in session 575).

## Publisher and report

U.S. Energy Information Administration (EIA), Monthly Densified Biomass Fuel Report, read through EIA's API v2, routes under `densified-biomass`. The report's page is `https://www.eia.gov/biofuels/biomass/`. The connector asks each route:

`https://api.eia.gov/v2/densified-biomass/<route>/data/?frequency=monthly&data[]=<column>&start=2016-01`

| Route | EIA's column | Variable | Unit | Keyed by |
|---|---|---|---|---|
| `sales-and-price-by-region` | `average-price` | `domestic_price` | `USD/short_ton` | region |
| `export-sales-and-price` | `average-price` | `export_price` | `USD/short_ton` | the U.S. |
| `capacity-by-region` | `number-of-facilities` | `facilities` | `count` | region |
| `capacity-by-region` | `number-of-fte-employees` | `fte_employees` | `count` | region |
| `feedstocks-and-cost` | `cost` | `feedstock_cost` | `USD/short_ton` | fuel type |

Pages of 5,000 records sorted by period, 3 seconds apart. The key is read from `EIA_API_KEY` and is redacted in every `source_url`. The header's Source line names three routes; the feedstocks route is the fourth, added in session 575.

## Vintage and revision rule

The header gives months 2016-01 to 2026-05, and EIA's records by route: sales-and-price-by-region 500, export-sales-and-price 113, capacity-by-region 500, feedstocks-and-cost 496. The first month, 2016-01, is fixed in the connector.

The table is written with `ip.write_snapshot`: each run replaces the whole table, and the header says the previous file held 1,613 rows (now 2,090). A page an earlier run saved in `warehouse/raw/eia_wood_pellets/` is reused unless `--fresh`; `--offline` asks nothing. A new month or a revised figure reaches the table only through a page asked again. Ceiling: 13 requests a run. A read shorter than EIA's count on any route stops the run.

## Shape

Series. 13 entities.

- `entity`: `eia_wood_pellets:<route short name>:<region or fuel type>`: `sales:` and `capacity:` with `EAST`, `SOUTH`, `WEST` and `US-TOTAL`; `export:US`; `feedstocks:` with `RP` (Roundwood/Pulpwood), `SR` (Sawmill Residuals), `WPMR` (Wood Product Manufacturing Residuals) and `OR` (Other Residuals).
- `variable` and unit as in the table above. Rows: `domestic_price` 500, `export_price` 113, `facilities` 500, `fte_employees` 500, `feedstock_cost` 477. EIA's tons are short tons.
- `ts_utc`: the month's first day at 00:00:00Z; `freq` `P1M`; `geo` `US`; `market` empty.
- `node`: EIA's region name, or the fuel type's name for the feedstocks.
- `source`, `source_url`, `retrieved_at`; `vintage` empty.

`US-TOTAL` holds the regions: a sum takes one level.

## License

ERW verdict: public (`docs/licenses.md`). Header: License: public (a work of the U.S. government; cite "U.S. Energy Information Administration, Monthly Densified Biomass Fuel Report").

## Cross-check

None in the connector. It stops on a unit not in its map, on a key given twice, and on a read shorter than EIA's count.

## What it does not hold

- EIA's quantities and capacity in tons: the vocabulary has no tonnage, a ruling asked in sessions 490 and 519.
- A figure EIA withholds has no row; nothing is filled. Other Residuals' feedstock cost ends in 2026-02; the other series reach 2026-05.
- Prices by state or plant: only EIA's regions, the U.S. and the fuel types.
