# Session 2435 report: Egypt's capacity, peak load and generation by fiscal year (EEHC's annual reports), internal

24 October 2026, from 11:14 UTC to 11:27 UTC, on lab-desktop (the data machine), chain 117, unattended. Precheck passed (`runs/c117/pre2435.out`). Model spend USD 0. Pulls: 12 requests of 15 (4 by the probe, 7 by the fetch, 1 report again by the trial; the write read them offline).

## Read these first

- **The ERW held no EEHC source** (`sources.csv` and the connectors on main searched for EEHC and Egypt).
- **The hosts:**
  - www.eehc.gov.eg has no robots file (HTTP 404, read 707);
  - www.moee.gov.eg, the ministry's host of the earlier reports, closes two pages only (read 710);
  - no rule names an AI agent.
- **A new table, `eehc_egypt_electricity_annual`** (series, 105 rows, `power`). It is read from the summary table "Electricity in <year>" of four annual reports, each giving its fiscal year and the one before: fiscal years 2014/15 to 2017/18, 2019/20 and 2020/21, and 2022/23 and 2023/24. It holds:
  - installed capacity (MW): total, hydro, thermal, the 2015/16 fast track plan, renewables, and the private BOOT plants;
  - the peak load (MW);
  - generation (MWh): total, hydro, thermal, renewables, IPP purchases, BOOT, isolated plants, and industrial surplus.
  - `ts_utc` is the fiscal year's first day (1 July), and `x_fiscal_year` keeps EEHC's label.
  - Written, validated (0 errors, 0 warnings), archived, and held from the Redivis storage and the live set.
- **Internal.** EEHC's site carries "All Rights Reserved ©2022" and grants no reuse (read 708).
- **Not in the table:**
  - **Fiscal years 2018/19 and 2021/22.** Their reports were not found. EEHC's 2022/23 and 2024/25 reports (27 and 30 MB) are scanned images without text, so they were fetched but not read.
  - **The report data:** the 2015/16 report prints the peak load's unit as GWh beside megawatt figures (28,015 and 29,200); they are written as MW.
  - **A file name:** the ministry's `REP2021-2022en.pdf` holds the 2020/2021 report. Its fiscal years are read from the table itself.
- **The 2024/2025 report's link on EEHC's page doubles its path** and answered 404 (request 6). Asked at the path given once, it answered (request 7).

## Cross-checks

- Total generation by fiscal year over the mean of `owid_ember_electricity_annual`'s demand for Egypt in its two calendar years: 0.993 to 1.010.
- Within the table, the kinds sum to the total within 0.1 TWh (2023/24: 229.37 TWh of parts against 229.28 TWh).
- Peak load: 28,015 MW in 2014/15, 36,800 MW in 2023/24. Installed capacity: 35,220 MW, then 59,694 MW.

## Requests (12 of 15)

| n | What | Outcome |
|---|---|---|
| 1 | www.eehc.gov.eg/robots.txt | 404 |
| 2 | the 2022/2023 report's page | 200: "All Rights Reserved ©2022"; links the reports |
| 3 | the 2024/2025 report's page | 200: its PDF link |
| 4 | www.moee.gov.eg/robots.txt | 200: two pages closed |
| 5 | the 2023/2024 report (fetch) | 200, 12.4 MB, text |
| 6 | the 2024/2025 report at its link (fetch) | 404 (the link doubles its path) |
| 7 | the 2024/2025 report at the path given once (fetch) | 200, 30 MB, scanned |
| 8 | the 2020/2021 report, `REP2021-2022en.pdf` (fetch) | 200, 4.4 MB, text |
| 9 | the 2022/2023 report (fetch) | 200, 27 MB, scanned |
| 10 | the 2017/2018 report (fetch) | 200, 7.2 MB, text |
| 11 | the 2015/2016 report (fetch) | 200, 12.6 MB, text |
| 12 | the 2017/2018 report again (the trial) | 200, 7.2 MB |

Reads recorded: 707 to 710 (on this branch).

**Why request 12.** Each fetch script opened the same raw folder, so its manifest kept only the last file. Two rows were rebuilt from the records the fetches printed (time of retrieval and last modified) and from each file's own size and hash. The 2017/2018 record's last-modified line was cut off in the output, so the trial asked for that report again.

## Decisions made without you

- **`internal`** under EEHC's notice.
- **The fiscal year on its first day,** its label kept, rather than split across calendar years.
- **The 2015/2016 peak load written as MW,** its printed unit being a slip the other reports do not repeat.
- **Two manifest rows rebuilt** from the fetches' own records, not fetched again.

## For Samuel's ruling

- **EEHC's consent,** if Egypt's figures are wanted public.

## Files

- New: `warehouse/connectors/eehc_egypt_electricity.py`, `tests/test_session2435.py`, this report.
- Changed:
  - `warehouse/metadata/build_coverage.py`, `warehouse/redivis/release_v1.py`, `warehouse/supabase/live_set.yaml`;
  - `docs/coverage.md`, `warehouse/metadata/coverage.csv`, `warehouse/metadata/sources.csv`, `warehouse/metadata/archive_manifest.csv`;
  - the license record (reads 707 to 710, `license_tables.csv`, `docs/licenses.md`).
- On the data machine only: `runs/c117/s2435/`, `warehouse/raw/eehc_electricity/`, `warehouse/output/eehc_egypt_electricity_annual.csv`.
