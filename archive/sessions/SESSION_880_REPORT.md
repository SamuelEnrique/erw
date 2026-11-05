# Session 880 report: the Stanford draft's grown tables and its metadata

23 October 2026, from 03:54 UTC, on lab-desktop (the data machine), a session of `queue/done/047-night-23-october-data-utilities-plants.md` (run before session 879, as the chain's file says). Model spend USD 0.

## Read these first

- **The draft now holds `ercot_wind_solar_hsl_hourly` empty (0 rows): my fault, to be mended first.** Its true replace deleted the draft's copy and the request cap stopped the upload before the new copy was sent. Nothing is released, so no reader sees it; the next Redivis session uploads it before anything else (`upload.py --target stanford --prove-by-listing --tables ercot_wind_solar_hsl_hourly`, about 5 requests). Chain 048's file says so. A cap should stop between tables, not inside one; the counter used here (`runs/c047/s880/counted.py`) refuses mid-table.
- **Refreshed and proved by the reconcile:** five of the smallest tables the daily run had grown (`ercot_wind_solar_hsl_daily`, `energy_companies`, `ercot_wind_solar_forecast`, `eia_retail_fuel_prices`, `frb_treasury_yields`); `eia_coal_receipts_annual` with its header lines now in `erw_headers` (2,958 lines); `erw_coverage` (316 rows) and `erw_sources` (416 rows), refreshed by a plain upload.
- **The reconcile:** 176 of 214 tables match; 37 differ because the daily run has grown them since their upload, and `ercot_wind_solar_hsl_hourly` is empty (above).
- No sign was found that the owner had released the draft as it stands, so the refresh went ahead (the chain's condition).

## Pulls against their ceilings

| Host | Requests | What |
|---|---|---|
| redivis.com | 97 of 100 | five small tables sent and a sixth begun (34), the plain upload of the coal receipts with the header and metadata tables (57), the reconcile (6) |
| Supabase | 2 | the data lock's checks |

## Decisions made without you

- The smallest grown tables first, so that a cap would leave the largest for later; the plain upload chosen for the receipts, as it also refreshes the metadata tables.

## For Samuel's ruling

- None new; do not release the draft before `ercot_wind_solar_hsl_hourly` is uploaded again.

## Files

- New: this report. Changed: `warehouse/metadata/redivis_uploads_stanford.csv`. On the data machine only: `runs/c047/s880/`.
