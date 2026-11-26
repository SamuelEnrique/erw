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

## The page (session 8012, chain 505)

The page "Energy use by industry" (`/industry`, in review, in no menu) draws this file and nothing else: `site/app/industry/page.tsx`, its arithmetic in `site/lib/industry.ts`. What it shows:

- **The industrial sector, month by month**: the Monthly Energy Review's eight series (Table 2.4) from a chosen year (from 2015 by default), and the newest month beside the same month a year before with the change in percent. A year's figure is the sum of its twelve months, written only when all twelve are held.
- **Manufacturing industries ranked**: the 21 three-digit industries of the 2022 survey by total fuel consumption in a chosen Census region, largest first, with each fuel and the industry's share of the 21 industries' sum (not held in a region where EIA withholds a total). A cell EIA withholds is "not held" with EIA's reason on hover, never zero.
- **Two industries side by side**: any of the survey's 81 industries, their fuels and the components of their electricity (Tables 11.1 and 11.3). Table 3.2's "Net electricity" is not an industry's electricity use: it equals purchases plus transfers in plus onsite generation from renewables other than wood and other biomass, less sales and transfers offsite, at 3,412 Btu a kWh (within 1 TBtu in all 52 industries with every part held, session 10224); electricity made onsite from fuel (cogeneration, 146,163,000 MWh in 2022) is counted in that fuel. Paper's net electricity is 51.6 percent of its net demand, Chemicals' 71.4 percent. The State Energy Data System's and Form EIA-861M's electricity is electricity sold to industrial customers, without what plants make for themselves (in the South 22.1 percent of manufacturing's net demand in 2022). The hovers say so.
- **States, year by year**: every state and the District of Columbia by a chosen source in a chosen year, with the total, the average price and the expenditures (nominal dollars); two states side by side, by year, with the change of the total since 2019 and electricity sold to industry by month (Form EIA-861M).
- **EIA's outlook**: any series of any of the eleven industries of the Annual Energy Outlook 2026, two cases drawn, every case in the table. They are EIA's projections, not the ERW's.

Every figure carries its source on hover. The page computes only a year's twelve months summed, the shares and the percent changes it names.

### Replication and cross-check

`replication/industry/replicate.py` reads the page as served (the internal view) and computes every marked figure again from this file, from this note and not from the page's code: 535 figures on the page as it opens and 586 on a second set of choices, all reproduced on 19 November 2026. It writes `figures.csv` and `crosscheck.csv`. The cross-checks set one EIA publication beside another: the Monthly Energy Review's twelve months against the State Energy Data System's industrial total for the United States (2024: 31,395.0 against 31,356.6 TBtu, 0.12 percent apart; 2023: 0.08 percent), and Form EIA-861M's electricity sold to industry at 3,412 Btu per kWh against the State Energy Data System's industrial electricity (equal to the thousandth in 2023 and 2024: the State Energy Data System takes its retail sales from EIA's Form 861, so the two are not independent, and the check shows only that the file joins them without loss).

### Decisions (session 8012)

| Key | Choice | Default |
|---|---|---|
| `as-published` | Every figure is EIA's own; the page sums only a year's twelve months and computes only the shares and changes it names | EIA's figures as published |
| `withheld` | A cell EIA withholds is "not held" with EIA's reason on hover, never zero | "not held" with the reason |
| `whole-year` | A year's figure from a monthly series is written only when all twelve months are held | twelve months or no figure |
| `first-two` | Industries A and B open on the two largest three-digit industries; states A and B on the two largest by total in the newest year | Chemicals and Petroleum and Coal Products; Texas and Louisiana in 2024 |
| `ranking` | Industries by total in the chosen region, states by the chosen source and year, largest first; one with no figure stands last | largest first |
| `cases` | The outlook opens on the Counterfactual Baseline case and the High Electricity Demand case; every case is in the table | AEO2026 names no Reference case |
| `from-2015` | The monthly chart opens on the months from 2015; the file holds them from January 1973 | from 2015 |
| `nominal` | Prices and expenditures in nominal dollars, as the State Energy Data System gives them | nominal dollars |
