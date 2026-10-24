# Azerbaijan's electricity balance, a year, 2007 to 2025, and its electricity production and plant capacity by kind of plant, 1913 to 2025 (State Statistical Committee of the Republic of Azerbaijan, Energy tables 3.1.18, 5.4 and 5.3)

Energy Research Warehouse (ERW), method note written in session 2452 (chain 118) for a table first written on 24 October 2026 (session 2450 of chain 118, its report `archive/sessions/SESSION_2450_REPORT.md`).

Tables: `statsaz_azerbaijan_electricity_annual`

## Publisher and address

State Statistical Committee of the Republic of Azerbaijan, its Energy section in English (`https://stat.gov.az/source/balance_fuel/?lang=en`, read 804; the page shows "Last updated: 08.09.2026" beside its headline indicators), three Excel 97 workbooks, three requests:

- `https://stat.gov.az/source/balance_fuel/en/003_1.18en.xls` (table 3.1.18, Electricity)
- `https://stat.gov.az/source/balance_fuel/en/005_4en.xls` (table 5.4, Production of electricity)
- `https://stat.gov.az/source/balance_fuel/en/005_3en.xls` (table 5.3, Plant capacity)

Source id `statsaz:energy`. What each holds:

- **3.1.18** has three sheets, the same 59 lines in three units: `3_1_18` ("3.1.18 Electricity", "million kWh", taken), `3_2_18` (thousand TOE) and `3_3_18` (terajoule), not taken. Columns 2007 to 2025. The lines follow the energy balance's form: Production, with Electricity plants (EP) (and under it EP (working with fuel), Hydroelectric, Wind and Solar power plants, Electricity generated from waste incineration) and CHP plants; Import; Export (negative); International bunkers (three lines); Stock changes; Total supply; Statistical difference; Transfers; Transformation input (eight lines: Electricity plants, CHP plants, Heat plants, Gas works, Blast furnaces, Oil refineries, Petrochemical plants, Other transformation processes); Energy industries own use; Losses (in transmission networks, in distribution networks); Final consumption; Final energy consumption, with Industry and construction (13 lines), Transport (Road, Rail, Domestic aviation, Domestic navigation, Pipeline, Transport not elsewhere specified), Other fields of economy (Agriculture, forestry and fishing; Commerce and pub. services; Households; Not elsewhere-specified); Non-energy use.
- **5.4**, one sheet: "5.4 Production of electricity, million kWh", rows a year (1913, 1920, 1930 to 1990 by ten, 1995, then 2000 to 2025, 36 years), columns "Production of electricity" and, under "including", "fuel-fired electricity and CHP plants", "hydroelectric power plants", "avtopro-ducers (working with fuel)", "by generator", "wind power plants", "solar power plants", "electricity generated from was-tes incine-ration", "electricity generated from bio-mass inci-neration".
- **5.3**, one sheet: "5.3 Plant capacity, MW", the same 36 years, columns "Plant capacity as of the end of the year" and, under "including", "Fuel-fired electricity and CHP plants - total", "Hydroelectric power plants", "Wind power plants", "Solar power plants", "Municipal solid waste plant", "Biogas power plants".

None of the three workbooks carries a cell note or a footnote line (every sheet read whole, this session). No workbook or page read defines "avtopro-ducers (working with fuel)" or "by generator" (point 3). The Energy page gives the signs: "« - » not applicable", "« ... » data not available", "« 0.0 » data characterized by the least number", and "Note: In some cases discrepancy between total and the summed is explained by rounding" (point 4). It says the balance follows the "International Recommendations on Energy Statistics" adopted by the UN Statistical Commission in February 2011, and links "Brief methodological guidelines for compiling energy balances", which was not read. The column heading "Plant capacity as of the end of the year" stands over every year of 5.3; nothing in the workbook qualifies it for any year.

Session 2450's probe (`runs/c118/s2450/probe.csv`) made 6 requests: www.stat.gov.az's robots file (connection reset, 12:39:52Z, read 802), stat.gov.az's robots file (HTTP 200 with the home page, 78,964 bytes, read 803), the Energy section (read 804), and the three workbooks a second apart: 3.1.18 at 12:40:25Z (86,528 bytes, Last-Modified "Mon, 07 Sep 2026 13:01:54 GMT", read 805), 5.4 at 12:40:26Z (40,960 bytes, "12:55:48 GMT", read 806) and 5.3 at 12:40:27Z (49,664 bytes, "12:46:03 GMT", read 807). All are saved in `runs/license_reads/s2450/`, each with the probe log's SHA-256 (checked in this session). The write read them offline from `warehouse/raw/statsaz_azerbaijan/20261024T123952Z_probe/` ("raw file reused", run log).

