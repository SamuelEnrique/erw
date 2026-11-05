# ERCOT real-time prices at the storage resources' settlement points, the hubs and the Load Zones, a 15-minute interval, from 28 September 2026 (ERCOT NP6-905-CD)

Energy Research Warehouse (ERW), method note written in session 2256 (chain 102) for a table first written on 5 October 2026 (session 120).

Tables: `ercot_rtm_node_prices`

## Publisher and address

Electric Reliability Council of Texas (ERCOT), "Settlement Point Prices at Resource Nodes, Hubs and Load Zones" (NP6-905-CD, report type 12301): one small zip for each 15-minute Settlement Interval, with the real-time Settlement Point Price of every settlement point. ERCOT's public list keeps seven days of it.

`https://www.ercot.com/misapp/servlets/IceDocListJsonWS?reportTypeId=12301` (the document list, JSON)

`https://www.ercot.com/misdownload/servlets/mirDownload?doclookupId=<DocID>` (each interval's zip, about 8 kB: 8,240 bytes on average over the 2,451 saved)

Product page: `https://www.ercot.com/mp/data-products/data-product-details?id=NP6-905-CD`. The User-Agent is "Mozilla/5.0 (compatible; ERW-connector/0.1; +https://github.com/SamuelEnrique/erw)". Every request goes to the host `www.ercot.com`, under `/misapp/` and `/misdownload/`, paths ERCOT's robots file disallows (read 170 of `warehouse/metadata/license_reads.csv`, session 2002, 23 October 2026 at 15:11:50 UTC). Whether the ERW keeps reading these paths is a standing question for the owner; neither the connector's docstring nor the table's header says so.

Source id `ercot:NP6-905-CD`, shared with `ercot_rtm_hub_prices`. Connector: `warehouse/connectors/ercot_rt_spp.py` (session 120), its only table; `warehouse/connectors/ercot_zone_prices.py` names this table in a comment and does not write it. The connector's `--pull-dam` (session 358) saves ERCOT's day-ahead Settlement Point Prices (NP4-190-CD) and writes no table. The settlement points kept are read from `ercot_dam_esr_awards`, which must be on the machine. Read by `warehouse/derived/ercot_storage_realtime.py` (`ercot_storage_node_basis`). Method: `docs/methods/ercot_storage_realtime.md`.

Schedule: `warehouse/scheduled.py`, step `ercot_rtm_node_prices` (`ercot_rt_spp.py --daily --max-rows 500000`), the first step after the sync in `warehouse/run_data_machine.sh`, the data machine's daily run ("ERW data machine daily", `scripts/register_data_machine_daily.ps1`; session 204, the owner's ruling of 12 October 2026). The step refuses to run on GitHub's runner. `warehouse/run_data_machine_tables.sh` names the table in its weekly load list, which the loader leaves (the table is under `catalogue_hold`). The connector writes no run status: `warehouse/metadata/run_status.csv` holds no row for it. Its own record is `warehouse/raw/ercot_rtm_spp/rows_by_run.csv` (13 runs from 12 to 23 October 2026: 672 and 33 files on 12 October, then 95 to 97 a day) and a log a run, `warehouse/raw/ercot_rtm_spp/pull_<run>.log`.

The first date is from session 120's report (this table, 213,900 rows, "the week listed"), from the earliest `retrieved_at` in the rows, 2026-10-05T09:23:38Z, and from the commit that first adds its coverage row, `0e31e89e`, 5 October 2026 at 10:07 UTC.

## Vintage and revision

Intervals 2026-09-28T04:45:00Z (23:45 Central on 27 September) to 2026-10-23T17:00:00Z, written by run `20261023T172010Z`. `retrieved_at` is the time each zip was saved: 215,280 rows on 5 October 2026, 219,648 on 12 October, then 29,640 to 30,264 a day from 13 to 23 October. `vintage` is empty.

Each run with a new file reads every saved zip again and merges the rows into the table held on (entity, variable, ts_utc) (`ip.write_csv`): the header's last line says this run wrote 764,400 rows, 29,952 new and 734,448 replacing. ERCOT posts a price once; an interval posted twice is read once when the prices are the same (8 October 2026 11:45 Central, the log says so) and left out when they differ (none so far: "0 files not written").

`coverage.csv` (on main and in this worktree) and `archive_manifest.csv` give 734,448 rows to 2026-10-22T17:00:00Z, last run 2026-10-22T17:20:29Z: they describe the table before the run of 23 October, which added 29,952 rows.

## Shape and variables

