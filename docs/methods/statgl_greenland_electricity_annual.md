# Greenland's renewable electricity and Nukissiorfiit's sales, a year (Statistics Greenland, ENX3VVE and ENX4NUK)

Energy Research Warehouse (ERW), method note written in session 2513 (chain 122) for a table first written on 24 October 2026 (session 2510).

Tables: `statgl_greenland_electricity_annual`

## Publisher and address

Statistics Greenland (Grønlands Statistik), two tables of its Statbank, read through the PxWeb API, one JSON-stat 2.0 query a table by POST, every value of every dimension selected:

- `https://bank.stat.gl/api/v1/en/Greenland/EN/EN20/ENX3VVE.px`: "Production and consumption of renewable energy etc. use by source, type and time";
- `https://bank.stat.gl/api/v1/en/Greenland/EN/EN20/ENX4NUK.px`: "Electricity, water and heat sold by Nukissiorfiit by location, product and time".

No key. Source id `statgl:ENX3VVE_ENX4NUK`. Connector: `warehouse/connectors/statgl_greenland_electricity.py` (session 2510). stat.gl and bank.stat.gl have no robots file (reads 908, 909). stat.gl's llms.txt (read 917) asks agents to use the Statbank API and to cite the Statbank with a link to the table.

## Vintage and revision

ENX3VVE 1996 to 2024 and ENX4NUK 2004 to 2024, written by run `20261024T182205Z` (the write under the lock, offline), which read the answers saved at 2026-10-24T17:51:39Z and 2026-10-24T17:51:42Z. `vintage` is the answers' `updated` field, 2025-12-18T13:00:00Z.

## Shape and variables

Series, 2,064 rows, 33 entities. `unit` MWh; `ts_utc` the year's first day; `freq` P1Y; `geo` GL; `node` the categories as Statistics Greenland labels them; `x_table` the table.

- ENX3VVE: `renewable_production` and `renewable_consumption`, `statgl:gl:<source>` (total, hydropower, waste), in MWh as given (the TJ unit not taken).
- ENX4NUK: `sales_normal_rates`, `sales_fishing_industry_rates`, `sales_electric_heating`, `statgl:gl:<location>`: `total_sales`, `towns`, `settlements`, the five municipalities, their towns (`nuuk_town` and others) and their settlements (`settlements_in_<municipality>`); kWh divided by 1,000. District heating and water not taken. A location's sums (towns plus settlements, a municipality's towns and settlements) hold as Statistics Greenland gives them; a sum over entities must take one level.

| GWh | 2004 | 2015 | 2024 |
|---|---|---|---|
| Hydropower produced | 196 | 423 | 487 |
| Sold at normal rates | 153 | 193 | 229 |

## Reading the source

- The run stops at once, asking nothing, while `statgl_energy` or bank.stat.gl is paused.
- Two requests a run; `--offline` reads the saved answers (`warehouse/raw/statgl_energy/query_<table>.json`).
- **The query selects every value** (`"filter": "all", "values": ["*"]`) of each dimension, as session 2502 learned that an empty query may eliminate one.
- **A location's slug:** its label folded to ASCII, "- here of in towns" to `towns`, "- Nuuk town" to `nuuk_town`.
- **Cells without a row:** a cell without a number (the locations before their first year).
- The run stops, and no file is written, for: dimensions other than the expected, a value array not the size of the dimensions, a year not of four digits, a key given twice.

Nothing is filled. Five values are below zero, as printed: four towns' or settlements' electric heating sales in 2007 and 2017 (-0.005 to -0.806 MWh) and Ittoqqortoormiit's fishing-industry sales in 2007 (-45.9 MWh); the table gives no note on them.

## License

Internal, not settled. No page of terms for the Statbank's statistics was found (session 2510). The "CC-BY-4.0" in Statistics Greenland's agent profile (read 918) licenses that profile. Held from the Redivis storage and the live set.

## Cross-checks (session 2510)

- Hydropower production over `owid_ember_electricity_annual`'s demand for Greenland: 0.56 (1996) rising to 0.81 (2024); diesel supplies the rest.

## What it does not hold

- Diesel and other thermal generation; monthly figures; prices (DKK).
