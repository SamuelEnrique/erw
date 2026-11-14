# Root causes of the failed scheduled runs of 13 November 2026 (UTC)

Written by session 4053 of chain 230 (the desktop's second window) on 14 November 2026 at about 02:45 UTC (fallback b, roadmap item 6).

**Sources:**
- `python warehouse/health.py summary --day 2026-11-13` run into a scratch folder: 6 failures. The daily run writes `2026-11-13-health.md` itself today, so this file stands beside it.
- The daily run's `daily-prices-log` artifact (run 43438591932).
- The two commits the push guard parked, `wip/red-daily-2026-11-13` (`7423bf708`) and `wip/red-dm-2026-11-13` (`70041bcb8`), with the failing tests rerun on each.

Nothing was rerun on a store, and nothing written to one.

- **`board_tests` (15:20 UTC):** tests 1118 and 1139 refused the built board's spark spread: 22.2287 in the spread row against 22.4387 recomputed from the file's own day-ahead and Henry Hub rows. That is exactly 7 (the heat rate) times 0.03, the same line as on 12 November (`2026-11-12-root-causes.md`). **Open:** window A's chain 226, session 3873.
- **`commit` and `health summary commit` (16:57 and 17:15 UTC), refused by the guard on test 3703:** on the parked commit the test lists six network figures the replication did not make, the first `series|eia930_all_demand|eia930:ERCO|demand_mw|2026-11-11T23:00:00Z`. The page reads each grid's demand in the hour it shows (`demandAt`); `replication/grid/replicate.py` did not. Fixed on main by window A's session 3888 (`97b2368fc`, 13 November 17:28 UTC), after the run had cut its commit. The parked commit's `replicate.py` lacks the 17 lines.
- **`package tests` (17:04 UTC):** `test_fetch_types_and_provenance[datacenter_tracker_rollups]` asks a table's header for a run log unless coverage marks the table derived (`package/tests/test_erw.py`, line 152). The rollups table, first written on 12 November (session 3775), is built from `datacenter_projects`, yet its header has no run log and its coverage row does not say `derived: yes`. **Open, the data machine's:** mark it derived, or write its run log line; window A's.
- **`dm_test_battery_dispatch` (the data machine, 19:19 UTC), test 178:** the group was put back. On the parked data-machine commit test 178 passes (44 tests with 314's file, one failure, 314's). Probably the machine's tree at 19:19 lacked a file that the morning's landing of the portable laptop's battery rows (`5fe21d6de`, 12:11 UTC) brought in, test 178's twelfth section. **Not reproduced.**
- **`dm_commit` (19:46 UTC), refused by the guard on test 314:** for MISO, the rule that finds each grid's tables no longer finds `iso_dam_hub_prices` or `iso_rtm_hub_prices` ("{'iso_dam_hub_prices', 'energy_projects', 'iso_rtm_hub_prices'} not less than or equal to {'energy_projects'} : miso"). MISO has been paused since 4 October (`docs/methods/miso_pause.md`), so its newest rows age out of those tables' windows. When the data machine rebuilds the grids' table list, MISO no longer has rows there, and test 314 still expects them. **Open, the data machine's:** the test should allow a paused grid's tables to drop out, or the list should keep a paused grid's tables by name.
