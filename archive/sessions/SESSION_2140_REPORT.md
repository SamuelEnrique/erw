# Session 2140 report: households' energy burden (DOE's LEAD Tool)

23 and 24 October 2026, from 23:52 UTC, on lab-desktop (the data machine), chain 090, unattended. Its pull ran in the background while sessions 2139 and 2141 ran. Model spend USD 0. Pulls: 53 requests of 70 (the robots file, and the 52 state zips, Vermont's first as a trial); the submission page was read again in session 2139 (read 320).

## Read these first

- **A new table, `doe_lead_energy_burden`** (series, 160,419 rows, `power;gas`): DOE's Low-Income Energy Affordability Data (the LEAD Tool, 2022 update) for every county of the 50 states, DC and Puerto Rico, and for each state. It holds households and their average income, electricity, gas and other fuel costs, total energy cost and energy burden, by income bracket as a share of area median income (0 to 30, 30 to 60, 60 to 80, 80 to 100, 100 to 150, 150 percent and up) and for all households. Written, validated (0 errors, 0 warnings), archived (160,419 rows), held from the Redivis storage and the live set, its release rows added. Public: CC BY 4.0, the submission's license (reads 261 and 320), under DOE's verdict.
- **How the 7.84 GB were taken without holding a file whole** (chain 069 left the source for this reason):
  - `--pull` streams each state's zip to `warehouse/raw/doe_lead/files/` with a manifest (address, time, bytes, sha256). California's is 912,720,159 bytes, all 52 together 7,841,647,083 bytes (7.84 GB, 7.30 GiB).
  - `--write` reads each state's AMI Counties CSV inside its zip in chunks of 200,000 rows, keeping only the columns it sums.
  - The census tract files and the FPL, SMI and LLSI files are not taken; the header says so.
- **The method, in the header:**
  - LEAD's cells (county by bracket by tenure, building age, building type and heating fuel) are summed to the county and bracket.
  - Households are the sum of LEAD's UNITS.
  - Each average is a sum of LEAD's value-times-units over the sum of its own units.
  - The burden is the total energy cost's average over the income's average, times 100. The ERW computes it the way the LEAD Tool computes a group's burden from its averages.
  - The table's year is the one the files name, 2022.
- **What the table shows:**
  - 127,451,762 households in all.
  - The burden for all households runs from 1.18 percent (DC) to 4.37 (Puerto Rico); among the states, Maine is highest at 4.12 and Vermont next at 3.95.
  - For households under 30 percent of area median income it runs from 9.7 percent (Washington) to 26.4 (Maine) among the states, and 44.7 in Puerto Rico.
  - Vermont was checked by hand from its cells before the code was written: 24.33 percent in the lowest bracket, 2.29 in the highest. The table gives the same.
- **Cross-check against EIA's SEDS** (`eia_seds_residential_annual`, chain 069, 2022), 51 places. Dividing SEDS's residential spending by LEAD's households:
  - Electricity per household is a median 1.09 times LEAD's average (0.91 in Hawaii to 1.25 in Maine).
  - All energy is 1.04 times (0.86 to 1.29).

  The two measure different things: SEDS's state totals are EIA's estimates of what the sector bought, and LEAD's averages come from the households' survey answers. So agreement within a quarter is what can be expected, and it holds.

## Requests (53 of 70)

| n | What | Outcome |
|---|---|---|
| 1 | data.openei.org/robots.txt | 404 |
| 2 | VT-2022-LEAD-data.zip (the trial) | 200, 28,399,134 bytes |
| 3 to 53 | the other 51 state zips | 200 each; 7.84 GB in all, the manifest has each |

Read recorded: 322 (the robots file) (renumbered at session 2147's merge, after chains 069 and 079's).

## Decisions made without you

- **Counties and states, not tracts:** the tract files are about five times the county files (Vermont: 90 MB against 17 MB) and hold the same households.
- **The AMI brackets, not FPL, SMI or LLSI:** the LEAD Tool shows these first. The other files are the same households cut by other income lines.
- **The burden computed from averages, and said so.**

## For Samuel's ruling

- None new.

## Files

- New: `warehouse/connectors/doe_lead.py`, `tests/test_session2140.py`, this report.
- Changed: `warehouse/metadata/build_coverage.py`, `warehouse/redivis/release_v1.py`, `warehouse/supabase/live_set.yaml`, `docs/coverage.md`, `warehouse/metadata/coverage.csv`, `warehouse/metadata/sources.csv`, `warehouse/metadata/archive_manifest.csv`, `docs/redivis/release-v1/`, the license record.
- On the data machine only: `runs/c090/s2140/`, `warehouse/raw/doe_lead/files/` (7.84 GB), `warehouse/output/doe_lead_energy_burden.csv`.
