# Session 2809 report: Czech regions' electricity capacity, production and consumption (the CZSO's Comparison of Regions 2025)

26 October 2026, from about 05:00 to 05:08 UTC, on lab-desktop (the data machine), chain 143, unattended. Precheck passed (`runs/c143/pre2809.out`). Model spend USD 0. Pulls: 6 requests of 15 (5 by the probe, 1 by the fetch); three web searches.

## Read these first

- **`czso_cz_regional_electricity_annual` is new:** the Czech Statistical Office's "Comparison of Regions in the Czech Republic 2025" (published 22 January 2026), tables 14.101 and 14.103, 2024's figures for the 14 regions and Czechia:
  - installed capacity at 31 December (MW) and gross production (MWh), by type of plant;
  - net consumption (MWh) by economic activity.

  The figures are the Energy Regulatory Office's (ERU), as the CZSO publishes them. 360 rows, 15 areas (ISO 3166-2 codes CZ-10 to CZ-80, and CZ). The table has been written, validated, archived and put in coverage. It is held from the live set and from Redivis storage until session 2815's draft.
- **Why this table:** the ERW holds Czechia as a whole (Eurostat, Energy-Charts) and no region of it.
  - **The Ústí nad Labem region (CZ-42) leads:** 20.1 TWh of the 73.9 TWh produced, and 5,418 MW of the 22,981 MW installed (its lignite plants). South Bohemia (CZ-31, Temelín) and Vysočina (CZ-63, Dukovany) follow.
  - Consumption is highest in Central Bohemia (8.1 TWh) and Moravia-Silesia (6.8 TWh).
  - Solar capacity is highest in South Moravia (674.5 MW).
- **Cross-check against Eurostat, Czechia 2024:**

  | Measure | CZSO (here) | Eurostat |
  |---|---|---|
  | gross production | 73,881,775 MWh | 73,900,393 MWh |
  | nuclear production | 29,696,397 MWh | 29,696,397 MWh |
  | wind production | 716,810 MWh | 716,810 MWh |
  | solar production | 3,592,654 MWh | 3,592,683 MWh |
  | installed capacity | 22,980.7 MW | 23,022.1 MW |
  | nuclear capacity | 4,290 MW | 4,290 MW |
  | net consumption, or final consumption | 55,924 GWh | 56,039 GWh |
  | households | 15,637 GWh | 15,635 GWh |
- **The tables' own sums:** the regions make Czechia in every row, and the plant types make each region's capacity and production. **The seven activities fall short of net consumption in all 15 areas,** by 261.6 GWh (0.5 per cent) for Czechia. That is kept as published and counted (54 of 69 comparisons hold, all 15 others this one). The tables' shares and households' kWh a head are not written.
- **Terms: the CZSO's verdict is new** (read 1617): "Statistical information released by the Czech Statistical Office through the website https://csu.gov.cz is licensed under CC BY 4.0". The terms must be mentioned, and adjusted or derived data labelled as such. The header says both.
  - The license record shows the table as agreed, public (619 tables, 259 publishers with a verdict, 0 problems).
  - csu.gov.cz's robots file (read 1613) disallows Baidu's agents and three paths, and names no Claude agent. www.czso.cz redirects to it (read 1614).
- **Only the latest edition was read:** each edition holds one year in a zip of its own. Earlier years (the 2023 edition's 2022, read 1615) are left for a later chain.
- **The console:** a Czech letter (č) cannot be printed by this machine's console, so the node is written in ASCII. The Czech name stays in `x_region`.

## The requests

| n | What | Outcome |
|---|---|---|
| 1 | csu.gov.cz's robots file | 200 |
| 2 | www.czso.cz's robots file | 200, redirected to csu.gov.cz's |
| 3 | the 2023 edition's energy chapter (www.czso.cz, redirected to csu.gov.cz) | 200, four Excel tables of 2022 |
| 4 | the 2025 edition's product page | 200, the tables' zip |
| 5 | the CZSO's conditions for use | 200, CC BY 4.0 |
| 6 | the 2025 edition's zip (fetch, 5.1 MB, last modified 12 February 2026) | 200 |

Reads recorded: 1613 to 1617.

## Decisions made without you

- **The regional tables taken** for the CZSO's national energy figures, which Eurostat holds already.
- **Capacity at 31 December written at the year's 1 January** (P1Y), as the ERW's annual tables are.
- **The activities' shortfall kept,** not given an "other" row.

## For Samuel's ruling

- None new.

## Files

- New:
  - `warehouse/connectors/czso_regional_electricity.py`
  - `tests/test_session2809.py` (4 tests, passing)
  - this report
- Changed:
  - the table's registration and holds;
  - the license record (reads 1613 to 1617, the CZSO's verdict) and `docs/licenses.md`;
  - coverage, sources, the archive manifest and the release v1 records.
- On the data machine only:
  - `runs/c143/s2809/`, `runs/c143/s2809_verdict.py`, `runs/license_reads/s2809/`;
  - `warehouse/raw/czso_regions/`.
