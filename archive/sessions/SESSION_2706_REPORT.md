# Session 2706 report: the brand document, the suite, and the landing that could not run

Energy Research Warehouse (ERW), session 2706, chain 131 (`queue/done/131-night-25-october-code-periodicals-v2.md`), samueloldlaptop, 25 October 2026, about 07:43 to 07:55 UTC. Model Opus 5.5. Model spend USD 0. No warehouse data written; nothing sent or posted; web requests to GitHub and the ERW's own database (the probe) only; no build.

## First: Monday's Digest will be the old code's

**Nothing of this chain is on main.** The landing gate did not run: the chain's memory rule (under 4 GB free, no build or gate) held at both reads, 1.96 GB free at 07:46:53 UTC and 2.06 GB at 07:48:52 UTC, as it did at session 2700's two reads (2.04 and 2.18 GB). This laptop has 7.3 GB in all, so the 4 GB line cannot be met here. The database probe passed three times (2.43, 0.47, 0.40 s). So Monday's scheduled Digest of 26 October, and tonight's Roundup of W43, are written by the code on main, not the v2 code; the two v2 previews of session 2705 are in your inbox (07:41 and 07:42 UTC). Every branch is pushed; the commands that land them are below, under "To finish".

## Read these first

- **Branch `wip/2706-periodicals`** (`c2c9ce5c`), cut from `wip/2705-periodicals` and merged with `origin/main` at about 07:45 UTC (`c820f42a`, no conflict). It holds every session of this chain over sessions 801 to 817, 2206 and 2207. Pushed.
- **`docs/brand.md` section 10** (`157fc878`): the Daily Digest's and the Weekly Roundup's v2 templates in the brandbook's words, the character's email rule, and the two send times left open with the workflow and pg_cron lines that would change them. No new rule.
- **`docs/voice.md` unchanged.** Two lines contradict the template; listed here, not resolved:
  1. "Its products carry its name: ERW's Energy Digest, ERW's Roundup, ..." against the template's names "ERW Daily Digest" and "ERW Weekly Roundup" (now the issues' titles).
  2. "dates as YYYY-MM-DD" against the masthead's "the issue date as 26 October 2026" (the masthead writes the date in words; the body keeps YYYY-MM-DD).
- **The suite**: every test file that reads the periodicals' code or the checkers (104 files, 1,261 tests) after the merge with main: one failure, fixed in this session (`c2c9ce5c`: session 2702's floor line had changed words that session 430's slow-site test reads; the held count is now added only when there is one); then 64 of the touched files' tests pass, and the node test of the Digest's keys passes (11).

## Checks

| Check | Exit | Result |
|---|---|---|
| `scripts/precheck.py --what "session 2706"` | 0 | passed |
| `git merge --no-edit origin/main` | 0 | no conflict |
| `python -m unittest` over the 104 files (`runs/s2700/suite2706.out`) | 1 | 1,261 run, 1 failure (session 430's slow-site wording), 25 skipped |
| `python -m unittest tests.test_session430 tests.test_periodicals` after the fix | 0 | 64 passed |
| `node --import ./scripts/alias-register.mjs scripts/test-digest-numbers.mjs` | 0 | 11 passed |
| `scripts/db_probe.py`, three times a minute apart | 0, 0, 0 | 2.43, 0.47, 0.40 s |
| memory (total minus the working sets' sum), twice | | 1.96 and 2.06 GB free: under the 4 GB line |
| `scripts/land_check.py` | not run | the memory rule |

## The landing

Not made (above). No snapshot pair, no push to `task/`. The scheduled Roundup of W43 tonight is the old code's, so there is nothing to read against session 2705's preview.

## Decisions made without you

- The landing branch is `wip/2706-periodicals` (it holds 2701 to 2705 and this session), not `wip/2705-periodicals` as the chain names, so the brand section and the floor-line fix land with the rest.
- The floor line's earlier words are kept when no figure is held (session 430's test reads them).
- The memory rule read as written, twice; the other Claude Code window left open.

## For Samuel's ruling

- **Where the landing runs.** This laptop cannot free 4 GB (7.3 GB in all): either the line is lowered for it (chain 085 landed at 2.4 GB; the gate was stopped by the system at 0.8 GB on 23 October), or the landing runs on the personal laptop or the desktop.
- The send times of both periodicals (`docs/brand.md` section 10, "Open").

## To finish

The landing of `wip/2706-periodicals`, on a machine with 4 GB free, from its main checkout, each command on its own with its exit code read (never piped):

1. `git pull --ff-only origin main`; if main has moved, merge it into the branch in a worktree (`git merge --no-edit origin/main`) and push the branch.
2. `.venv\Scripts\python.exe scripts\db_probe.py` (three tries a minute apart; under 3 s).
3. `.venv\Scripts\python.exe scripts\buildlock.py acquire s2706`
4. `CHECK_VALUES_TIMEOUT_MIN=45 CHECK_VALUES_REQUEST_S=120 .venv\Scripts\python.exe scripts\land_check.py --ref wip/2706-periodicals --lock-as s2706 --port 3706 --keep-worktree`
5. The commands it prints: `scripts\freeze.py status`; `node site/scripts/snapshot-live.mjs take s2706-before`; `git push origin wip/2706-periodicals:task/2706-periodicals`; wait for `code-branch.yml`'s merge and production's deployment of the merge (a mark of the new commit on the site); `node site/scripts/snapshot-live.mjs take s2706-after`; `node site/scripts/snapshot-live.mjs compare s2706-before s2706-after` (expected: none, every page is in review).
6. From the kept build (port 3706), `CHECK_VALUES_PAGES=/digest/2026-10-21 node scripts/check-values.mjs http://localhost:3706` in `site/` (session 2207's proof of the revised note), and screenshots of `/digest/2026-10-23`, `/roundup/2026-W41` at 390 and 1280 under `docs/brand/review-2703/` and `review-2704/`.
7. `.venv\Scripts\python.exe scripts\buildlock.py release s2706`; then `.venv\Scripts\python.exe scripts\check_digest.py --supabase --then-csv` and `scripts\check_roundup.py --supabase --then-csv` on main.
8. Once the branch is an ancestor of main: the "LANDING_PENDING" and "Not landed by this chain" lines of the reports of sessions 801 to 817, 2206 and 2207 replaced by what happened; the worktrees `erw-2700` to `erw-2706` removed and the merged `wip/` branches deleted on origin.
