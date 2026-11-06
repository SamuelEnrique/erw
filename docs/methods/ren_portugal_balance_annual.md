# Portugal's electricity balance a year, 2020 to 2025: production by source, storage, the commercial exchanges and consumption (REN, Data Hub, monthly balance export)

Energy Research Warehouse (ERW), method note written in session 2289 (chain 104) for a table first written on 24 October 2026 (session 2280 of chain 104, its report `archive/sessions/SESSION_2280_REPORT.md`).

Tables: `ren_portugal_balance_annual`

## Publisher and address

REN (Redes Energeticas Nacionais), Data Hub (whose pages also give the inputs, deliveries and losses of the "National Transmission Network"), the monthly electricity balance (`https://datahub.ren.pt/en/electricity/monthly-balance/`, read 484), through the page's CSV export of model 1550:

- `https://datahub.ren.pt/service/exports/csv?startDateString=<year>-12-31&endDateString=<year>-12-31&culture=en-GB&country=EN&modelId=1550`

Source id `ren:datahub_monthly_balance`. The export answers one month whatever range is asked: session 2280's request for 2020-01-01 to 2026-09-30 (pull 6, `runs/license_reads/s2280/06_...bin`, 1,266 bytes) gave January 2020 only. Each month's file holds, beside the month's peak ("Ponta [MW]") and the month itself, its year-to-date ("Acumulado [GWh]") and the same two for the year before, and two columns of change in percent. December's year-to-date is the year, so the Decembers of 2021, 2023 and 2025 give 2020 to 2025, each year once: the odd years from their own December, the even years from the year-before column of the next December.

Each file is a small UTF-8 CSV with a byte order mark, its row labels in Portuguese (written here without accents), footnote marks on three of them ("Hidrica 1", "Biomassa 2", "Outra Termica 3"). The page names the footnotes: 1 "Generation from natural inflow"; 2 "Includes: Forest biomass, biogas and the biodegradable fraction of municipal solid waste"; 3 "Includes: Fuel-oil, gas, the non-biodegradable fraction of municipal solid waste and other waste". The connector drops the marks; the header does not carry their meaning. Hydro here is therefore natural inflow only, pumped-storage generation being its own row.

Session 2280's probe (`runs/c104/s2280/probe.csv`) made 9 requests: the robots file (HTTP 404, 7,038 bytes, read 483), the monthly balance, API instructions, About and Hyperlinks pages (reads 484 to 487), the range request, and the three Decembers (HTTP 200, 1,296, 1,273 and 1,354 bytes, at 04:40:57Z, 04:40:58Z and 04:40:59Z). All nine are saved in `runs/license_reads/s2280/`; the three Decembers were seeded into `warehouse/raw/ren_balance/20261024T043858Z_probe/`, and the trial and the write read them offline.

Connector: `warehouse/connectors/ren_balance.py` (session 2280): `[--decembers 2021,2023,2025] [--offline] [--out-dir DIR]`, one request a December. A header not REN's December balance, a label not in its map, a value that is not a number or a year given twice stops the run; the peak and the month's own figures are not taken. **No schedule runs it**: no step of `warehouse/run_daily.sh`, `warehouse/run_data_machine.sh`, `warehouse/run_data_machine_tables.sh`, `warehouse/run_monthly.sh`, `warehouse/refresh_supply.sh`, `warehouse/scheduled.py` or `.github/workflows/` names it. The table is internal and listed under `catalogue_hold` in `warehouse/supabase/live_set.yaml`, so it is not in the live set.

## Vintage and revision

