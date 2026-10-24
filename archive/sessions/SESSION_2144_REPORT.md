# Session 2144 report: the Stanford draft

24 October 2026, from 00:40 UTC, on lab-desktop (the data machine), chain 090, unattended. Run after the merge of origin/main (chains 069 and 079), so that the metadata tables it refreshes hold every landed chain's rows. Model spend USD 0. Pulls: Redivis's API, 98 requests of 150 (a reconcile, 7; the upload, 83 and 1 to Supabase; a reconcile, 7).

## Read these first

- **No table of chain 079 to reconcile first:** chain 079 uploaded its own (session 2130), as chains 068 and 069 did before landing.
- **This chain's six public tables uploaded, each proved by the draft's own count:** `wfigs_wildfires` (6,222), `gfz_kp_index_3h` (277,032), `epa_ghg_inventory_annual` (5,016), `scripps_co2_mlo_monthly` (1,636), `doe_lead_energy_burden` (160,419) and `afdc_station_counts_annual` (13,520).
- **The run** (`runs/c090/s2144/upload.sh`, session 2094's, run as a background process, so that the 10-minute limit of a foreground command could not stop it inside a table):
  - It held the data lock from 00:42:50 to 00:45:47 UTC.
  - It pulled the main checkout first, which was clean and fast-forwarded to `a1b02fd0`.
  - It copied in the branch's coverage, sources, license record and validator (the unit `ppm`, Decision 67) for the one run, and put main's back after.
- **The metadata tables refreshed from the merged branch:** `erw_coverage` 434 rows, `erw_sources` 521, `erw_headers` 4,131 lines (40 header lines of 4 tables not on this machine kept). Session 2130's upload had left `erw_sources` 10 rows behind main; that lag is closed.
- **The reconciles,** read against the main checkout's coverage (which does not yet list this chain's tables, so they are counted as "Redivis tables with no CSV here"):
  - before: 321 tables, 275 match, 45 differ, none missing;
  - after: 274 match, 46 differ (tables daily runs have grown since their upload), none missing.
- **The draft also holds chain 092's `afdc_ev_charging_state_annual`.** Its EV columns repeat part of this chain's `afdc_station_counts_annual`, from the same AFDC workbook; it is left for the owner's ruling, and chain 092's agent agrees.
- The release note (`docs/reviews/redivis-v1-release-note-2026-10-23.md`) is extended. **Nothing released.**

## Decisions made without you

- **The upload after the merge, not before.** An upload from the unmerged branch would have refreshed `erw_coverage` without chains 069 and 079's tables, as chain 079's own upload did for chain 068's.
- **Both AFDC tables in the draft,** pending the ruling.

## For Samuel's ruling

- The Redivis click (nothing released).
- `afdc_station_counts_annual` and chain 092's `afdc_ev_charging_state_annual` (keep both, or drop one, or drop the EV part of one).

## Files

- New: this report.
- Changed: `warehouse/metadata/redivis_uploads_stanford.csv` (six rows), the release note.
- On the data machine only: `runs/c090/s2144/`.
