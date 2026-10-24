# Canada's petroleum products by supply and disposition, by province, a month, January 2019 to July 2026: production, trade, stocks, refinery inputs and products supplied for 31 products, in cubic metres (Statistics Canada, table 25-10-0081-01)

Energy Research Warehouse (ERW), method note written in session 2380 (chain 112) for a table first written on 24 October 2026 (session 2378 of chain 112, its report `archive/sessions/SESSION_2378_REPORT.md`).

Tables: `statcan_petroleum_products_monthly`

## Publisher and address

Statistics Canada (StatCan), table 25-10-0081-01, "Petroleum products by supply and disposition, monthly" (`https://www150.statcan.gc.ca/t1/tbl1/en/tv.action?pid=2510008101`), read from the table's full CSV download, one request:

- `https://www150.statcan.gc.ca/n1/tbl/csv/25100081-eng.zip`

Source id `statcan:25-10-0081-01`. The zip holds `25100081.csv` (24,758,288 bytes, 138,411 lines of data) and `25100081_MetaData.csv`, whose member notes define the lines (below). The metadata names five surveys: Monthly Refined Petroleum Products (2150), Crude Oil and Natural Gas (2198), the Monthly Renewable Fuel and Hydrogen Survey (5294), Canadian international merchandise trade (5295) and the Monthly Energy Transportation and Storage Survey (5300). Its cube note 24: in January 2019 the refined products survey changed (upgraders and terminals added, variables added and dropped); data before 2019 stay in tables 25-10-0041-01 to 25-10-0044-01, and "the current estimates may not be comparable with the estimates prior to January 2019".

Session 2378's probe (`runs/c112/s2378/probe.csv`) made 2 requests to www150.statcan.gc.ca, 10 seconds apart: the robots file (09:05:10Z, read 619) and the zip (HTTP 200, 1,653,149 bytes, at 2026-10-24T09:05:20Z, Last-Modified "Tue, 29 Sep 2026 12:30:43 GMT"). Both are saved in `runs/license_reads/s2378/`. The session also made 7 requests to EIA's API for routes it left (`runs/c112/s2378/meta_*.json`, `sample_rescom.json`, `routes.out`): lease condensate ends in 2021 and coalbed methane in 2019, as the report says.

Connector: `warehouse/connectors/statcan_petroleum_products.py` (session 2378): `[--offline] [--out-dir DIR]`, one request, asked again unless `--offline`. A unit other than "Cubic metres", a scalar factor other than "units", an area, item or product not in its maps, a month that does not read, a status other than blank, "..", "x" or "F", or a key given twice stops the run. **No schedule runs it**: no step of `warehouse/run_daily.sh`, `warehouse/run_data_machine.sh`, `warehouse/run_data_machine_tables.sh`, `warehouse/run_monthly.sh`, `warehouse/refresh_supply.sh`, `warehouse/scheduled.py` or `.github/workflows/` names it. The table is public; it is held from the live set (listed under `catalogue_hold` in `warehouse/supabase/live_set.yaml`) and from the Redivis release (`STORAGE_HELD` in `warehouse/redivis/release_v1.py`).

## Vintage and revision

One write, run `20261024T090640Z` ("File holds 112385 rows, one snapshot; the previous file held 0 rows"), from the saved zip. `retrieved_at` is 2026-10-24T09:05:20Z and `vintage` the zip's Last-Modified, 2026-09-29T12:30:43Z, in every row. The months run from January 2019 to July 2026 (91), the same for every area.

StatCan revises the table at the same address, and each run asks the zip again and writes the whole table. No line of this file carries a symbol: the SYMBOL column is blank in all 138,411, so `x_revised` is blank in every row (no "r" and no "p").

## Shape and variables

Series, 112,385 rows, 406 entities `statcan_pp:<area>:<product>` (14 areas: Canada, the ten provinces and the three territories; 31 products), 1,331 nodes (area, item and product), `unit` m3, `freq` P1M, `market` blank, `geo` CA or CA-<province>. `x_product` StatCan's product; `x_parent` the product it is part of (blank for the three tops); `x_total` yes on 17,329 rows, the products with parts; `x_vector` StatCan's vector.

| Variable | StatCan's line | Note | Rows | Areas | Negative | Zero |
|---|---|---|---|---|---|---|
| field_production | Field production, supply | 4: NGL production at gas processing plants | 1,183 | 4 | 0 | 0 |
| renewable_production | Renewable fuel plant net production, supply | 19 | 463 | 2 | 0 | 147 |
| refinery_production | Refinery and blender net production, supply | 13: net of reprocessing; may be negative | 15,430 | 10 | 1,198 | 6,240 |
| imports | Imports, supply | 6: the province of entry | 24,206 | 14 | 0 | 12,051 |
| adjustments | Adjustments, supply | 25 to 28 | 668 | 1 (Canada) | 325 | 0 |
| stock_change | Stock change, disposition | 14 | 26,208 | 12 | 6,998 | 12,339 |
| refinery_inputs | Refinery and blender net inputs, disposition | 13 | 6,381 | 10 | 820 | 2,301 |
| exports | Exports, disposition | 5 | 20,408 | 14 | 0 | 10,169 |
| products_supplied | Products supplied, disposition | 12 | 1,238 | 1 (Canada) | 1 | 318 |
| ending_stocks | Ending stocks | 3, 15 | 16,200 | 9 | 0 | 6,177 |

