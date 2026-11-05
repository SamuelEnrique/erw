# Nova Scotia's in-province load an hour, 2022 to August 2026 (NS Power's OASIS reports)

Energy Research Warehouse (ERW), method note written in session 2717 (chain 136) for a table first written on 25 October 2026 (session 2708).

Tables: `nspower_ns_load_hourly`

## Publisher and address

Nova Scotia Power (NS Power), its OASIS site, Monthly Reports, Hourly Total Net Nova Scotia Load (`https://www.nspower.ca/oasis/monthly-reports/hourly-total-net-nova-scotia-load`). The page lists a CSV and an HTM file a year from 2012; the table reads the CSV files for 2022 to 2026, under `https://www.nspower.ca/docs/default-source/monthly-reports/`. No key. Source id `nspower:oasis_hourly_total_net_ns_load`. Connector: `warehouse/connectors/nspower_ns_load.py` (session 2708), whose raw store is `warehouse/raw/nspower/`. www.nspower.ca's robots file closes only `/WindFarmMap/` (read 1425); nspower.ca redirects to it (read 1428).

## Vintage and revision

Written by run `20261025T182018Z` (the write under the lock, offline), which read the files retrieved from 2026-10-25T16:53:15Z (2025) to 16:57:03Z (2026). The page: "These files are updated in the following calendar month". The 2026 file held hours to the end of August when read.

## Shape and variables

Series, 40,308 rows, one entity, `nspower:ns:load`, from 2022-01-01T04:00:00Z to 2026-09-01T02:00:00Z (UTC). `variable` load; `unit` MW, the page's "All Load Values are in MW, totalized over 1 hour"; `ts_utc` the hour's start; `freq` PT1H; `geo` CA-NS; `node` the files' title, "Nova Scotia Power in-province load".

**Figures:**
- 11.32 TWh in 2022, 11.25 in 2023 and 11.41 in 2024, by UTC year.
- The highest hour, 2,467.3 MW, began at 2023-02-04T15:00:00Z.
- The lowest, 335.87 MW, began at 2022-09-24T11:00:00Z, the morning post-tropical storm Fiona reached the province. The fifteen hours under 500 MW are all on that day in Atlantic time, from 05:00 UTC on 24 September to 02:00 UTC on the 25th.

## Reading the source

- The run stops at once, asking nothing, while `nspower` or www.nspower.ca is paused.
- Five requests a run, saved and reused unless `--fresh`; `--offline` asks nothing.
- **The clock:** Atlantic local time with daylight saving, by hour ending. Each day's 24th hour carries its own date at 00:00. Each hour is placed from its day's local midnight in UTC (America/Halifax).
  - The spring day has 23 hours (no hour ending 03:00).
  - **The autumn day's 02:00 is not placed.** The 2025 file lists it once for the day's two such hours. The 2022 to 2024 files list it twice with the same value (882.60 MW twice in 2022). The files do not say which hour a single row is, or whether a second is a copy. So that day's hours from 04:00 and 05:00 UTC have no row.
- **The files differ year to year:**
  - The HOUR column skips the spring hour's number in 2025 and not in 2022, so it is checked only to rise.
  - The 2023 file writes its times as "1/1/2023 1:00", the others as "2025-01-01 01:00".
- **Hours without a row, counted in the header:**
  - 578 hours, 1 to 25 April 2025, read "Data Lost Due To Cybersecurity Incident" (the page's note on Emera's incident of April 2025).
  - One blank hour, 8 March 2025.
  - The 2026 file's last 1,296 hours are listed with no value and counted as not yet posted.
  - Seven autumn hours are not placed.
- Only days ended before a file's retrieval are kept. Nothing is filled.
- **The run stops for:**
  - a title or header not in this form;
  - a time not on the hour or outside the file's year;
  - an HOUR that does not rise;
  - an hour given twice (but the autumn 02:00);
  - a day without the hours its date has;
  - a load not a positive number.

## License

Internal. NS Power's Terms of Service (`https://www.nspower.ca/legal`), 3.1: "You will not use our Intellectual Property Rights (or anything that is confusingly similar to our Intellectual Property Rights) for any purpose." The verdict is on record (needs written permission, read 1427). Held from the live set and from the public release package.

## Cross-check

Against `statcan_electricity_trade_monthly`'s Nova Scotia, available for use (generation plus receipts less deliveries), twelve months summed:

| Year | There (TWh) | Here (TWh) | Gap |
|---|---|---|---|
| 2022 | 10.96 | 11.32 | 3.3 per cent |
| 2023 | 11.08 | 11.25 | 1.5 per cent |
| 2024 | 11.26 | 11.41 | 1.4 per cent |

The load here is by UTC year, Statistics Canada's by local month.
