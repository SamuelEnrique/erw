# Session 687 report: the Stanford draft's metadata, refreshed

22 October 2026, from 11:05 UTC, on lab-desktop (the data machine), a session of `queue/done/044-night-24-october-data.md`. Model spend USD 0.

## Read these first

- **`erw_coverage` and `erw_sources` in the Stanford draft now describe all 190 public tables**: `python warehouse/redivis/upload.py --target stanford --prove-by-listing grid_peak_vs_capacity` (from the main checkout, chain 043 having landed) sent `grid_peak_vs_capacity` again (56 rows) and then `erw_headers` (2,736 lines), `erw_coverage` (294 rows) and `erw_sources` (398 rows), each proved by the draft's own count. Nothing was released.
- **The reconcile was not run here:** the upload took 56 requests of the session's 60, and a reconcile takes 5. Session 688 runs it at the start of its own ceiling.
- The release note says so (`docs/reviews/redivis-v1-release-note-2026-10-23.md`).

## Pulls against their ceilings

| Host | Requests | What |
|---|---|---|
| Redivis API | 56 of 60 | the table, the proof, and the three metadata tables waited on by the client |

## Decisions made without you

- The reconcile moved to session 688 rather than pass the ceiling by one.

## For Samuel's ruling

- None new: the click (the release note's steps 2 to 5).

## Files

- Changed: `warehouse/metadata/redivis_uploads_stanford.csv`, `docs/reviews/redivis-v1-release-note-2026-10-23.md`. New: this report.
