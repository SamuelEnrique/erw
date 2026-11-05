# Population of each US metropolitan area, whole and by state part (the Census Bureau's estimates, vintage 2025)

Energy Research Warehouse (ERW), method note written in session 2074 (chain 067) for a table first written on 6 October 2026 (session 129).

Tables: `census_metro_population`

## Publisher and address

U.S. Census Bureau, Population Estimates Program, Metropolitan and Micropolitan Statistical Areas Totals, vintage 2025 (`https://www.census.gov/data/tables/time-series/demo/popest/2020s-total-metro-and-micro-statistical-areas.html`), read from one file: `https://www2.census.gov/programs-surveys/popest/datasets/2020-2025/metro/totals/cbsa-est2025-alldata.csv` (every metropolitan and micropolitan area, its metropolitan divisions and its counties). Source id `census:popest_cbsa`. Connector: `warehouse/connectors/census_metro_population.py` (session 129), written to weight the grids' weather stations (`noaa_grid_weather_stations`, `docs/methods/demand_weather.md`). No scheduled job runs it.

## Vintage and revision

One run, `20261006T004024Z` (6 October 2026); every row's `retrieved_at` is 2026-10-06T00:36:54Z. The header records the file's Last-Modified as 26 March 2026 and "Rows in the file: 2,806 of the 5,000 ceiling". The file on the data machine was restored from the Redivis draft by `scripts/sync.py`, as its last header line says.

A run deletes the table and writes it again from the file (`os.remove` before `write_csv`), so a later vintage replaces this one whole. Values are the Bureau's, unchanged; nothing is revised by the ERW.

## Shape and variables

Series, 1,650 rows: 825 entities, two variables each. `entity` `census:cbsa:<code>` for a whole metropolitan statistical area (387) or `census:cbsa:<code>:<state FIPS>` for its part in one state (438); `variable` `population_base_2020` (the estimates base, `ts_utc` 2020-04-01T00:00:00Z) and `population_2025` (the estimate of 1 July 2025, `ts_utc` 2025-07-01T00:00:00Z); `unit` count; `freq` and `market` empty; `geo` US; `node` the Bureau's name for the area, one name per entity; `vintage` 2025. `x_state` and `x_counties` are filled on part rows only: the state's FIPS code and the number of the area's counties summed there (1 to 29; 1,186 counties in all).

Every area has at least one part: 344 areas lie in one state (their single part equals the whole) and 43 in more than one, up to four (Philadelphia-Camden-Wilmington, 37980). The parts reach 51 state codes, the District of Columbia included; no part is in Puerto Rico (72).

| | 1 April 2020 | 1 July 2025 |
|---|---|---|
| Sum of the 387 areas | 285,704,792 | 295,450,885 |
| Largest | New York-Newark-Jersey City, NY-NJ, 20,083,400 | the same, 20,112,448 |
| Smallest | Eagle Pass, TX, 57,887 | Carson City, NV, 58,571 |

From base to 2025 the median area grew 2.50 percent; the fastest was Myrtle Beach-Conway-North Myrtle Beach, SC (+21.80 percent) and the slowest Charleston, WV (-4.95 percent).

## Reading the source

- Rows are kept where `LSAD` is "Metropolitan Statistical Area"; micropolitan areas and metropolitan divisions are not written. A part by state sums the rows whose `LSAD` is "County or equivalent" and whose `CBSA` is the area's, grouped by the first two digits of `STCOU`.
- A file without the columns `CBSA`, `MDIV`, `STCOU`, `NAME`, `LSAD`, `ESTIMATESBASE2020` and `POPESTIMATE2025` stops the run. For each variable, an area whose counties do not add to the area's own figure stops the run.
- Ceiling: 5,000 rows, counted as the file's data rows. Before the first pull the size and the first 20,000 bytes are read and the rows estimated; an estimate over the ceiling is not pulled, and a file over it is not written. A file saved by an earlier run is read from `warehouse/raw/census_metro_population/`.

## License

`license_verdicts.csv` records the Census Bureau, read 17: "may be public", for public and for commercial use. The sentence is from the terms of the Bureau's API ("You may not use the Census Bureau name, or the like to imply endorsement ..."); its note says the population files are plain downloads that no page read restricts. `license_tables.csv` lists the table under the Census Bureau; `docs/licenses.md` gives it "may be public", flag public, ERW verdict public. The Bureau's citation page is quoted in `docs/methods/demand_weather.md`. Cite: U.S. Census Bureau, Population Division, Annual Estimates of the Resident Population for Metropolitan Statistical Areas, vintage 2025.

## Cross-checks (session 2074)

- The counts above were computed from the rows, read past the header lines. No (entity, variable, ts_utc) is given twice.
- The parts of each area sum to the area's row in all 774 area-variable pairs (387 areas, two variables).
- The 35 populations in `noaa_grid_weather_stations` (`population_base_2020`, by `x_cbsa`, New York's by its part 35620:36, 13,167,758) equal this table's in 35 of 35.

## What it does not hold

- Micropolitan areas, metropolitan divisions and counties as rows of their own: counties are summed into state parts only.
- The estimates of 1 July 2020 to 2024, the components of change, and any year before the 2020 base.
- Puerto Rico's areas.
