# Session 3933 report: the Redivis draft and the records

Energy Research Warehouse (ERW). Chain 267, data machine (lab-desktop), 14 November 2026, 10:39 to 10:42 UTC. Opus 5.5. Model spend USD 0. Requests: Redivis's API only, one `upload.py --tables` run of three tables (about 46 by session 3902's count of 28 plus 6 a table); no publisher.

- **Uploaded to the warehouse's own drafts** (under the data lock, in the foreground): `large_load_connection_rules` 87 rows (Redivis count 87), `battery_stack_monthly` 11,634 (11,634), `price_years_by_window` 2,754 (2,754); `erw_headers` 2,819 lines (35 for the three). **Nothing released.**
- **Not uploaded:** `eia930_daily_total_interchange`. This machine's copy has the 2025 fill but lacks 10 to 12 November (EIA's API ends at the 9th today); the daily run rebuilds it with the branch's code once land-c merges.
- **The Stanford draft:** not asked. `large_load_connection_rules`' ERW verdict is unsettled, which the uploader refuses (sessions 3853 and 3869); the two derived tables are already there as the daily run keeps them.
- **The records:** `redivis_uploads.csv` moved onto the branch, the main checkout put back after `lock.py status` read the lock free. `build_tables.py --check` exit 0; tests 410, 275, 1008, 1009 and 1001: 38 passed (364 subtests); `build_llms.py --check` exit 0 after the last coverage row.
- **Seen in `sync.py --check`** (10:19 to 10:27 UTC): 648 tables, 0 missing, 8 behind (the deal and datacenter tables and the news tables, which the laptops and the daily run write), 4 diverged (`api_cost_ledger`, `eia930_daily_total_interchange`, `grid_network_links`, `price_board_latest`), 4 ahead (`energy_projects`, `ercot_interconnection_queue`, `ercot_peak_premium_monthly`, and `large_load_connection_rules`, now uploaded). Not restored: `--refresh` would overwrite this machine's newer copies.

## Decisions made without you

- **The interchange table waits for the daily run's build** rather than putting a copy without 10 to 12 November on the draft.

## For Samuel's ruling

- **Three tables are newer here than on Redivis** (`energy_projects` 39,939 rows against 39,917, `ercot_interconnection_queue` 1,758 against 1,736, `ercot_peak_premium_monthly` 23,856 against 23,688): `sync.py` says to upload them or they are lost with this machine. Default: left for the runs' session (3934) to read why before an upload.
