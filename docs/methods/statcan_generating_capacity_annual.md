# Canada's installed electricity generating capacity by type of generation and class of producer, by province, a year, 2006 to 2025 without 2012 (Statistics Canada, table 25-10-0022-01, the Annual Electric Power Generating Stations Survey)

Energy Research Warehouse (ERW), method note written in session 2415 (chain 114) for a table first written on 24 October 2026 (session 2418 of chain 114, its report `archive/sessions/SESSION_2418_REPORT.md`).

Tables: `statcan_generating_capacity_annual`

## Publisher and address

Statistics Canada (StatCan), table 25-10-0022-01 (formerly CANSIM 127-0009), "Installed plants, annual generating capacity by type of electricity generation" (`https://www150.statcan.gc.ca/t1/tbl1/en/tv.action?pid=2510002201`), read from the table's full CSV download, one request:

- `https://www150.statcan.gc.ca/n1/tbl/csv/25100022-eng.zip`

Source id `statcan:25-10-0022-01`. The zip (93,501 bytes) holds `25100022.csv` (1,172,178 bytes, 6,655 lines of data) and `25100022_MetaData.csv` (5,020 bytes), both dated 19 October 2026 inside the zip. The metadata gives the frequency Annual, the reference periods 2006-01-01 to 2025-01-01, three dimensions (geography, 14 members; class of electricity producer, 4; type of electricity generation, 12), one survey (2193, the Annual Electric Power Generating Stations Survey), no cube note and no correction. Its notes define the members:

- Note 1 (public and private utilities): "A utility is an organization that, as its prime purpose, generates, transmits and/or distributes electric energy for sale. It can be private or public (provincial or municipal)."
- Note 2 (industries): "Establishments that are not part of the electric power generation, transmission and distribution industry (North American Industry Classification System (NAICS): 22111)."
- Note 3 (total installed capacity): "The capacity measured at the output terminals of all generating units in a station, without deducting station service requirements."
- Notes 4 to 11 define the hydraulic, wind, tidal, solar, conventional steam, nuclear steam, combustion and internal combustion types. Note 7, solar: "Starting in 2024, solar capacity totals also include systems below 100 kW. Previously, only surveyed systems of 100 kW and above were covered."
- Note 12 (on the type dimension): "Beginning in 2015, a large number of renewable energy companies engaged in solar, wind, hydro and other renewable technologies were added to the survey's overall target population. As a result, the number of establishments surveyed increased from 400 to 1200 establishments. Consequently, users should use caution when making historical comparisons with the data prior to 2015."

Geothermal and other non-combustibles have no note. No note says at what date in the year capacity is measured, or whether it is nameplate.

Session 2418's probe (`runs/c114/s2418/probe.csv`) made 2 requests to www150.statcan.gc.ca, 11 seconds apart: the robots file (11:01:44Z, read 761) and the zip (HTTP 200, 93,501 bytes, at 2026-10-24T11:01:55Z, Last-Modified "Mon, 19 Oct 2026 12:30:44 GMT", read 762). Both are saved in `runs/license_reads/s2418/`; the zip was seeded into `warehouse/raw/statcan_generating_capacity/20261024T110119Z_probe/`, and the trial and the write read it from there ("raw file reused" in both logs).

Connector: `warehouse/connectors/statcan_generating_capacity.py` (session 2418): `[--offline] [--out-dir DIR]`, one request, asked again unless `--offline`. A unit other than "Kilowatts", a scalar factor other than "units", an area, class or type not in its maps, a year that does not read, a status other than blank, "..", "x" or "F", a key given twice or a zip not holding `25100022.csv` alone stops the run. Kilowatts are written as MW (divided by 1,000, rounded to 0.001). Each total and total thermal is compared with its types, and the cells off by more than 1 MW are listed in the run log; they do not stop the run. **No schedule runs it**: no step of `warehouse/run_daily.sh`, `warehouse/run_data_machine.sh`, `warehouse/run_data_machine_tables.sh`, `warehouse/run_monthly.sh`, `warehouse/refresh_supply.sh`, `warehouse/scheduled.py` or `.github/workflows/` names it. The table is public; it is held from the live set (listed under `catalogue_hold` in `warehouse/supabase/live_set.yaml`) and from the Redivis release (`STORAGE_HELD` in `warehouse/redivis/release_v1.py`).

## Vintage and revision