Connector: `warehouse/connectors/statsaz_azerbaijan.py` (session 2450): `[--offline] [--out-dir DIR]`, three requests, 2 seconds apart when asked. The balance's lines are taken by label, each line's variable `balance_` and its label's slug ("Commerce and pub. services" becomes `commerce_and_public_services`); a label met a second time gets `balance_transformation_` (only "CHP plants", whose second line is all dashes). 5.4's and 5.3's columns are found by their heading words in the first sheet's rows 3 and 4. Checks, each stopping the run: the balance's production is electricity plants plus CHP plants, and electricity plants are their five kinds; from 2000, 5.4's and 5.3's parts add to their totals; the balance's production equals 5.4's in each year both give; all within 1 GWh or 1 MW; a label, year or value that does not read. **No schedule runs it**: no step of `warehouse/run_daily.sh`, `warehouse/run_data_machine.sh`, `warehouse/run_data_machine_tables.sh`, `warehouse/run_monthly.sh`, `warehouse/refresh_supply.sh`, `warehouse/scheduled.py` or `.github/workflows/` names it. The table is public; it is held from the live set (listed under `catalogue_hold` in `warehouse/supabase/live_set.yaml`) and is in the release's held list (`warehouse/redivis/release_v1.py`, among the tables marked "held: not yet on Redivis ... In v1 by its license once uploaded").

## Vintage and revision

One write, run `20261024T124207Z` ("This run wrote 1067 rows: 1067 new, 0 replacing earlier rows ...; 0 rows are kept from earlier runs"), from the saved workbooks; the report records no separate trial. Each row's `source_url`, `retrieved_at` and `vintage` are its workbook's: 726 rows from 3.1.18 (retrieved 2026-10-24T12:40:25Z, `vintage` 2026-09-07T13:01:54Z), 187 from 5.4 (12:40:26Z, 2026-09-07T12:55:48Z) and 154 from 5.3 (12:40:27Z, 2026-09-07T12:46:03Z).

No figure is marked provisional; 2025 is printed like the other years. 5.3's 2025 figures alone carry two decimals (8,567.04 MW in all). Whether the Committee revises earlier years when it saves a new workbook is not known from these files; a later run asks the three addresses again and merges by (entity, variable, ts_utc).

## Shape and variables

Series, 1,067 rows, one entity `statsaz:AZ`, `geo` AZ, `freq` P1Y, `market` blank; `unit` MWh for the balance and 5.4 (million kWh times 1,000, 913 rows), MW for 5.3 (154 rows). 56 variables: 40 of the balance's 59 lines (the 19 others are "-" in every year: the three bunker lines, Stock changes, Transfers, Transformation input and its eight lines, Domestic aviation, Domestic navigation, Transport not elsewhere specified, Not elsewhere-specified, Non-energy use), 9 of 5.4 and 7 of 5.3. `node` is the balance's label, or "Production of electricity: <kind>" and "Plant capacity, end of year: <kind>" with the ERW's slug as the kind (point 1).

| Variable | Rows | The workbook's line or column |
|---|---|---|
| balance_ (36 lines) | 19 each | 3.1.18, 2007 to 2025: Production, Electricity plants (EP), EP (working with fuel), Hydroelectric power plants, CHP plants, Import, Export, Total supply, Statistical difference, Energy industries own use, Losses and its two lines, Final consumption, Final energy consumption, Industry and construction and its 13 lines, Transport, Rail, Pipeline, Other fields of economy and its three lines |
| balance_wind_power_plants | 15 | 2009, 2010, 2013 to 2025 |
| balance_solar_power_plants, balance_electricity_generated_from_waste_incineration | 13 each | 2013 to 2025 |
| balance_road | 1 | 2025 (27.5 million kWh) |
| production_total, capacity_total, capacity_fuel_fired_and_chp | 36 each | 1913 to 2025 |
| production_fuel_fired_and_chp, production_hydro | 33 each | from 1940 ("..." before) |
| production_autoproducers_fuel | 30 | from 1970: "avtopro-ducers (working with fuel)" |
| production_by_generator | 7 | 2000 to 2006: "by generator" |
| production_wind, capacity_wind | 15 each | 2009, 2010, 2013 to 2025 |
| production_solar, production_waste_incineration, capacity_solar, capacity_municipal_solid_waste | 13 each | 2013 to 2025 |
| production_biomass_incineration | 7 | 2015 to 2020 and 2023, every cell shown as "0.0" |
| capacity_hydro | 31 | from 1960 |
| capacity_biogas | 10 | 2015 to 2024 |

