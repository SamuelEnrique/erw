# Session 7020 report: gate h landed; the lock's writes; the daily run's lost push fixed at the cause; the desk's sixteen rows

Energy Research Warehouse (ERW). Chain 301, data machine (lab-desktop), 16 November 2026. Opus 5.5. Model spend USD 0.

## The landing

- Gate h (`wip/c301-later`, `44d82be7a`: sessions 7014 to 7018, gate g's content, the eight tools at the done line) landed at 16:15 UTC through `task/7018-landing` (run 43905489885), merged at `0bd9c936c`. Freeze: none. Snapshots `before-44d82be7` and `after-44d82be7`, the second after the deploy's status read success: **0 differences** (expected: every page is in review).

## The daily run's commit, refused (fixed at the cause)

- The GitHub daily run of 16 November (43881234167) held the data lock from 14:10 UTC. Its own commit passed the push guard's suite (9,660 tests), and its one push was then refused ("fetch first"): my landing had merged at 16:37 UTC, during that suite. The day's metadata, docs and digests did not reach main, and its archive step, which follows the commit, did not run. So today's runner builds (`energy_projects` among them) are in the live set and not in the archive. The next run rebuilds them.
- **At the cause** (`wip/c301-last`): a refused push now rebases onto the new main and runs the guard again on the rebased commit before pushing, up to three times; a conflict stops it with a warning (test 7020_push_retry). Main still never gets a commit the suite has not passed. Until it lands, a landing must wait for the daily run's commit step (saved to memory).

## The lock's writes (`runs/c301/lock_all.sh`, under the data lock from 16:45 UTC)

- **32:** the map's file rebuilt from the archive's newest `energy_projects` (5 November, 3,684 queue positions); the live set holds today's runner build, which the archive does not hold (above), and refused the older load as it should.
- **4:** `ferc_eqr_party_mw` rebuilt with each party's place from `ferc_eqr_party_totals` (708 places moved, none blank). **20:** the stored summary waits: `ferc_eqr_contracts` on this machine is older than the live set's (18,135 rows against 18,989), so its load was refused, and the summary is stored only with that load.
- **6:** the register of source faults rebuilt (29 faults), its site copy written (test 118 passes).
- **8:** the research tables rewritten from the reworded files, the large-load page file rebuilt in the branch from its own notes (test 7200).
- **36:** the peak premium's annual table with `ytd_` (4,032 rows, 2,016 added).
- **31:** the awards table by duration class (1,244 rows). The real-time builder failed its own check against the awards table: the class rows made its pivot by month ambiguous. Fixed (the check reads the fleet's rows); its rebuild waits for the lock, which the data machine's own daily run took at about 17:00 UTC.
- The curtailment profile and the mix rebuilt again, with 8 March read since their builds.
- Everything validated (exit 0), covered, archived, loaded: profile 42 rows, peak premium 2,016, awards 992, mix 222, register 29 written. No snapshot was taken just before this load: the after-snapshot of the 16:40 landing came before it, and set against `after-load7020` it shows **0 differences**. The outputs were copied into `wip/c301-last` before the data machine's run could touch them in main.

## The landing desk

- Rows 15 and 16 (old laptop) and 33 (portable) were in gate e: marked landed at `f4cc50518`.
- The sixteen other requested rows (old laptop 17 to 28, portable 34 to 37) in one desk branch, `wip/c301-desk-b`. Conflicts:
  - `docs/methods/demand_growth.md` (twice): both sides kept.
  - `site/app/shoulder/page.tsx`: the old laptop's wording of the same sentence kept (its later head, its own test); the portable's test and its faults row follow it.
- Gate i failed on four errors: tests of different branches imported a `replicate` or a `from_hourly` of the same name from different replication folders, and in one suite process the first one loaded was reused. Five test files now import their own module fresh (757 tests that name a replication folder pass together). Gate j started at 17:14 UTC.

## Errors

- My first conflict resolver missed CRLF line endings and committed one merge with its markers still in; caught by the next merge, resolved and amended before any push.
- A copied gate script renamed `gate_held.sh` by a broad substitution; caught before the gate ran.

## For Samuel's ruling

- None new.
