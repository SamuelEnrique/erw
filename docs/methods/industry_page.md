# Energy use by industry (`site/data/industry.json`, `eia_seds_industrial_annual`, `eia_aeo_industrial`)

Session 8003, chain 501 step D2, 19 November 2026. Builder: `warehouse/derived/industry_page.py`. Two new tables: `eia_seds_industrial_annual` (`warehouse/connectors/eia_seds_industrial.py`) and `eia_aeo_industrial` (`warehouse/connectors/eia_aeo_industrial.py`). The page file's shape: `docs/state/page_files_regions.md`, section 9. The second window (chain 502) builds the page.

## What the file holds, and from where

| Part of the file | Source | Span | Unit |
|---|---|---|---|
| `monthly` | `eia_sector_energy_consumption_monthly`: EIA's Monthly Energy Review, the industrial sector's consumption by source (Table 2.4 series TEICBUS, TNICBUS, CLICBUS, NNICBUS, PAICBUS, REICBUS, ESICBUS, LOICBUS) | January 1973 to the newest month EIA prints | TBtu |
| `industries` | `eia_mecs_manufacturing`: the 2022 Manufacturing Energy Consumption Survey, fuel by industry (NAICS) and census region (Table 3.2), and the components of each industry's electricity (Tables 11.1 and 11.3) | 2022 | TBtu; MWh |
| `states_annual` | `eia_seds_industrial_annual` and `eia_seds_state_energy` (NGICB, ESICB): the State Energy Data System, each state's industrial consumption by source, expenditures and average price | 1990 to 2024 | TBtu; USD; USD/MMBtu |
| `electricity_sales_monthly` | `eia_retail_sales_monthly`: Form EIA-861M, electricity sold to industrial customers by state | January 2001 to the newest month | MWh |
| `outlook` | `eia_aeo_industrial`: the Annual Energy Outlook 2026, the industrial sub-sector tables (24 to 34), energy use by fuel, every case | the AEO's years | TBtu |

Every figure is as its publisher printed it: nothing is summed across sources, filled or scaled, except the unit changes the tables' headers state (billion Btu as TBtu, million dollars as USD). A cell EIA withholds has no figure. The industries are ranked by their 2022 total fuel consumption in the United States, at the three-digit NAICS level, where MECS prints a total.

## The two new tables

- **`eia_seds_industrial_annual`**: seventeen SEDS series of the industrial sector by state and year, from EIA's API v2 (route `seds`), 1990 to 2024, 30,940 rows on 19 November 2026 (7 requests): total and end-use consumption; coal, petroleum, hydrocarbon gas liquids, distillate and residual fuel oil, petroleum coke, renewables, wood and waste, and the sector's share of electrical system losses; expenditures in total and for coal, petroleum, natural gas and electricity; the total average price. It does not repeat `eia_seds_state_energy`'s industrial natural gas and electricity (NGICB, ESICB) and their prices, which the page file reads from there.
- **`eia_aeo_industrial`**: the AEO2026's industrial sub-sector tables (refining, food, paper, bulk chemicals, glass, cement and lime, iron and steel, aluminum, metal-based durables, other manufacturing, nonmanufacturing), the series in trillion Btu (energy use by fuel) in each of the eleven cases EIA publishes, 75,504 rows (42 requests). These are EIA's projections, not observations. EIA gives one series id to two series in places (Bulk Chemical's total energy use and its hydrogen total), so the entity carries six hex digits of the sha1 of the series' name beside the id. The tables' other series (combined heat and power capacity and generation, energy per dollar of shipments, shipments, carbon dioxide) are not taken; the header counts them.

Both are public (EIA, a work of the U.S. government; record 1 of `warehouse/metadata/license_reads.csv`).

## What the file does not say

It ranks industries and states by what EIA printed. It does not explain a change, compare an industry's energy with its output, or add an industry's figures across the surveys, which measure different things (MECS counts manufacturing's fuel by plant; SEDS and the Monthly Energy Review count the whole industrial sector, agriculture, mining and construction included).

## Build

    python warehouse/lock.py run --task seds -- <python> warehouse/connectors/eia_seds_industrial.py
    python warehouse/lock.py run --task aeo -- <python> warehouse/connectors/eia_aeo_industrial.py
    python warehouse/derived/industry_page.py

The data machine's daily run calls the last after the Monthly Energy Review and EIA-861M tables refresh.
