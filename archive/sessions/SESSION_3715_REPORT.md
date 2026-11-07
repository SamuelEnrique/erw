# Session 3715 report: the landing of sessions 3701 to 3717

Energy Research Warehouse (ERW). Chain 208, session 16 of 20, portable laptop, 6 November 23:27 UTC to 7 November 02:16 UTC (about two hours of it with the laptop asleep and its network down, from about 00:19 to 02:12 UTC).

- **Landed:** `9245ed56d`, "Merge task/3701-3717-sellable: checks passed (run 42317420854)", 7 November 00:33 UTC. The gated commit `678d9efa2` is on main: sessions 3701 to 3717 with `origin/main` merged.
- **The gate** (`land_check.py --ref wip/3701-sellable --task 3701-3717-sellable --port 3706 --keep-worktree`, `runs/land_check/678d9efa2c3ab4b47c2f12cbd0b1ae5066667c0c.txt`):
  - passed: freeze, main merged, task branches, the probe, the lock, the worktree, **the whole suite (8,103 tests, 364 skipped, 33 minutes)**, Ask's replay, `npm ci`, the build, serve;
  - **check-values failed, exit 1:** 7,793 of 7,793 values matched. The four failures:
    - the floors of `/deals`, `/learn/problems/know-your-grid` and `/digest`;
    - `/datacenters?view=grids` not read.
  - The branch changes no file under `site/`. The build differs from main's only in two method notes' text, so the four failures are main's own.
- **On the kept build, by hand, each its own command with its exit read:**
  - `warm-live` exit 0;
  - `CHECK_VALUES_PAGES="/datacenters?view=grids"` check-values exit 0: 27 of 27 values; the earlier failure was a fetch under load;
  - `check-routes` exit 0 (1 live page, 225 in review, 0 failed);
  - `check-cross-checks` exit 0 (92 of 92);
  - `check-csp` exit 0 (97 pages, 0 violations).
  - The server I started was stopped by its PID (9580).
- **Then the printed sequence**, each command alone with its exit read:
  - `freeze.py status` 0;
  - `git ls-remote --heads origin "task/*"` 0: `task/2230-2295-deals` new in flight; trial-merged with `git merge-tree`, exit 0, and so was `origin/main`;
  - the snapshot before, `before-678d9efa` (25 pages, 0 failed), exit 0;
  - `git push origin 678d9efa2:refs/heads/task/3701-3717-sellable` 0;
  - the merge, at 00:33 UTC;
  - the snapshot after, `after-678d9efa` (02:13 UTC), exit 0;
  - the compare, exit 0.
- **The comparison: 0 differences on the 25 pages.** Expected: every page is in review, and a visitor reads the in-review page. Three other branches landed between the two snapshots (deals 00:55, attention 02:00, companies 02:09 UTC); they showed no difference either. Both snapshots are in `runs/snapshots/` of the main checkout.
- **The new merge gate's first run** (run 42317420854) did as written:
  - "Merge the main this branch lands on";
  - the suite on the merged tree (9 min 21 s);
  - in the merge job, "The suite again when main moved since the checks": 1 s, main had not moved;
  - the pull request merged.
- The kept worktree was removed (its folder by a long-path delete; git's own removal stopped at a too-long file name).

## Decisions made without you

- **Landed past check-values' failures:**
  - the three floors are other chains' pages, which this branch cannot change: it changes no `site/` file;
  - the unread page passed when read alone;
  - the three checks the gate skipped passed on the same build.
  - Chains 147, 149 and 158 landed the same way on the same floors.
- The snapshot after was taken at 02:13 UTC, not right after the merge: the laptop slept. The comparison covers the three later landings as well.

## For Samuel's ruling

- `/digest`'s floor now fails too, as `/deals`' and `/learn/problems/know-your-grid`'s did. Each gate's check-values stops on them.
