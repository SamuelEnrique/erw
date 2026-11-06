# Session 2947 report: the Ask branch landed

6 November 2026, about 08:13 to 09:35 UTC, on lab-desktop (the data machine), chain 157 (the owner's), unattended. Model spend USD 0. Pulls: GitHub only.

## Read these first

- **The personal laptop's chain 152 landed as `1b4caf85f`** (task/2220-2226-ask, run 42193896198, checks passed 09:30 UTC, deployed 09:32). This is `wip/2227-ask`, which holds `wip/2220-ask` to `wip/2226-ask` and its report, merged with origin/main in its own worktree.
- **The merge's conflicts, resolved as the union:**
  - `eval_s1113.py`: the laptop's refactor (`grade_set(which, rules)`, `hold_answer`) is kept, with main's sets s1133, s1122 and s2918 beside its s2224. `grade_s1114(which, rules)` stays as a wrapper, so main's callers (test 2918) work. Test 2886 now reads `grade_set`'s source.
  - `runs.json`: the laptop's list with main's board run; `left_out` the union.
  - The three documents were written again from it; test 1147 counts 13 runs.
  - Ask's tests: 59 passed.
- **The gate, three runs:**
  - The first (`2808dc89`) failed one test of the branch's own code: `site/scripts/shots-2226.mjs` put the internal token in an address (`/internal/unlock?token=`), which test 301 forbids. It now opens the internal view through the form at `/internal/open` (browser.mjs's `unlockForm`). Test 301: 9 passed.
  - The second (`89aaf054`) stopped at `main_merged`: the code machine had landed again.
  - The third (`27053b99`): suite 7,750 OK; npm ci, build and serve passed; check-values 7,793 of 7,793 matched, its 2 failures main's known floors. check-routes, check-cross-checks (92) and check-csp (97 pages) were run by hand on the kept build.
- **Snapshots** `s2947-before` and `s2947-after`: 25 pages, **0 differences**.
- **Deleted, each an ancestor of main first:** `wip/2220-ask` to `wip/2227-ask` and `wip/2227-ask-land`; the workflow had deleted `task/2220-2226-ask`.
- **`docs/state/note_2026-11-06_portable.md`'s "Not landed" line** is answered with the commit.
- **The landing request file:** not on origin's main.

## Decisions made without you

- **`wip/2227-ask` landed rather than `wip/2226-ask`:** it holds 2226 and its report.
- **The token fixed in the branch's script** rather than the test loosened.

## For Samuel's ruling

- None.
