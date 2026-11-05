# Session 2311 report: Uruguay's generation by source, not taken (ADME's generator cannot serve a long span within the ceiling)

24 October 2026, from 06:12 UTC to 06:27 UTC, on lab-desktop (the data machine), chain 106, unattended. Model spend USD 0. Pulls: 9 requests of 15 (5 by the probe, 4 by the fetch: the six-year page, and the one-year page asked three times by `fetch_raw`'s retries before the session stopped it).

## Read these first

- **No table this session.**
- **ADME's data is open.** adme.com.uy and pronos.adme.com.uy have no robots file (both 404). ADME's open data page (read 515) says that, under Article 82 of Law 19355 and Decree 54/2017, "ADME ha implementado el acceso abierto a las bases de datos de la operación del Sistema Interconectado Nacional" (ADME has opened access to the operating databases of the national system). It names the hourly generation by source, from the SCADA, as a spreadsheet (sheets GPF, Eólica, Solar, Térmica, Biomasa, Intercambios). The licenses round (session 2313) reads the licence Decree 54/2017 points to before any verdict.
- **The spreadsheet could not be had for a usable span.**
  - The page `gpf.php` builds the file on request from a start and an end date (its default is 48 hours).
  - Asked for 1 January 2020 to 22 October 2026, it answered a PHP fatal error.
  - Asked for 2025, it did not answer within 300 seconds, twice. The session stopped the fetch so as not to ask ADME's server for the same heavy computation again.
  - A table from monthly pages would need two requests a month (the page, then its file): 160 for 2020 to 2026, beyond any session's ceiling.
- **For a later chain:** a standing daily connector asking yesterday's 48 hours, two requests a day, would build the record forward. It is a choice for a data job, not for one session.

## Requests (9 of 15)

| n | What | Outcome |
|---|---|---|
| 1 | adme.com.uy/robots.txt | 404 |
| 2 | ADME's home page | 200 |
| 3 | ADME's open data page | 200: open access, Law 19355 and Decree 54/2017 |
| 4 | pronos.adme.com.uy/robots.txt | 404 |
| 5 | gpf.php, the default 48 hours | 200: the form and two cached ODS files |
| 6 | gpf.php, 2020 to 2026 | 200: a PHP fatal error |
| 7 to 9 | gpf.php, 2025 | timed out at 300 s, three times; stopped |

Reads recorded: 514 to 516.

## Decisions made without you

- **The fetch stopped after two timeouts** rather than left to its four retries.
- **No table from the 48-hour page alone:** two days are not a record.

## For Samuel's ruling

- **A standing daily pull of ADME's hourly generation** (two requests a day), if Uruguay is wanted.

## Files

- New: this report. Changed: the license record (reads 514 to 516).
- On the data machine only: `runs/c106/s2311/`, `warehouse/raw/adme_generation/` (the error page).
