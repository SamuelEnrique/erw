# Session 2619 report: Chad's electricity not taken (INSEED's site drawn by script; ARSE gives its energy by year only as chart labels, which cannot be placed in their years)

25 October 2026, about 06:41 to 06:45 UTC, on lab-desktop (the data machine), chain 130, unattended. Precheck passed (`runs/c130/pre2619.out`). Model spend USD 0. Pulls: 7 requests of 15 (4 by the probe, 3 fetches).

## Read these first

- **No table.**
- **INSEED:**
  - Its robots file allows `/` to `*`, but its dashboard and login, and asks a crawl delay of 1 second (read 1243), which was kept with a sleep before the next request.
  - The 2022 yearbook's address, which searches give, now returns the shell of a new site drawn by script (3.2 kB, fetched once), whose data come from an API on another host (inseed.ssn-tchad.td). Earlier chains did not take sites drawn by script, and the API was not asked.
- **ARSE, the regulator:**
  - www.arse.td's robots file names `*` with no rule (read 1244). Its media list (read 1245) gives the annual reports for 2021, 2023 and 2024, on arse.td, whose robots file was read first (read 1246).
  - The 2024 report (34 pages, fetched) covers the regulator's activities and gives no production figures.
  - The 2023 report (45 pages, fetched) gives the energy delivered by year only as chart labels. Its text names two years: 598 GWh delivered in 2023 and 540 GWh in 2022, and SNE's production falling from 382 to 345 GWh. The chart's labels come out of the PDF in their drawing order (778, 688, 623, 598, 545, 547, 540, 414), so the other years cannot be placed without guessing.
  - Its one table, the available capacity by year (SNE, independent producers and total, 2016 to 2023, in MW), is not the series asked for. Earlier chains took no figures from chart labels (URCA, chain 127).
- **No verdict:** no terms page was read.

## Requests (7 of 15)

| n | What | Outcome |
|---|---|---|
| 1 | www.inseed.td's robots file | 200, a crawl delay of 1 second |
| 2 | INSEED's 2022 yearbook address (a fetch, after the delay) | 200, a script shell of 3.2 kB |
| 3 | www.arse.td's robots file | 200 |
| 4 | ARSE's media list, search "rapport" | 200 |
| 5 | arse.td's robots file | 200 |
| 6, 7 | ARSE's annual reports 2024 and 2023 (fetches) | 200, 3.3 and 1.0 MB |

Reads recorded: 1243 to 1246.

## Decisions made without you

- **Chad not taken:** no figure from chart labels, and none from the World Bank's copies of ARSE's reports. Two years in prose are not a series.
- **INSEED's API on inseed.ssn-tchad.td not asked:** it is the script's own route, which earlier chains left alone (TEIAS, chain 127).

## For Samuel's ruling

- None new.

## Files

- New: this report.
- Changed: the license record (reads 1243 to 1246) and `docs/licenses.md`.
- On the data machine only: `runs/c130/s2619/`, `runs/license_reads/s2619/`, `warehouse/raw/inseed_td/`, `warehouse/raw/arse_td/`.
