# Commercial buildings' and homes' energy by characteristic (EIA's CBECS 2018 and RECS 2020)

Energy Research Warehouse (ERW), method note written in session 2023 (chain 057) for two tables first written on 23 October 2026 (session 2017).

Tables: `eia_cbecs_commercial_buildings`, `eia_recs_households`

## Publisher and address

U.S. Energy Information Administration (EIA), two surveys' consumption and expenditure crosstabulations, each table's workbook as EIA prints it:

- 2018 Commercial Buildings Energy Consumption Survey (CBECS), `https://www.eia.gov/consumption/commercial/data/2018/`: Tables C1 (consumption by major fuel, and the number of buildings), C2 (expenditures by major fuel) and E1 (major fuels' consumption by end use), `.../2018/ce/xls/c1.xlsx`, `c2.xlsx` and `e1.xlsx`. Source id `eia:cbecs_2018`.
- 2020 Residential Energy Consumption Survey (RECS), `https://www.eia.gov/consumption/residential/data/2020/`: Tables CE4.1 (site consumption by fuel and end use, with housing units) and CE4.11 (expenditures by fuel and end use), `.../2020/c&e/xls/ce4.1.xlsx` and `ce4.11.xlsx`. Source id `eia:recs_2020`.

Connector: `warehouse/connectors/eia_buildings.py` (session 2017), one run writing both tables.

## Vintage and revision

The latest surveys with consumption: CBECS 2018 (C1 last modified 16 December 2022, C2 15 December 2022, E1 28 July 2023) and RECS 2020 (CE4.1 26 March 2024, CE4.11 18 March 2024). Retrieved 23 October 2026 18:37 UTC and written by run `20261023T184141Z` from the saved files (`--offline`).

A workbook once saved is read from the saved file on every later run, so EIA's revision is taken only when the saved copy is gone. Each table is written whole each time, and each survey apart: a failure of one does not stop the other.

## Shape and variables

Series, one year each (`ts_utc` 2018-01-01 or 2020-01-01, `freq` P1Y, `geo` US). `entity` `cbecs:<heading>_<category>` or `recs:<heading>_<category>`, each slugged, a part's entity naming the categories it sits in; `cbecs:all` and `recs:all` for all buildings and all homes. `node` the category as printed; `x_heading` its heading; `x_level` its indent (0 a category, 1 a part of the category above it, 2 a part of that); `x_parent` the category it is a part of; `x_table` the table. A heading's level-0 rows are the ones to add; a level-1 row is inside its `x_parent`.

| Table | Rows | Entities | Variables | Units |
|---|---|---|---|---|
| `eia_cbecs_commercial_buildings` | 5,944 | 270 (C1 270, C2 269, E1 269; 228 at level 0, 42 at level 1) | 23 | TBtu (C1 1,515 rows, E1 2,907), USD (C2 1,252), count (buildings, 270) |
| `eia_recs_households` | 2,802 | 77, each in both tables (58 at level 0, 17 at level 1, 2 at level 2) | 39 | TBtu (CE4.1 1,361), USD (CE4.11 1,364), count (housing units, 77) |

| Variables | From |
|---|---|
| buildings; consumption_sum_major_fuels, consumption_electricity_primary, consumption_electricity_site, consumption_natural_gas, consumption_fuel_oil, consumption_district_heat | C1 (thousand buildings times 1,000; trillion Btu as TBtu) |
| expenditure_sum_major_fuels, expenditure_electricity, expenditure_natural_gas, expenditure_fuel_oil, expenditure_district_heat | C2 (million dollars times 1,000,000) |
| enduse_total and enduse_ space_heating, cooling, ventilation, water_heating, lighting, cooking, refrigeration, office_equipment, computing, other | E1 (TBtu) |
| housing_units; consumption_total; consumption_electricity_ total, space_heating, water_heating, air_conditioning, refrigerators, other; consumption_ natural_gas, propane and fuel_oil_kerosene, each total, space_heating, water_heating, other | CE4.1 (million housing units times 1,000,000; TBtu) |
| expenditure_ the same nineteen | CE4.11 (billion dollars times 1,000,000,000) |

The totals: commercial buildings in 2018, 5,918,000 buildings, 6,787 TBtu of major fuels (electricity at the site 4,081, natural gas 2,300, fuel oil 101, district heat 305) and USD 141.238 billion; homes in 2020, 123,530,000 housing units, 9,481 TBtu and USD 232.76 billion.

CBECS has 42 headings in each table. EIA prints some headings and labels with a different footnote letter from table to table (the climate zone heading is "Climate zonec" in C1, "Climate zonea" in C2 and "Climate Zonea" in E1; "Other sourcesd" in C1 is "Other sourcesb" in C2 and E1; two office equipment labels end in e in C1 and c in C2 and E1). The table was first written with the letters as printed, so nine categories had one entity in C1 and another in C2 and E1; session 2023 changed the connector (`footnotes()` and `rename()`) to set aside a final lowercase letter wherever two of a survey's tables print the same words with different letters, and wrote the table again: the nine now join across the three tables, `x_heading` holds the heading without the letter ("Climate zone"), and `node` keeps EIA's label as printed. "Electricity not used" under the percentage lit during off hours is in C1 only. The 270 entities are 270 categories. RECS's tables print the same letters, and none was set aside.

## Reading the tables

- Each table's title (its first three rows) must hold "Table <name>", and its top six rows its unit's words (trillion Btu or trillion British thermal units, million dollars, billion dollars); a row "All buildings" or "All homes" must exist, and each column's header (the rows above that one) must hold its words; otherwise the run stops for that survey.
- From the All row on: a row whose label begins "Data source", "Note" or "Source" ends the table, and a row without a label is passed over. A row with no figure is a heading if it is bold, and stops the run if it is not. A category before any heading, or indented under no category, stops the run, and so does an entity given twice in one table.
- A coded cell has no row and is counted in the header: CBECS (*) 14, N 49, Q 272; RECS * 7, N 44, Q 190 (Q withheld; N no cases in the sample; * or (*) less than 0.5 of the unit). The code also passes over NA and W. Any other text where a figure belongs stops the run. Nothing is filled. Values are rounded to six decimals.
- A figure two tables of a survey share (RECS's housing units, in CE4.1 and CE4.11) must agree within one part in a million, or the run stops; it is kept once, from CE4.1.
- Ceiling: five requests, one a table. EIA's robots file does not disallow `/consumption/`.

## License

Public: works of the U.S. government. Each table's header: "License: public (EIA: U.S. government publications are in the public domain)." `license_tables.csv` maps both to EIA through the source registry; `license_verdicts.csv` gives EIA (read 1) may be public.

## Cross-checks (sessions 2017 and 2023)

- Session 2017, against EIA's sector figures for the same years (SEDS's US row and the MER): CBECS electricity at the site 4,081 TBtu against commercial retail electricity 4,715 (86.6 percent); CBECS natural gas 2,300 against 3,639 (MER) and 3,655 (SEDS), 63.2 and 62.9 percent; RECS electricity 4,453 against residential 4,997 (89.1 percent); RECS natural gas 4,241 against 4,876 (87.0 percent). CBECS covers buildings of more than 1,000 square feet, RECS occupied primary homes.
- Session 2017 found each heading's level-0 rows adding to the total within rounding under every heading not marked "more than one may apply". Session 2023, from the rows: true of all eleven RECS headings (9,480 to 9,482 TBtu against 9,481; expenditures within USD 70 million of 232.76 billion) and of 18 of CBECS's 22 such headings in C1 and in E1 (6,786 to 6,788 TBtu against 6,787). Four CBECS headings do not add to the total, their categories not covering every building: Electric vehicle (EV) charging (one category, 735 TBtu), Percentage lit when open (6,778), Primary space-heating energy source (6,566) and Water-heating equipment (6,589).
- Session 2023: the counts above were computed from the rows, read past the header lines. CBECS's four fuels sum to the sum of major fuels within 1 TBtu in all 203 entities with every figure (all buildings: 4,081 + 2,300 + 101 + 305 = 6,787); its four expenditures within USD 1 million in 203 of 205, and USD 2 million in the other two; E1's ten end uses sum to its total within 2 TBtu in all 249 with every figure, and E1's total equals C1's sum of major fuels within 1 TBtu in all 260 entities with both.
- RECS's four fuels sum to the total within 1 TBtu in all 65 entities with every figure (all homes: 4,453 + 4,241 + 391 + 396 = 9,481); electricity's five end uses sum to its total within 2 TBtu in all 75; each other fuel's three end uses to its total within 1 TBtu.

## What it does not hold

- The relative standard errors (EIA's rse sheets), and floorspace (square feet are not an ERW unit).
- CBECS's and RECS's other tables (CE1.1's intensities among them), the microdata, and surveys before 2018 and 2020; RECS 2024 has published preliminary housing characteristics only, and CBECS 2024 nothing yet (session 2017).
- A figure EIA withholds or marks with a code: those cells have no row.
- States: every figure is national or a part of the nation (census regions and divisions are categories).
