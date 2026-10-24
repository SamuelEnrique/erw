# Natural gas pipeline capacity at each state border, a year (EIA's U.S. State-to-State Capacity)

Energy Research Warehouse (ERW), method note written in session 2094 (chain 068) for a table first written on 23 October 2026 (session 2090).

Tables: `eia_state_to_state_capacity`

## Publisher and address

U.S. Energy Information Administration (EIA), U.S. State-to-State Capacity, the natural gas pipeline workbook linked under "Pipelines" on EIA's natural gas data page (`https://www.eia.gov/naturalgas/data.php`, `PAGE`). The connector reads the page, takes the newest link of the form `EIA-StatetoStateCapacity_<Mon><Year>.xlsx` (`newest`, by year and then month) and reads the workbook's sheet "Pipeline State2State Capacity" (`SHEET`). The table on the data machine is from `https://www.eia.gov/naturalgas/pipelines/EIA-StatetoStateCapacity_Jan2026.xlsx`, the January 2026 issue. Pauses of 1 second, timeouts of 60 seconds (the page) and 180 seconds (the workbook), with the ERW's user agent (`UA`). Source id `eia:state_to_state_capacity`. Connector: `warehouse/connectors/eia_state_to_state.py` (session 2090).

## Vintage and revision

The file on the data machine was written by run `20261023T212419Z` (23 October 2026), as its header says. `retrieved_at` is 2026-10-23T21:21:11Z and `vintage`, the workbook's Last-Modified, 2026-02-03T21:15:45Z, on all 19,311 rows.

Each run builds the table whole and replaces the file (`ip.write_snapshot`). The data page is asked for fresh on every run that is not offline, so a new issue is found by its link. The workbook is asked for without `fresh` (`ip.fetch_raw`): an issue already saved in `warehouse/raw/eia_state_to_state/` is reused, and a change EIA makes to a file under the same name is not read until that raw file is gone. No age check is made.

## Shape and variables

Series, 19,311 rows: 686 crossings, 33 years (1990, then 1994 to 2025; the sheet has no row for 1991 to 1993). Rows a year run from 544 (1994 to 1996) to 664 (2025). 529 crossings have a row in all 33 years; 8 have one row only. 173 pipelines are named, 171 of them in 2025.

- `entity` `eia_s2s:<pipeline>:<state from>:<county from>:<state to>:<county to>:<n>`, each part in lower case with underscores (`slug`; an empty part reads `none`). n is the row's place among the year's rows with the same pipeline, states and counties, as EIA lists them (`build`).
- `variable` `capacity`; `unit` bcf/d, EIA's MMcf a day over 1,000; `x_capacity_mmcfd` the figure as published. On every row `value` is `x_capacity_mmcfd` over 1,000 exactly. 1,327 rows are 0 (11 in 2025); none is negative. The largest is 5.118 bcf/d, Transcontinental Gas P L Co from Randolph County, Alabama to Heard County, Georgia, in 2025.
- `ts_utc` the year's first day; `freq` P1Y; `market` empty; `node` the pipeline as EIA names it.
- `geo` `US-<state to>` where the state to is a state or DC (49 codes). It is empty on 1,346 rows whose state to is not a state: Mexico 571, Gulf of America 289, Ontario 272, Saskatchewan 107, Quebec 33, British Columbia 33, New Brunswick 26, Manitoba 15.
- `x_region_from`, `x_region_to`, `x_state_from`, `x_county_from`, `x_state_to`, `x_county_to`, `x_notes` as printed. The regions are Canada, Gulf of America, Intra-regional, Mexico, Midwest, Mountain, Northeast, Pacific, South Central and Southeast; Intra-regional is a region to only (12,192 rows). The states from that are not states: Gulf of America 1,155 rows, Ontario 297, Gulf of America - Deepwater 289, British Columbia 198, Saskatchewan 165, Mexico 150, Alberta 99, Manitoba 99, Quebec 99, New Brunswick 33. `x_county_from` is empty on the 33 rows of North Baja Pipeline Co from California to La Paz County, Arizona. `x_notes` holds a note on 879 rows.
- One crossing stays within one state: Pacific Interstate Offshore Co from Offshore Pacific to Santa Barbara County, California (33 rows).

