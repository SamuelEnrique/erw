# Alternative fueling stations by state and fuel, near the end of each December from 2007 (AFDC's Historical Station Counts)

Energy Research Warehouse (ERW), method note written in session 2143 (chain 090) for a table first written on 24 October 2026 (session 2141).

Tables: `afdc_station_counts_annual`

## Publisher and address

U.S. Department of Energy (DOE), Alternative Fuels Data Center (AFDC), the historical counts workbook linked from its "Alternative Fueling Station Counts by State" page, `https://afdc.energy.gov/stations/states`. The connector reads one file, `https://afdc.energy.gov/files/docs/historical-station-counts.xlsx`: a sheet a year, 2025 back to 2007, and an "About the Data" sheet. Source id `doe:afdc_station_counts`. Connector: `warehouse/connectors/afdc_stations.py` (session 2141), one step: it asks, reads and writes in one run, or reads the saved workbook only with `--offline`. It takes the place names from `afdc_registrations.py` (`PLACES`).

The About sheet: the counts are "the number of public and private (non-residential) stations in the Alternative Fuels Data Center (AFDC) Alternative Fueling Station Locator ... near the end of December each year"; changes "represent both stations that opened and went out of service"; and "In 2021, there was a jump in EV charging station counts", as NREL moved its counting to the Open Charge Point Interface (OCPI) hierarchy of stations, ports and connectors.

## Vintage and revision

Years 2007 to 2025 in the file on the data machine, written by run `20261024T001741Z` (24 October 2026), offline, from the workbook session 2141 saved (170,217 bytes): every row's `retrieved_at` is 2026-10-24T00:06:25Z and its `vintage` 2026-06-23T22:12:10Z, the workbook's Last-Modified. A year's count is as of late December of that year, and `ts_utc` is that year's 1 January: the row for 2025-01-01 is the count near the end of December 2025. AFDC replaces the workbook at its address each year (the docstring), so the connector asks it fresh, and each run replaces the table whole (`iso_prices.write_snapshot`). No job runs the connector, so the 2026 count is not taken until it is run after AFDC adds that sheet.

## Shape and variables

Series, 13,520 rows: 52 places (the 50 states, DC, and `afdc_st:US` for each sheet's own Total row), 19 years, 260 variable-years a place. `entity` afdc_st:<state code>; `unit` count; `freq` P1Y; `geo` US-<state> or US; `node` the column as the sheet prints it; `x_layout` the sheet's form, 2007_2013 (2,912 rows, 8 variables a year) or 2014_on (10,608 rows, 17 variables a year).

- 2007 to 2013, one number a fuel: stations_biodiesel, stations_cng, stations_e85, stations_hydrogen, stations_lng, stations_propane, stations_total, and the Electric column, written as ev_locations for 2007 to 2010 and as ev_ports for 2011 to 2013. The About sheet: "From 2007 through 2010, the 'Electric' data represent the number of station locations (i.e., unique physical places). From 2011 through 2013, the 'Electric' data represent the number of charging outlets (ports)".
- 2014 on: those fuels and stations_renewable_diesel, ev_locations and ev_ports, ports by level (ev_ports_level1, ev_ports_level2, ev_ports_dc_fast), hydrogen as stations_hydrogen_retail, stations_hydrogen_non_retail and stations_hydrogen, and propane as stations_propane_primary, stations_propane_secondary and stations_propane.

| Year | EV locations | EV ports | DC fast ports | E85 | CNG | Propane | Hydrogen | Biodiesel | Total |
|---|---|---|---|---|---|---|---|---|---|
| 2007 | 432 | | | 1,325 | 731 | 2,331 | 33 | 805 | 5,692 |
| 2010 | 626 | | | 2,296 | 869 | 2,604 | 58 | 615 | 7,111 |
| 2011 | | 5,070 | | 2,494 | 941 | 2,551 | 56 | 633 | 11,788 |
| 2013 | | 19,472 | | 2,616 | 1,290 | 2,967 | 53 | 832 | 27,314 |
| 2014 | 10,957 | 25,913 | 1,494 | 2,839 | 1,496 | 2,929 | 51 | 782 | 34,113 |
| 2020 | 31,751 | 107,395 | 17,539 | 3,946 | 1,546 | 2,966 | 63 | 712 | 116,734 |
| 2021 | 50,097 | 128,703 | 21,945 | 4,351 | 1,510 | 2,806 | 67 | 706 | 138,246 |
| 2025 | 85,692 | 271,488 | 68,599 | 5,100 | 1,385 | 2,995 | 78 | 1,645 | 284,265 |

The United States (the Total row), near the end of December of each year. A blank is a count the sheet's form does not give. Renewable diesel is 0 from 2014 to 2022, then 606, 655 and 1,493. At the end of 2025 California holds 74,599 ports (17,344 DC fast), New York 20,363 and Florida 15,377; Alaska the fewest, 213.

`stations_total` is kept as published. The sheet's note (d): "Individual stations count multiple times if the station offers more than one fuel type. For electric, the total includes EVSE ports rather than station locations." From 2014 on it equals the fuels summed with ev_ports in all 624 place-years. In the earlier sheets it does not in 24 place-years, and all 24 are in the 2013 sheet (West Virginia: 430 against 65; Alabama: 10 against 197); the sheets for 2007 to 2012 have none. The docstring (line 27), the header and session 2141's report (line 18) place them in "2007 to 2013"; the count is right, the years are 2013 alone. The 2013 Total row itself equals its fuels summed (27,314).

## Reading the source

- The run stops at once, asking nothing, while `afdc_stations` is in `paused_sources.csv` or afdc.energy.gov is a paused host.
- The workbook goes through `iso_prices.fetch_raw`, asked fresh unless `--offline` (then only the saved copy is read). A request not answered with HTTP 200 is tried up to four times (`iso_prices.with_retries`, the waits 5, 10 and 15 seconds); HTTP 404 is not retried. Timeout 60 seconds; 1 second after the request. One document a run.
- Only sheets named by a four-digit year are read; no such sheet, or a year's sheet given twice, stops the run. Each sheet must have exactly one row whose first cell is "State". A header equal to `NEW_HEAD` is read as the 2014 form: from the third row after it, a place row and the row under it (the levels), skipping empty rows and rows that begin with "(" (the notes). Any other header must give `OLD_HEAD` (a column's name taken from two rows below where the header cell is empty), else the run stops; its rows are read until the first that begins with "(".
- A place must be "Total" (written as US) or a name in `afdc_registrations.PLACES`, else the run stops. A count must be a whole number, commas allowed, and a pair or triple must have two or three parts ("659 | 2,119"), else the run stops. A count given twice stops the run. Nothing is filled. The code counts no row ceiling.

