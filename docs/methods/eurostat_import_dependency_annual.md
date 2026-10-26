# European energy import dependency by product, 1990 to 2024 (Eurostat's nrg_ind_id)

Energy Research Warehouse (ERW), method note written in session 2787 (chain 141) for a table first written on 26 October 2026 (session 2790).

Tables: `eurostat_import_dependency_annual`

## Publisher and address

Eurostat (the Statistical Office of the European Union), "Energy imports dependency" (nrg_ind_id, `https://ec.europa.eu/eurostat/databrowser/view/nrg_ind_id/default/table`). The table reads two files from Eurostat's SDMX 2.1 dissemination API, with no key:
- the whole dataset, every key: `https://ec.europa.eu/eurostat/api/dissemination/sdmx/2.1/data/nrg_ind_id/A...?format=SDMX-CSV&compressed=false`;
- the SIEC codelist, for the products' names.

Source id `eurostat:nrg_ind_id`. Connector: `warehouse/connectors/eurostat_import_dependency.py` (session 2790), whose raw store is `warehouse/raw/eurostat_import_dependency/`. ec.europa.eu's robots file leaves `/eurostat/api/dissemination/` open and names no Claude agent (read 1587).

## Vintage and revision

Written by run `20261026T020614Z` (the write under the lock, offline), which read the file retrieved at 2026-10-26T02:04:16Z; Eurostat's last update, as the file gives it (no time zone), 16/07/26 23:00:00. Eurostat revises the energy balances, and so this indicator, each year.

## Shape and variables

Series, 16,627 rows, 39 areas, 13 products, 1990 to 2024:
- `entity` `eurostat_import_dependency:<geo>:<SIEC>`. The products are the total; solid fossil fuels with anthracite, coking coal, other bituminous coal, sub-bituminous coal and lignite; natural gas; oil and petroleum products (excluding biofuels) with crude oil and natural gas liquids; peat; and oil shale and oil sands.
- `variable` `import_dependency`; `unit` pct (net imports divided by gross available energy, times 100).
- `ts_utc` the year's 1 January; `freq` P1Y; `geo` ISO alpha-2 (Eurostat's EL is GR), blank for EU27_2020; `node` "<geo> import dependency, <the SIEC name>"; `x_geo_code`, `x_siec`, `x_flag` and `x_conf_status` Eurostat's codes and flags.

**A negative value is a net exporter; above 100, a country imports more than it uses** (stocks built, or bunkers). **Figures:** the EU27's total dependency was 50.02 per cent in 1990, 55.74 in 2010 and 57.29 in 2024.

Countries kept: as `eurostat_electricity_production_annual` keeps them; the United Kingdom and Kosovo are left out.

## Reading the source

- The run stops at once, asking nothing, while Eurostat is paused.
- **251 values lie outside -100 to 200** (from -31,930 to 3,601) where a product's gross available energy is near zero. They are kept as Eurostat publishes them and counted in the header. 6,959 zeros are kept; there are no blanks.
- A header not Eurostat's; a unit other than PC, a frequency other than A, or a product not in the SIEC codelist; a value not a number; or a key given twice stops the run. Nothing is filled.

## License

Public with acknowledgement: Eurostat's copyright notice, the verdict on record (read 280, session 2123). Cite: Eurostat, nrg_ind_id. In the release package; held from the live set.

## Cross-check

Natural gas (G3000) against `eurostat_gas_balance_monthly` (net imports over observed inland consumption, twelve months summed), per cent:

| Country | Year | Monthly balance | nrg_ind_id (here) |
|---|---|---|---|
| Germany | 2019 | 99.6 | 100.1 |
| Germany | 2023 | 93.8 | 93.7 |
| Italy | 2023 | 95.8 | 96.3 |
| Spain | 2023 | 98.8 | 98.5 |
| France | 2023 | 97.8 | 99.5 |

The monthly balance's observed consumption stands for the annual gross available energy, so the two differ by a point or two at most.
