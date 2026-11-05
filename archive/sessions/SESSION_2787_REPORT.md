# Session 2787 report: method notes for chain 141's three tables, and the Stanford draft of all three

26 October 2026, about 02:08 to 02:22 UTC, on lab-desktop (the data machine), chain 141, unattended. Run after session 2790, so that its table is described and uploaded with the chain's others. Precheck passed (`runs/c141/pre2787.out`). Model spend USD 0. Pulls: 88 Redivis requests of 150, and 1 to Supabase; none to a publisher.

## Read these first

- **Method notes** for the chain's three tables in two files, each checked against its table by code (`runs/c141/s2787_check.py`). All 41 figures the notes name match: counts, retrieval times, and both sides of each cross-check. Each table has its Method cell (`runs/c141/cells.py`):
  - `docs/methods/statec_lu_power_capacity_annual.md`, which describes both new Luxembourg tables (`Tables:` names `statec_lu_power_capacity_annual` and `statec_lu_supplier_mix_annual`): the capacity, and the disclosed supply mix, named as not generation;
  - `docs/methods/eurostat_import_dependency_annual.md` (the extreme ratios kept as published).
- **With these, every held table outside the unlanded chains' eight has a note** (`runs/c141/undescribed.py`: 611 tables, 8 without).
- **The Stanford draft:** three public tables uploaded, each proved by the draft's count:
  - `statec_lu_power_capacity_annual` (951 rows);
  - `statec_lu_supplier_mix_annual` (196);
  - `eurostat_import_dependency_annual` (16,627).

  How it ran:
  - A plain upload under the data lock (cap 130), the main checkout pulled first, from this branch merged with main: `runs/c141/s2787.sh`, copied from chain 140's.
  - The metadata tables were proved whole: `erw_headers` 5,415 lines, `erw_coverage` 611 rows, `erw_sources` 701 rows.
  - Reconciles: before, 451 tables, 388 match, 60 differ, 3 not yet uploaded; after, 393 match, 58 differ (tables the daily runs have grown since their upload), none missing.
  - Requests: 8, 73 (72 to Redivis, 1 to Supabase) and 8. **Nothing released.**
- **The upload record** (`warehouse/metadata/redivis_uploads_stanford.csv`, three rows) and the release note's paragraph go in with this report.

## Decisions made without you

- **Session 2790 run before this one,** so that its table is in the notes and the upload.
- **One note for both new Luxembourg tables,** beside chain 140's note for the generation and trade tables.

## For Samuel's ruling

- **Releasing the draft,** as before: a person's click after the diff.

## Files

- New: two method notes; this report.
- Changed: `docs/coverage.md` (three Method cells), `docs/reviews/redivis-v1-release-note-2026-10-23.md`, `warehouse/metadata/redivis_uploads_stanford.csv`.
- On the data machine only: `runs/c141/s2787.sh`, `runs/c141/s2787/`, `runs/c141/s2787_check.py`, `runs/c141/s2787_note.py`, `runs/c141/cells.py`.
