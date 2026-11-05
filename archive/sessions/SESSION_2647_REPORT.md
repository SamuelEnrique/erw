# Session 2647 report: Sao Tome and Principe's electricity not taken (INE's monthly bulletins give 13 months, of 2021, in a file named for 2022)

25 October 2026, about 08:44 to 08:49 UTC, on lab-desktop (the data machine), chain 132, unattended. Precheck passed (`runs/c132/pre2647.out`). Model spend USD 0. Pulls: 7 requests of 15 (6 by the probe, 1 fetch).

## Read these first

- **No table.**
- **INE:** www.ine.st's robots file closes only the Joomla system paths (read 1307; read with its comments stripped). Its pages lead from Economia (read 1309) to the economy documents (read 1310) and the Conjuntura bulletins (read 1311). These are monthly bulletins of 2017 and 2020 to 2022; the 2022 list (read 1312) gives twelve, the newest December.
- **The December 2022 bulletin** (25 pages, fetched once) has Table 8a, "Evolucao da Producao de Eletricidade", in kWh. But its months run from December 2020 to December 2021, not 2022. Thirteen months whose year disagrees with their file's name are not a series to take.
- The bulletins of earlier years were not fetched: each holds about a year, and the newest data found end in 2021.
- **No verdict:** the home page's footer carries a copyright line (read 1308), but no terms page was read.

## Requests (7 of 15)

| n | What | Outcome |
|---|---|---|
| 1 to 6 | www.ine.st's robots file, home page and the documents' pages | 200 |
| 7 | the December 2022 bulletin (a fetch) | 200, 1.1 MB, 2021's months |

Reads recorded: 1307 to 1312.

## Decisions made without you

- **Sao Tome and Principe not taken.**

## For Samuel's ruling

- None new.

## Files

- New: this report.
- Changed: the license record (reads 1307 to 1312) and `docs/licenses.md`.
- On the data machine only: `runs/c132/s2647/`, `runs/license_reads/s2647/`, `warehouse/raw/ine_st/`.
