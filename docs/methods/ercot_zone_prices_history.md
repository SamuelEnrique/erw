# ERCOT's load zone settlement point prices from 2015: day-ahead an hour for the eight load zones, real time a 15-minute interval for the four competitive zones

Energy Research Warehouse (ERW), method note written in session 2242 (chain 101) for a table first written on 7 October 2026 (session 140, an approved pull, commit `472bc483`, `archive/sessions/SESSION_140_REPORT.md`, "(a) ERCOT's load zones"); its daily refresh is session 149's (`archive/sessions/SESSION_149_REPORT.md`). The hubs of the same workbooks are `ercot_all_hub_prices_history`.

Tables: `ercot_zone_prices_history`

## Publisher and address

Electric Reliability Council of Texas (ERCOT), two reports of yearly workbooks:

- NP4-180-ER, "Historical DAM Load Zone and Hub Prices", `https://www.ercot.com/mp/data-products/data-product-details?id=NP4-180-ER`, list `https://www.ercot.com/misapp/servlets/IceDocListJsonWS?reportTypeId=13060`;
- NP6-785-ER, "Historical RTM Load Zone and Hub Prices", `https://www.ercot.com/mp/data-products/data-product-details?id=NP6-785-ER`, list `https://www.ercot.com/misapp/servlets/IceDocListJsonWS?reportTypeId=13061`.

Each workbook is `https://www.ercot.com/misdownload/servlets/mirDownload?doclookupId=<DocID>`, one a report and year; every row's `source_url` names its own. Source ids `ercot:NP4-180-ER` and `ercot:NP6-785-ER`. Saved workbooks under `warehouse/raw/ercot_zone_prices/` (`manifest.csv`: address, bytes, sha256, publication and retrieval of each; `requests.csv`: every request). Every request goes to `www.ercot.com` under `/misapp/` and `/misdownload/`, paths ERCOT's robots file disallows (read 170 of `warehouse/metadata/license_reads.csv`, session 2002, 23 October 2026: "disallows /misapp, /misdownload, /meetings, /content/... and others"). The connector sends its own User-Agent naming the ERW and pauses 5 seconds between requests.

