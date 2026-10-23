# Light-duty vehicles registered by state and fuel type, a year (the Alternative Fuels Data Center's registration counts)

Energy Research Warehouse (ERW), method note written in session 2038 (chain 058) for a table first written on 23 October 2026 (session 2036).

Tables: `afdc_vehicle_registrations_annual`

## Publisher and address

U.S. Department of Energy (DOE), Alternative Fuels Data Center (AFDC), Vehicle Registration Counts by State (`https://afdc.energy.gov/vehicle-registration`, `PAGE`): the table the page prints for each year, read at `https://afdc.energy.gov/vehicle-registration?year=<year>` (`url_of`), 2016 to 2025 by default (`YEARS`, `--years`). AFDC's API is not asked: it needs a key the ERW does not hold. One request a year, a pause of 1 second after each, timeout 60 seconds, with the ERW's user agent (`UA`). Source id `doe:afdc_vehicle_registrations`. Connector: `warehouse/connectors/afdc_registrations.py` (session 2036).

The counts are derived by the National Laboratory of the Rockies (formerly NREL) from Experian Information Solutions' registration data, rounded to the closest 100 vehicles, and count the light-duty vehicles registered through the year's end (AFDC's words, in the docstring and header); the header adds that fuel types come from VINs, not aftermarket conversions.

## Vintage and revision

The file on the data machine was written by run `20261023T195027Z` (23 October 2026), as its header says, from the ten pages session 2036's trial saved and the write reused offline. `retrieved_at` one time a year, 2026-10-23T19:49:21Z (2016) to 19:49:33Z (2025). `vintage` is empty on every row: the pages send no Last-Modified.

Until session 2038 the pages were asked for without `fresh`, so a year's page already saved would have been reused; since session 2038 a run that is not `--offline` asks for each again (`fresh=not args.offline`), so a revision AFDC makes at the same address is read. Each run replaces the table whole (`ip.write_snapshot`). No age check is made.

## Shape and variables

Series, 6,240 rows: 52 entities, 12 variables, 624 series of 10 years each, 2016 to 2025.

- `entity` `afdc_reg:<state code>` for the 50 states and the District of Columbia, and `afdc_reg:US` for the page's own United States row; `geo` US-<state code>, or US.
- `variable` `registrations_<fuel>`, `node` the column's name as the page prints it: `ev` Electric (EV), `phev` Plug-In Hybrid Electric (PHEV), `hev` Hybrid Electric (HEV), `biodiesel` Biodiesel, `e85` Ethanol/Flex (E85), `cng` Compressed Natural Gas (CNG), `propane` Propane, `hydrogen` Hydrogen, `methanol` Methanol, `gasoline` Gasoline, `diesel` Diesel, `unknown_fuel` Unknown Fuel.
- unit `count`; every value is a multiple of 100, and 1,709 are 0.
- `ts_utc` the year's first day, the count being the vehicles registered through the year's end; `freq` P1Y; `market` empty.

The United States in 2025: gasoline 240,682,100; E85 19,561,100; hybrid 13,929,600; diesel 7,176,500; electric 5,689,100; biodiesel 3,375,000; plug-in hybrid 1,765,700; unknown fuel 1,616,900; CNG 23,200; hydrogen 16,600; propane 5,500; methanol 0 (it is 0 from 2021, 500 in 2016). The twelve sum to 293,841,300.

Electric vehicles in the United States: 2016 280,300, 2017 377,100, 2018 572,600, 2019 783,600, 2020 1,018,900, 2021 1,454,400, 2022 2,442,300, 2023 3,555,900, 2024 4,503,700, 2025 5,689,100. California: 141,500 in 2016, 1,256,600 in 2023, 1,843,100 in 2025 (0.324 of the United States).

## Reading the source

- The page's title must read "<year> Light-Duty Vehicle Registration Counts by State and Fuel Type" for the year asked, or the run stops.
- The page must hold exactly one table, whose first row is State followed by the twelve columns of `COLUMNS` in order, or the run stops.
- A place not in `PLACES` (the 50 states, DC and United States), a row with a cell more or fewer than the header, or a count that is not a whole number written in groups of three digits with commas stops the run.
- A year whose table does not hold 52 places stops the run; a place, fuel and year given twice stops it.
- The United States row is the page's own, never a sum the connector makes. Nothing is filled.
- Each request is tried up to 4 times (`iso_prices.with_retries`), waiting 5 seconds times the attempt number after each failure; HTTP 404 is a `SourceGap`, not retried; any answer but HTTP 200 is a failure.
- Ceiling: one request a year, ten for the default years. No row ceiling is set in the code.
- Any failure is recorded as a failure, and no file is written.
- The connector does not call `iso_prices.paused()`; DOE is not in `warehouse/metadata/paused_sources.csv`.

## License

Public. `sources.csv` has `public` for `doe:afdc_vehicle_registrations`; the header: "License: public (DOE; cite "U.S. Department of Energy, Alternative Fuels Data Center, with data from Experian Information Solutions")." `license_tables.csv` gives the table's publisher as U.S. Department of Energy (DOE), by the source registry. `license_verdicts.csv`, U.S. Department of Energy (DOE), read 54 (DOE's web policies, `https://www.energy.gov/about-us/web-policies`, read 19 October 2026): "Government information at DOE websites is in the public domain. [...] Public domain information may be freely distributed and copied, but it is requested that in any subsequent use the Department of Energy be given appropriate acknowledgement." Verdict: may be public, and may be public for commercial use. `license_verdicts.csv` has no row of AFDC's own.

Robots: read 215 (session 2036), `afdc.energy.gov`'s file, a comment and no rule.

Open for Samuel's ruling (session 2036): the counts come from Experian's commercial data, which DOE publishes openly; if a ruling holds that the vendor's terms are needed, the table is held internal by changing its line in `sources.csv`.

## Cross-checks (session 2038)

- The counts above were computed from the rows, read past the header lines; no (entity, variable, ts_utc) appears twice, and the United States electric vehicles a year equal the header's.
- The page's United States row equals its 50 states and DC summed in every year and fuel, 120 of 120, as session 2036 found.
- Session 2036 also compared 2023's electric vehicles with AFDC's Electric Vehicle Registrations by State workbook (data 10962, exact counts): each state within 50, as rounding to 100 allows (California 1,256,600 against 1,256,646), and the United States row 455 above the workbook's total. The workbook is not in the ERW and was not read again here.

## What it does not hold

- Years before 2016; `--years` asks for other years, one request each.
- Exact counts: every count is rounded to 100.
- Medium- and heavy-duty vehicles, and counts by county, make or model.
- Additions and removals within a year: a count is of the vehicles registered through the year's end.
