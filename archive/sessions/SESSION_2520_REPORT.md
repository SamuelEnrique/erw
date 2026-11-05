# Session 2520 report: Seychelles's electricity, not taken (PUC's reports load by script; NBS shows no energy section)

24 October 2026, about 19:13 to 19:14 UTC, on lab-desktop (the data machine), chain 123, unattended. Precheck passed (`runs/c123/pre2520.out`). Model spend USD 0. Pulls: 6 requests of 15.

## Read these first

- **The ERW holds no Seychellois source.**
- **The hosts:** NBS's robots file closes Joomla's system paths (read 944), PUC's `/wp-admin/` only (read 945); the Seychelles Energy Commission's www.sec.gov.sc does not resolve (read 946).
- **PUC:** its site search finds its publications page (read 947), whose annual reports, statistics and other lists are loaded by script ("Loading...", read 949).
- **NBS:** its home page has no energy section in its menu (read 948). Its terms (session 2523) allow short extracts only, with its written consent.
- **Not taken.**

## Requests (6 of 15)

| n | What | Outcome |
|---|---|---|
| 1 to 3 | www.nbs.gov.sc, www.puc.sc and www.sec.gov.sc robots files | 200, 200, the name does not resolve |
| 4 | PUC's site search | 200 |
| 5 | NBS's home page | 200 |
| 6 | PUC's publications page | 200: lists loaded by script |

Reads recorded: 944 to 949 (on this branch). One web search reached no publisher's host.

## Decisions made without you

- **No table for Seychelles.**

## For Samuel's ruling

- None.

## Files

- Changed: `warehouse/metadata/license_reads.csv` (reads 944 to 949), `docs/licenses.md`. New: this report.
- On the data machine only: `runs/c123/s2520/`.
