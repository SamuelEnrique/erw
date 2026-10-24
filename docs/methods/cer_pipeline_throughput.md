# Throughput and capacity of the nine Canadian pipelines that cross the U.S. border (Canada Energy Regulator)

Energy Research Warehouse (ERW), method note written in session 2171 (chain 094) for a table first written on 24 October 2026 (session 2169, `archive/sessions/SESSION_2169_REPORT.md`).

Tables: `cer_pipeline_throughput`

## Publisher and address

Canada Energy Regulator (CER), Pipeline Throughput and Capacity Data, listed in the Government of Canada's open data catalogue (`https://open.canada.ca/data/en/dataset/dc343c43-a592-4a27-8ee7-c77df56afb34`); one CSV a pipeline at `https://www.cer-rec.gc.ca/open/energy/throughput-capacity/<pipeline>-throughput-and-capacity.csv`. Source id `cer:throughput_capacity`. Files saved under `warehouse/raw/cer_throughput/`.

Connector: `warehouse/connectors/cer_throughput.py` (session 2169): `[--offline] [--out-dir DIR]`, nine requests: oil, a month by product: keystone, enbridge-mainline, southern-lights, cochin; gas, a day: foothills, alliance, westcoast, tcpl-mainline, mnp. **No schedule runs it**: no step of `warehouse/run_daily.sh`, `warehouse/run_data_machine.sh`, `warehouse/run_data_machine_tables.sh`, `warehouse/run_monthly.sh`, `warehouse/scheduled.py` or `.github/workflows/` names it.

## Vintage and revision

One run, `20261024T004836Z`; the files retrieved from 2026-10-24T00:41:07Z to 00:46:14Z; `vintage` each file's last-modified time, 2026-08-27T21:29:23Z to 21:33:30Z. A later run merges by (entity, variable, ts_utc).

## Shape and variables

