# Session 661 report: the public tables, uploaded to the Stanford draft (the first batch)

22 October 2026, from 08:51 UTC, on lab-desktop (the data machine), a session of `queue/done/043-night-23-october-data-redivis-gaps.md`. Model spend USD 0.

## Read these first

- **72 public tables and `erw_headers` are in the draft of `datapages.erw:b9wm`**, each proved: the draft's row count equals the CSV's data rows for every one. Nothing was released. The draft was opened by the first upload (Redivis's `next` version over the released v1.0, whose starter table stays as it was).
- **The uploader has a second target**, `upload.py --target stanford` (`config.yaml`, `targets`): the Datapages dataset, its own manifest (`warehouse/metadata/redivis_uploads_stanford.csv`), and a gate that refuses any table whose ERW verdict in `docs/licenses.md` is not `public` before anything is read or sent. The default target, which the daily run uses, is unchanged.
- **The proof is read from listings of the draft** (`--prove-by-listing`). The client waits on each upload by asking every two seconds, about 13 requests a table: the 186 tables would have taken about 2,400 requests against the three sessions' 1,200. Sent without waiting, a table costs 3 requests under 1 MB and 5 above; the draft is then listed every minute until every table's rows match, and an upload that failed is removed. Tests: `tests/test_session661.py` (8).
- **The batches changed from the plan's, for the ceiling, not for storage:** 661 took the 72 smallest (four in the trials, 68 in the batch); 662 takes the next 66 (1.10 GB); 663 the last 48 (12.05 GB, the largest) and the metadata tables.
- **The reconcile** (`--target stanford --reconcile`, read only): 72 of 72 uploaded tables match their CSVs, 0 mismatch, 116 not yet uploaded (not asked); the one table in the draft with no CSV here is the starter, `eia930_iso_hourly_demand_2019_2025`. 4 requests.

## Pulls against their ceilings

| Host | Requests | What |
|---|---|---|
| Redivis API | 370 of 400 | three trials (25, 35 and 33: one table waited on, one waited on with its trace, two proved by listing), the batch (273), the reconcile (4) |

## Decisions made without you

- The proof by listing, in place of the client's wait on each upload (the ceiling); each table is still proved against its CSV, and a table that never matches is reported failed.
- The batches regrouped by request cost: 72, 66 and 48 tables.
- Under a target, `--reconcile` does not ask about a table its manifest says was never uploaded there (it is listed "not uploaded"), so a reconcile between batches costs a few requests, not one a table.

## For Samuel's ruling

- None new. The three of session 660 stand (the daily run's target, the starter table, Datapages' storage).

## Files

- Changed: `warehouse/redivis/upload.py`, `warehouse/redivis/config.yaml`. New: `warehouse/metadata/redivis_uploads_stanford.csv`, `tests/test_session661.py`, this report. On the data machine only: `runs/s661/` (the counted runs, the batch lists, the reconcile file).