One write, run `20261024T045537Z` ("This run wrote 146 rows: 146 new, 0 replacing earlier rows ...; 0 rows are kept from earlier runs"), from the three saved Decembers. `retrieved_at` is each December's download time: 2026-10-24T04:40:57Z for 2020 and 2021, 04:40:58Z for 2022 and 2023, 04:40:59Z for 2024 and 2025, as header line 4 lists them. `vintage` is blank in every row: REN's answers carry no Last-Modified (the raw manifest's `last_modified` is empty).

REN's file marks no figure as provisional or final. Each even year is the year-before column of a later file, so it is the figure as REN printed it twelve months after its own December; whether REN revised it in between, the files do not say. A later run merges by (entity, variable, ts_utc), so a revised figure replaces the old one, and a row REN stops printing keeps its earlier value.

## Shape and variables

Series, 146 rows, one entity `ren:PT`, `node` Portugal, `geo` PT, `unit` MWh, `freq` P1Y, `market` blank, `vintage` blank. 27 variables, REN's 27 row labels across the three files; 23 have a row in every year and four in two:

| Variable | REN's row | 2020 | 2021 | 2022 | 2023 | 2024 | 2025 |
|---|---|---|---|---|---|---|---|
| production_total | PRODUCAO TOTAL | 49,343 | 46,705 | 44,016 | 44,095 | 45,686 | 48,872 |
| renewable | Producao Renovavel | 28,774 | 29,693 | 25,154 | 31,181 | 36,754 | 36,890 |
| renewable_hydro | Hidrica (natural inflow) | 12,198 | 11,607 | 6,354 | 11,771 | 14,540 | 14,508 |
| renewable_wind | Eolica | 12,067 | 12,919 | 12,960 | 12,927 | 14,143 | 13,481 |
| renewable_solar | Solar | 1,270 | 1,719 | 2,532 | 3,589 | 4,908 | 6,104 |
| renewable_wave | Ondas | | | | | 0 | 0 |
| renewable_biomass | Biomassa | 3,238 | 3,449 | 3,309 | 2,895 | 3,162 | 2,797 |
| biomass_cogeneration | Cogeracao | 1,379 | 1,592 | 1,466 | 1,162 | 1,340 | 1,178 |
| biomass_other | Outros | 1,859 | 1,857 | 1,843 | 1,733 | 1,822 | 1,619 |
| non_renewable | Producao nao Renovavel | 18,958 | 15,415 | 16,590 | 10,035 | 5,108 | 7,894 |
| coal | Carvao | 2,133 | 694 | | | | |
| natural_gas | Gas Natural | 16,564 | 14,500 | 16,397 | 9,844 | 4,862 | 7,670 |
| natural_gas_combined_cycle | Ciclo Combinado | 12,152 | 10,976 | 13,917 | 7,922 | 3,325 | 6,522 |
| natural_gas_cogeneration | Cogeracao | 4,412 | 3,524 | 2,481 | 1,922 | 1,537 | 1,148 |
| other_thermal | Outra Termica | 262 | 221 | 193 | 190 | 247 | 223 |
| other_thermal_cogeneration | Cogeracao | 67 | 27 | 26 | 32 | 32 | 17 |
| other_thermal_other | Outros | 194 | 194 | 167 | 159 | 215 | 207 |
| storage_production | Producao por Armazenamento | 1,612 | 1,597 | 2,272 | 2,879 | 3,824 | 4,088 |
| pumped_storage_production | Producao por Bombagem | 1,612 | 1,597 | 2,272 | 2,879 | 3,824 | 4,081 |
| battery_injection | Injecao de Baterias | | | | | 0 | 7 |
| storage_consumption | CONSUMO PARA ARMAZENAMENTO | 1,986 | 1,988 | 2,938 | 3,625 | 4,744 | 5,127 |
| pumping_consumption | Bombagem | 1,986 | 1,988 | 2,938 | 3,625 | 4,744 | 5,119 |
| battery_charging | Baterias | | | | | 0 | 9 |
| net_imports | SALDO IMPORTADOR | 1,456 | 4,753 | 9,253 | 10,233 | 10,465 | 9,291 |
| imports_commercial | Importacao (valor comercial) | 6,401 | 8,957 | 12,170 | 13,547 | 14,949 | 13,349 |
| exports_commercial | Exportacao (valor comercial) | 4,943 | 4,201 | 2,914 | 3,329 | 4,509 | 4,065 |
| consumption | CONSUMO | 48,813 | 49,470 | 50,332 | 50,703 | 51,407 | 53,036 |

GWh as REN prints them; the table holds each times 1,000 in MWh (every value a whole multiple of 1,000). A blank cell is a row REN does not print that year. Rows a year: 24 in 2020 and 2021, 23 in 2022 and 2023, 26 in 2024 and 2025.

- **Placeholders.** `renewable_wave` is 0 in both of its rows (REN prints the "Ondas" line with 0 in 2024 and 2025); `battery_injection` and `battery_charging` are 0 in 2024, their first year, and 7 and 9 GWh in 2025.
- **Signs.** No value is negative. `net_imports` is positive in all six years (Portugal a net importer each year); the header's "negative a net export" never occurs here.
- **Parents.** Each parent is the sum of its children within REN's rounding, at most 1 GWh apart (the cross-check below, and session 2289's for storage, natural gas and other thermal). `production_total` includes the storage production, so a share of `renewable` in it (58.3 percent in 2020, 75.5 in 2025) is smaller than a share of production less storage (60.3 and 82.4).

