# Canada's supply and disposition of crude oil and of natural gas by province, a month, January 2016 to July or August 2026 (Statistics Canada, tables 25-10-0063-01 and 25-10-0086-01)

Energy Research Warehouse (ERW), method note written in session 2185 (chain 097) for a table first written on 24 October 2026 (session 2179).

Tables: `statcan_oil_gas_supply_monthly`

## Publisher and address

Statistics Canada (StatCan), two tables, each read from its full CSV download (a zip holding the table and its metadata file):

- 25-10-0063-01, "Supply and disposition of crude oil and equivalent" (`https://www150.statcan.gc.ca/t1/tbl1/en/tv.action?pid=2510006301`): `https://www150.statcan.gc.ca/n1/tbl/csv/25100063-eng.zip`
- 25-10-0086-01, "Natural gas supply and disposition, monthly" (`https://www150.statcan.gc.ca/t1/tbl1/en/tv.action?pid=2510008601`): `https://www150.statcan.gc.ca/n1/tbl/csv/25100086-eng.zip`

The User-Agent is "Mozilla/5.0 (compatible; ERW-connector/0.1; +https://github.com/SamuelEnrique/erw)". Source ids `statcan:25-10-0063-01` and `statcan:25-10-0086-01`. Connector: `warehouse/connectors/statcan_oil_gas.py` (session 2179), its only table. www150.statcan.gc.ca's robots file (read 353, as read 344 in session 2176) asks a crawl delay of 2 seconds and does not disallow /n1/ or /t1/.

The gas table the chain file named, 25-10-0055-01, is inactive: its page (read 354) says it is archived and "Replaced by 25-10-0086-01". It is not taken.

The table is not scheduled: no line of `warehouse/run_daily.sh`, the other `warehouse/*.sh` scripts, `warehouse/scheduled.py`, `scripts/` or `.github/workflows/` names the connector (searched in session 2185), and `run_status.csv` holds no row for it. It was written once, by run `20261024T014056Z` on the data machine, offline from the saved zips.

## Vintage and revision

Crude oil from January 2016 to July 2026, natural gas from January 2016 to August 2026 (`ts_utc`), 128 months in all. The crude zip was retrieved at 2026-10-24T01:35:55Z and the gas zip at 01:37:35Z, by the session's probe; the write read those copies. Their Last-Modified times are the rows' `vintage`: 2026-09-29T12:30:43Z (crude) and 2026-10-23T12:30:28Z (gas). `coverage.csv` gives the same 56,007 rows, 383 nodes and the same first and last `ts_utc`.

Each run writes the whole table again (`ip.write_snapshot`), and both zips are asked again unless `--offline`, since StatCan revises its tables at the same addresses. No row carries StatCan's revision mark in this run (`x_revised` is blank throughout).

## Shape and variables

Series, 56,007 rows, 23 entities, 65 variables, 463 series (one StatCan vector each).

- `entity` `statcan_oil:<area>` (12 areas: `ca`, `atl` for the Atlantic provinces, nl, ns, nb, qc, on, mb, sk, ab, bc, nt) or `statcan_gas:<area>` (11: `ca`, ns, nb, qc, on, mb, sk, ab, bc, yt, nt).
- `variable` the supply or disposition item as a slug, with ", supply" and ", disposition" dropped. Where the crude table gives one name twice (its inventories by fields and plants, transporters and refineries, under both opening and closing inventory), the parent's slug comes first (`closing_inventory_refineries`). A count of customers ends `_customers`. Crude oil has 34 variables, gas 31; no name is shared between the two (crude `export_to_the_united_states`, gas `exports_to_the_united_states`).
- `unit` `m3` (48,839 rows; Decision 70) or `count` (7,168 rows, the six gas customer counts). Crude is in cubic metres as StatCan gives it; gas is given in thousand cubic metres and written times 1,000. A volume over the month, not a rate; a cubic metre of crude oil is 6.2898 barrels, and a cubic metre is 35.3147 cubic feet (Decision 70).
- `freq` P1M; `ts_utc` the month's first day at 00:00 UTC; `geo` CA or CA-<province>; the Atlantic provinces' rows (`statcan_oil:atl`) carry `geo` CA; `market` empty; `node` the area and item in StatCan's words ("Alberta: Closing  inventory, storage", with StatCan's double space).
- `x_product` crude_oil (25,533 rows) or natural_gas (30,474); `x_item` StatCan's item; `x_parent` the variable of the item this one is part of (blank in 22,265 rows), never to be summed with it; `x_area_total` yes for Canada and the Atlantic provinces (9,229 rows); `x_table`; `x_vector`; `x_revised`.

1,627 values are negative, all but one of them inventory changes, storage adjustments and metering differences (net_inventory_changes 645, storage_adjustments 370, inventory_change_storage 328, metering_differences_line_losses_and_adjustments 283, industrial_consumption 1), as StatCan prints them; 4,962 are zero. The last row of 18 series is earlier than July 2026. No (entity, variable, ts_utc) is given twice. The counts were computed in session 2185 from the rows, read past the 12 header lines with pandas (every column as text).

Not taken, as the header counts them: figures marked ".." (not available: crude 539, gas 23,158) or "x" (suppressed for confidentiality: crude 5,265, gas 384); the gas table's 43,264 figures in gigajoules (no unit in the standard for them) and its 10,752 in Canadian dollars (a currency other than USD is a standing question for the owner); and the crude table's barrels, which are checked and not kept.

