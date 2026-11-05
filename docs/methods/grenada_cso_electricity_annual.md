# Grenada's electricity produced and consumed by category, a year (CSO Grenada)

Energy Research Warehouse (ERW), method note written in session 2499 (chain 121) for a table first written on 24 October 2026 (session 2496).

Tables: `grenada_cso_electricity_annual`

## Publisher and address

The Central Statistical Office of Grenada (CSO), its table "Production and Consumption of Electricity by Category, 2000 to 2023": `https://stats.gov.gd/subjects/energy/production-and-consumption-of-electricity-by-category-2000-to-2023/`. One GET of the web page, no key; the figures are in its HTML table. Source id `grenada_cso:electricity_by_category`. Connector: `warehouse/connectors/grenada_cso_electricity.py` (session 2496). stats.gov.gd's robots file disallows nothing (read 839). The table's source line reads "Central Statistical Office"; the island's one utility is GRENLEC.

## Vintage and revision

2000 to 2023, written by run `20261024T162952Z` (the write under the lock, offline), which read the page saved at 2026-10-24T15:13:07Z. The page gives no date of update.

## Shape and variables

Series, 144 rows, 5 entities. `unit` MWh (the CSO's thousands of kWh, the same quantity); `ts_utc` the year's 1 January; `freq` P1Y; `geo` GD; `node` and `x_label` the CSO's row label.

- `grenada_cso:gd:total`, `generation`: "Electricity Production Volume (thousands of KWH)".
- `grenada_cso:gd:<category>` (domestic, commercial, industrial, street_lights, total), `consumption`: "Electricity Consumption, Volume (thousands of KWH)".

| GWh | 2000 | 2010 | 2019 | 2020 | 2023 |
|---|---|---|---|---|---|
| Produced | 133.5 | 208.7 | 239.1 | 219.9 | 261.2 |
| Consumed | 113.3 | 184.8 | 217.0 | 199.7 | 237.4 |

## Reading the source

- The run stops at once, asking nothing, while `grenada_cso_electricity` or stats.gov.gd is paused.
- One request a run (timeout 120 seconds); `--offline` reads the saved page.
- **The table:** the page's first HTML table, row by row: a header of the 24 years, the production row, the section "Electricity Consumption, Volume" with a row a category and its total, then the section "Value (EC$ thousands)", not taken.
- **Figures:** with or without thousands separators and with one to three decimals (2021 to 2023's consumption is printed "86011.856"); each is read as the number it prints.
- The consumption total is written as printed; its largest gap from its categories' sum is 0.2 MWh, in the header.
- **Cells without a row:** an empty cell (none).
- The run stops, and no file is written, for: no table, a header other than the years 2000 to 2023, a row of another width, a row not in the map, a key given twice.

Nothing is filled.

## License

Internal, not settled. The site's terms (read 841): "The materials located on this website, including the information ... are protected by copyright"; "Access and use of the Data is subject to the requirements set forth under the Open Licence Agreement". The agreement's link points at statsgrd.com, a name that does not resolve (read 843), and its page on stats.gov.gd has a title and no text (read 845). No verdict is written. Saint Lucia's CSO, whose site is built on the same frame (session 2497), grants a worldwide royalty-free licence in its Open Licence Agreement; Grenada's may say the same, but it was not there to read. Held from the Redivis storage and the live set.

## Cross-checks (session 2496)

- Production over `owid_ember_electricity_annual`'s demand for Grenada: 0.96 to 1.05 (2000 to 2022), 1.09 in 2023.
- The page "Production and Consumption of Electricity, 2000 to 2023" (read 840) gives the same production and total consumption.

## What it does not hold

- Generation by source; monthly figures; the consumption's value (EC$).
