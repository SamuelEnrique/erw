# The world's energy outlook to 2050 (EIA's International Energy Outlook 2023)

Energy Research Warehouse (ERW), method note written in session 987 (chain 055) for a table first written on 23 October 2026.

Tables: `eia_ieo_projections`

## Publisher and address

U.S. Energy Information Administration (EIA), International Energy Outlook 2023 (the World Energy Projection System), through the EIA API v2 route `ieo/2023` (`https://api.eia.gov/v2/ieo/2023/data/`), tables 1 (world total primary energy consumption by region), 2 (by region and fuel), 10 (energy-related CO2 emissions by region), 20 (net electricity generation by region and fuel) and 21 (installed generating capacity by region and fuel), scenario Reference. Connector: `warehouse/connectors/eia_ieo.py` (session 978). The key comes from `EIA_API_KEY`; the saved pages keep their addresses with the key removed.

## Vintage and revision

The 2023 release (EIA's latest International Energy Outlook in the API; earlier releases 2017, 2019, 2021). Years 2020 to 2050, 2020 to 2022 marked HISTORIC by EIA and the rest PROJECTION. A snapshot (ceiling four requests, 5,000 rows each). A projection is EIA's model result of 2023, not an observation.

## Shape and variables

Series, 17,856 rows (EIA's total for the five tables, checked by the connector). `entity` `eia_ieo2023:<tableId>:<regionId>:<seriesId>` (region `0-0` for the tables by series, `6-n` for the 21 regions of tables 20 and 21); `node` EIA's series name, with the region's name added for the tables by region; `ts_utc` the year's 1 January; `freq` P1Y; `geo` empty; `x_history`, `x_scenario`, `x_table`.

| Variable | Tables | Unit | Series |
|---|---|---|---|
| consumption | 1, 2 | TBtu (EIA's quad Btu times 1,000) | 51 |
| emissions | 10 | tCO2 (EIA's million metric tons, "MMmt", times 1,000,000) | 21 |
| generation | 20 | MWh (EIA's "bill kWh" times 1,000,000) | 231 |
| capacity | 21 | MW (EIA's "gigawatts" times 1,000) | 273 |

A total holds its parts: a sum takes one level.

## Reading the API

- The pages are sorted by every facet (table, region, series, year), so they do not overlap; the rows read must equal EIA's total, or the run stops (session 978's first fetch, sorted without the region, shared six rows between two pages and missed six).
- A unit not in the map, a table or scenario not asked for, or an (entity, year) given twice stops the run; a value EIA leaves empty has no row. Nothing is filled.

## License

Public: a work of the U.S. government (record 1 of `license_reads.csv`).

## Cross-checks (sessions 978 and 987)

- The base years against EIA's statistics: world CO2 within 1.6 percent of `eia_world_energy_co2_annual` (2021: 35,420 and 35,779 million tonnes), world net generation within 2 percent of `eia_world_electricity_annual` (2021: 27,364 and 27,842 TWh).
- Primary energy runs higher in the outlook: the U.S. by 4 percent (2021: 96,784 TBtu, against 93,364 in the international statistics and 93,375 in `eia_primary_energy_monthly`), the world by 9 percent. A difference of accounting is the likely cause (EIA's statistics now count noncombustible renewables by captured energy); not checked further.
- Session 987, against the code: `TABLES`, `UNITS` and the sort are as above; the counts computed from the rows.

## What it does not hold

- The outlook's six other cases (high and low economic growth, oil price and zero-carbon technology cost) and its 54 other tables (GDP, population, transport, sectors, coal trade).
