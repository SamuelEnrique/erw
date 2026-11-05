# Session 2695 report: method notes for chain 135's three tables, and the Stanford draft of all three

25 October 2026, about 13:21 to 13:36 UTC, on lab-desktop (the data machine), chain 135, unattended. Run after session 2698, so that its table is described and uploaded with the chain's others. Precheck passed (`runs/c135/pre2695.out`). Model spend USD 0. Pulls: 86 Redivis requests of 150, and 1 to Supabase; none to a publisher.

## Read these first

- **Method notes** for the chain's three tables, each checked against its table by code (`runs/c135/s2695_check.py`). All 49 figures the notes name match: the tables' row and entity counts, their retrieval times, and the cross-checks' figures on both sides. Each note has its Method cell (`runs/c135/cells.py`, copied from chain 134's):
  - `docs/methods/desnz_regional_renewable_capacity_annual.md` (the UK's regional capacity, public; the 2022 sheet's names and the co-firing row);
  - `docs/methods/desnz_gb_regional_consumption_annual.md` (Great Britain's electricity by region, public; the areas not joined across 2014 and 2015);
  - `docs/methods/desnz_gb_regional_gas_consumption_annual.md` (Great Britain's gas by region, public; weather corrected, gas years, the domestic band).
- **Two faults in the check script, none in the notes:** a first assertion matched `meters_non_domestic` as if it were `meters_non_consuming`, and the Energy Trends lookup read generation in place of capacity. Both were the script's; each was fixed and the check run again, with no difference.
- **With these, every held table outside the unlanded chains' eight has a note** (`runs/c135/undescribed.py`: 589 tables, 8 without, the same 8 as session 2690).
- **The Stanford draft:** three public tables uploaded, each proved by the draft's count:
  - `desnz_regional_renewable_capacity_annual` (3,157 rows);
  - `desnz_gb_regional_consumption_annual` (2,608);
  - `desnz_gb_regional_gas_consumption_annual` (1,966).

  How it ran:
  - A plain upload under the data lock (cap 130), the main checkout pulled first, from this branch merged with main (nothing new on main): `runs/c135/s2695.sh`, copied from chain 134's.
  - The metadata tables were proved whole: `erw_headers` 5,202 lines, `erw_coverage` 589 rows, `erw_sources` 679 rows.
  - Reconciles: before, 430 tables, 369 match, 58 differ, 3 not yet uploaded; after, 374 match, 56 differ (tables the daily runs have grown since their upload), none missing.
  - Requests: 8, 71 (with 1 to Supabase) and 8. **Nothing released.**
- **The upload record** (`warehouse/metadata/redivis_uploads_stanford.csv`) and the release note's paragraph go in with this report.

## Decisions made without you

- **Session 2698 run before this one,** so that its table is described and uploaded with the chain's others, and the upload ran before the daily run's lock at about 14:10.

## For Samuel's ruling

- **Releasing the draft,** as before: a person's click after the diff.

## Files

- New: three method notes; this report.
- Changed: `docs/coverage.md` (three Method cells), `docs/reviews/redivis-v1-release-note-2026-10-23.md`, `warehouse/metadata/redivis_uploads_stanford.csv`.
- On the data machine only: `runs/c135/s2695.sh`, `runs/c135/s2695/`, `runs/c135/s2695_check.py`, `runs/c135/s2695_note.py`, `runs/c135/cells.py`.
