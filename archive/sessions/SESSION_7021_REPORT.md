# Session 7021 report: the desk's sixteen rows landed; where free energy is, replicated; the peak premium built daily; requests 13 and 18 finished

Energy Research Warehouse (ERW). Chain 301, data machine (lab-desktop), 16 November 2026. Opus 5.5. Model spend USD 0.

## The landing desk

- Gate j (`wip/c301-desk-b`, `e6ffcaa68`: old laptop rows 17 to 28, portable rows 34 to 37) passed every step: the suite (9,913 tests, 1,197 s), the replay, check-values (floors met), routes, cross-checks. Landed through `task/7020-desk` (run 43922473644, success 18:04:45 UTC), merged at `492752123`. Freeze: none. Snapshots `before-e6ffcaa6` and `after-e6ffcaa6`, the second after the deploy's status read success: **0 differences** (expected: every page is in review).
- The landing was pushed at 17:49 UTC while the data machine's own daily run was in its table steps, far from its commit (it holds the lock from 17:00 UTC).
- The sixteen rows marked landed in `docs/state/landing_request_oldlaptop.md` and `landing_request_portable.md`. Gate j's land worktree removed.

## The data machine's push, the same fault as the GitHub run's

- `warehouse/run_data_machine.sh` pushed once after its guard's suite, as the GitHub daily run did. A landing during that suite would lose the day's page files. The same retry now applies: a refused push rebases onto the new main and the guard runs again, up to three times; a conflict stops it (test 7020_push_retry, a second case).

## Where free energy is (the curtailment replication's fourth part)

- `replication/curtailment/free_energy.py`, written from the method note and the file's own statement of its rules (not from the builder): for 39 places of five grids, both windows (the month and the year, each grid's own standard-time window) and the heat maps. Real time is used where it holds 95 percent of the window's hours, an hour of 15-minute prices only when all four are held; a window under 95 percent is compared by its two counts.
- On the file of 15 November: **507 of 561 figures equal**; every difference is ERCOT's (38 figures), the 24 hours of 15 October filled after that file was built (Houston's one negative hour among them). The data machine's run of today rebuilds the file; it is compared again then.
- The method note now says what the replication covers and what it does not (SPP's shares, CAISO's shares before 2026, and the worth file).

## The ERCOT peak premium, rebuilt daily

- Found while replicating: the two peak-premium tables are built only by the GitHub daily run, whose call of the builder always skips (the hub history is not on the runner), so they stood at 21 October until session 7020 rebuilt them by hand.
- The builder gains `--split`: it splits the two consolidated families it reads, builds, and builds them back whatever the build did. A daily table step on the data machine (`dm_peak_premium`, after the nuclear fleet step) runs it; the two tables load daily and weekly. Tests 7020_peak_daily and 247 (28 steps).
- `replication/ercot_peak_premium/from_hourly.py` recomputes the new `ytd_` rows: **28,056 of 28,056** rows of the two tables equal at six decimals.

## Done-line requests finished

- **13:** with `wip/7507-peak-premium` on main, `replicate.py --write` on today's tables: 25,110 of 25,110 figures, 6,266 of 6,266 of the two-hub section; the two page-figure files committed and the note's quoted counts updated (test 7516).
- **18:** with `wip/7509-interconnection` on main, its replication taught request 17's rule (a status with no position is 0 MW, not "not held"): part A 823 of 823; part B every queue in full (CAISO 344, ERCOT 150, NYISO 408, MISO 132, SPP 384, ISO-NE 316). Tests 7509 and 7518 pass (they need `site/node_modules`; in a worktree a junction, removed after).

## Waiting for the data lock

- `runs/c301/lock2.sh`: the real-time storage table by duration class (request 31), and the two new tables, the peak premium per settlement point (request 35) and the fleet's offers by price (request 30), with their validation, coverage, archive and load. Their live-set rules are in the branch. Their license and release registrations follow the first write.

## Errors

- My free-energy script first read the windows from the wrong key and crashed; corrected before any figure was reported.

## For Samuel's ruling

- None new.