The balance, million kWh as printed (`runs/c118/s2452/notes/az2.out`):

| Year | Production | Import | Export | Total supply | Own use | Losses | Final consumption | of which households | Statistical difference |
|---|---|---|---|---|---|---|---|---|---|
| 2007 | 21,847.2 | 547.8 | -785.7 | 21,609.3 | 2,198.7 | 3,432.0 | 15,844.4 | 8,334.2 | 134.2 |
| 2010 | 18,709.5 | 99.8 | -462.4 | 18,346.9 | 2,158.8 | 3,830.1 | 12,233.7 | 5,755.3 | 124.3 |
| 2015 | 24,688.4 | 107.5 | -265.0 | 24,530.9 | 3,935.7 | 2,868.6 | 17,619.1 | 7,937.9 | 107.5 |
| 2020 | 25,839.1 | 136.5 | -1,150.7 | 24,824.9 | 3,740.5 | 2,042.2 | 19,019.2 | 7,118.0 | 23.0 |
| 2022 | 29,039.8 | 137.1 | -2,997.4 | 26,179.5 | 3,719.4 | 2,185.6 | 20,258.7 | 6,569.1 | 15.8 |
| 2023 | 29,305.9 | 212.0 | -3,245.7 | 26,272.2 | 3,864.7 | 2,238.0 | 20,158.0 | 6,625.8 | 11.5 |
| 2024 | 28,412.6 | 170.7 | -1,396.2 | 27,187.1 | 3,530.1 | 2,253.5 | 21,391.8 | 7,034.2 | 11.7 |
| 2025 | 28,683.0 | 177.4 | -1,148.1 | 27,712.3 | 3,906.8 | 2,275.1 | 21,519.6 | 7,040.8 | 10.8 |

Production by kind, million kWh: the balance's and 5.4's, 2013 and 2025:

| | 2013 | 2025 |
|---|---|---|
| 3.1.18: EP (working with fuel) | 13,256.1 | 15,746.6 |
| 3.1.18: CHP plants | 8,473.5 | 9,099.1 |
| 5.4: fuel-fired electricity and CHP plants | 20,065.6 | 22,878.3 |
| 5.4: avtopro-ducers (working with fuel) | 1,664.0 | 1,967.4 |
| Hydro (both) | 1,489.1 | 2,842.5 |
| Wind, solar, waste incineration (both) | 0.8, 0.8, 134.1 | 172.3, 600.4, 222.1 |
| Production (both) | 23,354.4 | 28,683.0 |

Plant capacity at the end of the year, MW (5.3):

| Year | Total | Fuel-fired and CHP | Hydro | Wind | Solar | Municipal solid waste | Biogas |
|---|---|---|---|---|---|---|---|
| 2018 | 7,828.9 | 6,552.2 | 1,130.8 | 66.0 | 34.9 | 44.0 | 1.0 |
| 2020 | 7,621.6 | 6,326.1 | 1,149.4 | 66.0 | 35.1 | 44.0 | 1.0 |
| 2022 | 7,976.9 | 6,652.3 | 1,164.7 | 64.0 | 51.2 | 44.0 | 0.7 |
| 2023 | 7,907.4 | 6,323.1 | 1,209.4 | 64.0 | 266.2 | 44.0 | 0.7 |
| 2024 | 7,115.1 | 5,698.5 | 1,062.3 | 64.0 | 257.6 | 32.0 | 0.7 |
| 2025 | 8,567.04 | 6,857.04 | 1,118.56 | 303.8 | 255.64 | 32.0 | (-) |

- **The balance closes exactly.** In every year 2007 to 2025: total supply is production plus import plus export (export negative); the statistical difference is total supply less own use, losses and final consumption; losses are transmission plus distribution; final consumption equals final energy consumption; final energy consumption is industry and construction, transport and other fields; each of those is its lines (0.0 million kWh off in every case, this session).
- **Autoproducers sit inside the balance's fuel lines, beside 5.4's fuel-fired column.** 5.4's parts add to its total with "avtopro-ducers" as a separate part, and the balance's EP (working with fuel) plus CHP plants equal 5.4's fuel-fired and CHP plus avtopro-ducers in every year 2007 to 2025 (within 0.8 million kWh in 2007 to 2009 and 0.1 in 2012, 5.4 printing whole numbers then; exactly from 2013). So `production_fuel_fired_and_chp` leaves out 1,967.4 million kWh in 2025 (6.9 percent of production) that the balance counts as fuel-fired (point 3). The autoproducers' 301.0 million kWh of 2011 become 1,630.0 in 2012, the year the balance's own use rises from 2,247.1 to 3,605.9; the workbooks do not link the two.
- **Exports peak in 2022 and 2023** (2,997.4 and 3,245.7 million kWh, 10.3 and 11.1 percent of production) and fall back to 1,148.1 in 2025.
- **Losses fall by a third:** 3,432.0 million kWh in 2007 (17.7 percent of supply less own use) to 2,275.1 in 2025 (9.6 percent).
- **Capacity drops 792.3 MW in 2024, then rises 1,451.94 MW in 2025**, with fuel-fired capacity from 6,323.1 to 5,698.5 to 6,857.04 MW and wind from 64.0 to 303.8; the workbook gives no reason.

