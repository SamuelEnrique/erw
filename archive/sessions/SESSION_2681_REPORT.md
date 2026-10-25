# Session 2681 report: method notes for chain 134's three tables, and the Stanford draft of its two public tables

25 October 2026, about 12:05 to 12:18 UTC, on lab-desktop (the data machine), chain 134, unattended. Run after session 2684, so that its table is in. Precheck passed (`runs/c134/pre2681.out`). Model spend USD 0. Pulls: 84 Redivis requests of 150, and 1 to Supabase; none to a publisher.

## Read these first

- **Method notes** for the chain's three tables, each checked against its table by code (`runs/c134/s2681_check.py`). All 34 figures they name, with the tables' row and entity counts, retrieval times and BC Hydro's first and last hours, match. Each note has its Method cell (`runs/c134/cells.py`, copied from chain 133's):
  - `docs/methods/desnz_uk_nations_electricity_annual.md` (the UK nations, public; the derived block left out, Table 1's gaps stated);
  - `docs/methods/bchydro_ba_load_hourly.md` (British Columbia, internal; the time base and its daylight-saving days);
  - `docs/methods/desnz_regional_renewables_annual.md` (the UK's regions, public; each year's columns kept).
- **One fix the check found:** the regional renewables note first gave the workbook's retrieval as 12:00:28Z. The table says 12:00:30Z, and the note was set right before its commit.
- **With these, every held table outside the unlanded chains' eight has a note** (`runs/c134/undescribed.py`: 586 tables, 8 without).
- **The Stanford draft:** two public tables uploaded, each proved by the draft's count: `desnz_uk_nations_electricity_annual` (4,167 rows) and `desnz_regional_renewables_annual` (3,002).
  - `bchydro_ba_load_hourly` is internal and was not uploaded.
  - A plain upload under the data lock (cap 130), the main checkout pulled first, from this branch merged with main (nothing new on main): `runs/c134/s2681.sh`, copied from chain 133's.
  - The metadata tables were proved whole: `erw_headers` 5,171 lines, `erw_coverage` 586 rows, `erw_sources` 676 rows.
  - Reconciles: before, 427 tables, 367 match, 58 differ, 2 not yet uploaded; after, 371 match, 56 differ (tables the daily runs have grown since their upload), none missing.
  - Requests: 8, 68 (with 1 to Supabase) and 8. **Nothing released.**
- **The upload record** (`warehouse/metadata/redivis_uploads_stanford.csv`) and the release note's paragraph go in with this report.

## Decisions made without you

- **Session 2684 run before this one,** so that its table is described and uploaded with the chain's others.

## For Samuel's ruling

- **Releasing the draft,** as before: a person's click after the diff.

## Files

- New: three method notes; this report.
- Changed: `docs/coverage.md` (three Method cells), `docs/reviews/redivis-v1-release-note-2026-10-23.md`, `warehouse/metadata/redivis_uploads_stanford.csv`.
- On the data machine only: `runs/c134/s2681.sh`, `runs/c134/s2681/`, `runs/c134/s2681_check.py`, `runs/c134/cells.py`.
