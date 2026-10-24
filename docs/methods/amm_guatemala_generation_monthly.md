# Guatemala's generation by fuel, imports, exports and the interconnected system's demand, a month, January 2017 to December 2025 (Administrador del Mercado Mayorista, Generacion Mensual por Planta)

Energy Research Warehouse (ERW), method note written in session 2410 (chain 114) for a table first written on 24 October 2026 (session 2408 of chain 114, its report `archive/sessions/SESSION_2408_REPORT.md`).

Tables: `amm_guatemala_generation_monthly`

## Publisher and address

Administrador del Mercado Mayorista, Guatemala (AMM), the wholesale market's administrator, its yearly workbooks "Generacion Mensual por Planta (XLS)", which the annual reports frame of its operation results page (`https://www.amm.org.gt/portal/?page_id=145`, read 721) opens through its script `js/informes.js` (read 723), nine requests:

- `https://www.amm.org.gt/pdfs2/pub_gen_mensual_x_planta/GM<year>0101.xls` for 2017 to 2020 and `.xlsx` for 2021 to 2025

Source id `amm:generacion_mensual_por_planta`. The script builds the same address for every year from 2006 (`if (anio4dint<2006)` it answers that no report exists) and switches to `.xlsx` from 2021; only 2017 to 2025 were taken. Each workbook has two sheets, `Energia` and `Graficos`. `Energia` is titled "DESPACHO DE CARGA EJECUTADO DEL SISTEMA NACIONAL INTERCONECTADO" with the year beneath, its columns ENERO to DICIEMBRE and TOTAL, "ENERGIA" and "GWH". It lists every plant's energy a month under headings (PLANTAS HIDROELECTRICAS, with a sub-heading "GENERACION DISTRIBUIDA RENOVABLE"; PLANTAS EOLICAS; PLANTAS SOLARES; PLANTAS TERMICAS, split into coal steam turbines, geothermal plants, the cogenerating sugar mills ("INGENIOS COGENERADORES"), and reciprocating engines and gas turbines by fuel), then five system rows and a block by resource. What is taken:

- the system rows: "TRANSACCIONES INTERNACIONALES (NETO)", "IMPORTACIONES ( - )", "EXPORTACIONES ( + )", "GENERACION TOTAL S.N.I. [GWH]", "DEMANDA S.N.I. [GWH]";
- the block "GENERACION POR TIPO DE RECURSO" (so titled in all nine workbooks): one row a resource and TOTAL.

The 2017 workbook carries cell notes on plant rows only (El Manantial 3 added from October 2017, Xolhuitz added to Ixtalito from March 2017, Termica B2 added to Termica B from November 2017, Pantaleon B1 and B3 together, Pantaleon and La Union connected at 230 kV), and 2018's one on El Manantial; the other seven have none. No workbook defines a row.

Session 2408's probe (`runs/c114/s2408/probe.csv`) made 14 requests to www.amm.org.gt: the robots file (HTTP 404, 10:25:10Z, read 719), the home page (read 720), the operation results page (read 721), the monthly reports frame (read 722), the script (read 723), and the nine workbooks (reads 724 to 732): 2025's first, at 10:26:26Z, then 2017 to 2024 from 10:26:46Z to 10:26:53Z, 0 to 2 seconds apart. Each answered HTTP 200; sizes 372,224 to 517,632 bytes (.xls) and 185,714 to 192,092 bytes (.xlsx); Last-Modified from "Thu, 18 Jan 2018 21:07:38 GMT" (2017) to "Tue, 20 Jan 2026 05:40:38 GMT" (2025). All are saved in `runs/license_reads/s2408/`, each workbook with the probe log's SHA-256. The write read them offline from `warehouse/raw/amm_guatemala/20261024T102510Z_probe/` ("raw file reused", run log).

