# RINs generated and renewable fuel produced under the Renewable Fuel Standard, a month by D code and a year by D code and fuel (EPA's EMTS data)

Energy Research Warehouse (ERW), method note written in session 2038 (chain 058) for tables first written on 23 October 2026 (session 2030).

Tables: `epa_rfs_rins_monthly`, `epa_rfs_fuel_annual`

## Publisher and address

U.S. Environmental Protection Agency (EPA), Public Data for the Renewable Fuel Standard (`https://www.epa.gov/fuels-registration-reporting-and-compliance-help/public-data-renewable-fuel-standard`, `PAGE`), the "Historical Monthly Data" CSV files drawn from the EPA Moderated Transaction System (EMTS). Two listing pages (`LISTS`), each linking one file a month:

- RIN generation and renewable fuel volume production by month: `.../spreadsheet-rin-generation-and-renewable-fuel`, files `rindata_<mon><year>.csv` (columns FUEL_CODE, RIN_YEAR, Production Month, RIN_QUANTITY, BATCH_VOLUME).
- The same by fuel type: `.../spreadsheet-rin-generation-and-renewable-fuel-0`, files `fuelproduction_<mon><year>.csv` (RIN Year, Fuel, Fuel Code, Fuel Category, Fuel Category Code, RIN Quantity, Batch Volume).

A run reads each listing page and takes the newest `<stem>_<mon><year>.csv` it links (`newest`). The files read: `https://www.epa.gov/system/files/other-files/2026-10/rindata_sep2026.csv` and `.../fuelproduction_sep2026.csv`. Four requests a run, a pause of 1 second after each, timeouts 60 seconds (pages) and 120 seconds (files), with the ERW's user agent (`UA`). EPA's bulk file API is not asked (it needs a key). Source id `epa:rfs_emts`. Connector: `warehouse/connectors/epa_rfs_rins.py` (session 2030).

## Vintage and revision

Both files on the data machine were written by run `20261023T184631Z` (23 October 2026), as their headers say. `retrieved_at` 2026-10-23T18:42:34Z (monthly) and 2026-10-23T18:42:32Z (annual); `vintage`, the files' Last-Modified, 2026-10-14T21:35:00Z and 2026-10-14T21:34:41Z. Both files run through September 2026.

EPA issues each file again every month with the whole history, and its figures change when reports are corrected. The listing pages are read fresh on every run that is not `--offline`, so a new month's file, which has a new name, is fetched; a file whose address is already saved in `warehouse/raw/epa_rfs_rins/` is reused (`ip.fetch_raw` without `fresh`). Each run replaces both tables whole (`ip.write_snapshot`). The latest year is partial, to the month the file names. No age check is made.

## Shape and variables

`epa_rfs_rins_monthly`: series, 1,632 rows, 5 entities, 10 series (816 rows each of `rins_generated` and `batch_volume`), July 2010 to September 2026.

