# Transportation's energy by mode and fuel, and electric vehicle sales, a year (ORNL's Transportation Energy Data Book)

Energy Research Warehouse (ERW), method note written in session 2052 (chain 059) for a table first written on 23 October 2026 (session 2048).

Tables: `ornl_tedb_transportation_annual`

## Publisher and address

Oak Ridge National Laboratory (ORNL), Transportation Energy Data Book (Davis, Dahal, Moore, Patwary and Boundy), Edition 41, `https://tedb.ornl.gov`. The connector reads the data page `https://tedb.ornl.gov/data/`, takes the zip of the highest edition it links (`https://tedb.ornl.gov/downloads/Spreadsheets_Ed_41.zip`), and reads five workbooks from it: Tables 2.2, 2.4, 2.7, 2.8 and 6.2. Table 6.2 is compiled by the Transportation Research Center at Argonne National Laboratory. Source id `ornl:tedb`. Connector: `warehouse/connectors/ornl_tedb.py` (session 2048).

## Vintage and revision

1950 to 2024, Edition 41 (`x_edition`); the zip last modified 2026-09-29T19:36:00Z (`vintage` in every row), retrieved 2026-10-23T18:58:56Z, written by run `20261023T190539Z` from the saved copy. Header: "This run wrote 674 rows: 674 new ...; 0 rows are kept from earlier runs."

The table is merged on (entity, variable, ts_utc): a new edition replaces the years it restates and the years it no longer prints stay. The data page is asked fresh each run; the zip is reused when saved.

## Shape and variables

Series, 674 rows; `freq` P1Y, `ts_utc` the year's first day, `geo` US, `node` the row's or column's label as printed, `x_table` the book's table.

| Table | Rows | Entities | Variables | Years |
|---|---|---|---|---|
| 2.2, energy consumption by end-use sector | 175 | 5 (transportation, industrial, commercial, residential, total) | `energy_consumption`, TBtu (the book's quadrillion Btu x 1,000) | 35: 1950 to 1995 every five years, 2000 to 2024 |
| 2.4, transportation energy by source | 234 | 1 | `energy_use` TBtu, and `share_` petroleum, natural_gas, coal, renewables, electricity in pct (the book's fraction x 100) | 39: 1950 to 1990 every five years, 1995 to 2024 |
| 2.7, energy by mode and fuel | 103 | 28 modes | `energy_use_` gasoline, diesel, lpg, jet_fuel, residual_fuel_oil, natural_gas, electricity, total, TBtu | 2023 |
| 2.8, energy by mode | 58 | 29 modes (2.7's 28 and `off_highway`) | `energy_use`, TBtu | 2022, 2023 |
| 6.2, light-duty sales | 104 | 1 | `sales_hybrid`, `sales_plugin_hybrid`, `sales_battery_electric`, `sales_light_duty`, count (the book's thousands x 1,000) | 1999 to 2024 |

Units: TBtu 375 rows, pct 195, count 104. A mode's entity is its path, `ornl_tedb:t2_7:highway.light_duty.cars`, `t2_8:nonhighway.rail.passenger.commuter`, built from the label's level in a closed map and its indentation (an indented part of a part is level 3).

In 2024: the nation used 94,200 TBtu, transportation 28,200 (Table 2.2); 1,609,000 hybrids, 321,800 plug-in hybrids and 1,247,700 battery electric vehicles were sold of 15,436,000 light-duty vehicles. Table 2.8's total for all modes: 25,767.6 TBtu in 2022, 26,101.6 in 2023.

## Reading the source

- Each workbook is the first sheet of `Table<n>_<nn>_<YYYY>-<MM>.xlsx`; exactly one file of each must be in the zip, or the run stops. An empty first column is dropped (the sheets begin in column B).
- A row or column label not in the closed maps (a trailing footnote letter a to g dropped) stops the run, as does a header not found, Table 2.7's year not Table 2.8's latest, or an (entity, variable, year) given twice.
- A cell that is empty, a dash, or the letters "a" or "b" is no row. Year rows are read until the first row that is not a year, so the per-cent change rows below are not taken; the shares of 2.2, 2.8 and 6.2 are not taken.
- Table 2.7's rows take Table 2.8's latest year (2023).
- Ceiling: two requests (the data page and the zip).

## License

`license_tables.csv` lists the table under "Oak Ridge National Laboratory (ORNL), Transportation Energy Data Book". `license_verdicts.csv` holds no verdict for that publisher; reads 188 (the robots file, every path but /admin/ allowed) and 189 (the citation page: "states no terms of reuse") are in `license_reads.csv`. `docs/licenses.md` lists the table as "not settled (needs written permission by default)", flagged internal, among the publishers no read covers. Session 2048's report leaves the terms for Samuel's ruling: publish, ask ORNL, or keep internal.

## Cross-checks (session 2052)

- The counts above were computed from the rows, read past the header lines; no (entity, variable, ts_utc) is given twice.
- Table 2.7's `energy_use_total` equals Table 2.8's 2023 figure in all 28 modes the two share (largest difference 0).
- Table 2.4's five shares sum to between 99.9 and 100.1 in each of the 39 years. Table 2.2's transportation against Table 2.4's total: the 35 common years within 49.1 TBtu (2024: 28,200 and 28,150.9), the book's rounding to a tenth of a quad. Table 2.2's four sectors sum to its total within 200 TBtu (1955).
- Session 2048's report set Table 2.2's total, commercial and industrial against EIA's monthly sector series summed to the year: within 50 TBtu to 2020, EIA above TEDB from 2022 (total 382.3 TBtu above in 2024).

## What it does not hold

- The book's other tables and figures.
- Table 2.7 for any year but 2023, and Table 2.8 for any but 2022 and 2023.
- The years between the book's five-year steps before 1995 (2.4) and 2000 (2.2).
- Table 2.8 holds one mode more than Table 2.7, `off_highway` (2,326.8 TBtu in 2023), equipment that does not travel on roads; session 2048's report, corrected by session 2052, says so.
