# Session 680 report: Redivis, the second pass

22 October 2026, from about 10:05 UTC, on lab-desktop (the data machine), a session of `queue/done/043-night-23-october-data-redivis-gaps.md`. Model spend USD 0.

## Read these first

- **The chain's four public tables are in the Stanford draft**, each proved by the draft's own count: `utility_service_territories` 11,893, `interconnection_durations` 3,098, `interconnection_durations_summary` 1,365, `grid_peak_vs_capacity` 56; their header lines are merged into `erw_headers` (2,736 lines). Nothing was released.
- **The reconcile after:** 190 of 192 match; the two that do not are the metadata tables, `erw_coverage` (290 in the draft, 294 now) and `erw_sources` (395, 398 now), uploaded by session 663 before these tables existed. Refreshing them costs about 40 requests, beyond what this session had left; the release note gives the one command, for after the landing.
- **The package for the click** (`docs/redivis/release-v1-stanford/`) is rebuilt: 193 tables in v1 with the metadata tables, none held; `--check` 0 differences. The release note of session 664 is extended with these tables.
- The summary table was first refused by the main checkout's validator, which does not know the unit `month` until this branch lands; it was uploaded with the branch's validator copied in for the run, and main's put back.

## Pulls against their ceilings

| Host | Requests | What |
|---|---|---|
| Redivis API | 78 of 100 | the three tables and `erw_headers` (36), the summary and `erw_headers` again (37), the reconcile (5) |

## Decisions made without you

- The upload ran from the main checkout with the branch's `docs/licenses.md`, `coverage.csv` and `sources.csv` (and, for the summary, its validator) copied in, since the uploader's gate reads the ERW verdicts there; main's files were put back after.
- `erw_coverage` and `erw_sources` were left as session 663 uploaded them rather than overrun the ceiling.

## For Samuel's ruling

- None new; the metadata refresh is listed under the release note's steps.

## Files

- Changed: `warehouse/metadata/redivis_uploads_stanford.csv` (190 tables), `docs/redivis/release-v1-stanford/README.md` and `tables.csv`, `docs/reviews/redivis-v1-release-note-2026-10-23.md`. New: this report. On the data machine only: `runs/s680/`.
