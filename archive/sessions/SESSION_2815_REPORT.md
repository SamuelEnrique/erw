# Session 2815 report: method notes for chain 143's seven tables (133 figures checked); the Stanford draft takes all seven

26 October 2026, from about 05:35 to 05:52 UTC, on lab-desktop (the data machine), chain 143, unattended. Precheck passed (`runs/c143/pre2815.out`). Model spend USD 0. Pulls: Redivis's API only, 104 of 150 (and 1 Supabase request by the uploader). Run after session 2818, as file 143 asks.

## Read these first

- **Seven method notes, each checked by code against its table** (`runs/c143/s2815_check.py`: 133 figures, no difference left):
  - `docs/methods/eurostat_electrification_rate_annual.md`
  - `docs/methods/destatis_de_electricity_monthly.md`
  - `docs/methods/bfe_ch_electricity_wednesdays.md`
  - `docs/methods/czso_cz_regional_electricity_annual.md`
  - `docs/methods/eurostat_nuclear_fuel_cycle_annual.md`
  - `docs/methods/eurostat_ev_recharging_power_annual.md`
  - `docs/methods/eurostat_industry_electricity_annual.md`

  Each table's Method cell in `docs/coverage.md` now points to its note.
- **Contradictions found by the check, acted on:**
  - **Session 2818's list of country years differing by more than 5 per cent was short.** It named the Netherlands' 2017 only. The 11 are Estonia 2017 to 2020, Greece 2020, Georgia 2024, Italy 2021, the Netherlands 2017 to 2019 and Serbia 2020. The note and session 2818's report are corrected.
  - The industry note's first German figures were rounded; they are now the table's (chemicals 43,345,000 MWh, basic metals 31,682,000, food, drink and tobacco 17,953,000).
  - The nuclear note's licence line named `nrg_ind_nuc`, a typo for `nrg_inf_nuc`, corrected before the check.
- **No held table without a note** beyond the unlanded chains' eight (`runs/c143/s2815_undescribed.out`: 622 tables, 8 without a note).
- **The Stanford draft:** chain 143's seven public tables were uploaded and each proved by the draft's count:
  - `eurostat_electrification_rate_annual`, 38,269 rows;
  - `destatis_de_electricity_monthly`, 123;
  - `bfe_ch_electricity_wednesdays`, 11,154;
  - `czso_cz_regional_electricity_annual`, 360;
  - `eurostat_nuclear_fuel_cycle_annual`, 4,247;
  - `eurostat_ev_recharging_power_annual`, 1,171;
  - `eurostat_industry_electricity_annual`, 8,307.

  This was a plain upload under the data lock (cap 125), from chain 143's branch merged with main (main had not moved). The metadata tables were proved whole: `erw_headers` 5,525 lines, `erw_coverage` 622 rows, `erw_sources` 712 rows. **Nothing released.**
- **Reconciles:**
  - before: 462 tables, 395 match, 60 differ, 7 not yet uploaded (this chain's);
  - after: 404 match, 58 differ (tables the daily runs have grown since their upload), none missing.
- **Requests:** the before reconcile 8, the upload 89 (88 to Redivis, 1 to Supabase), the after reconcile 8. That is 104 Redivis requests of 150.
- **The release note** (`docs/reviews/redivis-v1-release-note-2026-10-23.md`) has a paragraph for this upload.

## Decisions made without you

- None beyond the notes' own (each table's session made its decisions).

## For Samuel's ruling

- The Redivis click: not yet. Chain 143's seven tables join the earlier chains' public tables in the draft.

## Files

- New: the seven method notes and this report.
- Changed:
  - `docs/coverage.md` (seven Method cells);
  - `docs/reviews/redivis-v1-release-note-2026-10-23.md`;
  - `warehouse/metadata/redivis_uploads_stanford.csv`;
  - session 2818's report (one correction).
- On the data machine only: `runs/c143/s2815.sh`, `runs/c143/s2815/`, `runs/c143/s2815_check.py`, `runs/c143/s2815_fix.py`, `runs/c143/s2815_note.py` and `runs/c143/cells.py`.
