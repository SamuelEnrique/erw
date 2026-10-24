# Session 2282 report: Japan's areas' demand: not taken (TEPCO refuses the reader, Kansai's terms forbid reposting, OCCTO's data sit behind its system); Portugal's production by type an hour (Energy-Charts) in its place

24 October 2026, from 05:07 UTC, on lab-desktop (the data machine), the third session of `queue/done/104-day-7-november-data-portugal-italy-japan-argentina.md`, unattended. Model spend USD 0. Pulls: 12 requests of 15 (below).

## Read these first

- **Japan is closed to the ERW for now:**
  - OCCTO's site has no robots file (read 472), but its area supply-and-demand data are served through its interactive system pages (occtonet3), not as files.
  - TEPCO's host answers HTTP 403 even to its robots file (read 473), so it is not asked again.
  - **Kansai Transmission and Distribution's site terms** (read 476) give a new verdict, needs written permission in both columns: beyond private use and what copyright law allows, copying, transmitting, distributing, altering or reposting the site's data on one's own website without permission violates copyright, and prior permission is asked.
- **Portugal's production by type an hour in its place,** under the queue file's rule (a source that cannot be taken is replaced by another public one).
  - Energy-Charts' Portugal series, under the CC BY 4.0 of the API's description (read 471, session 2281).
  - It is a public companion to session 2280's `ren_portugal_balance_annual`, which is internal while REN states no terms.
- **One table written, validated, archived, in coverage (sector power), in the release package, both holds:** `energy_charts_portugal_power`, 2020 to 22 October 2026, 725,799 rows, hourly, in MW.
- **The cross-check** (`runs/c104/s2282/cross.py`, `cross.out`):
  - **Energy-Charts' Portuguese load equals REN's consumption** (session 2280's table) to the GWh in five of six years, and within 0.05% in the other (2022: 50.308 against 50.332 TWh). So Energy-Charts republishes REN's figures.
  - Against Ember the same 0.877 to 0.924 as REN's.
  - Production, storage and trading less load is a median 6 MW (0.11% of load).
  - Solar rose from 1.3 TWh in 2020 to 6.1 in 2025.
- **A licensing question this raises,** for Samuel: Energy-Charts states CC BY 4.0 over its API's data. Its Portuguese series are REN's figures, and its Italian ones (session 2281) are likely Terna's, published by operators that state no terms (REN) or allow only personal use (Terna). The two tables are public under Energy-Charts' statement, as chains 102's and 103's Energy-Charts tables are.

## The pulls

1. www.occto.or.jp/robots.txt (read 472): HTTP 404.
2. www.tepco.co.jp/robots.txt (read 473): HTTP 403.
3. www.kansai-td.co.jp/robots.txt (read 474): HTTP 404.
4. Kansai's electricity forecast page (read 475).
5. Kansai's site terms (read 476).
6. to 12. Energy-Charts' Portugal, a year a request, 2020 to 2026 (to 22 October), 31 seconds apart. They were seeded into the raw store, and the trial and the write read them offline.

## Errors

- **The connector's generator first split the template's docstring at its opening quotes;** fixed before any write.

## Decisions made without you

- **Japan left** at its hosts and terms; Energy-Charts' Portugal in its place.

## For Samuel's ruling

- **Energy-Charts' CC BY over operators' figures** (above): keep the Energy-Charts tables public, or follow the operators' own terms? Undone: public under Energy-Charts' statement.
- **Kansai's and OCCTO's data** need consent or an interface the ERW's reader can use.

## Files

- New: `warehouse/connectors/energy_charts_portugal.py`, `tests/test_session2282.py`, this report.
- Changed:
  - `warehouse/metadata/build_coverage.py`, `warehouse/redivis/release_v1.py`, `warehouse/supabase/live_set.yaml`
  - `warehouse/metadata/license_reads.csv` (441 to 445), `warehouse/metadata/license_verdicts.csv` (Kansai)
  - the coverage, sources, archive manifest and license files
  - `docs/redivis/release-v1/`
- On the data machine only: `runs/c104/s2282/`, `runs/license_reads/s2282/`, `runs/s2282_*`, `warehouse/raw/energy_charts_portugal/`.
