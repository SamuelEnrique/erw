# Canada's electricity receipts, deliveries and availability by province a month, January 2008 to July 2026, the trade with the United States among them (Statistics Canada, table 25-10-0016-01)

Energy Research Warehouse (ERW), method note written in session 2331 (chain 108) for a table first written on 24 October 2026 (session 2328 of chain 108, its report `archive/sessions/SESSION_2328_REPORT.md`).

Tables: `statcan_electricity_trade_monthly`

## Publisher and address

Statistics Canada, table 25-10-0016-01, "Electric power generation, monthly receipts, deliveries and availability" (`https://www150.statcan.gc.ca/t1/tbl1/en/tv.action?pid=2510001601`; formerly CANSIM 127-0003), from the Monthly Electricity Supply and Disposition Survey (survey 2151). The table reads the full CSV download, one request:

- `https://www150.statcan.gc.ca/n1/tbl/csv/25100016-eng.zip`

Source id `statcan:25-10-0016-01`. The zip holds `25100016.csv` (37,718 data lines: 14 areas, 17 components, 223 months, January 2008 to July 2026, every line in "Megawatt hours", scalar factor "units", 0 decimals) and `25100016_MetaData.csv`. The metadata names the areas (Canada, the ten provinces and the three territories), the components with their parents, the symbol legend, 19 notes and one correction. The notes that bear on reading the table:

- Note 3, total receipts: "Nationally, this is the sum of purchased receipts and other receipts from the United States. Provincially, this is the sum of electricity received from other provinces and from the United States."
- Note 7, total deliveries: "Nationally, this is the sum of deliveries of electricity to the United States. Provincially, this is the sum of electricity delivered to other provinces and to the United States."
- Notes 6 and 16 to 17: "other" receipts and deliveries are "Electricity received [given] in compensation".
- Note 18: available for use is "total generation plus total receipts less total deliveries".
- Note 19: the survey's target population "has been expanded to improve coverage of renewable energy in Canada, particularly wind and solar power. As a result of this change, users will have to use caution when comparing data for historical purposes", with changes in British Columbia, Alberta, Ontario, Quebec and Prince Edward Island for wind and in Ontario for solar (no date given).
- Correction 4128 of 7 October 2026: the Manitoba "Receipts from other provinces" and "Total electricity available for use" values for May 2026 were corrected.

Session 2328's probe (`runs/c108/s2328/probe.csv`) made 5 requests, three of them for New Zealand and Chile (not taken; reads 579 to 581) and two to Statistics Canada, 16 seconds apart: the robots file (read 582) and the zip (HTTP 200, 266,977 bytes, at 2026-10-24T07:22:19Z, Last-Modified "Thu, 08 Oct 2026 12:30:35 GMT"). All five are saved in `runs/license_reads/s2328/`; the zip was seeded into `warehouse/raw/statcan_electricity_trade/20261024T072112Z_probe/`, and the trial and the write read it offline.

