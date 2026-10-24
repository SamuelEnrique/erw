# Panama's gross generation by plant type, net production, peak demand and load factor, a year, 1970 to 2021, and its gross generation a month, 1980 to 2021 (Secretaria Nacional de Energia, Generacion Historica Electrica, Serie 1970-2021)

Energy Research Warehouse (ERW), method note written in session 2410 (chain 114) for two tables first written on 24 October 2026 (session 2407 of chain 114, its report `archive/sessions/SESSION_2407_REPORT.md`).

Tables: `sne_panama_electricity_annual`, `sne_panama_generation_monthly`

## Publisher and address

Secretaria Nacional de Energia, Panama (SNE), its workbook "Generacion Historica Electrica (Serie 1970-2021)", listed on its Datos y Estadisticas page (`https://www.energia.gob.pa/datos-y-estadisticas/`, read 649), one request:

- `http://www.energia.gob.pa/wp-content/uploads/2024/04/2-CEE-1970-2021-GE-Generaci%C3%B3n-El%C3%A9ctrica.xls`

Source id `sne:estadisticas_electricidad`. The workbook is an Excel 97 file of 2,254,848 bytes with 65 sheets (graphs G-GE-1 to G-GE-10, tables C-GE-1B to C-GE-26, an empty Hoja1). Three tables are taken; their accented letters do not survive the file's encoding, so the labels below drop them:

- Cuadro GE-8, sheet `C-GE-8 GenBruXTCen&PSis,80-21`, "Generacion bruta por tipo de central y plantas del sistema, 1980 - 2021 (GWh)": a row a plant, grouped under eleven numbered types, with seven summary rows at the top (Total del Sistema; Total - Sistema Interconectado Nacional (1a+2a+3a+4a+5+6); Total - Autoridad del Canal de Panama (1b+2b+3b+4b) /c/; Total Eolica (7); Total Solar (8); Total Gas Natural (9); Total Biogas (10); Total - Sistemas Aislados (11)), a column a year.
- Cuadro GE-10, sheet `C-GE-10 GenBruTotMen,80-21`, "Generacion bruta total mensual, 1980 - 2021 (GWh)": a row a year, an annual column and twelve months.
- Cuadro GE-14, sheet `C-GE-14 ProdNet,DemMax,FactCar`, "Produccion neta, demanda maxima y factor de carga, 1970 - 2021": net production (GWh), its increment, maximum demand (MW), its increment, load factor (%).

