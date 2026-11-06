# Households' energy burden, energy costs and income by county, state and income bracket (DOE's Low-Income Energy Affordability Data, the LEAD Tool, 2022 update)

Energy Research Warehouse (ERW), method note written in session 2143 (chain 090) for a table first written on 24 October 2026 (session 2140).

Tables: `doe_lead_energy_burden`

## Publisher and address

U.S. Department of Energy, Office of State and Community Energy Programs, "Low-Income Energy Affordability Data - LEAD Tool - 2022 Update", submission 6219 of the Open Energy Data Initiative, `https://data.openei.org/submissions/6219`. The connector asks one zip a state at `https://data.openei.org/files/6219/<ST>-2022-LEAD-data.zip`, 52 of them (the 50 states, DC and Puerto Rico), and reads one file in each, `<ST> AMI Counties 2022.csv`. Source id `doe:lead_2022`. Connector: `warehouse/connectors/doe_lead.py` (session 2140), in two steps: `--pull` streams the zips to `warehouse/raw/doe_lead/files/` with a manifest, and `--write` builds the table from the saved zips only, under the data lock.

## Vintage and revision

The year the files name, 2022, for every row. The file on the data machine was written by run `20261024T002203Z` (24 October 2026). The 52 zips were pulled from 2026-10-23T23:59:10Z (Vermont, the trial) to 2026-10-24T00:10:31Z (Wyoming), each row's `retrieved_at` its state's time in the manifest; `vintage` is the same time, not the Last-Modified the manifest also records (22 October 2024, 21:48:13 to 23:05:05 GMT, for all 52). The manifest's 52 zips hold 7,841,647,083 bytes, from 18,069,292 (DC) to 912,720,159 (California): 7.84 GB, or 7.30 GiB. Session 2140's report says "7.4 GB" (lines 8, 9, 35 and 53), which is neither; it is what `du -h` prints for the folder.

A zip in the manifest is never asked again, so a revised file at the same address is not taken; each `--write` replaces the table whole from the saved zips (`iso_prices.write_snapshot`). No job runs the connector.

## Shape and variables

Series, 160,419 rows: 3,274 entities (3,222 counties and 52 states and territories), 49 variables, one year. `entity` doe_lead:<county FIPS> or doe_lead:<state>; `variable` <measure>:ami_<bracket>, seven measures by seven brackets; `unit` count (households), USD (the five cost and income averages, a year) or pct (energy_burden); `freq` P1Y; `ts_utc` 2022-01-01T00:00:00Z; `geo` US-<state>; `node` the county's name as LEAD writes it, or the state's code; `source_url` the state's zip. Extra columns: `x_level` county (157,871 rows) or state (2,548), `x_bracket` as LEAD writes it (0-30%, 30-60%, 60-80%, 80-100%, 100-150%, 150%+, or all), `x_fips`, `x_file` the CSV read.

The measures: households, the sum of LEAD's UNITS (weighted estimates, so not whole numbers: Vermont's are 265,857.97); income_avg, electricity_cost_avg, gas_cost_avg and other_fuel_cost_avg, each LEAD's value-times-units summed over the sum of its own units; energy_cost_avg the three cost averages added; energy_burden energy_cost_avg over income_avg, times 100. The burden is computed by the ERW from the averages; the header says so.

| Bracket (share of area median income) | Households | State burden, median of the 52 | Lowest | Highest among the states and DC | Puerto Rico |
|---|---|---|---|---|---|
| 0 to 30 percent | 16,559,857 | 18.96 | 9.70 (WA) | 26.38 (ME) | 44.70 |
| 30 to 60 | 21,172,747 | 6.98 | 3.78 (WA) | 10.85 (ME) | 12.27 |
| 60 to 80 | 13,511,780 | 4.60 | 2.71 (DC) | 7.20 (ME) | 8.64 |
| 80 to 100 | 12,803,578 | 3.59 | 1.89 (CA) | 5.76 (ME) | 6.89 |
| 100 to 150 | 27,965,436 | 2.65 | 1.18 (DC) | 4.16 (ME) | 5.28 |
| 150 and up | 35,438,363 | 1.50 | 0.69 (DC) | 2.40 (ME) | 2.60 |
| All households | 127,451,762 | 2.59 | 1.18 (DC) | 4.12 (ME) | 4.37 |

Percent of income. Households are summed over the 52 places. Puerto Rico's burden is the highest in every bracket.

