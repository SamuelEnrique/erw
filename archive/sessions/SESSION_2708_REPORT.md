# Session 2708 report: Nova Scotia's in-province load an hour, 2022 to August 2026 (NS Power's OASIS reports), internal; queue file 137 written first

25 October 2026, about 16:48 to 17:00 UTC, with the write at 18:20 UTC: this machine's daily task held the data lock from 17:00 to about 18:20. On lab-desktop (the data machine), chain 136, unattended. Precheck passed first (`runs/c136/pre2708.out`). Model spend USD 0. Pulls: 10 requests of 15 (5 by the probe, 1 fetch of the 2025 file under a run name of its own, 4 by the trials); one web search.

## Read these first

- **Queue file 137 first:**
  - `queue/next/137-day-7-december-data-pei-yukon-northwest-territories-nunavut.md` (sessions 2722 to 2735) was written from file 136 by `runs/c136/write_137.py`, made by exact replacements from chain 135's writer (`runs/c136/make_write_137.py`). It keeps the rules word for word.
  - 137 was the next free number, and 2722 to 2735 were free on main and on every branch. The code machine's periodicals chain holds 2700 to 2707.
  - Its sources: Prince Edward Island, Yukon, the Northwest Territories and Nunavut, Canada's four smallest grids. None is in the record or the queue.
  - Pushed to main alone as `5007d10f`; snapshots `c136-q137-before` and `c136-q137-after` show **0 differences**.
- **Chain 136's worktree:** `erw-c136` on `wip/2708-2721-data`, from main at `4ceb3b46`.
- **NS Power's first page was gone, and its terms keep the table internal:**
  - www.nspower.ca's robots file closes only `/WindFarmMap/` and names no Claude agent (read 1425). nspower.ca redirects to it (read 1428).
  - Its Today's Energy Stats page answers 404 (read 1426). A search found its OASIS monthly reports.
  - **Its Terms of Service** (read 1427), 3.1: the site's creative works are its exclusive property, and "You will not use our Intellectual Property Rights ... for any purpose". The table is **internal**; session 2713 records the verdict, needs written permission.
- **A new table, `nspower_ns_load_hourly`** (series, 40,308 rows, `power`, internal):
  - Entity `nspower:ns:load`, variable `load`, MW totalized over the hour, the hour's start in UTC, geo CA-NS.
  - From the OASIS page Hourly Total Net Nova Scotia Load (read 1429), one CSV a year for 2022 to 2026. The 2026 file is posted to August.
  - Figures: 11.32 TWh in 2022, 11.25 in 2023, 11.41 in 2024; peaks 2,216, 2,467 and 2,088 MW.
- **How the hours are placed:** the files give Atlantic local time with daylight saving, by hour ending; each day's 24th hour carries its own date at 00:00. Each hour is placed from its day's local midnight in UTC (America/Halifax), BC Hydro's method (session 2679).
  - **The spring day** has 23 hours (no hour ending 03:00).
  - **The autumn day's 02:00 is never placed.** The 2025 file lists it once for two hours. The 2022 to 2024 files list it twice with the same value (882.60 MW twice in 2022), which reads as a copy. So that day's hours from 04:00 and 05:00 UTC have no row: 2 a year, 1 in 2025.
- **The files differ year to year,** each difference read, not forced:
  - The HOUR column skips the spring hour's number in 2025 and does not in 2022, so it is checked only to rise.
  - The 2023 file writes its times "1/1/2023 1:00".
- **Gaps, counted in the header:**
  - 578 hours of 1 to 25 April 2025 read "Data Lost Due To Cybersecurity Incident", as the page warns.
  - One blank hour, 8 March 2025.
  - The 2026 file's last 1,296 hours (September and October) are listed without values. They are counted as not yet posted.
  - Nothing is filled.
- **Its record:** written by run `20261025T182018Z` under the data lock and validated (exit 0). It is in coverage, archived (`20261025T182024Z-local`), held from the live set, and kept out of the release package (internal). The patch applied cleanly; the write's and the finish's results were read before each commit.

## Cross-check

Against `statcan_electricity_trade_monthly`'s Nova Scotia, available for use (generation plus receipts less deliveries), with the load summed by UTC year:

| Year | Available for use (TWh) | Load here (TWh) | Gap |
|---|---|---|---|
| 2022 | 10.96 | 11.32 | 3.3 per cent |
| 2023 | 11.08 | 11.25 | 1.5 per cent |
| 2024 | 11.26 | 11.41 | 1.3 per cent |

Generation alone was 8.99, 8.28 and 8.83 TWh in `statcan_electricity_generation_monthly`, the rest imported over the Maritime Link and from New Brunswick.

## Requests (10 of 15)

| n | What | Outcome |
|---|---|---|
| 1 | www.nspower.ca's robots file (its own request) | 200 |
| 2 | Today's Energy Stats | 404 |
| 3 | the Terms of Service | 200 |
| 4 | nspower.ca's robots file | 200 (sent to www) |
| 5 | the OASIS load page | 200 |
| 6 | the 2025 file (the fetch) | 200 |
| 7 to 10 | the 2022, 2023, 2024 and 2026 files (the trials) | 200 |

Reads recorded: 1425 to 1429. Test 205's bound is raised by 40 for this chain's reads, from 1425.

## Decisions made without you

- **Internal, under NS Power's terms.**
- **2022 to 2026 only:** the 2019 and 2021 files are Excel and the years before use other names; they were left to keep the ceiling and a run of years.
- **The autumn 02:00 not placed,** whether given once or twice.
- **The trailing blank hours of the year in progress** counted as not yet posted, not as blank.
- **Writes after the daily task's lock:** the four tables of sessions 2708, 2714, 2715 and 2720 were written in turn from 18:20 UTC.

## For Samuel's ruling

- **NS Power's permission** would make `nspower_ns_load_hourly` public.

## Files

- New: `warehouse/connectors/nspower_ns_load.py`, `tests/test_session2708.py`, this report.
- Changed: the registration, test 205's bound, the metadata files, and the license record (reads 1425 to 1429) with `docs/licenses.md`.
- On the data machine only: `runs/c136/s2708/`, `runs/c136/make_write_137.py`, `runs/c136/write_137.py`, `runs/c136/raise205.py`, `runs/license_reads/s2708/`, `warehouse/raw/nspower/`, `warehouse/output/nspower_ns_load_hourly.csv`.
