# Session 2667 report: method notes for chain 133's five tables, and the Stanford draft of its four public tables and chain 132's last

25 October 2026, about 10:50 to 11:05 UTC, on lab-desktop (the data machine), chain 133, unattended. Run after session 2670, so that its table is in. Precheck passed (`runs/c133/pre2667.out`). Model spend USD 0. Pulls: 93 Redivis requests of 150, and 1 to Supabase; none to a publisher.

## Read these first

- **Method notes** for the chain's five tables, each checked against its table by code (`runs/c133/s2667_check.py`). All 76 figures they name, with the tables' row and entity counts, match: 0 differences. Each note has its Method cell (`runs/c133/cells.py`, copied from chain 132's):
  - `docs/methods/stat_tj_tajikistan_electricity_annual.md` (Tajikistan, public; the table's parts that do not add);
  - `docs/methods/cosit_iraq_electricity_annual.md` (Iraq, internal; investment plants counted with imports);
  - `docs/methods/stat_kz_kazakhstan_electricity_annual.md` (Kazakhstan, public; the editions' row names, and the plant classes' break between 2024 and 2025);
  - `docs/methods/aedg_alaska_generation_monthly.md` (Alaska, public; one row a service area; 78 per cent of EIA's 2021 total);
  - `docs/methods/asub_aland_electricity_sales_annual.md` (Aland's sales, public).
  - No contradiction found.
- **With these, every held table outside the unlanded chains' eight has a note** (`runs/c133/undescribed.py`: 583 tables, 8 without).
- **The Stanford draft:** five public tables uploaded, each proved by the draft's count:
  - `edf_sei_islands_electricity_annual` (326 rows), chain 132's, which came after session 2653's upload;
  - `stat_tj_tajikistan_electricity_annual` (475), `stat_kz_kazakhstan_electricity_annual` (84), `aedg_alaska_generation_monthly` (51,061) and `asub_aland_electricity_sales_annual` (603).
  - `cosit_iraq_electricity_annual` is internal and was not uploaded.
  - A plain upload under the data lock (cap 130), the main checkout pulled first, from this branch merged with main (a weekly vacuum commit came in): `runs/c133/s2667.sh`, copied from chain 132's.
  - The metadata tables were proved whole: `erw_headers` 5,151 lines, `erw_coverage` 583 rows, `erw_sources` 673 rows.
  - Reconciles: before, 425 tables, 362 match, 58 differ, 5 not yet uploaded; after, 369 match, 56 differ (tables the daily runs have grown since their upload), none missing.
  - Requests: 8, 77 (with 1 to Supabase) and 8. **Nothing released.**
- **The upload record** (`warehouse/metadata/redivis_uploads_stanford.csv`) and the release note's paragraph go in with this report.

## Decisions made without you

- **Session 2670 run before this one,** so that its table is described and uploaded with the chain's others.

## For Samuel's ruling

- **Releasing the draft,** as before: a person's click after the diff.

## Files

- New: five method notes; this report.
- Changed: `docs/coverage.md` (five Method cells), `docs/reviews/redivis-v1-release-note-2026-10-23.md`, `warehouse/metadata/redivis_uploads_stanford.csv`.
- On the data machine only: `runs/c133/s2667.sh`, `runs/c133/s2667/`, `runs/c133/s2667_check.py`, `runs/c133/cells.py`.
