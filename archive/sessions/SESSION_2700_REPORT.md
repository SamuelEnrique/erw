# Session 2700 report: the periodicals' branches merged with main; the gate not run (memory)

Energy Research Warehouse (ERW), session 2700, chain 131 (`queue/done/131-night-25-october-code-periodicals-v2.md`), samueloldlaptop, 25 October 2026, about 06:36 to 06:44 UTC. Model Opus 5.5. Model spend USD 0. No warehouse data written; nothing sent or posted; web requests to GitHub, the ERW's own database (reads) and production (the snapshots) only.

## Read these first

- **`wip/818-periodicals` was not inside `wip/2206-periodicals-fixes`.** The chain file says 2206 "holds 818 merged with main"; `git merge-base --is-ancestor` says neither 801's first commit (`976cb07b`) nor 817's (`60b2c592`) is in 2206 or in main. So this session merged both: `wip/2700-periodicals` is cut from `origin/wip/2206-periodicals-fixes` (`50640b5b`), with `origin/wip/818-periodicals` merged in (`483f2828`, three files resolved) and then `origin/main` (`164c9a83`, clean). Every session of chains 060 and 061 and of 2206 and 2207 is now on one branch, pushed.
- **The three conflicts, each resolved by keeping both sides** (both are this chain's own files; neither side removed what the other added):
  - `scripts/check_digest.py`: 2206's `compare(...)` for a fuel close (fix 5, the revised figure) kept; 804's `digest_demand` reader (US48 demand at its hour) added after it.
  - `site/lib/digest.ts`: the `Place` type keeps 2207's `label` and 804's `cell`; 2207's `Revision` type kept.
  - `warehouse/news/brief.py`: 801's `WHY_ADJECTIVES` and `critically` with 2206's comment and `TERM`; 2206's `window_rows` call kept over 818's inline window (2206's does the same and also says both bounds).
- **The gate was not run.** The chain's memory rule (under 4 GB free: no build or gate) held at both reads: 2.04 GB free of 7.31 GB at 06:39 UTC and 2.18 GB at 06:41 UTC (the old laptop has 7.3 GB in all, and a second Claude Code window, not this session's, holds about 300 MB). So nothing landed, there was no snapshot pair for the landing, and sessions 2701 to 2705 work on branches over `wip/2700-periodicals`; 2706 lands them all at once, or leaves the commands below.
- **`check_digest.py --supabase --then-csv` on the archive** (the branch's code, the live set, then the main copy's CSVs): **147 ok, 0 FAILED, 2 revised** by the publisher after the issue was written (the two WTI closes of rulings item 7), 4 not held by this source, 5 from the chart's record, 9 fun facts checked against their stored sources when written; exit 0 (`runs/s2700/check_digest.out`).

## What to review

- The merge commit's three resolutions (above), `git show 483f2828 -- scripts/check_digest.py site/lib/digest.ts warehouse/news/brief.py`.

## Checks

| Check | Exit | Result |
|---|---|---|
| `scripts/precheck.py --what "session 2700"` | 0 | passed; on duty until 22:36 UTC |
| `scripts/freeze.py status` | 0 | no freeze |
| `python -m unittest tests.test_periodicals tests.test_session2206 tests.test_session2207 tests.test_session470 tests.test_session577 tests.test_session232 tests.test_session267 tests.test_session498 tests.test_session402` on the merged tree | 0 | 173 passed |
| `scripts/check_digest.py --supabase --then-csv --in-dir ../erw/warehouse/output` | 0 | 147 ok, 0 failed, 2 revised |
| memory (total minus the working sets' sum) | | 2.04 and 2.18 GB free: under the 4 GB line |

## The landing

None. The queue step's own commit (the move of file 131 to `queue/done/`) was pushed to main at 06:37 UTC as `835e669e`, with snapshots `c131-q-before` and `c131-q-after`: **0 differences** in all 25 pages (`runs/c131-q-compare.out`).

## Decisions made without you

- `wip/818-periodicals` merged into the session's branch with 2206, though the chain file names only 2206: the file's purpose is to land "what exists", and 818 is that.
- The three conflicts resolved by keeping both sides (above).
- The memory rule read as the chain writes it (total minus the working sets' sum), twice, two minutes apart; the second Claude Code window left open.
- The full suite not run outside the gate on this machine at 2 GB free (the harness killed a suite at low memory before); the nine test files of the periodicals' code were run instead.

## For Samuel's ruling

- The memory line of 4 GB is above what the old laptop can free (7.3 GB in all, about 5.2 GB in use with two Claude Code windows): on this machine the chain's gate can only run if the line is lowered (chain 085 landed at 2.4 GB) or the landing moves to the desktop or the personal laptop.

## To finish

1. When a machine has 4 GB free: from the main checkout, `.venv\Scripts\python.exe scripts\db_probe.py` (three tries a minute apart); `.venv\Scripts\python.exe scripts\buildlock.py acquire s2700`; `CHECK_VALUES_TIMEOUT_MIN=45 CHECK_VALUES_REQUEST_S=120 .venv\Scripts\python.exe scripts\land_check.py --ref wip/2700-periodicals --lock-as s2700 --port 3700` (or the newest branch of this chain, see session 2706); the commands it prints (freeze status, `node site/scripts/snapshot-live.mjs take <before>`, `git push origin wip/2700-periodicals:task/2700-periodicals`, the after snapshot once production carries the merge, `compare`); `buildlock.py release s2700`.
