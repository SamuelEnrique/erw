# Session 863 report: the Stanford draft, 14 tables up

23 October 2026, from 02:22 UTC, on lab-desktop (the data machine), a session of `queue/done/046-night-22-october-data-sources-gaps.md`. Model spend USD 0.

## Read these first

- **14 public tables uploaded to the Stanford Redivis draft (`datapages.erw:b9wm`), each with the true replace and proved by the draft's own count**, and their header lines merged into `erw_headers` (2,866 lines): chain 041's two never uploaded there, chain 045's three new tables and its rewritten `eia861m_utility_sales_monthly` (the draft now holds it without EIA's aggregates), and chain 046's eight. Nothing released.
- **The reconcile:** 160 of 205 tables match; the 45 that differ are the 43 a daily run has grown since their upload (as session 688 found) and `erw_coverage` and `erw_sources`, which only a plain upload refreshes (about 40 requests: a later session's). The release note says so (`docs/reviews/redivis-v1-release-note-2026-10-23.md`).
- **No new table entered the live set** (no ruling names one).

## Pulls against their ceilings

| Host | Requests | What |
|---|---|---|
| redivis.com | 99 of 100 | the 14 uploads and their proofs and the header merge (93), the reconcile (6) |
| Supabase | 1 | the data lock's check |

The uploads ran under a hard cap (`runs/c046/s863/counted.py`, `ERW_CAP`).

## Decisions made without you

- `--tables` (the tables and their header lines only) rather than a plain upload, so that 14 tables fitted the ceiling; `erw_coverage` and `erw_sources` wait.
- The smallest tables first, so that a ceiling reached mid-way would leave only the largest for later.

## For Samuel's ruling

- The click stands as the release note gives it (release the draft as it is, or refresh the 43 grown tables and the two metadata tables first).

## Files

- New: this report. Changed: `warehouse/metadata/redivis_uploads_stanford.csv` (14 rows), `docs/reviews/redivis-v1-release-note-2026-10-23.md`. On the data machine only: `runs/c046/s863/`.
