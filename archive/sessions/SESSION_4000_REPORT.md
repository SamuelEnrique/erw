# Session 4000 report: chain 228's ground, the old laptop's row 9, the root causes, the suite in batches

Energy Research Warehouse (ERW). Chain 228 (`queue/done/228-day-13-november-desktop-window2-landings.md`), the desktop's second window (the landing desk), 13 November 2026 from 09:25 UTC. Opus 5.5, high effort. Model spend under the owner's key: USD 0.

## Done

- **The chain file** `228-day-13-november-desktop-window2-landings.md` committed alone and pushed (`6a03f3dc8`), taken by name with chain 183's command `chain_queue.take(who='lab-desktop-window2', file=...)` in this window's worktree (`2c708547f`): `next --file` refuses a window's name on a data machine.
- **The next file** is `230-day-13-november-desktop-window2-landings-continued.md` (`76ceca05e`, renumbered `c7d10f01d`): window 3 pushed its own 229 seconds before.
- **Snapshots of the queue pushes:** `w2-q228-before` (09:30) and `w2-q228-after` (09:35, after `c7d10f01d`'s deploy showed success): 0 differences on the 25 pages.
- **Precheck:** passes from the main checkout. From a worktree it fails `daily_cap` (no ledger file there) and writes an idle row; the rerun put the machine back on duty, so no ready email follows.
- **Freeze:** none.
- **Memory and disk:** 5.4 GB free of 15.7 GB; disk 240 GB free.
- **Row 16 of the portable laptop** (`wip/3701-sellable`, session 4001's step) is already landed: its head `8d9a9dba2` and session 3718's three commits are ancestors of main through `task/3751-green` at `5a2193a1e` (12 November 11:14 UTC). The row is marked.
- **Root causes (roadmap item 6):** sections appended to `queue/summary/2026-11-06-health.md` to `2026-11-11-health.md`, and `queue/summary/2026-11-12-root-causes.md` (the bot writes 12 November's own summary today). With session 3718's, 30 October to 12 November are covered. Two stay open:
  - the board's spark spread (12 November 21:13 run; window A's session 3873 has it): the spread row and the file's gas row disagree by exactly 7 times a gas difference;
  - the Roundup's `api_cost_ledger` refusal of 8 November (3 rows short of the last upload).
- **The suite in batches (roadmap item 1):** `scripts/suite_batches.py` runs discover's tests in its order, at most N modules a process, and prints unittest's own closing lines.
  - A batch that dies is run again one module a process; a module that still dies is named as an ERROR.
  - `land_check.py` uses it automatically below 12 GB of memory, or with `--suite-batch N` (0 means one process).
  - `suite_gate.py --batch N` does the same for the guard's runner.
  - Test 4000, 16 tests.
- **The memory-heavy part found and fixed:** numpy's OpenBLAS commits a buffer for each thread when numpy is imported.
  - On the desktop's 20 threads, `import numpy, pandas` takes a process from 17 MB to 702 MB peak commit. With `OPENBLAS_NUM_THREADS=1` it is 91 MB.
  - Every suite process pays this, and so does every Python child a test starts. A profile of the first 263 modules, each run alone, gave a median peak of 708 MB.
  - `land_check.py` (`suite_env`), `suite_gate.py` (`clean_env`) and `suite_batches.py` now run the suite with the maths libraries on one thread (`ONE_THREAD`).
  - The laptops have fewer threads, so their saving per process is smaller but of the same kind. This is the likeliest cause of row 9's commitment-limit exits.
  - **The second profile, with the caps:** every module run alone; 1,088 modules; median 132 MB, 90th percentile 171 MB, maximum 526 MB (`test_periodicals`).
    - The five at 400 MB or more are in `scripts/suite_alone.txt`.
    - Two pytest-style modules print `NO TESTS RAN` when run alone. The runner now reads that line as a pass.
  - **The proof:** the whole suite through `suite_batches.py --batch 40 --alone scripts/suite_alone.txt`, 10:55 to 11:14 UTC.
    - **8,648 tests OK, 382 skipped**, the same counts as discover, in 35 processes and 1,148 s. One process takes 1,000 to 1,200 s.
    - The heaviest process peaked at 652 MB.
    - **An 8 GB laptop can run the gate's suite** once this lands.
    - The worktree took a merge of main while the run was under way. The list of modules is fixed at the start, and the counts match the profile's.

## Row 9 of the old laptop: landed at `3a82aebe4`

- **Branch:** `wip/1905-revert`, with `origin/main` merged at `428a0664f` and pushed to the branch, as the row asks. It holds the datacenter grids view's public columns back again until the owner rules (`datacenter-faults-2026-11-11.md` row 4, state `ruling`).
- **The gate** ran on the desktop (`runs/c153/gate_held.sh`, task `1944-revert`, port 3944), 09:34 to 10:04 UTC.
  - The suite: 8,633 tests OK, 382 skipped, 17 minutes. The two memory failures of the old laptop's gates did not recur here.
  - The build passed. check-routes passed; check-cross-checks passed all 92; check-csp ran 97 pages with 0 violations.
  - check-values had one failure: `/digest`'s floor, main's own. It failed in all 35 gates on this machine, and `cv_diff` found 0 new. Its cause and fix are under Done below.
- **The landing:**
  - Freeze none. Snapshot `w2-s4000-before` at 10:04.
  - Pushed to `task/1944-revert`. Run 43406357288 passed and merged at 10:32 (`3a82aebe4`). The deploy succeeded at 10:33.
  - Snapshot `w2-s4000-after`: **0 differences** on the 25 pages. This was expected: every page is in review.
- **The marks:** rows 9 and 16 were marked on main as `a2a3e9153`, with snapshots before and after: 0 differences.
- **Clean-up:** the worktrees `erw-w2-1905` and `erw-land-428a0664` were removed. The old laptop may delete `wip/1905-revert` on origin and its own worktrees.

- **`/digest`'s floor (main kept green, fallback c):** session 402 made `/digest` today's issue only. So before the daily run writes it (14:00 UTC), and at weekends, the page says so and carries 0 checked numbers, and its floor of 9 failed every morning gate.
  - `check-values.mjs` now writes a note for that floor when the page says `data-digest-none="pending"` or `"weekend"`.
  - A missed day still fails.
  - The rule is `noIssueToday` in `held-marks.mjs`, with tests 4000 and periodicals.
- **The 8 November ledger refusal**, traced further: the Roundup restored `api_cost_ledger` from the archive at 3,886 rows, 6 under the last upload.

## Decisions made without you

- Chain 228's next file is 230, not 229 (window 3 took 229).
- The precheck runs from the main checkout (it writes only untracked files there); it relabelled the machine's duty from window A's "session 3872" to this session.
- 12 November's root causes stand in their own file, so the daily run's own `2026-11-12-health.md` does not conflict.
- The batch runner is the gate's default only below 12 GB; the desktop and GitHub's runner keep one process.

## For Samuel's ruling

- None new yet.
