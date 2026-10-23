# The Annual Energy Outlook by Electricity Market Module region

Energy Research Warehouse (ERW), method note written in session 918 (chain 051) for a table first written on 23 October 2026.

Tables: `eia_aeo_emm_regions`

## Publisher and address

U.S. Energy Information Administration (EIA), Annual Energy Outlook 2026, Table 54 (Electric Power Projections by Electricity Market Module Region), through EIA's API v2, route `aeo/2026`, the API's `tableId` 62:
`https://api.eia.gov/v2/aeo/2026/data/?frequency=annual&data[]=value&facets[tableId][]=62&facets[scenario][]=cb2026`. Connector: `warehouse/connectors/eia_aeo_regions.py` (session 913). `eia_aeo_electricity` (session 490) holds the national Tables 8 and 9 in every case.

## Vintage and revision

AEO2026, case `cb2026`, the Counterfactual Baseline, 2025 to 2050, when written (pages retrieved 2026-10-23 08:14 to 08:15 UTC; written offline at `20261023T081725Z`). AEO2026 names no Reference case. A snapshot: each run replaces the table whole. A run reuses saved pages unless `--fresh` (ceiling: 17 requests; the table is 16 pages of 5,000 records); `--case` takes another case, about 16 requests more. The release is fixed in the connector (`RELEASE`), so AEO2027 needs it changed.

## Shape and variables

Series. `entity` `eia_aeo_2026_emm:<regionId>:<seriesId>`; regionId `5-1` to `5-25` the EMM regions, `5-0` the United States. EIA's series ids carry the region in their next to last part (`cap_NA_elep_NA_NA_NA_texr_gw` for Texas, `NA` for the U.S.). `variable` `value`; `node` "<region>: <series name>"; `ts_utc` the year's 1 January; `freq` `P1Y`; `geo` empty for a region (it spans states), `US` for 5-0. `x_scenario`, `x_scenario_name`, `x_history` (every row `PROJECTION`), `x_region`, `x_region_name`, `x_dollar_year`.

| EIA's unit | ERW unit | Factor | Rows | What |
|---|---|---|---|---|
| GW | `MW` | 1,000 | 35,152 | capacity by technology; cumulative planned and unplanned additions and retirements; end-use capacity |
| billion kWh | `MWh` | 1,000,000 | 21,632 | generation by fuel, sales by sector, net energy for load with imports and exports |
| cents/kWh (nominal, 2025) | `USD/kWh` | 0.01 | 10,816 | end-use prices and prices by service (generation, transmission, distribution) |
| $/MMBtu (nominal, 2025) | `USD/MMBtu` | 1 | 5,408 | fuel prices to the electric power sector |
| quadrillion Btu | `TBtu` | 1,000 | 2,704 | fuel use |

The 25 regions: Texas (5-1), Florida (5-2), MISO West, Central, East and South (5-3 to 5-6), New England (5-7), New York City and Long Island (5-8), Upstate New York (5-9), PJM East, West, Commonwealth Edison and Dominion (5-10 to 5-13), SERC East, Southeastern and Central (5-14 to 5-16), SPP South, Central and North (5-17 to 5-19), and WECC Southwest, California North, California South, Northwest, Rockies and Basin (5-20 to 5-25). When written: 75,712 rows, 2,912 series, 112 a region.

## Reading the pages

- Pages of 5,000 records sorted by region, series and year; the run stops unless the records read equal the API's count, and if an (entity, variable, ts_utc) comes twice.
- A unit not in the map stops the run. Real dollars are read from the unit's year ("2025 cents/kWh"); nominal ones are marked `nominal`.
- Not taken: the emissions (2,704 rows in million short tons and 676 in short tons; short tons are not in the standard's units).
- A value the API leaves empty has no row; nothing is filled or interpolated.

## License

Public: a work of the U.S. government (record 1 of `license_reads.csv`); cite "U.S. Energy Information Administration, Annual Energy Outlook 2026".

## Cross-checks (sessions 913 and 918)

- The 25 regions summed against the table's U.S. row: every capacity series in every year within 0.1 percent (969 of 969 series-years). Generation and sales sum to a little less than the U.S. row (total generation 4,503 against 4,518 TWh in 2025). Prices are averages and are not summed.
- The U.S. row against `eia_aeo_electricity` (case `cb2026`), by series with the region part set aside: the 28 cumulative additions and retirements series agree in 403 of 403 non-zero series-years. Table 54's "Electric Power Sector : Total Generation" (4,249 TWh in 2025) is not Table 8's series of the same id (4,518), which is total generation with the end-use sectors; named, not mended.
- Session 918, against the code and the table: every row's `x_history` is `PROJECTION`; `x_dollar_year` is filled for the 16,224 price rows and empty for quantities.

## What it does not hold

- The other ten cases, and the emissions.
- The regions' boundaries: EIA's EMM region map is not read; `x_region_name` names them.
