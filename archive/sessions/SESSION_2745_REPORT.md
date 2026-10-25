# Session 2745 report: method notes for chain 138's three tables, and the Stanford draft of all three

25 October 2026, about 21:10 to 21:24 UTC, on lab-desktop (the data machine), chain 138, unattended. Run after session 2748, so that its table is described and uploaded with the chain's others. Precheck passed (`runs/c138/pre2745.out`). Model spend USD 0. Pulls: 85 Redivis requests of 150, and 1 to Supabase; none to a publisher.

## Read these first

- **Method notes** for the chain's three tables, each checked against its table by code (`runs/c138/s2745_check.py`). All 44 figures the notes name match: counts, retrieval times, and both sides of each cross-check. Each note has its Method cell (`runs/c138/cells.py`):
  - `docs/methods/desnz_uk_capacity_by_connection_annual.md` (installed capacity by transmission and distribution);
  - `docs/methods/desnz_uk_mpp_capacity_countries_annual.md` (the major power producers by UK country; the shares as a ratio);
  - `docs/methods/desnz_uk_fuel_used_generation_annual.md` (fuel used; MTOE stated as MWh).
- **One fix the check found, my own:** the CCGTs' 2025 fuel is 167.15 TWh, which I had rounded to 167.1. It was corrected to 167.2 before the commit.
- **With these, every held table outside the unlanded chains' eight has a note** (`runs/c138/undescribed.py`: 599 tables, 8 without).
- **The Stanford draft:** three public tables uploaded, each proved by the draft's count:
  - `desnz_uk_capacity_by_connection_annual` (1,245 rows);
  - `desnz_uk_mpp_capacity_countries_annual` (1,539);
  - `desnz_uk_fuel_used_generation_annual` (900).

  How it ran:
  - A plain upload under the data lock (cap 130), the main checkout pulled first, from this branch merged with main (nothing new on main): `runs/c138/s2745.sh`, copied from chain 137's.
  - The metadata tables were proved whole: `erw_headers` 5,294 lines, `erw_coverage` 599 rows, `erw_sources` 689 rows.
  - Reconciles: before, 439 tables, 376 match, 60 differ, 3 not yet uploaded; after, 381 match, 58 differ (tables the daily runs have grown since their upload), none missing.
  - Requests: 8, 70 (with 1 to Supabase) and 8. **Nothing released.**
- **The upload record** (`warehouse/metadata/redivis_uploads_stanford.csv`) and the release note's paragraph go in with this report.

## Decisions made without you

- **Session 2748 run before this one,** so that its table is in the notes and the upload.

## For Samuel's ruling

- **Releasing the draft,** as before: a person's click after the diff.

## Files

- New: three method notes; this report.
- Changed: `docs/coverage.md` (three Method cells), `docs/reviews/redivis-v1-release-note-2026-10-23.md`, `warehouse/metadata/redivis_uploads_stanford.csv`.
- On the data machine only: `runs/c138/s2745.sh`, `runs/c138/s2745/`, `runs/c138/s2745_check.py`, `runs/c138/s2745_note.py`, `runs/c138/cells.py`.
