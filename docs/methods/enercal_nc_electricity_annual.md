# New Caledonia's electricity from Enercal's activity report 2024-2025: net production by plant, the public grid's purchases by source, transmission sales (July 2022 to June 2025)

Energy Research Warehouse (ERW), method note written in session 2611 (chain 129) for a table first written on 25 October 2026 (session 2608).

Tables: `enercal_nc_electricity_annual`

## Publisher and address

Enercal, New Caledonia's public generator and transmission operator, Rapport d'activite 2024-2025, its key-figure pages "Chiffres cles 2024-2025 - Enercal Producteur" (page 21) and "Chiffres cles 2024-2025 - Enercal Transport" (page 24): `https://www.enercal.nc/wp-content/uploads/2026/01/Enercal-Rapport-dactivite-2024-2025.pdf`, listed under Nos publications. One GET, no key. Source id `enercal_nc:rapport_activite_2024_2025_chiffres_cles`. Connector: `warehouse/connectors/enercal_nc_electricity.py` (session 2608), whose raw store is `warehouse/raw/enercal_nc/`. www.enercal.nc's robots file names `*` with no rule (read 1209).

ISEE's workbook `production-electricite.xls` (fetched the same session) was updated on 6 August 2019 and ends in 2018, so it was not taken. The energy observatory (observatoire-energie.gouv.nc) answered 503, under maintenance (read 1208).

## Vintage and revision

Written by run `20261025T051911Z` (the write under the lock, offline), which read the report saved at 2026-10-25T05:15:52Z. `vintage` is its last-modified time, 2026-01-19T00:44:42Z. Enercal's years run from July to June, and each report gives three of them.

## Shape and variables

Series, 83 rows, 30 entities. `entity` `enercal:nc:<block>:<item>`, `item` total being the block's TOTAL. The blocks:
- `thermal` and `renewable`: Enercal's net production by plant (Doniambo, Nepoui, Prony, Ducos, the islands' diesel plants; Yate, Neaoua, Thu, the micro hydro plants, Mare);
- `een`: Enercal Energies Nouvelles' renewable plants;
- `public_purchases`: the public distribution's purchases from the producers on the Grande Terre transmission network and the islands' networks, by source (coal, fuel, biogas, hydro, solar, wind);
- `transport_sales`: sales to the transmission network's clients (EEC-Engie, Enercal Distribution, SLN's mine sites).

`variable` is `net_generation`, `purchases` or `sales`; `unit` MWh (the report's GWh times 1,000); `ts_utc` the year's first day, 1 July; `freq` P1Y; `geo` NC; `node` the report's label; `x_period` the report's year ("2024-2025").

The public distribution bought 683.6 GWh in 2022-2023 and 640.6 GWh in 2024-2025. In 2024-2025: coal 72.9, fuel 173.5, hydro 243.1, solar 119.3, wind 29.7 and biogas 2.1. Enercal's own thermal production fell from 910.4 to 351.5 GWh, Doniambo producing in 2022-2023 only.

## Reading the source

- The run stops at once, asking nothing, while `enercal_nc` or www.enercal.nc is paused.
- One request a run; `--offline` reads the saved report.
- **Each page** is found by its title line, once. **Each block** is found by its heading ("PRODUCTION THERMIQUE", the first "PRODUCTION RENOUVELABLE", "operee par Enercal Energies Nouvelles", "DISTRIBUTION PUBLIQUE", "Ventes d'electricite aux clients du reseau de Transport"), with its line of three consecutive years on the heading or the line after it. Its rows run to its TOTAL line: a label and one to three French decimals.
- A row of fewer figures than years holds the last years' (biogas and Gadji Energie print one figure, which their totals place in 2024-2025). A "-" is not written, as the report gives no key.
- **Check:** each block's rows add to its TOTAL within 0.2 GWh a year; the largest gap is 0.1 GWh.
- The run stops, and no file is written, for: a page or heading found other than once, a line of years out of order, a line inside a block that is not a row, no TOTAL, a check missed, or a row given twice.

Nothing is filled. Not taken: the metallurgists' sales outside the public distribution (one line split over several, with shares), network lengths, connections, the distributor's tables, the financial pages.

## License

Internal. Enercal's Mentions legales (read 1211) forbid electronic reproduction of any part of the site, its downloadable documents included, "sauf autorisation expresse du directeur de la publication". Verdict: needs written permission. ISEE's Mentions legales (read 1205) carry the same clause. Held from the live set and from Redivis.

## Cross-check

EIA's world table (`eia_world_electricity_annual`, read past its header lines) gives New Caledonia 3,087 GWh of generation in 2022 and in 2023 and 3,119 GWh in 2024. That includes the nickel smelters' own plants, which Enercal's public figures leave out.