## Checks the connector makes

- Before any request, the connector and www150.statcan.gc.ca are checked against `warehouse/metadata/paused_sources.csv`; a paused publisher stops the run with no request. It is not paused.
- Each zip must hold exactly its table and its metadata file, and the metadata must list its members, or the run stops.
- Each line's coordinate must name an area and an item the metadata lists, under the same names as the line; the area must be in the map of 15; the month must read as YYYY-MM; the status must be blank, ".." or "x"; the scale must be units or thousands; the unit must be cubic metres, customers, barrels (crude), gigajoules or Canadian dollars (gas). Anything else stops the run, and so does a key (entity, variable, month) given twice, two items with one variable, or a table with no row.
- Every crude figure is given in cubic metres and in barrels. Both must be withheld alike, and each barrel figure must be within 0.5 barrel plus 0.01 percent of the cubic metres times 6.2898, or the run stops. 25,533 figures were compared.
- Nothing is filled. Ceiling: two requests a run, a pause of 2 seconds after each, as the robots file asks.

## The cross-check

Session 2179 set Canada's exports to the U.S. against EIA's imports from Canada in `runs/c097/s2179/cross.py` (on the data machine, not in git), reading the trial copy of the table:

| Year | Crude, StatCan exports to the U.S., million bbl | EIA imports from Canada, million bbl | Ratio | Gas, StatCan exports to the U.S., bcf | EIA pipeline imports from Canada, bcf | Ratio |
|---|---|---|---|---|---|---|
| 2016 | 1,121.280 | 1,180.948 | 0.949 | 2,876.043 | 2,916.854 | 0.986 |
| 2017 | 1,199.796 | 1,257.907 | 0.954 | 2,973.867 | 2,953.524 | 1.007 |
| 2018 | 1,284.982 | 1,352.105 | 0.950 | 2,793.336 | 2,808.722 | 0.995 |
| 2019 | 1,345.331 | 1,388.624 | 0.969 | 2,632.942 | 2,686.563 | 0.980 |
| 2020 | 1,283.593 | 1,316.054 | 0.975 | 2,441.110 | 2,499.957 | 0.976 |
| 2021 | 1,335.366 | 1,372.250 | 0.973 | 2,729.854 | 2,784.437 | 0.980 |
| 2022 | 1,364.560 | 1,386.375 | 0.984 | 2,942.449 | 2,997.434 | 0.982 |
| 2023 | 1,393.710 | 1,416.899 | 0.984 | 2,868.563 | 2,911.362 | 0.985 |
| 2024 | 1,459.357 | 1,486.547 | 0.982 | 3,059.486 | 3,127.578 | 0.978 |
| 2025 | 1,400.892 | 1,427.229 | 0.982 | 3,159.132 | 3,149.328 | 1.003 |
| 2026 | 824.723 | 857.404 | 0.962 | 1,970.055 | 1,751.404 | 1.125 |

Crude: `statcan_oil:ca` `export_to_the_united_states` times 6.2898, against `eia_crude_imports_detail_monthly` (every grade from Canada to the U.S., kbbl). Gas: `statcan_gas:ca` `exports_to_the_united_states` times 35.3147, against `eia_gas_trade_country_monthly` (`N9102CN2`, MMcf). 2026 is a part year, and StatCan's gas months run past EIA's.

The replaced gas table, 25-10-0055-01, beside 25-10-0086-01 for Canada: 732 figures in both, 676 within 1 percent, a median difference of 0; by item the median differences are 0 except total imports (0.0085).

## License

The header: "License: public (the Statistics Canada Open Licence; see license_verdicts.csv). Source: Statistics Canada, Tables 25-10-0063-01 and 25-10-0086-01. This does not constitute an endorsement by Statistics Canada of this product." `license_verdicts.csv` gives Statistics Canada "may be public", the same if the ERW sells anything (read 346, the Open Licence, recorded in session 2181): "Statistics Canada grants you a worldwide, royalty-free, non-exclusive licence to: use, reproduce, publish, freely distribute, or sell the Information". A value-added product carries a source line and the statement that StatCan does not endorse it; the header carries both. `coverage.csv`: public.

## Found while writing this note

- The docstring gives `geo` as "CA or CA-<province>". The Atlantic provinces' rows (`statcan_oil:atl`, 1,313 rows) also carry `geo` CA, so a filter on `geo` CA takes Canada and the Atlantic provinces together; `entity` or `x_area_total` tells them apart.
- The docstring and the header write the license as "public"; the verdict in `license_verdicts.csv` is "may be public". The session 2176 table's header writes "may be public".
- The docstring says the robots file "disallows its framework and error paths, not /n1/". Read 344 also records files ending .csv, .xls and the like as disallowed. The zips the connector asks are not such files.

Acted on in session 2185: the docstring and the header say the Atlantic provinces carry `geo` CA (filter on the entity), the robots account names the file-ending rules, and both StatCan headers now read "public" for the table's license (the verdict, "may be public", is the publisher's terms; the table's license is public). The table was written again (the same rows).

## What it does not hold

- The gas table's heat content (gigajoules) and values (Canadian dollars).
- The crude table's barrels, which are checked and not kept.
- Months before January 2016, and the inactive gas table 25-10-0055-01.
- Refined products, natural gas liquids other than the crude table's condensate and pentanes plus, and prices.
- Figures StatCan withholds (".." and "x"), which have no row.
