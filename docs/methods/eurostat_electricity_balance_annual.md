# Europe's electricity balance, a year, 1990 to 2025: each country's gross and net production, imports, exports, electricity used in transformation, the energy sector's own use, losses and final consumption by sector (Eurostat, nrg_cb_e, E7000)

Energy Research Warehouse (ERW), method note written in session 2457 (chain 118) for a table first written on 24 October 2026 (session 2454 of chain 118, its report `archive/sessions/SESSION_2454_REPORT.md`).

Tables: `eurostat_electricity_balance_annual`

## Publisher and address

Eurostat (Statistical Office of the European Union), "Supply, transformation and consumption of electricity, annual data" (`nrg_cb_e`; the data browser page `https://ec.europa.eu/eurostat/databrowser/view/nrg_cb_e/default/table`), the product electricity (SIEC E7000) in GWh, through the SDMX 2.1 dissemination API, two requests without a key:

- `https://ec.europa.eu/eurostat/api/dissemination/sdmx/2.1/data/nrg_cb_e/A..E7000.GWH.?format=SDMX-CSV&compressed=false&startPeriod=1990`
- `https://ec.europa.eu/eurostat/api/dissemination/sdmx/2.1/codelist/ESTAT/NRG_BAL?format=TSV` (the balance items' names)

Source id `eurostat:nrg_cb_e`. The data answer is SDMX-CSV with the columns `DATAFLOW, LAST UPDATE, freq, nrg_bal, siec, unit, geo, TIME_PERIOD, OBS_VALUE, OBS_FLAG, CONF_STATUS`: 78,105 lines, DATAFLOW `ESTAT:NRG_CB_E(1.0)`, frequency A, product E7000 and unit GWH on every line, 63 balance items, 43 areas, the years 1990 to 2025, and "LAST UPDATE" 22/10/26 23:00:00 on every line. No line lacks a value: Eurostat leaves a missing figure out of the file rather than printing it blank. The 43 areas are the 27 members, EU27_2020, the euro area EA21, Iceland, Liechtenstein and Norway (no line for Switzerland), nine candidates (Albania, Bosnia and Herzegovina, Georgia, Moldova, Montenegro, North Macedonia, Serbia, Turkiye, Ukraine), the United Kingdom and Kosovo. The codelist is a flat list of 666 codes and names (two columns on every line, no parent column).

Session 2454's probe (`runs/c118/s2454/probe.csv`) made 3 requests to ec.europa.eu: the robots file (HTTP 200, 10,827 bytes, 12:51:33Z, read 846), the data (HTTP 200, 6,179,930 bytes, at 2026-10-24T12:51:41Z, no Last-Modified, read 847) and the NRG_BAL codelist (HTTP 200, 47,481 bytes, 12:53:12Z, read 848). All three are saved in `runs/license_reads/s2454/` (files 01 to 03); the data and the codelist were seeded into `warehouse/raw/eurostat_electricity_balance/20261024T125133Z_probe/` (byte for byte the same as files 02 and 03), and the write read them from there ("raw file reused" twice in its log). The robots file has the same SHA-256 as session 2413's (file 10 of `runs/license_reads/s2413/`).

Connector: `warehouse/connectors/eurostat_electricity_balance.py` (session 2454): `[--offline] [--out-dir DIR]`, two requests (the codelist first, then the data), asked again unless `--offline`. GWh are written as MWh (times 1,000, rounded to 0.001); the EU's members, Switzerland, Iceland, Liechtenstein, Norway, the nine candidates and EU27_2020 are kept, which leaves out EA21, the United Kingdom and Kosovo. A header not Eurostat's SDMX-CSV, a unit, frequency, product or balance item not expected (an item is expected when the codelist names it), a value that is not a number, a period that is not a year or a key given twice stops the run, and so does net production above gross by more than 1 GWh. No other sum is checked. **No schedule runs it**: no step of `warehouse/run_daily.sh`, `warehouse/run_data_machine.sh`, `warehouse/run_data_machine_tables.sh`, `warehouse/run_monthly.sh`, `warehouse/refresh_supply.sh`, `warehouse/scheduled.py` or `.github/workflows/` names it (grep, no match). The table is public; it is held from the live set (listed under `catalogue_hold` in `warehouse/supabase/live_set.yaml`) and from the Redivis release (in the tuple of session 489's loop that fills `STORAGE_HELD` in `warehouse/redivis/release_v1.py`).

## Vintage and revision

One write, run `20261024T125506Z` ("This run wrote 73062 rows: 73062 new, 0 replacing earlier rows ...; 0 rows are kept from earlier runs"), from the saved files. `retrieved_at` is 2026-10-24T12:51:41Z in every row, the download time (the probe log's row 2, read 847). `vintage` is blank in every row: the answer has no Last-Modified, and the file's own "LAST UPDATE", 22/10/26 23:00:00 (day, month, year: 22 October 2026, no time zone), is written in header line 3 only.

**2025 is provisional and partial.** Its 734 rows cover 37 areas (no Iceland, Liechtenstein or Ukraine) and 20 items, and every one is flagged: 713 "p", 21 "e". Before 2025 the flags are few: Ukraine 2021 (10 "p", 2 "e"), Finland's road transport 2022 ("b") and Belgium's chemical industry 2024 ("d"). The files read do not define "b" or "d". A later run merges by (entity, variable, ts_utc), so a revised figure replaces the old one, and a figure Eurostat stops printing keeps its earlier value.

## Shape and variables

Series, 73,062 rows, 40 entities `eurostat_electricity_balance:<geo>`, 63 variables (the NRG_BAL code in lower case), 2,504 series, `unit` MWh, `freq` P1Y, `market` blank, `geo` ISO alpha-2 (Eurostat's EL written GR) and blank for EU27_2020, `node` "<geo code> electricity, <the item's name>", `x_geo_code`, `x_nrg_bal`, `x_flag` (as above) and `x_conf_status` (blank in every row). 1,328 country years.

**Areas and years.** 33 areas have every year from 1990 to 2025; Iceland runs 1990 to 2024, Ukraine 1990 to 2021, Montenegro from 2005, Moldova from 2010, Georgia from 2013, Bosnia and Herzegovina from 2014, and Liechtenstein 2014 to 2024. No area has a gap inside its span. Liechtenstein, which `eurostat_electricity_production_annual` does not hold, prints final consumption 0 in every year and its whole supply as statistical difference (2020: production 104, imports 299, inland demand 403, statistical difference 403 GWh).

**Items** (rows, and rows not 0, in brackets):

- **Supply and trade**, a row in every country year: gross production GEP, net production NEP and inland demand ID (never 0), imports IMP (114 zeros) and exports EXP (152 zeros; Cyprus and Iceland print 0 for both in every year).
- **Transformation input** (TI_EHG_*, TI_HYDP), the electricity used to make another energy or to store it: pumping in pure pumped storage plants (1,328, 580) and in mixed plants (1,328, 399), electric boilers (1,328, 337), electrically driven heat pumps (1,328, 259), charging batteries (518, 68) and hydrogen production (216, 10; not 0 only in 2024 and 2025, Germany 2024 5,980 GWh). Boilers and heat pumps make derived heat; the stored electricity comes back as production, which `eurostat_electricity_production_annual`'s note shows inside TOTAL (pumped hydro and batteries). The files read do not say how the hydrogen is made.
- **Energy sector:** the power plants' own use NRG_EHG_E (1,328, 1,315), and NRG_E, the rest of the energy sector (1,326, 1,181), with its 15 parts and NRG_PLG, 1990 to 2024. Three parts are 0 in every row (gasification plants for biogas, gas-to-liquids plants, charcoal production plants); patent fuel, coal liquefaction and LNG plants are rarely not 0 (70, 52, 33); NRG_PLG ("production, liquefaction, gasification") has 181 rows, 4 not 0, all in 2024.
- **Losses:** LOSS (1,259, 1,248; 1990 to 2024, none for Ukraine), with transmission losses TRANSL (482, 143) and distribution losses DL (551, 218; to 2025), and DL's non-technical part DL_NT (482, 21, never above DL).
- **Available for final consumption** AFC (1,328), **statistical differences** STATDIFF (1,327: 375 positive, 232 negative, 720 zero) and **final consumption** FC (1,326; no row for Hungary 2025 or Ukraine 2021).
- **Industry** FC_IND_E (1,326) and 13 branches (1,289 or 1,290 each, 1990 to 2024); **transport** FC_TRA_E (1,326) with rail, road, pipelines and not elsewhere specified; **other sectors**: commercial and public services, households, agriculture and forestry, fishing and not elsewhere specified (1,289 or 1,290 each, 1990 to 2024); agriculture and forestry apart (192 rows each: Ireland and the EU from 1990, the others mostly from 2022); and the other sectors' total FC_OTH_E, 36 rows, all in 2025 (37 areas less Hungary; 0 for Estonia, Georgia, Ireland and Slovakia).

No item is blank in every row; the three energy sector parts above are the only items 0 in every row.

**The balance, by the figures** (within 1 GWh, country years where every term has a row):

- **Gross is net plus the power plants' own use:** GEP = NEP + NRG_EHG_E in all 1,328. Net is never above gross (equal in 13).
- **Inland demand is net production plus imports less exports less transformation input:** ID = NEP + IMP - EXP - the six TI items (a missing TI row read as 0) in all 1,328, the largest gap 0.002 GWh; and in all 1,419 country years of the file. Without the TI items it misses in 903 of the table's 1,328 (970 of the file's 1,419, the docstring's count; point 2).
- **Available is inland demand less losses:** AFC = ID - LOSS in all 1,259 with LOSS; where LOSS has no row (Ukraine, and every area in 2025) AFC = ID - DL, so all 1,328 hold.
- **Final consumption is available less the statistical difference:** FC = AFC - STATDIFF in all 1,326. A positive STATDIFF is electricity available that final consumption does not place.
- **Final consumption holds the energy sector:** FC = FC_IND_E + FC_TRA_E + the other sectors (their five parts, or FC_OTH_E in 2025) + NRG_E in 1,292 of 1,325. Germany's 2023 gap the docstring quotes, 9.5 TWh, is its NRG_E, 9,510 GWh. The 33 misses: France 2011 to 2024, where FC leaves out its "other sectors, not elsewhere specified" (the gap equals FC_OTH_NSP_E each year, 596.9 to 1,385.0 GWh; it holds in France up to 2010); Austria 2024, whose transport total is 0 while its four parts sum to 3,944.1 GWh; Ireland and Georgia 2025, which print FC with every sector 0; Poland 2025 (2.9 GWh); and the EU in the years that carry them (point 3).
- **The parts hold their totals:** FC_IND_E its 13 branches in all 1,289; NRG_E its 15 parts plus NRG_PLG in all 1,289 (NRG_PLG is needed only in 2024: Denmark, Finland, the Netherlands and the EU); FC_TRA_E its four in 1,286 of 1,288 (Austria and the EU 2024); agriculture and forestry its two in 156 of 192 (the EU in 35 years, its parts covering fewer members, and North Macedonia 2022 and 2023 by 1.0 and 1.2 GWh). NRG_EHG_E is not a part of NRG_E: NRG_E with it misses in 1,276 of 1,289.
- **Losses are split late:** where TRANSL or DL is not 0, LOSS = TRANSL + DL in 135 of 149 (misses the EU 2011 to 2023 and Poland 2022, 5,141.1 GWh); in 330 other country years LOSS is above 1 GWh and both parts are 0. Before 2022 a reader of DL alone mostly reads 0 (point 6).
- **The EU is the sum of its members** for GEP, NEP, IMP, EXP, ID and STATDIFF in all 36 years, and for FC in the 35 years to 2024 (Hungary has no 2025 FC), to 0.1 GWh. So the EU's imports and exports include trade between members (2024: imports 440.2, exports 452.5 TWh).

**Signs.** Every item is positive or 0 except STATDIFF (232 negative rows, the lowest France 2009, -5,082.476 GWh). Exports and transformation input are printed positive and are subtracted in the identities above.

Source values, GWh, as the file prints them ("no line": the file has none):

| Item | Germany 2023 | France 2023 | Hungary 2025 | Liechtenstein 2020 |
|---|---|---|---|---|
| GEP gross production | 522,871.000 | 524,900.933 | 39,723.000 p | 104.000 |
| NEP net production | 498,697.000 | 502,388.898 | 37,933.000 p | 104.000 |
| NRG_EHG_E power plants' own use | 24,174.000 | 22,512.035 | 1,790.000 p | 0.000 |
| IMP imports | 69,307.000 | 25,431.848 | 23,339.000 p | 299.000 |
| EXP exports | 60,082.000 | 75,903.550 | 14,341.000 p | 0.000 |
| TI_EHG_EPS_PURE pumping, pure plants | 7,569.000 | 2,121.029 | 0.000 p | 0.000 |
| TI_EHG_EPS_MIX pumping, mixed plants | 843.000 | 3,643.454 | 0.000 p | 0.000 |
| TI_EHG_CB charging batteries | 219.000 | 134.021 | 23.000 p | no line |
| ID inland demand | 499,271.000 | 445,822.189 | 46,850.800 p | 403.000 |
| LOSS losses | 25,774.000 | 37,130.685 | no line | 0.000 |
| AFC available for final consumption | 473,497.000 | 408,691.504 | 44,032.800 p | 403.000 |
| STATDIFF statistical differences | 0.000 | 1,357.274 | 44,032.800 p | 403.000 |
| FC final consumption | 473,497.000 | 407,334.230 | no line | 0.000 |
| NRG_E energy sector | 9,510.000 | 11,076.460 | no line | 0.000 |
| FC_IND_E industry | 190,458.000 | 101,767.220 | no line | 0.000 |
| FC_OTH_HH_E households | 131,454.000 | 150,736.280 | no line | 0.000 |

EU27_2020, TWh (the table's MWh divided by 1,000,000; "TI" the six transformation input items, "other" the five other sectors' parts):

| Year | GEP | NEP | Imports | Exports | TI | ID | Losses | AFC | STATDIFF | FC | NRG_E | Industry | Transport | Other |
|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|
| 1990 | 2,275.3 | 2,132.4 | 218.5 | 184.8 | 27.0 | 2,139.2 | 151.0 | 1,988.2 | 0.5 | 1,987.7 | 100.8 | 892.8 | 56.8 | 937.3 |
| 2010 | 2,984.1 | 2,831.5 | 291.5 | 286.6 | 42.4 | 2,794.0 | 185.4 | 2,608.6 | -1.3 | 2,609.9 | 99.3 | 925.9 | 56.2 | 1,528.5 |
| 2023 | 2,760.9 | 2,647.6 | 406.8 | 407.3 | 50.5 | 2,596.6 | 175.9 | 2,420.8 | 7.0 | 2,413.8 | 72.7 | 822.8 | 70.1 | 1,449.4 |
| 2024 | 2,828.4 | 2,718.0 | 440.2 | 452.5 | 64.8 | 2,640.9 | 176.6 | 2,464.3 | 6.6 | 2,457.7 | 74.6 | 825.2 | 71.8 | 1,483.3 |
| 2025 p | 2,858.8 | 2,750.1 | 437.0 | 460.9 | 62.0 | 2,664.1 | 176.3 (DL) | 2,487.8 | 75.7 | 2,412.1 | 81.9 | 772.8 | 79.1 | 1,444.1 (FC_OTH_E) |

The EU's 2025 final consumption is low because three members' consumption sits in STATDIFF: Hungary (no FC row, STATDIFF 44,032.8 GWh, all of AFC), Slovakia (22,508.0) and Estonia (7,419.3).

## Placing values in time, and what is filled

`ts_utc` is the year's 1 January at 00:00:00Z, a label for the calendar year. Every one of the file's 73,062 lines for the 40 areas kept has a value, so "a blank has no row" never applies (header line 3: "0 blanks"). Zeros are kept as Eurostat prints them: 27,483 of the 73,062 rows; a zero may be an item a country does not have or does not split (the losses above, Liechtenstein's final consumption), and the file does not separate the two. EA21's, the United Kingdom's and Kosovo's 5,043 lines are left out. Nothing is filled. The table's MWh equal the file's GWh times 1,000 in every row.

## License

Header: "License: public with acknowledgement (Eurostat's copyright notice, https://ec.europa.eu/eurostat/web/main/help/copyright-notice). Cite: Eurostat, nrg_cb_e. Eurostat bears no responsibility for this reshaping (GWh written as MWh)." `warehouse/metadata/license_verdicts.csv`: Eurostat (Statistical Office of the European Union), read 280, "Reuse of statistical data, metadata, publications, and other dissemination tools published on this website for commercial or non-commercial purposes is authorised provided the source is acknowledged. [...] [Not for commercial reuse:] Data for countries other than: Member States of the European Union (EU) Member States of the European Free Trade Association (EFTA) official EU acceding and candidate countries.", verdict "may be public", if the ERW sells anything "may be public". ec.europa.eu's robots file disallows `/eurostat/SDMX/diss-web/rest/`, `/eurostat/tgm/` and the search pages, not `/eurostat/api/dissemination/`; its only named agents are Baiduspider and Twitterbot (read 846). `docs/licenses.md`, the table's row: verdict today "may be public", flag public, "agrees", ERW verdict public.

## Checks (session 2457)

The figures in this note were computed from the rows of `warehouse/output/eurostat_electricity_balance_annual.csv`, read past its 10 header lines (counted), and from the saved files 02 and 03 of `runs/license_reads/s2454/`, read only (scripts run from the session's scratch folder, not saved under `runs/`). The read numbers are those of `warehouse/metadata/license_reads.csv` at the time of reading: session 2456's merge renumbered them during this session (820 to 822 before, 846 to 848 after), and the report now gives 846 to 848.

- 73,062 rows, 40 areas, 63 items, 1990 to 2025, as header lines 1 and 3 state; 2,504 series (coverage's 2,504 nodes); no (entity, variable, ts_utc) twice; the only negative values STATDIFF's; MWh, P1Y, the one `source` and `source_url` and the one `retrieved_at` in every row.
- **Against the file:** 78,105 lines; 73,062 for the 40 areas kept and 5,043 for EA21 (2,150), the United Kingdom (1,620) and Kosovo (1,273); key for key, every value the file's times 1,000 (to under 0.000001 MWh), every flag, variable and `node` as the file and the codelist give them.
- **The identities:** the section above.
- **Net against gross:** never above, in all 1,328 country years, as header line 3 says.
- **The trial's dropped check:** industry, transport and FC_OTH_E (a missing row read as 0) against FC misses in 1,309 of 1,326 country years, as the report says.
- Session 2454's cross-check (`runs/c118/s2454/cross.py`, `cross.out`), run again here: GEP against `eurostat_electricity_production_annual`'s TOTAL, 1,279 country years, the same within 1 GWh in 1,139; 140 differ (92 with this GEP higher, 48 lower), the largest Romania 1998, 509.0 GWh; none in 2023; three in 2024 (the EU 318.5, France 191.6, Slovakia 127.0 GWh, this GEP lower). Liechtenstein is the one area here and not there.

## The session report against the table

Every figure of `SESSION_2454_REPORT.md` checked against the table, the saved files, the probe log and `cross.out` holds (73,062 rows, 1990 to 2025, 40 areas, 63 items, MWh as GWh times 1,000, 970 of 1,419, Germany 2023's 9.5 TWh, 1,309 of 1,326, 1,328 country years, 1,139 of 1,279, 140 at most 509.0 GWh, EU 2023 2,760.9 in both, Germany 2023 522.9 in both, France 2024 570.7 against 570.9 TWh, 3 requests to ec.europa.eu, the robots file the same as session 2413's, reads 846 to 848, held from the live set and the release, coverage sector power), except:

- "other sectors' total (FC_OTH_E) is in the codelist but has no value": it has 36 rows, all in 2025 (point 1).
- "The file's identities do not close": they close, once transformation input, losses and the energy sector are placed (points 2 and 3).
- "the United Kingdom, Kosovo and the euro area left out, as the gas balance does": `eurostat_gas_balance_monthly` keeps EA21 (point 7).
- The six EIA requests were not checked (no file of them was read).

## Limits

- **Overlapping levels.** GEP holds NEP; FC holds NRG_E and the sectors; the sectors, NRG_E and LOSS hold their parts; a sum takes one level.
- **NRG_EHG_E is outside NRG_E,** and outside final consumption: the power plants' own use is the gap between gross and net.
- **Losses before 2022** are mostly a total only: TRANSL and DL are 0 where the split is not reported.
- **The EU's trade includes trade between members;** it is not the EU's trade with the rest of the world.
- **2025 is provisional,** 20 items, 37 areas, with final consumption by sector given only as three totals, and large statistical differences where final consumption is not yet placed.
- **Breaks inside the file:** France's FC leaves out its other sectors' "not elsewhere specified" from 2011; Austria's transport total is 0 in 2024; Liechtenstein's consumption is all statistical difference.
- **Zeros** are 38 percent of the rows, and a zero is not distinguished from a figure not split or not collected.

## What it does not hold

- Electricity in units other than GWh, products other than electricity (E7000), the codelist's 603 other items (gross available energy, gross inland consumption, the Energy Efficiency Directive and Renewable Energy Directive items, non-energy use), production by fuel (`eurostat_electricity_production_annual`) or by month (`eurostat_electricity_monthly`), trade by partner, EA21, the United Kingdom, Kosovo and Switzerland (not in the file).

## Points for the session to act on

1. **FC_OTH_E has values.** The docstring says "other sectors' total, FC_OTH_E, is in the codelist but has no value", header line 3 "FC_OTH_E has no value", and the report the same. It has 36 rows, all in 2025 (every area with 2025 rows but Hungary); before 2025 the five parts carry the other sectors, and in 2025 the parts have no row. The docstring and header should say that FC_OTH_E is given for 2025 only, its parts for 1990 to 2024 only.
2. **Inland demand closes once transformation input is subtracted.** The docstring says "net production plus imports less exports differs from inland demand in 970 of 1,419 country years" and "the file's identities do not close". ID = NEP + IMP - EXP - the six TI items holds within 0.002 GWh in all 1,328 country years of the table and all 1,419 of the file; the 970 count country years of the file (it includes EA21, the United Kingdom and Kosovo, 91 country years the table does not hold; in the table, 903 of 1,328). Likewise GEP = NEP + NRG_EHG_E (all 1,328), AFC = ID - LOSS (DL where LOSS has no row; all 1,328) and FC = AFC - STATDIFF (all 1,326). The docstring should give these identities, and the connector could check them, as it now checks net against gross.
3. **Final consumption holds the energy sector; Germany's 9.5 TWh is that.** The docstring says "the parts of final consumption fall short of it, by 9.5 TWh for Germany in 2023". Germany's 2023 gap is its NRG_E, 9,510 GWh. FC = industry + transport + other sectors + NRG_E holds in 1,292 of 1,325 country years; the misses are France 2011 to 2024 (FC leaves out FC_OTH_NSP_E, the gap equal to it each year), Austria 2024 (FC_TRA_E 0, its parts 3,944.1 GWh), Ireland and Georgia 2025 (FC with every sector 0), Poland 2025 (2.9 GWh) and the EU in those years. The header could say that Eurostat's FC includes the energy sector's use, and list these breaks.
4. **NRG_EHG_E is not a part of NRG_E.** The docstring lists "nrg_e energy sector own use and its parts" and header line 2 "nrg_e and its parts". NRG_E equals its 15 parts plus NRG_PLG in all 1,289 country years; the power plants' own use NRG_EHG_E is outside it (with it, 1,276 misses) and is GEP less NEP. Three parts are 0 in every row (biogas gasification, gas-to-liquids, charcoal plants), and NRG_PLG is not 0 only in 2024. The docstring should name NRG_EHG_E apart.
5. **The flags and 2025.** The docstring gives "(p provisional, e estimated, d, b)" and header line 2 "x_flag p provisional, e estimated"; header line 1 says "1990 to 2025". Every 2025 row is flagged (713 "p", 21 "e"); 2025 has 37 areas and 20 items; "d" and "b" occur once each (Belgium FC_IND_CPC_E 2024, Finland FC_TRA_ROAD_E 2022) and are not defined in the files read. Header line 1 could say that 2025 is provisional and partial, and Eurostat's flag list should be read before "b" and "d" are named.
6. **Losses: LOSS is the total, and the split is late.** The docstring names "dl distribution losses" and not LOSS, TRANSL or AFC. LOSS has 1,259 rows (none for Ukraine, none in 2025, where DL stands in its place); TRANSL and DL are both 0 in 330 country years where LOSS is above 1 GWh, the split being reported mostly from 2022. The docstring should name LOSS as the total and say when its parts are given.
7. **EA21 is left out, unlike the gas balance, and not by Eurostat's terms.** The docstring says "Countries kept: the EU's members, EFTA's and the official candidates, with EU27_2020, as eurostat_gas_balance_monthly keeps them (the United Kingdom and Kosovo left out)"; header line 3 "Areas left out by Eurostat's terms: EA21 UK XK"; the report "the United Kingdom, Kosovo and the euro area left out, as the gas balance does". `eurostat_gas_balance_monthly` keeps EA21 and EA20 (its KEPT); EA21 is an aggregate of members, which the terms allow. The header should list EA21 apart from the areas the terms leave out (or the table keep it), and the docstring and report be corrected. Switzerland is in KEPT but has no line in the file; Liechtenstein (2014 to 2024) prints final consumption 0 with its whole supply as statistical difference.
8. **The EU's imports and exports include trade between members.** The EU's IMP and EXP equal the sum of its members' in all 36 years (2024: 440.2 and 452.5 TWh). Nothing in the docstring or header says so; a reader may take them for trade with countries outside the EU.
9. **"0 blanks" and the empty confidentiality column.** Header line 3 says "0 blanks have no row" and the docstring "A blank has no row": Eurostat's file has no line without a value (it leaves missing figures out), so the rule never applies; `x_conf_status` is blank in every row (CONF_STATUS blank on all 78,105 lines). The header could say that missing figures are absent from Eurostat's file, and the column could be dropped or described as empty.
10. **Austria's 2024 transport and 2025's statistical differences.** Austria's FC_TRA_E is 0 in 2024 (3,602.1 in 2022, 3,641.8 in 2023, 4,215.2 GWh in 2025) while its four parts sum to 3,944.1 GWh, which carries into the EU's 2024 transport total. In 2025 Hungary has no FC row (STATDIFF 44,032.8 GWh, all of AFC), and Slovakia (22,508.0) and Estonia (7,419.3) place most consumption in STATDIFF, so the EU's 2025 FC (2,412.1 TWh) is below 2024's (2,457.7) while its AFC is above. These are Eurostat's figures, kept as published; the header could name them.

Compared besides, with no contradiction found: the header's counts (73,062 rows, 40 areas, 63 items, 27,483 zeros, 1,328 country years with net never above gross), "EL is GR", "blank for EU27_2020", the factor 1,000, "Exports are positive, as Eurostat prints them" (true: no item but STATDIFF is ever negative), "The items overlap (totals hold their parts)", "zeros are kept; nothing is filled", the last update, `retrieved_at` against the probe log, `source_url`, the blank `vintage` (no Last-Modified), the robots file, the license lines and verdict, the hold in `live_set.yaml` and `release_v1.py`, no schedule, and every row against the file.

## Acted on (session 2457)

- **Points 1 to 6, 8 and 9:** the connector's docstring and header lines 2 and 3 were corrected: fc_oth_e has values in 2025 only; the identities close, and the run now stops unless inland demand is net production plus imports less exports less the six transformation input items within 1 GWh (it holds in all 1,328 country years); Germany's 9.5 TWh is nrg_e; nrg_ehg_e is named apart from nrg_e; loss is the total of losses, its split mostly from 2022; 2025 is provisional and partial; "b" and "d" are not defined in the files read; the EU's trade includes trade between members; a figure Eurostat lacks is absent from its file, and x_conf_status is blank there. The table was written again offline from the saved files, with the same 73,062 rows (only the header changed).
- **Point 7:** EA21 stays out (a decision of session 2457, reversible): the header and docstring now say it is left out by this connector's list, not by Eurostat's terms, and that the gas balance keeps it. Session 2454's report is corrected in place.
- **Point 10:** Austria's 2024 transport and 2025's statistical differences are Eurostat's figures, kept as published; this note names them.
- Session 2454's report is corrected on the identities, FC_OTH_E and the euro area, each line saying so.

