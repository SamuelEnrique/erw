# Session 579 report: the landing gate in one script, without the push

Chain 034 (`queue/done/034-night-22-october-code.md`), samueloldlaptop, unattended, 22 October 2026. Branch `wip/579-s`, cut from `origin/wip/506-combined` (origin/main already in it).

## Summary

`scripts/land_check.py` runs the gate of a landing for one commit (a branch or HEAD), each step its own process with its exit code read, never piped: freeze status, origin/main merged, a trial merge with every remote `task/` branch in flight, the database probe, the build lock, the whole suite in a clean worktree of the commit, `npm ci` and the build (stopped after 30 minutes), the server, check-values with its resume (exit 3 resumed with `CHECK_VALUES_RESUME=1` until 0 or 1, at most three tries), check-routes, check-cross-checks, check-csp, and the server stopped by PID. One line a step goes to `runs/land_check/<sha>.txt`, each step's output to `runs/land_check/<sha>/<step>.out`. When every step passed it prints, and does not run, the freeze status, the `task/` listing, the before snapshot, the push, the after snapshot and the comparison, each as its own command. It never pushes, never takes a snapshot and never deletes a branch. 25 tests, every step stubbed; one test runs a tiny Python process through the real runner (exit code read, a timeout stops it). A bullet in `docs/machines.md`, "The landing gate". Not landed: the brief says session 589 lands the chain.

## What was done

- `scripts/land_check.py` (standard library only). Exits: 0 every step passed, 1 a step failed or the site is frozen, 2 bad input. Options `--ref`, `--task`, `--port` (3700), `--build-min` (30), `--lock-as`, `--worktree`, `--keep-worktree`.
- Steps beyond the part's list, all from the chain's landing rules and the memory notes: `main_merged` (git fetch, `merge-base --is-ancestor origin/main <sha>`), `task_branches` (`ls-remote`, then `merge-tree --write-tree` for each branch not on main; a conflict fails, a clean one is named), `duty.py beat` before the suite and each build, `warm-live.mjs` after the server starts (its exit noted only).
- The suite runs in the clean worktree before `npm ci`, as on GitHub's runner, with every variable whose name holds SUPABASE, ANTHROPIC, OPENAI, API_KEY, TOKEN, SECRET, PASSWORD, RESEND, REDIVIS or DB_URL taken out of its environment and `ERW_LOCK_EXEMPT=1`. `site/.env.local` is copied in from the main checkout only after the suite, for the build.
- check-values runs with its own state file (`runs/land_check/<sha>/check-values-state.json`) and `CHECK_VALUES_PAGES` unset (the landing gate is the full run). Exit 1 whose only failures are `FAIL | <page> | the floor |` lines on the ten pages of session 408's held list (session 415's report) passes only when each of those pages, read with the internal cookie, shows "license needed" and is not the in-review page; the line says so.
- The build: a log holding "statement timeout" is built once more; a second such log fails.
- The server: refused when the port is taken; stopped by its PID's process tree (`taskkill /T /F`), then any PID still listening on the port (`Get-NetTCPConnection`), never by a command-line match. Cleanup in a `finally`: server stopped, worktree removed (`git worktree remove --force`, no branch), build lock released only if this run took it.

## Checks

| Command | Exit | Result |
|---|---|---|
| `scripts/precheck.py --what "session 579"` (main checkout) | 0 | on duty |
| `ERW_LOCK_EXEMPT=1 python -m unittest tests.test_session579` | 0 | 25 tests OK |
| `ERW_LOCK_EXEMPT=1 python -m unittest tests.test_session579 tests.test_session301 tests.test_session498` and the 23 test files that read `docs/machines.md` | 0 | 472 tests OK, 5 skipped |
| `python scripts/land_check.py --ref nope-xyz` | 2 | "nope-xyz is not a commit", nothing written |
| `Ops().port_busy(3700)`, `Ops().listeners(3700)`, `task_name("HEAD")` | n/a | False, [], `579-s` |

No build, no whole suite and no real gate run: the part asks for stubbed tests, and a real run holds the build lock for up to two hours.

## Decisions made without you

- The gate stops at the first failing step, except freeze: a frozen site still gets every other step's result, and no push command is printed (it says to push to `wip/` instead).
- The build and the page checks run in the clean worktree after a fresh `npm ci`, not in the main checkout: the exact commit, no stale fetch cache, no other copy's incremental state.
- Added `main_merged`, `task_branches`, `duty.py beat` and `warm-live.mjs` to the part's list, from the chain's landing rules and the memory notes (sessions 139 and 251/258).
- A "statement timeout" build is retried once, automatically, under the same lock.
- The ten held floors are hard-coded with the reports that name them; the gate fetches each page to confirm "license needed" rather than trusting the floor line.
- Default port 3700 (no session number uses it); `--lock-as` lets a session already holding the build lock under its own name run the gate without waiting on itself.
- The record file is appended, a `#` header line a run.

## For Samuel's ruling

None.

## To finish

Nothing for this session. Session 589 lands the chain; its landing is the first real run (`.venv\Scripts\python.exe scripts/land_check.py --ref <combined branch> --lock-as s589`). A worst-case run (three check-values tries at 20 minutes each plus a 30-minute build twice) approaches the build lock's 3-hour stale limit; normal runs are well under.

## Files changed

- `scripts/land_check.py` (new)
- `tests/test_session579.py` (new)
- `docs/machines.md` (one bullet, "The landing gate")
- `archive/sessions/SESSION_579_REPORT.md` (this report)