## Placing values in time, and what is filled

`ts_utc` is the year's 1 January at 00:00:00Z, a label for the calendar year, 1913-01-01 to 2025-01-01. The balance and production are the year's energy; capacity is at the end of the year, as 5.3's heading says for every year. Before 2000 only single years are given (1913, 1920, 1930 to 1990 by ten, 1995); 1913 to 1930 have a total and no parts in 5.4 ("..."). A "-" (not applicable) or "..." (not available) has no row; nothing is filled. Cells shown "0.0" are kept as their stored value (point 4).

## License

Header: "License: public with the source cited (the record's verdict, may be public): the site reads \"It is necessary to refer to the information on the site..!\". Cite: State Statistical Committee of the Republic of Azerbaijan, stat.gov.az." The Energy section's saved page (read 804) ends "It is necessary to refer to the information on the site..!" and, above the signs, reads "In cases of using statistics in publications and printing works, it should be referred to the State Statistical Committee of the Republic of Azerbaijan." The Azerbaijani footer of the home page saved as the robots answer (read 803) reads "... istinad etmək zəruridir..!". `warehouse/metadata/license_verdicts.csv`: the Committee, read 804, verdict "may be public", the same if the ERW sells anything. `warehouse/metadata/license_reads.csv` records reads 802 to 807 (session 2450). `docs/licenses.md`, the table's row: verdict today "may be public", flag public, "agrees", if the ERW sells anything "may be public", ERW verdict public. The report asks Samuel whether the figures should be public.

## Checks (session 2452)

The figures in this note were computed from the rows of `warehouse/output/statsaz_azerbaijan_electricity_annual.csv`, read past its 10 header lines (counted), and from the three saved workbooks and the Energy page, read only with xlrd from their bytes (scripts `runs/c118/s2452/notes/az_dump.py`, `az.py`, `az2.py`, `az_fmt.py` and `html_text.py`, outputs `az04.txt`, `az05.txt`, `az06.txt`, `az03.txt`, `az.out` and `az2.out` beside them).

- 1,067 rows, 56 variables, 1913 to 2025, as header lines 1, 3 and 10 state; one entity; no (entity, variable, ts_utc) twice; no blank value.
- **Against the workbooks:** an independent read of every numeric cell of the lines and columns taken gives exactly the table's 1,067 keys and values, times 1,000 where MWh (0 missing, 0 extra, 0 differences).
- **3.1.18 against 5.4's total:** equal from 2013; 0.2, 1.0, 0.8, 0.3, -0.2 and 0.1 million kWh apart in 2007 to 2012 (header line 3: "within 1.0 GWh").
- **5.4 and 5.3 before 2000:** the parts add to the totals in every year they are printed (1940 to 1995 for 5.4, 1913 to 1995 for 5.3), though the connector checks only from 2000.
- **Formats:** every cell of 5.4's biomass column has the number format "0.0"; the four non-zero cells hold 0.0005, 0.0002, 0.0004 and 0.0006 (2015 to 2018).
- Session 2450's cross-check (`runs/c118/s2450/cross.py`, `cross.out`): the balance's total supply against `owid_ember_electricity_annual`'s Azerbaijan demand in 2010, 2015, 2020, 2022, 2023 and 2024: 0.2, 0.5, 0.3, 0.4, 0.8 and 2.2 percent above (2023: 26.27 against 26.06 TWh; 2024: 27.19 against 26.61).

## The session report against the table

Every figure of `SESSION_2450_REPORT.md` checked against the table, the workbooks and `cross.out` holds (1,067 rows, 56 variables, the three tables and their years, the single years before 2000, MWh and MW, the checks, 1.0 GWh, reads 802 to 807, the footer in both languages, the connection reset and the robots answer, 26.27 against 26.06 and 27.19 against 26.61 TWh, -2,997.4 and -3,245.7 million kWh, 6 requests of 15, a second apart), except:

