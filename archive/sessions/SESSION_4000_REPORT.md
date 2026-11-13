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
  - Test 4000, 15 tests.

## Row 9 of the old laptop

(written when the gate ends)

## Decisions made without you

- Chain 228's next file is 230, not 229 (window 3 took 229).
- The precheck runs from the main checkout (it writes only untracked files there); it relabelled the machine's duty from window A's "session 3872" to this session.
- 12 November's root causes stand in their own file, so the daily run's own `2026-11-12-health.md` does not conflict.
- The batch runner is the gate's default only below 12 GB; the desktop and GitHub's runner keep one process.

## For Samuel's ruling

- None new yet.
