# Session 2036 report: electric vehicles by state (the Alternative Fuels Data Center's registration counts)

23 October 2026, from 19:47 UTC, on lab-desktop (the data machine), the ninth session of `queue/done/058-day-24-october-data-outages-fuels-mines-vehicles.md`, unattended. Model spend USD 0. Pulls: 14 requests of 20 (below).

## Read these first

- **One table written, validated, archived, in coverage (sectors power and products, public), in the release package, both holds:** `afdc_vehicle_registrations_annual`, the light-duty vehicles registered in each state, DC and the United States by fuel type, 2016 to 2025: 6,240 rows, twelve fuel types (electric, plug-in hybrid, hybrid, biodiesel, flex fuel, CNG, propane, hydrogen, methanol, gasoline, diesel and unknown), each a count rounded to the closest 100, as of the year's end.
- **Electric vehicles in the United States:** 280,300 (2016), 1,018,900 (2020), 3,555,900 (2023), 4,503,700 (2024), 5,689,100 (2025); California 1,256,600 in 2023.
- **The published table, not the API:** AFDC's Vehicle Registration Counts by State page prints each year's table (`/vehicle-registration?year=<year>`); the counts are reached without AFDC's key-gated API, so the chain file's stop does not apply. AFDC's Electric Vehicle Registrations by State workbook (data 10962) holds only 2023's electric vehicles, exact.
- **The cross-check:** each state's 2023 electric vehicles on the page are within 50 of the workbook's exact counts, as rounding to 100 allows (California 1,256,600 against 1,256,646). The page's United States row is the sum of its rounded state rows in every year and fuel (120 of 120), so it is 455 above the workbook's exact total in 2023.
- **The counts are derived by the National Laboratory of the Rockies from Experian Information Solutions' registration data** (AFDC's words). DOE publishes them on its own site, which defers to DOE's web policies (read 54, may be public), and the table takes that verdict.

## The pulls

1. `afdc.energy.gov/robots.txt` (read 194): a comment, no rule. 2. Electric Vehicle Registrations by State (data 10962). 3. Vehicle Registration Counts by State (the 2025 table). 4. The 10962 workbook. 5 to 14. The connector's trial, the ten years' pages, saved in `warehouse/raw/afdc_registrations/` and reused by the write (`--offline`).

## Decisions made without you

- **The page's table for each year** rather than the single-year workbook: it covers ten years and twelve fuels.
- **The United States row kept** as the page's own total (`afdc_reg:US`), never a sum the connector makes.
- **A count's date is its year's first day with freq P1Y,** the header saying it counts vehicles registered through the year's end.

## For Samuel's ruling

- **The counts come from Experian's commercial data.** DOE publishes them openly with no restriction on the page, and the table is flagged public on DOE's verdict. If a ruling holds that a DOE page republishing a vendor's derived counts needs the vendor's terms, the table is held internal by changing its line in `sources.csv`; reversible, nothing else depends on it.

## Files

- New: `warehouse/connectors/afdc_registrations.py`, `tests/test_session2036.py` (3 tests), this report.
- Changed: `build_coverage.py`, `release_v1.py`, `live_set.yaml`, `docs/coverage.md`, `coverage.csv`, `archive_manifest.csv`, `sources.csv`, `license_reads.csv` (194), `license_tables.csv`, `docs/licenses.md`, `docs/redivis/release-v1/`.
- On the data machine only: `runs/c058/s2036/`, `runs/license_reads/s2036/`, `runs/s2036*`, `warehouse/raw/afdc_registrations/`.