Each county has 49 rows but one: Kenedy County, Texas, has no cell in the 0 to 30 percent bracket, so its 7 rows for that bracket are absent (the log's 19,331 county-bracket cells are the 3,222 counties' six brackets less that one). 23 values are 0, among them Kalawao County, Hawaii's electricity and energy cost in the lowest bracket. Counties a place: Texas 254, Georgia 159, Virginia 133; DC 1, Delaware 3, Hawaii 5; Puerto Rico 78, Alaska 30. Connecticut is held as its nine 2022 areas as LEAD writes them, eight named planning regions and code 9120 named "Hartford County".

The county FIPS is the code as LEAD writes it, without a leading zero: the 318 counties of the states coded 01 to 09 have four digits (`doe_lead:6075` is San Francisco County), the other 2,904 five. The docstring and the header say only "<county FIPS>". A join to a five-digit FIPS needs the zero put back.

## Reading the source

- `--pull` stops at once, asking nothing, while `doe_lead` is in `paused_sources.csv` or data.openei.org is a paused host, and asks the host's pause again before each zip. A state already in the manifest with HTTP 200 is not asked. At most `MAX_REQUESTS` (60) zips a pull, `PAUSE` (2) seconds between them, timeout 120 seconds, no retry.
- A zip not answered with HTTP 200 is logged and written in the manifest with its status, not saved. One answered is streamed in 1 MiB pieces to a `.part` file with its sha256; a length other than the Content-Length removes the `.part` and stops the pull; a whole file is renamed and its manifest row written after. This pull asked 52 zips in two runs (Vermont, then the other 51), all HTTP 200.
- `--write` asks nothing. It reads each saved zip of the manifest: a zip holding other than one `<ST> AMI Counties <YYYY>.csv` stops the write, and so do a row of another state, a bracket not one of the six, more than one state code in a file, files naming more than one year, no zip saved, or a county, bracket and measure given twice. The CSV is read in chunks of 200,000 rows, only the 14 columns of `COLS`, and summed to the county and bracket.
- A cell whose average has no households reporting it (a sum of units of 0, so not a number or infinite) is no row. A state whose zip is not saved is left out and named in the header (none). Nothing is filled. The code counts no row ceiling.

## License

Public. The submission's license is CC BY 4.0: the submission page (read 341 on this branch, session 2139, 24 October 2026) shows it, with the Open Energy Data Initiative's footer, "Content is available under Creative Commons Attribution 4.0 unless otherwise noted". The table is filed under the U.S. Department of Energy (DOE), whose verdict in `license_verdicts.csv` (read 54, `https://www.energy.gov/about-us/web-policies`) is "may be public", for public and for commercial use: "Government information at DOE websites is in the public domain. [...] Public domain information may be freely distributed and copied, but it is requested that in any subsequent use the Department of Energy be given appropriate acknowledgement." The header asks the citation "U.S. Department of Energy, Low-Income Energy Affordability Data (LEAD) Tool". `sources.csv` flags `doe:lead_2022` public; `license_tables.csv` lists the table under DOE.

The docstring (line 29) cites "read 261": the submission page as session 2108 (chain 069) read it, read 261 on main and, since this chain's merge with main, on the branch too. Session 2139 read the same page again as read 341. Before the merge, read 261 on the branch was kp.gfz-potsdam.de's robots file.

## Cross-checks (session 2143)

- The counts above were computed from the rows, read past the header lines. The file's rows are identical to the trial file `runs/c090/s2140/trial/doe_lead_energy_burden.csv` that session 2140's cross-check read.
- The table against itself: in every county and state the six brackets' households sum to the all-households row (within 0.0002), and each state's counties sum to the state (within 0.0002 for all households, 0.0006 for the lowest bracket). energy_cost_avg equals the three cost averages added, and energy_burden equals energy_cost_avg over income_avg times 100, in every cell (within the rounding to four places).
- Session 2140's check by hand of Vermont's cells (24.33 percent in the lowest bracket, 2.29 in the highest): the rows give 24.33 and 2.29.
- Session 2140's check against EIA's SEDS (`runs/c090/s2140/cross.out`, `eia_seds_residential_annual`, 2022, 51 places): SEDS's residential electricity spending over LEAD's households is a median 1.09 times LEAD's electricity average (0.911 in Hawaii to 1.249 in Maine), and all energy 1.038 times (0.859 to 1.289). SEDS's totals are EIA's estimates of what the sector bought, LEAD's averages come from households' answers, so the two are not expected to agree exactly.

## What it does not hold

- The census tract files, and the cuts by the federal poverty line, state median income and the low-income line (FPL, SMI and LLSI): the same households in other brackets.
- LEAD's cells by tenure, building age, building type and heating fuel, which are summed out.
- Any year but the one the 2022 update's files name, and any later update.
