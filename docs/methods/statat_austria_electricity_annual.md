# Austria's electricity balance, 1970 to 2024 (Statistics Austria's energy balances)

Energy Research Warehouse (ERW), method note written in session 2773 (chain 140) for a table first written on 25 October 2026 (session 2764).

Tables: `statat_austria_electricity_annual`

## Publisher and address

Statistics Austria (Statistik Austria), "Energy balances Austria 1970-2024", an OpenDocument spreadsheet listed on its energy balances page (`https://www.statistik.at/en/statistics/energy-and-environment/energy/energy-balances`): `https://www.statistik.at/fileadmin/pages/99/energy_balances_austria_1970-2024_data.ods`, its sheet "Electricity". No key. Source id `statat:energy_balances_1970_2024`. Connector: `warehouse/connectors/statat_energy_balance.py` (session 2764), whose raw store is `warehouse/raw/statistik_austria/`. www.statistik.at's robots file closes only its search pages and names no Claude agent (read 1509).

## Vintage and revision

Written by run `20261025T234002Z` (the write under the lock, offline), which read the file retrieved at 2026-10-25T23:33:09Z, last modified 7 November 2025. Statistics Austria publishes the balances each autumn with the year before added, and revises earlier years.

## Shape and variables

Series, 6,675 rows, 117 entities, 8 variables, each year from 1970 to 2024, in MWh. **The sheet gives its blocks in TJ and again in MWh; the table reads the MWh blocks, so nothing is converted.**

- `entity`:
  - `statat_ele:at` for a balance item's total;
  - `statat_ele:<plant>[:<owner>[:<fuel>[:<sub-fuel>]]]` for the transformation input and output by plant type (power, CHP, heating plants and the others), owner (public plants, autoproducers) and fuel;
  - `statat_ele:sector:<sector>` for final energy use by sector: 19 branches and the three totals (industry, transport, other sectors); internal navigation and air transport are 0 in every year and not written;
  - `statat_ele:branch:<branch>` for the energy sector's use by branch, from 1999, where the sheet begins it.
- `variable`, the balance item: `imports`, `exports`, `gross_inland_consumption`, `transformation_input`, `transformation_output`, `energy_sector_use`, `transport_losses`, `final_energy_use`. Four more items (primary production, stock changes, recycling, non-energy use) are 0 in every year and not written.
- `ts_utc` the year's first day; `freq` P1Y; `geo` AT; `node` the sheet's labels, outermost first.

**Gross inland consumption of electricity is its net imports** in the balance's convention; generation is the transformation output.

**Figures:** generation was 29,453,000 MWh in 1970, 59,855,089 in 2000 and 78,753,844 in 2024; final energy use 20,219,998, 50,805,814 and 62,699,563.

## Reading the source

- The run stops at once, asking nothing, while `statistik_austria` or www.statistik.at is paused.
- One request a run, saved and reused unless `--fresh`; `--offline` asks nothing.
- **The file is read by streaming its 263 MB content.xml with the standard library** (`zipfile` and `xml.etree.ElementTree.iterparse`). No ODS reader is a dependency of the ERW. Repeated cells and rows are expanded as the format writes them.
- The sheet's structure is fixed in the connector (the twelve balance items, eight plant types, two owners, the fuels and their sub-fuels). A label outside it stops the run.
- A row that is 0 in every year is not written (96 rows); a zero within a written row stays.
- **Checks,** within 1 MWh in every year, all passing:
  - gross inland consumption equals primary production plus imports, stock changes and recycling less exports;
  - final energy use equals the balance's remainder;
  - each parent row equals its parts;
  - the sectors make final energy use;
  - the branches make the energy sector's use.

  281 parent years whose fuel breakdown is not yet split (zero parts under a non-zero fuel) are counted, not checked.
- Nothing is filled.

## License

Public. Statistics Austria's general terms, section 10 (read 1518): reproduction, distribution and making available, commercial or not, with the source "STATISTIK AUSTRIA" cited and edits stated. The verdict, may be public, was given in session 2764. In the release package; held from the live set.

## Cross-check

Against `eurostat_electricity_production_annual` (Austria, TOTAL less pumped hydro RA130) and `econtrol_austria_electricity_monthly` (twelve months summed), GWh:

| Year | Generation (here) | Eurostat less pumped hydro | Imports (here) | E-Control imports | Exports (here) | E-Control exports |
|---|---|---|---|---|---|---|
| 1990 | 49,296 | 49,296 | | | | |
| 2015 | | | 29,389 | 29,389 | 19,328 | 19,328 |
| 2020 | | | 24,522 | 24,523 | 22,327 | 22,327 |
| 2024 | 78,754 | 78,758 | 18,923 | 18,927 | 25,703 | 25,703 |

Statistics Austria's balance leaves pumped storage generation out of the transformation output.
