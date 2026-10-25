# Session 2766 report: ISTAT not taken (its SDMX service down, its legacy host a redirect loop); the session's ceiling passed by a redirect loop

25 October 2026, about 23:53 to 23:55 UTC, on lab-desktop (the data machine), chain 140, unattended. Precheck passed (`runs/c140/pre2766.out`). Model spend USD 0. Pulls: 5 probe lines of 15, **but about 35 HTTP requests**, as one line followed a redirect loop.

## Read these first

- **A ceiling overrun, mine, reported first:**
  - The probe I copied from chain 139 calls `requests` with redirects allowed and no cap of its own, so `requests`' default of 30 applies.
  - sdmx.istat.it's robots file redirected in a loop. That one probe line followed 30 redirects before the client stopped with TooManyRedirects: **about 31 requests to sdmx.istat.it**, and about 35 for the session against a ceiling of 15.
  - No data was taken from the host. Nothing more was asked of ISTAT after it.
  - **Fixed for the rest of the chain:** `runs/c140/probe_tpl/probe.py` caps redirects at 5, and later sessions copy it. The lesson is in the memory.
- **ISTAT not taken:**
  - www.istat.it's robots file is `User-agent: *` with no rule and names no Claude agent (read 1530). The bare name istat.it does not resolve (read 1531). esploradati.istat.it has no robots file (read 1532).
  - **ISTAT's SDMX service** (esploradati.istat.it/SDMXWS) answered its dataflow list with HTTP 500: "A network-related or instance-specific error occurred while establishing a connection to SQL Server" (read 1533). Its backend was down.
  - **The legacy SDMX host** sdmx.istat.it looped (read 1534).
  - Italy's electricity statistics are Terna's (closed: written permission). ISTAT's energy tables could not be listed tonight.
- **No table.** A later chain may ask ISTAT's SDMX service again, with the redirect cap.

## Requests (5 probe lines; about 35 HTTP requests)

| n | What | Outcome |
|---|---|---|
| 1 | www.istat.it's robots file (its own request) | 200, no rule |
| 2 | istat.it's robots file (its own request) | the name does not resolve |
| 3 | esploradati.istat.it's robots file (its own request) | no file (the data browser's page) |
| 4 | ISTAT's SDMX dataflow list | 500, its SQL server unreachable |
| 5 | sdmx.istat.it's robots file (its own request) | TooManyRedirects after 30 (about 31 requests) |

Reads recorded: 1530 to 1534.

## Decisions made without you

- **The session stopped at the overrun,** with no replacement source sought: any further request would have added to a ceiling already passed.

## For Samuel's ruling

- None new. (The overrun is reported, not a ruling.)

## Files

- New: this report. Changed: the license record (reads 1530 to 1534) and `docs/licenses.md`.
- On the data machine only: `runs/c140/s2766/`, `runs/c140/probe_tpl/probe.py`, `runs/license_reads/s2766/`.
