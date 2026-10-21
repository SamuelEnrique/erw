# Chain of 22 October 2026, night: session 563, code machine, unattended (chain 023's landing)

machine: code

Written by portable-laptop at about 23:15 UTC on 21 October, on the owner's instruction, by session 562. Session 562 merged the ten branches of chain 023 (429, 430, 497 to 505) and origin/main onto `wip/562-land-023`, then built and type-checked it. The owner stopped its check-values run at 30 of 152 pages (no FAIL by then) before the landing could finish. This file holds the one session that lands it. Queue file 025 (session 506) is a separate file and is not this session's.

## Session 563: land `wip/562-land-023` through the full gate

Long end 2:00. Precheck first (`.venv\Scripts\python.exe scripts/precheck.py --what "session 563"`). Read `archive/sessions/SESSION_562_REPORT.md` on `wip/562-land-023` first, all of it, and do its "To finish" in order, each command its own, never piped, each exit code read before the next. Work in a worktree of `wip/562-land-023` that has `site/node_modules`, `.env` and `site/.env.local` (a fresh worktree needs `npm ci` in `site/`; `docs/machines.md` says what else). Hold the build lock (`scripts/buildlock.py acquire s563`, on the branch) for the suite, the build and check-values, and run check-values alone on the machine: in session 562's first part it ran beside other checks, and ten page floors failed then that the full run on a quiet machine must explain.

The steps, as the report gives them:

1. Merge origin/main. Where both sides are new work, keep both, as session 562 did in `site/lib/supabase.ts`.
2. Run the whole suite. Only `test_session153` may fail (it fails on main too). Fix any other failure on the branch before going on.
3. Freeze status, `db_probe.py` at exit 0, the build, `tsc --noEmit`.
4. Run check-values in full against the built server (`CHECK_VALUES_TIMEOUT_MIN=90`). The only FAIL lines allowed are the known ones (the `/deals` floor under its hold, session 461's list). If the floors of `/map`, `/events` and its event pages, `/learn/bill`, `/research/card/gas_sets_price` or `/roundup`'s fetch fail again, run the same pages on a build of origin/main. A FAIL that main has too is main's: name it in the report. A FAIL that only the branch has is a fault: find it and fix it. Do not land on an unexplained FAIL.
5. Merge origin/main once more, then `node site/scripts/snapshot-live.mjs take s563-before`, `git push origin HEAD:refs/heads/task/563-land-023`, wait for `code-branch.yml` to merge it and for the deploy, then `take s563-after` and `compare s563-before s563-after`. Every line of the comparison goes into the report, marked expected or not, and any line not expected goes at the top.

If the landing cannot finish, push the branch to `wip/563-land-023` with the exact remaining commands under "To finish" and stop. After the landing: delete the merged wip branches listed in the report, and write `archive/sessions/SESSION_563_REPORT.md` (the checks with their exits, decisions, "For Samuel's ruling", "To finish", files).