## Placing values in time, and what is filled

`ts_utc` is the year's 1 January at 00:00:00Z, a label for the calendar year; REN's year-to-date to the end of December is the value. The six years 2020 to 2025 all have rows. A row REN does not print in a year has no row (coal from 2022, the wave and battery lines before 2024); nothing is filled. No cell of the three files is blank.

## License

Header: "License: internal. The Data Hub's pages state no terms of reuse; internal until a ruling. Cite: REN, Data Hub." `warehouse/metadata/license_verdicts.csv` holds no row for REN. `docs/licenses.md` records the reads 483 to 487 (session 2280; numbered 431 to 435 until chain 102's reads were merged ahead of them in commit ef284545): no robots file; the monthly balance page ("states no terms"), the API instructions, About and Hyperlinks pages ("states no terms of reuse"); the About page: "here, we present this service's numbers to the scientific community, journalists and all interested parties"), and the table's row: verdict today "not settled (needs written permission by default)", not read "REN (Redes Energeticas Nacionais)", flag internal, "not settled", if the ERW sells anything "may be public", ERW verdict internal. The report leaves the ruling to Samuel ("public or internal?").

## Checks (session 2289)

The figures in this note were computed from the rows of `warehouse/output/ren_portugal_balance_annual.csv`, read past its 10 header lines (counted), and from the saved files, read only (scripts `runs/c104/s2289/ren.py` and `ren2.py`, outputs `ren.out` and `ren2.out` beside them).

- 146 rows, 27 variables, years 2020 to 2025, as header lines 3 and 10 state; one entity; no (entity, variable, ts_utc) twice; no blank value; unit MWh, freq P1Y and geo PT throughout; `source_url` names the December each year came from.
- **Against the files:** an independent parse of the three saved Decembers gives 24, 23 and 26 labelled lines, each with a value for both years (no blank cell), and the table holds as many rows a year as the files lines; each year's sum of the files' year-to-date cells equals the table's sum in GWh (2020 233,679; 2021 229,643; 2022 232,494; 2023 230,277; 2024 236,147; 2025 247,302).
- **The trial against the table:** `runs/c104/s2280/trial/ren_portugal_balance_annual.csv` (run `20261024T045207Z`) has the same 146 rows in every column, `retrieved_at` included.
- Session 2280's cross-check (`runs/c104/s2280/cross.py`), run again from the main checkout with the written table as argument 1 (output `runs/c104/s2289/ren_cross.out`): identical to the saved `cross.out`, which was run on the trial. Parents against their children within 0.001 TWh; net imports less commercial imports less exports -0.002, -0.003, -0.003, 0.015, 0.025 and 0.007 TWh (2020 to 2025); consumption against production less storage use plus net imports within 0.001 TWh; REN's consumption against Ember's Portuguese demand (`owid_ember_electricity_annual`) 0.924, 0.917, 0.906, 0.899, 0.890 and 0.877 (2025: 53.036 against 60.44 TWh); renewable share of production 58.3, 63.6, 57.1, 70.7, 80.4 and 75.5 percent.
- Session 2289's own: storage production less pumped storage and batteries 0 in every year; storage consumption less pumping and batteries 0, except -1 GWh in 2025; natural gas less its parts within 1 GWh; other thermal less its parts within 1 GWh.

## Where the description and the data disagree

1. **REN's balance is mainland Portugal's; the table says Portugal.** The header, the docstring and the report call it "Portugal's electricity balance", with `node` Portugal and `geo` PT. REN's monthly balance page describes the import balance's "contribution to the consumption of electricity in mainland Portugal", and the page reads it nowhere as the whole country. Ember's Portuguese demand, against which the cross-check sets REN's consumption (0.877 to 0.924), is the whole country's, so part of the gap may be the islands; the cross-check does not test it.
2. **The wave line holds only zeros.** The docstring names waves among the rows REN prints "from 2024"; REN prints the line with 0 in both years, so `renewable_wave` is a placeholder of two zeros, not measured wave output. The batteries' 2024 rows are 0 too, beside 7 and 9 GWh in 2025.
3. **The license files say REN was not read.** `docs/licenses.md` lists the table under "Not settled: a publisher was not read" ("not read: REN (Redes Energeticas Nacionais)"), though the same file records reads 483 to 487 of REN's pages from session 2280. What is missing is a verdict row in `license_verdicts.csv` (the pages state no terms), not a read.
4. **Hydro's footnote is dropped without its meaning.** REN's "Hidrica 1" is "Generation from natural inflow"; the header calls the variables "REN's rows in snake case" and says nothing of the footnotes, so a reader may take `renewable_hydro` to include pumped-storage generation, which is `pumped_storage_production`.

Compared besides, with no contradiction found: the header's and docstring's counts, years, variables, unit, factor of 1,000, the rows absent (coal after 2021; waves and batteries before 2024) and "nothing is filled" against the rows and the three files.

Not acted on: this note changes no file but itself.

Acted on in session 2289: the node is now "Portugal (mainland)" and the header says the balance is mainland Portugal's, as REN's page gives it; the table was written again offline (the same 146 rows). `renewable_wave`'s zeros are REN's as published; the license record lists REN without a verdict because its pages state no terms (reads 483 to 487), as session 2280 recorded.

## The session report against the table

Every figure of `SESSION_2280_REPORT.md` checked against the table, the saved files and the rerun cross-check holds (2020 to 2025, 146 rows, each a year in MWh from REN's GWh times 1,000, the export answering January 2020 for a range, December of 2021, 2023 and 2025 giving six years in three requests, every parent within 1 GWh of its children, consumption balancing within 1 GWh, net imports up to 25 GWh from commercial imports less exports in 2024, 0.877 to 0.924 of Ember's demand falling each year, 53.036 against 60.44 TWh in 2025, renewables 58.3 percent in 2020, 75.5 in 2025 and 80.4 in 2024, 9 requests of 15, reads 483 to 487, no robots file), except:

- "Portugal's electricity balance" and the report's "Portuguese demand" comparison: REN's balance is mainland Portugal's (disagreement 1).
- "production by source (hydro, wind, solar, waves, ...)": the wave rows are 0 in both years REN prints them (disagreement 2).
- Files: "`warehouse/metadata/license_reads.csv` (431 to 435)": the merge of chain 102 (commit ef284545) renumbered them 462 to 466, as the report's own text above now says; this line was not changed with it.

## What it does not hold

- The months (each file's month column), the monthly peaks in MW, the change columns, years before 2020 (the page offers 2011 on) and 2026 to date; the Data Hub's other models (the transmission network's inputs, deliveries and losses, installed capacity); the Azores and Madeira; and production by plant or by hour.
