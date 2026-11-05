# Session 2687 report: Ukraine's electricity not taken (Ukrenergo behind a Cloudflare challenge; the statistics service's figures found end in 2020)

25 October 2026, about 12:51 to 12:55 UTC, on lab-desktop (the data machine), chain 135, unattended. Precheck passed (`runs/c135/pre2687.out`). Model spend USD 0. Pulls: 3 requests of 15, all by the probe; one web search.

## Read these first

- **The ERW held Ukraine only in EIA's world tables;** no source or read named Ukrenergo or the State Statistics Service.
- **Ukrenergo** (ua.energy): its robots address answers HTTP 403 with a Cloudflare challenge (read 1407); the host is not asked again.
- **The State Statistics Service:**
  - Its old host, ukrstat.gov.ua, fails certificate verification (read 1408).
  - Its new host, stat.gov.ua, allows its pages with a 5-second crawl delay (read 1409).
  - A search found the service's electricity dataset listed for 1990 to 2020 only, on a Ukrainian energy data portal; no later official figure was found.
  - Publication has been limited since 2022, as file 135 foresaw. Nothing more was asked within this ceiling, and no figure was taken from the aggregators the search returned.
- **No table.**

## Decisions made without you

- **Ukraine not taken.** stat.gov.ua is not closed; a later chain may read its pages, keeping the crawl delay.

## For Samuel's ruling

- None new.

## Files

- New: this report.
- Changed: `warehouse/metadata/license_reads.csv` (reads 1407 to 1409), `docs/licenses.md`.
- On the data machine only: `runs/c135/s2687/`, `runs/license_reads/s2687/`.
