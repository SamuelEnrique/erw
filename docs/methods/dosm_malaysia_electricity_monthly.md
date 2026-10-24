# Malaysia's electricity supply and consumption a month, January 2018 to June 2026: supply from public and private installations and imports, consumption by sector, exports and losses (DOSM, data.gov.my)

Energy Research Warehouse (ERW), method note written in session 2326 (chain 108) for a table first written on 24 October 2026 (session 2322 of chain 108, its report `archive/sessions/SESSION_2322_REPORT.md`).

Tables: `dosm_malaysia_electricity_monthly`

## Publisher and address

Department of Statistics Malaysia (DOSM), two datasets of the national open data portal's catalogue: Monthly Electricity Supply (`https://data.gov.my/data-catalogue/electricity_supply`, read 551) and Monthly Electricity Consumption (`https://data.gov.my/data-catalogue/electricity_consumption`, read 553). The table reads each dataset's CSV, one request a file:

- `https://storage.data.gov.my/energy/electricity_supply.csv` (columns `date,sector,supply`)
- `https://storage.data.gov.my/energy/electricity_consumption.csv` (columns `date,sector,consumption`)

Source id `dosm:electricity_supply_consumption`. Both pages say "Data as of 30 Jun 2026, 23:59" and "Last updated: 08 Oct 2026, 12:00", "Next update: N/A". Their "How is this data produced?" says the grid is managed by Tenaga Nasional Berhad (Peninsular Malaysia), Sabah Electricity Sdn. Bhd. and Sarawak Energy Berhad, that "Independent power producers also supply electricity", and that the dataset is "compiled from the operational records of these providers". The pages' "Data source(s)" lists those three, the Energy Commission of Malaysia and DOSM. The value is defined as "Amount of electricity supplied [consumed] in millions of kilowatt-hours (MKWh)". The consumption page defines the sectors: "Commercial usage includes the industrial and mining sectors, while domestic usage includes public lighting."

