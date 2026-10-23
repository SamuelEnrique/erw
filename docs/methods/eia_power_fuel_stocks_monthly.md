# Fuel stocks at power plants (EIA)

Energy Research Warehouse (ERW), method note written in session 932 (chain 052) for a table first written on 23 October 2026.

Tables: `eia_power_fuel_stocks_monthly`

## Publisher and address

U.S. Energy Information Administration (EIA), Form EIA-923, electric power operational data, through EIA's API v2, route `electricity/electric-power-operational-data`, data column `stocks`, fuels COL, PEL and PC, sectors 98 and 99, from January 2008. Connector: `warehouse/connectors/eia_power_fuel_stocks.py` (session 927). The route's generation is `eia_state_generation_monthly`'s and its costs `eia_power_plant_fuel_costs`'.

## Vintage and revision

January 2008 to July 2026 when written (pages retrieved 2026-10-23 10:03 to 10:04 UTC). A snapshot: each run replaces the table whole, reusing saved pages unless `--fresh` (ceiling: 14 requests; the table is 14 pages of 5,000 records).

## Shape and variables

Series. `entity` `eia_power_stocks:<location>:<sector>:<fuel>`: location a state's postal code, a census region's code (ENC, ESC, MAT, MTN, NEW, PAC, PCC, PCN, SAT, WNC, WSC) or US; sector 98 electric power or 99 all sectors; fuel COL coal excluding waste coal, PEL petroleum liquids, PC petroleum coke. `variable` `stocks`, at the month's end; `unit` `short_ton` (EIA's thousand short tons times 1,000) or `kbbl`; `ts_utc` the month's first day; `freq` `P1M`; `geo` `US-<state>`, `US`, or empty for a region; `node` "<location>, <sector>, <fuel>".

When written: 48,702 rows of the route's 67,687 records (a record without a stocks figure has no row), 320 series, 64 locations; 22,548 rows in short tons and 26,154 in kbbl. The electric power sector held 147.0 million short tons of coal in January 2008, 187.2 in January 2016, 92.7 in January 2023 and 108.8 in July 2026.

## Reading the pages

- Pages sorted by month, location, sector and fuel; the run stops unless the records read equal the API's count, and if a key comes twice.
- A unit other than thousand short tons or thousand barrels stops the run.
- Nothing is filled: a state EIA withholds has no row.

## License

Public: a work of the U.S. government (record 1 of `license_reads.csv`).

## Cross-checks (sessions 927 and 932)

- The states do not sum to the U.S. row, and should not be read as if they did: EIA withholds many states' stocks (28 to 47 states have a coal figure in a month for the electric power sector), so the states summed are a median 90 percent of the U.S. row.
- The census regions sum to about the U.S. row (median 98 percent), but PAC and its two parts PCC and PCN are all listed, so their sum overlaps.
- The Electric Power Monthly's national stocks are this table's U.S. rows: the same series.

## What it does not hold

- 2001 to 2007, and the sectors' parts (utilities, independent producers, commercial and industrial plants): one run each, at about 14 requests.
