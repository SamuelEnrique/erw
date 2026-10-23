# The minerals of batteries and grids (the USGS's Mineral Commodity Summaries)

Energy Research Warehouse (ERW), method note written in session 960 (chain 054) for a table first written on 23 October 2026.

Tables: `usgs_mcs_critical_minerals`

## Publisher and address

U.S. Geological Survey (USGS), National Minerals Information Center, Mineral Commodity Summaries 2026 Data Release, "Commodity Salient U.S. and World Statistics", ScienceBase item `69837e43b66b01367d7ec7c7` (`https://www.sciencebase.gov/catalog/item/69837e43b66b01367d7ec7c7`), its one CSV, `MCS2026_Commodities_Data.csv` (the data of every chapter of the publication, https://doi.org/10.3133/mcs2026). Connector: `warehouse/connectors/usgs_mcs.py` (session 954). ScienceBase's robots file allows every path to every reader; its content signals reserve AI training (search=yes, ai-train=no, use=reference), which the ERW does not do.

## Vintage and revision

The 2026 edition (data for 2021 to 2025; 2025 is USGS's estimate of early 2026), retrieved 23 October 2026. A snapshot (ceiling one request). A new edition is a new ScienceBase item: the connector's `URL` needs it.

## Shape and variables

Series, 692 rows, 299 series, for six chapters: lithium, cobalt, nickel, natural graphite, copper, rare earths. `entity` `usgs_mcs:<chapter>:<country>:<the statistic's detail>`, slugs of USGS's words; `geo` US for the United States, empty elsewhere; `x_*` USGS's chapter, section, commodity, country, statistic, detail, unit, notes and whether the commodity is on the 2025 critical minerals list.

| Variable | Rows | What |
|---|---|---|
| production | 251 | U.S. production and each country's mine (and copper's refinery) production |
| reserves | 78 | each country's reserves, 2025 |
| price | 100 | the chapters' price series (LME cash for cobalt, copper and nickel; battery-grade lithium carbonate; rare earth oxides; graphite import unit values) |
| import, export, consumption, stock, employment, net_import_reliance | 52, 55, 50, 25, 15, 22 | the U.S. salient statistics |
| import_share | 44 | the import sources, a share of 2021 to 2024 (`ts_utc` 2021-01-01, `freq` P4Y) |

Units: `t` (metric tons; USGS's thousand metric tons times 1,000), `USD/t`, `USD/kg`, `USD/lb` (cents per pound over 100), `pct`, `count` (Decision 56 of `docs/datastandard.md` added `t` and `USD/kg`). What is weighed (a mineral's content or a gross weight) is in the node.

## Reading the file

- The file is Windows-1252: its em dash in the section "Salient Statistics" and "United States" is written as a colon, its en dashes as hyphens, its curly quotes plainly, all by code point.
- USGS's marks have no row: 26 dashes (zero, as USGS prints it), 17 W (withheld to avoid disclosing company data), 7 s (less than half a unit, or included in the world total), 6 NA, 5 E (net exporter) and 15 bounds such as ">50"; each counted in the header.
- A unit or statistic not in the maps, a year not as read, or a key given twice stops the run. Nothing is filled.

## License

U.S. public domain: "USGS-authored or produced data and information are considered to be in the U.S. Public Domain" (read 87 of `license_reads.csv`, session 496). Cite the data release.

## Cross-checks (sessions 954 and 960)

- Copper (LME grade A cash) and nickel (LME cash) against `wb_commodity_prices_monthly`'s annual averages: within 0.2 percent for 2021 to 2024 (copper 2024: 9,143 and 9,142 USD/t). Cobalt (LME cash) against `imf_commodity_prices`: within 1 percent for 2021 to 2024. USGS's 2025 figures, estimates, differ by 1 to 5 percent.
- The IMF's lithium series is on another basis (six to ten times USGS's battery-grade carbonate) and is not compared.
- Session 960, against the code: `CHAPTERS`, `UNITS` and `VARIABLES` give the six chapters, the units and the variables above; the counts computed from the rows.

## What it does not hold

- The other 83 chapters (manganese, vanadium, the heavy rare earths, aluminum, silicon and the rest).
- The data release's "Mineral Industry Trends and Salient Statistics" item.
