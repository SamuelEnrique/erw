# Session 3309 report (chain 200, session 12 of the plan): the second landing

lab-desktop, 6 and 7 November 2026, 23:50 to 02:11 UTC. Landed `8a0dff6c6` as `0ee931c1b` (Merge task/3300-companies: checks passed, run 42326558862), deployed by Vercel at 02:10 UTC.

- **The gate** (`land_check.py --port 3330`, detached; it waited 70 minutes for the build lock behind three other windows' gates): freeze, main_merged, task_branches (chain 156's `task/2230-2295-deals` in flight, merging cleanly), db_probe, build lock, worktree pass; **suite pass** (8,048 tests, 375 skipped), ask_replay, npm ci, **build pass**; check_values exit 1: 7,816 of 7,816 values match Supabase; the floors of `/deals`, `/learn/problems/know-your-grid`, `/roundup` (0 of 0) and, new since 00:00 UTC, `/digest` (0 of 9: the new day's digest is not written yet). The same four failed in every gate after midnight (`b5a743f9`, `e1c6dd65`, `ff2898e9`): main's. check-routes, check-cross-checks, check-csp on the gate's own build (`runs/c200/rest_checks.py`, its own build lock, detached): **exit 0, 0, 0**.
- **check-companies.mjs** on the gate's build: 194 of 194, 1,306 figures read (fewer rows drawn since the fold).
- **Snapshots:** `s3309-before` (01:54:54) and `s3309-after` (02:10:42, after Vercel's `success`): 25 pages, **0 differences** (expected: every change is on pages in review).
- Freeze status exit 0 before the push; not between 14:00 and 16:15 UTC.

## Decisions made without you

- Landed with check_values' four floor failures, main's in every gate of the night, after running the gate's last three checks on its build (all passed).
- A background shell waiting for the build lock was stopped by Claude Code for low memory (about 3 GB free while other windows built); it held nothing. The wait was not restarted in a shell: the checks script took and released the lock itself, run as a detached process.

## Cost

- No model call. USD 0.00.
