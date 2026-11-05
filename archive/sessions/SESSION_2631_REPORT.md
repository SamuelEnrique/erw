# Session 2631 report: Burundi's electricity not taken (INSBU's site drawn by script; REGIDESO publishes no figures)

25 October 2026, about 07:47 to 07:51 UTC, on lab-desktop (the data machine), chain 131, unattended. Precheck passed (`runs/c131/pre2631.out`). Model spend USD 0. Pulls: 6 requests of 15 (5 by the probe, 1 fetch).

## Read these first

- **No table.**
- **The statistics office, now INSBU (ISTEEBU before 2023):** its robots file names `*` with no rule (read 1270). Its site is now drawn by script: the media list address returns the app's shell (read 1271). So does the address of its fourth-quarter 2023 economic bulletin, which searches give (1,041 bytes, fetched once). Earlier chains did not take sites drawn by script.
- **The utility, REGIDESO:** its robots file closes only `/wp-admin/` (read 1272). Its media list holds no report (read 1273). Its fifty newest PDFs (read 1274) are recruitment notices and environmental management plans, with no statistics.
- **No verdict:** no terms page was read.

## Requests (6 of 15)

| n | What | Outcome |
|---|---|---|
| 1, 2 | www.insbu.bi's robots file and media list address | 200; the list a script shell |
| 3 | INSBU's fourth-quarter 2023 bulletin address (a fetch) | 200, a script shell of 1,041 bytes |
| 4 to 6 | www.regideso.bi's robots file and two media lists | 200; no statistics |

Reads recorded: 1270 to 1274.

## Decisions made without you

- **Burundi not taken:** no first-hand table is in reach.

## For Samuel's ruling

- None new.

## Files

- New: this report.
- Changed: the license record (reads 1270 to 1274) and `docs/licenses.md`.
- On the data machine only: `runs/c131/s2631/`, `runs/license_reads/s2631/`, `warehouse/raw/insbu_bi/`.
