# ERCOT's storage resources in real time, by resource and hour (ERCOT's 60-Day SCED Disclosure Reports)

Energy Research Warehouse (ERW), method note written in session 2138 (chain 090) for a table first written on 5 October 2026 (session 120).

Tables: `ercot_sced_esr_hourly`

What the table is used for, and the monthly table and page built from it, are in `docs/methods/ercot_storage_realtime.md` (session 120 and later); this note describes the code and the rows as they stand.

## Publisher and address

Electric Reliability Council of Texas (ERCOT), "60-Day SCED Disclosure Reports", data product NP3-965-ER (report type 13052), page `https://www.ercot.com/mp/data-products/data-product-details?id=NP3-965-ER`. One zip a day for the operating day 60 days before, listed at `https://www.ercot.com/misapp/servlets/IceDocListJsonWS?reportTypeId=13052` and served at `https://www.ercot.com/misdownload/servlets/mirDownload?doclookupId=<DocID>`. Of each zip the connector reads the file `60d_ESR_Data_in_SCED-<DD-MMM-YY>.csv` (one row a storage resource and SCED run) and looks at `60d_SCED_SMNE_GEN_RES-<DD-MMM-YY>.csv`; the date in those names is the publish date, not the operating day (in the zip of 5 August 2026 both say 04-OCT-26). Source id `ercot:NP3-965-ER`. Connector: `warehouse/connectors/ercot_sced_esr.py` (session 120), in steps: `--list` reads ERCOT's list, `--pull` saves each zip under `warehouse/raw/ercot_60d_sced/zips/` with a manifest and reduces its day to `warehouse/raw/ercot_60d_sced/days/<day>.csv`, and `--write` builds the table from the reduced days only, under the data lock.

## Vintage and revision

Operating days 1 February to 20 August 2026 (Central) in the file on the data machine, 201 days, none absent between them; `warehouse/raw/ercot_60d_sced/days/missing.csv` does not exist, so no day has failed a check. Written by run `20261019T171944Z` (19 October 2026): "Operating days held: 201, 2026-02-01 to 2026-08-20 ... Days absent between them: 0."

| Operating days | Zips | Bytes | `retrieved_at` |
|---|---|---|---|
| 1 February to 5 August 2026 | 186 | 10,424,463,724 | 5 October 2026 (1,458,735 rows) |
| 6 to 14 August 2026 | 9 | 498,344,616 | 14 October 2026 (73,224 rows) |
| 15 to 20 August 2026 | 6 | 332,223,866 | 19 October 2026 (48,816 rows) |

`vintage` is the operating day plus 60 days at 00:00:00Z in every row; `retrieved_at` is when the zip was downloaded (from the manifest); `source_url` is the zip (201 addresses). The data machine runs `--pull --from 2026-02-01` and then `--write` once a week (`dm_ercot_sced_pull`, `dm_ercot_sced_write` in `warehouse/run_data_machine_tables.sh`). A day already reduced is not read again unless `--again` is given, and ERCOT's corrections and supplements (zips whose FriendlyName is not `60_Day_SCED_Disclosure`) are listed and never read, so a day is not revised once held. Each `--write` builds the file again from every reduced day.

## Shape and variables

Series, 1,580,775 rows, all `variable` net_output_mwh: one row a resource and hour. 342 entities (`ercot:<Resource Name>`), 119 scheduling entities (`x_qse`); 318 resources on 1 February and 339 on 20 August. `unit` MWh; `freq` PT1H; `ts_utc` the hour's start; `geo` US-TX; `market` ercot_rtm; `node` the resource's settlement point as `ercot_dam_esr_awards` names it (293 points; blank for 3 resources, ercot:DA_ESR2, ercot:TDWLPR_1_ESR4 and ercot:PAVLOV_ESR2, 6,431 rows). The value is the Telemetered Net Output integrated over the hour, positive when it discharges. The `x_` columns, as the header lists them: `x_net_q1_mwh` to `x_net_q4_mwh` (each 15-minute Settlement Interval), `x_discharge_mwh`, `x_charge_mwh`, `x_base_point_mwh`, `x_hsl_mw`, `x_lsl_mw`, `x_soc_start_mwh`, `x_soc_min_mwh`, `x_soc_max_mwh`, seven `x_as_<service>_mwh` (regup, regdn, rrspfr, rrsffr, rrsufr, ecrs, nspin), `x_sced_runs` and `x_qse`.

| Month | Days | Rows | Resources | Discharge MWh | Charge MWh | Net MWh |
|---|---|---|---|---|---|---|
| 2026-02 | 28 | 215,882 | 323 | 649,813.3 | 782,443.8 | -132,630.4 |
| 2026-03 | 31 | 240,516 | 324 | 767,059.5 | 922,517.1 | -155,457.6 |
| 2026-04 | 30 | 234,000 | 325 | 736,329.7 | 889,836.8 | -153,507.1 |
| 2026-05 | 31 | 241,489 | 325 | 747,515.8 | 903,527.2 | -156,011.4 |
| 2026-06 | 30 | 237,312 | 330 | 721,940.1 | 891,874.4 | -169,934.2 |
| 2026-07 | 31 | 249,240 | 335 | 847,904.9 | 1,042,275.5 | -194,370.6 |
| 2026-08 | 20 | 162,336 | 339 | 600,548.9 | 731,438.0 | -130,889.0 |

