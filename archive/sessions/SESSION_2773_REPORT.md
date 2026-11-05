# Session 2773 report: method notes for chain 140's five tables, and the Stanford draft of all five

26 October 2026, about 00:22 to 00:38 UTC, on lab-desktop (the data machine), chain 140, unattended. Run after session 2776, so that its table is described and uploaded with the chain's others. Precheck passed (`runs/c140/pre2773.out`). Model spend USD 0. Pulls: 95 Redivis requests of 150, and 1 to Supabase; none to a publisher.

## Read these first

- **Two errors of mine, found by the check and corrected before the commit:**
  - **Austria's sectors:** report 2764 said 21 sectors and their three totals. 22 sector entities are written: 19 branches and the three totals, as internal navigation and air transport are 0 in every year.
  - **Spain's bound:** report 2765 said the 391,748 dwellings above 10,000 kWh would have to average about 32 MWh to reach Eurostat's household figure. It is about 22.4 MWh: the 64,368 GWh already leaves those dwellings out, and I had added their 10,000 kWh twice.

  Reports 2764 and 2765 are corrected in place, each correction marked.
- **Method notes** for the chain's five tables in four files, each checked against its table by code (`runs/c140/s2773_check.py`). All 90 figures the notes name match: counts, retrieval times, and both sides of each cross-check. Each table has its Method cell (`runs/c140/cells.py`):
  - `docs/methods/statat_austria_electricity_annual.md` (the MWh blocks, nothing converted; the ODS read by streaming);
  - `docs/methods/ine_es_dwellings_electricity_2021.md` (the census's dwellings, every municipality);
  - `docs/methods/statbel_be_electricity_production_annual.md` (to 2025, one year past Eurostat);
  - `docs/methods/statec_lu_electricity_generation_annual.md`, which describes both Luxembourg tables (`Tables:` names the two).
- **With these, every held table outside the unlanded chains' eight has a note** (`runs/c140/undescribed.py`: 608 tables, 8 without).
- **The Stanford draft:** five public tables uploaded, each proved by the draft's count:
  - `statat_austria_electricity_annual` (6,675 rows);
  - `ine_es_dwellings_electricity_2021` (58,626);
  - `statbel_be_electricity_production_annual` (200);
  - `statec_lu_electricity_generation_annual` (942);
  - `statec_lu_electricity_trade_annual` (584).

  How it ran:
  - A plain upload under the data lock (cap 130), the main checkout pulled first, from this branch merged with main: `runs/c140/s2773.sh`, copied from chain 139's.
  - The metadata tables were proved whole: `erw_headers` 5,385 lines, `erw_coverage` 608 rows, `erw_sources` 698 rows.
  - Reconciles: before, 448 tables, 383 match, 60 differ, 5 not yet uploaded; after, 390 match, 58 differ (tables the daily runs have grown since their upload), none missing.
  - Requests: 8, 80 (79 to Redivis, 1 to Supabase) and 8. **Nothing released.**
- **The upload record** (`warehouse/metadata/redivis_uploads_stanford.csv`, five rows) and the release note's paragraph go in with this report.

## Decisions made without you

- **Session 2776 run before this one,** so that its table is in the notes and the upload.
- **One note for both Luxembourg tables,** as they share a publisher, a service and a reading.

## For Samuel's ruling

- **Releasing the draft,** as before: a person's click after the diff.

## Files

- New: four method notes; this report.
- Changed: `docs/coverage.md` (five Method cells), `docs/reviews/redivis-v1-release-note-2026-10-23.md`, `warehouse/metadata/redivis_uploads_stanford.csv`, reports 2764 and 2765 (the corrections).
- On the data machine only: `runs/c140/s2773.sh`, `runs/c140/s2773/`, `runs/c140/s2773_check.py`, `runs/c140/s2773_note.py`, `runs/c140/cells.py`.