GE-8 carries seven footnotes (rows 197 to 203): /a/ "Planta Hidroelectrica que pertenece a Sistemas Regionales" (Santa Fe); /b/ "En los anos 1980,1981 y 1982 incluye la generacion de BLM #2, BLM #3 y BLM #4" (Central 9 de Enero No 2); /c/ "La ACP solo puede transferir al SIN 40 MW por restricciones fisicas en la interconeccion con el sistema" (the Canal Authority's rows); /edemet/ and /edechi/, a distributor's plant delivering directly to Edemet or Edechi (Capira, Chitre, La Yeguada, Dolega, Macho Monte); /indep-edemet/, an independent generator delivering directly to Edemet (no row carries this mark); /auto-edechi/, a self-generator delivering its surplus directly to Edechi (Arkapal). GE-10 and GE-14 carry no footnote and no cell note. GE-13, "Produccion neta y consumo total de energia electrica" (not taken), carries the definitions that bear on GE-14 (below).

Session 2407's probe (`runs/c114/s2407/probe.csv`) made 11 requests: 4 to www.cnd.com.pa and 2 to sitiopublico.cnd.com.pa (the Centro Nacional de Despacho, whose lists load by script from its private site and were not taken; reads 641 to 646), then 5 to www.energia.gob.pa: the robots file (10:10:57Z, read 647), the statistics page, which redirects to a fuel consumption post (read 648), the Datos y Estadisticas page (read 649), the workbook (HTTP 200, 2,254,848 bytes, at 2026-10-24T10:11:29Z, Last-Modified "Mon, 01 Apr 2024 15:57:18 GMT", read 650) and the energy balances workbook (1,436,672 bytes, read 651, not taken). All are saved in `runs/license_reads/s2407/`; the saved workbook has the probe log's SHA-256 (39887201...). The connector's runs read it offline from `warehouse/raw/sne_panama/20261024T100855Z_probe/` ("raw file reused", run log).

Connector: `warehouse/connectors/sne_panama.py` (session 2407): `[--only annual|monthly] [--offline] [--out-dir DIR]`, one request. GE-8's rows are found by the start of their label; the eleven types must add to the system total, and the interconnected system, the Canal Authority and the isolated systems must add to it, within 0.5 GWh a year; each GE-10 year's twelve months must add to its annual column within 0.5 GWh; a label, year or value that does not read stops the run. GE-14's and GE-10's rows are read down to the growth rates. **No schedule runs it**: no step of `warehouse/run_daily.sh`, `warehouse/run_data_machine.sh`, `warehouse/run_data_machine_tables.sh`, `warehouse/run_monthly.sh`, `warehouse/refresh_supply.sh`, `warehouse/scheduled.py` or `.github/workflows/` names it. Both tables are internal; they are held from the live set (listed under `catalogue_hold` in `warehouse/supabase/live_set.yaml`) and are not in the Redivis release package, which takes public tables only (`warehouse/redivis/release_v1.py`: "an internal table is never in the public dataset").

## Vintage and revision

Three runs, all from the saved workbook: the trial `20261024T102122Z` (into `runs/c114/s2407/trial/`), a first write `20261024T102146Z` ("569 new", "504 new"; the report: it "stopped at the coverage build"), and the write of record `20261024T102202Z` ("This run wrote 569 rows: 0 new, 569 replacing earlier rows"; the monthly table "0 new, 504 replacing"; `runs/c114/s2407/write.out`, every step exit 0). `retrieved_at` is the workbook's download time, 2026-10-24T10:11:29Z, and `vintage` its Last-Modified, 2024-04-01T15:57:18Z, in every row of both tables; every row's `source_url` is the workbook.

The sheets mark no figure as provisional or revised. The series ends in 2021; the Secretaria's newer files on the page are its energy balances to 2025 (not taken). A later run asks the same address again and merges by (entity, variable, ts_utc).

## Shape and variables

`sne_panama_electricity_annual`: series, 569 rows, one entity `sne:PA`, `node` Panama, `geo` PA, `freq` P1Y, `market` blank; `unit` MWh for generation and net production (the sheets' GWh times 1,000), MW for peak demand, pct for load factor. 17 variables:

| Variable | Rows | Years | The sheet's row |
|---|---|---|---|
| generation_gross_total | 42 | 1980 to 2021 | GE-8, Total del Sistema |
| generation_gross_interconnected | 42 | 1980 to 2021 | GE-8, Total - Sistema Interconectado Nacional (1a+2a+3a+4a+5+6) |
| generation_gross_canal_authority | 22 | 2000 to 2021 | GE-8, Total - Autoridad del Canal de Panama (1b+2b+3b+4b) /c/ |
| generation_gross_hydro | 42 | 1980 to 2021 | GE-8, 1. Total Hidroelectricas |
| generation_gross_steam_bunker | 42 | 1980 to 2021 | GE-8, 2. Vapor ( Bunker) |
| generation_gross_internal_combustion | 42 | 1980 to 2021 | GE-8, 3. Combustion Interna (Bunker/Diesel) |
| generation_gross_gas_turbine_light_diesel | 42 | 1980 to 2021 | GE-8, 4. Turbina de Gas (Diesel Liviano) |
| generation_gross_gas_turbine_marine_diesel | 34 | 1988 to 2021 | GE-8, 5. Turbina de Gas (Diesel Marino) |
| generation_gross_light_diesel_other | 42 | 1980 to 2021 | GE-8, 6. Sub-Total (Diesel Liviano) |
| generation_gross_wind | 9 | 2013 to 2021 | GE-8, 7. Centrales Eolicas |
| generation_gross_solar | 8 | 2014 to 2021 | GE-8, 8. Central Solar |
| generation_gross_natural_gas | 4 | 2018 to 2021 | GE-8, 9. Planta de Gas Natural |
| generation_gross_biogas | 6 | 2016 to 2021 | GE-8, 10. Planta de Biogas |
| generation_gross_isolated_systems | 42 | 1980 to 2021 | GE-8, 11. Sistemas Aislados |
| net_production | 52 | 1970 to 2021 | GE-14, Produccion Neta (GWh) |
| peak_demand | 49 | 1973 to 2021 | GE-14, Demanda Maxima (MW) |
| load_factor | 49 | 1973 to 2021 | GE-14, Factor de Carga (%) |

`sne_panama_generation_monthly`: series, 504 rows, the same entity, one variable `generation_gross_total` (MWh), `freq` P1M, January 1980 to December 2021, GE-10's months.

What the types hold, from GE-8's plant rows:

- **Type 1, hydro**, the SIN's plants (1a) and, from 2000, the Canal Authority's (1b: 283.3 GWh in 2021).
- **Type 2, "Vapor ( Bunker)"**, is coal from 2011: BLM Carbon (2011 to 2020) and "Minera Panama (Carbon)" (from 2018) are 52.9 percent of the type in 2011, 89.7 in 2013 and all of it from 2015 to 2021 (2,283.6 GWh in 2021, all Minera Panama). Earlier it is the bunker steam plants (Central 9 de Enero, San Francisco, Avenida Sur) and, 2000 to 2014, the Canal Authority's steam plant (2b) (point 1).
- **Type 3**, internal combustion on bunker or diesel, SIN (3a) and Canal Authority (3b); zero in 1988 to 1992.
- **Type 6, "Sub-Total (Diesel Liviano)"**, light diesel plants that are not gas turbines, among them the distributors' Capira and Chitre (/edemet/), rental and temporary plants (Aggreko Cerro Azul, Cerro Azul 1 and 2, Charco Azul, Panama 2, Plantas Temporales), Termo-Colon, Tropitermica, the old plants of 1980 (Pedregal, Pielstick, Puerto Armuelles, Santiago, Valbuena) and, in 1999 and 2000, Petroterminales. It peaks at 862.4 GWh in 2014 and is 0.4 to 11.5 GWh from 2018.
- **Type 9**, Costa Norte, on natural gas (and 0.2 GWh on diesel in 2018).
- **Type 11, isolated systems**, plants not on the SIN: Petroterminales (diesel, 2001 to 2011 and 2013, 11.5 to 22.4 GWh) and "Otros Sistemas Aislados" by fuel: diesel throughout, bunker from 2003 to 2020 (5.4 to 34.7 GWh), and natural gas in 2021 only (40.6 GWh, while bunker is blank) (point 4).

The summary rows: the SIN total equals 1a + 2a + 3a + 4a + 5 + 6 + 7 + 8 + 9 + 10 within 0.5 GWh in all 42 years, though its label names 1a to 6 only (point 3); the Canal Authority's equals 1b + 2b + 3b + 4b in all 22 years; rows 9 to 13 equal the type rows 7 to 11 in every year.

GWh, MW and percent as the sheets print them (load factor rounded to two places; the sheet carries more), from the table (`runs/c114/s2410/notes/pa.out`); the table holds the GWh times 1,000 in MWh. A blank cell is the sheet's blank, which has no row.

| Year | Total | Interconnected | Canal Authority | Hydro | Type 2 (steam) | Internal combustion | Wind | Solar | Natural gas | Isolated | Net production | Peak (MW) | Load factor |
|---|---|---|---|---|---|---|---|---|---|---|---|---|---|
| 1970 | | | | | | | | | | | 801.7 | | |
| 1980 | 1,813.277 | 1,802.8 | | 963.486 | 768.453 | 46.656 | | | | 10.477 | 1,756.5 | 305.5 | 65.5 |
| 1990 | 2,660.217 | 2,650.657 | | 2,212.666 | 344.875 | 0 | | | | 9.56 | 2,746.1 | 464.35 | 67.5 |
| 2000 | 4,886.54 | 4,417.84 | 452.2 | 3,418.01 | 294.1 | 809.1 | | | | 16.5 | 4,968.0 | 777.0 | 72.99 |
| 2010 | 7,361.2 | 6,544.3 | 763.3 | 4,193.9 | 509.1 | 1,914.8 | | | | 53.6 | 7,290.3 | 1,222.4 | 68.08 |
| 2015 | 10,261.8 | 9,198.2 | 992.5 | 6,256.6 | 712.0 | 2,585.7 | 418.5 | 16.4 | | 71.1 | 9,939.0 | 1,612.0 | 70.38 |
| 2018 | 11,231.77 | 10,462.07 | 685.6 | 7,855.2 | 526.1 | 1,299.9 | 587.87 | 232.6 | 623.4 | 84.1 | 10,733.1 | 1,665.0 | 73.59 |
| 2019 | 12,921.84 | 12,155.14 | 676.9 | 5,096.3 | 2,348.93 | 1,530.0 | 724.6 | 294.8 | 2,812.0 | 89.8 | 12,285.4 | 1,961.0 | 71.52 |
| 2020 | 12,767.47 | 12,183.76 | 501.01 | 7,349.2 | 2,437.0 | 563.1 | 584.2 | 316.92 | 1,402.4 | 82.7 | 12,097.5 | 1,969.0 | 70.14 |
| 2021 | 13,886.52 | 13,309.92 | 481.3 | 8,341.9 | 2,283.6 | 452.4 | 529.6 | 585.62 | 1,554.0 | 95.3 | 13,234.0 | 2,020.0 | 74.79 |

- **The Canal Authority's plants enter in 2000.** Before 2000 GE-8 has no Canal Authority row; the interconnected system and the isolated systems give 4,434.34 GWh in 2000, below 1999's total of 4,458.5, and the Canal's 452.2 GWh make the total rise 9.6 percent. Its share is 9.3 percent in 2000, 13.0 in 2014 and 3.5 in 2021 (point 3).
- **Net production is above gross generation in 14 years**, 1984, 1987 to 1995 and 1997 to 2000 (2000: 4,968.0 against 4,886.54 GWh), because it holds purchases (point 2).
- **Zeros** are written as published: internal combustion 1988 to 1992, marine diesel gas turbines 1994, type 6 in 2001.

## Net production and peak demand: what GE-13 says

GE-14 itself defines nothing. Its net production equals GE-13's "Produccion Neta Total" in every year 1970 to 2021 within 0.05 GWh except 2000 (4,968.0 against 4,967.5). GE-13's footnotes: 1/ "Generacion Neta: Es la generacion bruta de la central menos la energia utilizada por los equipos auxiliares de las plantas"; 2/ "Produccion Neta Total: Es la generacion neta mas las compras de energia a otras empresas"; 3/, on the purchases column, "En los anos 1986 a 2020 aparecen cifras del intercambio neto"; 4/ losses are net production less consumption. So net production is net generation plus purchases from other companies, which footnote 3/ calls the net interchange. In 2000: net generation 4,850.0 plus purchases 117.5 is 4,967.5 GWh, against GE-8's gross 4,886.54. The purchases column is positive every year 1980 to 2000 (2.1 GWh in 1980 to 250.7 in 1997), mixed in 2001 to 2014, and negative from 2015 (-122.2 GWh) to 2021 (-367.6 in 2016, -449.9 in 2020, -425.6 in 2021, a year footnote 3/ does not name).

Whose figures: GE-13's net generation is above GE-8's interconnected gross generation in every year 2000 to 2021 and never above the interconnected system and the Canal Authority together, so it covers the Canal's plants; it is 96.75 to 99.25 percent of GE-8's total in the years read (1980, 1990, 2000, 2010, 2019, 2021). Net production is therefore the country's, not the SIN's alone, with the net interchange in it. Neither sheet says whose peak demand is given. GE-14's load factor equals net production over peak demand and the year's hours within 0.2 points in every year from 1998 (the recomputed factor less the published one: 6.66 points in 1973, 1.26 to 2.02 in 1974 to 1978, -2.22 in 1986), so the peak is read on the same footing as net production; whether it is the SIN's peak or the country's is not stated (point 2).

## Placing values in time, and what is filled

`ts_utc` is the year's 1 January at 00:00:00Z for the annual table (1970-01-01 to 2021-01-01) and the month's first day for the monthly table (1980-01-01 to 2021-12-01). Generation and net production are totals of the year or month; peak demand is the year's maximum; load factor is a percent. A blank cell has no row; nothing is filled. Every GE-10 month has a figure.

GE-10's annual column is not GE-8's total in every year: it is 1.677, 1.714, 1.056, 2.272 and 1.967 GWh lower in 1980 to 1984, 0.076 higher in 2020 and 0.063 lower in 2021, and within 0.05 GWh in the other 35 years. The two tables keep their own figures; header line 3 of the monthly table gives the 2.272 GWh (1983).

## License

Header: "License: internal. The Secretaria's Datos y Estadisticas page says it makes the information available and that its use must cite the source; every page's footer says all rights are reserved; internal until a ruling. Cite: Secretaria Nacional de Energia, Panama, Generacion Historica Electrica (Serie 1970-2021)." The saved Datos y Estadisticas page reads "La Secretaria Nacional de Energia pone a disposicion la informacion contenida en este sitio; para su utilizacion debera citarse la fuente: SECRETARIA NACIONAL DE ENERGIA", and both saved pages' footers "(c) Copyright Secretaria de Energia | Todos los derechos reservados". `warehouse/metadata/license_verdicts.csv`: the Secretaria, read 649, verdict "may be public", the same if the ERW sells anything, with the footer noted. `warehouse/metadata/license_reads.csv` records reads 641 to 651 (session 2407): the robots file ("disallows /wp-admin/ only; names no AI agent"; the file is `User-agent: *`, `Disallow: /wp-admin/`, `Allow: /wp-admin/admin-ajax.php`), the statistics page, the Datos y Estadisticas page and the two workbooks, and the CND pages. `docs/licenses.md`, both tables' rows: verdict today "may be public", flag internal, "DISAGREES: the flag is stricter", if the ERW sells anything "may be public", ERW verdict internal; both are listed under "Flagged internal; the sentence read allows it". The report leaves the ruling to Samuel.

## Checks (session 2410)

The figures in this note were computed from the rows of `warehouse/output/sne_panama_electricity_annual.csv` and `warehouse/output/sne_panama_generation_monthly.csv`, each read past its 10 header lines (counted), and from the saved workbook, read only with xlrd (scripts `runs/c114/s2410/notes/pa.py` and `pa2.py`, outputs `pa.out` and `pa2.out` beside them).

- 569 and 504 rows, 17 and 1 variables, 1970 to 2021 and 1980-01 to 2021-12, as header lines 1, 3 and 10 state; one entity; no (entity, variable, ts_utc) twice; no blank value.
- **Against the workbook:** all 419 non-blank GE-8 cells of the 14 rows taken, all 150 non-blank GE-14 cells and all 504 GE-10 months equal the table's values (times 1,000 where MWh), with no row for a blank cell and no cell without a row (0 differences).
- **The sums:** the eleven types add to the total, and the interconnected system, the Canal Authority and the isolated systems add to it, with 0 MWh difference in every year; each GE-10 year's months add to its annual column (largest difference 0.0 GWh).
- **The trial against the tables:** `runs/c114/s2407/trial/` holds the same 569 and 504 keys with 0 differences in value or `retrieved_at`.
- Session 2407's cross-check (`runs/c114/s2407/cross.py`, `cross.out`): net production and gross generation against `owid_ember_electricity_annual`'s Panama demand, 2000 to 2021. Net production is below Ember's demand in every year 2000 to 2018, by 0.8 to 2.6 percent (2014: 9.150 against 9.390 TWh), and above it in 2019 to 2021 (8.8, 15.3 and 13.4 percent; 2021: 13.234 against 11.670 TWh); gross generation is 14.5, 21.7 and 19.0 percent above in 2019 to 2021. Load factor against net production over the peak and the year's hours: largest gap 6.66 points (1973).
- **Session 2410's own:** GE-13 against GE-14 and GE-8 (the section above); the coal plants in type 2; the isolated systems by fuel; the 2000 break.

## The session report against the table

Every figure of `SESSION_2407_REPORT.md` checked against the tables, the workbook and `cross.out` holds (569 and 504 rows, the sheets and their years, the eleven types and the three parts adding to the total within 0.5 GWh, GE-10 within 2.272 GWh of GE-8, Costa Norte's 623.4 GWh in 2018, 13.234 against 11.670 TWh in 2021, 9.939 against 10.180 in 2015, 8.8, 15.3 and 13.4 percent, gross 14.5 to 21.7 percent above, 6.66 points in 1973, 4.968 against 4.887 TWh in 2000, reads 641 to 651 and what each says, 11 requests of 15, 2.3 MB and 1.4 MB), except:

- "From 2000 to 2015, net production is 0.8 to 2.4 per cent below Ember's demand": 0.8 to 2.6 percent (2.5 in 2012 and 2013, 2.6 in 2014), and it stays below in 2016 to 2018 (2.2, 1.8 and 1.4 percent) (point 5).
- "GE-14's net production is above GE-8's gross generation in 2000": in 14 years, for the reason GE-13 gives (point 2).
- "The ERW holds no Panama trade figure to tell whether exports explain it": the same workbook's GE-13 holds the net interchange, and net production already includes it (point 2).

## Limits

- **Net production is not generation**: it is net generation plus purchases, the net interchange from 1986 (GE-13). Net production less exports would count the exports twice.
- **The total breaks in 2000**, when the Canal Authority's plants enter GE-8; a growth rate across 1999 and 2000 mixes the two.
- **Type 2 is coal from 2015**, whatever its label; a sum of "bunker" generation by the variable's name would count coal.
- **The Canal Authority's plants are connected to the SIN** but, by footnote /c/, can pass it only 40 MW; `generation_gross_interconnected` leaves them out, and holds wind, solar, natural gas and biogas despite its label.
- **Fuel totals from the types** leave out the isolated systems' diesel, bunker and natural gas (95.3 GWh in 2021).
- **Peak demand's scope is not stated.**
- **One file.** The workbook was read once; how far the Secretaria revised earlier figures is not known from it.

## What it does not hold

- Installed capacity (GE-1 to GE-3E), generation by plant or by company (the plant rows of GE-8, GE-9), the monthly hydro generation (GE-11), GE-13's net generation, purchases, sales and losses, fuel use and its cost (GE-15 to GE-20), the sugar mills' bagasse tables, the hydro inventories and concessions (GE-21 to GE-23), the growth rates and increments; years after 2021; the energy balances to 2025; CND's statistics.

## Points for the session to act on

1. **Type 2, "steam on bunker", is coal from 2011, and all coal from 2015.** The docstring calls `generation_gross_steam_bunker` "(2, steam plants on bunker)" and the header names it `_steam_bunker`. GE-8's plant rows under "2. Vapor ( Bunker)" include "BLM Carbon" (452.0 GWh in 2011, 686.5 in 2014, 186.5 in 2020, 0 in 2021) and "Minera Panama (Carbon)" (170.8 GWh in 2018, 2,283.6 in 2021); together they are 52.9 percent of the type in 2011, 89.7 in 2013 and 100 percent from 2015 to 2021. The sheet's label is the publisher's; the variable and the header could say "steam plants, on bunker to 2010, mostly coal from 2011 and wholly coal from 2015", or the variable could be renamed `generation_gross_steam`.
2. **Net production holds the net interchange, it is the country's, and the peak's scope is not stated.** The docstring and header give `net_production` with no definition, and the report finds it above gross generation "in 2000" and says "The ERW holds no Panama trade figure to tell whether exports explain it". GE-14 has no notes; its net production equals GE-13's "Produccion Neta Total" (all years within 0.05 GWh but 2000, 0.5), which GE-13's footnote 2/ defines as net generation plus purchases from other companies, and footnote 3/ says the purchases are the net interchange in 1986 to 2020 (the column also has -425.6 GWh in 2021). Net production is above GE-8's gross in 14 years (1984, 1987 to 1995, 1997 to 2000), each a year of positive purchases (2000: 4,850.0 net generation plus 117.5). GE-13's net generation exceeds the SIN's gross every year 2000 to 2021, so it covers the Canal Authority's plants: the figure is national. The interchange is already in net production (-350.0, -449.9 and -425.6 GWh in 2019 to 2021), so exports cannot explain its excess over Ember's demand. Neither GE-13 nor GE-14 says whether the maximum demand is the SIN's or the country's; the load factor ties it to net production within 0.2 points from 1998. The header could define net production by GE-13's footnotes and say that the peak's scope is not given.
3. **The Canal Authority's plants start in 2000, can pass the SIN only 40 MW, and the SIN row includes types 7 to 10.** Header line 2 calls `generation_gross_canal_authority` "the Panama Canal Authority's plants" with "(1980 to 2021)" for GE-8, and `generation_gross_interconnected` "the national interconnected system". The Canal's row starts in 2000 (22 rows), so `generation_gross_total` breaks there (2000 without the Canal: 4,434.34 GWh, below 1999's 4,458.5). Footnote /c/ on all its rows: "La ACP solo puede transferir al SIN 40 MW por restricciones fisicas en la interconeccion con el sistema". The SIN row's label reads "(1a+2a+3a+4a+5+6)", but its values equal 1a to 6 plus types 7 to 10 in every year 2013 to 2021 (2021: 2,691.72 GWh of wind, solar, natural gas and biogas). The header could carry the first year, footnote /c/ and what the SIN row adds up to.
4. **The isolated systems hold natural gas in 2021, and fuel totals from the types miss them; the distributors' footnotes are not carried.** The docstring lists `generation_gross_natural_gas (9)` and `generation_gross_isolated_systems (11)` without saying that type 11's "Otros Sistemas Aislados" are split by fuel on GE-8 (2021: 54.7 GWh diesel, 40.6 natural gas, bunker blank after 34.7 in 2020), so 40.6 GWh of 2021's natural gas generation are not in `generation_gross_natural_gas` (1,554.0). Petroterminales is in type 6 in 1999 and 2000 (5.8 and 9.3 GWh) and in the isolated systems from 2001 (11.5 GWh). GE-8's footnotes /edemet/, /edechi/ and /auto-edechi/ mark plants that deliver directly to a distributor (Capira, Chitre, La Yeguada, Dolega, Macho Monte), among them a self-generator's surplus (Arkapal); they are counted in the SIN's figures. A clause in header line 2 would let a reader build fuel totals knowingly.
5. **A slip in the report.** "From 2000 to 2015, net production is 0.8 to 2.4 per cent below Ember's demand": `cross.out` gives -2.5 percent in 2012 and 2013 and -2.6 in 2014, and net production is below Ember's demand in 2016 to 2018 too (-2.2, -1.8, -1.4).

Compared besides, with no contradiction found: the header's and docstring's counts, years, units, the factor of 1,000, "A blank cell has no row; a zero is written as published", "The isolated systems are both a type and a part of the system", the 1980 example (1,811.6 against 1,813.277 GWh) and the 2.272 GWh, `retrieved_at` and `vintage` against the probe log, the robots file, the license lines, the source lines, and every row against the workbook. Of GE-8's footnotes, /a/ (a regional hydro plant) and /b/ (BLM 2 to 4 inside 9 de Enero No 2 in 1980 to 1982) touch plant rows only.

Acted on in session 2410: the docstring and the annual table's header (a new line of definitions, so the header has 11 lines; the figures above were counted before it) now say that type 2 is steam plants, mostly coal from 2011 and wholly coal from 2015, and keep the variable's name; that net production is net generation plus purchases, the net interchange, by GE-13's footnotes, national, and that neither sheet says whose maximum demand is given; that the Canal Authority's row starts in 2000, so the total breaks there, with footnote /c/'s 40 MW; that the interconnected system's row holds types 7 to 10; and that the isolated systems hold 40.6 GWh of natural gas in 2021. The monthly table's header names the break in 2000. Session 2407's report is corrected in place on the range below Ember's demand (0.8 to 2.6 per cent, 2000 to 2018), on the years net production is above gross generation (14, not 2000 only), and on exports, which net production already nets. Both tables were written again offline: the same rows.
