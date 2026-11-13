# Session 5163 report: the landing rows and the records; where roadmap item 7 stands

13 November 2026, unattended, `portable-laptop` window P2. Branch `wip/5150-security`, worktree `erw-p2-5150`. Model spend USD 0. Pulls: the snapshots of the live pages around the push of the row's new head. Nothing built, nothing landed, no warehouse data written.

Clock: precheck 19:43 UTC, the records and their test by 19:46 UTC, the row after this report. Inside the long end of 1:00.

## Read these first

- **Roadmap item 7, as a session can take it: nothing is left to close without you.** The list has 32 rows and none is open.
  - 1 closed (the hole in the curtain, live since this morning's landing).
  - 10 fixed and waiting on one landing (row 23 of `docs/state/landing_request_portable.md`).
  - 13 rulings, each with a default this chain acted on.
  - 8 noted.
- **The item's own words, read against that:**
  - "every open item of the security review closed or ruled": yes, once row 23 lands. The 13 rulings are written with their defaults; none blocks the landing.
  - "the usage counts live": yes, recording since 10 October, unchanged by this chain.
  - "on the pages the rulings allow": your reading (row 24). The strict reading is one setting away.
  - "with no cookie": yes, and now held by a test.
  - "and no identifier": your reading (row 23). A count with no visitor value at all is one setting away.
- **The roadmap is yours to mark.** This window did not touch `docs/roadmap.md`.
- **Three things are built and wait only for a word or a setting**: `wip/5157-retire-link` (the old link), `USAGE_VISITORS=off`, `USAGE_TOOL_PAGES=off`.

## This window's branches and rows

| Branch | Head | Landing row | State |
|---|---|---|---|
| `wip/5100-tools`, `wip/5100-security` | `7fd58dfe3` | 18 | landed at `b1ea7427a` (chain 234) |
| `wip/5150-security` | this session's last commit (the row names it) | 23, task `5158-security`, port 5101 | requested; not yet landed at 19:43 UTC |
| `wip/5157-retire-link` | `3118c0a7a` | none, on purpose | waits for your word (rows 3 and 4 of the list) |

## What was done

- **The list counts itself**: a section "Where the list stands" in `docs/reviews/security-faults-2026-11-13.md`, rows by state.
- **`docs/security.md`**: the list's size brought up to date (it said 26 rows).
- **`tests/test_session5163.py`**, 6 tests: the list's own table of counts equals the rows as they read; no row is open; a row said fixed or closed names a test file that exists; every limit `docs/security.md` lists by name and number is the code's.
- **Landing row 23's head brought up to date** (after this report; the row's commit and its snapshots are in session 5164's report).

## Checks, with exit codes

| Command | Exit | Result |
|---|---|---|
| `scripts/precheck.py --what "session 5163 (window P2)"` | 0 | on duty |
| `git merge origin/main` | 0 | merged |
| `git merge-base --is-ancestor 5411fef7d origin/main` | 1 | row 23 has not landed yet |
| `pytest tests/test_session5163.py` | 0 | 6 passed |
| `pytest` on the 20 test files of this chain and the older ones they lean on (run before the push, below) | 0 | see the row |

- **Not run:** the build, the whole suite (0.9 GB of memory free).
- **Still running when this was written:** session 5161's scan of the whole git history (7,481 commits, started 19:37 UTC). Its result goes into session 5161's report.

## Decisions made without you

- **Row 8 is counted once, as fixed**, in the list's table: its `certifi` is fixed, its four major versions are rulings, and the table says both.
- **The row's head moved once, here**, not after every session: each move is a push to `main`.

## For Samuel's ruling

Nothing new. The 13 rulings of the list stand, each with its default; the three that are built are named above.

## The prompt

`queue/done/237-day-14-november-portable-p2-security-continued.md`, "Session 5163: the landing rows and the records".
