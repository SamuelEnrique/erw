# Session 2035 report: motor fuel (FHWA's monthly motor fuel reported by the states)

23 October 2026, from 19:39 UTC, on lab-desktop (the data machine), the eighth session of `queue/done/058-day-24-october-data-outages-fuels-mines-vehicles.md`, unattended. Model spend USD 0. Pulls: 11 requests of 20 (below).

## Read these first

- **One table written, validated, archived, in coverage (sector products, public), in the release package, both holds:** `fhwa_motor_fuel_monthly`, the gallons of gasoline and of special fuels (diesel, mostly, and alternative fuels) each of the 50 states, DC and Puerto Rico reports taxed a month, January 2020 to May 2026: 7,998 rows, `gasoline_volume` and `special_fuel_volume` in `gal` (Decision 59, session 2030), each with FHWA's data type (Actual, Estimate, or Gas Holiday: Georgia's April and May 2026, when its gasoline tax was suspended).
- **FHWA's own site stopped the Monthly Motor Fuel Reports after December 2023.** Its page sends readers to DOT's DataHub (`data.transportation.gov`), where FHWA's Office of Highway Policy Information publishes the reports' source data as two datasets, "Monthly Motor Fuel - Gasoline Volumes Distributed" (`5qxh-t94v`) and "Monthly Special Fuel Volumes Distributed" (`5n49-mh85`), from 2020. The older reports (January 2012 to December 2023, one workbook a month) were not taken.
- **Rows not written, counted in the header:** North Carolina's five months of 2026 marked "Not Published" (a 0 that measures nothing), and the months June to December 2026, in which every place reads 0 (the datasets carry the rest of the year before the states report).
- **The cross-check against `eia_product_supplied_monthly`** (thousand barrels at 42 gallons), the 50 states and DC summed, whole years: FHWA's gasoline is 1.027 to 1.037 of EIA's U.S. product supplied of finished motor gasoline every year from 2020 to 2025 (141.35 against 136.97 billion gallons in 2025); FHWA's special fuels are 0.72 to 0.78 of EIA's distillate fuel oil, which also counts heating oil and the rail, marine and off-road diesel the states' highway taxes do not.
- **FHWA's verdict: "U.S. Department of Transportation, Federal Highway Administration (FHWA)", may be public** (read 214): the dataset's own record gives its license as "Public Domain U.S. Government", with the terms link usa.gov/government-works; the gasoline dataset's says "Public Domain".

## The pulls

1. `www.fhwa.dot.gov/robots.txt` (read 212): a one-second crawl delay; `/policyinformation/travel_monitoring/` and other paths disallowed, not `/policyinformation/motorfuel`. 2. The motor fuel index (an empty stub). 3. The motor fuel data page. 4. The fuel quick-find page. 5. The Monthly Motor Fuel Reports page. 6. `data.transportation.gov/robots.txt` (read 213): a one-second crawl delay, only its browse, search and facet paths disallowed. 7. The DataHub story "Monthly Motor Fuel Report", for the datasets' ids. 8 and 9. The two datasets' metadata (read 214 is the first). 10 and 11. The two CSV files, saved in `warehouse/raw/fhwa_motor_fuel/` and reused by the write (`--offline`). Requests to each host were at least a second apart.

## Decisions made without you

- **DataHub's datasets in place of FHWA's monthly workbooks:** they are the reports' source data, go past December 2023, and come as two files instead of 144.
- **Gasoline and special fuels in one table,** two variables, since the datasets share their keys.
- **Georgia's Gas Holiday months kept** with their data type: the volumes are what Georgia still reported taxed.
- **Puerto Rico kept**, and left out of the cross-check's sum, as EIA's U.S. figures do not include it.

## For Samuel's ruling

- None new.

## Files

- New: `warehouse/connectors/fhwa_motor_fuel.py`, `tests/test_session2035.py` (3 tests), this report.
- Changed: `build_coverage.py`, `release_v1.py`, `live_set.yaml`, `docs/coverage.md`, `coverage.csv`, `archive_manifest.csv`, `sources.csv`, `license_reads.csv` (212 to 214), `license_verdicts.csv` (FHWA), `license_tables.csv`, `docs/licenses.md`, `docs/redivis/release-v1/`.
- On the data machine only: `runs/c058/s2035/`, `runs/license_reads/s2035/`, `runs/s2035*`, `warehouse/raw/fhwa_motor_fuel/`.
