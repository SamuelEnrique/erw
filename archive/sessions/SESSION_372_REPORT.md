# Session 372 report: the day note, and the queue

20 October 2026, about 20:05 UTC, unattended, on samueloldlaptop (the code machine), the last session of the chain of 20 October, day (`queue/done/012-day-20-october-code.md`). Run by the chain's orchestrator. Model spend USD 0; no pull; no warehouse data written.

## Read these first

- **The note is `docs/state/review_2026-10-20_day_code.md`**: one line a session, the screenshot folders, the decisions made without you, what waits for you, and "To finish", every command of the landing that could not be made.
- **Sessions 365 and 366 are on main** (`e468065a`). **Sessions 367 to 371 and this one are on `wip/367-372-day`**, merged and tested together (26 test modules, OK), not landed: Claude Code stopped the landing build for low memory at 19:44 UTC, and a job it stops is not started again unattended.
- **`iso_queue_statistics` is wrong in the live set** (the note's item 2): the code is fixed on the branch; the data machine rebuilds the table after the landing.
- **The queue step was not run**: `queue/next/014-night-20-october-code.md` (sessions 381 to 383, `machine: code`) is on main and waits for this machine; its first session runs "To finish" if the branch is not on main by then.

## What to review

- `docs/state/review_2026-10-20_day_code.md` on `wip/367-372-day` (`https://github.com/SamuelEnrique/erw/blob/wip/367-372-day/docs/state/review_2026-10-20_day_code.md`).
- `queue/next/014-night-20-october-code.md` on main.

## Checks

| Check | Exit | Result |
|---|---|---|
| The test modules of sessions 365 to 371, the menu, package and pin modules (26) on the merged head `e55bf71f` | 0 | OK (24 skipped) |
| The whole suite at `ba84f0e4` (367 and 369) | 1 | 4,700 tests, 2 failures (`test_session103`'s comment-hash rule against `queue_statistics.py`, `test_session330`'s map line); both fixed in `005b590d`, their modules OK |
| The landing build at `ba84f0e4` | stopped | Claude Code's memory reaper, 19:44 UTC, at "Running TypeScript" |

## Landing

Not made (above). The queue file `014-night-20-october-code.md` was pushed to main alone, with a snapshot before and after: see below.

## Decisions made without you

1. **The landing not restarted after the memory stop**; every command written under "To finish".
2. **One branch for 367 to 372**, so that one landing (one build, one suite, one snapshot pair) carries them.
3. **The queue step not run**, and 014 written from roadmap items 2 and 8 so that the machine has work; its first session lands the branch.

## For Samuel's ruling

- Whether a chain may restart a job the memory reaper stopped (`CLAUDE_CODE_DISABLE_BG_SHELL_PRESSURE_REAP=1` when Claude Code starts; yours to set).
- The items of the note's "Waiting for you".

## Files

- `docs/state/review_2026-10-20_day_code.md`, this report (on `wip/367-372-day`); `queue/next/014-night-20-october-code.md` (on main).