- "within 0.2 to 0.8 per cent from 2010 to 2023": `cross.out` covers 2010, 2015, 2020, 2022 and 2023 only, not every year (point 5).

## Limits

- **Two levels in one table.** The balance's lines hold their parts, and 5.4's and 5.3's totals hold theirs; a sum takes one level, and final consumption and final energy consumption are the same figure.
- **The kinds of plant differ between the tables.** The balance splits fuel-fired production into electricity plants and CHP plants, with autoproducers inside; 5.4 puts autoproducers apart; 5.3 has no autoproducer column, and whether its fuel-fired capacity includes them is not said.
- **"0.0" is the least number, not zero,** and "-" is not applicable.
- **Undefined columns:** "avtopro-ducers (working with fuel)" and "by generator" (2000 to 2006).

## What it does not hold

- The balance in thousand TOE and terajoules (sheets `3_2_18`, `3_3_18`), the other energy products' balances, the energy accounts, consumption by region, and the balance before 2007.

## Points for the session to act on

1. **The docstring's `node` is not what the table holds.** The docstring reads "entity statsaz:AZ; geo AZ; node Azerbaijan". The code writes the balance's label as `node` ("Total supply", "Commerce and pub. services") and, for 5.4 and 5.3, "Production of electricity: <kind>" or "Plant capacity, end of year: <kind>" with the ERW's slug ("Production of electricity: autoproducers_fuel"), not the workbook's column heading. The docstring could say so, or the node could carry the workbook's heading.
2. **Header line 2 lists a line that has no row.** It names "transformation input" among the `balance_<line>` variables; Transformation input and its eight lines are "-" in every year, as are 10 other lines (19 of 59 in all), and none has a row. The docstring's "every line with a value" is right. The header could drop "transformation input" or list the 19 lines that are all "-".
3. **`production_fuel_fired_and_chp` leaves out the autoproducers, which the balance's fuel lines include; neither column is defined.** Header line 2 and the docstring give 5.4 as "the total and its parts by kind of plant". 5.4's parts add to its total with "avtopro-ducers (working with fuel)" and, in 2000 to 2006, "by generator" as separate parts; the balance's EP (working with fuel) plus CHP plants equal 5.4's fuel-fired and CHP plus avtopro-ducers in every year 2007 to 2025 (exactly from 2013). Taken alone, `production_fuel_fired_and_chp` misses 1,967.4 million kWh of fuel-fired production in 2025 (6.9 percent). No workbook or page read defines either column. The header could say that `production_autoproducers_fuel` is fuel-fired output of autoproducers outside 5.4's fuel-fired column, and that `production_by_generator` is undefined.
4. **"-" is "not applicable", and "0.0" is "the least number".** The docstring reads 'A dash ("-", nil) or "..." (not available) has no row'. The Energy page's signs read "« - » not applicable", "« ... » data not available", "« 0.0 » data characterized by the least number". All seven cells of 5.4's biomass column are shown "0.0": four hold 0.0005 to 0.0006 million kWh and three (2019, 2020, 2023) hold 0, so the table has four rows of 0.2 to 0.6 MWh and three zeros where the Committee prints a figure too small to show. The docstring could take the page's words, and the header say what the biomass rows are.
5. **The report claims more years than its cross-check compared.** "within 0.2 to 0.8 per cent from 2010 to 2023 (2023: 26.27 against 26.06 TWh), and 2.2 per cent above in 2024": `runs/c118/s2450/cross.out` prints 2010, 2015, 2020, 2022, 2023 and 2024 only. "in the years compared (2010, 2015, 2020, 2022 and 2023)" would be what was checked.

Compared besides, with no contradiction found: the header's and docstring's counts, years, units, the factor of 1,000, the single years before 2000, "export (negative, as printed)", "end of year" (5.3's heading, over every year), the checks and "within 1.0 GWh", "The balance's lines and the kinds overlap (totals hold their parts): a sum takes one level", the sheets in thousand TOE and terajoules not taken, `retrieved_at` and `vintage` against the probe log, the robots answers, the footer as quoted, and every row against the workbooks.

Acted on in session 2452: the docstring now gives the node as the table holds it; calls "-" "not applicable" and "0.0" "the least number", as the Committee's page does, and names the biomass cells; and says that table 5.4's fuel-fired and CHP part leaves out the autoproducers, which the balance's fuel lines hold, neither autoproducers nor "by generator" being defined. Header line 2 no longer lists transformation input as a line with rows. Session 2450's report is corrected on the years its cross-check compared. The table was written again offline: the same rows.
