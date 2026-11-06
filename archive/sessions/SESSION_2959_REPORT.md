# Session 2959 report: the landing request file, the Stanford draft

6 November 2026, about 08:45 to 09:04 UTC, on lab-desktop (the data machine), chain 157 (the owner's), unattended. Model spend USD 0. Pulls: Redivis's API only (a plain upload of five tables, then one reconcile), within the 150 allowed.

## Read these first

- **The landing request file:** not on origin's main. No laptop branch to land.
- **This chain's four public tables are in the Stanford draft** (`runs/c153/upload_stanford_2959.sh`, session 2929's script for this branch). It ran as a detached process under the data lock (taken 08:46 and released), with the branch's license record and coverage copied in and main's put back. Each table was counted equal:
  - `generator_pipeline_by_grid`: 5,147 rows;
  - `iso_queue_snapshot_summary`: 570;
  - `nuclear_fleet_status`: 15,048;
  - `gas_balance_weekly`: 40,507;
  - `erw_headers`: 5,628 lines (43 for the four).
  - "uploaded 5 of 5 tables to the draft of erw:b9wm (target stanford); nothing released".
- **The upload record:** `redivis_uploads_stanford.csv`'s four rows went to the branch as a patch (applied cleanly), and main's file was put back.
- **`--reconcile`, after:** 469 tables, 385 match, 83 differ by the days since their last upload. The reconcile reads main's coverage, which holds the four only once this branch lands, so it lists them as "Redivis tables with no CSV here", as session 2882 found for its own.
- **The release package:** the four stay held from v1, prepared before them (`release_v1.STORAGE_HELD`, now "in the Stanford draft since 6 November ... in v1 when the owner adds it to the package's list"). `release_v1.py --check`: 0 differences. Tests 275 and 410: OK.
- **`docs/state/redivis_v1_ready.md`** updated with the upload. **Nothing released.**

## Decisions made without you

- **The four left out of v1's list** (136 tables), so the package the owner reviews does not change without his choice.

## For Samuel's ruling

- **Whether to add the four derived tables to Redivis version 1** before the click.