| Entity | `node` (the fuel type file's name) | Months | First, last |
|---|---|---|---|
| `epa_rfs:d3` | Cellulosic Biofuel | 158 | 2012-04, 2026-09 |
| `epa_rfs:d4` | Biomass-Based Diesel | 195 | 2010-07, 2026-09 |
| `epa_rfs:d5` | Advanced Biofuel | 195 | 2010-07, 2026-09 |
| `epa_rfs:d6` | Renewable Fuel | 195 | 2010-07, 2026-09 |
| `epa_rfs:d7` | Cellulosic Diesel | 73 | 2012-11, 2026-01 |

D4, D5 and D6 have every month of their span; D3 has 158 of its 174 months and D7 73 of its 159. A month EPA does not list has no row.

`epa_rfs_fuel_annual`: series, 568 rows, 32 entities (fuels), 64 series (284 rows each of the two variables), RIN years 2010 to 2026. `entity` `epa_rfs:d<code>:<EPA's fuel category code>`; `node` and `x_fuel_category` the fuel category as EPA names it; `x_d_code_name` the D code's name. Fuels by D code: D3 6, D4 7, D5 11, D6 6, D7 2. Rows a year run from 18 (2010) to 44 (2024); 2026 has 32.

Both tables: `rins_generated` unit `count` (RINs); `batch_volume` unit `gal`, the renewable fuel's volume in gallons (Decision 59 of `docs/datastandard.md`, added by session 2030); `ts_utc` the month's or the RIN year's first day; `freq` P1M or P1Y; `geo` US; `market` empty. No value is negative or zero.

## Reading the source

- No `<stem>_<mon><year>.csv` link on a listing page stops the run.
- A file without its columns (`COLS`) stops the run.
- Every column but Fuel and Fuel Category must be a whole number (commas allowed), or the run stops. Rows that are empty in every column are passed over.
- The D codes' names come from the fuel type file (`d_names`): a D code given two names stops the run, and a D code in the monthly file that the fuel type file does not name stops it.
- A production month outside 1 to 12 stops the run; an (entity, variable, ts_utc) given twice in either table stops it.
- A month or a fuel EPA does not list has no row; nothing is filled.
- Each request is tried up to 4 times (`iso_prices.with_retries`), waiting 5 seconds times the attempt number after each failure; HTTP 404 is a `SourceGap`, not retried; any answer but HTTP 200 is a failure.
- Ceiling: four requests (two listing pages, two files). No row ceiling is set in the code.
- A failure is recorded for both tables, and neither file is written.
- The connector does not call `iso_prices.paused()`; EPA is not in `warehouse/metadata/paused_sources.csv`.

## License

Public. `sources.csv` has `public` for `epa:rfs_emts`, naming both tables; the headers: "License: public (EPA: the agency's information is in the public domain unless noted; cite "U.S. EPA, Renewable Fuel Standard, EMTS data")." `license_verdicts.csv`, EPA, read 55 (EPA's disclaimers page, `https://www.epa.gov/web-policies-and-procedures/epa-disclaimers`, read 19 October 2026): "Unless otherwise specified, geospatial data produced by the EPA is by default in the public domain and is not subject to domestic copyright protection under 17 U.S.C." Its note: "The same page: EPA's documents may be freely distributed and used for non-commercial, scientific and educational purposes." Verdict: may be public, and may be public for commercial use.

Robots: read 205 (session 2030), `www.epa.gov`'s file, which disallows only site machinery, admin, user and search paths.

## Cross-checks (session 2038)

- The counts above were computed from the rows, read past the header lines; no (entity, variable, ts_utc) appears twice in either table.
- The two files agree: for every D code, year and variable (162 pairs), the monthly rows summed to the year equal the annual rows summed over fuels, exactly.
- Session 2030's cross-check, recomputed: D6 `batch_volume` summed to the year, against `eia_oxygenate_production_monthly`'s U.S. fuel ethanol plant production (`M_EPOOXE_YOP_NUS_1`, thousand barrels at 42 gallons), is 0.918 to 0.997 of EIA's from 2011 to 2024 (2011 0.977, 2015 0.991, 2020 0.928, 2024 0.918) and 0.888 in 2025. D6 counts only the fuel that generated a RIN; the session's reason for the gap (exported ethanol generates none) was not tested.
- RINs a gallon, a month: D6 1.000 to 1.016, D4 1.500 to 1.648, D5 1.005 to 1.546, D3 1.000 to 1.500, D7 1.000 to 1.700. In 2025, D4's 4.36 billion gallons generated 7.13 billion RINs.

## What it does not hold

- A month by fuel: the monthly file has no fuel, and the fuel type file has no month.
- RINs separated, retired or traded, prices of RINs, and the obligations: only generation is read.
- Generation by producer, plant or state.
- EPA's interactive dashboards (`edap.epa.gov`), not asked.
- Plant production of ethanol: `eia_oxygenate_production_monthly`; the plants' capacity: `eia_biofuel_plants`.
