# Czech regions' electricity capacity, production and consumption, 2024 (the CZSO's Comparison of Regions)

Energy Research Warehouse (ERW), method note written in session 2815 (chain 143) for a table first written on 26 October 2026 (session 2809).

Tables: `czso_cz_regional_electricity_annual`

## Publisher and address

The Czech Statistical Office (CZSO, ČSÚ), "Comparison of Regions in the Czech Republic 2025", published 22 January 2026 (`https://csu.gov.cz/produkty/comparison-of-regions-in-the-czech-republic-2025`). Its tables come in one zip, `https://csu.gov.cz/docs/107508/4491dd21-67d2-55cf-a3e6-926ec9c4b345/33020525.zip?version=1.1`. Chapter 14 (Energy) holds:
- table 14.101: installed capacity and gross production by type of plant and region (`14_energetika/2514101.xlsx`);
- table 14.103: net consumption by economic activity and region (`14_energetika/2514103.xlsx`).

**The figures are the Energy Regulatory Office's (ERÚ),** as the CZSO publishes them.

Source id `czso:comparison_of_regions_14_energy`. Connector: `warehouse/connectors/czso_regional_electricity.py` (session 2809), whose raw store is `warehouse/raw/czso_regions/`. csu.gov.cz's robots file (read 1613) disallows Baidu's agents and three paths to every reader, and names no Claude agent. www.czso.cz redirects to it (read 1614).

## Vintage and revision

Written by run `20261026T050613Z`, which read the zip retrieved at 2026-10-26T05:01:44Z (last modified 12 February 2026). The table holds one year, 2024. Each edition holds one year in a zip of its own (the 2023 edition's 2022 was read, 1615), so earlier years would need their editions' zips, one request each.

## Shape and variables

Series, 360 rows, 15 areas (the 14 regions, by their ISO 3166-2 codes CZ-10 to CZ-80, and Czechia, CZ), 2024:
- `entity` `czso_regions:<area>:<item>`.
  - For capacity and production the items are: total, steam, combined_cycle, hydro (pumped storage included), gas_combustion, nuclear, wind, solar.
  - For consumption: total, industry, energy, transport, construction, agriculture_forestry, households, trade_services.
- `variable`:
  - `installed_capacity` (MW, at 31 December);
  - `gross_production` (MWh, the table's GWh times 1,000);
  - `net_consumption` (MWh).
- `ts_utc` the year's 1 January; `freq` P1Y; `geo` CZ.
- `node` "CZSO <area code>, <the table's English label>", in ASCII, since this machine's console cannot print every Czech letter; `x_region`, `x_table` and `x_label` the tables' own, in Czech.

**Figures, 2024:**
- Czechia's installed capacity 22,980.7 MW, gross production 73,881,775 MWh, net consumption 55,923,956 MWh.
- The Ústí nad Labem region (CZ-42) produced 20,104,250 MWh and holds 5,417.6 MW.
- Central Bohemia (CZ-20) used the most: 8,145,224 MWh.

## Reading the source

- **The regions make Czechia** in every row, and the plant types make each region's capacity and production. All 54 such comparisons hold within 0.5 MW or 0.5 GWh.
- **The seven activities fall short of net consumption in all 15 areas,** by 261.6 GWh for Czechia (0.5 per cent). This is kept as published, counted, with no "other" row made.
- The tables' shares (per cent) and households' consumption per inhabitant (kWh) are not written: they are computed from the rows written.
- "- " (nothing) is zero; nothing is filled.
- The run stops, asking nothing, while the CZSO is paused. It also stops on:
  - a member not in the zip;
  - a title without its year;
  - a header without the 14 regions and Czechia;
  - a row not in the structure;
  - a value not a number.

## License

CC BY 4.0, the CZSO's conditions for use (read 1617, session 2809's verdict): "Statistical information released by the Czech Statistical Office through the website https://csu.gov.cz is licensed under CC BY 4.0". The terms are to be mentioned, and adjusted or derived data labelled as such; the header says the table is reshaped, not unaltered official statistics. In the release package; held from the live set.

## Cross-check

Czechia 2024 against Eurostat's tables:

| Measure | Here | Eurostat | Table |
|---|---|---|---|
| Gross production, MWh | 73,881,775 | 73,900,393 | `eurostat_electricity_production_annual` (TOTAL) |
| Nuclear production, MWh | 29,696,397 | 29,696,397 | the same (N900H) |
| Wind production, MWh | 716,810 | 716,810 | the same (RA300) |
| Installed capacity, MW | 22,980.7 | 23,022.1 | `eurostat_electricity_capacity_annual` (TOTAL) |
| Nuclear capacity, MW | 4,290 | 4,290 | the same (N9000) |
| Households' consumption, MWh | 15,637,233 | 15,634,581 | `eurostat_electricity_consumption_annual` |
