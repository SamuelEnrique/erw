# Session 2623 report: a second own choice, none taken (Andorra's statistics site is drawn by script; every IMSEE address serves Monaco's home page)

25 October 2026, about 06:54 to 06:58 UTC, on lab-desktop (the data machine), chain 130, unattended. Precheck passed (`runs/c130/pre2623.out`). Model spend USD 0. Pulls: 5 requests of 20.

## Why these

- **Andorra and Monaco** appear nowhere in the record, the queue or the unlanded chains' branches. Andorra's Departament d'Estadistica publishes a monthly energy bulletin (A115: consumption, imports and domestic production; searches find copies on a newspaper's host).

## Read these first

- **No table.**
- **Andorra:** www.estadistica.ad has no robots file (HTTP 404, read 1259). Its root page (read 1260) is a server's start page whose script sends the reader to an ArcGIS Hub site (`/portal/apps/sites/#/estadistica-ca/`), drawn by script. Earlier chains did not take such sites. The bulletin's copies on altaveu.com are a newspaper's, not first-hand, and were not asked.
- **Monaco (IMSEE):** the robots address (read 1261), the Territoire et environnement theme (read 1262) and the Mentions legales (read 1263) each serve the home page itself (the same 435,001 bytes). No table or terms could be read; the footer reads "Tous droits reserves".
- **No verdict:** no terms could be read.

## Requests (5 of 20)

| n | What | Outcome |
|---|---|---|
| 1, 2 | www.estadistica.ad's robots file and root page | 404; a script redirect |
| 3 to 5 | www.imsee.mc's robots address, environment theme and Mentions legales | 200, each the home page |

Reads recorded: 1259 to 1263.

## Decisions made without you

- **Neither taken,** and no figure taken from a newspaper's copy of Andorra's bulletin. Session 2628 is the chain's third own choice.

## For Samuel's ruling

- None new.

## Files

- New: this report.
- Changed: the license record (reads 1259 to 1263) and `docs/licenses.md`.
- On the data machine only: `runs/c130/s2623/`, `runs/license_reads/s2623/`.