One write, run `20261024T110253Z` ("File holds 5952 rows, one snapshot; the previous file held 0 rows"), from the saved zip. `retrieved_at` is 2026-10-24T11:01:55Z and `vintage` the zip's Last-Modified, 2026-10-19T12:30:44Z, in every row. StatCan marks 180 lines "r" (revised), all of them 2013's; no line is "p" (preliminary). Each run asks the zip again and writes the whole table.

## Shape and variables

Series, 5,952 rows, 55 entities `statcan_cap:<area>:<class>`, 12 variables `capacity_<type>`, 392 (entity, variable) series, `unit` MW, `freq` P1Y, `market` blank, `geo` CA or CA-<code> (the ten provinces and three territories), `node` "<area>: <class>: <type>", `x_class`, `x_type`, `x_vector`, `x_symbol` ("r" on 180 rows, all 2013) and `x_terminated` (blank in every row: no member is terminated). Classes: all, public utilities, private utilities, industry.

| Variable | Rows | First | Last | Zeros |
|---|---|---|---|---|
| capacity_total | 988 | 2006 | 2025 | 1 |
| capacity_hydraulic_turbine | 698 | 2006 | 2025 | 1 |
| capacity_wind_power_turbine | 663 | 2006 | 2025 | 8 |
| capacity_tidal_power_turbine | 60 | 2006 | 2021 | 8 |
| capacity_solar_power | 319 | 2007 | 2025 | 4 |
| capacity_geothermal | 12 | 2023 | 2025 | 0 |
| capacity_other_non_combustibles | 43 | 2018 | 2025 | 5 |
| capacity_total_thermal | 927 | 2006 | 2025 | 4 |
| capacity_conventional_steam_turbine | 707 | 2006 | 2025 | 5 |
| capacity_nuclear_steam_turbine | 160 | 2006 | 2025 | 0 |
| capacity_combustion_turbine | 668 | 2006 | 2025 | 18 |
| capacity_internal_combustion_turbine | 707 | 2006 | 2025 | 18 |

**No figure for 2012.** All 322 lines of 2012 in StatCan's file are marked ".." (not available), so the table has no row for 2012; the metadata gives no note on it. Rows a year: 287 (2006), 304, 288, 290, 295, 298 (2011), none (2012), 296 (2013), 304, 306, 307 (2016), 306 (2017), 314, 317, 322, 323, 326, 345, 361 and 363 (2025).

**The 2017 count.** StatCan's file lists 322 cells for each of 2012 to 2016 and 306 for 2017. The 16 not listed in 2017 are the 15 cells marked ".." in 2016 and New Brunswick's private utilities' conventional steam turbine, which has a value in 2016 (180,000 kW) and is ".." again from 2018; all 16 are listed again in 2018, 6 of them with a value. The table's rows do not drop: 307 in 2016 and 306 in 2017. The metadata does not explain why 2017 lists no ".." cell.

**The span.** The metadata's reference periods are 2006-01-01 to 2025-01-01, the table's first and last years; it does not say whether earlier years are in an archived table.

