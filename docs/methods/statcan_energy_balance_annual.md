# Canada's supply and demand of primary and secondary energy by province and fuel, a year, 1995 to 2024: production, trade, transfers, stocks, transformation and final use by sector (Statistics Canada, table 25-10-0029-01, the Report on Energy Supply and Demand)

Energy Research Warehouse (ERW), method note written in session 2380 (chain 112) for a table first written on 24 October 2026 (session 2383 of chain 112, its report `archive/sessions/SESSION_2383_REPORT.md`).

Tables: `statcan_energy_balance_annual`

## Publisher and address

Statistics Canada (StatCan), table 25-10-0029-01 (formerly CANSIM 128-0016), "Supply and demand of primary and secondary energy in terajoules, annual" (`https://www150.statcan.gc.ca/t1/tbl1/en/tv.action?pid=2510002901`), read from the table's full CSV download, one request:

- `https://www150.statcan.gc.ca/n1/tbl/csv/25100029-eng.zip`

Source id `statcan:25-10-0029-01`. The zip holds `25100029.csv` (32,797,219 bytes, 210,053 lines of data) and `25100029_MetaData.csv`, which names fifteen surveys (coal, coke, refined products, pipelines, natural gas transmission and distribution, electricity supply and disposition, thermal generating station fuel, industrial consumption, end use of gas and refined products, renewable fuels) and carries the notes that define the lines. Its cube notes: 1, quarterly data before 2002 are in table 25-10-0004; 2, the table replaced tables 25-10-0009, 25-10-0010 and 25-10-0012 and "Comparisons of the new datasets with earlier published datasets should be done with caution"; 3, production and availability of total primary and secondary energy "are not shown as these would lead to double-counting".

Session 2383's probe (`runs/c112/s2383/probe.csv`) made 2 requests to www150.statcan.gc.ca, 6 seconds apart: the robots file (09:09:43Z, read 620) and the zip (HTTP 200, 2,790,629 bytes, at 2026-10-24T09:09:49Z, Last-Modified "Thu, 13 Nov 2025 13:30:17 GMT"). Both are saved in `runs/license_reads/s2383/`.

Connector: `warehouse/connectors/statcan_energy_balance.py` (session 2383): `[--offline] [--out-dir DIR]`, one request, asked again unless `--offline`. A unit other than "Terajoules", a scalar factor other than "units", an area not in its map of 16, a year that does not read, a status other than blank, "..", "x" or "F", or a key given twice stops the run; fuels and lines are not mapped, each becomes a slug. Terajoules are written as MWh (times 1,000,000/3,600, rounded to 0.001). **No schedule runs it**: no step of `warehouse/run_daily.sh`, `warehouse/run_data_machine.sh`, `warehouse/run_data_machine_tables.sh`, `warehouse/run_monthly.sh`, `warehouse/refresh_supply.sh`, `warehouse/scheduled.py` or `.github/workflows/` names it. The table is public; it is held from the live set (listed under `catalogue_hold` in `warehouse/supabase/live_set.yaml`) and from the Redivis release (`STORAGE_HELD` in `warehouse/redivis/release_v1.py`).

## Vintage and revision

One write, run `20261024T091126Z` ("File holds 128420 rows, one snapshot; the previous file held 0 rows"), from the saved zip. `retrieved_at` is 2026-10-24T09:09:49Z and `vintage` the zip's Last-Modified, 2025-11-13T13:30:17Z, in every row: the 2024 figures as StatCan released them in November 2025. No line carries a symbol (the SYMBOL column is blank in all 210,053), so none is marked preliminary or revised. Each run asks the zip again and writes the whole table.

## Shape and variables

