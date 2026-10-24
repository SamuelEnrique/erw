# Shale gas proved reserves and their yearly changes, the U.S., the states and the reporting districts, 2007 to 2021, a closed record (EIA, U.S. Crude Oil and Natural Gas Proved Reserves)

Energy Research Warehouse (ERW), method note written in session 2247 (chain 101) for a table first written on 24 October 2026 (session 2250 of chain 101, its report `archive/sessions/SESSION_2250_REPORT.md`).

Tables: `eia_shale_gas_reserves_annual`

## Publisher and address

U.S. Energy Information Administration (EIA), U.S. Crude Oil and Natural Gas Proved Reserves, shale gas, through EIA's API v2, route `natural-gas/enr/shalegas`, annual. The header's page is the route itself, `https://api.eia.gov/v2/natural-gas/enr/shalegas/`. The connector asks `https://api.eia.gov/v2/natural-gas/enr/shalegas/data/?frequency=annual&data[]=value&facets[process][]=R5301&...&facets[process][]=R53R02&start=2007` (each row's `source_url`), in pages of 5,000, with EIA's key (read from `.env`, never saved; `REDACTED` in every saved address). Source id `eia:natural-gas/enr/shalegas`.

Eleven processes, all of product EPG0 "Natural Gas", unit "BCF": R5301 "Shale, Proved Reserves", R5302 "Shale, Reserves Based Production", R5303 and R5304 revision increases and decreases, R5305 sales, R5306 acquisitions, R5307 extensions, R5307A "Extensions and Discoveries", R5308 new field discoveries, R5309 new reservoir discoveries in old fields, R53R02 adjustments. The route answers 45 areas: NUS, R48 (lower 48), RUSF (lower 48 federal offshore), 22 states (`S<state>`) and 20 districts (California's RCAC, RCAJ and RCASF, Louisiana's RLAN and RLASO, New Mexico's RNMEAST and RNMWEST, Texas's RTX01 to RTX10 with 07B, 07C and 08A, and RTXSF).

Session 2250 listed the petroleum and natural gas routes (`runs/c101/s2250/routes.json`; `routes.py`, `routes2.py`), and asked the shale route's metadata and one page of all its data (`sample.py`, saved as `sample.json`: 5,000 of EIA's 5,247 records, with EIA's warning "incomplete return"). No page of EIA's was saved under `runs/license_reads/`; EIA's verdict is read 1. The trial's two data pages are in `warehouse/raw/eia_shale_gas_reserves/20261024T035058Z/`.

Connector: `warehouse/connectors/eia_shale_gas_reserves.py` (session 2250, made from the crude quality connector): `[--from 2007] [--offline | --fresh] [--out-dir DIR]`, at most 10 requests a run, 3 seconds apart; a page saved in `warehouse/raw` is reused unless `--fresh`. A process, unit or area not in its map, or a key given twice, stops the run; a record without a number has no row. **No schedule runs it**: no step of `warehouse/run_daily.sh`, `warehouse/run_data_machine.sh`, `warehouse/run_data_machine_tables.sh`, `warehouse/run_monthly.sh`, `warehouse/refresh_supply.sh`, `warehouse/scheduled.py` or `.github/workflows/` names it.

## Vintage and revision

The two pages were fetched by session 2250's trial (run `20261024T035058Z`) at 2026-10-24T03:51:02Z and 03:51:06Z (the raw manifest; 1,647,069 and 84,321 bytes). The table is run `20261024T035332Z`, written from them with "0 requests of 10": "File holds 4455 rows, one snapshot; the previous file held 0 rows."

`retrieved_at` is 2026-10-24T03:53:32Z in every row, the write's start, not the pages' time (disagreement 3); `vintage` is blank. The route's data end in 2021: every record of the pages and of the sample is dated 2007 to 2021. The header and report call the table a closed record. A run replaces the whole file, so a value EIA revises or adds would arrive whole at the next run.

## Shape and variables

Series, 4,455 rows, 469 entities `eia_shale_gas_reserves:RES_EPG0_<process>_<area>_BCF` (EIA's series id), 11 variables, all in `bcf`; `freq` P1Y, `market` blank, `node` EIA's series description. 43 areas have rows: the U.S. (122 rows), the lower 48 (122), the federal offshore (8), 20 states (2,199) and the 20 districts (2,004). New York and Utah are in the route but every record of theirs is empty, so they have no row.

| Variable | EIA's process | Rows | Series | Years | Zeros | Negative |
|---|---|---|---|---|---|---|
| proved_reserves | R5301 | 543 | 43 | 2007 to 2021 | 99 | 0 |
| reserves_based_production | R5302 | 543 | 43 | 2007 to 2021 | 110 | 0 |
| revision_increases | R5303 | 478 | 43 | 2009 to 2021 | 105 | 0 |
| revision_decreases | R5304 | 478 | 43 | 2009 to 2021 | 108 | 0 |
| sales | R5305 | 478 | 43 | 2009 to 2021 | 209 | 0 |
| acquisitions | R5306 | 478 | 43 | 2009 to 2021 | 219 | 0 |
| extensions | R5307 | 251 | 42 | 2009 to 2015 | 67 | 0 |
| new_field_discoveries | R5308 | 251 | 42 | 2009 to 2015 | 203 | 0 |
| new_reservoir_discoveries_in_old_fields | R5309 | 251 | 42 | 2009 to 2015 | 175 | 0 |
| extensions_and_discoveries | R5307A | 226 | 42 | 2016 to 2021 | 83 | 0 |
| adjustments | R53R02 | 478 | 43 | 2009 to 2021 | 81 | 139 |

- **2007 and 2008 hold only proved reserves and production** (62 rows a year); the changes begin in 2009. Rows a year: 62, 62, 310, 330, 324, 372, 380, 400, 400, 320, 296, 303, 304, 296 and 296.
- **The discoveries change form in 2016.** Extensions and the two kinds of discoveries are given apart to 2015; from 2016 EIA gives only their total, R5307A, and its records of R5307, R5308 and R5309 for 2016 to 2021 are empty (720 of the 792 empty records). A reader wanting one series from 2009 to 2021 adds the three parts to 2015 and takes R5307A after.
- **Zeros and gaps.** Alaska's reserves and production are 0 in every year it has (30 rows), so the U.S. equals the lower 48 in every year; the federal offshore has rows only for 2019, all 0. Nine area-years are empty in every process (72 records): California's three districts in 2018, New Mexico's two districts and Kentucky in 2017, California in 2019, and New York and Utah in 2019; the states with proved reserves number 16 a year to 2011, 18 to 20 after.
- Adjustments are the only measure with negative values (139 rows); revision decreases and sales are given as positive amounts that reduce reserves.

| Year | U.S. proved reserves | U.S. reserves-based production |
|---|---|---|
| 2007 | 23,304 | 1,293 |
| 2008 | 34,428 | 2,116 |
| 2009 | 60,644 | 3,110 |
| 2010 | 97,449 | 5,336 |
| 2011 | 131,616 | 7,994 |
| 2012 | 129,396 | 10,371 |
| 2013 | 159,115 | 11,415 |
| 2014 | 199,684 | 13,447 |
| 2015 | 175,601 | 15,213 |
| 2016 | 209,809 | 17,032 |
| 2017 | 307,903 | 18,589 |
| 2018 | 342,135 | 22,054 |
| 2019 | 353,086 | 25,556 |
| 2020 | 317,756 | 26,139 |
| 2021 | 393,779 | 27,985 |

bcf. Reserves fell in 2012, 2015 and 2020.

## Placing values in time, and what is filled

`ts_utc` is 1 January of EIA's `period` (YYYY) at 00:00:00Z (Decision 11), a label for the year. The header says the reserves are "as of 31 December" of that year; the pages' descriptions do not say so. Production and the changes are the year's flows. The pages hold 5,247 records (EIA's `total`): 4,455 with a number, which are the table's rows (0 keys and 0 values differ), and 792 empty (`null`), which have no row. Nothing is filled.

## The geo of each area

`geo` is US for NUS, R48 and RUSF, and `US-<state>` for a state or a district within one. EIA's `area-name` cannot check the districts: the pages and the sample give "NA" for every district and for R48 and RUSF, and for the states "USA-<state>" or the state's name in capitals (CALIFORNIA, COLORADO, OHIO, TEXAS). The series descriptions name each area, and every district's names its state: "California - Coastal Region Onshore", "California--San Joaquin Basin Onshore", "California State Offshore", "Louisiana--North", "Louisiana--South Onshore", "New Mexico--East", "New Mexico--West", "Texas--RRC District 1" to "10" (2, 3 and 4 "onsh") and "Texas--State Offshore". The mapping holds for all 43 areas with rows, and the sample's 45 area names equal the pages'.

The districts add up to their state exactly: Texas's thirteen, California's three, Louisiana's two and New Mexico's two equal the state's proved reserves in every year both have (largest difference 0). So the table holds each of these four states twice under one `geo`, as the header warns.

## License

Header: "License: public (a work of the U.S. government; cite "U.S. Energy Information Administration, U.S. Crude Oil and Natural Gas Proved Reserves")." `docs/licenses.md` and `warehouse/metadata/license_verdicts.csv`: read 1 (EIA's copyrights and reuse page, `https://www.eia.gov/about/copyrights_reuse.php`), "U.S. government publications are in the public domain and are not subject to copyright protection. You may use and/or distribute any of our data, files, databases, reports, graphs, charts, and other information products that are on our website or that you receive through our email distribution service.", verdict "may be public", if the ERW sells anything "may be public"; EIA asks for the acknowledgment "Source: U.S. Energy Information Administration" with the date. The table's row: flag public, "agrees", ERW verdict public.

## Checks (session 2247)

The figures in this note were computed from the rows of `warehouse/output/eia_shale_gas_reserves_annual.csv`, read past its 10 header lines (counted), and from the saved pages and sample, read only (scripts `runs/c101/s2247/shale.py`, `shale2.py` and `shale3.py`, outputs beside them).

- 4,455 rows, `ts_utc` from 2007-01-01T00:00:00Z to 2021-01-01T00:00:00Z, "5,247 records of EIA's, 4,455 rows", as header line 3 states; 469 series; no (entity, variable, ts_utc) twice; no blank value; unit bcf throughout; each row's `node` is the page's series description.
- **Against the pages:** EIA's `total` is 5,247 on both pages (5,000 and 247 records), every record dated 2007 to 2021; the table's keys and values are the pages', with 0 differences. The sample holds the same 45 areas, its records likewise 2007 to 2021.
- **The trial against the table:** `runs/c101/s2250/trial/eia_shale_gas_reserves_annual.csv` has the same keys and the same values in every column but `retrieved_at` (03:50:58Z in the trial, 03:53:32Z in the table).
- Session 2250's cross-check (`runs/c101/s2250/cross.py`), run again from the main checkout with the written table as argument 1: its output is identical to the saved `cross.out`, which was run on the trial. U.S. reserves against last year's plus extensions and discoveries, revisions, acquisitions less sales, adjustments, less production: a gap of 0 in every year 2009 to 2021 but 2020, when the reported 317,756 bcf is 596 above the computed 317,160. The states' proved reserves summed against the U.S.: 0.997 (2007), 0.998, 0.998, 0.999, 0.999, then 0.999 to 1.000 from 2012 (2021: 393,777 against 393,779).
- **The balance for every area** (`shale2.py`, last year's reserves taken only where last year has a row): 455 of 463 area-years close within 0.5 bcf. The eight that do not: the U.S. and the lower 48 in 2020 (596), New Mexico and New Mexico East in 2020 (586), Texas in 2020 (10) with its districts 7C (2) and 8 (8), and Texas district 7B in 2009 (1). So 2020's 596 bcf is New Mexico East's 586 and Texas's 10.
- **The states against the U.S.:** the U.S. equals the lower 48 plus the federal offshore in every year (Alaska and the federal offshore being 0); the states' sum is 0.9972 to 1.0000 of the lower 48, the shortfall largest in the early years (66 bcf in 2007, 123 in 2014, 2 in 2021). No area in the pages explains it; the states with rows are all the states the route gives a number for.

## Where the description and the data disagree

1. **The header's access line is not the request.** Header line 8 gives `.../shalegas/data/?frequency=monthly&data[]=value&start=2007`. The route is annual (the connector asks `frequency=annual`, the rows' `source_url` say so), and the requests name the eleven processes. The docstring's address says `frequency=annual`; the header's template was not changed from the crude quality connector's.
2. **Header line 3 counts "Months 2007-01 to 2021-01".** The table holds years, 2007 to 2021, labelled at 1 January.
3. **`retrieved_at` is the run's start, not the retrieval.** As in the other EIA tables of this chain: the rows say 2026-10-24T03:53:32Z, a run that asked nothing ("0 requests of 10"); the trial's say 03:50:58Z, four seconds before its first page; EIA served the pages at 03:51:02Z and 03:51:06Z. Header line 10 says `retrieved_at` says where a row came from.
4. **"EIA's metadata gives 2007 to 2021" cannot be checked from what was kept.** `sample.py` printed the route's start and end and the production route's, but neither answer nor its printout was saved in `runs/c101/s2250/`. What was kept agrees: every record in the two pages and in the sample is dated 2007 to 2021. That the shale production route also ends in 2021 rests on the session's word alone.

Compared besides, with no contradiction: the docstring's processes, variables, areas, districts and geo rule, the header's span, unit, row and record counts and "a blank has no row", against the rows, the pages and the sample.

Not acted on: this note changes no file but itself.

Acted on in session 2247. The header's access address now says frequency=annual with the eleven processes, as the requests did, and its third line says years. The connector now stamps each row with the time EIA served its page (a reused page's first download, kept by `ip.raw_cached`), not the time the write began; the table was written again offline (no request, the same rows), and its rows now carry EIA's serving times. Session 2247's report corrects session 2250's "23 states" (20 with rows) and its federal offshore (rows only for 2019, all 0).

## The session report against the table

Every figure of `SESSION_2250_REPORT.md` checked against the table, the saved pages and sample and the rerun cross-check holds (2007 to 2021, 4,455 rows, 469 series, bcf, the measures named, the U.S. balance exact in every year 2009 to 2021 but 2020, 2020's 596 bcf, the states' sum 0.997 to 1.000 of the U.S., 23,304 bcf in 2007 and 393,779 in 2021, production 1,293 and 27,985 bcf, 11 requests), except:

- "Areas: the U.S., the lower 48, the federal offshore, 23 states": the route gives 22 states and the table holds 20 (New York and Utah have only empty records). The federal offshore has one year, 2019, all 0.
- "EIA's route gives 2007 to 2021, and its shale gas production route also ends in 2021": the data do; the metadata and the production route were not saved (disagreement 4).
- "2020 is EIA's own": it is; the table shows where, New Mexico East (586 bcf) and Texas districts 7C and 8 (10 bcf).

## What it does not hold

- Years after 2021 (the route has none) and before 2007, the changes for 2007 and 2008, New York and Utah, the other proved reserves EIA publishes (all gas, crude oil, coalbed methane), and shale gas production other than the reserves-based figure.
