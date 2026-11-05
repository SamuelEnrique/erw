# Session 2717 report: method notes for chain 136's four tables, and the Stanford draft of its three public tables

25 October 2026, about 18:32 to 18:48 UTC, on lab-desktop (the data machine), chain 136, unattended. Run after session 2720, so that its table is described and uploaded with the chain's others. Precheck passed (`runs/c136/pre2717.out`). Model spend USD 0. Pulls: 92 Redivis requests of 150, and 1 to Supabase; none to a publisher.

## Read these first

- **Method notes** for the chain's four tables, each checked against its table by code (`runs/c136/s2717_check.py`). All 77 figures the notes name match: the tables' counts and spans, retrieval times, coordinates, and both sides of each cross-check. Each note has its Method cell (`runs/c136/cells.py`):
  - `docs/methods/nspower_ns_load_hourly.md` (Nova Scotia's load, internal; the clock, the autumn hour, the lost April 2025);
  - `docs/methods/desnz_uk_power_stations.md` (the UK's stations, public; the grid coordinates converted);
  - `docs/methods/desnz_uk_interconnector_flows_annual.md` (the UK's interconnector flows, public);
  - `docs/methods/desnz_uk_storage_annual.md` (the UK's storage, public).
- **Four of my own lines were set right before the commit:**
  - Two the tables do not hold were removed: a reason for France's net exports in 2022, and the weather behind Nova Scotia's peak.
  - The check found the fifteen hours under 500 MW run past 24 September in UTC. They are all on that day in Atlantic time, the morning post-tropical storm Fiona reached the province, and the note says so.
  - The check also found the 2024 gap against Statistics Canada is 1.4 per cent, not 1.3. It was corrected in the note and in session 2708's report.
- **With these, every held table outside the unlanded chains' eight has a note** (`runs/c136/undescribed.py`: 593 tables, 8 without).
- **The merge of origin/main** (the daily task's page files, `24df3774`) conflicted in `docs/coverage.md` and `coverage.csv` on three tables' generated lines. They were resolved row by row (`runs/c136/s2717_resolve.py`), not as a union:
  - `noaa_uscrn_solar_monthly` keeps the branch's row, which session 2718 corrected;
  - `node_basis_daily` and `node_basis_summary` take main's newer rows.

  Afterwards, read as text, the branch's coverage differs from main's only in session 2718's seven statuses and this chain's four new tables.
- **The Stanford draft:** three public tables uploaded, each proved by the draft's count:
  - `desnz_uk_power_stations` (1,364 rows);
  - `desnz_uk_interconnector_flows_annual` (642);
  - `desnz_uk_storage_annual` (360).

  How it ran:
  - `nspower_ns_load_hourly` is internal and was not uploaded.
  - A plain upload under the data lock (cap 130), the main checkout pulled first, from this branch merged with main: `runs/c136/s2717.sh`, copied from chain 135's.
  - The metadata tables were proved whole: `erw_headers` 5,234 lines, `erw_coverage` 593 rows, `erw_sources` 683 rows.
  - Reconciles: before, 433 tables, 370 match, 60 differ, 3 not yet uploaded; after, 375 match, 58 differ (tables the daily runs have grown since their upload), none missing.
  - Requests: 8, 77 (with 1 to Supabase) and 8. **Nothing released.**
- **The upload record** (`warehouse/metadata/redivis_uploads_stanford.csv`) and the release note's paragraph go in with this report.

## Decisions made without you

- **Session 2720 run before this one,** so that its table is in the notes and the upload.
- **The coverage conflicts resolved row by row,** by which side holds each table's newer truth, rather than as a union, which would have listed three tables twice.

## For Samuel's ruling

- **Releasing the draft,** as before: a person's click after the diff.

## Files

- New: four method notes; this report.
- Changed: `docs/coverage.md` (four Method cells), `docs/reviews/redivis-v1-release-note-2026-10-23.md`, `warehouse/metadata/redivis_uploads_stanford.csv`, `archive/sessions/SESSION_2708_REPORT.md` (the 2024 gap).
- On the data machine only: `runs/c136/s2717.sh`, `runs/c136/s2717/`, `runs/c136/s2717_check.py`, `runs/c136/s2717_note.py`, `runs/c136/s2717_resolve.py`, `runs/c136/cells.py`.
