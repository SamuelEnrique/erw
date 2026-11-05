# Session 2604 report: Sierra Leone's electricity not taken (no current published series); Statistics Sierra Leone's open licence read

25 October 2026, about 05:02 to 05:08 UTC, on lab-desktop (the data machine), chain 129, unattended. Precheck passed (`runs/c129/pre2604.out`). Model spend USD 0. Pulls: 13 requests of 15 (12 by the probe, 1 fetch).

## Read these first

- **No table.** None of the three publishers puts a current generation or sales series online:
  - **Statistics Sierra Leone (Stats SL):** its Publications page (read 1190) holds no energy publication; its newest statistical digest covers 2007 to 2013, and its home page (read 1188) lists none.
  - **The regulator, EWRC:** its pages' sitemap (read 1185, 37 pages) leads to two annual reports, for 2019 and 2020 (read 1186). The 2020 report (48 pages, fetched) holds tariffs, complaints and EWRC's own accounts, no generation or sales series. Its Other Reports page (read 1187) holds public registers and water reports.
  - **The distributor, EDSA:** its home page (read 1189) links a project impacts register and a privacy page, no figures. Its robots address returns the home page, so it has no robots file (read 1183).
- **The hosts:** www.statistics.sl's robots file names `*` and closes only system folders (read 1181); ewrc.gov.sl's allows `/` (read 1182). No crawl delay and no AI agent named in either.
- **One verdict, for a later chain: Statistics Sierra Leone may be public.** Its Terms and Conditions send the use of data to its Open Licence Agreement (read 1191). The Agreement (read 1192): "STATS SL hereby grants you ... a non-exclusive, worldwide, royalty-free license to copy, modify, translate, publish, adapt, distribute, create derivative works from, and otherwise use the data for both commercial and non-commercial purposes", with the source acknowledged in its own words. It does not reach third parties' data, which is INSTAT Mali's form.
- **The 2007 to 2013 digest was not fetched.** Its electricity figures would be the former National Power Authority's, which the licence does not reach, and they end in 2013.

## Requests (13 of 15)

| n | What | Outcome |
|---|---|---|
| 1 to 3 | the robots files of www.statistics.sl, ewrc.gov.sl and edsa.sl | 200 (EDSA's address returns its home page) |
| 4, 5 | EWRC's sitemap index and pages' sitemap | 200 |
| 6, 7 | EWRC's Annual Reports and Other Reports pages | 200 |
| 8 | EWRC's 2020 annual report (a fetch) | 200, 8.7 MB, no generation series |
| 9, 10 | Stats SL's and EDSA's home pages | 200 |
| 11 | Stats SL's Publications page | 200 |
| 12, 13 | Stats SL's Terms and Conditions and Open Licence Agreement | 200 |

Reads recorded: 1181 to 1192 (read 1185's page count corrected to 37 before the commit).

## Decisions made without you

- **Sierra Leone not taken:** no publisher has a series after 2013 online, and no figure is taken from the press or a secondary source.
- **Stats SL's verdict recorded now,** with no table, so that a later chain needs no new read.

## For Samuel's ruling

- Nothing new.

## Files

- New: this report.
- Changed: the license record (reads 1181 to 1192, Stats SL's verdict) and `docs/licenses.md`.
- On the data machine only: `runs/c129/s2604/`, `runs/license_reads/s2604/`, `warehouse/raw/ewrc_sl/`.
