# Session 2043 report: the reactors' event reports (the NRC's Event Notification Reports)

23 October 2026, from 18:34 UTC, on lab-desktop (the data machine), the second session of `queue/done/059-night-24-october-data-storms-reactor-events-lng-climate.md`. Model spend USD 0. Pulls: 15 requests of 15 (www.nrc.gov's robots file, asked in a call of its own and read first; the event reports' index, which answered at its new address under `/documents-reports/`; the raw data file; the data dictionary; the 2025 and 2026 yearly indexes; one daily page; then the trial's eight daily pages). The write, at 18:39 UTC, reused every saved file (`--offline`).

## Read these first

- **One table written, validated, archived, in coverage (sectors power and uranium, public), in the release package, both holds:** `nrc_event_notifications`, 25 rows (one a report and unit) of 20 power reactor reports (16 from the raw file, 4 from the pages), 7 of them scrams: the event's time in UTC and as the NRC wrote it, the facility, unit, region, state, reactor type, the notification's time, the emergency class, every 10 CFR section with its words, the scram code, criticality, and the unit's power and mode before and at the report.
- **Not the latest two years:** the NRC publishes a page a business day (about 245 a year), so two years would take about 490 requests against a ceiling of 15. The table holds what the ceiling allowed: the NRC's raw data file (pipe separated, the fields of its data dictionary), which **stopped updating on 5 August 2025** (its Last-Modified) and holds reports of May to July 2025, and the nine newest daily pages, 13 to 23 October 2026. Only the "Power Reactor" reports are kept (16 of the raw file's 54; agreement state, materials, fuel cycle and Part 21 reports are not).
- **The connector reaches further back on each later run:** it asks for at most `--pages` new daily pages a run (default 10), newest first, and reuses every page an earlier run saved, so later runs fill the current year's pages (about 245; an earlier year is read with `--year`), the table rewritten whole from every saved page each run (session 2052 corrected an earlier line here, which said a run a day would reach two years back). It is not in the daily run; adding it is for a later session.
- **A scram** is a unit whose scram code is not N (A/R automatic, M/R manual) or a report under 50.72(b)(2)(iv)(B), the reactor protection system's actuation while critical: Monticello's report of 28 July 2025 gives code N for a trip from 100 to 0 percent under that section.
- **The probe's three saved copies (the raw file, the 2026 index and the 22 October page) were put in the connector's raw store** (`warehouse/raw/nrc_event_reports/20261023T183500Z_probe/`, each with the time the probe fetched it and its checked hash), so the trial did not ask for them again.

## The cross-check

Each scram against `nrc_reactor_status`'s power for that unit on the event's day and the next (the status report is the morning's), `runs/c059/s2043/cross.py`:

| Report | Unit | Event day (local) | Power before, the report | Status that morning | Status next morning |
|---|---|---|---|---|---|
| 57810 | Watts Bar 2 | 2025-07-13 | 100 | 100 | 0 |
| 57813 | Prairie Island 1 | 2025-07-16 | 100 | 100 | 0 |
| 57822 | Susquehanna 1 | 2025-07-22 | 96 | 96 | 0 |
| 57832 | Monticello | 2025-07-28 | 100 | 100 | 0 |
| 57839 | Braidwood 1 | 2025-07-30 | 100 | 100 | 0 |
| 58489 | Hatch 1 | 2026-10-10 | 100 | 100 | 0 |
| 58501 | Waterford 3 | 2026-10-16 | 75 | 91 | 0 |

Every scram shows the unit at 0 percent the next morning, and six of seven start from the morning's power. Waterford 3 was at 91 percent that morning and at 75 when it tripped at 22:45 CDT.

## Errors

- None that changed a number. The parser was written for the daily pages' power reactor blocks before one had been seen (the 22 October page held none) and stops on any label it does not know; the trial's pages raised none.

## Decisions made without you

- **The raw file and the newest pages within the ceiling,** said in the header, not a sample spread over two years.
- **One row a report and unit** (`nrc_en:<number>:<unit>`); a report in both publications keeps the daily page's row, and stops the run if the two disagree on the time, scram code or power.
- **The event text not taken,** nor the NRC staff notified.
- **The 50.72(b)(2)(iv)(B) rule** added to the scram code to mark a scram, as the chain file names it.
- **No terms page asked:** the NRC's site disclaimer (read 16) holds; the robots file was read again (it disallows only search, ads.txt and autodiscover for every reader).

## For Samuel's ruling

- None new. Whether to add `nrc_event_reports.py` to the daily run (a page a day, and ten a run to fill the two years) is a reversible choice for a later session.

## Files

- New: `warehouse/connectors/nrc_event_reports.py`, `tests/test_session2043.py` (4 tests), this report.
- Changed: `build_coverage.py`, `release_v1.py`, `live_set.yaml`, `docs/coverage.md`, `coverage.csv`, `archive_manifest.csv`, `sources.csv`, `license_tables.csv`, `docs/licenses.md`, `docs/redivis/release-v1/`.
- On the data machine only: `runs/c059/s2043/`, `runs/license_reads/s2043/`, `runs/s2043*`, `warehouse/raw/nrc_event_reports/`.
