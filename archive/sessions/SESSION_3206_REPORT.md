# Session 3206 report: the data machine's page files, and its first run with the guards

6 November 2026, about 19:48 to 20:00 UTC, on lab-desktop (the data machine, its first window), chain 185, unattended. Model spend USD 0. Pulls: none.

## Read these first

- **This machine's run of 6 November** (17:00 to 18:14 UTC): 55 steps ok, and `dm_test_findings` passed. `dm_test_board` failed; chain 184 fixed it (test 132).
- **Why its page files broke main** (`e475f7069`, put back by chain 184 at `a96634458`): the datacenter page files gained about four days of new hours (built 2 November, then 6 November). Four tests hold committed files to figures recorded or computed another way:
  - **Test 190:** the hourly CSV agrees with the page files hour for hour (the exporter's own check passed). But once the hub's October was complete (720 of 744 hours, counted), the test compared the hub figure for the first time. The page counts the hub over 8,736 hours, the CSV's mirror over 8,735: the CSV's window ends at the zone's last real-time hour (2026-11-01T04:00Z), and October's last standard-time hour (05:00Z) is held at the hub only. The exporter's check exempts that edge (the window's first and last month), and the test does not.
  - **Test 1491:** the replication is held to a recorded `replication/datacenter/page_figures.json`; the refreshed files move four of its 14 figures.
  - **Test 538:** `check-cross-checks.mjs --files` holds the finding cards to the figures written in the methods notes' cross-check rows; the recomputed cards moved.
  - **Test 720:** the siting cards are the All grids tab's figures, and the tab reads the datacenter files. The run rebuilt those files and not the cards (`site/scripts/siting-card.mjs`).
- **The guard, on `wip/c185-data`:** `warehouse/run_data_machine.sh` gains `group dm_test_replication`. Its steps are datacenter page, export, carbon and the findings recompute; its tests are 190, 1491, 538 and 720; it puts back `site/data/datacenter`, `site/public/datacenter`, `site/data/findings` and `site/public/findings` whole when any test fails. A refresh that breaks them no longer reaches main. Test 3206 holds the group's steps, tests, files and place.
- **Not fixed here, for a later session:** the four tests' recorded figures and the CSV's window edge. Until they follow a refresh, the group keeps these files at their last good build, so the datacenter and findings pages do not refresh. That is visible, not broken.
- **The board group's put-back** restores tracked files only. The failed build's new `site/public/board/s/` files reached main with the run's commit (removed by chain 184's revert). Not changed here, because a `git clean` on those folders would also remove untracked files that other windows leave there.
- **The gate:** passed on `c3b4cfaf0` (main merged at 01:54 UTC on 7 November, under one hold of the build lock: `runs/c153/gate_held.sh`): suite 8,284 tests OK (360 skipped); ask replay, npm ci, build and serve passed; check-values 3 failures, all main's known (`cv_diff.py`: 0 new); by hand on the kept build, check-routes (225 in review, 0 failed), check-cross-checks (92 passed), check-csp (97 pages, 0 violations). Four earlier gates of the branch passed the same way (`3b057a759`, `101317b9c`) or stopped on main having moved (`eaf08c789`): each time main took another landing, three times other windows took the build lock in the seconds between the gate and the hand checks, and one wait for the lock took 1 hour 52 minutes.
- **The landing:** landed as `e65e232ad` (task/c185-data at `c3b4cfaf0`, run 42329411053, checks passed 02:40 UTC on 7 November, deployed 02:41), snapshots `s3218-land-before` and `s3218-land-after`: 25 pages, 0 differences.
- **The runner's run of 7 November** (the first with the board guard): tomorrow. Chain 193 and chain 204 read it.

## Decisions made without you

- **A guard, not a cure:** the group puts a breaking refresh back; reworking four tests' recorded figures is left to a session with the time.
- **No `git clean` in the put-back**, for the other windows' untracked files.

## For Samuel's ruling

- **The datacenter and findings pages will not refresh** while tests 190, 1491, 538 and 720 hold recorded figures: should those tests follow each refresh (their figures recomputed in the same run), or should the files stay frozen until a person reviews?
