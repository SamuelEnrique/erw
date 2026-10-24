# Mauritius's electricity generated, its renewable share and electricity sold, a year, 2017 to 2025, and its capacity, peak demand and generation by source, 2022 to 2025 (Statistics Mauritius, Energy and Water Statistics 2023 and 2025)

Energy Research Warehouse (ERW), method note written in session 2410 (chain 114) for a table first written on 24 October 2026 (session 2409 of chain 114, its report `archive/sessions/SESSION_2409_REPORT.md`).

Tables: `statsmu_mauritius_electricity_annual`

## Publisher and address

Statistics Mauritius, its Economic and Social Indicators "Energy and Water Statistics", the 2025 edition (Issue 1929, page `https://statsmauritius.govmu.org/Pages/Statistics/ESI/Energy_Water/Energy_Water_Yr25.aspx`, read 743) and the 2023 edition (Issue 1791, page `.../Energy_Water_Yr23.aspx`, read 745), each an Excel workbook, two requests:

- `https://statsmauritius.govmu.org/Documents/Statistics/ESI/2026/EI1929/ESI_Energy_Yr25_050626.xlsx` (2025 edition)
- `https://statsmauritius.govmu.org/Documents/Statistics/ESI/2024/EI1791/Energy_Water_Yr23_070624.xlsx` (2023 edition)

Source id `statsmu:energy_water_statistics`. Each workbook has 14 sheets (Tables 1 to 16 and a sheet of figures). Three tables are taken, from two sheets:

