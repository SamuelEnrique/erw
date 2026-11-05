# Fuel and electricity used by public transit, an agency, mode and type of service, a report year, 2022 to 2025 (the FTA's National Transit Database, Fuel and Energy)

Energy Research Warehouse (ERW), method note written in session 2185 (chain 097) for a table first written on 24 October 2026 (session 2182).

Tables: `ntd_transit_energy_annual`

## Publisher and address

U.S. Department of Transportation, Federal Transit Administration (FTA), National Transit Database (NTD), the dataset "2022 - 2025 NTD Annual Data - Fuel and Energy" on DOT DataHub (`https://data.transportation.gov/d/8ehq-7his`), read as one CSV:

`https://data.transportation.gov/api/views/8ehq-7his/rows.csv?accessType=DOWNLOAD`

The User-Agent is "Mozilla/5.0 (compatible; ERW-connector/0.1; +https://github.com/SamuelEnrique/erw)". Source id `fta:ntd_fuel_energy`. Connector: `warehouse/connectors/ntd_transit_energy.py` (session 2182), its only table. data.transportation.gov's robots file (read 370) asks a crawl delay of 1 second and disallows browse and facet searches, OData and login paths, not `/api/views/` or `/data.json`. The dataset was found in DOT DataHub's `data.json` (read 374), whose record for it gives the license.

The table is not scheduled: no line of `warehouse/run_daily.sh`, the other `warehouse/*.sh` scripts, `warehouse/scheduled.py`, `scripts/` or `.github/workflows/` names the connector (searched in session 2185), and `run_status.csv` holds no row for it. It was written once, by run `20261024T015626Z` on the data machine, offline from the saved CSV.

## Vintage and revision

Report years 2022 to 2025 (`ts_utc` the year's first day). The CSV was retrieved at 2026-10-24T01:54:08Z by the session's probe, after the dataset's metadata (01:54:05Z), and the write read that copy. Its Last-Modified time, 2026-10-14T15:08:39Z, is every row's `vintage`. `coverage.csv` gives the same 10,161 rows and the same first and last `ts_utc`; its count of 1,751 nodes is the count of `node` names, not of entities (below).

Each run writes the whole table again (`ip.write_snapshot`), and the CSV is asked again unless `--offline`, since the FTA revises it at the same address. The dataset's name gives its years; a later year in the same dataset enters on the next run, and a dataset at a new address needs a code change.

## Shape and variables

Series, 10,161 rows, 1,425 entities (agency, mode and type of service), 553 agencies, 9 variables. `entity` `ntd_mode:<NTD ID>:<mode code>:<type of service code>`; `ts_utc` the report year's first day at 00:00 UTC; `freq` P1Y; `geo` US-<state of the agency's headquarters> (51 values: 49 states, DC and PR); `market` empty; `node` "<agency>: <mode name> (<type of service>)" as the FTA names them.

| `variable` | Unit | Rows | Entities | The FTA's column |
|---|---|---|---|---|
| electric_battery | MWh | 3,000 | 1,358 | Electric Battery (kWh), divided by 1,000 |
| gasoline | gal | 2,862 | 843 | Gasoline (gal) |
| diesel | gal | 2,236 | 662 | Diesel (gal) |
| cng_gal_equivalent | gal | 832 | 232 | Compressed Natural Gas (gal equivalent) |
| biodiesel | gal | 571 | 333 | Bio-Diesel (gal) |
| electric_propulsion | MWh | 359 | 94 | Electric Propulsion (kWh), divided by 1,000 |
| lpg_gal_equivalent | gal | 222 | 66 | Liquefied Petroleum Gas (gal equivalent) |
| hydrogen | t | 43 | 17 | Hydrogen (kg), divided by 1,000 |
| other_fuel | gal | 36 | 20 | Other Fuel (gal/gal equivalent) |

Electric propulsion is electricity fed to vehicles by third rail or overhead wire; electric battery is electricity charged into vehicles' batteries (the docstring's words). LPG and CNG are in the FTA's gallon equivalents, named so in the variable.