Series, 764,400 rows, 312 entities, one variable. `entity` `ercot:<settlement point>`; `variable` `spp_rtm`; `unit` USD/MWh; `freq` PT15M; `ts_utc` the interval's start, read from the file's DeliveryDate, DeliveryHour and DeliveryInterval in Central time (never from the file's name); `geo` US-TX; `market` `ercot_rtm`; `node` the settlement point's name; `source_url` the zip's address (2,450 distinct); `x_point_type` ERCOT's SettlementPointType.

| `x_point_type` | Points | What they are |
|---|---|---|
| RN | 293 | resource nodes at which a storage resource is settled (the header: 293 of the 295 points in `ercot_dam_esr_awards`) |
| LZ | 8 | Load Zones: LZ_AEN, LZ_CPS, LZ_HOUSTON, LZ_LCRA, LZ_NORTH, LZ_RAYBN, LZ_SOUTH, LZ_WEST |
| HU | 5 | hubs: HB_HOUSTON, HB_NORTH, HB_PAN, HB_SOUTH, HB_WEST |
| LZ_DC | 4 | DC ties: DC_E, DC_L, DC_N, DC_R |
| SH | 1 | HB_BUSAVG |
| AH | 1 | HB_HUBAVG |

The table is whole over its span: 2,450 intervals with none missing, every point in every interval (312 points by 2,450 intervals). Prices: mean 40.07 USD/MWh, median 33.98; lowest -251.00 (BATCAVE_RN, 2026-10-04 03:45 UTC), highest 2,760.29 (BIRD_ESR1, 2026-09-30 17:30 UTC); 36,047 rows below zero (4.72 percent) and 379 above 1,000. HB_HUBAVG runs from -9.37 to 438.35, mean 37.58. No autumn clock change falls in the span (it comes on 1 November 2026).

The counts in this note were computed in session 2256 with pandas from the rows of `warehouse/output/ercot_rtm_node_prices.csv` on the data machine, read past its 9 header lines as strings; no (entity, variable, ts_utc) is given twice. The bytes and files are from `warehouse/raw/ercot_rtm_spp/zips/manifest.csv` (2,451 files, all "requested").

## Checks the connector makes

- Before any request, `iso_prices.paused("ercot")` (with `--daily` before the log is opened: a paused publisher is a skip, not a failure). ERCOT is not paused. `iso_prices.paused_host()` is not asked.
- The list is tried up to four times, 15 seconds apart; a list that cannot be read stops the pull. Only files named `SPPHLZNP6905_<date>_<time>_csv` are taken, and a file already saved is not asked again.
- A listed file over 200,000 bytes is not asked. Each file is tried up to three times, 10, 20 and 30 seconds after a failure, and kept only when it answers HTTP 200 with the listed size; a file that fails three times is left for a later run. 1.5 seconds before each request.
- Ceilings: 200,000,000 bytes of downloads over every run (the manifest's requested bytes: 20,196,332 so far), and 500,000 rows a UTC day, counted as each file is saved (the rows the table keeps, about 312 a file). Before each request the run checks that one more file could not pass the day's ceiling; if it could, the run stops, says STOPPED, and writes what it saved.
- A file must hold one CSV with DeliveryDate, DeliveryHour, DeliveryInterval, SettlementPointName, SettlementPointType, SettlementPointPrice and DSTFlag, and exactly one interval. A file is not written when its hour or interval is out of range, its DSTFlag is Y (a repeated hour), its time is ambiguous or absent in Central time, a price is not a number, or a point and type, or a point beyond a zone's LZ and LZEW rows, is given twice. Such a file is logged; the others are written.
- A Load Zone printed twice in one interval (types LZ and LZEW, LZ_DC and LZ_DCEW) keeps the LZ or LZ_DC row; the EW row stays in the saved file.
- A point and interval given twice across files stops the write. No file read at all stops it.
- The write needs the data lock (`ip.write_csv`).

## License

The header: "License: public. ERCOT's terms of use (https://www.ercot.com/help/terms): raw data in public portions of the website may be used, reproduced and redistributed in compilations, charts and analyses." `license_verdicts.csv` gives ERCOT "may be public" (read 2; the same if the ERW sells anything). `license_tables.csv` names ERCOT as the one publisher, from the source registry; `docs/licenses.md` gives the ERW verdict public; `coverage.csv`: public. The table is under `catalogue_hold` in `warehouse/supabase/live_set.yaml`, not loaded; no page reads it.

## Found while writing this note

- The connector asks `/misapp/` and `/misdownload/` on `www.ercot.com`, paths ERCOT's robots file disallows (read 170, session 2002). Neither its docstring nor its header says so.
- `iso_prices.paused_host()` is not asked; `paused("ercot")` is.
- `coverage.csv` and `archive_manifest.csv` give 734,448 rows to 2026-10-22T17:00:00Z; the file holds 764,400 to 2026-10-23T17:00:00Z. The run of 23 October wrote the table, and its stores (coverage, archive, Redivis draft) are not yet recorded.
- The byte ceiling (`MAX_BYTES`, 200,000,000, "this connector's share of the session's download ceiling") counts every file requested since 5 October 2026, not a day's. At the 787,066 bytes a day saved from 13 to 23 October, the 179,803,668 bytes left last about 228 days, to about June 2027; then every run stops at the ceiling and ERCOT's list forgets each day not pulled.
- The docstring and the header say a value is written "as ERCOT prints it". The code turns it into a number first (`pd.to_numeric`), so a trailing zero is dropped: 77,313 values are written with one decimal (45.5, not 45.50).
- The docstring says "the day of the autumn clock change is left out". The code leaves out only the files whose Central time is ambiguous or flagged repeated (DSTFlag Y): the two 01:00 hours of that day, eight intervals; the day's other intervals are written.
- The connector writes no run status, so `run_status.csv` holds no row for the table, unlike the connectors that call `ip.write_status`.

## What it does not hold

- Settlement points beyond the storage resources' points, the hubs and the Load Zones: the files list about 1,142 points (5 October 2026), and the saved zips keep them all.
- The LZEW and LZ_DCEW rows.
- Intervals before 28 September 2026: ERCOT's list keeps seven days, so the storage disclosure's days (60 days behind) cannot be met from it.
- Day-ahead prices: `--pull-dam` saves NP4-190-CD's files and writes no table.
- The repeated hour of an autumn clock change.
