# The nation's greenhouse gas emissions a year from 1990, by economic sector, by the power industry's gas and fuel, and with electricity distributed (EPA's Inventory of U.S. Greenhouse Gas Emissions and Sinks, 1990 to 2022)

Energy Research Warehouse (ERW), method note written in session 2143 (chain 090) for a table first written on 23 October 2026 (session 2136).

Tables: `epa_ghg_inventory_annual`

## Publisher and address

U.S. Environmental Protection Agency (EPA), "Inventory of U.S. Greenhouse Gas Emissions and Sinks: 1990-2022" (April 2024), page `https://www.epa.gov/ghgemissions/inventory-us-greenhouse-gas-emissions-and-sinks-1990-2022`. The connector asks one zip, the "2024 Trends in Greenhouse Gas Emissions Tables" of the Inventory's Chapter 2, `https://www.epa.gov/system/files/other-files/2024-04/trends-in-greenhouse-gas-emissions-and-removals.zip` (15 CSV files, Tables 2-1 to 2-15), and reads three of them: Table 2-10 (emissions allocated to economic sectors, each sector's sources under it), Table 2-11 (electric power-related emissions by gas, each gas's fuels or sources under it) and Table 2-12 (emissions by economic sector and gas with electricity-related emissions distributed). Source id `epa:ghg_inventory_1990_2022`. Connector: `warehouse/connectors/epa_ghg_inventory.py` (session 2136), one step.

## Vintage and revision

Years 1990 to 2022 in the file on the data machine, written by run `20261023T233011Z` (23 October 2026) from the zip saved by session 2136's trial (53,063 bytes): every row's `retrieved_at` is 2026-10-23T23:21:15Z and its `vintage` 2024-08-26T14:52:48Z, the zip's Last-Modified. The Inventory's page said, when session 2136 read it, that the 1990 to 2023 Inventory was published only as a draft for public comment (January 2025); the table holds the last final one. A later edition is not found by the connector: `URL`, `PAGE` and `SOURCE` name the 1990 to 2022 edition, so taking another means changing them. Each run replaces the table whole (`iso_prices.write_snapshot`). No job runs the connector.

## Shape and variables

Series, 5,016 rows: 8 entities, 85 variables, 152 series of 33 years each, every value a whole number. `unit` tCO2e (Decision 61): the Inventory's MMT CO2 Eq. times 1,000,000. `freq` P1Y; `ts_utc` 1 January of the year; `geo` US; `market` and `node` empty. Extra columns: `x_table` (2-10, 2-11 or 2-12), `x_sector`, `x_group` (the gas in Table 2-11, the basis in Table 2-12, empty in Table 2-10) and `x_line`, the lines as published.

- Table 2-10, 2,607 rows: a sector's own line is `direct:total` and each source under it `direct:<source>`, for transportation, electric_power_industry, industry, agriculture, commercial, residential and u_s_territories; the national lines go to `epa_ghgi:us` as `total_gross_emissions_sources`, `lulucf_sector_net_total` (negative in all 33 years, the only negative values) and `net_emissions_sources_and_sinks`.
- Table 2-11, 627 rows: `epa_ghgi:electric_power_industry`, `power:<gas>` for CO2, CH4, N2O, SF6 and CF4, `power:<gas>:<line>` under each, and `power:total`.
- Table 2-12, 1,782 rows: the five end-use sectors (not the electric power industry, whose emissions it distributes, and not U.S. Territories), each with `distributed:total`, `distributed:direct` and `distributed:electricity_related`, and `distributed:<basis>:<gas>` under each.

| Year | Gross emissions | LULUCF net | Net emissions | Electric power, all gases | Electric power, CO2 | Transportation, direct | Industry, direct |
|---|---|---|---|---|---|---|---|
| 1990 | 6,536.9 | -976.7 | 5,560.2 | 1,880.2 | 1,836.4 | 1,521.4 | 1,723.3 |
| 2005 | 7,494.6 | -907.7 | 6,586.9 | 2,457.4 | 2,417.5 | 1,965.9 | 1,587.3 |
| 2019 | 6,590.1 | -863.6 | 5,726.6 | 1,650.8 | 1,624.2 | 1,874.6 | 1,531.8 |
| 2020 | 6,001.8 | -904.4 | 5,097.4 | 1,482.2 | 1,457.0 | 1,625.3 | 1,435.9 |
| 2022 | 6,343.2 | -854.2 | 5,489.0 | 1,577.5 | 1,549.2 | 1,801.5 | 1,452.5 |

Million metric tons CO2 equivalent (the rows divided by 1,000,000). In 2022 the power industry's CO2 from fossil fuel combustion is 1,531.7: coal 851.5, natural gas 659.3, petroleum 20.5 and geothermal 0.4 (in 1990 coal 1,546.5, natural gas 175.4, petroleum 97.5).

Two cautions for a sum. Under Table 2-11's CO2, `power:co2:fossil_fuel_combustion` is a subtotal of the coal, natural gas, petroleum and geothermal lines (within 0.1 MMT in every year), so a sum over every `power:co2:` line counts that CO2 twice. And the global warming potentials: the header says the Inventory's tables do not name theirs, while Decision 61 introduced `tCO2e` for the Greenhouse Gas Reporting Program's totals under the IPCC's Fourth Assessment Report; nothing in the table says the two tables' tCO2e are weighted alike.

Where the code, the header and the docstring disagree:

- The footnote letters. The docstring (line 19, "the footnote letter after a word dropped") and session 2136's report (line 29) say the letters EPA appends are dropped. `FOOTNOTE` drops them only after Combustion, Total, HFCs and Percent. Table 2-11's "Stationary Sourcesa" (footnote a: "Includes only stationary combustion emissions related to the generation of electricity") keeps its letter, under CH4 and N2O: `x_line` "Stationary Sourcesa" and the variables `power:ch4:stationary_sourcesa` and `power:n2o:stationary_sourcesa` (66 rows).
- The national variables. The header (code line 217) gives Table 2-10's variables as `direct:<line>`, and the docstring (line 15) as `<table's basis>:<line>`; the three national lines are written without a basis, as `total_gross_emissions_sources`, `lulucf_sector_net_total` and `net_emissions_sources_and_sinks`.
- Table 2-12's Residential line under Direct Emissions is labelled SF6, as EPA labels it, and is written as `distributed:direct:sf6`. Its values equal Table 2-10's Residential substitution of ozone depleting substances in all 33 years, as the report says; the header notes the label.

## Reading the source

- The run stops at once, asking nothing, while `epa_ghg_inventory` is in `paused_sources.csv` or www.epa.gov is a paused host.
- The zip goes through `iso_prices.fetch_raw` without `fresh`: a copy an earlier run saved is read whether or not the run is `--offline`, so the zip is asked once a machine. A request not answered with HTTP 200 is tried up to four times (`iso_prices.with_retries`, the waits 5, 10 and 15 seconds); HTTP 404 is not retried. Timeout 120 seconds.
- `read_table` takes a table's second row as its years, counting the four-digit columns from the left (the Percent column after them is not read); years not 1990 onward in order stop the run. A row with an empty first cell, or with every year empty (EPA's notes under the table), is skipped.
- A value printed "+" ("does not exceed 0.05 MMT CO2 Eq.") is not written and is counted (0 in these tables). A value not a number, commas aside, stops the run. A value is EPA's number times 1,000,000, rounded to a whole ton.
- Table 2-10: a line before any sector stops the run, and so does a sector or national line missing. Table 2-11: a line before any gas stops it; its Total must equal Table 2-10's Electric Power Industry in every year (the comparison is numeric, to 0.1). Table 2-12: its three national lines and U.S. Territories must equal Table 2-10's and are not written; a line under no sector and basis stops the run.
- A series given twice stops the run. Nothing is filled. The code counts no row ceiling.

## License

Public. `license_verdicts.csv` records EPA, read 55 (`https://www.epa.gov/web-policies-and-procedures/epa-disclaimers`, 19 October 2026): "may be public", for public and for commercial use. The sentence: "Unless otherwise specified, geospatial data produced by the EPA is by default in the public domain and is not subject to domestic copyright protection under 17 U.S.C." The verdict's note adds that EPA's documents may be freely distributed and used for non-commercial, scientific and educational purposes. `sources.csv` flags `epa:ghg_inventory_1990_2022` public; `license_tables.csv` lists the table under EPA.

## Cross-checks (session 2143)

- The counts above were computed from the rows, read past the header lines. The file's rows are identical to the trial file `runs/c090/s2136/trial/epa_ghg_inventory_annual.csv` that session 2136's cross-check read.
- The table against itself, in every year, to EPA's rounding: the seven sectors' `direct:total` sum to the gross emissions within 0.2 MMT; each sector's sources sum to its own total within 0.3 MMT; Table 2-11's five gases sum to `power:total` within 0.1 MMT, and `power:total` equals the power industry's `direct:total` exactly; in Table 2-12, each sector's gases sum to its direct and electricity-related lines, and those two to its total, within 0.2 MMT; the five sectors' electricity-related lines sum to Table 2-11's total within 0.2 MMT, and the five distributed totals with U.S. Territories' direct total to the gross emissions within 0.2 MMT.
- Against EIA's energy-related CO2 (`eia_co2_state_annual`, 1990 to 2022): EIA's electric power sector (`eia_co2:US:EC:TO`) is 0.9999 to 1.0006 times the Inventory's `power:co2:fossil_fuel_combustion`. EIA's all-sector total (`eia_co2:US:TT:TO`) is 1.038 to 1.058 times the Inventory's CO2 from fossil fuel combustion summed over the seven sectors of Table 2-10.
- Session 2136's checks (`runs/c090/s2136/cross.out`): `eia_power_co2_state_annual`'s `US:ALL` is 1.053 to 1.083 times the Inventory's power CO2 from fossil fuel combustion, 1990 to 2022, a measure that differs from `eia_co2_state_annual`'s electric power sector; and the power plants of `epa_ghgrp_facility_emissions` sum to 1.017 to 1.023 times the Inventory's power total, 2015 to 2022.

## What it does not hold

- The 1990 to 2023 Inventory, published as a draft only.
- The other twelve tables of Chapter 2, the other chapters' tables, EPA's Data Explorer, and the states' inventories.
- The share of the total in 2022 that Tables 2-10 and 2-12 print after the years.
- Table 2-12's national lines and U.S. Territories, which repeat Table 2-10's and are checked, not written.
