# Session 662 report: the public tables, uploaded to the Stanford draft (the second batch)

22 October 2026, from 09:04 UTC, on lab-desktop (the data machine), a session of `queue/done/043-night-23-october-data-redivis-gaps.md`. Model spend USD 0.

## Read these first

- **66 more public tables are in the draft of `datapages.erw:b9wm`**, each proved against its CSV (1.10 GB of CSV, the tables from 1 MB to 52 MB), with their header lines merged into `erw_headers`. Every upload succeeded; none was refused for storage. Nothing was released.
- **The draft now holds 138 of the 186 public tables.** The 48 largest (12.05 GB) are session 663's.
- **The reconcile** (`--target stanford --reconcile`, read only, after the batch): 138 match, 0 mismatch, 0 missing, 50 not yet uploaded (the 48 tables and the two metadata tables `erw_coverage` and `erw_sources`). The one table in the draft with no CSV here is the starter, `eia930_iso_hourly_demand_2019_2025`.
- **The proof cost more than session 661's estimate:** once the draft holds more than 100 tables, a listing takes two pages. 366 requests for the batch.

## Pulls against their ceilings

| Host | Requests | What |
|---|---|---|
| Redivis API | 371 of 400 | the batch (366: 66 uploads, the listings of the proof, `erw_headers`), the reconcile (5) |

## Decisions made without you

- Session 663's proof asks every two minutes, not every minute, for at most 90 minutes: its tables are the largest, and each listing is two requests.

## For Samuel's ruling

- None new.

## Files

- Changed: `warehouse/metadata/redivis_uploads_stanford.csv` (138 tables). New: this report. On the data machine only: `runs/s662/` (the counted run, the reconcile file).