- `x_ntd_id`; `x_agency` (696 names for 553 agencies: an agency's name can differ between years, so 285 entities carry two or three `node` names); `x_city` (blank for four agencies); `x_mode` (MB 4,445 rows, DR 3,542, CB 587, VP 543, FB 209, CR 206, SR 151, LR 138, RB 105, HR 94, YR 37, MG 36, TB 26, IP 18, TR 6, AR 6, PB 6, CC 6); `x_tos` (DO 5,771, PT 4,325, TX 54, TN 11); `x_uza` the urbanized area (302); `x_mode_voms` vehicles operated in maximum service (blank in 7 rows); `x_reporter_type` (Full Reporter 10,152, Reduced Reporter 9); `x_questionable` yes where the FTA marks the figure Questionable (no row in this run).

Rows by year: 2022 2,919, 2023 2,942, 2024 2,128, 2025 2,172; agencies 527, 521, 523 and 522. The fall from 2023 to 2024 comes from electric_battery, which the FTA leaves blank where it wrote zero before: electric_battery has 1,267 rows in 2022 and 1,237 in 2023, of which 1,113 and 1,051 are zero, and 226 and 270 rows in 2024 and 2025, of which 4 and 14 are zero. Biodiesel goes the other way (66 and 73 rows, none zero, then 224 and 208, of which 160 and 162 are zero). 2,550 values are zero in all, as the FTA prints them; none is negative.

National totals (the cross-check's figures, which the rows give again): electric propulsion 5,499,279 MWh in 2022 to 6,666,445 in 2025; electric battery 48,864 to 112,167 MWh; diesel 415,900,196 to 437,927,889 gal; CNG 170,897,996 to 198,830,256 gal equivalents; hydrogen 246 to 570 t. No (entity, variable, ts_utc) is given twice. The counts were computed in session 2185 from the rows, read past the 10 header lines with pandas (every column as text).

## Checks the connector makes

- Before any request, the connector and data.transportation.gov are checked against `warehouse/metadata/paused_sources.csv`; a paused publisher stops the run with no request. It is not paused.
- The CSV must have 67 columns and hold the 33 the connector reads (15 identifying columns, from Agency to Mode VOMS, the 9 quantities and their 9 Questionable columns), or the run stops.
- A key (NTD ID, mode, type of service, report year) given twice stops the run, and so does a report year not of four digits, a state not two capital letters, a blank NTD ID, a quantity that does not read as a number or is negative, or a Questionable column holding anything but blank or "Questionable" beside a quantity taken.
- A blank quantity has no row; a zero the FTA prints is kept. Miles and miles per gallon are not taken (no unit for a distance in the standard; the ratios are the FTA's own arithmetic). Nothing is filled.
- Ceiling: one request a run, a pause of 1 second after it, as the robots file asks.

## The cross-check

Session 2182 set transit's electricity (electric_propulsion plus electric_battery) by state and year beside EIA's retail sales to the transportation sector (`eia_retail_sales_monthly`, entities ending `:TRA`, years of 12 months) in `runs/c097/s2182/cross.py` (on the data machine, not in git), reading the trial copy of the table. Over the 13 states whose transportation sales exceed 100 GWh in a year, the median ratio is 0.756. The ratios by state:

| State | 2022 | 2023 | 2024 | 2025 |
|---|---|---|---|---|
| NY | 0.829 | 0.970 | 0.980 | 0.975 |
| CA | 0.983 | 0.998 | 1.014 | 1.142 |
| IL | 0.960 | 0.973 | 0.940 | 0.871 |
| PA | 0.697 | 0.894 | 0.731 | 0.694 |
| NJ | | 1.172 | 1.103 | 1.131 |
| MD | 0.245 | 0.227 | 0.211 | 0.212 |
| DC | | | 2.019 | 1.966 |

The cross-check prints the 25 largest state years only, so the blanks above are years not printed. DC is about 2 and Maryland about 0.2 because the table places each agency at its headquarters' state: the Washington Metropolitan Area Transit Authority, in DC, draws power in Maryland and Virginia too.

## License

The header: "License: public (Public Domain U.S. Government, https://www.usa.gov/government-works; see license_verdicts.csv). Cite the Federal Transit Administration, National Transit Database." `license_verdicts.csv` gives the FTA "may be public", the same if the ERW sells anything (read 374, the license field of the dataset's record in DOT DataHub's catalog, `https://www.usa.gov/government-works`, as for the FHWA, read 214; recorded in session 2181). `coverage.csv`: public.

## Found while writing this note

- The docstring and the header say "Only Full Reporters report energy (the FTA's description)". The table holds 9 rows of Reduced Reporters, all of 2025: City of Burlington (Link Transit), First Tennessee Human Resource Agency, and the County of Kern.
- The docstring says the dataset's columns "must be the 67 read on 24 October 2026". The code checks that there are 67 columns and that the 33 it reads are among them; a renamed column it does not read would pass.
- The FTA leaves electric battery blank for most agency modes in 2024 and 2025 where it wrote zero in 2022 and 2023, so rows by year and zeros by year are not comparable (above).
- Session 2182's report found the FTA's "Compressed Natural Gas (mpg) Questionable" column holds numbers, not the word Questionable. That column is not taken; the connector stops only for the Questionable column of a quantity it takes.

Acted on in session 2185: the docstring and the header now say the 2025 file holds some Reduced Reporters and that electric battery's zeros of 2022 and 2023 are blanks from 2024; the docstring says what the column check checks. The table was written again (the same rows).

## What it does not hold

- Miles and miles per gallon.
- Agencies that report no fuel or energy (most Reduced Reporters), and demand response taxi, which the dataset does not hold.
- Report years before 2022, which this dataset does not hold.
- Where the energy is used: each agency is placed at its headquarters' state, not where its vehicles run.
