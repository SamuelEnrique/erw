# Session 2929 report: the Stanford draft

6 November 2026, about 06:11 to 06:20 UTC, on lab-desktop (the data machine), chain 153, unattended. Model spend USD 0. Pulls: Redivis's API only: two reconciles (one listing of the draft each) and a plain upload of two tables with `erw_headers`, within the ceiling of 150. The branch had been merged with main first (`7ba70128`; main had not moved).

## Read these first

- **`--reconcile`, before** (`runs/s2929_reconcile1.out`): 469 tables, 384 match, 84 differ, 0 missing from the draft, 1 not yet uploaded to the target. `ercot_transmission_projects` differed (2,203 here, 2,122 in the draft); `ercot_node_transmission` matched in count, but its counts by county had changed.
- **Uploaded in a plain upload** (`runs/c153/upload_stanford.sh`, session 2882's script for this branch). It ran as a detached process, not in a shell's background, under the data lock (taken 06:16:49 and released). The branch's license record and coverage were copied in for the one run, and main's were put back.
  - `ercot_transmission_projects`: 2,203 rows, Redivis count 2,203.
  - `ercot_node_transmission`: 569 rows, Redivis count 569.
  - `erw_headers`: refreshed, 5,585 lines (19 for the two tables).
  - "uploaded 3 of 3 tables to the draft of erw:b9wm (target stanford); nothing released".
- **The upload record:** the change is in `redivis_uploads_stanford.csv`, not `redivis_uploads.csv`, so the script's patch was empty. The Stanford record's two rows went to the branch as a patch of their own (`runs/s2929_stanford_manifest.patch`, applied cleanly), and main's file was put back.
- **`--reconcile`, after** (`runs/s2929_reconcile2.out`): 469 tables, **385 match, 83 differ** (by the days since their last upload; the daily tables), 0 missing. Both of this chain's tables match.
- **Not uploaded:** `utility_large_load_tariffs` and `large_load_connection_rules` (the uploader refuses an unsettled verdict; both are in `release_v1.STORAGE_HELD`, session 2926).
- **`docs/state/redivis_v1_ready.md`** brought to what the draft holds: this chain's upload, the reconcile's figures and the new table held. **Nothing was released.**

## Decisions made without you

- **Only this chain's two changed public tables uploaded**, not the 83 that differ by days. Those are the daily run's uploads, and the release file says how to bring them current before the click.

## For Samuel's ruling

- None new.
