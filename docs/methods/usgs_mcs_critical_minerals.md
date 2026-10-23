# The minerals of batteries and grids (the USGS's Mineral Commodity Summaries)

Energy Research Warehouse (ERW), method note written in session 960 (chain 054) for a table first written on 23 October 2026.

Tables: `usgs_mcs_critical_minerals`

## Publisher and address

U.S. Geological Survey (USGS), National Minerals Information Center, Mineral Commodity Summaries 2026 Data Release, "Commodity Salient U.S. and World Statistics", ScienceBase item `69837e43b66b01367d7ec7c7` (`https://www.sciencebase.gov/catalog/item/69837e43b66b01367d7ec7c7`), its one CSV, `MCS2026_Commodities_Data.csv` (the data of every chapter of the publication, https://doi.org/10.3133/mcs2026). Connector: `warehouse/connectors/usgs_mcs.py` (session 954). ScienceBase's robots file allows every path to every reader; its content signals reserve AI training (search=yes, ai-train=no, use=reference), which the ERW does not do.

## Vintage and revision

The 2026 edition (data for 2021 to 2025; 2025 is USGS's estimate of early 2026), retrieved 23 October 2026. A snapshot (ceiling one request). A new edition is a new ScienceBase item: the connector's `URL` needs it.

## Shape and variables

Series, 1,600 rows, 653 series, for sixteen chapters: lithium, cobalt, nickel, natural graphite, copper and the rare earths (session 954), and aluminum, gallium, germanium, indium, manganese, the platinum-group metals, the heavy rare earths, silicon, tellurium and vanadium (session 981). `entity` `usgs_mcs:<chapter>:<country>:<the statistic's detail>`, slugs of USGS's words; `geo` US for the United States, empty elsewhere; `x_*` USGS's chapter, section, commodity, country, statistic, detail, unit, notes and whether the commodity is on the 2025 critical minerals list.

| Variable | Rows | What |
|---|---|---|
| production | 465 | U.S. production and each country's mine (and refinery or smelter) production |
| reserves | 98 | each country's reserves, 2025 |
| price | 216 | the chapters' price series (LME cash for cobalt, copper and nickel; battery-grade lithium carbonate; rare earth oxides; the platinum-group metals; aluminum's U.S. market spot; manganese per ton of content and the rest) |
| import, export, consumption, stock, employment, net_import_reliance | 196, 165, 106, 63, 25, 62 | the U.S. salient statistics |
| capacity, shipment, supply | 50, 3, 5 | smelter and refinery capacity, shipments, supply (session 981) |
| import_share | 146 | the import sources, a share of 2021 to 2024 (`ts_utc` 2021-01-01, `freq` P4Y) |

Units: `t` (metric tons; USGS's thousand metric tons times 1,000, kilograms over 1,000), `USD/t`, `USD/kg` (dollars per troy ounce times 32.1507466: a troy ounce is 31.1034768 g), `USD/lb` (cents per pound over 100), `pct`, `count` (Decision 56 of `docs/datastandard.md` added `t` and `USD/kg`). What is weighed (a mineral's content or a gross weight) is in the node.

## Reading the file

- The file is Windows-1252: its em dash in the section "Salient Statistics" and "United States" is written as a colon, its en dashes as hyphens, its curly quotes plainly, all by code point.
- USGS's marks have no row: 80 dashes (zero, as USGS prints it), 54 NA, 51 W (withheld to avoid disclosing company data), 7 s (less than half a unit, or included in the world total), 6 E (net exporter), 1 "Small" and 39 bounds such as ">50"; each counted in the header.
- Manganese's price is "dollars per metric ton unit" by its detail (a metric ton unit is 10 kg of content), though USGS's unit column says per metric ton: written per metric ton of content, times 100 (session 981).
- A figure USGS prints in two sections with the same value (4: U.S. platinum and palladium mine production, 2024 and 2025) is kept once; with two values the run stops.
- A unit or statistic not in the maps, a year not as read, or a key given twice stops the run. Nothing is filled.

## License

U.S. public domain: "USGS-authored or produced data and information are considered to be in the U.S. Public Domain" (read 87 of `license_reads.csv`, session 496). Cite the data release.

## Cross-checks (sessions 954 and 960)

- Copper (LME grade A cash) and nickel (LME cash) against `wb_commodity_prices_monthly`'s annual averages: within 0.2 percent for 2021 to 2024 (copper 2024: 9,143 and 9,142 USD/t). Cobalt (LME cash) against `imf_commodity_prices`: within 1 percent for 2021 to 2024. USGS's 2025 figures, estimates, differ by 1 to 5 percent.
- The IMF's lithium series is on another basis (six to ten times USGS's battery-grade carbonate) and is not compared.
- Session 960, against the code: `CHAPTERS`, `UNITS` and `VARIABLES` give the six chapters, the units and the variables above; the counts computed from the rows.

## What it does not hold

- The other 73 chapters (iron ore, steel, zinc, lead, salt, soda ash and the rest).
- The data release's "Mineral Industry Trends and Salient Statistics" item.

## Session 981's additions (checked by session 987)

Aluminum's U.S. market spot price runs 15 to 23 percent above the World Bank's LME price (`wb_commodity_prices_monthly`) through 2024, the U.S. Midwest premium, and 51 percent in 2025; a different price, not compared further. The counts above computed from the rows.
