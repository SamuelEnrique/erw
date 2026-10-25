# Session 2575 report: Algeria's electricity, not taken (ONS's certificate fails, the Ministry's balance is gone, CREG's figures are images or prose)

25 October 2026, about 02:22 to 02:27 UTC, on lab-desktop (the data machine), chain 127, unattended. Precheck passed (`runs/c127/pre2575.out`). Model spend USD 0. Pulls: 13 requests of 15 (10 by the probe, 3 by fetches). No table.

## Read these first

- **The ERW held no source for Algeria** but EIA's international tables.
- **The Office National des Statistiques (ONS):** www.ons.dz's certificate fails verification (read 1099); not asked again.
- **The Ministry of Energy** (www.energy.gov.dz, no robots file, read 1102): its home page (read 1103) says only "(c) Ministry of Energy 2026", and its electricity page (read 1104) is prose. Its 2022 national energy balance, which a search found at `/Media/galerie/bilan_energetique_2022_web_65b0e0d173bab.pdf`, now answers with the site's page (one fetch, 60 kB of HTML); no newer balance is linked.
- **Sonelgaz** (www.sonelgaz.dz) serves its home page at the robots address (read 1101); a search found no report of its with figures.
- **CREG,** the regulator: www.creg.dz does not resolve (read 1100); its site is creg.gov.dz (robots closes /wp-admin/ only, read 1106; www.creg.gov.dz has none, read 1105). Its file list (read 1108) holds activity reports to 2022 and "Chiffres cles 2023". Both fetched once: the key figures (four pages, 8.5 MB) are images with no text layer; the 2022 activity report (29 pages) is prose, with one renewables figure (3,654 GWh cumulative), no table of production. No figure is read from images, and none from prose.
- **No verdict given:** no table was taken, and no terms page was found (the Ministry's footer is a copyright line only).

## Requests (13 of 15)

| n | What | Outcome |
|---|---|---|
| 1 to 4 | www.ons.dz's, www.creg.dz's, www.sonelgaz.dz's and www.energy.gov.dz's robots addresses | a certificate failure, no such name, the home page, an error page |
| 5, 6 | the Ministry's home and electricity pages | 200 |
| 7 | the 2022 energy balance's address (a fetch) | 200, the site's page, not the PDF |
| 8, 9 | www.creg.gov.dz's and creg.gov.dz's robots files | 404, 200 |
| 10, 11 | CREG's media search for "rapport", its list of PDF files | 200 (empty), 200 (68 files) |
| 12, 13 | CREG's key figures 2023 and activity report 2022 (fetches) | 200, 8.5 MB (images) and 1.8 MB (prose) |

Reads recorded: 1099 to 1108 (the probe's ten).

## Decisions made without you

- **Algeria not taken:** no figure from images or prose.

## For Samuel's ruling

- None new.

## Files

- Changed: the license record (reads 1099 to 1108) and `docs/licenses.md`. New: this report.
- On the data machine only: `runs/c127/s2575/`, `warehouse/raw/mem_dz/`, `warehouse/raw/creg_dz/`.
