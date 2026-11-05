# Session 2731 report: method notes for chain 137's three tables, and the Stanford draft of all three

25 October 2026, about 19:46 to 20:00 UTC, on lab-desktop (the data machine), chain 137, unattended. Run after session 2734, so that its table is described and uploaded with the chain's others. Precheck passed (`runs/c137/pre2731.out`). Model spend USD 0. Pulls: 86 Redivis requests of 150, and 1 to Supabase; none to a publisher.

## Read these first

- **Method notes** for the chain's three tables, each checked against its table by code (`runs/c137/s2731_check.py`). All 56 figures the notes name match: counts, retrieval times, the 2015 difference, and both sides of each cross-check. Each note has its Method cell (`runs/c137/cells.py`):
  - `docs/methods/desnz_uk_plant_loads_annual.md` (the UK's maximum load, load factors and efficiency; DESNZ's March-ending year);
  - `docs/methods/desnz_uk_co2_intensity_annual.md` (the CO2 intensity of the UK's electricity supplied);
  - `docs/methods/desnz_uk_derated_capacity_annual.md` (de-rated capacity; DESNZ's own 99 MW of 2015 and 2016).
- **One fix the check found, my own:** I had written that each year's GB peak sits "9,000 to 12,500 MW" above Elexon's highest daily mean. The gaps run from 8,157 MW (2024) to 12,551 (2025). It was corrected to "8,150 to 12,550" in the note and in session 2728's report.
- **With these, every held table outside the unlanded chains' eight has a note** (`runs/c137/undescribed.py`: 596 tables, 8 without).
- **The Stanford draft:** three public tables uploaded, each proved by the draft's count:
  - `desnz_uk_plant_loads_annual` (425 rows);
  - `desnz_uk_co2_intensity_annual` (119);
  - `desnz_uk_derated_capacity_annual` (1,680).

  How it ran:
  - A plain upload under the data lock (cap 130), the main checkout pulled first, from this branch merged with main (nothing new on main): `runs/c137/s2731.sh`, copied from chain 136's.
  - The metadata tables were proved whole: `erw_headers` 5,264 lines, `erw_coverage` 596 rows, `erw_sources` 686 rows.
  - Reconciles: before, 436 tables, 373 match, 60 differ, 3 not yet uploaded; after, 378 match, 58 differ (tables the daily runs have grown since their upload), none missing.
  - Requests: 8, 71 (with 1 to Supabase) and 8. **Nothing released.**
- **The upload record** (`warehouse/metadata/redivis_uploads_stanford.csv`) and the release note's paragraph go in with this report.

## Decisions made without you

- **Session 2734 run before this one,** so that its table is in the notes and the upload.

## For Samuel's ruling

- **Releasing the draft,** as before: a person's click after the diff.

## Files

- New: three method notes; this report.
- Changed: `docs/coverage.md` (three Method cells), `docs/reviews/redivis-v1-release-note-2026-10-23.md`, `warehouse/metadata/redivis_uploads_stanford.csv`, `archive/sessions/SESSION_2728_REPORT.md` (the gap range).
- On the data machine only: `runs/c137/s2731.sh`, `runs/c137/s2731/`, `runs/c137/s2731_check.py`, `runs/c137/s2731_note.py`, `runs/c137/cells.py`.
