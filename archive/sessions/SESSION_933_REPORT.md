# Session 933 report: the Stanford draft, chain 052's seven tables and the draft's metadata

23 October 2026, 10:25 to 10:30 UTC, on lab-desktop (the data machine), a session of `queue/done/052-day-23-october-data-world-oil-reactors-stocks.md`. Model spend USD 0. Pulls: Redivis's API, 92 requests of 150 (and 1 to Supabase for the lock check).

## Read these first

- **Chain 051's tables were all in the draft** (session 919), so this session began with this chain's.
- **Seven tables uploaded to the Stanford draft in one plain upload, each proved by the draft's count:** `eia_world_oil_gas_annual` (448,267 rows), `eia_world_oil_monthly` (541,215), `nrc_power_reactors` (130), `wb_commodity_prices_monthly` (11,139), `eia_power_fuel_stocks_monthly` (48,702), `ornl_hydropower_relicensing` (559), `ercot_node_planned_generation` (569).
- **The plain upload also refreshed the draft's metadata,** as the next file asked: `erw_coverage` (353 rows, from 316) and `erw_sources` (451, from 416), and rebuilt `erw_headers` in full from disk (3,335 lines; the lines of tables not on this machine kept as the draft had them).
- **86 Redivis requests for the upload,** one run under a cap of 140, no cap inside a table.
- **The reconcile (6 requests): 214 of 252 tables match; 37 differ, none is missing from the draft.** The 37 are tables a daily run has grown since their upload (CAISO's, EIA-930's, ERCOT's prices and storage tables, the carbon intensity and weather tables, `nrc_reactor_status` and the rest); `erw_coverage` and `erw_sources` now match.
- **For the upload, the main checkout ran with the branch's `coverage.csv`, `sources.csv` and `docs/licenses.md`,** since chain 052's tables and session 928's verdicts are not on main yet. Main's files were restored after, and the upload record (`warehouse/metadata/redivis_uploads_stanford.csv`) carried to the branch as a patch.
- **The release note extended** (`docs/reviews/redivis-v1-release-note-2026-10-23.md`, session 933's paragraph). Nothing released.

## Decisions made without you

- **A plain upload, not `--tables`,** so that the two metadata tables and the header lines came with the seven in one run.

## For Samuel's ruling

- None new. The release note's "click" list stands: every public table of chains 048 to 052 is in the draft.

## Files

- New: this report.
- Changed: `warehouse/metadata/redivis_uploads_stanford.csv`, `docs/reviews/redivis-v1-release-note-2026-10-23.md`.
- On the data machine only: `runs/c052/s933/`.
