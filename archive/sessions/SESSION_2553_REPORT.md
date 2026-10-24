# Session 2553 report: a second own choice, none taken (DOE Philippines serves no statistics file; China's yearbook tables are images)

24 October 2026, about 23:18 to 23:22 UTC, on lab-desktop (the data machine), chain 125, unattended. Precheck passed (`runs/c125/pre2553.out`). Model spend USD 0. Pulls: 8 requests of 20 (6 by the probe, 2 by fetches).

## Read these first

- **The Philippines (DOE):** the ERW holds no Philippine source (PSA's OpenSTAT and IEMOP were closed by chains 106 and 109). doe.gov.ph serves its site's page at the robots address (no robots file, read 1038). DOE's 2024 power statistics PDFs are indexed on legacy.doe.gov.ph, whose name no longer resolves (read 1039); at the same paths on doe.gov.ph the 2024 summary and the 2023 summary each answer with the site's HTML page (status 200), not a file. Not taken.
- **China (NBS):** the ERW holds no Chinese source. data.stats.gov.cn and www.stats.gov.cn have no robots file (reads 1040, 1041). The China Statistical Yearbook 2025's English index is a frame set (read 1042); its table list (read 1043) gives the energy chapter's tables (9-01 to 9-19) as JPG images, and no session reads a table from an image. NBS's monthly releases give a month at a time in a page each, which this ceiling would not cover. Not taken.
- **No table this session.**

## Requests (8 of 20)

| n | What | Outcome |
|---|---|---|
| 1, 2 | doe.gov.ph's robots address and legacy.doe.gov.ph's robots file | 200, the site's page; the name does not resolve |
| 3, 4 | the 2024 and 2023 summaries on doe.gov.ph (fetches) | 200, the site's HTML page each |
| 5, 6 | data.stats.gov.cn and www.stats.gov.cn robots files | 404, 404 |
| 7, 8 | the yearbook's index and its table list | 200 |

Reads recorded: 1038 to 1043. Three web searches found DOE's and NBS's files; they reached no publisher's host.

## Decisions made without you

- **No table read from images, and none from a host that answers a file's address with a page.**

## For Samuel's ruling

- None.

## Files

- Changed: `warehouse/metadata/license_reads.csv` (reads 1038 to 1043), `docs/licenses.md`. New: this report.
- On the data machine only: `runs/c125/s2553/`, `warehouse/raw/doe_ph/` (the two HTML pages).
