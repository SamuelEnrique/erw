# Session 2358 report: Bangladesh closed, Moldova's electricity in its place (StatBank)

24 October 2026, from 08:28 UTC, on lab-desktop (the data machine), a session of `queue/done/110-day-12-november-data-pakistan-bangladesh-morocco-kazakhstan.md`. Model spend USD 0.

Pulls: 10 requests of 15:
- **Bangladesh:** pgcb.gov.bd's, www.pgcb.gov.bd's and bpdb.gov.bd's robots addresses (certificate verification failed on all three).
- **Moldova:**
  - statbank.statistica.md's robots address (HTTP 404);
  - four listings of StatBank's PxWeb API;
  - the table's metadata;
  - one JSON-stat query by POST.

The trial and the write ran offline.

## Read these first

- **Bangladesh is closed to the reader.** The Power Grid Company of Bangladesh (both hosts) and the Bangladesh Power Development Board answer with certificates that fail verification, and the ERW does not work around that (as for the Corps of Engineers' host, session 2255). The file's rule replaces a closed source with another public one.
- **In Bangladesh's place: Moldova, from the National Bureau of Statistics' StatBank** (not held; no chain planned it).
  - **Table:** `statbank_moldova_electricity_monthly`, 980 figures, January 2015 to August 2026, internal until the licenses' round reads the bureau's terms.
  - **Variables (7):** production, imports, electricity acquired from other sources, stock change, exports, gross inland consumption, and the residential sector's share.
  - **Access:** one query by POST after the metadata's GET, as session 2357 reads MakStat.
- **The unit was found from the data.** The API states none; the figures are thousand kWh, which is MWh:
  - StatBank's exports equal Eurostat's for Moldova (`eurostat_electricity_monthly`, entity `eurostat_elec:MD`): median ratio 1.000 over 79 months;
  - its production, gross, is about 13 percent over Eurostat's net production.
- **Imports, two ways.** The bureau's "Import" leaves out the electricity bought from the Transnistrian region's plant, which it counts as "acquired from other sources". Imports plus that line equal Eurostat's imports in all 79 months. The header says so.
- **The months of 2026 not yet published** (September to December) have no row.
- **Registered:** the sector rule (`power`), the live-set hold, the license tables (licenses check: 497 tables, 0 problems). The test is `tests/test_session2358.py` (3 tests).

## Errors

- None.

## Decisions made without you

- **Bangladesh replaced by Moldova,** as the file's rule allows.
- **The unit read as MWh** from the agreement with Eurostat, the API stating none.

## For Samuel's ruling

- None new.

## Files

- New: `warehouse/connectors/statbank_moldova.py`, `tests/test_session2358.py`, this report.
- Changed: `warehouse/metadata/build_coverage.py`, `warehouse/supabase/live_set.yaml`, `docs/coverage.md`, `coverage.csv`, `sources.csv`, `archive_manifest.csv`, `license_tables.csv`, `docs/licenses.md`.
- On the data machine only: `runs/c110/s2358/`, `runs/license_reads/s2358/`.