Each file is a small UTF-8 CSV, 612 data lines (102 months, six sectors), values printed with 1 to 20 decimal places of GWh in the supply file and 1 to 14 in the consumption file (the supply file's first line: `2018-01-01,total,13156.104056110958`). Session 2322's probe (`runs/c108/s2322/probe.csv`) made 8 requests: the robots files of data.gov.my (HTTP 200, 114 bytes, read 548), api.data.gov.my (HTTP 404, read 549) and storage.data.gov.my (HTTP 404, read 552), the address `https://data.gov.my/terms-of-use` (HTTP 404, read 550), the two dataset pages, and the two files (HTTP 200, 22,768 and 22,875 bytes, at 2026-10-24T06:31:10Z and 06:31:11Z, Last-Modified "Wed, 07 Oct 2026 16:10:05 GMT" and "16:10:06 GMT"). All eight are saved in `runs/license_reads/s2322/`; the two files were seeded into `warehouse/raw/dosm_malaysia_electricity/20261024T063043Z_probe/`, and the trial and both writes read them offline.

Connector: `warehouse/connectors/dosm_malaysia_electricity.py` (session 2322; its license word changed by session 2323): `[--offline] [--out-dir DIR]`, at most two requests. A header not DOSM's, a sector not in its map, a date not a month's first day, a value that is not a number or a month and sector given twice stops the run. **No schedule runs it**: no step of `warehouse/run_daily.sh`, `warehouse/run_data_machine.sh`, `warehouse/run_data_machine_tables.sh`, `warehouse/run_monthly.sh`, `warehouse/refresh_supply.sh`, `warehouse/scheduled.py` or `.github/workflows/` names it. The table is public, and it is held from the live set (listed under `catalogue_hold` in `warehouse/supabase/live_set.yaml`) and from the Redivis release (`STORAGE_HELD` in `warehouse/redivis/release_v1.py`).

## Vintage and revision

Two writes from the same saved files. Session 2322's, run `20261024T063423Z` (`runs/c108/s2322/write.out`: 1,224 rows, archived 1,224); session 2323's, run `20261024T065220Z`, after the license word in the header changed from `CC BY 4.0` to `public, CC BY 4.0` (`runs/c108/s2323/write_dosm.out`; header line 10: "This run wrote 1224 rows: 0 new, 1224 replacing earlier rows ...; 0 rows are kept from earlier runs"; the archive took 0 rows, nothing having changed). `retrieved_at` is each file's download time: 2026-10-24T06:31:10Z for the supply rows, 06:31:11Z for the consumption rows. `vintage` is each file's Last-Modified: 2026-10-07T16:10:05Z (supply) and 2026-10-07T16:10:06Z (consumption).

Both pages say "Data for the most recent 6 months is provisional and subject to revision in future updates" (the consumption page: "is still provisional and may be revised"). The table holds no flag: the provisional months are January to June 2026, the last six. A later run merges by (entity, variable, ts_utc), so a revised month replaces the old figure, and a month DOSM stops printing keeps its earlier value.

## Shape and variables

Series, 1,224 rows, one entity `dosm:MY`, `node` Malaysia, `geo` MY, `unit` MWh, `freq` P1M, `market` blank. 12 variables, each the file's name and DOSM's sector, 102 rows each (January 2018 to June 2026). Each value is DOSM's million kWh times 1,000; because DOSM prints many decimals, the values are not whole MWh (1,105 of 1,224 rows have a fraction).

| Variable | DOSM's sector | 2018 | 2020 | 2022 | 2023 | 2024 | 2025 | 2026 (Jan to Jun) |
|---|---|---|---|---|---|---|---|---|
| supply_total | supply, total | 163.488 | 162.946 | 176.613 | 181.640 | 193.738 | 193.007 | 100.381 |
| supply_local_public | supply, local_public | 161.418 | 160.578 | 174.351 | 175.452 | 187.397 | 186.341 | 97.108 |
| supply_local_private | supply, local_private | 2.044 | 2.350 | 2.259 | 6.155 | 6.285 | 6.423 | 3.232 |
| supply_imports | supply, imports | 0.025 | 0.018 | 0.003 | 0.033 | 0.056 | 0.242 | 0.042 |
| consumption_local_commercial | consumption, local_commercial | 113.773 | 108.391 | 117.794 | 126.307 | 131.866 | 134.970 | 70.390 |
| consumption_local_domestic | consumption, local_domestic | 31.415 | 36.367 | 38.245 | 40.671 | 43.884 | 44.409 | 23.700 |
| consumption_exports | consumption, exports | 1.508 | 1.570 | 0.816 | 0.893 | 0.918 | 0.914 | 0.463 |
| consumption_losses | consumption, losses | 16.791 | 16.618 | 19.758 | 13.769 | 17.071 | 12.713 | 5.828 |

TWh, the sum of each year's months in the table (`runs/c108/s2326/notes/my.out`). Not shown: `supply_local` (public plus private), `supply_distribution` (equal to `supply_total`, below), `consumption_local` (commercial plus domestic) and `consumption_total` (equal to `supply_total`). The highest month is May 2026 (17,563,331 MWh of total supply), the lowest April 2020 (11,685,347 MWh).

- **Identities.** Public plus private equals local supply; local supply plus imports equals total supply; commercial plus domestic equals local consumption; local consumption plus exports plus losses equals total consumption; total supply equals total consumption. Each holds in all 102 months, the largest gap under 6e-9 MWh (floating point).
- **`supply_distribution`.** It equals `supply_total` in all 102 months, to 0 MWh (`my.out`). DOSM publishes it as a sector of the supply file without defining it beyond "distribution"; it is kept as published.
- **Placeholders.** `supply_imports` is 0 in 26 months (the first December 2018, the last July 2025); no other variable has a zero. No value is negative.
- **A break in 2023.** Private installations rise from 2.259 TWh in 2022 to 6.155 TWh in 2023 (189,805 MWh in December 2022, 519,940 MWh in January 2023), and losses fall from 19.758 to 13.769 TWh; losses as a share of total supply are 10.1 to 11.2 percent from 2018 to 2022 and 6.6 to 8.8 percent from 2023 to 2025. Neither the pages nor the header explain the change.

## Placing values in time, and what is filled

`ts_utc` is the month's first day at 00:00:00Z (DOSM's `date`, "with DD set to 01 as the data is at monthly frequency"), a label for the calendar month. The 102 months from January 2018 to June 2026 all have the 12 variables; no cell of the two files is blank, and nothing is filled.

## License

Header: "License: public, CC BY 4.0 (each dataset's page on data.gov.my). Cite: Department of Statistics Malaysia, data.gov.my." Each dataset page: "This data is made open under the Creative Commons Attribution 4.0 International License (CC BY 4.0)" (reads 551 and 553). `warehouse/metadata/license_verdicts.csv`: Department of Statistics Malaysia (DOSM), read 551, verdict "may be public", if the ERW sells anything "may be public", attribution to DOSM. data.gov.my's robots file: `User-agent: *` / `Allow: /`, no AI agent named (read 548); api.data.gov.my and storage.data.gov.my have none (reads 549 and 552, HTTP 404; storage answers S3's `NoSuchKey`); `https://data.gov.my/terms-of-use` is HTTP 404 (read 550). `docs/licenses.md`, the table's row: verdict today "may be public", flag public, "agrees", ERW verdict public.

## Checks (session 2326)

The figures in this note were computed from the rows of `warehouse/output/dosm_malaysia_electricity_monthly.csv`, read past its 10 header lines (counted), and from the saved files and pages, read only (scripts `runs/c108/s2326/notes/my.py`, `my2.py`, outputs `my.out`, `my2.out` beside them).