"Areas" counts the areas with at least one value. The eleventh line the docstring and header name, "Net inter-regional receipts, supply" (`net_interregional_receipts`), is a member of the metadata (note 9) but has no line in the CSV (point 1).

Canada's flows in 2025, million m3 summed over the twelve months, from the table (`runs/c112/s2375/notes/pp.out`):

| Product | Refinery production | Imports | Exports | Adjustments | Products supplied |
|---|---|---|---|---|---|
| Finished petroleum products | 116.347 | 9.100 | 20.592 | -0.432 | 104.295 |
| Finished motor gasoline | 44.246 | 1.945 | 1.885 | -1.106 | 43.186 |
| Distillate fuel oil | 42.224 | 0.926 | 10.521 | 0.674 | 33.258 |
| Kerosene-type jet fuel | 6.591 | 3.353 | 0.552 | | 9.377 |
| Still gas | 8.910 | | | | 8.910 |
| Petroleum coke | 4.404 | 1.377 | 1.556 | | 4.228 |
| Asphalt | 5.341 | 0.225 | 3.188 | | 2.352 |
| Residual fuel oil | 3.113 | 0.340 | 1.770 | | 1.685 |

Natural gas liquids in 2025: field production 69.632, imports 17.546, exports 17.582 million m3 (propane 19.634, 0.197 and 13.849).

- **Signs.** Stock change is positive for a build and negative for a draw: it equals the month's ending stocks less the previous month's within 1 m3 in 15,806 of 15,994 cells where both are given, and has the same sign in 7,172 of the 7,177 where the change exceeds 1,000 m3 (point 2). Refinery production and inputs are net (note 13) and negative in 1,198 and 820 rows. Adjustments balance the motor gasoline blending components and renewable fuels (notes 25 to 28) and are negative in 325 rows. Products supplied is negative once: petroleum coke, Canada, August 2022, -308,782 m3.
- **Products supplied is zero by assumption** for motor gasoline blending components (all 91 rows 0) and fuel ethanol (all 79 rows 0) (notes 25 and 26); for renewable fuels it is 0 except in 10 months, by at most 39 m3, the same months its parts do not add to it.

## Placing values in time, and what is filled

`ts_utc` is the month's first day at 00:00:00Z; flows are the month's and ending stocks are "as of 12 midnight on the last day of the month" (note 3). A figure marked ".." (626) or "x" (25,400) has no row, as header line 3 counts them; no line is "F". The "x" cells are mostly the smaller provinces' (British Columbia 5,685, New Brunswick 5,005, Newfoundland and Labrador 4,351, Nova Scotia 4,174, Prince Edward Island 3,877). Nothing is filled.

## License

Header: "License: public (the Statistics Canada Open Licence; see license_verdicts.csv). Source: Statistics Canada, Table 25-10-0081-01. This does not constitute an endorsement by Statistics Canada of this product." `warehouse/metadata/license_verdicts.csv`: Statistics Canada, read 361, the Open Licence, "Statistics Canada grants you a worldwide, royalty-free, non-exclusive licence to: use, reproduce, publish, freely distribute, or sell the Information; ...", verdict "may be public", the same if the ERW sells anything; a value-added product carries a source line and the statement that StatCan does not endorse it, which the header carries. `docs/licenses.md`, the table's row: flag public, "agrees", ERW verdict public. Read 619 records the robots file: a crawl delay of 2 seconds, framework and error paths disallowed, not /n1/, no AI agent named; the file also disallows paths ending .csv, .xls and the like, which the zip is not.

## Checks (session 2380)

The figures in this note were computed from the rows of `warehouse/output/statcan_petroleum_products_monthly.csv`, read past its 10 header lines (counted), and from the saved zip, read only (scripts `runs/c112/s2375/notes/pp.py` and `pp2.py`, outputs `pp.out`, `pp2.out` and the metadata as `pp_meta.txt` beside them).

