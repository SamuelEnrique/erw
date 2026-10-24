# Session 2364 report: Europe's coal a month (Eurostat), a second source of the session's own choosing

24 October 2026, from 08:58 UTC, on lab-desktop (the data machine), a session of `queue/done/110-day-12-november-data-pakistan-bangladesh-morocco-kazakhstan.md`. Model spend USD 0.

Pulls: 3 requests of 20:
- ec.europa.eu's robots file;
- nrg_cb_sffm (answered at once);
- the SIEC codelist.

The trial and the write ran offline.

## Read these first

- **Why:** Eurostat's monthly solid fuels supply sits beside session 2363's monthly oil. The ERW held no European coal series by month, and no chain took it (the other agents were told).
- **One series table, `eurostat_solid_fuels_monthly`:** 209,040 figures, public.
  - **Coverage:** January 2016 to September 2026, 37 European countries and the EU27 aggregate.
  - **Fuels:** hard coal, brown coal, coke oven coke, peat, and oil shale and oil sands.
  - **Flows:** every one the file gives, 16 balance items:
    - production, imports (and those from outside the EU), exports;
    - opening and closing stocks and their change, gross inland deliveries;
    - power plants' and coke ovens' intake, and industry's and other sectors' final consumption.
  - **Unit:** `t` (Eurostat's thousand tonnes times 1,000).
  - **License:** Eurostat's verdict is on record.
- **Left out by Eurostat's terms:** the United Kingdom and Kosovo, named in the header.
- **`vintage`** is empty: the shared fetch helper (`ip.vintage_of`) found no Last-Modified in Eurostat's answer; Eurostat's own last update is in the header (worded by session 2366).
- **The checks:**
  - **Members against the EU:** hard coal and brown coal production summed over the members that report equal Eurostat's EU27 figure in all 124 months of hard coal and 124 of 126 of brown coal (1 t apart in two); all 27 report in 88 and 78 of them (corrected by session 2366).
  - **The EU in 2024:** it produced 45.3 Mt of hard coal and 196.6 Mt of brown coal.
- **Registered:**
  - the sector rule (`coal`), the live-set hold;
  - the release package's held list and its rows (the release check passes);
  - the license tables (licenses check: 506 tables, 0 problems);
  - the test, `tests/test_session2364.py` (3 tests).
- **Not in the Stanford draft yet:** session 2366 uploads it.

## Errors

- None.

## Decisions made without you

- **Eurostat's monthly solid fuels** as the second own choice, all five fuels kept.

## For Samuel's ruling

- None new.

## Files

- New: `warehouse/connectors/eurostat_solid_fuels_monthly.py`, `tests/test_session2364.py`, this report.
- Changed:
  - `warehouse/metadata/build_coverage.py`, `warehouse/supabase/live_set.yaml`, `warehouse/redivis/release_v1.py`;
  - `docs/redivis/release-v1/`;
  - `docs/coverage.md`, `coverage.csv`, `sources.csv`, `archive_manifest.csv`, `license_tables.csv`, `docs/licenses.md`.
- On the data machine only: `runs/c110/s2364/`, `runs/license_reads/s2364/`.