## License

Public. `license_verdicts.csv` records the U.S. Department of Energy (DOE), read 54 (`https://www.energy.gov/about-us/web-policies`, 19 October 2026): "may be public", for public and for commercial use. The sentence: "Government information at DOE websites is in the public domain. [...] Public domain information may be freely distributed and copied, but it is requested that in any subsequent use the Department of Energy be given appropriate acknowledgement." afdc.energy.gov's robots file holds a comment and no rule (read 215, session 2036). `sources.csv` flags `doe:afdc_station_counts` public; `license_tables.csv` lists the table under DOE.

## Cross-checks (session 2143)

- The counts above were computed from the rows, read past the header lines. The file's rows are identical to the trial file `runs/c090/s2141/trial/afdc_station_counts_annual.csv` that session 2141's cross-check read. In all 260 variable-years the 50 states and DC sum exactly to the sheet's Total row, as session 2141 found.
- From 2014 on, hydrogen's retail and non-retail and propane's primary and secondary sum to their totals in all 624 place-years. A place's Level 1, Level 2 and DC fast ports do not sum to its ports in 44: the Total row in every year from 2014 to 2025, and 32 state-years (California every year from 2017, ports 79 above the levels in 2017; Georgia 2016, 1,493 ports against 2,892 by level). Both are kept as AFDC prints them.
- Against `afdc_ev_charging_state_annual` (session 2155, the same workbook read by another connector): its 3,060 state values of EV stations, ports and ports by level, 2014 to 2025, equal this table's ev_locations, ev_ports and ports by level in all 3,060. That table lists the same 32 state-years whose levels do not sum to their ports.
- EVs registered at the end of 2025 (`afdc_vehicle_registrations_annual`) over this table's ports: 21.0 for the United States, a median of 18.2 among the states and DC, as session 2141 found (`runs/c090/s2141/cross.out`).

## What it does not hold

- Residential chargers, which the counts leave out.
- Puerto Rico and the territories: the sheets name the states and DC only.
- A station's place, network or opening date: the Station Locator's API, which needs a key the ERW does not hold, was not used (session 2141).
- The count near the end of December 2026, until AFDC adds it and the connector is run again.