Connector: `warehouse/connectors/amm_guatemala.py` (session 2408): `[--offline] [--out-dir DIR]`, nine requests, 2 seconds apart when asked. Labels are upper-cased with accents and lost characters dropped; a resource row is matched by its first four letters (GEOT, EOLI or ELIC, SOLA, HIDR, BIOG, BIOM, SYNG, "GAS ", CARB, COQU, BUNK, DIES). Checks, each stopping the run: the workbook's year is the year asked; the resources add to their TOTAL, which equals GENERACION TOTAL; exports less imports equal TRANSACCIONES; generation less TRANSACCIONES equals the demand; each row's months add to its TOTAL column; all within 0.01 GWh. A blank month of a resource has no row; a blank month of a system row stops the run. **No schedule runs it**: no step of `warehouse/run_daily.sh`, `warehouse/run_data_machine.sh`, `warehouse/run_data_machine_tables.sh`, `warehouse/run_monthly.sh`, `warehouse/refresh_supply.sh`, `warehouse/scheduled.py` or `.github/workflows/` names it. The table is internal; it is held from the live set (listed under `catalogue_hold` in `warehouse/supabase/live_set.yaml`) and is not in the Redivis release package, which takes public tables only (`warehouse/redivis/release_v1.py`: "an internal table is never in the public dataset").

## Vintage and revision

One write, run `20261024T102905Z` ("This run wrote 1739 rows: 1739 new, 0 replacing earlier rows ...; 0 rows are kept from earlier runs"), from the saved workbooks; no separate trial was run (the report: the reader "had parsed all nine workbooks read-only first"). Each row's `source_url` is its year's workbook, `retrieved_at` that workbook's download time (2026-10-24T10:26:26Z for 2025, 10:26:46Z to 10:26:53Z for 2017 to 2024) and `vintage` its Last-Modified (2018-01-18T21:07:38Z for 2017 to 2026-01-20T05:40:38Z for 2025, each in the January after its year).

The workbooks mark no figure as provisional. Each year is read from its own workbook as last saved; whether AMM revises a year's workbook after that January is not known from these files. A later run asks the nine addresses again and merges by (entity, variable, ts_utc).

## Shape and variables