- 1,224 rows, 12 variables, January 2018 to June 2026, as header lines 1, 3 and 10 state; one entity; no (entity, variable, ts_utc) twice; no blank value; unit MWh, freq P1M and geo MY throughout; `source_url` the file each row came from (612 each).
- **Against the files:** an independent parse of the two saved CSVs gives 612 lines each, six sectors of 102 months, no blank cell; every line matches its row, value times 1,000, within 2e-9 MWh.
- **The trial against the table:** `runs/c108/s2322/trial/dosm_malaysia_electricity_monthly.csv` has the same 1,224 keys with 0 differences in value, `retrieved_at` or `vintage`.
- Session 2322's cross-check (`runs/c108/s2322/cross.py`, `cross.out`, run on the trial): the five identities within 6e-9 MWh, `supply_imports` zero in 26 months, the yearly sums printed above. Its last test, `supply_distribution` against local consumption plus losses, gives a largest gap of 154,706 MWh; its lookup of Ember generation for Malaysia prints empty.
- Session 2326's own: `supply_distribution` equals `supply_total` in 102 of 102 months; against `owid_ember_electricity_annual`'s `owid_energy:MYS` `electricity_demand` (the only Malaysian energy variable it holds besides emissions), DOSM's total supply is below Ember's demand by 3.31 percent in 2018 (163.488 against 169.09 TWh), 4.75 (2019), 5.52 (2020), 4.26 (2021), 3.09 (2022), 2.71 (2023), 1.68 (2024) and 3.45 (2025: 193.007 against 199.91 TWh).

## The session report against the table

Every figure of `SESSION_2322_REPORT.md` checked against the table, the saved files and `cross.out` holds (January 2018 to June 2026, 1,224 rows, 12 variables, million kWh times 1,000, the latest six months provisional, CC BY 4.0 from reads 551 and 553, the robots files and the missing terms page, the five identities "to the kWh in every month", `distribution` equal to total supply in all 102 months, DOSM 1.7 to 5.5 percent below Ember in every year 2018 to 2025 with 163.49 against 169.09 TWh and 193.01 against 199.91 TWh, imports zero in 26 months, 8 requests of 15), except:

- "Imports are small: 0.02 to 0.24 TWh a year": 2022's imports are 0.003 TWh (point 1).
- The distribution and Ember figures hold, but neither is in `cross.out`, which the report names as their source (point 2).

## What it does not hold

- Generation by fuel or by plant, capacity, the Peninsular, Sabah and Sarawak grids apart, prices or tariffs, months before 2018 (the files begin in January 2018), the parquet copies of the same files, and DOSM's other energy datasets.

## Points for the session to act on

1. **The report's import range leaves out 2022.** The report says imports are "0.02 to 0.24 TWh a year"; the table's 2022 imports sum to 2,923.3 MWh, 0.003 TWh (`my.out`), and `cross.out` prints 2022 as 0.00. The range over 2018 to 2025 is 0.003 to 0.242 TWh.
2. **Two of the report's cross-check results are not in `cross.out`.** The report sets "DOSM's `distribution` supply equals total supply in all 102 months" and the Ember comparison (1.7 to 5.5 percent, 163.49 against 169.09 TWh, 193.01 against 199.91 TWh) under "The cross-check (`runs/c108/s2322/cross.py`, `cross.out`)". `cross.py` tests distribution against local consumption plus losses (largest gap 154,706.0 MWh) and looks for Ember generation variables, printing an empty frame. Session 2326 computed both claims from the table and they hold (0 MWh in 102 months; 1.68 to 5.52 percent). `cross.py` should test what the report states and be run again.
3. **The header does not say `supply_distribution` equals `supply_total`.** Header line 2 lists it among the variables without saying it repeats the total in every month, so a reader summing the supply sectors counts the total twice. One clause in the header would prevent it.
4. **A break between 2022 and 2023 is not described.** `supply_local_private` almost triples (2.259 to 6.155 TWh) and `consumption_losses` falls by 30 percent (19.758 to 13.769 TWh) from one year to the next, the step falling between December 2022 and January 2023. DOSM's pages do not explain it, and the header, docstring and report do not mention it; a loss rate computed across the two years compares unlike figures.

Compared besides, with no contradiction found: the header's and docstring's counts, months, variables, unit and factor of 1,000, "Commercial includes industry and mining; domestic includes public lighting", "The latest six months are provisional (DOSM)" and "Nothing is filled" against the rows, the two files and the two pages. Header line 7's "compiled from TNB, SESB, Sarawak Energy and the Energy Commission" follows the pages' "Data source(s)" list; the docstring's "with the independent producers'" follows their methodology text; both are DOSM's.

Acted on in session 2326: session 2322's report now gives imports as 0.003 to 0.24 TWh a year; `runs/c108/s2322/cross.py` now tests distribution against the total and the total against Ember's demand, on the written table, and `cross.out` bears out both claims (0 MWh in all 102 months; 1.68 to 5.52 per cent below Ember). Header line 3 now says that `supply_distribution` equals `supply_total` (102 of 102 months, computed by the connector) and is never to be added to the other sectors, and names the level change of private supply and losses between December 2022 and January 2023. The table was written again offline: the same rows.
