# Session 2660 report: Angola's electricity not taken (INE's lists load by script under a copyright line; IRSEA has published no report; PRODEL's site is drawn by script)

25 October 2026, about 10:13 to 10:18 UTC, on lab-desktop (the data machine), chain 133, unattended. Precheck passed (`runs/c133/pre2660.out`). Model spend USD 0. Pulls: 8 requests of 15, all by the probe.

## Read these first

- **The ERW held Angola only in EIA's world tables;** no source or read named INE Angola, PRODEL, ENDE or IRSEA.
- **INE (www.ine.gov.ao):**
  - It has no robots file (HTTP 404, read 1350).
  - Its home page (read 1351) loads its publication lists by script ("A carregar...").
  - Its footer is a copyright line only: "Copyright 2021 - | Instituto Nacional de Estatistica | Todos os direitos reservados".
  - Its only electricity series named on the page is the industrial production index, an index rather than a quantity.
- **IRSEA, the regulator:**
  - www.irsea.gov.ao's robots file allows `/` with a 3-second crawl delay (read 1352), kept by a sleep before each request.
  - Its home page sent the reader to irsea.gov.ao (read 1353). That host's robots file was asked next, before any other path, and has the same rules (read 1354).
  - The publications page lists no report: "Ainda nao existe informacao!" under both studies and reports (read 1355). Its footer: "(c) 2026 IRSEA | Todos Direitos Reservados".
  - The electricity page gives the regulated companies, the tariffs (prices, not taken) and the service quality rules, but no production figures (read 1356).
- **PRODEL, the generator:** www.prodel.co.ao has no robots file, and its robots address serves the site's page, drawn by script (read 1357). Nothing more was asked.
- **No table.** ENDE and the ministry (MINEA) were not asked within this ceiling.

## Decisions made without you

- **Angola not taken.** INE and IRSEA go to session 2663's round from reads 1351 and 1355. Each shows a copyright line with no reuse statement.

## For Samuel's ruling

- None new.

## Files

- New: this report.
- Changed: `warehouse/metadata/license_reads.csv` (reads 1350 to 1357), `docs/licenses.md`.
- On the data machine only: `runs/c133/s2660/`, `runs/license_reads/s2660/`.