Series, 1,739 rows, one entity `amm:GT`, `node` Guatemala, `geo` GT, `freq` P1M, `market` blank, `unit` MWh throughout (the workbooks' GWh times 1,000). 17 variables, 108 rows each (January 2017 to December 2025) except three:

| Variable | Rows | The workbook's row |
|---|---|---|
| generation_geothermal, _wind, _solar, _hydro, _biogas, _biomass, _coal, _bunker, _diesel | 108 each | GENERACION POR TIPO DE RECURSO: Geotermica, Eolica, Solar, Hidroelectrica, Biogas, Biomasa, Carbon Mineral, Bunker, Diesel |
| generation_petcoke | 89 | Coque de Petroleo, from August 2018 (11 zeros) |
| generation_natural_gas | 78 | Gas Natural, from July 2019 (18 zeros; every month of 2023 is 0) |
| generation_syngas | 60 | Syngas, from 2021 (51 zeros) |
| generation_total | 108 | GENERACION TOTAL S.N.I. [GWH] (equal to the block's TOTAL) |
| imports | 108 | IMPORTACIONES ( - ) |
| exports | 108 | EXPORTACIONES ( + ) |
| net_exports | 108 | TRANSACCIONES INTERNACIONALES (NETO) |
| demand_sni | 108 | DEMANDA S.N.I. [GWH] |

Diesel has 4 zero months. Imports and exports are positive; the signs in their labels say how they enter TRANSACCIONES, which is exports less imports, negative in 52 months (5 in 2020, 6 in 2021, 8 in 2022, 9 in 2023, all 12 in 2024 and 2025). The demand is generation less TRANSACCIONES, that is generation plus imports less exports.

The year's totals (the twelve months added), GWh as the workbooks give them, from the table and the workbooks (`runs/c114/s2410/notes/gt.out`); the table holds each month's GWh times 1,000 in MWh. A blank is a resource the year's workbook does not list.

| Year | Total | Hydro | Coal | Petcoke | Biomass | Bunker | Geothermal | Wind | Solar | Imports | Exports | Net exports | Demand SNI |
|---|---|---|---|---|---|---|---|---|---|---|---|---|---|
| 2017 | 11,489.899 | 5,765.328 | 3,059.517 | | 1,577.671 | 395.473 | 253.048 | 218.055 | 198.203 | 773.037 | 1,763.151 | 990.114 | 10,499.785 |
| 2018 | 12,522.391 | 5,190.985 | 3,902.717 | 507.749 | 1,735.896 | 379.221 | 249.754 | 319.501 | 208.313 | 415.844 | 2,104.890 | 1,689.046 | 10,833.346 |
| 2019 | 12,228.232 | 4,381.129 | 3,900.487 | 752.898 | 1,848.785 | 492.282 | 262.137 | 330.777 | 233.405 | 705.479 | 1,778.785 | 1,073.306 | 11,154.926 |
| 2020 | 11,122.062 | 5,816.538 | 1,857.198 | 651.434 | 1,717.964 | 230.261 | 273.856 | 312.684 | 221.507 | 961.829 | 1,056.244 | 94.415 | 11,027.647 |
| 2021 | 11,943.077 | 5,960.293 | 2,870.300 | 305.856 | 1,718.090 | 226.490 | 264.968 | 323.795 | 229.600 | 1,108.233 | 1,099.097 | -9.136 | 11,952.213 |
| 2022 | 12,024.708 | 6,942.219 | 1,359.239 | 1,063.617 | 1,639.894 | 169.732 | 281.989 | 313.795 | 219.867 | 1,336.501 | 974.172 | -362.329 | 12,387.037 |
| 2023 | 12,222.890 | 5,571.879 | 2,306.246 | 1,252.264 | 1,625.323 | 560.964 | 285.438 | 343.957 | 245.918 | 1,887.705 | 1,023.876 | -863.828 | 13,086.718 |
| 2024 | 13,117.407 | 5,334.174 | 2,719.925 | 1,656.350 | 1,593.407 | 871.166 | 275.036 | 286.434 | 252.104 | 1,656.884 | 842.256 | -814.628 | 13,932.036 |
| 2025 | 13,308.411 | 5,473.519 | 2,651.823 | 1,612.030 | 1,672.053 | 633.345 | 269.053 | 342.801 | 529.207 | 1,823.254 | 555.844 | -1,267.410 | 14,575.821 |

The small resources: biogas 17.558 to 29.965 GWh a year; diesel 1.656 (2019) to 36.269 (2024); natural gas 0.008 (2019), 5.698, 13.898, 9.239, 0 (2023), 74.297 and 94.746 (2025); syngas 0.158 (2021), 0.051, 0, 0.046 and 0.027.

- **Guatemala turns from net exporter to net importer** in 2021 (-9.136 GWh); by 2025 it imports 1,267.410 GWh net, 8.7 percent of the demand.
- **Generation is of the SNI as dispatched.** The title is the executed load dispatch of the national interconnected system, and the total row is "GENERACION TOTAL S.N.I."; generation not dispatched on the SNI is not in it (point 1).
- **Distributed generation is in it.** Every workbook lists "GENERACION DISTRIBUIDA RENOVABLE" (small hydro) and marks solar, biomass and biogas plants "(GDR)". This note's count (the rows under that heading up to the next PLANTAS heading, and every row whose label holds "GDR"): 331.392 GWh in 2017 (2.88 percent of the total), 325.008 (2.60) in 2018, 376.825 (3.39) in 2020, 439.240 (3.65) in 2022, 453.731 (3.46) in 2024 and 504.343 (3.79) in 2025 (point 1).
- **The resource rows split plants by fuel, not by plant.** The sugar mills' heading reads "INGENIOS COGENERADORES (T. VAPOR)" in 2017 to 2023 and "INGENIOS COGENERADORES (BIOMASA, BUNKER, CARBON)" in 2024 and 2025; their plants produced 2,163.394 GWh in 2017 against a Biomasa row of 1,577.671, and 2,638.099 in 2025 against 1,672.053. The rest of the mills' output is in the other resources' rows, so `generation_biomass` is not the mills' output and `generation_coal` is not the coal plants' alone. The coal steam turbines' heading reads "(100% CARBON)" in 2017 and "(CARBON, COQUE DE PETROLEO)" in 2025.

## Placing values in time, and what is filled

`ts_utc` is the month's first day at 00:00:00Z, a label for the calendar month, 2017-01-01 to 2025-12-01. Every value is the month's energy. A resource a year's workbook does not list, or a blank month of a listed one (petroleum coke's January to July 2018, natural gas's January to June 2019), has no row; nothing is filled. Every system row has all 108 months.

## License

Header: "License: internal. AMM's pages state no terms of reuse; internal until a ruling. Cite: Administrador del Mercado Mayorista, Generacion Mensual por Planta." `warehouse/metadata/license_verdicts.csv` holds no row for AMM. `warehouse/metadata/license_reads.csv` records reads 719 to 732 (session 2408): the robots file ("HTTP 404: no robots file"), the home page ("links to its operation results and publications; states no terms of reuse"; the saved page holds no "derechos", "copyright", "terminos" or "condiciones"), the operation results page, the monthly reports frame, the script ("the annual Generacion Mensual por Planta (XLS) opens pdfs2/pub_gen_mensual_x_planta/GM<year>0101.xls, .xlsx from 2021, no key") and the nine workbooks. `docs/licenses.md`, the table's row: verdict today "not settled (needs written permission by default)", not read "Administrador del Mercado Mayorista (AMM), Guatemala", flag internal, "not settled", if the ERW sells anything "may be public", ERW verdict internal. The report leaves the ruling to Samuel ("AMM states no terms").

## Checks (session 2410)

The figures in this note were computed from the rows of `warehouse/output/amm_guatemala_generation_monthly.csv`, read past its 10 header lines (counted), and from the nine saved workbooks, read only with xlrd and openpyxl from their bytes (scripts `runs/c114/s2410/notes/gt.py` and `gt_dump.py`, outputs `gt.out`, `gt2017.txt` and `gt2025.txt` beside them).

- 1,739 rows, 17 variables, January 2017 to December 2025, as header lines 1, 3 and 10 state; one entity; no (entity, variable, ts_utc) twice; no blank value.
- **Against the workbooks:** all 1,739 non-blank cells of the rows taken equal the table's values times 1,000, with no row for a blank cell (0 differences).
- **TRANSACCIONES is exports less imports** in all 108 months, within 0.0005 GWh, and the demand is generation less TRANSACCIONES in all 108; the workbooks' labels and every month agree with the docstring's sign.
- **No trial** was run; the write's run log (`warehouse/output/logs/amm_guatemala_20261024T102905Z.log`) records 14 to 17 variables a year (14 in 2017, 15 in 2018, 16 in 2019 and 2020, 17 from 2021).
- Session 2408's cross-check (`runs/c114/s2408/cross.py`, `cross.out`): AMM's demand and generation against `owid_ember_electricity_annual`'s Guatemala demand, 2017 to 2024. AMM's demand is lower every year: by 7.7, 6.4, 4.2, 10.7, 22.9, 10.6, 17.1 and 14.8 percent (2021: 11.952 against 15.500 TWh; Ember's own series falls from 15.50 to 13.86 TWh in 2022).

## The session report against the table

Every figure of `SESSION_2408_REPORT.md` checked against the table, the workbooks and `cross.out` holds (1,739 rows, January 2017 to December 2025, the resources and their first years, every check in every month within 0.01 GWh, petroleum coke's and natural gas's blank first months, the script's address, reads 719 to 732, 4.2 and 22.9 percent, 11.952 against 15.500 TWh, 15.50 and 13.86 TWh, generation above the demand to 2020, 11.943 against 11.952 TWh in 2021, 13.117 against 13.932 in 2024, 14 requests of 15), except:

- "AMM's rises steadily from 10.50 to 13.93 TWh between 2017 and 2024": it falls in 2020, from 11.155 to 11.028 TWh (point 5).
- "nine workbooks (2017 to 2025), about a second apart": 2025's was asked first, 20 seconds before 2017's; the other eight were 0 to 2 seconds apart (point 5).

## Limits

- **The SNI only.** The figures are the interconnected system's executed dispatch; generation not dispatched on it is not in the table.
- **Demand is a supply figure.** `demand_sni` is generation plus imports less exports; the system's losses are inside it, and the workbook gives no consumption or loss row.
- **Resources, not plants.** A mill or a coal plant burning several fuels is split across the rows.
- **Nine years.** The workbooks exist from 2006 by the script; 2006 to 2016 were not taken.

## What it does not hold

- Generation by plant (the plant rows), the peak demand (MW, not in these workbooks), prices, the two statistics tools (Knowage and Reportes Dinamicos), years before 2017 and 2026.

## Points for the session to act on

1. **The plants include distributed generation, and the generation is the SNI's dispatch; the header says neither.** Header line 1 reads "generation by fuel, imports, exports and the national interconnected system's demand", and line 2 qualifies only the demand as the SNI's. Every workbook's title is "DESPACHO DE CARGA EJECUTADO DEL SISTEMA NACIONAL INTERCONECTADO" and its total row "GENERACION TOTAL S.N.I. [GWH]", and every workbook lists a "GENERACION DISTRIBUIDA RENOVABLE" heading and plants marked "(GDR)": 331.392 GWh in 2017 (2.88 percent of the total) to 504.343 in 2025 (3.79). The header could say that generation is the SNI's executed dispatch, distributed renewable generation included.
2. **`demand_sni` holds the system's losses.** Header line 2 gives it as "DEMANDA S.N.I." and the docstring as "the national interconnected system's demand". It is generation plus imports less exports in all 108 months (the connector's own check); the workbook has no consumption or loss row, so it is the energy supplied to the SNI, losses included, not energy consumed. The report compares it with Ember's demand without saying so. A clause in header line 2 would keep it from being read as consumption.
3. **Two labels as the header gives them are not the workbooks'.** Header line 7 and the docstring name the block "GENERACION POR TIPO DE COMBUSTIBLE"; all nine workbooks title it "GENERACION POR TIPO DE RECURSO". Header line 2 and the docstring call TRANSACCIONES "regional transactions"; the row is "TRANSACCIONES INTERNACIONALES (NETO)", with "IMPORTACIONES ( - )" and "EXPORTACIONES ( + )". The sign the header gives (exports less imports) holds in every month.
4. **Header line 4's range of retrieval times runs backwards.** It reads "the workbooks retrieved 2026-10-24T10:26:46Z to 2026-10-24T10:26:26Z": the code prints the first and the last year's times (2017's and 2025's), and 2025's workbook was asked first. "10:26:26Z to 10:26:53Z" would be the range.
5. **Two slips in the report.** "AMM's rises steadily from 10.50 to 13.93 TWh between 2017 and 2024": it falls in 2020 (11.155 to 11.028 TWh). "nine workbooks (2017 to 2025), about a second apart": 2025's at 10:26:26Z, 20 seconds before 2017's at 10:26:46Z; the other eight 0 to 2 seconds apart.
6. **The license record says AMM was not read.** `docs/licenses.md` lists the table under "Not settled: a publisher was not read" and AMM among the "Publishers no read of this sweep covers", though `license_reads.csv` records reads 719 to 732 of its pages; `scripts/licenses.py` counts a publisher with no row in `license_verdicts.csv` as not read. What is missing is a verdict (the pages state no terms), not a read.

Compared besides, with no contradiction found: the header's and docstring's counts, years, variables, the factor of 1,000, the first years of syngas, natural gas and petroleum coke, "a zero is as published", the checks, the addresses and the .xls and .xlsx switch, `retrieved_at` and `vintage` against the probe log, the robots file's 404, the license lines, and every row against the workbooks. The workbooks' cell notes concern plant rows only.

Acted on in session 2410: the docstring and header now say that generation is the interconnected system's executed dispatch with distributed renewable generation included, that `demand_sni` is generation plus imports less exports and so holds the system's losses, and use the workbooks' labels, "GENERACION POR TIPO DE RECURSO" and "TRANSACCIONES INTERNACIONALES (NETO)"; header line 4 gives the workbooks' retrieval times earliest first. Session 2408's report is corrected in place on the demand (it falls in 2020), on the requests' spacing, and on the transactions (international, not regional). Point 6: as for CEB and Ghana's Energy Commission, "not read" means no verdict, which an internal table under unstated terms does not have; nothing was changed. The table was written again offline: the same rows (run of 10:58 UTC).