Series, 128,420 rows, 354 entities `statcan_eb:<area>:<fuel>`, 6,437 nodes, 46 variables (StatCan's lines as slugs), `unit` MWh, `freq` P1Y, `market` blank; `x_fuel`, `x_line`, `x_vector`, and `x_terminated` t on 191 rows. 16 areas: Canada (`ca`, `geo` CA), the ten provinces and three territories (CA-<code>), and two groups with a blank `geo`, the Atlantic provinces (`atl`) and "Yukon, Northwest Territories and Nunavut" (`ter`). Every area has 1995 to 2024 except Yukon, the Northwest Territories and Nunavut, from 1999; `ter` covers 1995 to 2024.

**Fuels**, 28 with rows (StatCan's file has 29; anthracite has no value in any line). Totals hold their parts (the metadata's parent members): total primary and secondary energy; primary energy (crude oil, natural gas, gas plant NGLs, primary electricity hydro and nuclear, steam, total coal, renewable fuels); total coal (Canadian bituminous, sub bituminous, lignite, imported bituminous, all terminated, last value 2009); total refined petroleum products (LPGs, still gas, motor gasoline, kerosene and stove oil, diesel, light and heavy fuel oil, petroleum coke, aviation gasoline, aviation turbo fuel, non-energy products); coke, coke oven gas and secondary electricity, thermal. "Secondary energy" itself has no line in the file.

**Lines**, 46. Supply: production, exports, imports, inter-regional transfers, stock variation, inter-product transfers, other adjustments, availability; transformation: to electricity by utilities and by industry, to coke and manufactured gases, to refined petroleum products, to steam generation; then net supply, producer consumption, non-energy use, energy use final demand, and its sectors (total industrial with mining, manufacturing and its seven industries, forestry and construction; total transportation with railways, airlines, marine, pipelines, road and retail pump sales; agriculture; residential; public administration; commercial and other institutional), the statistical difference, and "Stock change, utilities and industry" (terminated; 32 values, all 0).

Canada in 2024, terajoules as StatCan prints them (`runs/c112/s2375/notes/eb4.out`; the table holds each times 277.778 in MWh; a blank is a line without a value):

| Fuel | Production | Imports | Exports | Stock variation | Availability | Net supply | Final demand | Statistical difference |
|---|---|---|---|---|---|---|---|---|
| Primary energy | 24,664,357 | 3,305,818 | 14,474,714 | 14,252 | 12,290,858 | 6,467,684 | | |
| Crude oil | 11,759,895 | 1,763,002 | 9,465,968 | -37,646 | 4,201,187 | | | |
| Natural gas | 8,913,339 | 1,058,261 | 3,416,881 | 20,743 | 5,169,994 | 4,005,738 | 3,186,548 | -369 |
| Gas plant NGLs | 1,042,166 | 128,823 | 414,245 | 1,495 | 830,409 | 725,396 | 131,871 | 0 |
| Primary electricity, hydro and nuclear | 1,722,727 | 84,534 | 129,993 | | 1,677,268 | 1,677,268 | 2,009,511 | 85,048 |
| Total coal | 1,146,029 | 153,986 | 1,012,285 | 30,152 | 263,828 | 24,942 | 18,300 | 3,831 |
| Renewable fuels | 80,201 | 117,213 | 35,343 | -492 | 148,171 | | | |
| Secondary electricity, thermal | 517,015 | | | | 517,015 | 517,015 | | |
| Total refined petroleum products | 4,922,452 | 439,024 | 987,053 | -14,659 | 3,953,185 | 3,892,638 | 3,026,438 | 0 |
| Total primary and secondary energy | | 3,780,466 | 15,462,989 | 2,885 | | 10,976,739 | 8,505,363 | 89,191 |

## Signs, and how the lines are defined

The header and docstring give no sign convention. The metadata's notes and the figures give this one (session 2380's checks, `eb3.out`, in terajoules on the zip's own figures):

- **Exports and stock variation are positive numbers that are subtracted.** Note 7: availability is "the summation of production, imports, inter-regional transfers, inter-product transfers and other adjustments, less exports and stock variation". Exports are never negative (3,509 rows). Where every term is given, availability equals that sum within 1 TJ in 3,101 of 3,209 cells; where the stock variation exceeds 100 TJ, within 0.5 percent in all 1,360 cells, against 158 with its sign reversed. A positive stock variation is therefore a build in stocks, a negative one a draw (1,576 negative rows); no fuel fits the opposite sign.
- **Inter-regional transfers are net receipts, added** (note 4: "the net inter-regional movement of product between regions"): of the cells with a transfer above 100 TJ and every term given, 1,792 fit the transfer added and 22 subtracted. They should cancel across the country, but Canada's own line is non-zero in 128 of its 388 values (at most 739 TJ, total refined petroleum products, 2001), and the provinces and territories add to within 1 TJ of zero in 113 of 180 complete fuel-years (at most 415 TJ apart).
- **Inter-product transfers and other adjustments are signed and added** (notes 5 and 6; negative in 1,446 and 958 rows). Other adjustments include losses and "is also used to balance supply and disposition".
- **Transformation lines are inputs, positive, subtracted from availability** (note 8): net supply equals availability less the five transformation lines within 1 TJ in 5,048 of 5,061 cells. The exception is steam: its "Transformed to steam generation" line is the steam produced, negative (224 rows), so that its net supply is positive (Canada 2024: -34,340 TJ, net supply 34,340). The aggregates primary energy and total primary and secondary energy carry it net, negative in 199 and 192 rows.
- **The statistical difference is net supply less producer consumption, non-energy use and final demand** (positive when supply exceeds recorded use): within 1 TJ in 2,796 of 3,229 cells; with the opposite sign, in 1,078. Its exceptions are electricity (below), total primary and secondary energy (115), gas plant NGLs (90) and total refined petroleum products (60), which this note did not resolve. The metadata lists "Statistical difference" under "Energy use, final demand" (its parent member 18), but final demand is the six sectors without it: within 1 TJ in 4,080 of 4,398 cells, and only 1,297 of 3,070 with the difference added (point 3).
- **Electricity's demand is booked under primary electricity.** "Secondary electricity, thermal" has only production, availability and net supply. "Primary electricity, hydro and nuclear" carries all the demand lines, and its final demand exceeds its own net supply (Canada 2024: 2,009,511 against 1,677,268 TJ, 558.20 against 465.91 TWh): it is the use of all electricity. From 2010 its statistical difference is the primary and the secondary net supply less producer consumption, non-energy use and final demand (Canada 2024: 465.91 + 143.62 - 27.70 - 558.20 is 23.63 TWh; StatCan prints 85,048 TJ, 23.62 TWh); in 2005 to 2009 it leaves the secondary net supply out (all 30 cells of those years), so Canada's is -110.95, -101.73, -108.25, -99.81 and -97.53 TWh, against +37.71 in 2010; before 2005 the line has no value (point 1).
- **Producer consumption** of electricity falls from 52.42 TWh (2004) to 18.84 TWh (2005) at the same break.
- **Negative values elsewhere** are few: availability 6 rows (crude oil, diesel, NGLs, LPGs; the largest Alberta's crude oil, 2003, -195,037 TJ), net supply 60, final demand 1 (natural gas, Newfoundland and Labrador, 1999, -8 TJ).

## Canada's hydro and nuclear production against the generation table

Session 2383 found the balance's production of "Primary electricity, hydro and nuclear" 33 to 55 TWh a year above the hydraulic and nuclear turbines of `statcan_electricity_generation_monthly`. **StatCan's metadata does not say why.** Member 7, the fuel, has no note; the only electricity note, 43 on secondary electricity, says gases from oil sands upgrading used for electricity are reported as still gas; nothing defines what primary electricity includes.

The figures, without explaining them (`runs/c112/s2375/notes/eb2.out`, TWh; the generation table's class "all", years of 12 months):

| Year | Balance, primary electricity | Hydraulic and nuclear turbines | Gap | Wind, solar and tidal | Gap less wind, solar and tidal |
|---|---|---|---|---|---|
| 2016 | 509.74 | 477.09 | 32.65 | 32.29 | 0.36 |
| 2017 | 519.80 | 486.50 | 33.31 | 32.96 | 0.35 |
| 2018 | 512.20 | 476.68 | 35.52 | 34.07 | 1.45 |
| 2019 | 508.27 | 473.11 | 35.16 | 35.25 | -0.09 |
| 2020 | 512.95 | 475.27 | 37.68 | 38.83 | -1.15 |
| 2021 | 505.43 | 464.36 | 41.07 | 38.92 | 2.15 |
| 2022 | 518.64 | 474.65 | 43.99 | 42.28 | 1.71 |
| 2023 | 486.64 | 443.85 | 42.79 | 44.32 | -1.53 |
| 2024 | 478.54 | 423.56 | 54.98 | 51.08 | 3.90 |

From 2016 the gap equals the generation table's wind, solar and tidal generation within 4 TWh in every year; in 2008 to 2015 the gap exceeds them by 0.28 to 19.57 TWh. The balance's primary and secondary electricity together are within 13 TWh of the generation table's total of all types in 2016 to 2024 (the generation table's total less the balance's: +4.40 TWh in 2019, -12.66 in 2024). So the figures are consistent with the fuel counting wind, solar and tidal generation with hydro and nuclear, as its name does not say; StatCan states nothing on it, and a reader should not take the fuel as hydro and nuclear alone (point 2).

## Placing values in time, and what is filled

`ts_utc` is the year's 1 January at 00:00:00Z, a label for the calendar year. A figure marked "x" (49,530) or ".." (32,103) has no row, as header line 3 counts them; no line is "F". Nothing is filled. The table's MWh equal the zip's terajoules times 1,000,000/3,600 to 0.001 in every row.

## License

Header: "License: public (the Statistics Canada Open Licence; see license_verdicts.csv). Source: Statistics Canada, Table 25-10-0029-01. This does not constitute an endorsement by Statistics Canada of this product." `warehouse/metadata/license_verdicts.csv`: Statistics Canada, read 361, the Open Licence ("use, reproduce, publish, freely distribute, or sell the Information"), verdict "may be public", the same if the ERW sells anything; a value-added product carries a source line and the statement that StatCan does not endorse it, which the header carries. `docs/licenses.md`, the table's row: flag public, "agrees", ERW verdict public. Read 620 records the robots file as read 619 did: a crawl delay of 2 seconds, framework and error paths disallowed, not /n1/, no AI agent named; the file also disallows paths ending .csv, .xls and the like, which the zip is not.

## Checks (session 2380)

The figures in this note were computed from the rows of `warehouse/output/statcan_energy_balance_annual.csv`, read past its 10 header lines (counted), and from the saved zip, read only (scripts `runs/c112/s2375/notes/eb.py`, `eb2.py`, `eb3.py` and `eb4.py`, outputs `eb.out`, `eb2.out`, `eb3.out`, `eb4.out` and the metadata as `eb_meta.txt` beside them).

- 128,420 rows, 354 series, 46 variables, 1995 to 2024, as header lines 1, 3 and 10 state; no (entity, variable, ts_utc) twice; MWh throughout.
- **Against the zip:** 210,053 lines: 128,420 with a value (the table's rows), 49,530 "x" and 32,103 ".."; every unit "Terajoules", scalar factor "units", DECIMALS 0; every row's value the zip's times 1,000,000/3,600, matched by vector and year.
- **The trial against the table:** `runs/c112/s2383/trial/statcan_energy_balance_annual.csv` has the same 128,420 keys with 0 differences in value or `retrieved_at`.
- **Parts against totals** (within 1 TJ where every part is given): total industrial against its four parts in 3,273 of 3,301 cells; total manufacturing against its seven in 1,081 of 1,102; total transportation against its six in 2,562 of 2,601 (all within 7 TJ); primary energy's stock variation in 2024 is its five fuels' (14,252 TJ).
- The supply identities and signs: the section above.
- Session 2383's cross-check (`runs/c112/s2383/cross.py`, `cross.out`, run on the trial): primary energy production of the Atlantic provinces against its four within 0.1 percent in all 25 years with all four given; the provinces and territories against Canada in all 17 complete years (largest gap 0.0000); Canada's hydro and nuclear against the generation table, 2017 to 2024, as in the table above.

## The session report against the table

Every figure of `SESSION_2383_REPORT.md` checked against the table, the zip and `cross.out` holds (128,420 rows, 354 series, 1995 to 2024, 46 lines, MWh from terajoules, the two groups with a blank `geo`, `x_terminated`, 49,530 "x" and 32,103 "..", the cross-check's counts, 519.80 against 486.50 TWh in 2017, 478.54 against 423.56 in 2024, read 620, 2 requests, 2.8 MB), except:

- "29 fuels": the table holds 28 (point 4).
- "The balance's 'primary electricity' may count generation the monthly survey classes elsewhere": the gap matches wind, solar and tidal from 2016 (point 2).
- "Errors: None": the write's log ends in a failure (point 5).
- "robots, the table's zip (2.8 MB); 3 s apart": 6 seconds apart (point 6).

## Limits

- **Electricity is split across two fuels.** Supply is in two (primary, hydro and nuclear and, by the figures, wind, solar and tidal; secondary, thermal), demand in one (primary). A sum of final demand across fuels counts electricity once; a reader of primary electricity alone sees demand above supply.
- **The statistical difference of electricity changes definition in 2010** and is absent before 2005.
- **Inter-regional transfers do not cancel** at Canada's level in about a third of the fuel-years.
- **Suppression** ("x") is heavy; totals such as total primary and secondary energy have no production or availability by design (cube note 3).
- **Breaks:** the coal ranks end in 2009 (total coal continues), and cube note 2 warns against comparisons with the archived tables.

## What it does not hold

- Years before 1995 (and quarterly data, table 25-10-0004), anthracite (no value), "Secondary energy" as a fuel, energy in physical units, prices, and months (the monthly tables are `statcan_oil_gas_supply_monthly`, `statcan_petroleum_products_monthly`, `statcan_electricity_generation_monthly` and `statcan_electricity_trade_monthly`).

## Points for the session to act on

1. **Electricity's demand lines are all electricity's, and its statistical difference changes definition in 2010.** Neither the header nor the docstring says that "Secondary electricity, thermal" has only production, availability and net supply while "Primary electricity, hydro and nuclear" carries the demand of all electricity (Canada 2024: final demand 2,009,511 TJ against its own net supply of 1,677,268). Its statistical difference includes the secondary net supply from 2010 (157 of 192 cells match, Canada 2024: 23.62 TWh) and leaves it out in 2005 to 2009 (all 30 cells; Canada -97.53 to -110.95 TWh); before 2005 it has no value. A clause in header line 2 would keep a reader from taking those five years' -100 TWh as a measured imbalance or primary electricity's demand as hydro and nuclear's.
2. **"Primary electricity, hydro and nuclear" is more than hydro and nuclear, by the figures; StatCan does not say.** The report records the balance's production 33 to 55 TWh a year above the generation table's hydraulic and nuclear turbines and leaves it to this note. The metadata gives the fuel no note. From 2016 to 2024 the gap equals the generation table's wind, solar and tidal generation within 4 TWh every year (2024: 54.98 against 51.08 TWh); before 2016 the generation table's wind falls short of the gap by up to 19.57 TWh. The header could say that the fuel's production matches hydro, nuclear, wind, solar and tidal generation in 2016 to 2024, and that StatCan's metadata does not define it.
3. **The signs are not stated, and the metadata places the statistical difference under final demand.** Header line 2 could say: exports and stock variation are positive and subtracted (a positive stock variation a build); inter-regional transfers, inter-product transfers and other adjustments are signed and added; transformation lines are inputs, positive, except steam's own "Transformed to steam generation", which is its output, negative; the statistical difference is net supply less producer consumption, non-energy use and final demand. The metadata lists "Statistical difference" as a child of "Energy use, final demand" (parent member 18), but final demand is the six sectors without it (4,080 of 4,398 cells within 1 TJ; 1,297 of 3,070 with it added), so a sum of final demand's children by the metadata's tree would count the difference in.
4. **28 fuels, not 29.** The report says "29 fuels"; StatCan's file has 29, but anthracite (terminated) has no value in any line, so the table holds 28 (`x_fuel` has 28 names).
5. **The write's log ends in a failure the report does not record.** `runs/c112/s2383/write.out` ends "metadata to the branch exit=1" and "done, fail=1"; the report's Errors section says "None". The coverage, sources and archive manifest rows did reach the branch (commit 9e54e683 holds them), so what failed, and whether anything is missing, should be named.
6. **The requests were 6 seconds apart, not 3.** The report's pulls table says "3 s apart"; the probe log has 09:09:43Z and 09:09:49Z.

Compared besides, with no contradiction found: the header's and docstring's counts, years, areas and their codes, the unit and factor, the statuses counted, "Fuels and lines overlap (totals hold their parts): a sum takes one level", "Nothing is filled", `retrieved_at` and `vintage` against the probe log, the robots file, the license lines, and every row against the zip.

Acted on in session 2380: the docstring and header line 2 now state the signs, that the statistical difference is not part of final demand (whatever the metadata's tree), that electricity's demand lines under primary electricity cover all electricity, that its statistical difference leaves out secondary net supply in 2005 to 2009, and that primary electricity's production appears to hold wind, solar and tidal (StatCan does not say). Session 2383's report now gives 28 fuels with values, the requests 6 seconds apart, the write's metadata step (exit 1, joined by the resolver, nothing missing) and this note's finding on the gap. The table was written again offline: the same rows.