200 days hold 24 distinct hours and one, 8 March 2026 (the spring clock change), holds 23. A day holds 7,452 to 8,136 rows. `x_sced_runs` is 7 to 19 a row, 12.1 on average. The highest `x_hsl_mw` is 240 MW.

## Reading the source

- `--list` and an online `--pull` ask `iso_prices.paused("ercot")` before the list is requested and stop when ERCOT is paused; no zip is asked for before the list, so no request reaches ERCOT while it is paused. `--pull --offline` and `--write` make no request.
- The list is tried four times, 15 seconds apart, timeout 120 seconds. A zip is asked for only when no copy is on the disk; it is tried four times (waits of 15, 30, 45 and 60 seconds), timeout 600 seconds, and kept only when it answers HTTP 200 with exactly the bytes the list states. Requests are 2 seconds apart. Two regular zips for one operating day stop the run.
- Download ceiling: 12,000,000,000 bytes (`MAX_BYTES`), counted over every zip this connector's manifest records as requested. The run stops before a request that would pass it, and before it starts when the days wanted need more than is left; on the data machine's schedule that stop is a skip. The manifest records 11,255,032,206 bytes, so 744,967,794 are left, about 13 zips of the 53 to 60 MB the saved ones measure.
- A day is reduced only when the zip holds exactly one storage file with every column the reducer reads, every row's Resource Type is ESR, every SCED time stamp reads as MM/DD/YYYY HH:MM:SS on the operating day, no row is in a repeated hour (the autumn clock change: such a day is left out), no stamp is ambiguous or absent in Central time, no resource and stamp repeat, no two SCED runs are more than an hour apart, and the pieces of the runs add up to the time they cover. A day that fails is written to `missing.csv` with its reason and has no rows.
- Each run's MW is held until the next SCED run of the day, whichever resources it holds (the last run until local midnight), and never across a run the resource is not in. A run is cut at each quarter-hour it crosses. A blank ancillary service award is 0 MW for that run. An hour reached only by the tail of the hour before, with no run of its own, has no row.
- Row ceiling: 9,000,000 (`MAX_ROWS`), counted on this table's rows; at the ceiling `--write` stops and writes nothing. The file holds 1,580,775.

## License

Public. `license_verdicts.csv` records ERCOT, read 2 (`https://www.ercot.com/help/terms`, 12 October 2026 in `license_reads.csv`): "may be public", for public and for commercial use. The sentence: "raw data provided in public portions of this website may be used, reproduced, and redistributed in compilations, charts, and analyses without maintaining such notices." `sources.csv` flags `ercot:NP3-965-ER` public; `license_tables.csv` lists the table under ERCOT.

## Cross-checks (session 2138)

- The counts above were computed from the rows, read past the header lines, and agree with the manifest of the 201 saved zips. No (entity, variable, ts_utc) is given twice.
- In every row the four quarters add up to the value within 0.000002 MWh, and discharge less charge equals the value within 0.000001 MWh, the rounding of the values to six decimals.
- Against `ercot_storage_rt_monthly` (derived from the reduced days and the day-ahead awards, over the days both hold): over the same days, the table's discharge, charge and net differ from that table's `rt_discharge_mwh`, `rt_charge_mwh` and `rt_net_mwh` by at most 0.001 MWh in all seven months, the rounding of the two. February to July use every day of the month; August uses 1 to 15 August, the 15 days the monthly table holds (`days_held`; its header: "Operating days: 196 matched, 2026-02-01 to 2026-08-15"). The table's resource-hours, with the monthly table's day-ahead-only hours added (23 in February, 0 after), equal its `resource_hours` in every month.
- In the zip of 5 August 2026 the storage file holds 98,310 rows of 339 resources and 198 columns, as the docstring says; 160 of the column names hold "Curve", "SCED1", "SCED2" or "TPO", the offer curves the docstring says are not read.

What the docstring says and the code or the files do not:

- The docstring says a zip holds "among eleven files" the two read. All 201 saved zips hold ten files.
- The docstring lists `metered_mwh`, the settlement metered energy of the hour, as part of an hour's row "when the SMNE file holds the resource for all four (written only then)". The table has no such column (`to_rows` does not write it), and in the reduced days it is blank in all 1,580,775 resource-hours: the metered file of the zip of 5 August holds 1,618 resource codes and none of them is a storage resource of that day's storage file. The header says so: "ERCOT's metered file in the same zip does not hold the storage resources."
- The docstring describes the first pull, "1 February to 5 August 2026 (186 days, 10.4 GB)". The table now holds 201 days to 20 August and the manifest 11.26 GB; the header gives the current figures.
- The docstring says the ceilings of 12 GB and 9,000,000 rows are "in total (with the node prices pulled beside it)". The code counts only this connector's downloads and this table's rows against them.

## What it does not hold

- Operating days before 1 February 2026 (the pull took the most recent months that fit its ceiling) and after 20 August 2026, until the weekly pull reads them.
- A day with a repeated hour: none falls in the window held; under the code, 1 November 2026 would be left out with its reason.
- The settlement meter, any price, the offer curves, and the Load Resource and generator files of the same zip.
