# Every country's coal, total energy and CO2, a year (EIA's International Energy Statistics, the bulk file)

Energy Research Warehouse (ERW), method note written in session 946 (chain 053) for tables first written on 23 October 2026.

Tables: `eia_world_coal_annual`, `eia_world_energy_co2_annual`

## Publisher and address

U.S. Energy Information Administration (EIA), International Energy Statistics, from the bulk file `https://www.eia.gov/opendata/bulk/INTL.zip` that session 909 saved (last modified by EIA 19 October 2026). Connector: `warehouse/connectors/eia_intl_bulk.py`, its fourth and fifth tables (`--table eia_world_coal_annual`, `--table eia_world_energy_co2_annual`, session 937). Source id `eia:international_bulk`. See `eia_world_electricity_annual.md` for the file, the area names and `x_area`, and `eia_world_oil_gas.md` for the oil and gas tables from the same file.

## Vintage and revision

Coal 1980 to 2024, total energy and CO2 1949 to 2025 when written. Snapshots: each run replaces its table whole; a run reuses the saved file unless `--fresh` (one request for all five tables of the connector). Before 1980 the energy table has rows only for the U.S. and the groups that hold it (North America, the OECD and its parts, the world).

## Shape and variables

Series. `entity` `eia_intl:<EIA area code>:<EIA product id>`; `ts_utc` the year's first day; `freq` `P1Y`; `geo` empty; `node` "<area>, <product>"; `x_area` country, former, part or region. 265 areas in each (220 country, 36 region, 7 former, 2 part).

| Table | Variables | Units | Rows when written |
|---|---|---|---|
| coal | production, consumption, imports, exports | short_ton (EIA's thousand short tons times 1,000) | 78,319 each |
| coal | reserves (product 7 only) | short_ton (EIA's million short tons times 1,000,000) | 4,031 (2008 to 2023) |
| energy | production, consumption | TBtu (EIA's quadrillion Btu times 1,000) | 78,404 and 89,405 |
| energy | emissions | tCO2 (EIA's million metric tonnes of CO2 times 1,000,000) | 79,179 |

Coal's products: 7 coal, holding its kinds 11 anthracite, 12 bituminous, 119 subbituminous and 14 lignite, with 130 metallurgical coal and 21 metallurgical coke apart. Energy's: 44 total energy and by source 4411 coal, 4413 natural gas, 4415 petroleum and other liquids, 4417 nuclear, 4418 renewables and other, 4419 nuclear, renewables and other; CO2 4008 from all fuels, 4002 coal and coke, 4006 petroleum and other liquids, 4010 consumed natural gas. EIA files the same emissions again under the fuels' own product ids (1 coal and coke, 5 petroleum and other liquids, 3002 natural gas), and product 5 also carries petroleum's consumption in Btu: the U.S.'s 2022 values under 1, 5 and 3002 equal those under 4002, 4006 (and 4415's consumption) and 4010. A sum takes one level and one copy.

Counts: 7,685 of EIA's series in the coal table (7,671 entity and variable pairs with a figure) and 5,819 in the energy table (5,817); their entities, the area and product pairs, are 1,854 and 3,701.

## Reading the file

- Only the annual series in the tables' units are taken: thousand and million short tons for coal; quadrillion Btu and million metric tonnes of CO2 for energy. EIA's tonne, terajoule and oil-equivalent copies are not.
- In these two tables, a series in the table's units whose product or activity is not the table's is passed over (the same units hold other products' copies), not an error; in the first three tables such a series stops the run.
- A value EIA leaves empty or marks has no row; nothing is filled. EIA writes many zeros for areas with no coal, which are kept as zeros.

## License

Public: a work of the U.S. government (record 1 of `license_reads.csv`).

## Cross-checks (sessions 937 and 946)

- The U.S. against EIA's U.S. tables (session 937): coal production against `eia_coal_production_annual` equal in 24 of 24 years (2024: 512,540,324 short tons); CO2 from all fuels against `eia_co2_state_annual`'s U.S. total within 0.7 percent in 53 of 53 years (2022: 4,938 and 4,934 million tonnes); total energy consumption against SEDS's within 0.2 percent in 35 of 35 years (2024: 94,556 and 94,543 TBtu).
- The world against the countries summed (country and former only): coal production and consumption, total energy consumption and CO2 within 0.04 percent every year (2023: 37,315 million tonnes of CO2).
- Session 937, against the code: the first three tables, run again from the code that added these two, are the same row for row.
- Session 946, against the table: the U.S.'s 2022 emissions (4,937,754,949 tCO2 from all fuels; 938,209,028 coal and coke; 2,251,412,666 petroleum; 1,748,133,255 gas) and the duplicated product ids read from the table; the counts above computed from the rows. Session 937's report called the area and product pairs "series"; corrected there.

## What they do not hold

- Coal in tonnes or Btu, energy intensity, population and GDP (EIA's file holds them in other units and products).
- Monthly coal or energy.
