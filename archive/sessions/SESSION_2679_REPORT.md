# Session 2679 report: British Columbia's balancing authority load an hour, January 2024 to September 2026 (BC Hydro), internal, a second source of the session's own choosing

25 October 2026, about 11:53 to 12:01 UTC, on lab-desktop (the data machine), chain 134, unattended. Precheck passed (`runs/c134/pre2679.out`). Model spend USD 0. Pulls: 9 requests of 20:
- 4 by the probe;
- 3 by the session's fetch script;
- 2 by the connector's trials, which asked again the 2024 and 2025 workbooks the fetch script had saved (the reason is below).

## Read these first

- **Why this source:**
  - EIA-930 holds BC Hydro's balancing authority (BCHA) only as a partner in US interchange, and the ERW held no BC load.
  - Hydro-Quebec was tried first. donnees.hydroquebec.com's robots file closes `/api/` and every download to all but Googlebot (read 1395), as earlier chains found, so it was not asked again.
- **The host:** www.bchydro.com's robots file closes extranet, media library, account and template paths, not the public documents, and names no AI agent (read 1396).
- **The way in:** the historical transmission data page (read 1397) lists the Hourly Control Area Load workbooks from 2007 to 2026. The table reads 2024, 2025 and the year in progress, 2026.
- **The terms** (read 1398, the Legal page): "All editorial content and graphics on this site are protected by Canadian copyright and international treaties and may not be copied without the express permission of British Columbia Hydro and Power Authority (BC Hydro), which reserves all rights".
  - **Verdict: needs written permission.** The table is **internal**.
- **A new table, `bchydro_ba_load_hourly`** (series, 24,095 rows, 1 entity, `power`): `bchydro:bcha:load`, variable `load`, MW, hourly, `geo` CA-BC.
  - It runs from 08:00 UTC on 1 January 2024 to 06:00 UTC on 1 October 2026, the end of 30 September in Pacific time.
  - By UTC year: 66.4 TWh and a peak of 12,334 MW in 2024; 67.3 TWh and 11,359 MW in 2025; 49.6 TWh to September 2026.
- **The time base:** the reports are in Pacific local time with daylight saving, by hour ending.
  - The spring day has 23 hours (no HE 2). The autumn day has 25, its repeated hour marked "2*"; the 2025 sheet lists "2*" before HE 2, the 2024 sheet after.
  - Each day's hours are put in time order, "2*" after HE 2, and counted from the day's local midnight in UTC (America/Vancouver).
  - A day whose hours are not its date's stops the run. All five change days in the files (two in 2024, two in 2025, the spring day of 2026) check.
  - I first took the 24-hour days' total of 8,760 for a fixed offset; the "2*" label showed otherwise before anything was written.
- **Kept:** only whole days that ended before retrieval. A load not positive, a date of another year, a day given twice or a gap stops the run.
- **Its record:** written by run `20261025T115752Z` under the data lock and validated (exit 0). It is in coverage, archived (`20261025T115757Z-local`), held from the live set, and not in the release package (internal). The write's and the finish's results were read before the commit.
- **Why two workbooks were asked twice:** the fetch script was run once a workbook with the same run name, and each run rewrote that folder's manifest. Only the last workbook stayed findable, so the connector asked the other two again. Session 2664's repeats likely had the same cause. File 135 gets the lesson: one run name a fetch, or let the connector's trial make the fetches.

## Cross-checks

Against `statcan_electricity_generation_monthly`'s British Columbia (all types), in TWh:
- 2024: generation 59.0 against the load's 66.4;
- 2025: generation 64.5 against 67.3.

The load is above generation by BC's net imports, which were large in 2024.

## Requests (9 of 20)

| n | What | Outcome |
|---|---|---|
| 1 | donnees.hydroquebec.com's robots file | 200 |
| 2 to 4 | www.bchydro.com's robots file, the data page, the Legal page | 200 |
| 5 to 7 | the 2025, 2024 and 2026 workbooks (the fetch script) | 200 |
| 8, 9 | the 2024 and 2025 workbooks again (the trials) | 200 |

Reads recorded: 1395 to 1398.

## Decisions made without you

- **BC Hydro as the second own choice; internal** under its Legal page.
- **2024 to 2026 only;** the workbooks back to 2007 are left for a later chain.

## For Samuel's ruling

- None new. BC Hydro grants permission case by case; a request would make the table public.

## Files

- New: `warehouse/connectors/bchydro_ba_load.py`, `tests/test_session2679.py`, this report.
- Changed: the registration; the metadata files; the license record (reads 1395 to 1398, BC Hydro's verdict) and `docs/licenses.md`.
- On the data machine only: `runs/c134/s2679/`, `runs/license_reads/s2679/`, `warehouse/raw/bchydro/`, `warehouse/output/bchydro_ba_load_hourly.csv`.
