# Session 2182 report: the fuel and electricity public transit uses (the FTA's National Transit Database)

24 October 2026, from 01:54 UTC, on lab-desktop (the data machine), a session of `queue/done/097-day-1-november-data-canada-offshore-inspections-supply.md`, the first source of the session's own choosing. Model spend USD 0. Pulls: data.transportation.gov, 2 requests of 20: the dataset's metadata and its CSV. Its robots file and catalog were read in session 2181 (reads 355 and 359). The trial and the write ran offline. Also Supabase, for the locks and the archive.

## Why this source

The ERW held no transit energy. The National Transit Database gives the electricity each rail and bus system draws, as well as its diesel, natural gas and hydrogen, by agency, mode and year. That is a direct, published account of one transport sector's electricity demand, beside the grids that serve it. The FTA's dataset is public domain (session 2181's verdict).

## Read these first

- **One series table, `ntd_transit_energy_annual`:** 10,161 figures for 553 agencies and 1,425 agency modes, report years 2022 to 2025, from "2022 - 2025 NTD Annual Data - Fuel and Energy" (DOT DataHub 8ehq-7his). Each figure is one agency, mode and type of service's use of one fuel in a year.
- **Units:**
  - gallons as the FTA gives them (`gal`; LPG and CNG in its gallon equivalents, named so in the variable);
  - electricity in MWh (the FTA's kWh divided by 1,000), split into electric propulsion (third rail or overhead wire) and electric battery (charging);
  - hydrogen in metric tons (the FTA's kg divided by 1,000).

  No new unit is needed.
- **Not taken:** miles and miles per gallon. The standard has no distance unit, and the ratios are the FTA's own arithmetic.
- **A blank has no row, and a zero the FTA prints is kept.** No quantity taken carries the FTA's Questionable mark this year (the flag is kept in `x_questionable`).
- **The national totals, 2022 to 2025:**
  - electric propulsion grew from 5.50 to 6.67 TWh;
  - battery charging grew from 49 to 112 GWh, more than doubling;
  - diesel stayed near 416 to 438 million gallons;
  - CNG rose from 171 to 199 million gallon equivalents;
  - hydrogen rose from 246 to 570 t.
- **The cross-check** (`runs/c097/s2182/cross.py`) puts transit's electricity by state beside EIA's retail sales to the transportation sector (`eia_retail_sales_monthly`, `:TRA`, whole years):
  - New York 0.83 to 0.98, California 0.98 to 1.14, Illinois 0.87 to 0.97, New Jersey 1.10 to 1.17, Pennsylvania 0.69 to 0.89.
  - DC is about 2 and Maryland about 0.2, because the table puts each agency at its headquarters' state. WMATA is in DC and draws power in Maryland and Virginia too.
  - The median over the 13 states above 100 GWh is 0.76.
- **Registered:**
  - the sector rule (`power;products`);
  - both holds;
  - the release package's rows (1 table, 9 variables);
  - the license tables (licenses check: 0 problems; release check: 0 differences).

  No row is given twice. The test is `tests/test_session2182.py` (3 tests).

## Found on the way

- **The FTA's "Compressed Natural Gas (mpg) Questionable" column holds numbers** (for example 3.79 or 913.33), not the word Questionable. These look like the CNG miles per gallon themselves. The column is not taken, and the connector stops if a Questionable column of a quantity it takes holds anything but blank or Questionable.

## Errors

- None.

## Decisions made without you

- **This source chosen,** for the reason above.
- **kWh and kg scaled to MWh and t,** existing units, rather than adding `kWh` and `kg`.
- **Miles and mpg not taken.**

## For Samuel's ruling

- None new.

## Files

- New: `warehouse/connectors/ntd_transit_energy.py`, `tests/test_session2182.py`, this report.
- Changed: `warehouse/metadata/build_coverage.py`, `warehouse/supabase/live_set.yaml`, `warehouse/redivis/release_v1.py`, `docs/coverage.md`, `coverage.csv`, `sources.csv`, `archive_manifest.csv`, `license_tables.csv`, `docs/licenses.md`, `docs/redivis/release-v1/`.
- On the data machine only: `runs/c097/s2182/`.
