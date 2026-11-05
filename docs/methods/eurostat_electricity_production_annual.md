# Europe's gross electricity production by fuel, a year, 1990 to 2024: each country's electricity generated from each energy product, all producers (Eurostat, nrg_bal_peh, GEP)

Energy Research Warehouse (ERW), method note written in session 2415 (chain 114) for a table first written on 24 October 2026 (session 2413 of chain 114, its report `archive/sessions/SESSION_2413_REPORT.md`).

Tables: `eurostat_electricity_production_annual`

## Publisher and address

Eurostat (Statistical Office of the European Union), "Production of electricity and derived heat by type of fuel" (`nrg_bal_peh`; the data browser page `https://ec.europa.eu/eurostat/databrowser/view/nrg_bal_peh/default/table`), the balance item GEP (gross electricity production) in GWh, through the SDMX 2.1 dissemination API, two requests without a key:

- `https://ec.europa.eu/eurostat/api/dissemination/sdmx/2.1/data/nrg_bal_peh/A.GEP..GWH.?format=SDMX-CSV&compressed=false&startPeriod=1990`
- `https://ec.europa.eu/eurostat/api/dissemination/sdmx/2.1/codelist/ESTAT/SIEC?format=TSV` (the products' names)

Source id `eurostat:nrg_bal_peh`. The data answer is SDMX-CSV with the columns `DATAFLOW, LAST UPDATE, freq, nrg_bal, siec, unit, geo, TIME_PERIOD, OBS_VALUE, OBS_FLAG, CONF_STATUS`: 99,202 lines, DATAFLOW `ESTAT:NRG_BAL_PEH(1.0)`, frequency A, item GEP and unit GWH on every line, 75 SIEC products, 41 areas, the years 1990 to 2024, and "LAST UPDATE" 02/06/26 23:00:00 on every line. The 41 areas are the 27 members, EU27_2020, Iceland and Norway (no line for Switzerland or Liechtenstein), nine candidates (Albania, Bosnia and Herzegovina, Georgia, Moldova, Montenegro, North Macedonia, Serbia, Turkiye, Ukraine), the United Kingdom and Kosovo. The codelist is a flat list of 333 codes and names, with no parent column.

Session 2413's probe (`runs/c114/s2413/probe.csv`) made 4 requests to ec.europa.eu: the robots file (10:50:57Z, read 756), one year of every dimension (`nrg_bal_peh` for 2023, 6,851,824 bytes, read 757), the data (HTTP 200, 7,424,621 bytes, at 2026-10-24T10:51:35Z, no Last-Modified, read 758) and the SIEC codelist (15,243 bytes, 10:51:44Z, read 759). All four are saved in `runs/license_reads/s2413/` (files 10 to 13); the data and the codelist were seeded into `warehouse/raw/eurostat_electricity_production/20261024T104838Z_probe/`, and the trial and the write read them from there ("raw file reused" in both logs).

Connector: `warehouse/connectors/eurostat_electricity_production.py` (session 2413): `[--offline] [--out-dir DIR]`, two requests (the codelist first, then the data), asked again unless `--offline`. GWh are written as MWh (times 1,000, rounded to 0.001); only the EU's members, EFTA's, nine candidates and EU27_2020 are kept, which leaves out the United Kingdom and Kosovo. A header not Eurostat's SDMX-CSV, a unit, frequency, balance item or product not expected, a value that is not a number, a period that is not a year or a key given twice stops the run. TOTAL is compared with its top groups plus pumped hydro (RA130) and the country years off by more than 1 GWh are listed in the run log; they do not stop the run. **No schedule runs it**: no step of `warehouse/run_daily.sh`, `warehouse/run_data_machine.sh`, `warehouse/run_data_machine_tables.sh`, `warehouse/run_monthly.sh`, `warehouse/refresh_supply.sh`, `warehouse/scheduled.py` or `.github/workflows/` names it. The table is public; it is held from the live set (listed under `catalogue_hold` in `warehouse/supabase/live_set.yaml`) and from the Redivis release (`STORAGE_HELD` in `warehouse/redivis/release_v1.py`).

## Vintage and revision

One write, run `20261024T105308Z` ("This run wrote 73988 rows: 73988 new, 0 replacing earlier rows ...; 0 rows are kept from earlier runs"), from the saved files. `retrieved_at` is 2026-10-24T10:51:35Z in every row, the download time. `vintage` is blank in every row: the answer has no Last-Modified, and the file's own "LAST UPDATE", 02/06/26 23:00:00 (day, month, year: 2 June 2026, no time zone), is written in header line 3 only.

No line carries a provisional or estimated flag. A later run merges by (entity, variable, ts_utc), so a revised figure replaces the old one, and a figure Eurostat stops printing keeps its earlier value.

## Shape and variables

Series, 73,988 rows, 2,256 entities `eurostat_electricity_production:<geo>:<SIEC>`, one variable `gross_electricity_production`, `unit` MWh, `freq` P1Y, `market` blank, `geo` ISO alpha-2 (Eurostat's EL written GR) and blank for EU27_2020, `node` "<geo code> gross electricity production, <SIEC name>", `x_geo_code`, `x_siec`, `x_flag` and `x_conf_status` (both blank in every row). 39 areas, 58 products with rows.

**Areas and years.** 34 areas have every year from 1990 to 2024; Montenegro starts in 2005, Moldova in 2010, Georgia in 2013 and Bosnia and Herzegovina in 2014; Ukraine runs from 1990 to 2020 only. 1,279 country years have a TOTAL.

**Products.** Eurostat's file has 75 SIEC codes; 17 have no value in any line (electricity E7000, refinery feedstocks, additives, other hydrocarbons, ethane, aviation gasoline, motor gasoline, gasoline-type jet fuel, white spirit, lubricants, paraffin waxes, charcoal, the blended biogasoline, biodiesels and bio jet kerosene, pure bio jet kerosene, and ambient heat from heat pumps RA600), so the table holds 58. Three products have rows that are all 0 (gas coke C0312, natural gas liquids O4200, pure biogasoline R5210P). Batteries (BA100), heat (H8000), other fuels (X9900) and pumped hydro (RA130) have no line for Ukraine; bioenergy (BIOE) and fossil energy (FE) have none for EU27_2020.

**The hierarchy, by the figures** (country years where every term has a row, within 1 GWh):

- **TOTAL is its top groups, pumped hydro and batteries.** Solid fossil fuels, manufactured gases, peat, oil shale, natural gas, oil, renewables and biofuels (RA000), non-renewable waste, nuclear heat, heat (H8000) and other fuels, plus pumped hydro (RA130), equal TOTAL in 1,230 of 1,279 country years. The other 49 all lie in 2020 to 2024 (2 in 2020, 4 in 2021, 12 in 2022, 14 in 2023, 17 in 2024), in each TOTAL exceeds the sum, and in each the excess is the batteries' production (BA100): with BA100 added, all 1,279 hold, the largest gap 0.634 GWh. The EU's 2024 gap of 1,040.3 GWh is its batteries' 1,041.0 GWh (point 2).
- **Renewables leave out pumped hydro, and so does "Hydro".** RA000 equals hydro (RA100), geothermal, wind, solar thermal, solar photovoltaic, tide, primary solid biofuels, the pure liquid biofuels, other liquid biofuels, biogases and renewable municipal waste in all 1,279. Pumped hydro is not inside RA100 here: RA130 exceeds RA100 in 104 country years. The codelist's codes would suggest otherwise (RA110 pure hydro, RA120 mixed hydro and RA130 pumped hydro follow RA100), and the `node` reads "Hydro" (point 4).
- **The fuel groups hold their parts** in all 1,279: solid fossil fuels its ten coals and cokes, manufactured gases its four gases, oil its twelve products, peat its two, non-renewable waste its two.
- **Fossil energy (FE) and bioenergy (BIOE)** are two further aggregates the docstring does not name. FE equals the fossil groups with non-renewable waste, and BIOE the biofuels with renewable municipal waste, in 1,111 of 1,244 country years each; in the other 133, the same country years, they are off by equal and opposite amounts (within 0.002 GWh in all 1,244; largest Germany 2024, 1,364.0 GWh): some production is placed in FE where its parts place it in BIOE, or the reverse, which this note did not resolve (point 6).

**Producers.** The 2023 file of every dimension (read 757) has GEP and its four parts by producer: main activity electricity only (GEP_MAPE), main activity combined heat and power (GEP_MAPCHP), autoproducer electricity only (GEP_APE) and autoproducer combined heat and power (GEP_APCHP). For TOTAL, the four add to GEP within 1 GWh in all 39 areas of that file (it has no line for Ukraine or the United Kingdom). So "all producers" holds.

EU27_2020, TWh (the table's MWh divided by 1,000,000):

| Year | Total | Natural gas | Solid fossil fuels | Nuclear | Renewables and biofuels | Hydro | Pumped hydro | Wind | Solar PV | Batteries |
|---|---|---|---|---|---|---|---|---|---|---|
| 1990 | 2,275.3 | 187.6 | 794.9 | 729.1 | 301.9 | 283.6 | 17.9 | 0.8 | 0.0 | 0.0 |
| 2010 | 2,984.1 | 588.8 | 701.2 | 854.5 | 652.6 | 371.8 | 29.5 | 139.9 | 22.5 | 0.0 |
| 2023 | 2,760.9 | 462.5 | 318.7 | 619.6 | 1,229.5 | 330.4 | 31.2 | 480.5 | 249.3 | 1.0 |
| 2024 | 2,828.7 | 443.2 | 271.9 | 649.5 | 1,332.5 | 369.7 | 34.4 | 490.0 | 304.0 | 1.0 |

**Heat (H8000).** The codelist names H8000 "Heat"; its children in the codelist are derived heat and district heating (H8000D), renewable heat (H8100) and waste heat and cold (H8200), none of them in this file. Ambient heat from heat pumps is a separate product (RA600, no value), and "Other fuels n.e.c., heat from chemical sources" is X9900H, also not in the file. Electricity from H8000 is not 0 in 42 country years: Czechia every year from 2010 (74 to 90.9 GWh), Spain 2022 to 2024 (282.0, 272.8, 236.3 GWh), Austria 2020 to 2024 (4.8 to 11.8), Finland 2021, 2023 and 2024 (4, 1, 4) and Turkiye in 2024 only (1,320.9 GWh, 0 in every earlier year); the EU's equals the sum of its members' (320.8 GWh in 2024). None of the files read says what heat this is; the docstring calls the group "heat from other sources", which is not Eurostat's name in these files (point 3).

## Placing values in time, and what is filled

`ts_utc` is the year's 1 January at 00:00:00Z, a label for the calendar year. Of the 95,167 lines for the 39 areas kept, 21,179 have no value; each carries the flag "m" (missing), and they have no row. No line with a value has a flag, and CONF_STATUS is blank on all 99,202 lines, so `x_flag` and `x_conf_status` are blank in every row (point 5). Zeros are kept as Eurostat prints them: 47,987 of the 73,988 rows; a zero may be a product a country does not use, and the file does not separate that from a figure not collected. The United Kingdom's and Kosovo's 4,035 lines are left out under Eurostat's terms. Nothing is filled. The table's MWh equal the file's GWh times 1,000 in every row.

## License

Header: "License: public with acknowledgement (Eurostat's copyright notice, https://ec.europa.eu/eurostat/web/main/help/copyright-notice). Cite: Eurostat, nrg_bal_peh. Eurostat bears no responsibility for this reshaping (GWh written as MWh)." `warehouse/metadata/license_verdicts.csv`: Eurostat (Statistical Office of the European Union), read 280, "Reuse of statistical data, metadata, publications, and other dissemination tools published on this website for commercial or non-commercial purposes is authorised provided the source is acknowledged. [...] [Not for commercial reuse:] Data for countries other than: Member States of the European Union (EU) Member States of the European Free Trade Association (EFTA) official EU acceding and candidate countries.", verdict "may be public", if the ERW sells anything "may be public". ec.europa.eu's robots file disallows the old SDMX path and the search pages, not `/eurostat/api/dissemination/`, and names no AI agent (read 756). `docs/licenses.md`, the table's row: verdict today "may be public", flag public, "agrees", ERW verdict public.

## Checks (session 2415)

The figures in this note were computed from the rows of `warehouse/output/eurostat_electricity_production_annual.csv`, read past its 10 header lines (counted), and from the saved files 11, 12 and 13 of `runs/license_reads/s2413/`, read only (scripts run from the session's scratch folder, not saved under `runs/`).

- 73,988 rows, 39 areas, 58 products, 1990 to 2024, as header lines 1, 3 and 10 state; 2,256 series; no (entity, variable, ts_utc) twice; no negative value; MWh throughout.
- **Against the file:** 99,202 lines; 95,167 for the 39 areas kept and 4,035 for the United Kingdom and Kosovo; 95,167 less 21,179 without a value is 73,988, key for key, every value the file's times 1,000.
- **The trial against the write:** the trial's log and the write's list the same 49 country years.
- **The identities:** the section above.
- Session 2413's cross-check (`runs/c114/s2413/cross.py`, `cross.out`): gross over the year's sum of `eurostat_electricity_monthly`'s net production, 332 country years with twelve months (2016 to 2024), a median 1.0610, 1.0010 to 1.1684 between the 5th and 95th percentiles (EU 2023: 2,760.9 against 2,572.0 TWh). Gross is below net in 10 country years: Albania 2018 to 2024, Iceland 2020 (0.9998), Luxembourg 2021 and Moldova 2020; `cross.py` prints at most 10, and a run without that limit gives the same 10.

## The session report against the table

Every figure of `SESSION_2413_REPORT.md` checked against the table, the saved files and `cross.out` holds (73,988 rows, 1990 to 2024, 39 areas, GWh times 1,000, 1,230 of 1,279, 49 kept, the EU in 2024 at 1,040 GWh, 47,987 zeros, 21,179 blanks, the United Kingdom and Kosovo left out, the median 6.1 percent, 0.1 to 16.8 percent, 2,760.9 against 2,572.0 TWh, Germany 1.147, Norway 1.006, Albania 0.969 to 0.996, Luxembourg 0.974, Moldova 0.920, reads 747 to 759, 13 requests, 7.4 MB), except:

- "for 75 SIEC products": the table holds 58 (point 1).
- "The other 49 are kept as published": they are the batteries' production, which TOTAL holds (point 2).
- "Gross is below net in a few country years: Albania from 2018 to 2024 ..., Luxembourg in 2021 (0.974) and Moldova in 2020 (0.920)": Iceland 2020 (0.9998) is the tenth.
- "the plants' own use": the files read do not define gross; the figures are consistent with it (point 7).

## Limits

- **Overlapping levels.** TOTAL, FE, BIOE, RA000 and the fuel groups hold their parts; a sum takes one level, and TOTAL holds batteries and pumped hydro, which no group holds.
- **Batteries and pumped hydro are output from stored electricity,** counted in TOTAL; a reader wanting generation from primary sources subtracts them.
- **Years differ by area** (Ukraine ends in 2020; four candidates start between 2005 and 2014).
- **Zeros** are two thirds of the rows, and a zero is not distinguished from a figure not collected.
- **Heat (H8000)** is not defined in the files read; Turkiye's 1,320.9 GWh in 2024, with 0 before, is unexplained.

## What it does not hold

- Net production (Eurostat's monthly net figures are `eurostat_electricity_monthly`), production by type of producer (GEP_MAPE and the other three parts), derived heat (GHP), units other than GWh (the file of every dimension also has TJ and KTOE), the 17 products with no value, the United Kingdom and Kosovo, Switzerland and Liechtenstein (not in the file), and capacity (`eurostat_electricity_capacity_annual`, `eurostat_renewable_capacity_annual`).

## Points for the session to act on

1. **58 products, not 75.** The docstring says "The 75 products are Eurostat's SIEC codes" and the report "for 75 SIEC products". Eurostat's file has 75 codes, but 17 have no value in any line (electricity E7000, RA600 ambient heat from heat pumps, and fifteen oil and biofuel products), so the table holds 58, as header line 3 says. Three more (gas coke, natural gas liquids, pure biogasoline) have rows that are all 0.
2. **The 49 country years that do not add are the batteries.** The docstring lists TOTAL's top groups without batteries (BA100), and header line 3 and the report keep the 49 "as Eurostat publishes them". All 49 lie in 2020 to 2024, TOTAL exceeds the sum in each, and the gap is BA100's production: with BA100 added, all 1,279 country years hold within 0.634 GWh (the EU in 2024: gap 1,040.3 GWh, batteries 1,041.0). The docstring's identity should add BA100, the total check should include it, and the header's count of misses would then be 0.
3. **"Heat from other sources" is not Eurostat's name, and H8000 is not defined.** The docstring names the group "heat from other sources"; the codelist calls H8000 "Heat" and lists as its children derived heat, renewable heat and waste heat and cold; heat pumps' ambient heat is RA600 (no value) and "heat from chemical sources" is X9900H (not in the file). The files read do not say what heat H8000's electricity comes from. Its values are small except Spain (236 to 282 GWh, 2022 to 2024) and Turkiye (1,320.9 GWh in 2024, 0 before). The docstring should use the codelist's name, and Eurostat's metadata for `nrg_bal_peh` should be read for a definition before the header gives one.
4. **"Hydro" excludes pumped hydro here, though the codelist's codes place RA130 after RA100.** The docstring says renewables leave pumped hydro out, which holds (RA000 equals its parts without RA130 in all 1,279 country years). It does not say that RA100 "Hydro" also leaves it out: RA130 exceeds RA100 in 104 country years. The header could say that RA100 is hydro without pumped hydro.
5. **`x_flag` and `x_conf_status` are empty in every row.** The docstring describes "the observation's flag and confidentiality status". Every line flagged "m" has no value and no row, no line with a value has a flag, and CONF_STATUS is blank on all 99,202 lines. The docstring could say so, or the columns could be dropped.
6. **FE and BIOE, and the areas' years, are not described.** The docstring's hierarchy does not name fossil energy (FE) or bioenergy (BIOE), which overlap TOTAL's groups, have no row for EU27_2020, and differ from their parts by equal and opposite amounts in 133 country years (Germany 2024, 1,364.0 GWh). Header line 1 says "1990 to 2024"; Ukraine ends in 2020, and Montenegro, Moldova, Georgia and Bosnia and Herzegovina start in 2005, 2010, 2013 and 2014. The docstring's "EFTA's" members are Iceland and Norway only; the file has no line for Switzerland or Liechtenstein.
7. **"Gross" is not defined.** The docstring defines "all producers" (borne out: the four producer parts add to GEP in all 39 areas of the 2023 file) but not "gross". The report explains gross over net as "the plants' own use"; no file read defines it. Eurostat's metadata should be read and the definition stated in header line 2. The report could also name Iceland 2020 (0.9998) among the country years below net.

Compared besides, with no contradiction found: the header's counts (73,988 rows, 39 areas, 58 products, 47,987 zeros, 21,179 blanks, 1,230 of 1,279, the largest 1,040.3 GWh for the EU in 2024), "Areas left out by Eurostat's terms: UK XK", the last update, "EL is GR", "blank for EU27_2020", the factor 1,000, "A blank (Eurostat's flag m, missing) has no row; zeros are kept; nothing is filled", "Eurostat's TOTAL is the sum of its top groups ... plus pumped hydro (RA130), which renewables leave out" (true with batteries added), `retrieved_at` against the probe log, the robots file, the license lines, and every row against the file.

Acted on in session 2415: the check adds batteries (BA100) to the top groups and pumped hydro, and TOTAL now agrees within 1 GWh in all 1,279 country years (the largest gap 0.634 GWh). The docstring and header now give 58 products with rows of the file's 75; name fossil energy (FE) and bioenergy (BIOE) as totals whose parts disagree in 133 country years; say that hydro (RA100) leaves out pumped hydro, that H8000 is Eurostat's undefined "Heat", that GEP is gross, own use included, and that the flag columns are blank; and give the areas' spans (Switzerland and Liechtenstein absent, Ukraine to 2020, four candidates from 2005 to 2014). Session 2413's report is corrected in place on the products, the TOTAL identity and Iceland's 2020. The table was written again offline: the same rows.
