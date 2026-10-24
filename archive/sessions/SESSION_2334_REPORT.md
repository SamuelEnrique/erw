# Session 2334 report: U.S. refinery utilization and capacity by PADD and refining district, a month (EIA, petroleum/pnp/unc), the third own choice

24 October 2026, from 07:32 UTC, on lab-desktop (the data machine), the thirteenth session of `queue/done/108-day-10-november-data-malaysia-thailand-ecuador-kenya.md`, unattended. It runs before session 2333 so that the records include its table. Precheck passed (`runs/c108/pre2334.out`). Model spend USD 0. Pulls: EIA's API, 12 of 20 (below).

## Read these first

- **Three EIA routes the ERW does not hold were read first** (metadata, 3 requests):
  - `petroleum/cons/refmg` (refiner motor gasoline sales) ends in March 2022, so it was left.
  - `petroleum/stoc/typ` (stocks by type) overlaps the held `cu` and `wstk` and file 109's state stocks (`stoc/st`), so it was left.
  - `petroleum/pnp/unc` runs from January 1985 to July 2026, so it was taken.
- **One public table:** `eia_refinery_utilization_monthly`. It is written, validated, archived, in coverage (sector oil and products), and held from the live set and the release.
  - **Content:** 36,672 rows, 80 series, January 1985 to July 2026. Gross input to refineries; operable, operating and idle operable capacity (kbbl/d); and EIA's utilization of operable capacity.
  - **Areas:** the U.S., the five PADDs and the ten refining districts (Appalachian No. 1, East Coast, the three Midwest and five Gulf Coast districts).
  - **Utilization** is written as a ratio (EIA's percent divided by 100), as `eia_refinery_weekly` writes it. The first trial wrote it as pct; it was changed before the write.
  - **Why this one:** the ERW holds the weekly PADD figures (`eia_refinery_weekly`) and the annual capacity by refinery (`eia_refinery_capacity_annual`), but not the monthly figures or the districts. The districts separate, for example, the Texas Gulf Coast from Louisiana's.
- **License:** EIA's verdict is on record (public).

## The cross-check (`runs/c108/s2334/cross.py`, `cross.out`)

- **Utilization against input over capacity:** EIA's utilization equals gross input over operable capacity within 0.006 in 7,819 of 7,984 area-months (largest gap 0.050).
- **Capacity's parts:** operable equals operating plus idle within 1 kbbl/d in 4,713 of 4,736.
- **The districts add to their PADDs, and the PADDs to the U.S.:**
  - PADD 1 is East Coast plus Appalachian No. 1 in all 499 months.
  - PADD 3 is its five districts in 489 (gross input; the largest gap 2).
  - PADD 2 is its three in 475 (the largest gap 65 kbbl/d).
  - The U.S. is the five PADDs in 494.
- **Against `eia_refinery_weekly`:** each PADD's monthly utilization is within 0.02 of the mean of the weeks ending in the month in 694 of 970 PADD-months (median gap 0.011). The weekly figures are estimates, revised in the monthly report.
- **The U.S., yearly means:** utilization 0.776 (1985), 0.926 (2000), 0.903 (2019), 0.789 (2020), 0.905 (2024), 0.920 (2025). Operable capacity 15,671 kbbl/d (1985) and 18,181 (2025).

## Pulls against their ceilings

| Host | Requests | What |
|---|---|---|
| api.eia.gov | 12 of 20 | three routes' metadata, a year's sample of `pnp/unc`, the trial's 8 pages |

## Errors

- **Utilization first written as pct;** changed to ratio before the write, to match the weekly table.

## Decisions made without you

- **EIA's monthly refinery utilization chosen** as the third own choice: U.S. first, current to July 2026.
- **Utilization as a ratio.**

## For Samuel's ruling

- None new.

## Files

- New:
  - `warehouse/connectors/eia_refinery_utilization.py`
  - `tests/test_session2334.py`
  - this report
- Changed:
  - `warehouse/metadata/build_coverage.py`, `warehouse/redivis/release_v1.py`, `warehouse/supabase/live_set.yaml`
  - `warehouse/metadata/license_tables.csv`, `docs/licenses.md`
  - `docs/redivis/release-v1/`
  - the coverage, sources and archive manifest files
- On the data machine only: `runs/c108/s2334/`, `runs/s2334*`.
