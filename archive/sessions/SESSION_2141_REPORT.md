# Session 2141 report: a source of the session's own choosing (AFDC's fueling station counts)

24 October 2026, from 00:05 UTC, on lab-desktop (the data machine), chain 090, unattended, beside session 2140's pull. Model spend USD 0. Pulls: 2 requests of 20 (the Counts by State page and the workbook; afdc.energy.gov's robots file was read in session 2036, read 215, and holds no rule).

## Read these first

- **Why this source:**
  - The ERW holds the electric vehicles registered in each state (`afdc_vehicle_registrations_annual`, chain 058) but not the chargers they draw power from.
  - The chargers are a load the grid sees directly.
  - No chain has planned them: not 092, 094 or 097, nor the sources earlier chains named.
- **Two sources considered first and dropped:**
  - BLS's consumer prices for electricity and piped gas. Session 941 found www.bls.gov refuses automated readers, and session 509 found api.bls.gov's robots file disallows every path; neither was asked again.
  - The CFTC's Commitments of Traders, already held (`cftc_cot_positions`).
- **A new table, `afdc_station_counts_annual`** (series, 13,520 rows, `power`): the Alternative Fuels Data Center's alternative fueling station counts by state and fuel, near the end of each December, 2007 to 2025. Public and private (non-residential) stations; 52 places (the states, DC and the sheet's Total row as the United States). Written, validated (0 errors, 0 warnings), archived, held from the Redivis storage and the live set, its release rows added. Public under DOE's verdict (read 54).
- **What the counts mean, as AFDC's About the Data sheet says:**
  - From 2014 the electric charging columns give locations, ports, and ports by Level 1, Level 2 and DC Fast, and hydrogen and propane come with their designations. In the sheets for 2007 to 2013 there is one number a fuel: the Electric column counts locations to 2010 and ports from 2011, and the table names them `ev_locations` and `ev_ports` accordingly.
  - Counts jump in 2021 as the charging networks' OCPI feeds were integrated.
  - The sheet's Total counts a station once for each fuel, and electric by ports. It is kept as published. In 24 place-years, all in the 2013 sheet, it does not equal the sum of the fuels (West Virginia 2013: 430 against 65), and the header counts them.
- **Cross-checks:**
  - In all 260 variable-years, the 51 states and DC sum exactly to the sheet's own Total row.
  - The United States' charging ports grow from 5,070 (2011) to 25,913 (2014), 107,395 (2020) and 271,488 (2025); 68,599 of 2025's are DC fast, at 85,692 locations.
  - EVs registered per port at the end of 2025 (`afdc_vehicle_registrations_annual`'s EV count over this table's ports): 21.0 for the United States, a median of 18.2 among the states. The highest are New Jersey 33.5, Hawaii 30.4 and Florida 29.3; the lowest Wyoming 5.3, North Dakota 6.7 and Maine 7.2.

## Requests (2 of 20)

| n | What | Outcome |
|---|---|---|
| 1 | afdc.energy.gov/stations/states | 200: the current counts, and the link to the historical workbook |
| 2 | afdc.energy.gov/files/docs/historical-station-counts.xlsx | 200, 170,217 bytes, last modified 23 June 2026 |

No license read was added: AFDC's publisher is DOE, whose verdict (read 54) stands, and the robots file was read in session 2036.

## Decisions made without you

- **AFDC's historical workbook, not its Station Locator API.** The API needs a key the ERW does not hold, and the workbook is the series AFDC itself publishes.
- **The two Electric meanings named apart**, as the About sheet defines them.
- **The Totals kept as published,** the uneven ones counted.

## For Samuel's ruling

- None new.

## Files

- New: `warehouse/connectors/afdc_stations.py`, `tests/test_session2141.py`, this report.
- Changed: `warehouse/metadata/build_coverage.py`, `warehouse/redivis/release_v1.py`, `warehouse/supabase/live_set.yaml`, `docs/coverage.md`, `warehouse/metadata/coverage.csv`, `warehouse/metadata/sources.csv`, `warehouse/metadata/archive_manifest.csv`, `docs/redivis/release-v1/`, the license record (rebuilt).
- On the data machine only: `runs/c090/s2141/`, `warehouse/raw/afdc_stations/`, `warehouse/output/afdc_station_counts_annual.csv`.