Series, 408,073 rows, `unit` m3/d (Decision 69: the CER's thousand cubic metres a day times 1,000; a rate, never summed over days, and oil and gas cubic metres never added), `geo` CA, `node` the pipeline, key point (and product) in the CER's words; `x_company`, `x_direction`, `x_trade_type`, `x_latitude`, `x_longitude`, `x_reason` (the CER's reason for variance, on 3,536 rows).

| Pipeline (entity's second part) | Rows | Entities | Variables (rows) | freq | First to last |
|---|---|---|---|---|---|
| transcanada_tc_canadian_mainline_pipeline | 213,510 | 17 | capacity, throughput (106,755 each) | P1D | 2006-01-01 to 2026-06-30 |
| westcoast_or_bc_pipeline_system | 100,670 | 8 | capacity, throughput (50,335 each) | P1D | 2006-01-01 to 2026-06-30 |
| foothills_system | 29,944 | 2 | capacity, throughput | P1D | 2006-01-01 to 2026-06-30 |
| maritimes_northeast_pipeline_m_np_system | 29,944 | 2 | capacity, throughput | P1D | 2006-01-01 to 2026-06-30 |
| alliance_pipeline | 29,844 | 2 | capacity, throughput | P1D | 2006-01-01 to 2026-06-30 |
| enbridge_canadian_mainline_system | 2,756 | 11 | throughput 1,820, nameplate_capacity 468, available_capacity 468 | P1M | 2007-01-01 to 2026-06-01 |
| keystone_pipeline | 852 | 4 | throughput 384, available_capacity 192, committed_volume 138, uncommitted_volume 138 | P1M | 2010-07-01 to 2026-06-01 |
| cochin_pipeline | 373 | 5 | throughput 187, available_capacity 186 | P1M | 2014-07-01 to 2026-06-01 |
| southern_lights_pipeline | 180 | 3 | throughput 120, available_capacity 60 | P1M | 2011-03-01 to 2025-12-01 |

Entities: `cer_pipe:<pipeline>:<key point>` for an oil key point's capacity (one figure a month for all its products), `...:<key point>:<product>:<trade type>` for an oil line's volumes, `...:<key point>:<direction>` for a gas line. Trade types in the rows: export, import, intracanada, "intracanada / export" (Enbridge, 707 rows) and blank (Keystone, 414 rows).

## Placing values in time, and what is filled

`ts_utc` is the CER's Date at 00:00:00Z: an oil month's first day (P1M), a gas day (P1D). The gas files' GJ/d are not taken. A blank has no row; nothing is filled. Every gas line holds every day of 2006-01-01 to 2026-06-30 (7,486) except Alliance, which lacks 14 (2007-07-18, 2007-07-27, 2008-06-27, 2009-06-04, 2012-10-02 to 04, 2014-02-01, 2015-08-08 to 13).

## License

Header: "License: public. Contains information licensed under the Open Government Licence - Canada (https://open.canada.ca/en/open-government-licence-canada)." The report records the verdict as a new entry (read 309), may be public in both columns.

## Checks (session 2171)

The figures in this note were computed from the rows of `warehouse/output/cer_pipeline_throughput.csv`, streamed past its 10 header lines (scripts in `runs/c094/s2171/`).

- 408,073 rows, `ts_utc` from 2006-01-01T00:00:00Z to 2026-06-30T00:00:00Z, as the header states, with its row counts by pipeline; no (entity, variable, ts_utc) twice.
- Five throughput values are negative: TC Mainline's Eastern Triangle NOL receipts, east (2010-04-30, 2010-05-02, 2010-07-02, as low as -943,910.533 m3/d) and Westcoast's Sunset Creek, east (2012-11-30, -600; 2013-06-18, -100).
- Oil capacity: monthly throughput of a key point's products exceeds its nameplate capacity in 7 of 468 Enbridge key point months; its available capacity exceeds its nameplate in 184 of 468.
- Session 2169's cross-check (`runs/c094/s2169/cross.py`), run again: its output is identical to the saved `cross.out`.
  - Keystone's and Enbridge Mainline's throughput labelled export, in million barrels a year, against EIA's crude imports from Canada (`eia_crude_imports_detail_monthly`): 2021 378 against 1,372 (0.276), 2022 365 against 1,386 (0.263), 2023 390 against 1,417 (0.275), 2024 411 against 1,487 (0.277), 2025 393 against 1,427 (0.275). Enbridge's 707 rows labelled "intracanada / export" are not in that sum.
  - Throughput above capacity (gas: capacity; oil: available capacity): 5,939 of 202,861 key point periods with both.

## Where the description and the data disagree

1. **Contracted volumes and nameplate capacity.** The docstring says Enbridge's Mainline file gives no committed or uncommitted volumes, "so its lines have throughput and capacity only", implying the other oil lines carry them. Only Keystone has `committed_volume` and `uncommitted_volume` (138 rows each); Cochin and Southern Lights have neither (Southern Lights gives committed and uncommitted diluent as two products of `throughput`). `nameplate_capacity` occurs only on Enbridge's rows; Keystone, Cochin and Southern Lights have `available_capacity` alone.
2. **Trade types.** The docstring lists "export, import, intracanada, domestic"; the rows hold no "domestic", but "intracanada / export" (707 rows) and blank (414 rows).
3. **A key with an empty part.** Keystone's committed and uncommitted volumes come on the CER's product "Total" with no trade type, so their entity ends in an empty part: `cer_pipe:keystone_pipeline:international_boundary_at_or_near_haskett_manitoba:total:`.
4. **A capacity row's trade type.** A key point's oil capacity is written once a month from the first product row met, and its `x_trade_type` is that row's: Enbridge's into_sarnia capacity carries import on 231 months and "intracanada / export" on 3; Keystone's carries blank on 138 and export on 54. Neither the docstring nor the header says so.

## The session report against the table

Every figure of `SESSION_2169_REPORT.md` checked against the table, the code and the rerun cross-check holds: 408,073 rows, 2006 to June 2026, Keystone from 2010, the nine pipelines, `m3/d` as Decision 69, the keys (Enbridge's ex-Gretna carrying one product as export and as intracanada flow; Westcoast's Kingsvale in two directions), Enbridge's file without contracted volumes, 365 to 411 million barrels a year from 2021 to 2025 at 0.263 to 0.277 of EIA's 1,372 to 1,487, and 5,939 of 202,861 periods above capacity (2.9 percent). Its statements about routes outside the table (Trans Mountain, Express, rail) and the CER's notes on capacity were not checked. None found that does not hold; note that Southern Lights ends in December 2025, not June 2026.

Acted on in session 2171: a blank trade type no longer leaves an empty last part in the entity (Keystone's 276 rows of contracted volumes at Haskett, written again under `...:total`; the archive records the old keys as deleted); the docstring now says which lines carry contracted volumes and nameplate capacity, which trade types occur, and that a capacity row carries the first product row's direction and trade type. The table was written again offline (408,073 rows).

## What it does not hold

- The CER's other thirteen pipelines, the gas files' energy in GJ/d, and any sum of oil and gas volumes.