Connector: `warehouse/connectors/statcan_electricity_trade.py` (session 2328): `[--offline] [--out-dir DIR]`, one request, with a pause of 2 seconds (the robots file's crawl delay). A zip that does not hold `25100016.csv` alone, a unit other than megawatt hours, a scalar factor other than units, an area or component not in its maps, a month that does not read, a status not in its map or a key given twice stops the run. **No schedule runs it**: no step of `warehouse/run_daily.sh`, `warehouse/run_data_machine.sh`, `warehouse/run_data_machine_tables.sh`, `warehouse/run_monthly.sh`, `warehouse/refresh_supply.sh`, `warehouse/scheduled.py` or `.github/workflows/` names it. The table is public, and it is held from the live set (listed under `catalogue_hold` in `warehouse/supabase/live_set.yaml`) and from the Redivis release (`STORAGE_HELD` in `warehouse/redivis/release_v1.py`).

## Vintage and revision

One write, run `20261024T072400Z` ("File holds 25215 rows, one snapshot; the previous file held 0 rows"). `retrieved_at` is 2026-10-24T07:22:19Z in every row, the zip's download time; `vintage` is 2026-10-08T12:30:35Z, its Last-Modified.

StatCan revises the table at the same address. The table is a snapshot: a run replaces the whole file, so a revised month is revised at the next run. `x_revised` carries StatCan's "r": 254 rows, all from 2014 and 2015 (42 for Canada, 46 for Prince Edward Island, 34 for Ontario, the rest spread over the other areas). Manitoba's May 2026 figures, corrected on 7 October 2026 by correction 4128, carry no "r". No figure is marked preliminary.

## Shape and variables

Series, 25,215 rows, 14 entities `statcan_trade:<area>` (`ca` and the provinces' and territories' postal codes in lower case), `geo` CA or CA-<code>, `unit` MWh, `freq` P1M, `market` blank, `node` "<area>: <component>" as StatCan names them, `x_vector` StatCan's vector (170), `x_total` yes for the 7 components whose names begin "Total" (13,217 rows), `x_revised` above. 17 variables:

| Variable | StatCan's component | Areas with rows |
|---|---|---|
| generation | Total generation | all 14, 223 months each |
| receipts_total | Total receipts | Canada and the 10 provinces |
| receipts_other_provinces | Receipts from other provinces | the 10 provinces |
| receipts_us_purchased | Purchased receipts from the United States | Canada and 9 provinces (not Prince Edward Island) |
| receipts_us_other | Other receipts from the United States | Canada and 6 provinces, 39 to 44 months |
| deliveries_total | Total deliveries | Canada and the 10 provinces |
| deliveries_other_provinces | Deliveries to other provinces | the 10 provinces |
| deliveries_us | Deliveries to the United States | Canada and 9 provinces (not Prince Edward Island) |
| deliveries_firm_total, deliveries_firm_other_provinces, deliveries_firm_us | firm deliveries | at most 96 months an area |
| deliveries_non_firm_total, deliveries_non_firm_other_provinces, deliveries_non_firm_us | non-firm deliveries | at most 96 months an area |
| deliveries_other_total, deliveries_other_us | other deliveries | Canada and 6 provinces, 39 to 62 months |
| available_for_use | Total electricity available for use within specific geographic border | all 14, 223 months each |

From the table (`runs/c108/s2331/notes/sc.out`). The three territories have generation and available for use only (446 rows each).

Canada, TWh, the sum of each year's months:

| Year | generation | receipts_us_purchased | deliveries_us | available_for_use |
|---|---|---|---|---|
| 2008 | 601.279 | 23.282 | 55.964 | 569.208 |
| 2012 | 594.875 | 11.392 | 58.034 | 548.233 |
| 2016 | 646.292 | 9.308 | 73.092 | 582.508 |
| 2019 | 640.391 | 13.349 | 60.341 | 593.328 |
| 2022 | 640.092 | 14.096 | 65.406 | 588.782 |
| 2023 | 615.333 | 21.740 | 49.445 | 587.628 |
| 2024 | 609.488 | 23.277 | 35.778 | 596.987 |
| 2025 | 625.212 | 25.180 | 32.072 | 618.320 |
| 2026 (January to July) | 383.334 | 12.561 | 28.901 | 366.995 |

- **Canada's totals are the U.S. trade.** By notes 3 and 7, Canada's `receipts_total` and `deliveries_total` are its receipts from and deliveries to the United States; Canada has no rows for the other-provinces components. A province's totals include its trade with other provinces, so the provinces' totals do not sum to Canada's.
- **The provinces in 2024.** Deliveries to the U.S.: Ontario 12.482 TWh, British Columbia 6.299, Manitoba 5.991, Quebec 5.938, New Brunswick 2.253, Newfoundland and Labrador 1.830, Alberta 0.520, Saskatchewan 0.465, Nova Scotia 0; they sum to Canada's 35.778. Purchased receipts from the U.S.: British Columbia 14.317 TWh, Quebec 3.882, Manitoba 3.138, then six provinces under 0.7 each; they sum to Canada's 23.277.
- **Negative values.** Three rows, all Alberta: `deliveries_other_provinces` -11,739 MWh in February 2016 and -451 MWh in August 2018, `deliveries_total` -5,575 MWh in February 2016. Kept as StatCan publishes them.
- **Zeros.** 1,816 rows are 0, most in the firm, non-firm and other deliveries and the U.S. receipts. Every value is a whole MWh.

## Placing values in time, and what is filled

`ts_utc` is the month's first day at 00:00:00Z (StatCan's REF_DATE, YYYY-MM). StatCan marks 12,503 of its 37,718 cells ".." ("not available for a specific reference period"); they have no row, as header line 3 says. Most are the firm, non-firm and other deliveries, which StatCan gives for at most 96 months an area, and the other receipts from the U.S. No cell is marked "x" or "F", though the connector would count them. Nothing is filled.

