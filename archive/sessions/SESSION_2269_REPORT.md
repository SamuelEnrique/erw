# Session 2269 report: Taiwan's generation, not taken (Taipower's daily file has no header, and its definitions are on a host that fails at robots)

24 October 2026, from 04:03 UTC, on lab-desktop (the data machine), chain 103, unattended. Model spend USD 0. Pulls: 3 requests of 15.

## Read these first

- **No table this session.**
- **Taipower's terms allow the reuse.** Its website open data declaration (read 442), in Chinese: everything published on the site is offered to the public free of charge, non-exclusively and sublicensably. Users may reproduce, adapt, edit, publicly transmit or otherwise use it, to develop products or services, without the company's written or other authorisation, on the condition that the source is cited. www.taipower.com.tw has no robots file (its robots address answers the site's error page).
- **The data were found, but cannot be labelled.** Taipower's past supply and demand file (`/d006/loadGraph/loadGraph/data/sys_dem_sup.csv`) answered 200: 656 lines, one a day from 1 January 2025 to 18 October 2026, 71 values each (the date among them), and no header row. Its columns are defined on Taiwan's open-data platform (data.gov.tw), whose robots file answered HTTP 500, as chain 101's session found. That counts as no robots file the ERW can read, so data.gov.tw is not asked.
  - The first columns look like the daily report's supply capability, peak load and reserve margin, and the rest like generating units, but a table labelled from that guess would not trace to its source.
  - **For a later session:** the definitions, from a Taipower page that states them, or from data.gov.tw once its robots file answers.
- The file is saved on the data machine (`runs/license_reads/s2269/`, not in git), unused.

## Requests (3 of 15)

| n | What | Outcome |
|---|---|---|
| 1 | www.taipower.com.tw/robots.txt | 200, the site's error page |
| 2 | Taipower's open data declaration | 200: free reuse with the source cited |
| 3 | sys_dem_sup.csv | 200, 191,131 bytes, no header |

Reads recorded: 441 and 442.

## Decisions made without you

- **No table from a file whose columns are not defined where the ERW can read them.**

## For Samuel's ruling

- None new.

## Files

- New: this report.
- Changed: `warehouse/metadata/license_reads.csv`, `docs/licenses.md`.
- On the data machine only: `runs/c103/s2269/`.
