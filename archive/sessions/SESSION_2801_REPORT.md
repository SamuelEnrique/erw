# Session 2801 report: method notes for chain 142's four tables (138 figures checked); the Stanford draft takes all four

26 October 2026, from about 03:35 to 03:53 UTC, on lab-desktop (the data machine), chain 142, unattended. Precheck passed (`runs/c142/pre2801.out`). Model spend USD 0. Pulls: Redivis's API only, 92 of 150 (and 1 Supabase request by the uploader). Run after session 2804, as file 142 asks.

## Read these first

- **Four method notes, each checked by code against its table** (`runs/c142/s2801_check.py`: 138 figures, no difference left):
  - `docs/methods/statat_austria_electricity_monthly.md`
  - `docs/methods/eurostat_household_electricity_annual.md`
  - `docs/methods/eurostat_data_centre_electricity_annual.md`
  - `docs/methods/eurostat_ev_recharging_annual.md`

  Each table's Method cell in `docs/coverage.md` now points to its note.
- **Two contradictions found by the check, acted on:**
  - **Session 2795's "imports and exports equal E-Control's in every month" was not right.** E-Control's whole-grid rows (`Importe | Ges`, `Exporte | Ges`) agree within the files' rounding (0.05 GWh) in 77 of the 86 month figures. Nine, all in 2024, differ by more: the largest is September 2024's imports, 3.6 GWh or 0.2 per cent; read as E-Control's later revisions. E-Control's public-grid rows (`Oef`) are smaller and are not the same measure. The note says so, and session 2795's report carries a correction.
  - **Session 2798's "370 zeros, mostly space cooling" was not right:** 291 are other end uses, 78 space cooling and 1 cooking. The note and session 2798's report are corrected.
- **No held table without a note** beyond the eight that session 2796 listed, five of them described on the unlanded chains' branches (`runs/c142/s2801_undescribed.out`).
- **The Stanford draft:** chain 142's four public tables were uploaded and each proved by the draft's count:
  - `statat_austria_electricity_monthly`, 793 rows;
  - `eurostat_household_electricity_annual`, 3,150;
  - `eurostat_data_centre_electricity_annual`, 85;
  - `eurostat_ev_recharging_annual`, 465.

  This was a plain upload under the data lock (cap 130), from chain 142's branch merged with main (`a533c328`). The metadata tables were proved whole: `erw_headers` 5,455 lines, `erw_coverage` 615 rows, `erw_sources` 705 rows. **Nothing released.**
- **Reconciles:**
  - before: 455 tables, 391 match, 60 differ, 4 not yet uploaded (this chain's);
  - after: 397 match, 58 differ (tables the daily runs have grown since their upload), none missing.
- **Requests:** the before reconcile 8, the upload 77 (76 to Redivis, 1 to Supabase), the after reconcile 8. That is 92 Redivis requests of 150.
- **The release note** (`docs/reviews/redivis-v1-release-note-2026-10-23.md`) has a paragraph for this upload.

## Decisions made without you

- E-Control's later 2024 figures read as revisions, both kept as published.

## For Samuel's ruling

- The Redivis click: not yet. Chain 142's four tables join the earlier chains' public tables in the draft.

## Files

- New: the four method notes and this report.
- Changed:
  - `docs/coverage.md` (four Method cells);
  - `docs/reviews/redivis-v1-release-note-2026-10-23.md`;
  - `warehouse/metadata/redivis_uploads_stanford.csv`;
  - sessions 2795's and 2798's reports (one correction each).
- On the data machine only: `runs/c142/s2801.sh`, `runs/c142/s2801/`, `runs/c142/s2801_check.py`, `runs/c142/s2801_note.py`, `runs/c142/cells.py` and `runs/c142/undescribed.py`.