## License

Header: "License: public (the Statistics Canada Open Licence; see license_verdicts.csv). Source: Statistics Canada, Table 25-10-0016-01. This does not constitute an endorsement by Statistics Canada of this product." `warehouse/metadata/license_verdicts.csv`: Statistics Canada, read 361 (the Statistics Canada Open Licence), "Subject to this licence, Statistics Canada grants you a worldwide, royalty-free, non-exclusive licence to: use, reproduce, publish, freely distribute, or sell the Information; ...", verdict "may be public", if the ERW sells anything "may be public", its note asking for "Adapted from Statistics Canada, name of product, reference date. This does not constitute an endorsement by Statistics Canada of this product." www150.statcan.gc.ca's robots file asks a crawl delay of 2 seconds, disallows framework and error paths, not `/n1/`, and names no AI agent (read 582). `docs/licenses.md`, the table's row: verdict today "may be public", flag public, "agrees", ERW verdict public.

## Checks (session 2331)

The figures in this note were computed from the rows of `warehouse/output/statcan_electricity_trade_monthly.csv`, read past its 10 header lines (counted), and from the saved zip, read only (scripts `runs/c108/s2331/notes/sc.py`, `sc_meta.py` and `trials.py`, outputs `sc.out`, `sc_meta.out`, `sc_meta_tail.out` and `trials.out` beside them).

- 25,215 rows, 14 areas, 17 variables, January 2008 to July 2026 (223 months), as header lines 1 and 10 state; no (entity, variable, ts_utc) twice; no blank value; MWh and P1M throughout.
- **Against the zip:** 37,718 lines, 25,215 with a value and 12,503 marked "..", no other status; 254 lines marked "r"; the table's row count and its ".." count in header line 3 are the zip's.
- **The trial against the table:** `runs/c108/s2328/trial/statcan_electricity_trade_monthly.csv` has the same 25,215 keys with no cell differing.
- Session 2328's cross-check (`runs/c108/s2328/cross.py`, `cross.out`, run on the trial): receipts against their three parts in 239 area-months, no gap; deliveries against other provinces plus the U.S. in 1,846, no gap; deliveries against firm, non-firm and other in 315, one gap (Canada, February 2013, -125,051 MWh); available for use against generation plus receipts less deliveries in 2,390, two gaps (British Columbia and Canada, February 2019, -70,931 MWh); Canada's generation equal to `statcan_electricity_generation_monthly`'s total in all 223 months. Its comparison with `eia_international_electricity_annual` prints 2017 to 2024 only.
- Session 2331's own, the whole overlap with EIA's U.S. imports and exports (2008 to 2024, `sc.out`): Canada's deliveries to the U.S. less EIA's U.S. imports are -1.06 TWh (2008), -0.21, -0.71, -0.84, -1.22, -7.09 (2013), -7.72, -8.67 (2015), 0.38 (2016), 6.36, 3.45, 1.29 (2019), 5.67, 7.17, 8.44 (2022), 10.53 (2023) and 2.52 (2024). Canada's purchased receipts from the U.S. less EIA's U.S. exports are -0.92 (2008) to -0.44 (2015) in each year to 2015, then 3.09 (2016), 0.53, -0.62, -6.66 (2019), -4.32, -0.84, -1.66, 1.73 and 3.84 (2024).

