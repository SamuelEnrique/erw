# Session 2300 report: Norway's production and consumption a day (Statnett), a source of the session's own choosing

24 October 2026, from 06:28 UTC, on lab-desktop (the data machine), a session of `queue/done/105-day-8-november-data-mexico-india-peru-korea.md`. Model spend USD 0.

Pulls: 8 requests of 20:
- donnees.hydroquebec.com's robots file;
- www.neso.energy's and api.neso.energy's robots files;
- driftsdata.statnett.no's robots address (HTTP 404);
- Statnett's production and consumption data from 2020 (one answer);
- www.statnett.no's robots address (HTTP 404);
- Statnett's two data pages, in English and Norwegian.

The trial and the write ran offline.

## Read these first

- **Why Statnett.**
  - **Not taken elsewhere:** the ERW did not hold a Statnett source, and no chain running or planned has taken it.
  - **Tried first and closed by their robots files:**
    - Hydro-Québec's open data (Quebec exports to New York and New England). Its robots file disallows `/api/` and every download path to all readers but Google, as odre.opendatasoft.com's does.
    - Great Britain's NESO data portal. api.neso.energy, where its files are served, disallows `/` to every reader.
  - **Avoided:** the countries of chains 102 to 109 and the Baltic states chain 106 took.
  - **What it adds:** Norway's daily figures, beside the monthly balance the ERW holds from Statistics Norway (`ssb_norway_electricity_monthly`).
- **One series table, `statnett_norway_daily`:** 4,960 figures, production and consumption in MWh as published, for Norway's days from 1 January 2020 to 23 October 2026. The day in progress is not written. Internal.
- **How the answer is read.**
  - Statnett's answer is two arrays with a start time (Norway's midnight), an end time and a 24-hour step.
  - **They hold one empty slot after each autumn clock-change day,** 2020 to 2025. Placing the values by skipping those slots brings the last slot to Norway's day of the end time, the day in progress (82,734 MWh, partial). Treating them as days would put it six days in the future.
  - **The connector checks that placement** and stops if it fails.
  - **Eight days Statnett leaves empty,** 18 to 25 November 2025, have no row and are named in the header.
- **The cross-check** (`runs/c105/s2300/cross_ssb.py`), monthly sums against Statistics Norway's balance:
  - production is 99.4 percent of total generation (the median of 81 months);
  - consumption is 99.2 percent of gross consumption;
  - November 2025 is 70 percent (the eight missing days), and some summer months are down to 96 percent.
  - Statnett's own page says data "may be missing in some places on this page, for example, data from wind power production that came into operation after 2019". The header says so.
- **A check that could not decide:** the clock-change Sundays do not stand out from the Sundays around them by the hour's worth a 25- or 23-hour day would add or remove (weather moves them more). Whether Statnett counts those days as 24 hours is not known; the note will say so.
- **License: internal.** Neither Statnett page states terms, and there is no robots file on either host. The next licenses round reads Statnett's terms.
- **Registered:** the sector rule (`power`), the live-set hold, the license tables (licenses check: 483 tables, 0 problems). The test is `tests/test_session2300.py` (4 tests).

## Errors

- **The write's metadata patch carried main's newer rows** (chain 104's landing, in the main checkout) and did not apply. The table's own rows were put in by `runs/c102/add_own_rows.py` and checked: one row in each of the four files.

## Decisions made without you

- **Statnett,** after Hydro-Québec and NESO were found closed.
- **The empty autumn slots are read as Statnett's artefact, not as days,** on the evidence of the end time.

## For Samuel's ruling

- None new.

## Files

- New: `warehouse/connectors/statnett_norway.py`, `tests/test_session2300.py`, this report.
- Changed: `warehouse/metadata/build_coverage.py`, `warehouse/supabase/live_set.yaml`, `docs/coverage.md`, `coverage.csv`, `sources.csv`, `archive_manifest.csv`, `license_tables.csv`, `docs/licenses.md`.
- On the data machine only: `runs/c105/s2300/`, `runs/license_reads/s2300/`.
