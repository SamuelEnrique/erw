# Session 2507 report: Lesotho's electricity, not taken (LEC lists no report, LEWA's site finds none); Vanuatu's URA a PDF a month

24 October 2026, about 17:46 to 17:48 UTC, on lab-desktop (the data machine), chain 122, unattended. Precheck passed (`runs/c122/pre2507.out`). Model spend USD 0. Pulls: 9 requests of 15.

## Read these first

- **The ERW holds no Basotho source.**
- **The hosts:** LEWA's and LEC's robots files close `/wp-admin/` only (reads 896, 897); the Bureau of Statistics' www.bos.gov.ls has none (read 898).
- **LEWA:** its site search finds nothing for "statistics" and only a news post for "annual report" (reads 899, 900).
- **LEC:** its search finds its "Annual Reports" page (read 901), which lists no report (read 902).
- **Not taken:** no public figures for Lesotho in reach.
- **A replacement was tried:** Vanuatu's Utilities Regulatory Authority (URA), whose robots file closes Joomla's system paths only (read 903). Its "Monthly Energy Market Snapshot" is one PDF a month (read 904); a series would take a request a month, beyond this session's ceiling. URA's copyright statement (session 2509, read 906) allows personal, non-commercial use only. Left for a session with a larger ceiling, if a ruling allows the use.

## Requests (9 of 15)

| n | What | Outcome |
|---|---|---|
| 1 to 3 | LEWA, LEC and the Bureau of Statistics robots files | 200, 200, 404 |
| 4, 5 | LEWA's site searches | 200: nothing |
| 6, 7 | LEC's search and its annual reports page | 200: no report listed |
| 8 | ura.gov.vu/robots.txt | 200 |
| 9 | URA's snapshot for June 2022 | 200: a PDF a month |

Reads recorded: 896 to 904 (on this branch).

## Decisions made without you

- **No table for Lesotho; Vanuatu not built** within this ceiling.

## For Samuel's ruling

- None.

## Files

- Changed: `warehouse/metadata/license_reads.csv` (reads 896 to 904), `docs/licenses.md`. New: this report.
- On the data machine only: `runs/c122/s2507/`.
