# Session 3791 report: the next file, the landing, the queue

Energy Research Warehouse (ERW). Chain 212, session 18 of 18, data machine (lab-desktop), 12 November 2026 from 14:12 UTC. Opus 5.5. Model spend USD 0.

## The gate

- **First gate, `706c13d7c`** (14:13 to 14:31 UTC): the suite failed one test of 8,374, `test_session3298` (`package/llms.txt` older than coverage's newest row). The catalogue had been rebuilt before session 3781's `nuclear_fleet_status` row. Rebuilt in `d3f9b3956`; test 3298 passed.
- **Second gate, `d3f9b3956`** (14:32 to 14:58 UTC):
  - the suite passed (8,374 tests);
  - check-values failed on 17 checks: the 3 known floors, and 14 new ones, all `allgrids|forecast|ercot:*`: the page showed "0" for ERCOT's 0.4 MW revision.
  - Fixed in `2af7ce758`: the line shows one decimal under 10 MW.
  - My report commit (`3afa68dc3`) moved the branch while the gate ran, so its hand-check step looked for the wrong worktree (`gate_held.sh` reads the branch's head afterwards). The lesson, kept: nothing is committed to a branch while its gate runs.
- **Third gate, `2af7ce758`** (14:59 to 15:25 UTC, `runs/land_check/2af7ce75863d03c7c9e9f854ec705699b6031d33.txt`):
  - freeze, main merged, task branches, db probe, build lock, worktree: pass;
  - **suite: pass, 8,374 tests (361 skipped)**; ask_replay, npm ci, build, serve: pass;
  - check_values: only the 3 known floors fail (`/deals` 1 checked number and 1 held, floor 10; `/learn/problems/know-your-grid` 0, floor 10; `/digest` 0, floor 9). `cv_diff`: "3 failures, 3 known, 0 new".
  - The hand checks were run on the gate's own build, served again on port 3214 (15:32 to 15:38 UTC), because the script's relative output folder kept its server from starting:
    - check-routes: 1 live page and 225 in review, 0 failed;
    - check-cross-checks: 92 of 92;
    - check-csp: 97 pages, 0 violations.
  - The tab's new line read on that build at 1280 and 390 px in the internal view: 48 rows, 48 with a figure, 0 "not held".

## The landing

Never between 14:00 and 16:15 UTC: the push waits for 16:15. Written below.

## The next file

`queue/next/215-day-13-november-data-continued.md`: its "Sessions 3793 to 3797" filled from chain 212's note (`runs/c212/update_215.py`), pushed alone after the landing. Written below.
