# Session 2066 report: method notes for this chain's tables, and the Stanford draft

23 October 2026, from 20:42 UTC, on lab-desktop (the data machine), a session of `queue/done/066-day-25-october-data-disasters-loans-drought-assistance.md`. Model spend USD 0. Pulls: Redivis's API, 93 requests of 150 (6, 7, 73 and 7; the first reconcile's 6 were cut by a cap of 6, which a read-only reconcile can bear), and 1 to Supabase for the lock.

## Read these first

- **Four method notes,** each with its `Tables:` line and its Method cell (`runs/c057/method_cells_locked.sh`): `docs/methods/fema_disaster_declarations.md` (26,199 rows, 1,634 declarations, declared 7 January 2015 to 17 October 2026), `usdm_drought_state_weekly.md` (177,696 rows, 48 states, 617 weeks), `nhc_hurdat2_track_points.md` (27,812 fixes, 973 storms: 459 Atlantic, 514 Pacific; 509 landfalls), `nrc_license_actions.md` (236 events: 63 renewals issued, 1 withdrawn, 172 uprates). Written by a helper agent in the chain's worktree, checked here: its counts are the sessions' own and the tables', no em or en dash.
- **Contradictions found in this chain's connectors, each acted on, the four tables written again** (validated, archived, their coverage rows replaced by key) so their headers say the corrected words:
  - `fema_disasters.py`: a county's FIPS is in `entity_ids` only where FEMA names a county (913 rows hold the state alone); description and header now say so.
  - `usdm_drought.py`: the overlapping week was the 2023 span's (the map of 27 December 2022), not "every span's"; and the header said "License: public" while the verdict is not settled; both corrected.
  - `nhc_hurdat2.py`: the fixes are not all six-hourly (502 rows fall at other hours, 429 of them landfalls); the header's storm name is kept, not checked; a negative wind is blanked as -999 pressure is; all said.
  - `nrc_license_actions.py`: status is issued, withdrawn or approved; types include E(1); the renewal table's columns are read by position; an uprate's accession number keeps its mark; both addresses now redirect on www.nrc.gov. Session 2064's "64 renewed licenses" counts Crystal River's withdrawn application among them: 63 issued.
- **The pause check added to the nine connectors chains 057 and 066 wrote** (`eia_ice_electricity`, `eia_mecs`, `eia_buildings`, `eia_lng_liquefaction`, `lbnl_tracking_the_sun`, `fema_disasters`, `usdm_drought`, `nhc_hurdat2`, `nrc_license_actions`): CLAUDE.md asks every connector that reaches a publisher to ask `paused_sources.csv` first, and none did. Each now asks `ip.paused` and `ip.paused_host` as `boem_ogor.py` does; the session tests of both chains pass.
- **The Stanford draft:** a first reconcile (7 requests) found every table of chain 057 in the draft and current, chain 057's rewritten `eia_cbecs_commercial_buildings` there with its old ids (same count), and `erw_coverage` at 401 rows (chain 067's upload at 20:30). **Four tables uploaded, each proved by the draft's count:** `eia_cbecs_commercial_buildings` (5,944, its joined ids), `fema_disaster_declarations` (26,199), `nhc_hurdat2_track_points` (27,812) and `nrc_license_actions` (236), in one plain upload (73 requests, under a cap of 100) that refreshed `erw_coverage` (401) and `erw_sources` (489) and rebuilt `erw_headers` (3,890 lines, keeping 121 lines of 12 tables not on this branch). `usdm_drought_state_weekly` is unsettled, so the target does not take it. The last reconcile (7): 251 of 295 match, 44 differ (tables a daily run has grown), none missing. The draft's header lines for FEMA, NHC and the NRC are the first writes' (the rewrites changed header words, not rows); the next plain upload takes the new ones.
- **The release note extended** (its session 2066 paragraph). Nothing released.

## Errors

- **The first reconcile's cap of 6 was too few** (the draft has more tables than at session 2024): read-only, so the cut did no harm; run again with room.
- **The rewrites' metadata patches conflicted** (made against a main without this chain's rows); the rows were replaced by key (`runs/c066/s2066/replace_rows_many.py`), no key twice.

## Decisions made without you

- **The pause check added as code** (a connector's rule, not a figure), in the nine connectors written today only; the other connectors without it (four CAISO ones, session 2060) are for a code chain.
- **The tables written again** for their headers' words; no row changed.

## For Samuel's ruling

- None new.

## Files

- New: the four notes above, this report.
- Changed: the nine connectors above, `docs/methods/usdm_drought_state_weekly.md`, `docs/reviews/redivis-v1-release-note-2026-10-23.md`, `docs/coverage.md`, `coverage.csv`, `archive_manifest.csv`, `warehouse/metadata/redivis_uploads_stanford.csv`.
- On the data machine only: `runs/c066/s2066/`.