- Table 1, sheet `TAB1`, "Main Energy and Water Indicators" (2018 - 2025 in the 2025 edition, 2017 - 2023 in the 2023 edition): "Total electricity generated" (GWh), the row beneath it "Of which renewables" (%), "Total electricity sold" (GWh).
- Table 7, sheet `TAB7,8,9`, "Evolution of power plant capacities1, peak power demand and electricity generation" (the edition's two years): installed and effective capacity (MW), peak power demand of Mauritius and of Rodrigues (MW), and generation by hydro, wind, photovoltaic, thermal (landfill gas, other) and total (GWh).
- Table 8, the same sheet, "Electricity generation by source of energy" (the edition's two years): primary energy (hydro, wind, landfill gas, photovoltaic, each "(renewable energy)"), secondary energy (gas turbine (kerosene), fuel oil & diesel, coal, and "Bagasse & Fuelwood (renewable energy)" in the 2025 edition, "Bagasse (renewable energy)" in the 2023 edition), "Total electricity generated" and "of which renewable energy", in GWh and percent.

The footnotes that bear on the variables: Table 7's 1, on "capacities": "1 includes plant capacity for electricity not exported to CEB" (both editions; point 1). Table 1's 1 is "Revised", attached to the population, GDP and per capita rows, not to the three rows taken. Neither edition defines "Effective capacity". The same sheet's Table 9, "Generation of electricity by Central Electricity Board and Independent Power Producers" (not taken), and Table 11, "Sales of electricity by type of tariff" (sheet `TAB10,11`, "Source: Central Electricity Board (CEB)", not taken), say what the generation and the sales cover (below). The energy balances (Tables 2 and 3) carry the footnotes "includes woodchips" (fuelwood, 2025 edition) and "includes cane trash" (bagasse).

Session 2409's probe (`runs/c114/s2409/probe.csv`) made 14 requests, 6 of them to Namibian, Salvadoran and Honduran hosts (not taken) and 8 to statsmauritius.govmu.org: the robots file (HTTP 404, 10:32:08Z, read 739), the home page (read 740), the copyright notice (read 741), a guessed subject page (HTTP 404, read 742), the 2025 edition's page (read 743), its workbook (HTTP 200, 574,386 bytes, at 2026-10-24T10:33:20Z, Last-Modified "Fri, 05 Jun 2026 04:58:07 GMT", read 744), the 2023 edition's page (read 745) and its workbook (HTTP 200, 1,356,256 bytes, at 2026-10-24T10:33:57Z, Last-Modified "Fri, 07 Jun 2024 07:40:46 GMT", read 746). All are saved in `runs/license_reads/s2409/`; both workbooks have the probe log's SHA-256. The write read them offline from `warehouse/raw/statsmu_mauritius/20261024T103054Z_probe/` ("raw file reused", run log).

Connector: `warehouse/connectors/statsmu_mauritius.py` (session 2409): `[--offline] [--out-dir DIR]`, two requests, the older edition first; a year both editions give is taken from the later one. Table 7's columns are taken by position (3, 5, 9, 10, 11, 12, 14, 15, 17, 19), after its header words are found; Table 8's rows by label, the first label among three indented columns. Checks, each stopping the run: Table 8's primary sources add to its primary energy, its secondary ones to its secondary energy, the two to its total; Table 7's sources add to its total; both totals equal Table 1's generation; all within 0.01 GWh. **No schedule runs it**: no step of `warehouse/run_daily.sh`, `warehouse/run_data_machine.sh`, `warehouse/run_data_machine_tables.sh`, `warehouse/run_monthly.sh`, `warehouse/refresh_supply.sh`, `warehouse/scheduled.py` or `.github/workflows/` names it. The table is internal; it is held from the live set (listed under `catalogue_hold` in `warehouse/supabase/live_set.yaml`) and is not in the Redivis release package, which takes public tables only (`warehouse/redivis/release_v1.py`: "an internal table is never in the public dataset").

## Vintage and revision

One write, run `20261024T103556Z` ("This run wrote 79 rows: 79 new, 0 replacing earlier rows ...; 0 rows are kept from earlier runs"), from the saved workbooks; no separate trial was run. Each row's `source_url`, `retrieved_at` and `vintage` are its edition's: 50 rows from the 2025 edition (retrieved 2026-10-24T10:33:20Z, `vintage` 2026-06-05T04:58:07Z: Table 1's 2018 to 2025 and Tables 7 and 8's 2024 and 2025) and 29 from the 2023 edition (retrieved 10:33:57Z, `vintage` 2024-06-07T07:40:46Z: Table 1's 2017 and Tables 7 and 8's 2022 and 2023). So 2022 and 2023 come from two editions: Table 1's rows from 2025's, the others from 2023's.

The two editions give the same generation, renewable share and sales, to the last digit, in every year both print (2018 to 2023). No row taken is marked revised or provisional. A later run asks both addresses again; a newer edition is read only when the connector's list names it.

## Shape and variables

Series, 79 rows, one entity `statsmu:MU`, `node` Mauritius, `geo` MU, `freq` P1Y, `market` blank; `unit` MWh for generation and sales (the tables' GWh times 1,000), MW for capacity and peaks, pct for the renewable share. 16 variables: three from Table 1 with 9 rows each (2017 to 2025), thirteen from Tables 7 and 8 with 4 rows each (2022 to 2025).

| Variable | Rows | The workbook's row |
|---|---|---|
| generation_total | 9 | Table 1, Total electricity generated |
| renewable_share | 9 | Table 1, Of which renewables (%) |
| electricity_sold | 9 | Table 1, Total electricity sold |
| capacity_installed, capacity_effective | 4 each | Table 7, Installed capacity (MW), Effective capacity (MW) |
| peak_demand_mauritius, peak_demand_rodrigues | 4 each | Table 7, Peak power demand (MW), Mauritius, Rodrigues |
| generation_hydro, _wind, _landfill_gas, _photovoltaic | 4 each | Table 8, primary energy rows |
| generation_gas_turbine_kerosene, _fuel_oil_diesel, _coal, _bagasse | 4 each | Table 8, secondary energy rows |
| generation_renewable | 4 | Table 8, of which renewable energy |

Table 1, GWh and percent as the editions print them (`runs/c114/s2410/notes/mu.out`):

| Year | Generated | Of which renewables (%) | Sold | Sold over generated (%) |
|---|---|---|---|---|
| 2017 | 3,119.712 | 20.0 | 2,618.123 | 83.9 |
| 2018 | 3,131.641 | 20.7 | 2,650.246 | 84.6 |
| 2019 | 3,236.584 | 21.7 | 2,754.022 | 85.1 |
| 2020 | 2,882.401 | 23.9 | 2,448.241 | 84.9 |
| 2021 | 2,992.091 | 21.5 | 2,524.276 | 84.4 |
| 2022 | 3,119.226 | 19.2 | 2,698.147 | 86.5 |
| 2023 | 3,265.466 | 17.6 | 2,813.689 | 86.2 |
| 2024 | 3,417.639 | 18.2 | 2,931.514 | 85.8 |
| 2025 | 3,551.556 | 17.8 | 3,069.838 | 86.4 |

Tables 7 and 8, with Table 9's split by producer (MW and GWh):

| | 2022 | 2023 | 2024 | 2025 |
|---|---|---|---|---|
| Installed capacity (MW) | 867 | 880.51 | 907.315 | 946.055 |
| Effective capacity (MW) | 777.9 | 793.2 | 814.845 | 850.405 |
| Peak demand, Mauritius (MW) | 491.6 | 508.4 | 525.7 | 567.9 |
| Peak demand, Rodrigues (MW) | 7.6 | 8.5 | 8.551 | 9.53 |
| Hydro | 128.296 | 94.442 | 121.339 | 89.225 |
| Wind | 15.478 | 8.638 | 14.168 | 11.221 |
| Landfill gas | 17.214 | 13.318 | 8.730 | 6.122 |
| Photovoltaic | 154.497 | 148.788 | 177.982 | 230.848 |
| Gas turbine (kerosene) | 2.188 | 19.456 | 9.108 | 41.798 |
| Fuel oil & diesel | 1,534.704 | 1,576.200 | 1,451.152 | 1,760.523 |
| Coal | 983.897 | 1,095.392 | 1,336.385 | 1,116.797 |
| Bagasse (2024 and 2025: Bagasse & Fuelwood) | 282.952 | 309.233 | 298.775 | 295.022 |
| Of which renewable | 598.437 | 574.418 | 620.994 | 632.438 |
| Total generated | 3,119.226 | 3,265.466 | 3,417.639 | 3,551.556 |
| Table 9: CEB, of which Rodrigues | 1,673.876, 45.294 | 1,702.097, 48.559 | 1,605.284, 51.455 | 1,922.253, 56.175 |
| Table 9: IPPs, of which exported to CEB | 1,445.349, 1,242.030 | 1,563.369, 1,349.110 | 1,812.355, 1,567.358 | 1,629.303, 1,395.207 |

- **Generation is the Republic's and every producer's.** Table 9's total is the CEB's generation on Mauritius and on Rodrigues plus the Independent Power Producers', and equals Tables 1, 7 and 8's totals in every year. The IPPs' generation includes what they did not export to the CEB: 203.319, 214.259, 244.997 and 234.096 GWh in 2022 to 2025. Table 8's thermal rows hold the IPPs' (Table 9: IPP thermal 1,643.889 GWh in 2024); the energy balances put all coal into "Independent Power Producer / Autoproducer plants" (2025: 404,761 toe; public plants 0) (point 2).
- **Electricity sold is the CEB's sales by tariff.** Table 1's figure equals Table 11's total in every edition year (2024: 2,931,514.018 MWh; 2025: 3,069,838.290) and the Republic's per capita consumption of electricity sold times the mid-year population (within 0.04 GWh). Generation less sales (421.079 to 486.125 GWh in 2022 to 2025) holds the IPPs' own use as well as the network's own use and losses (point 3).
- **Bagasse & Fuelwood.** The 2025 energy balance books 2,880 toe of fuelwood ("includes woodchips") into IPP and autoproducer plants in 2025 and none in 2024 or 2023; bagasse "includes cane trash".
- **The renewable share** is Table 8's renewable total over its total, to one decimal, in 2022 to 2025 (session 2409's cross-check).

## Placing values in time, and what is filled

`ts_utc` is the year's 1 January at 00:00:00Z, a label for the calendar year, 2017-01-01 to 2025-01-01. Generation and sales are the year's totals, capacities the year's (the tables do not say at what date), peaks the year's maxima, each island's own. Tables 7 and 8 have no row before 2022; nothing is filled. Every cell taken has a figure.

## License

Header: "License: internal. The Government of Mauritius's copyright notice (https://statsmauritius.govmu.org/Pages/CopyrightNotice.aspx) lets State material be downloaded and reproduced accurately without specific permission, with the source (including the URL) and copyright status acknowledged; any other use needs the Government Information Service's approval; internal until a ruling. Source: Statistics Mauritius, statsmauritius.govmu.org, (c) Government of Mauritius." The saved notice (read 741) reads "Apart from any use permitted by the Copyright Act, the State copyright protected material may be downloaded free of charge to file or printer without requiring specific permission, provided that any such State owned material being reproduced accurately and not being used in a derogated manner or in a misleading context. Where this material is being issued to others, the source (including the URL) and copyright status must be acknowledged", then that the permission "does not extend to any material on this website that is identified as being the Copyright of a third party", and "Any other proposed use of any State protected material is subject to approval". `warehouse/metadata/license_verdicts.csv`: Statistics Mauritius, read 741, verdict "may be public", the same if the ERW sells anything. `warehouse/metadata/license_reads.csv` records reads 733 to 746 (session 2409). `docs/licenses.md`, the table's row: verdict today "may be public", flag internal, "DISAGREES: the flag is stricter", if the ERW sells anything "may be public", ERW verdict internal; it is listed under "Flagged internal; the sentence read allows it". The report leaves the ruling to Samuel.

## Checks (session 2410)

The figures in this note were computed from the rows of `warehouse/output/statsmu_mauritius_electricity_annual.csv`, read past its 10 header lines (counted), and from the two saved workbooks, read only with openpyxl from their bytes (scripts `runs/c114/s2410/notes/mu.py` and `gt_dump.py`, outputs `mu.out`, `mu12.txt` and `mu14.txt` beside them).

- 79 rows, 16 variables, 2017 to 2025, as header lines 1, 3 and 10 state; one entity; no (entity, variable, ts_utc) twice; no blank value.
- **Against the workbooks:** all 79 values equal the edition each row names, times 1,000 where MWh (0 differences); Table 1's three rows agree between the editions in 2018 to 2023 (largest difference 0).
- **Table 9 against the totals:** the CEB plus the IPPs equal the total generated in all four years (to 0.001 GWh); "Total units generated for sales" equals the CEB's Mauritius generation plus the IPPs' exports (2024: 3,121.186 GWh). In 2022 the 2023 edition gives the IPPs' exports as 1,242.030 GWh in one line and 1,241.640 in the other.
- **No trial** was run.
- Session 2409's cross-check (`runs/c114/s2409/cross.py`, `cross.out`): generation against `owid_ember_electricity_annual`'s Mauritius demand, within 0.6 percent in every year 2017 to 2024 (2020: 2.882 against 2.900 TWh, -0.6; 2024: 3.418 against 3.410); the renewable total over generation against Table 1's share, 19.19, 17.59, 18.17 and 17.81 percent against 19.2, 17.6, 18.2 and 17.8.

## The session report against the table

Every figure of `SESSION_2409_REPORT.md` checked against the table, the workbooks and `cross.out` holds (79 rows, the two editions and their issues, Table 1's 2017 to 2025, Tables 7 and 8's 2022 to 2025, the variables, the factor of 1,000, the checks within 0.01 GWh, the editions agreeing in 2018 to 2023, within 0.6 percent of Ember, 3.418 against 3.410 TWh, the share to one decimal, reads 733 to 746 and what each says, 14 requests of 15, 8 to statsmauritius.govmu.org). Nothing in it is contradicted; what it leaves out is in points 1 to 3.

## Limits

- **Generation counts producers' own use.** The total, the thermal rows and the renewable share include the IPPs' and autoproducers' electricity not exported to the CEB (about 200 to 245 GWh a year in 2022 to 2025).
- **Capacity counts producers' own plant** (Table 7's footnote), and "effective" is not defined.
- **Sales are the CEB's** to its customers; they are not consumption, and generation less sales is not a loss figure.
- **Peaks are each island's**, Mauritius and Rodrigues, not a sum.
- **Tables 7 and 8 have four years.** Earlier editions were not read.

## What it does not hold

- The energy balances (Tables 2 and 3), primary energy and final consumption beyond Table 1's electricity rows, Table 9's split by producer, fuel input (Table 10), sales by tariff (Table 11), water, rainfall and the other indicators of Table 1; years before 2017 and, for Tables 7 and 8, before 2022.

## Points for the session to act on

1. **Capacity includes plants serving their owners, by Table 7's footnote; "effective" is not defined.** The docstring and header give `capacity_installed` and `capacity_effective` as Table 7's "(MW)" without its footnote: "1 includes plant capacity for electricity not exported to CEB", attached to "capacities" in the title of both editions. Neither workbook says what "Effective capacity" is (777.9 to 850.405 MW against 867 to 946.055 installed). The header could carry the footnote and say that the effective capacity is not defined.
2. **Generation is every producer's, own use included; the header does not say so.** Header line 2 gives `generation_total` and the sources without saying who generates. Table 9 shows the total as the CEB's (Mauritius and Rodrigues) plus the IPPs', and the IPPs' as including electricity not exported to the CEB: 203.319, 214.259, 244.997 and 234.096 GWh in 2022 to 2025 (2024: 1,812.355 generated, 1,567.358 exported). Table 8's thermal rows hold the IPPs' plants; coal is burned only in "Independent Power Producer / Autoproducer plants" in the energy balances (2023: 383,493.56 toe; 2024: 458,840; 2025: 404,761; public plants 0). "Total units generated for sales" (Island of Mauritius) is smaller (2024: 3,121.186 against 3,417.639 GWh). A clause in header line 2 would say this.
3. **`electricity_sold` is the CEB's sales, and generation less sales is not losses.** The docstring and header give "electricity_sold (MWh)" with no definition. Table 1's figure equals Table 11's total of sales by tariff, whose source line is the Central Electricity Board, in every year both print (2024: 2,931,514.018 MWh), and equals the Republic's per capita consumption of electricity sold times the population. The gap to generation (486.125 GWh in 2024) holds the IPPs' own use (244.997 GWh) besides the own use and losses the energy balance books (2025: 6,612 and 17,029 toe). The header could say "the CEB's sales to its customers, Mauritius and Rodrigues".

Compared besides, with no contradiction found: the header's and docstring's counts, years, units, the factor of 1,000, the two editions and which years each gives, "A year both editions give is taken from the later one", "The values both editions give agree", the 2025 edition's "Bagasse & Fuelwood", the node as the Republic (Table 9 names the islands of Mauritius and Rodrigues), `retrieved_at` and `vintage` against the probe log, the robots file's 404, the copyright notice as quoted, and every row against the workbooks. Table 1's footnote "Revised" touches none of the rows taken.

Acted on in session 2410: the docstring and header now say that capacity includes plants not exporting to the CEB (Table 7's footnote) and that effective capacity is not defined; that generation is every producer's, the independent producers' own use included, with their thermal and all the coal; and that `electricity_sold` is the CEB's sales, so generation less sales is not losses. Session 2409's report needed no correction. The table was written again offline: the same rows.
