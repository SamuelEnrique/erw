# The Faroe Islands' electricity production by source and sales by consumer group, a year (Statistics Faroe Islands, UO03020 and UO03030)

Energy Research Warehouse (ERW), method note written in session 2499 (chain 121) for a table first written on 24 October 2026 (session 2502).

Tables: `hagstova_faroe_electricity_annual`

## Publisher and address

Statistics Faroe Islands (Hagstova Føroya), from SEV's figures (the islands' public power company), two tables of its statbank, read through the PxWeb API, one JSON-stat 2.0 query a table by POST:

- `https://statbank.hagstova.fo/api/v1/en/H2/UO/UO03/ork_elgerd.px`: "UO03020 Electricity production of SEV by hydro, wind and thermal in MWh (1990-2025)";
- `https://statbank.hagstova.fo/api/v1/en/H2/UO/UO03/ork_elsola.px`: "UO03030 Electricity sales of SEV in MWh (1997-2025)".

No key. Source id `hagstova:UO03`. Connector: `warehouse/connectors/hagstova_faroe_electricity.py` (session 2502). statbank.hagstova.fo answers HTTP 404 for a robots file (read 858); hagstova.fo's closes system paths only (read 857).

The session first chose IT.NRW's electricity fed in by source for North Rhine-Westphalia; ckan.open.nrw reset the connection at its robots file (read 856), and the Faroe Islands replaced it.

## Vintage and revision

Production 1990 to 2025 and sales 1997 to 2025, written by run `20261024T163010Z` (the write under the lock, offline), which read the answers saved at 2026-10-24T15:23:19Z (UO03020) and 15:23:23Z (UO03030). The statbank's table list gives both tables as updated on 3 June 2026; the answers' own `updated` field reads 2000-01-01, a placeholder, so `vintage` is left empty.

## Shape and variables

Series, 421 rows, 16 entities. `unit` MWh as given; `ts_utc` the year's 1 January; `freq` P1Y; `geo` FO; `node` the category as Statistics Faroe Islands names it; `x_table` the table's code.

- `generation` (UO03020): `hagstova:fo:<source>`: total, thermal, hydro (from 1990), wind (from 1993), solar (from 2019), biogas and tidal (from 2020).
- `sales` (UO03030): `hagstova:fo:<group>`: total_sales, fisheries_aquaculture ("Agric., fish. ind., aquac., ressource comp."), production_construction, shops_hotels, transport_communication, finance_business_services, public_private_services, street_lights, households ("Houses, apts, summer and boat houses").

| GWh | 1990 | 2010 | 2020 | 2025 |
|---|---|---|---|---|
| Produced | 211.0 | 280.4 | 406.8 | 506.2 |
| Of which wind | | 13.6 | 47.1 | 147.5 |
| Sold | | 255.0 | 370.7 | 460.1 |
| Sold to fisheries and aquaculture | | 25.9 | 83.9 | 133.8 |

## Reading the source

- The run stops at once, asking nothing, while `hagstova_faroe_energy` or statbank.hagstova.fo is paused.
- Two requests a run (timeout 120 seconds); `--offline` reads the saved answers (`warehouse/raw/hagstova_faroe_energy/query_<table>.json`).
- **The query selects every category and every year** (`"filter": "all", "values": ["*"]`). An empty query returns only the total: the category dimension is eliminated (session 2502's first try).
- **Cells without a row:** a cell without a number (the sources before their first year, the groups before 1997).
- The run stops, and no file is written, for: a table without its year and category dimensions, a category not in the map, a year not of four digits, a value array not the size of the dimensions, a key given twice.

Nothing is filled.

## License

Public. Statistics Faroe Islands' terms of use (read 866): "Statistical data, tables, texts, charts and infographics from Statistics Faroe Islands are available under Creative Commons Attribution 4.0 International (CC BY 4.0), unless otherwise stated." The terms cover the statbank and its API, for any purpose, commercial included, with Statistics Faroe Islands credited as the source. Verdict (session 2502): may be public, sold or not. The header carries the credit. Held from the live set; in the next Stanford draft.

## Cross-checks (session 2502)

- The sources sum to the total each year (2025: 102,421 + 250,245 + 147,523 + 184 + 5,865 + 11 = 506,249 MWh).
- Production over `owid_ember_electricity_annual`'s demand for the Faroe Islands: 0.96 to 1.04 (2000 to 2021), 0.904 in 2022 and 0.934 in 2023.

## What it does not hold

- Monthly figures; generation outside SEV; prices (DKK).