- 112,385 rows, 406 series, 91 months, as header lines 1, 3 and 10 state; no (entity, variable, ts_utc) twice; m3 throughout.
- **Against the zip:** 138,411 lines: 112,385 with a value (the table's rows, the trial's too), 25,400 "x" and 626 ".."; every unit "Cubic metres", every scalar factor "units", every DECIMALS 0.
- **The trial against the table:** `runs/c112/s2378/trial/statcan_petroleum_products_monthly.csv` has the same 112,385 keys with 0 differences in value or `retrieved_at`.
- **Products supplied against note 12** (field, renewable and refinery production, imports, net receipts and adjustments, less stock change, refinery inputs and exports): within 1 m3 in all 1,226 Canada cells where every line the series carries is given.
- **Stock change against ending stocks:** above (15,806 of 15,994 within 1 m3).
- **Provinces against Canada:** refinery production of finished products, in the 24 months where every province that ever reports it is given, is 1.01 to 1.49 million m3 a month below Canada's, the suppressed provinces' share.
- Session 2378's cross-check (`runs/c112/s2378/cross.py`, `cross.out`, run on the trial): natural gas liquids' four parts against it within 1 m3 in 2,165 of 2,165 cells; renewable fuels' two in 5,253 of 5,271 (5,262 within 0.5 percent; the 18 others are Canada's renewable production and products supplied in the same 9 months, by at most 39 m3); finished products' fourteen in 2,390 of 2,390; the provinces against Canada for finished products in 182 of 182 complete cells; Canada's finished motor gasoline supplied 43.18 million m3 (2019), 37.26 (2020), 40.00, 41.48, 42.18, 42.04 and 43.19 (2025).

## The session report against the table

Every figure of `SESSION_2378_REPORT.md` checked against the table, the zip and `cross.out` holds (112,385 rows, 406 series, January 2019 to July 2026, 31 products, m3, the parents and `x_total`, 25,400 "x" and 626 "..", the cross-check's counts, 43.18, 37.26 and 43.19 million m3, read 619, the EIA routes' end years), except:

- "eleven supply and disposition items ... inter-regional receipts": the file holds ten (point 1).
- "for Canada and each province and territory": products supplied and adjustments are Canada's only (point 3).
- "robots, the table's zip (1.65 MB); 3 s apart": the two requests were 10 seconds apart (point 4).
- "Canada is the largest supplier of the United States' imported products": not tested here.

## Limits

- **Consumption is Canada's only.** Products supplied, StatCan's approximation of consumption (note 12), and the adjustments are given for Canada alone; the provinces carry production, trade, stocks and refinery flows.
- **Provincial imports are by province of entry** (note 6), not of use.
- **The finished motor gasoline adjustment is applied only to the Canada total** (note 17), so the provinces' gasoline does not balance as Canada's does.
- **Suppression is heavy in the smaller provinces**, so the provinces do not add to Canada for most lines.
- **January 2019 is a break** (cube note 24); earlier years are in other tables, not comparable.

## What it does not hold

- Months before January 2019 (tables 25-10-0041-01 to 25-10-0044-01), inter-regional receipts (not in the file), crude oil (in `statcan_oil_gas_supply_monthly`), prices, and quantities in energy units.

## Points for the session to act on

1. **The table has ten lines, not eleven: StatCan's file holds no inter-regional receipts.** The docstring, header line 2 and the report list `net_interregional_receipts` ("Net inter-regional receipts, supply") among the items. The metadata lists the member (note 9: "The difference between total movements into and total movements out of each province and territory by pipeline, rail, tanker, and barge"), but none of the CSV's 138,411 lines carries it, and the table has no such row. The header could say the line is listed but not published.
2. **The sign of stock change: the header does not give it, and StatCan's note contradicts itself.** Note 14 reads "The difference between stocks at the beginning of the month and stocks at the end of the month. A negative number indicates a decrease in stocks and a positive number indicates an increase in stocks." The data follow the second sentence: stock change equals ending stocks less the previous month's within 1 m3 in 15,806 of 15,994 cells, and products supplied subtracts it (note 12). Header line 2 could say "stock_change positive for a build", and that refinery production and inputs are net and may be negative (note 13).
3. **Products supplied and adjustments are Canada's only.** The report says the table holds, "for Canada and each province and territory", the eleven items; products supplied (1,238 rows) and adjustments (668) have values for Canada only, renewable production for 2 areas, field production for 4, ending stocks for 9. The header could say which lines are national only.
4. **The requests were 10 seconds apart, not 3.** The report's pulls table says "3 s apart"; the probe log has the robots file at 09:05:10Z and the zip at 09:05:20Z. The crawl delay of 2 seconds was kept either way.

Compared besides, with no contradiction found: the header's and docstring's counts, months, products, parents and the three tops, `x_total`, the units, the statuses counted, "Nothing is filled", `retrieved_at` and `vintage` against the probe log, the robots file, the license lines, and every row against the zip.

Acted on in session 2380: the docstring and header line 2 now say StatCan lists inter-regional receipts but publishes none, that stock change is positive for a build (note 14's second sentence, which the data follow), that refinery production and inputs are net and can be negative, and that products supplied and adjustments are Canada's only. Session 2378's report now gives ten items, the national-only lines and the requests 10 seconds apart. The table was written again offline: the same rows.