## The session report against the table

Every figure of `SESSION_2328_REPORT.md` checked against the table, the saved zip and `cross.out` holds (25,215 rows, January 2008 to July 2026, 12,503 cells marked "..", MWh as published, the four identities and their two gaps, the 223 months of generation equal to the generation table's, 2024's 35.78 against 33.25 TWh and 23.28 against 19.44 TWh, 2017's 72.04 against 65.68, deliveries to the U.S. falling from 65.4 TWh in 2022 to 35.8 in 2024 and purchases rising from 14.1 to 23.3, the Open Licence, a crawl delay of 2 seconds, 5 requests of 20), except:

- "Canada's deliveries to the U.S. are 2.5 to 8.1 TWh a year above EIA's U.S. imports": 1.29 to 10.53 TWh over 2017 to 2024, and below EIA's in every year from 2008 to 2015 (point 1).
- "Canada's purchased receipts from the U.S. are 0.6 to 6.7 TWh from EIA's U.S. exports": 0.53 in 2017 (point 1).

## What it does not hold

- Generation by type (in `statcan_electricity_generation_monthly`), the trade by U.S. state, region or interconnection, prices or values of the trade, months before 2008 (table 25-10-0001-01, terminated), the annual tables, and the metadata's notes and correction, which no column carries.

## Points for the session to act on

1. **The report's comparison with EIA gives ranges the table does not bear out.** The report says Canada's deliveries to the U.S. "are 2.5 to 8.1 TWh a year above EIA's U.S. imports" and its purchased receipts "0.6 to 6.7 TWh from EIA's U.S. exports". Over the eight years `cross.out` prints (2017 to 2024), deliveries less EIA's imports are 1.29 (2019) to 10.53 TWh (2023), with 8.44 in 2022; receipts less EIA's exports range in size from 0.53 (2017) to 6.66 TWh (2019). Over the whole overlap, 2008 to 2015, StatCan's deliveries are below EIA's imports in every year (by 0.21 to 8.67 TWh), so "above" holds from 2016 only.
2. **The header does not say Canada's totals are the U.S. trade only.** Header line 2 marks the totals `x_total` "never summed with their parts", but StatCan's notes 3 and 7 define Canada's total receipts and deliveries as those with the United States, and a province's as those with other provinces and the U.S. A reader who sums the provinces' `deliveries_total` (or `receipts_total`) to reach Canada's counts the interprovincial trade that Canada's total leaves out. One clause in header line 2 would prevent it.
3. **StatCan's caution on historical comparison is not carried.** Note 19 warns that the survey's target population was expanded for wind and solar, so "users will have to use caution when comparing data for historical purposes", in five provinces for wind and Ontario for solar. `generation` and `available_for_use` are affected; neither the header, the docstring nor the report mentions it, and StatCan gives no date for the change.
4. **Three negative values are not described.** Alberta's `deliveries_other_provinces` is -11,739 MWh in February 2016 and -451 MWh in August 2018, and its `deliveries_total` -5,575 MWh in February 2016. They are StatCan's as published; header line 3 says nothing of signs, and a reader may take deliveries as never negative.

Compared besides, with no contradiction found: the header's and docstring's counts, components, areas, unit, the ".." count, "Nothing is filled", `x_total`, `x_vector`, `x_revised` and the license against the rows, the zip and its metadata. The correction of Manitoba's May 2026 figures is StatCan's own and carries no "r" in its file.

Acted on in session 2331: session 2328's report now gives the gaps to EIA over every year both tables hold (deliveries above EIA's imports by 0.38 to 10.53 TWh from 2016 to 2024, below by 0.21 to 8.67 TWh from 2008 to 2015; receipts 0.44 to 6.66 TWh from EIA's exports). The docstring and header line 3 now say that Canada's totals are its trade with the United States only, carry StatCan's note 19 on wind and solar, and list the three negative figures, as the connector finds them. The table was written again offline: the same rows.