Connector: `warehouse/connectors/ercot_zone_prices.py` (session 140): `--pull` (the two lists, then each workbook not yet held), `--write` (the table from the saved workbooks, no request; with `--years`, those years only), `--refresh` (both, for the years still growing), `--check` (the workbooks' hub rows against the hub history), `--out-dir`. The owner's approval (7 October 2026): USD 0 and a ceiling of 3,000,000 rows; a row counts once (session 149), and a request that could pass the ceiling is refused before it is made. Kept: day-ahead for LZ_HOUSTON, LZ_NORTH, LZ_SOUTH, LZ_WEST, LZ_AEN, LZ_CPS, LZ_LCRA and LZ_RAYBN; real time for the first four only. A zone's second real-time row (Settlement Point Type LZEW), the DC ties and the hubs stay in the saved workbooks. A Repeated Hour Flag Y outside the autumn's repeated hour, a time the clock change makes absent, or a zone and interval with two prices stops the year.

Schedule: the data machine's daily run, `warehouse/run_data_machine.sh`, step `dm_ercot_zone_prices` (`ercot_zone_prices.py --refresh`), registered with the Windows Task Scheduler by `scripts/register_data_machine_daily.ps1` (session 185, "ERW data machine daily"); when rows were added, the validator, the coverage row, the archive and the Redivis draft follow. Not on the GitHub runner: `warehouse/refresh_supply.sh` says "ERCOT's load zones (ercot_zone_prices_history) are NOT refreshed here", and no step of `run_daily.sh`, `run_data_machine_tables.sh`, `run_monthly.sh` or `.github/workflows/` runs it. `scheduled.py` names the table among the data machine's histories (`merchant_hubs` reads it). Run logs on this machine: 13, daily from 20261011T171639Z to 20261023T174101Z. `run_status.csv` holds no row of it; `runs/status/ercot_zone_prices.json` records run 20261023T174101Z, DAM ok and RTM ok. `archive_manifest.csv`: 2,481,384 rows as of run 20261018T173754Z-local. Not loaded into the live set (`live_set.yaml`, `catalogue_hold`, session 140: "The page reads the site's own files, built from them"). Readers: `warehouse/derived/datacenter_page.py`, `capture_price.py`, `node_basis.py` and `price_years.py`; `site/lib/siting.ts`.

## Vintage and revision

`vintage` is the time ERCOT published the workbook a row came from: one workbook a report and year. Each year from 2015 to 2025 comes from the copy ERCOT published after the year ended (on 1 January of the next year; 2025's real-time copy at 2026-01-01T19:25:58Z); 2026 comes from the copies published on 18 October 2026 (13:02:32Z day-ahead, 13:08:03Z real time). `retrieved_at`: 2,314,368 rows on 2026-10-07 and the 167,016 rows of 2026 on 2026-10-18.

The header is run `20261023T174101Z` ("--write, from the workbooks its --pull saved"); its log: the two lists asked ("ERCOT lists 17 documents" each), 2026's copies "held ... not asked again", "this run made 2 requests", and "This run wrote 167016 rows: 0 new, 167016 replacing earlier rows". ERCOT posts the current year's workbook again each Sunday (the docstring); a new copy replaces the year's rows and adds the intervals since. A finished year's copy is never asked for again.

## Shape and variables

Series, 2,481,384 rows; partition columns `market` and `year` (ERCOT's operating year, America/Chicago), as `ercot_all_hub_prices_history` has them. `entity` `ercot:<zone>`, `node` the zone, `unit` USD/MWh, `geo` US-TX.

| market | variable | freq | Zones | Rows a zone | First interval | Last interval |
|---|---|---|---|---|---|---|
| ercot_dam | spp_dam | PT1H | LZ_AEN, LZ_CPS, LZ_HOUSTON, LZ_LCRA, LZ_NORTH, LZ_RAYBN, LZ_SOUTH, LZ_WEST | 103,391 | 2015-01-01T06:00:00Z | 2026-10-18T04:00:00Z |
| ercot_rtm | spp_rtm | PT15M | LZ_HOUSTON, LZ_NORTH, LZ_SOUTH, LZ_WEST | 413,564 | 2015-01-01T06:00:00Z | 2026-10-18T04:45:00Z |

- Rows a year: day-ahead 70,080 (70,272 in 2016, 2020 and 2024), 55,672 in 2026; real time 140,160 (140,544 in the leap years), 111,344 in 2026. The last interval is 17 October 2026, 23:45 Central daylight time.
- Lowest -147.45 (LZ_HOUSTON, real time, 2023-01-24T20:45:00Z); highest 9,349.19 (LZ_SOUTH, real time, 2021-02-15T07:45:00Z, Winter Storm Uri). Every value to two decimals or fewer.
- Negative prices, real time: LZ_WEST 25,105 intervals, LZ_SOUTH 7,155, LZ_NORTH 6,314, LZ_HOUSTON 4,617; day-ahead: LZ_WEST 1,547 hours, LZ_SOUTH 206, LZ_NORTH 83, LZ_RAYBN 78, LZ_CPS 51, LZ_LCRA 43, LZ_AEN 41, LZ_HOUSTON 4.

Means over ERCOT's days from 1 October 2025 to 30 September 2026 (8,760 hours; 35,040 intervals), USD/MWh:

| Zone | Day-ahead | Real time |
|---|---|---|
| LZ_NORTH | 35.32 | 33.73 |
| LZ_HOUSTON | 35.48 | 33.43 |
| LZ_SOUTH | 34.44 | 33.75 |
| LZ_WEST | 37.38 | 35.27 |
| LZ_AEN | 38.78 | |
| LZ_CPS | 38.86 | |
| LZ_LCRA | 38.75 | |
| LZ_RAYBN | 35.60 | |

## Placing values in time, and what is filled

ERCOT gives the delivery date, the hour ending (1 to 24, Central time) and, in real time, the interval of the hour (1 to 4). The interval's start is the date plus (hour ending - 1) hours plus (interval - 1) x 15 minutes, Central time, and `ts_utc` is that instant in UTC. On the day the clocks go back, hour ending 2 is in the workbook twice (Repeated Hour Flag N, then Y) and becomes two distinct UTC hours; on the day they go forward ERCOT skips hour ending 3. A blank or non-numeric price is not written; nothing is filled.

## License

Header: "License: public. ERCOT's terms of use, item 5 (https://www.ercot.com/help/terms, read 6 October 2026): "raw data provided in public portions of this website may be used, reproduced, and redistributed in compilations, charts, and analyses without maintaining such notices."" `license_verdicts.csv`, ERCOT (read 2): "The publicly available contents of this website may be used, reproduced, and redistributed, provided that the contents are not modified and that you maintain all copyright and other notices contained in the contents, including this Agreement. Notwithstanding the foregoing, raw data provided in public portions of this website may be used, reproduced, and redistributed in compilations, charts, and analyses without maintaining such notices.", verdict "may be public", note "Item 6 forbids use that harms the site's performance; it names no automated access as such." `docs/licenses.md`, the table's row: ERCOT, "may be public", flag public, "agrees", ERW verdict public. No row in `license_status.csv`.

## Checks (session 2242)

The figures in this note were computed from the rows of `warehouse/output/ercot_zone_prices_history.csv`, read past its 19 header lines (scripts `runs/c101/s2242/check_ercot_zones.py` and `check_ercot_hubs.py`, outputs beside them).

- 2,481,384 rows, 2015-01-01T06:00:00Z to 2026-10-18T04:45:00Z, as the header states; the rows by market and zone are the header's, each one; no (entity, variable, ts_utc) twice; no blank cell; `year` is the Central year of `ts_utc` in every row; every day-ahead `ts_utc` on the hour and every real-time one on a quarter hour.
- "Missing stays missing: every zone has every interval of every year it is in": it holds. Each of the 12 series has every interval from its first to its last (103,391 hours; 413,564 quarter hours), the repeated autumn hour counted twice.
- Against `ercot_rtm_node_prices` (ERCOT's 15-minute settlement point prices, NP6-905-CD, the LZ rows of the four zones): the 7,684 intervals both hold, 2026-09-28T04:45:00Z to 2026-10-18T04:45:00Z, are equal to the cent.

## Where the description and the data disagree

1. **ERCOT's robots file.** The connector asks `/misapp/` and `/misdownload/` on `www.ercot.com`, paths ERCOT's robots file disallows (read 23 October 2026, session 2002). The docstring quotes the terms' item 5 and their sentence on the site's performance ("Hence one request at a time and a pause") and says nothing of the robots file; the header neither.
2. **Another note says the refresh never runs.** `docs/methods/datacenter_pays_algorithm.md` (session 190): "`ercot_zone_prices_history` is refreshed only by the data machine's run, which is registered nowhere" and "ERCOT's load zones stop on 3 October 2026". The table now runs to the interval starting 2026-10-18T04:45:00Z, from ERCOT's copies of 18 October; this machine's logs show the refresh every day from 11 to 23 October, and `scripts/register_data_machine_daily.ps1` registers the run.

## The session report against the table

`SESSION_140_REPORT.md` figures that are the table's hold. Row count then: 2,473,320 (now 2,481,384, after the refreshes). "North load zone, real time, October 2025 to September 2026: USD 33.73 per MWh ... 1.22 above the North hub": 33.7269 in the table, against 32.5042 for HB_NORTH in `ercot_all_hub_prices_history` (1.2227). "West load zone: 35.27, which is 4.61 above the West hub's 30.66": 35.2692 and 30.6607 (4.6085); "the hub understated a West Texas load's price by 15 percent": 4.6085 is 15.0 percent of the hub's price. "Day-ahead in the Austin, San Antonio and LCRA zones: 38.75 to 38.86": 38.7771, 38.8617 and 38.7451. "USD 29.55 million for 100 MW" follows from the rounded 33.73 (100 MW x 8,760 hours x 33.73); from the table's 33.7269 it is USD 29.54 million.

## What it does not hold

- Real time for LZ_AEN, LZ_CPS, LZ_LCRA and LZ_RAYBN (in the saved workbooks; it would pass the ceiling); the LZEW rows; the DC ties; the hubs (`ercot_all_hub_prices_history`); days before 2015; ERCOT's resource nodes (`ercot_rtm_node_prices`, the last weeks only); the price's components.
