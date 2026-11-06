# Session 663 report: the public tables, uploaded to the Stanford draft (the last batch)

22 October 2026, from 09:10 UTC, on lab-desktop (the data machine), a session of `queue/done/043-night-23-october-data-redivis-gaps.md`. Model spend USD 0.

## Read these first

- **All 186 public tables are in the draft of `datapages.erw:b9wm`**, each proved against its CSV, with the three metadata tables (`erw_headers` rebuilt from every public table's header, `erw_coverage`, `erw_sources`). This session's 48 were the largest, 12.05 GB of CSV (`eia930_all_emissions`, 1.10 GB, the largest). Nothing was released.
- **No upload was refused for storage.** The Datapages organization holds the draft (about 12.4 GB by the old draft's ratio), so its limit is above the old account's 10 GB; what it is, the API does not say.
- **The reconcile after the batch:** 187 of 188 match (45,817,197 rows in all); `erw_sources` read 396 rows against Redivis's 395, because the reconcile read `sources.csv` while session 667's write had added a row to it for a moment. The file is back to 395 rows, so all 188 match the files as they stand.
- **The draft also holds the starter table** `eia930_iso_hourly_demand_2019_2025`, from v1.0, untouched.
- The proof took about 3 minutes after the last table was sent (09:38 to 09:41 UTC): Redivis processed every table in time.

## Pulls against their ceilings

| Host | Requests | What |
|---|---|---|
| Redivis API | 341 of 400 | the batch (336: 48 uploads, the proof's listings every two minutes, `erw_headers`, `erw_coverage`, `erw_sources`), the reconcile (5) |

## Decisions made without you

- The metadata tables went with this batch (a plain upload of the 48 tables names them), so `erw_headers` holds every public table's header lines.
- Sessions 666, 670 to 672 and 674 to 678's work ran while this upload was sending and processing, out of the chain's order; none shares a file with it.

## For Samuel's ruling

- None new; session 664 lists what to look at before the click.

## Files

- Changed: `warehouse/metadata/redivis_uploads_stanford.csv` (all 186 public tables; the metadata tables are not in the manifest). New: this report. On the data machine only: `runs/s663/` (the counted run, the reconcile file).
