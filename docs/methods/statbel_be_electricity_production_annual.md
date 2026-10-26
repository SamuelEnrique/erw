# Belgium's gross electricity production by energy product, 2018 to 2025 (Statbel)

Energy Research Warehouse (ERW), method note written in session 2773 (chain 140) for a table first written on 26 October 2026 (session 2770).

Tables: `statbel_be_electricity_production_annual`

## Publisher and address

Statistics Belgium (Statbel), the beSTAT view "Evolution Gross electricity production 2025", linked from its electricity production page (`https://statbel.fgov.be/en/themes/energy/electricity-production`). The table reads beSTAT's CSV export of the view, `https://bestat.statbel.fgov.be/bestat/api/views/cd9605c7-3f71-4527-9404-40bfb81c8523/result/CSV`. No key. Source id `statbel:bestat_gross_electricity_production`. Connector: `warehouse/connectors/statbel_electricity_production.py` (session 2770), whose raw store is `warehouse/raw/statbel/`. statbel.fgov.be's robots file closes Drupal's core, admin, search and user paths and names no Claude agent (read 1552). bestat.statbel.fgov.be has no robots file: its root address refreshes to `/bestat/robots.txt`, which answers 404 (reads 1556 and 1557).

## Vintage and revision

Written by run `20261026T000615Z` (the write under the lock, offline), which read the export retrieved at 2026-10-26T00:03:53Z. The view's name carries its latest year, 2025; a later view may replace this one, and the connector's address would change with it.

## Shape and variables

Series, 200 rows, 25 entities, each year from 2018 to 2025:
- `entity`: `statbel_gep:be:total`, or `statbel_gep:be:<product group>:<product>`: 24 products in 8 groups (nuclear, solid fossil fuels, manufactured gases, natural gas, oil and petroleum products, non-renewable waste, renewables and biofuels, other sources). Pumped hydro is a product of the other sources.
- `variable` `gross_electricity_production`; `unit` MWh (Statbel's GWh times 1,000); `ts_utc` the year's first day; `freq` P1Y; `geo` BE; `node` the two product levels as Statbel writes them.

**Figures:** the total was 75,039.9 GWh in 2018, 100,481.8 in 2021 and 73,054.1 in 2025. **The table runs one year past Eurostat's,** with 2025 in it.

## Reading the source

- The run stops at once, asking nothing, while `statbel` or its beSTAT host is paused.
- One request a run, saved and reused unless `--fresh`; `--offline` asks nothing.
- **Check,** within 0.5 GWh in every year: the products add to the total. It holds every year.
- A header not the view's, an indicator other than gross electricity production, a year missing for a product, a product given twice or a value not a number stops the run. Nothing is filled.

## License

Public. Statbel's terms (`https://statbel.fgov.be/en/cc-40`, read 1559): CC BY 4.0, sharing and adapting for any use, commercial included, crediting "Source: Statbel", linking the licence and stating changes, as the header does. The verdict, may be public, was given in session 2770. In the release package; held from the live set.

## Cross-check

Against `eurostat_electricity_production_annual` (Belgium), GWh: equal in every year from 2018 to 2024 that was compared.

| Year | Total (here) | Eurostat TOTAL | Nuclear (here) | Eurostat N900H | Wind (here) | Eurostat RA300 |
|---|---|---|---|---|---|---|
| 2018 | 75,039.9 | 75,039.9 | 28,597.0 | 28,597.0 | 7,574.1 | 7,574.1 |
| 2022 | 95,950.3 | 95,950.3 | 43,879.1 | 43,879.1 | 12,352.6 | 12,352.6 |
| 2024 | 77,156.8 | 77,156.8 | 31,254.6 | 31,254.6 | 13,824.5 | 13,824.5 |
