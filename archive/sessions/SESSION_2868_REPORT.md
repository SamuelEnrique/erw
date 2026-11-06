# Session 2868 report: the map tracker and the policy games landed

6 November 2026, about 00:12 to 01:02 UTC, on lab-desktop (the data machine), chain 147, unattended. Model spend USD 0. Pulls: none but the snapshots and GitHub reads.

## Read these first

- **`wip/2300-map-tracker` landed as `f6279cc9d`.** It gives the project map's figures keyed with their source tips (session 2300).
  - Gate `3bf436ce`: suite 7,519 OK; check-values had 12 failures, all known, 0 new.
  - Task branch run 42135229891 passed at 00:30 UTC.
  - Snapshots `s2868a-before` and `s2868a-after`: **0 differences**.
- **`wip/2400-policy-games` landed as `07a5a6ccb`.** It brings the policy monitor's counts keyed, the paused sources said in place, the battery game's end table and fleet lines with their hovers, the bill calculator's table in its own scroll container, and the method notes (sessions 2400 to 2404).
  - **The first gate failed in the suite on three older tests the branch's own changes had made stale:**
    - `test_session157_page`: the view reads the new `paused.json` too.
    - `test_session188_waits`: the prebuild now also runs `build-paused.mjs`.
    - `test_session289`: the words "fleet of ... homes" now carry a hover.
  - The tests were brought to what the branch builds (`2f93dec6`'s parent). 43 tests pass, and the next gate's suite passed: 7,547 OK.
  - **That gate's check-values had 16 failures: the 12 known and 4 on `/grid/caiso`.** The interconnection queue's hybrid and storage counts and MW moved by one request (149 to 148 hybrid, 92 to 93 storage) between the build's read and check-values' read. The daily run of 22:19 UTC was loading the live set at that hour. The branch touches no grid, CAISO or queue file.
  - Task branch run 42139538413 passed at 01:00 UTC, its own check-routes against the live site included.
  - Snapshots `s2868b-before` and `s2868b-after`: **0 differences**.
- **The games' pages at 390 and 1280:** taken from session 2869's kept build, which includes this branch (see that report).
- **Branches on origin:** both are ancestors of main. Their deletion is left for the owner (refused by this machine's permission settings).

## Decisions made without you

- **The stale tests were updated, not skipped.** Each still holds the page to what it shows.
- **Landed past the four `/grid/caiso` lines,** as data moving under a check (above), not a fault of the branch.

## Files

- New: this report.
- On the data machine only: `runs/c147/fix_2400_tests.py`, `runs/c147/land_2300.out`, `land_2400*.out`.
