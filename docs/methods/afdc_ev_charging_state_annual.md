# Public and private electric vehicle charging stations and ports by state, near the end of each December (DOE, Alternative Fuels Data Center, historical station counts)

Energy Research Warehouse (ERW), method note written in session 2157 (chain 092) for a table first written on 24 October 2026 (session 2155).

Tables: `afdc_ev_charging_state_annual`

## Publisher and address

U.S. Department of Energy (DOE), Alternative Fuels Data Center (AFDC), the workbook "Historical Alternative Fueling Station Counts". The connector reads the station counts by state page,

`https://afdc.energy.gov/stations/states`

and takes from it the one link to the workbook, which was, for the run of 24 October 2026,

`https://afdc.energy.gov/files/docs/historical-station-counts.xlsx`

The workbook holds an "About the Data" sheet and one sheet a year from 2007 to 2025; the EV columns with ports by level begin in 2014, and the connector takes 2014 on. The User-Agent is "Mozilla/5.0 (compatible; ERW-connector/0.1; +https://github.com/SamuelEnrique/erw)". Source id `afdc:historical_station_counts`. Connector: `warehouse/connectors/afdc_ev_charging.py` (session 2155, a source of the session's choosing: public charging as a new and growing load), its only table. afdc.energy.gov's robots file holds no rule. Session 2155's report: 9 requests of 20.

The table is not scheduled: no line of `warehouse/run_daily.sh`, the other `warehouse/*.sh` scripts, `scripts/` or `.github/workflows/` names the connector (searched in session 2157), and `run_status.csv` holds no row for it. It was written once, by run `20261024T000246Z` on the data machine.

## Vintage and revision

2014 to 2025 (`ts_utc` 1 January of each year, for counts taken near the end of that year's December). The page and the workbook were retrieved at 2026-10-24T00:01:45Z and 00:01:46Z by the session's last trial and reused by the write run; the rows' `vintage`, the workbook's Last-Modified, is 2026-06-23T22:12:10Z. `coverage.csv` gives the same 3,060 rows, 51 entities and the same first and last `ts_utc`.

Each run writes the whole table again (`ip.write_snapshot`), and both requests are asked again unless `--offline`, since AFDC adds a year at the same address. AFDC's notes, in the header: legacy chargers are included and residential charging is not; changes are openings net of closures; in 2021 NREL moved to the OCPI hierarchy, so from then an outlet is a port (vehicles that can charge at once), where before it was a connector, and 2021's jump is partly the new counting.

## Shape and variables

Series, 3,060 rows: the 50 states and DC, five variables, twelve years, every cell present. `entity` `afdc_ev:<postal code, lower case>`; `unit` count; `freq` P1Y; `geo` US-<state>; `market` empty; `node` the state as AFDC names it; `x_counted_at` "near the end of December <year>" (AFDC's words in its About sheet).

| Variable | Rows | Mean a state-year | Zeros | Lowest | Highest |
|---|---|---|---|---|---|
| `ev_stations` | 612 | 780.7 | 0 | 1 (Alaska, 2014) | 20,627 (California, 2025) |
| `ev_ports` | 612 | 2,227.7 | 0 | 1 (Alaska, 2014) | 74,599 (California, 2025) |
| `ev_level1_ports` | 612 | 61.4 | 35 | 0 | 1,029 (California, 2016) |
| `ev_level2_ports` | 612 | 1,738.9 | 1 | 0 (Montana, 2014) | 56,451 (California, 2025) |
| `ev_dcfast_ports` | 612 | 428.9 | 20 | 0 | 17,344 (California, 2025) |

Summed over the states and DC (equal to AFDC's Total rows, which the connector checks):

| Year | Stations | Ports | Level 1 | Level 2 | DC fast |
|---|---|---|---|---|---|
| 2014 | 10,957 | 25,913 | 3,781 | 20,636 | 1,494 |
| 2015 | 14,119 | 34,289 | 3,511 | 27,320 | 3,456 |
| 2016 | 17,782 | 44,299 | 3,704 | 37,230 | 4,764 |
| 2017 | 19,940 | 52,337 | 3,254 | 43,599 | 5,400 |
| 2018 | 22,845 | 64,106 | 2,577 | 52,148 | 9,279 |
| 2019 | 26,968 | 85,253 | 2,737 | 69,921 | 12,511 |
| 2020 | 31,751 | 107,395 | 2,611 | 87,189 | 17,539 |
| 2021 | 50,097 | 128,703 | 3,379 | 103,325 | 21,945 |
| 2022 | 53,568 | 144,227 | 3,007 | 113,013 | 28,165 |
| 2023 | 64,315 | 176,032 | 2,972 | 135,112 | 37,920 |
| 2024 | 79,763 | 229,320 | 3,017 | 174,883 | 51,393 |
| 2025 | 85,692 | 271,488 | 3,032 | 199,833 | 68,599 |

In 32 state-years a state's three levels do not sum to its ports, as AFDC prints them: one a year from 2014 to 2016 (Montana 2014, 8 of 10; Montana 2015, 43 of 45; Georgia 2016, 2,892 against 1,493 ports, the levels exceeding the ports), four in 2017 and 2018 and three a year from 2019 to 2025 (California, Connecticut and Michigan, short by 1 to 90 ports; Hawaii in 2017 and 2018). The header lists each; both figures are kept. The counts were computed in session 2157 from the rows, read past the 10 header lines; no (entity, variable, ts_utc) is given twice.

## Checks the connector makes

- Before any request, afdc.energy.gov is checked against `warehouse/metadata/paused_sources.csv` by connector and by host; a paused publisher stops the run with no request. It is not paused.
- The page must link exactly one `historical-station-counts` workbook. The workbook's year sheets from 2014 must run without a gap.
- Each year's sheet must hold the header read ("State" in the first column, the EV column headed "(stations / charging outlets"), and two lines a state: stations and ports, then the Level 1, Level 2 and DC fast ports. A cell that does not read as "a | b" or "a | b | c" of whole numbers, a state not in the map, a state given twice, a state missing or no Total row stops the run, and nothing is written.
- The states and DC must sum to the sheet's Total row in every column, the three levels included (the Total row has its levels line in every year 2014 to 2025, read from the saved workbook in session 2157); the Total row is checked and not kept.
- Where a state's levels do not sum to its ports, both are kept as printed and the header lists each. Other fuels are not taken. Nothing is filled.
- Ceiling: two requests a run (the page and the workbook), by the code's shape rather than a counter, both asked again unless `--offline`. Each address is tried up to four times, 5, 10 and 15 seconds apart (`ip.with_retries`); an HTTP 404 is not retried. One second after each request.

## The cross-check

Session 2155 set each state's ports against its registered EVs (`afdc_vehicle_registrations_annual`), 510 state-years from 2016 to 2025, in `runs/c092/s2155/cross.py` (on the data machine, not in git): Pearson 0.96. Nationally, EVs a port rose from 6.3 (2016) to 21.0 (2025); among the largest EV states New York has the fewest EVs a port (10.3) and New Jersey the most (33.5).

## License

The header: 'License: public (DOE; cite "U.S. Department of Energy, Alternative Fuels Data Center, Station Locator").' `license_verdicts.csv` gives the U.S. Department of Energy (DOE) "may be public" (read 54, the Department's notice that government information on its websites is in the public domain, with acknowledgement asked; the same if the ERW sells anything): AFDC's pages link DOE's web policies and name no terms of their own, as for `afdc_vehicle_registrations_annual`. `docs/licenses.md` gives the ERW verdict public; `sources.csv` and `coverage.csv`: public. The publisher is named in `sources.csv` as in the registrations' row so the verdict applies (session 2155). Session 2155's report holds the table in the live set's catalogue hold and the release's storage hold, with the release package's rows.

## Found while writing this note

- Nothing: the docstring, the header lines, the code and the rows agree. The header's list of 32 unequal levels matches the rows.

## What it does not hold

- Residential charging, and the workbook's other fuels (biodiesel, CNG, E85, hydrogen and the rest).
- Years before 2014, which have no EV detail by level.
- Station locations, networks or connector types: counts by state only.