A row is a pipeline at one border in one year. A pipeline that crosses several borders has a row at each, so a sum over the crossings counts the same gas once a border; it is not the capacity of a pipeline or of the nation.

Repeats within a year are kept as EIA lists them: 12 rows carry an n above 1, on 5 crossings: Nat Gas P L Co of America from Miller County, Arkansas to Cass County, Texas (2018 to 2025), National Fuel Gas Supply Co from Steuben County, New York to Potter County, Pennsylvania (1997), Texas Eastern Trans Corp from Scioto County, Ohio to Greenup County, Kentucky (2015), and two Trunkline Gas Co crossings in 1990 (Obion County, Tennessee to Fulton County, Kentucky; Newton County, Texas to Beauregard, Louisiana). The two Trunkline pairs of 1990 are the same field for field; they are kept twice, as EIA's own pivot tables sum them.

## Reading the source

- No `EIA-StatetoStateCapacity_<Mon><Year>.xlsx` link on the data page stops the run (`newest`).
- The sheet's header is its second row (`header=1`); a sheet without the columns of `NEED` (year, Pipeline, Region From, Region To, State From, County From, State To, County To, Capacity (mmcfd), Notes) stops the run (`read`).
- A row with every column empty is passed over.
- A year that is not four digits beginning 19 or 20 stops the run; a capacity that is not a number once its commas are removed stops it. Nothing is filled.
- A crossing and year given twice stops the run; with n in the entity, a repeat EIA lists is not a duplicate.
- Each request is tried up to 4 times (`iso_prices.with_retries`), waiting 5 seconds times the attempt number after each failure; HTTP 404 is a `SourceGap`, not retried; any answer but HTTP 200 is a failure.
- Ceiling: two requests, the data page and the workbook. No row ceiling is set in the code.
- Any failure is recorded as a failure, and no file is written.
- The connector does not call `iso_prices.paused()`; EIA is not in `warehouse/metadata/paused_sources.csv`.

## License

Public: a work of the U.S. government. `sources.csv` has `public` for `eia:state_to_state_capacity`; the header: "License: public (EIA: "U.S. government publications are in the public domain"; cite "U.S. Energy Information Administration")." `license_verdicts.csv`, EIA, read 1 (EIA's copyrights and reuse page): "U.S. government publications are in the public domain and are not subject to copyright protection." Verdict: may be public, and may be public for commercial use; an acknowledgment is asked for.

Robots: the robots read of session 2090 found that `www.eia.gov`'s file disallows `/archive/` and site machinery, not `/naturalgas`.

## Cross-checks (session 2094)

- The counts above were computed from the rows, read past the header lines; they equal the header's (19,311 rows, 686 crossings, 1990 to 2025). No (entity, variable, ts_utc) appears twice.
- Session 2090 compared the capacity the table adds each year (each crossing's rise over the year before, rises only, summed over the crossings) with the capacity of the completed interstate projects in `eia_gas_pipeline_projects` that cross a state border, by year in service, 2015 to 2025. Recomputed here from the two tables: correlation 0.74; both highest in 2017 and 2018 (28,090 and 21,707 MMcf a day added, against 11,465 and 11,161 of projects) and lowest in 2022 and 2023 (897 against 897; 2,283 against 894). The border table adds more in the busy years, likely because a project counted once in the tracker raises the capacity at every border it crosses.
- The rows of 1990 sum to 271,847.5 MMcf a day and those of 2025 to 589,777, both counting a pipeline once a border.

## What it does not hold

- The years 1991 to 1993, which the sheet does not list.
- Capacity summed by state pair, state or region: EIA's other sheets of the workbook hold those, and a reader can sum the crossings.
- Flows: the table holds capacity, not the gas that moved.
- Pipeline projects, planned or completed: those are `eia_gas_pipeline_projects`.
