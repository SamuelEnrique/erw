# Manufacturing's fuel consumption and electricity by industry and census region (EIA's MECS, 2022)

Energy Research Warehouse (ERW), method note written in session 2023 (chain 057) for a table first written on 23 October 2026 (session 2016).

Tables: `eia_mecs_manufacturing`

## Publisher and address

U.S. Energy Information Administration (EIA), 2022 Manufacturing Energy Consumption Survey (MECS, Form EIA-846), `https://www.eia.gov/consumption/manufacturing/data/2022/`, three of its tables:

- `https://www.eia.gov/consumption/manufacturing/data/2022/xls/Table3_2.xlsx`, fuel consumption by energy source (trillion Btu);
- `https://www.eia.gov/consumption/manufacturing/data/2022/xls/Table11_1.xlsx`, electricity: components of net demand (million kWh);
- `https://www.eia.gov/consumption/manufacturing/data/2022/xls/Table11_3.xlsx`, electricity: components of onsite generation (million kWh).

Source id `eia:mecs`. Connector: `warehouse/connectors/eia_mecs.py` (session 2016).

## Vintage and revision

The 2022 survey, the latest (the next is fielded in 2027). Table 3.2 last modified 27 February 2026, Tables 11.1 and 11.3 on 28 July 2025; retrieved 23 October 2026 18:28 UTC and written by run `20261023T183331Z` from the saved files (`--offline`).

A table once saved is read from the saved file on every later run, so EIA's revision of a table is taken only when its saved copy is gone. The table is written whole each time.

## Shape and variables

Series, 5,363 rows, one year (`ts_utc` 2022-01-01, `freq` P1Y): 405 entities, the 81 industries (80 NAICS codes, 21 of three digits, 14 of four, 1 of five and 44 of six, and all manufacturing, `total`) in the nation and each census region. `entity` `mecs:<region>_<naics>` (region us, northeast, midwest, south or west); `geo` US for the nation (1,146 rows), empty for a census region (4,217); `node` the industry as the table names it; `x_naics` the code; `x_region` the region as the table names it; `x_table` the table; `x_mark` h where EIA marks the figure "Revised data".

| Variables | Unit | Table | Rows |
|---|---|---|---|
| fuel_total, fuel_net_electricity, fuel_residual_fuel_oil, fuel_distillate_fuel_oil, fuel_natural_gas, fuel_hgl, fuel_coal, fuel_coke_and_breeze, fuel_hydrogen, fuel_other | TBtu | 3.2 | 2,655 |
| elec_purchases, elec_transfers_in, elec_onsite_generation, elec_sales_transfers_offsite, elec_net_demand | MWh (the table's million kWh times 1,000) | 11.1 | 1,803 |
| gen_cogeneration, gen_renewable (renewables other than wood and other biomass), gen_other | MWh (the same) | 11.3 | 905 |

Manufacturing in 2022: 15,742 TBtu of fuel (natural gas 7,087, other 4,900, net electricity 2,674); 807,089,000 MWh purchased, 151,366,000 MWh generated onsite (146,163,000 of it cogeneration), 30,129,000 MWh sold or transferred offsite, 932,709,000 MWh net demand. Hydrogen is national only (50 rows): in a region it is inside Other. Two figures are below zero, as published: net electricity of All Other Petroleum and Coal Products (324199), -1 TBtu in the nation and the Midwest.

## Reading the tables

- Each sheet's title (its first four rows) must name the table and 2022, and the sheet must hold one header row, within its first 20, whose first cell is "codea" (EIA's "NAICS code" with its footnote letter); otherwise the run stops. A column's header is its text joined over the four rows ending at that row; each variable takes the shortest header beginning with its words, and a variable with no column stops the run.
- A row whose third cell is "Total United States" or "<Region> Census Region" begins that region's block. A row is an industry when its code has three to six digits, or the total when its code is empty and its label "Total"; a row with neither code nor label is passed over, and any other row stops the run. An industry before any region heading, or given twice in a region, stops it.
- Cells are read with only an empty cell empty (`keep_default_na=False`). A cell holding one of EIA's codes has no row and is counted in the header: * 1,307 (an estimate less than 0.5), D 30 (withheld to avoid disclosure), NA 324 (not available), Q 356 (withheld, relative standard error above 50 percent); the code also passes over W and X, which these tables do not use. Any other text where a figure belongs stops the run. Nothing is filled.
- An h in the cell after a figure is kept in `x_mark`.
- Table 11.3's total onsite generation must equal Table 11.1's within 0.5 MWh wherever both are figures, or the run stops; it is then dropped, the same figure as `elec_onsite_generation`. An (entity, variable, ts_utc) given twice stops the run.
- Ceiling: three requests. EIA's robots file does not disallow `/consumption/`.

## License

Public: a work of the U.S. government. The table's header: "License: public (EIA: U.S. government publications are in the public domain)." `license_tables.csv` maps it to EIA through the source registry; `license_verdicts.csv` gives EIA (read 1) may be public.

## Cross-checks (sessions 2016 and 2023)

- Session 2016, MECS against the Monthly Energy Review's industrial sector for 2022 (`eia_sector_energy_consumption_monthly`, twelve months summed): first use 20,843 TBtu (Table 1.2, read for the check, not stored) against total primary energy 26,076, 79.9 percent; fuel consumption 15,742, 60.4 percent; natural gas 7,087 against 10,781, 65.7 percent; coal 398 against 987, 40.3 percent; electricity purchased, 2,754 TBtu at 3,412 Btu a kWh, against retail electricity 3,482, 79.1 percent. The MER's sector also holds agriculture, mining and construction, and counts feedstocks.
- Session 2016: Tables 11.3 and 11.1 agree on onsite generation in all 315 industries and regions where both are figures (the run's own check, above).
- Session 2023: the counts above were computed from the rows, read past the header lines; each region holds all 81 industries.
- The nation's fuels sum to its total: 13 + 79 + 7,087 + 85 + 398 + 308 + 197 + 4,900 + 2,674 = 15,741 TBtu against 15,742; in all 26 entities with every fuel a figure, within 1 TBtu. The 21 three-digit subsectors sum to 15,740 TBtu.
- The four census regions sum to the nation: fuel 15,741 against 15,742 TBtu; purchases and net demand exactly (807,089,000 and 932,709,000 MWh); onsite generation 151,365,000 against 151,366,000 MWh.
- Net demand equals purchases plus transfers in plus onsite generation less sales and transfers offsite within 1,000 MWh (one unit of the table's rounding) in all 241 entities with the five figures (the nation: 807,089,000 + 4,383,000 + 151,366,000 - 30,129,000 = 932,709,000); cogeneration, renewables and other sum to onsite generation within 1,000 MWh in all 195 entities with the four.

## What it does not hold

- Table 1.2 (first use of energy for all purposes, fuel and nonfuel) and MECS's other tables: nonfuel (feedstock) use, end uses, prices, intensities and the rest.
- Surveys before 2022, and the relative standard errors.
- A figure EIA withholds or marks with a code: those cells have no row, and nothing is set to zero.
- Hydrogen by region (inside Other), and the byproduct fuels counted twice in fuel consumption, as EIA's note to Table 3.2 says, are not separated.
