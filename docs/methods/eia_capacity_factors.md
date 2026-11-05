# How hard the fleet runs (EIA's Electric Power Annual, capacity factors and heat rates)

Energy Research Warehouse (ERW), method note written in session 987 (chain 055) for tables first written on 23 October 2026.

Tables: `eia_capacity_factors_annual`, `eia_capacity_factors_monthly`, `eia_heat_rates_annual`

## Publisher and address

U.S. Energy Information Administration (EIA), Electric Power Annual (`https://www.eia.gov/electricity/annual/`), its workbooks `xls/epa_04_08_a.xlsx` (Table 4.8.A, generators primarily using fossil fuels), `xls/epa_04_08_b.xlsx` (Table 4.8.B, the others) and `xls/epa_08_01.xlsx` (Table 8.1, average operating heat rates). Connector: `warehouse/connectors/eia_epa_tables.py` (session 984), one `--table` each. EIA's robots file allows `/electricity/`.

## Vintage and revision

The workbooks last modified 19 October 2026: years 2015 to 2025, months January 2023 to December 2025 ("Values are final", EIA's note). Snapshots (ceiling three requests).

## Shape and variables

Series. `eia_capacity_factors_annual` (374 rows) and `eia_capacity_factors_monthly` (1,224 rows): `entity` `eia_epa_cf:<energy source>:<technology>`, 17 series (coal; natural gas combined cycle, gas turbine, steam turbine, internal combustion; petroleum steam turbine, gas turbine, internal combustion; geothermal; hydroelectric; nuclear; other biomass; other fossil gas; solar photovoltaic and thermal; wind; wood), technology `all` where EIA gives none; variables `capacity_factor` (ratio) and `time_adjusted_capacity` (MW: the summer capacity of generators in operation for the whole month; a year's, the months' time weighted average, as EIA notes); `freq` P1Y or P1M; `geo` US. A year's row and its January share `ts_utc`, hence two tables.

`eia_heat_rates_annual` (44 rows): `entity` `eia_epa_heat_rate:<coal|petroleum|natural_gas|nuclear>`; variable `heat_rate`; unit MMBtu/MWh (EIA's Btu per kWh over 1,000, the same figure); years 2015 to 2025. EIA's note: utility and independent power producer plants only, combined heat and power and the commercial and industrial sectors excluded; nuclear the units' tested heat rate.

## Reading the workbooks

- The headings must be as read (each pair "Time Adjusted Capacity (MW)" and "Capacity Factor" under its fuel and technology); a month not under a "Year" row, or a key given twice, stops the run.
- A cell EIA leaves empty has no row. Nothing is filled.

## License

Public: a work of the U.S. government (record 1 of `license_reads.csv`).

## Cross-checks (sessions 984 and 987)

- Wind's 2025 capacity factor, 0.338, against `lbnl_wind_capacity_factors`' capacity-weighted 0.340 for 1,210 land-based plants (session 944).
- Session 987, against the code: `capacity_factors` reads the pairs from column 1 in steps of two, the fuel carried across its technologies; the counts computed from the rows.

## What they do not hold

- The Electric Power Annual's other tables (generation, capacity, sales, prices and the rest are held from other EIA routes).
