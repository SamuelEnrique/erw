# Every country's oil and gas, a year and a month (EIA's International Energy Statistics, the bulk file)

Energy Research Warehouse (ERW), method note written in session 932 (chain 052) for tables first written on 23 October 2026.

Tables: `eia_world_oil_gas_annual`, `eia_world_oil_monthly`

## Publisher and address

U.S. Energy Information Administration (EIA), International Energy Statistics, from the bulk file `https://www.eia.gov/opendata/bulk/INTL.zip` that session 909 saved (last modified by EIA 19 October 2026). Connector: `warehouse/connectors/eia_intl_bulk.py`, the second and third tables beside `eia_world_electricity_annual` (`--table eia_world_oil_gas_annual`, session 923; `--table eia_world_oil_monthly`, session 929). Source id `eia:international_bulk`. See `eia_world_electricity_annual.md` for the file, the area names and `x_area`.

## Vintage and revision

Annual 1973 to 2025 and monthly January 1973 to July 2026 when written. Snapshots: each run replaces its table whole; a run reuses the saved file unless `--fresh` (one request for all three tables).

## Shape and variables

Series. `entity` `eia_intl:<EIA area code>:<EIA product id>`; `ts_utc` the year's or month's first day; `freq` `P1Y` or `P1M`; `geo` empty; `node` "<area>, <product>"; `x_area` country, former, part or region.

| Table | Variables | Units | Rows when written |
|---|---|---|---|
| annual | production, consumption, imports, exports | kbbl/d (liquids, EIA's thousand barrels a day), bcf (gas, EIA's billion cubic feet a year) | 162,941 and 32,971 production; 145,394 and 11,130 consumption; about 29,000 and 8,900 each of imports and exports |
| annual | bunker_consumption | kbbl/d | 19,237 |
| annual | stocks | kbbl (EIA's million barrels times 1,000) | 1,256 |
| monthly | production, consumption | kbbl/d | 527,849 and 6,706 |
| monthly | stocks | kbbl | 6,660 |

Products: 57 crude oil including lease condensate, 58 NGPL, 59 other liquids, 55 their sum, 56 refinery processing gain, 53 total petroleum and other liquids (55 and 56), 54 refined petroleum products and 62 to 68 each product, 5 petroleum and other liquids (consumption, stocks), 79 to 81 biofuels, 13 and 6798 to 8499 LPG and ethane; gas 26 dry, 3 gross, 43 vented and flared, 48 reinjected. The levels overlap: a sum takes one level.

## Reading the file

- Only the series in thousand barrels a day, billion cubic feet and million barrels are taken; EIA's cubic metre, tonne, Btu, terajoule and oil-equivalent copies are not. The annual table takes `.A` series, the monthly `.M`.
- The monthly table leaves out the OECD's and seven importers' gross imports by source country (their series put the importer in the product and the exporter in the area).
- An activity or product not in the maps stops the run; a value EIA leaves empty or marks has no row; nothing is filled. The file holds no reserves.

## License

Public: a work of the U.S. government (record 1 of `license_reads.csv`).

## Cross-checks (sessions 923, 929 and 932)

- The U.S. against EIA's U.S. tables: dry gas production against `eia_gas_balance_annual` within 1 percent in 28 of 28 years (2024: 37,767 and 37,725 bcf), consumption within 0.08 percent; crude production against `eia_crude_production_state_monthly` within 1 percent in 25 of 25 full years (annual) and in 296 of 306 months (monthly).
- The world against the countries summed: petroleum consumption and dry gas within 0.1 percent every year. Crude production by country covers only 24 countries to 1983, so the countries summed fall 9 to 23 percent short of EIA's world from 1980 to 1984, run about 1 percent over it from 1973 to 1979 and 0.5 to 1 percent over it from 2001 to 2007, and differ by 1.7 percent in 1992; within 0.5 percent otherwise.
- The months against the years: of 5,199 area-years of crude production with twelve months, 4,944 average within 1 percent of the annual figure (the world's 2024: 81,958 kbbl/d in both).
- Sessions 923 and 929, against the code: rerunning the electricity table (and in 929 the annual oil and gas table) from the code that adds each new table gives the same rows and header.

## What they do not hold

- Reserves; the OECD's imports by source. Coal, total energy and emissions are in `eia_world_coal_energy.md` (session 937, from the same file).
