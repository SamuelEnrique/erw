# Session 386 report: the morning note, and the queue

21 October 2026, from 05:15 UTC, unattended, on lab-desktop (the data machine), the last session of the chain of 20 to 21 October, night (`queue/done/013-night-20-october-data.md`). Run at Samuel's instruction of 05:15 UTC, which stopped session 384's wait for the scheduled runs of 21 October. Model spend USD 0. Pulls: none.

## Read these first

- **The note: [`docs/state/morning_2026-10-21_night.md`](../../docs/state/morning_2026-10-21_night.md).** The cause of 20 October's stop and the lock's fix (384); the refusals for storage that remove tables from the draft, and v1 at 135 tables with 2 held for storage (385); the move under Ben's organization prepared to the clicks (385); one line a session; pulls against ceilings; decisions; what waits, Redivis's storage first; the other machines.
- **Session 384's part (b) was not run**, and its report says so; it is session 387 of the next chain.
- **The queue held no file for this machine** (`chain_queue.py list`: `014-night-20-october-code.md` and `015-day-20-october-code-pm.md`, both `machine: code`), so this session wrote **`queue/next/016-day-21-october-data.md`**: sessions 387 to 389, from `docs/roadmap.md` "This week" items 6 (21 October's root causes, 384's part b, and the green streak) and 5 (the 20 tables whose license is not settled, at most 16 requests); item 9 waits on Samuel and Ben, so no session of it is planned. Numbers 387 to 389: 381 to 383 and 401 to 415 are the code machine's. Committed on main alone and pushed (`bfca6f1a`, 05:18 UTC), with snapshots `s386-queue-before` and `-after`.

## Landing

- `queue/next/016-day-21-october-data.md` on main: rule 8 snapshots, compared in the table below.
- The whole suite in the worktree after merging origin/main (`GITHUB_ACTIONS=true`, 4,705 tests, 278 skipped, 257 s): exit 1, one failure, `test_session166`'s skip of four ancillary tables, which counts 3 from 21 October because NYISO is now held (license needed) and greyed before its table is looked for. The code machine fixed the test on `task/367-372` (`b39bada3`, test only, not on main yet); this session took it with `git cherry-pick -x`, and `tests.test_session166` then passes (exit 0). Without it every landing of today fails its checks.
- This note and the reports of 384 and 386 on `task/386-morning`; the record of its checks is in session 389's note (it cannot be in the commit it lands).

| Snapshot pair | Differences | Expected |
|---|---|---|
| `s386-queue-before` (05:18 UTC), `s386-queue-after` (after the deployment of `bfca6f1a` reported success at 05:21 UTC) | 0 on 25 pages | yes: a queue file changes no page |

## The queue step

`python scripts/chain_queue.py next`, after the landing.

## Decisions made without you

1. The next chain from items 5 and 6 only; item 9's remaining acts are Samuel's and Ben's.
2. Session 384's report written by this session, with its part (b) marked not run, so that the chain's record is whole.
3. `b39bada3` taken from the code machine's branch rather than writing a second fix of the same test; the merge of `task/367-372` then meets the same change.
4. The next note named `docs/state/note_2026-10-21_day_data.md`, since it will be written during the day of 21 October, not in a morning.

## Files

- New: `docs/state/morning_2026-10-21_night.md`, `queue/next/016-day-21-october-data.md`, `archive/sessions/SESSION_384_REPORT.md`, this report.
