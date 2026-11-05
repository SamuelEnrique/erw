# Session 2829 report: method notes for chain 144's seven tables (115 figures checked); the Stanford draft takes its five public tables

26 October 2026, from about 07:07 to 07:23 UTC, on lab-desktop (the data machine), chain 144, unattended. Precheck passed (`runs/c144/pre2829.out`). Model spend USD 0. Pulls: Redivis's API only, 92 of 150 (and 1 Supabase request by the uploader). Run after session 2832, as file 144 asks.

## Read these first

- **Seven method notes, each checked by code against its table** (`runs/c144/s2829_check.py`: 115 figures, no difference left):
  - `docs/methods/eurostat_nonhousehold_bands_annual.md`
  - `docs/methods/eurostat_gas_import_origin_annual.md`
  - `docs/methods/eles_slovenia_hourly.md`
  - `docs/methods/hops_croatia_annual.md`
  - `docs/methods/eurostat_fossil_share_annual.md`
  - `docs/methods/eurostat_import_concentration_annual.md`
  - `docs/methods/eurostat_supply_diversity_annual.md`

  Each table's Method cell in `docs/coverage.md` now points to its note.
- **The check's one miss was its own:** the band sums' largest difference is exactly 0.01 (Italy 2022), which a float put a hair over the check's limit. The note's "within 0.01" stands, and the check's tolerance was fixed. No contradiction was found in the notes.
- **No held table without a note** beyond the unlanded chains' eight (`runs/c144/s2829_undescribed.out`: 629 tables, 8 without a note).
- **The Stanford draft:** chain 144's five public tables were uploaded and each proved by the draft's count:
  - `eurostat_nonhousehold_bands_annual`, 2,013 rows;
  - `eurostat_gas_import_origin_annual`, 1,253;
  - `eurostat_fossil_share_annual`, 1,279;
  - `eurostat_import_concentration_annual`, 6,497;
  - `eurostat_supply_diversity_annual`, 891.

  **The two internal tables,** `eles_slovenia_hourly` and `hops_croatia_annual`, wait for their publishers' terms and are not in the draft.

  This was a plain upload under the data lock (cap 125), from chain 144's branch merged with main (main had not moved). The metadata tables were proved whole: `erw_headers` 5,575 lines, `erw_coverage` 629 rows, `erw_sources` 719 rows. **Nothing released.**
- **Reconciles:**
  - before: 467 tables, 402 match, 60 differ, 5 not yet uploaded (this chain's);
  - after: 409 match, 58 differ (tables the daily runs have grown since their upload), none missing.
- **Requests:** the before reconcile 8, the upload 77 (76 to Redivis, 1 to Supabase), the after reconcile 8. That is 92 Redivis requests of 150.
- **The release note** (`docs/reviews/redivis-v1-release-note-2026-10-23.md`) has a paragraph for this upload.

## Decisions made without you

- **The internal tables left out of the draft.**

## For Samuel's ruling

- The Redivis click: not yet. Chain 144's five tables join the earlier chains' public tables in the draft.

## Files

- New: the seven method notes and this report.
- Changed:
  - `docs/coverage.md` (seven Method cells);
  - `docs/reviews/redivis-v1-release-note-2026-10-23.md`;
  - `warehouse/metadata/redivis_uploads_stanford.csv`.
- On the data machine only: `runs/c144/s2829.sh`, `runs/c144/s2829/`, `runs/c144/s2829_check.py`, `runs/c144/s2829_note.py`, `runs/c144/cells.py`.