Canada, all classes, MW as the table holds them (StatCan's kilowatts divided by 1,000, rounded here):

| Year | Total | Hydraulic | Wind | Solar | Nuclear | Total thermal |
|---|---|---|---|---|---|---|
| 2006 | 123,003 | 72,644 | 1,470 | | 13,345 | 48,885 |
| 2011 | 130,672 | 75,403 | 4,477 | 144 | 13,345 | 50,628 |
| 2016 | 144,375 | 80,449 | 11,974 | 2,086 | 14,033 | 49,847 |
| 2019 | 145,538 | 81,400 | 13,022 | 1,415 | 14,101 | 49,681 |
| 2024 | 155,749 | 83,022 | 17,738 | 5,288 | 12,939 | 49,649 |
| 2025 | 155,906 | 83,037 | 18,382 | 5,729 | 11,907 | 48,705 |

**Totals hold their parts** (within 1 MW): each total its seven types and each total thermal its four, in all 1,915 cells with a total (988 and 927); public plus private utilities plus industry equal all classes in all 830 cells where the four are given; the provinces and territories equal Canada in all 55 cells where the fourteen are given. Where a class or an area is "..", the parts fall short of the total (12 of 698 Canada cells by more than 1 MW).

## Solar, and the capacity factor of 2019

Session 2418's cross-check gives Canada's solar capacity factor (the year's generation in `statcan_electricity_generation_monthly` over the capacity times the year's hours) as 0.198 in 2019 and does not explain it. From 2014 (every year from then has twelve months of generation and a capacity; 2013's factor is 0.160), computed in session 2415 from the two tables the same way (Canada, all classes):

| Year | Solar capacity, MW | Generation, GWh | Factor |
|---|---|---|---|
| 2014 | 264.7 | 251 | 0.108 |
| 2015 | 1,874.7 | 259 | 0.016 |
| 2016 | 2,085.9 | 1,789 | 0.098 |
| 2017 | 2,297.9 | 2,048 | 0.102 |
| 2018 | 1,463.2 | 2,206 | 0.172 |
| 2019 | 1,415.1 | 2,450 | 0.198 |
| 2020 | 1,827.5 | 2,570 | 0.160 |
| 2021 | 2,231.4 | 2,740 | 0.140 |
| 2022 | 3,194.4 | 3,188 | 0.114 |
| 2023 | 3,273.1 | 4,668 | 0.163 |
| 2024 | 5,288.1 | 5,234 | 0.113 |
| 2025 | 5,728.5 | 5,964 | 0.119 |

The factor of 2019 is high because the capacity fell: Ontario's solar capacity, almost all of Canada's, went from 2,295.9 MW in 2017 to 1,460.0 in 2018 and 1,409.9 in 2019 (public utilities 754.3 to 324.0, private utilities 1,533.8 to 1,128.8), while Ontario's solar generation rose from 2,044 to 2,177 and 2,423 GWh. **No note covers that fall.** The metadata's two changes of definition fall in other years: note 12 widens the survey from 2015 (Canada's solar capacity 264.7 MW in 2014, 1,874.7 in 2015, while generation stays at 251 and 259 GWh, so 2015's 0.016), and note 7 adds systems below 100 kW from 2024 (the industry class's solar capacity 227.5 MW in 2023, 1,553.2 in 2024). Ontario's capacity falls again in 2023 (2,239.6 to 1,902.4 MW) as its generation rises. So the 2019 factor does not come from a stated definition change; the capacity series is not consistent from year to year in Ontario, and the files read do not say why. A factor also depends on when in the year capacity is counted, which the metadata does not state.

## Placing values in time, and what is filled

`ts_utc` is the year's 1 January at 00:00:00Z, a label for the reference year; the metadata does not say whether capacity is at the year's end or another date. A figure marked ".." (703, of them 322 in 2012) has no row, as header line 3 counts them; no line is "x" or "F". Nothing is filled. The table's MW equal the zip's kilowatts divided by 1,000 in every row (StatCan's values are whole kilowatts).

## License

Header: "License: public (the Statistics Canada Open Licence; see license_verdicts.csv). Source: Statistics Canada, Table 25-10-0022-01. This does not constitute an endorsement by Statistics Canada of this product." `warehouse/metadata/license_verdicts.csv`: Statistics Canada, read 361, the Open Licence ("use, reproduce, publish, freely distribute, or sell the Information"), verdict "may be public", the same if the ERW sells anything; a value-added product carries a source line and the statement that StatCan does not endorse it, which the header carries. `docs/licenses.md`, the table's row: verdict today "may be public", flag public, "agrees", ERW verdict public. Read 761 records the robots file: a crawl delay of 2 seconds, paths ending .csv disallowed, not the `/n1/tbl/csv/` zip, no AI agent named.

## Checks (session 2415)

The figures in this note were computed from the rows of `warehouse/output/statcan_generating_capacity_annual.csv`, read past its 10 header lines (counted), from the saved zip (`runs/license_reads/s2418/03_*`), read only, and from `statcan_electricity_generation_monthly` (scripts run from the session's scratch folder, not saved under `runs/`).

- 5,952 rows and 2006 to 2025, as header lines 1 and 10 state; 55 entities, 392 series; no (entity, variable, ts_utc) twice; MW throughout; no negative value.
- **Against the zip:** 6,655 lines: 5,952 with a value (the table's rows) and 703 ".."; every unit "Kilowatts", scalar factor "units", DECIMALS 0, TERMINATED blank; every row's value the zip's divided by 1,000, matched by vector and year, with 0 differences.
- **The totals:** the section above (1,915 of 1,915, as header line 3 says).
- Session 2418's cross-check (`runs/c114/s2418/cross.py`, `cross.out`): Canada's capacity factors for hydro, nuclear, wind, solar and the total in 2019, 2022 and 2024, as the report gives them.

## The session report against the table

Every figure of `SESSION_2418_REPORT.md` checked against the table, the zip and `cross.out` holds (5,952 rows, 55 series as entities, the four classes and twelve types, kilowatts divided by 1,000, 1,915 cells, 703 "..", the capacity factors and their capacities and generation, 2024's hydro the lowest of the three years, reads 760 to 762, 3 requests, 93,501 bytes), except:

- "5,952 rows, 55 series, 2006 to 2025": 2012 has no row (point 1).
- "Solar's 0.198 in 2019 is above its later values; this report does not explain it": it follows a fall in Ontario's capacity from 2017 to 2019 that no note explains (point 3).
- "robots, the table's zip (93,501 bytes); 2 s apart": 11 seconds apart (point 4).

## Limits

- **A year is missing:** 2012 has no figure at all.
- **Breaks in coverage:** the survey's population grows from 400 to 1,200 establishments in 2015 (note 12), solar includes systems below 100 kW from 2024 (note 7), and Ontario's solar capacity falls in 2018 and 2023 without a note.
- **Gross capacity:** measured at the generating units' output terminals, without deducting station service (note 3); the date in the year is not stated.
- **Suppression:** 703 ".." cells, more for New Brunswick (94), Quebec (81), Newfoundland and Labrador (68) and British Columbia (65); a sum of classes or areas falls short where one is "..".
- **Tidal** capacity (Canada) is 20 MW from 2007 to 2019 (4 MW in 2006), 0 in 2020 and 2021, and has no value from 2022.

## What it does not hold

- Years before 2006, 2012, the number of plants (the table's title names installed plants, but the file has capacity only), generation (`statcan_electricity_generation_monthly`), capacity by fuel within thermal, and individual stations.

## Points for the session to act on

1. **2012 has no row, and neither the header nor the report says so.** Header line 1 and the report say "2006 to 2025". All 322 lines of 2012 in StatCan's file are "..", so the table holds 19 years; 322 of header line 3's 703 ".." are that one year. The metadata gives no note on it. Header lines 1 and 3 could say "2006 to 2025 without 2012 (every 2012 figure is .. in StatCan's file)".
2. **The metadata's definitions and breaks are not carried.** The docstring and header give the types' names but not what capacity is or where the series breaks. The metadata's note 3 defines total installed capacity as "measured at the output terminals of all generating units in a station, without deducting station service requirements" (gross); note 12 warns that from 2015 the surveyed population grew from 400 to 1,200 establishments and asks "caution when making historical comparisons with the data prior to 2015"; note 7 says solar includes systems below 100 kW from 2024 only. No note says at what date in the year capacity is counted. Header line 2 could carry notes 3, 7 and 12 and say the date is not stated.
3. **Solar's 0.198 in 2019 does not come from a stated definition change.** The report leaves it unexplained. The factor is high because Canada's solar capacity fell from 2,297.9 MW (2017) to 1,463.2 (2018) and 1,415.1 (2019), almost all in Ontario (2,295.9 to 1,409.9 MW), while Ontario's solar generation rose (2,044 to 2,423 GWh); no note covers the fall. Note 12 explains the jump of 2015 (264.7 to 1,874.7 MW, a factor of 0.016) and note 7 the jump of 2024 in the industry class (227.5 to 1,553.2 MW). The report could say so, and the header could warn that solar capacity is not consistent from year to year.
4. **The requests were 11 seconds apart, not 2.** The report's pulls table says "2 s apart"; the probe log has 11:01:44Z and 11:01:55Z.

Compared besides, with no contradiction found: the header's and docstring's areas, classes, types and their variables, the unit and factor, "A figure StatCan marks .. (not available) has no row; nothing is filled", ".. 703", the totals within 1 MW in 1,915 of 1,915 cells, "Types and classes overlap (totals hold their parts)" (the classes add to all in 830 of 830 cells), `x_symbol` "r revised", `retrieved_at` and `vintage` against the probe log, the robots file, the license lines, and every row against the zip. The 2017 count (306 lines against 322) is explained above and is not a fault of the table.

Acted on in session 2415: the docstring and header now say that 2012 has no figure, and carry StatCan's notes 3 (gross capacity, before station service), 12 (the survey's growth in 2015) and 7 (solar below 100 kW from 2024); the docstring names Ontario's unexplained fall in solar capacity from 2017 to 2019. Session 2418's report is corrected in place on 2012, solar's 2019 factor and the requests' spacing (11 seconds). The table was written again offline: the same rows.
