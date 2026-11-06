# Session 449 report: the reports of 20 and 21 October, read as a reviewer

21 October 2026, about 07:10 to 07:40 UTC, unattended, on portable-laptop (the code role, set for tonight's chain), on `wip/441-450-third`. The chain of 21 October, night, third machine (`queue/done/017-night-21-october-third.md`, session 449). Model spend USD 0; no pull; no warehouse data written; no `site/` change, so no build. Read-only git only: the parent session commits.

## Read these first

- **The review is `docs/reviews/review-of-20-21-october.md`**: one line a session (36 reports found for the 76 numbers 365 to 440), a verdict word each with the evidence that holds it, the 40 numbers with no report and why, eight places where a report claims more than its checks show, nine places where two sessions' decisions conflict, and the five items that most need Samuel's eyes.
- **Verdicts: 15 met, 20 partly, 1 not met** (379, stopped correctly by its own gates). Most "partly" are sessions whose build checks could not run during the database's statement timeouts of 23:30 to about 05:30 UTC, and say so.
- **The first item: the landing of `task/381-382` at 07:05 UTC (`bb49c9e0`) is recorded in no report.** It put 367 to 372 and 381 to 383 on main, with two 383 commits that its report does not mention (`1bd23cc8`, a page change and a test; `accad477`, a check). Reports 367 to 371 still carry the landing placeholder.
- **The 015 chain stopped short**: 401 and 408 have commits and no report, 411, 412 and 415 never ran, and no evening note was written. `wip/015-land` merges into main without a conflict (`git merge-tree`, exit 0), but most of its branches passed no check on a production build.
- **Two premises of tonight's chains are contradicted by the record**: session 434 (data machine) is told 386 never ran, and 386 landed at 05:36 UTC (`7e08c274`); this laptop ran session 420 as a data machine and in the code machine's reserved numbers.

## What to review

- The review: `https://github.com/SamuelEnrique/erw/blob/wip/441-450-third/docs/reviews/review-of-20-21-october.md`, the last section first.
- The test: `tests/test_session449.py`.

## Checks

Every gate redirected to a file under `runs/chain_oct21_third/s449/`, never piped; the exit code read before the next step.

| Check | Exit | Result |
|---|---|---|
| `find_reports.sh` (every report of 365 to 440 on every remote branch) | 0 | 480 lines, 36 reports, 3 with two versions (main's read) |
| `hashes.sh` (every commit a report cites) | 0 | 71 commits: 66 in main, 5 on unlanded `wip/` branches as their reports say, 0 missing |
| `files.sh` (50 files the reports name, on the branch each names) | 0 | 49 present; `docs/brand/review-403` absent, as 403's report says |
| `git merge-tree --write-tree` (main with `wip/015-land`; `wip/015-land` with `wip/401-s`, `wip/408-s`) | 0, 0, 0 | no conflict |
| `tests.test_session449` | 0 | 5 tests OK: no em or en dash; one line for each of the 36 sessions with a verdict word; every number 365 to 440 a line or in the missing table; exactly five items; every cited commit exists |
| `tests.test_session449` against a spoiled copy (a verdict word removed, an item unnumbered, a dash added) | 0 | the three tests failed, as they should (`test_spoiled.out`) |
| Build, snapshot, browser checks, whole suite | none | no `site/` change; the parent runs the chain's suite |

## Decisions made without you

1. **Main's version of a report is read where two exist** (365, 366, 381): it is the later commit in each case.
2. **A landing is verified by ancestry**, `git merge-base --is-ancestor` against `origin/main` as fetched at the chain's start; a landing's checks are taken from the report that records them, and a landing no report records is said to be unrecorded, not judged.
3. **Verdicts take a stop by the session's own gate as "not met", not a fault** (379): the line says the stop was correct.
4. **Session 420 is reviewed** although no chain file asked for it: its number is in the range and its work is on a branch.
5. **`git merge-tree` was used to answer "will these collide"**: it writes objects but moves no ref, the nearest read-only form of a trial merge.
6. **The DB timeout's cause is not named**: the review sets the times side by side (374's load, 383's timeouts, 387's pg_cron failures, the 015 builds) and leaves the cause to the dashboard 387 asks Samuel to read.

## For Samuel's ruling

- Record the landing of `bb49c9e0` (07:05 UTC): its checks and its rule 8 comparison, in a report, before the next landing.
- Land `wip/015-land` with `wip/401-s` and `wip/408-s` through one gate once the database answers, or land them in parts.
- Session 434's premise (386 never ran): correct the data machine's chain before 434 starts, or let it run.
- This laptop's role: data (as session 420 ran) or code (as tonight's chain is written); `.erw/machine.json` was set to code for tonight.
- The numbers 416 to 430: keep them reserved for the code machine, given that 420 is taken.
- The two LinkedIn sets (407's ten posts, 420's ten findings): which one is the material, or both.

## To finish

- Nothing for this session; the review lands with the chain's branch, as session 451's list says.

## Files

- New: `docs/reviews/review-of-20-21-october.md`, `tests/test_session449.py`, this report.
- Not in git: `runs/chain_oct21_third/s449/` (`find_reports.sh`, `reports_found.txt`, `reports_latest.txt`, `reports/` with the 36 reports as read, `hashes.sh`, `hashes.out`, `files.sh`, `files.out`, `branches.out`, `mergetree_*.out`, `test.out`, `test_spoiled.out`).
