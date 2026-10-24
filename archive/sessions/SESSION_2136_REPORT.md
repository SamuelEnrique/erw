# Session 2136 report: the national greenhouse gas inventory (EPA)

23 October 2026, from 23:21 UTC, on lab-desktop (the data machine), chain 090, unattended. Model spend USD 0. Pulls: 4 requests of 15 (3 by the probe, 1 zip; the write ran offline).

## Read these first

- **A new table, `epa_ghg_inventory_annual`** (series, 5,016 rows, `carbon;power;oil;gas` like `epa_ghgrp_facility_emissions`): the nation's emissions a year from 1990 to 2022, in tCO2e (Decision 61, EPA's MMT CO2 Eq. times 1,000,000). It covers 8 entities and 85 variables, from three tables of the Inventory's Chapter 2:
  - Table 2-10: the economic sectors and their sources, direct;
  - Table 2-11: the electric power industry by gas and fuel;
  - Table 2-12: each sector by gas, with the electricity it uses distributed to it.

  Written, validated (0 errors, 0 warnings), archived, held from the Redivis storage and the live set. It is public under EPA's verdict (read 55), and its rows are in the release package.
- **The last final Inventory is 1990 to 2022** (April 2024). EPA's Inventory page says the 1990 to 2023 Inventory was published as a draft for public comment in January 2025; the table does not take the draft.
- **Gross emissions:** 6,536.9 MMT in 1990, 6,343.2 in 2022; the electric power industry's CO2 1,549.2 MMT in 2022.
- **The table checks itself:**
  - Table 2-11's Total equals Table 2-10's Electric Power Industry in every year.
  - Table 2-12's national lines and U.S. Territories equal Table 2-10's, so they are checked, not written twice.
  - The comparison is numeric: EPA prints 1965.0 in one table and 1965 in the other.
- **Cross-check, the power sector:**
  - `epa_ghgrp_facility_emissions`' power plants (direct emissions, x_sectors naming Power Plants), summed, hold 101.7 to 102.3 percent of the Inventory's electric power total in every year 2015 to 2022.
  - EIA's national CO2 (`eia_power_co2_state_annual`'s `US:ALL`) is 5.3 to 8.3 percent above the Inventory's fossil fuel combustion CO2 in every year 1990 to 2022, a steady gap. That table's states and DC sum to its `US` row, so a sum over every `:ALL` entity counts the nation twice; the check reads `US:ALL` alone.
- **Two fixes to chain 090's earlier tables:**
  - All three tables now have rows in `docs/redivis/release-v1/` (the release check asks a row of every table, held or not).
  - `gfz_kp_index_3h`'s registry row and header now say `public` (CC BY 4.0, as before, in its words), the registry's word for an open license. `tests/test_session410` failed on the license word `CC BY 4.0`. The file was rewritten offline under the lock, its rows unchanged.

## The source

- `https://www.epa.gov/system/files/other-files/2024-04/trends-in-greenhouse-gas-emissions-and-removals.zip` (the "2024 Trends in Greenhouse Gas Emissions Tables", 15 CSV files, last modified 26 August 2024), listed on the 1990-2022 Inventory's page.
- The footnote letters EPA appends after Combustion, Total, HFCs and Percent ("Stationary Combustionb", "LULUCF Sector Net Totalc", "HFCsb") and a stray character before one are dropped from the lines; the lines are otherwise as published. Table 2-11's "Stationary Sourcesa" keeps its letter, so `power:ch4:stationary_sourcesa` and `power:n2o:stationary_sourcesa` carry it (66 rows; found by session 2143, left as written, since a new name would break the table's series).
- No value in the three tables is printed as "+". Table 2-12's Residential line under Direct Emissions is labelled SF6, as EPA labels it (Table 2-10 gives Residential's substitutes for ozone depleting substances the same values). It is kept as published and noted in the header.
- The Inventory's tables do not name their global warming potentials, so the header does not either.

## Requests (4 of 15)

| n | What | Outcome |
|---|---|---|
| 1 | www.epa.gov/robots.txt | 200: site administration paths only |
| 2 | the Inventory page | 200: the 1990-2023 draft, the 1990-2022 final |
| 3 | the 1990-2022 Inventory's page | 200: the chapters and their table zips |
| 4 | the Trends tables zip | 200, 53,063 bytes |

Reads recorded: 300 to 302 (renumbered at session 2147's merge, after chains 069 and 079's). Chain 069 landed with reads 256 to 272 while this session ran.

## Decisions made without you

- **Three tables of Chapter 2, not the Data Explorer.** They are published files, and they give the sector, gas and fuel breakdowns the chain file asks for.
- **Table 2-12's repeated lines checked, not written.**
- **The sector words of `epa_ghgrp_facility_emissions`.**
- **`public` in the registry for GFZ's CC BY 4.0** (above).

## For Samuel's ruling

- None new.

## Files

- New: `warehouse/connectors/epa_ghg_inventory.py`, `tests/test_session2136.py`, this report.
- Changed:
  - `warehouse/connectors/gfz_kp_index.py` (the license word);
  - `warehouse/metadata/build_coverage.py`, `warehouse/redivis/release_v1.py`, `warehouse/supabase/live_set.yaml`;
  - `docs/coverage.md`, `warehouse/metadata/coverage.csv`, `warehouse/metadata/sources.csv`, `warehouse/metadata/archive_manifest.csv`;
  - `docs/redivis/release-v1/` (three tables' rows);
  - the license record.
- On the data machine only: `runs/c090/s2136/`, `runs/c090/rewrite.sh`, `warehouse/raw/epa_ghg_inventory/`, `warehouse/output/epa_ghg_inventory_annual.csv`.
