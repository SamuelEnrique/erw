# Session 2778 report: LADWP not taken (no current series published); queue file 142 written first

26 October 2026, about 01:42 to 01:48 UTC, on lab-desktop (the data machine), chain 141, unattended. Precheck passed first (`runs/c141/pre2778.out`). Model spend USD 0. Pulls: 4 requests of 15, all by the probe (redirects capped at 5; data.lacity.org's crawl delay of 1 second kept); one web search.

## Read these first

- **Queue file 142 first:**
  - `queue/next/142-day-12-december-data-srp-santee-cooper-nypa-cps-energy.md` (sessions 2792 to 2805) was written from file 141 by `runs/c141/write_142.py`, made by exact replacements from chain 140's writer (`runs/c141/make_write_142.py`). It keeps the rules word for word.
  - 142 was the next free number, and 2792 to 2805 were free on main and on every branch.
  - **Its sources are four more large US public power systems:** the Salt River Project, Santee Cooper, the New York Power Authority and CPS Energy. None is in the record, the queue or the unlanded chains' records. NYPA's session is told that New York's open data portal may be read only if its terms allow (chain 069 found Open NY's did not).
  - Pushed to main alone as `33e77bfb`; snapshots `c141-q142-before` and `c141-q142-after` show **0 differences**.
- **Chain 141's worktree:** `erw-c141` on `wip/2778-2791-data`, from main at `7321f0ae`.
- **LADWP not taken:**
  - www.ladwp.com's robots file closes Drupal's admin, search and user paths and one outage-alerts page, and names no Claude agent (read 1566); ladwp.com redirects to it (read 1567).
  - The City of Los Angeles open data portal (data.lacity.org, Socrata) closes browse filters, OData and login paths, asks a crawl delay of 1 second, and names no Claude agent (read 1568).
  - Its catalog, searched for LADWP power, holds eight results; the newest was updated in November 2018, and "LADWP Power Supply Since 2003" in February 2017 (read 1569). No current series.
  - The search found LADWP's figures on its Facts and Figures page and in PDF presentations (power sales of 22.6 million MWh in FY 2018-19), not in a data file.
  - LADWP's load is held hourly through EIA-930's LDWP balancing authority, and its sales through EIA-861.
- **No table.**
- **Test 205's bound** is raised by 40 for this chain's reads, from 1566.

## Requests (4 of 15)

| n | What | Outcome |
|---|---|---|
| 1 | www.ladwp.com's robots file (its own request) | 200 |
| 2 | ladwp.com's robots file (its own request) | redirected to www's |
| 3 | data.lacity.org's robots file (its own request) | 200, crawl delay 1 |
| 4 | data.lacity.org's catalog, "ladwp power" (after a 2-second wait) | 200, eight results, none current |

Reads recorded: 1566 to 1569.

## Decisions made without you

- **The 2017 dataset not taken:** a power supply table last updated in February 2017 would add a stale series beside EIA's current ones.

## For Samuel's ruling

- None new.

## Files

- New: this report. Changed: test 205's bound, the license record (reads 1566 to 1569) and `docs/licenses.md`.
- On the data machine only: `runs/c141/s2778/`, `runs/c141/make_write_142.py`, `runs/c141/write_142.py`, `runs/c141/raise205.py`, `runs/license_reads/s2778/`.
