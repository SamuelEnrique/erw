# Session 2519 report: Belize's electricity, not taken (the Energy Unit's report draws its figures as charts; SIB and the PUC publish none)

24 October 2026, about 19:11 to 19:13 UTC, on lab-desktop (the data machine), chain 123, unattended. Precheck passed (`runs/c123/pre2519.out`). Model spend USD 0. Pulls: 7 requests of 15 (6 by the probe, 1 by a fetch).

## Read these first

- **The ERW holds no Belizean source.**
- **The hosts:** SIB's and the PUC's robots files close admin paths only (reads 937, 938); BEL has none (read 939).
- **SIB's site search** for "electricity" finds press releases only (read 940); **the PUC's** for "statistics" finds nothing (read 941).
- **The Energy Unit** (Ministry of Public Utilities, Energy and Logistics): www.mpuele.gov.bz's robots file closes upload logs and admin only (read 942). Its "2024 Belize Annual Energy Report" (90.5 MB, 69 pages, last modified 1 October 2025) was fetched once (read 943). Its imprint allows free use with the Energy Unit credited (session 2523's verdict: may be public). But its electricity figures are drawn as charts (figures 20 to 26) and its "Detailed Energy Balance Table" (Appendix B) is an image, so no table can be read from the file. The text gives a few figures: gross generation 922.2 GWh in 2024 (672.7 GWh in 2015), imports from Mexico's CFE 407.7 GWh, BEL's purchases 755.89 GWh and sales 705.23 GWh.
- **Not taken:** a few figures from the text are not a table.

## Requests (7 of 15)

| n | What | Outcome |
|---|---|---|
| 1 to 3 | sib.org.bz, www.puc.bz and www.bel.com.bz robots files | 200, 200, 404 |
| 4, 5 | SIB's and the PUC's searches | 200: nothing |
| 6 | www.mpuele.gov.bz/robots.txt | 200 |
| 7 | the 2024 Belize Annual Energy Report (a fetch) | 200, 90.5 MB |

Reads recorded: 937 to 943 (on this branch). Two web searches found BEL's reports and the Energy Unit's; they reached no publisher's host.

## Decisions made without you

- **No table read from charts or an image.**

## For Samuel's ruling

- None.

## Files

- Changed: `warehouse/metadata/license_reads.csv` (reads 937 to 943), `docs/licenses.md`. New: this report.
- On the data machine only: `runs/c123/s2519/`, `warehouse/raw/belize_energy_report/`.
