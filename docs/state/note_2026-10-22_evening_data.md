# The data machine's note of the chain of 21 October, day and evening (written 21 October 2026, about 09:55 UTC)

Energy Research Warehouse (ERW), session 482, for Samuel. The data machine's chain of 21 October, day and evening (sessions 460 and 476 to 482, `queue/done/020-day-21-october-data-2.md`), unattended on lab-desktop, from 09:36 UTC to this note's push. Model spend USD 0 in every session. Before it: [`docs/state/note_2026-10-22_day_data.md`](note_2026-10-22_day_data.md) (sessions 452 to 459, landed as `f2a74167`).

## Read these first

- **A correction to session 454, made and explained** (session 460). Two tables session 454 "restored" were wrong. `policy_reads_evidence` and `price_board_spreads` already held the archive's latest run's own copies (3,362 and 2,408 rows, their data SHA-256 the run log's). `restore.py`'s replay keeps every key any run ever wrote, so its 5,143 and 2,436 rows held keys the latest runs had dropped, and `prove.py` read that as "this machine behind". The exact copies are back, coverage is 3,362 and 2,408 again, and neither table was loaded in between. `prove.py` now counts a copy that is the latest run's own as equal. Session 454's report has the correction appended.
- **Four branches for your ruling, each with its tests, none landed:**

  | Branch | Session | What it does |
  |---|---|---|
  | [`wip/455-loader`](https://github.com/SamuelEnrique/erw/tree/wip/455-loader) | 455 | the loader writes rows whose values moved, not those whose `retrieved_at` alone did; an older copy equal in value is no rollback; `series` analysed, not vacuumed, after a small load |
  | [`wip/477-loader-gate`](https://github.com/SamuelEnrique/erw/tree/wip/477-loader-gate) (on 455) | 477 | the loader asks `scripts/db_probe.py` before its first write (closed: exit 75, a skip); a 10-second pause after a table of 100,000 rows or more |
  | [`wip/478-stale-tile`](https://github.com/SamuelEnrique/erw/tree/wip/478-stale-tile) | 478 | a board row held two or more days behind its group gets `held = {since, newest, why}`, its status kept "ok" (a status of "stale" would take it off the board) |
  | [`wip/479-streak`](https://github.com/SamuelEnrique/erw/tree/wip/479-streak) | 479 | a job with fewer than half its expected runs is "short" in the day's record; ends the streak only when ruled (off). Half would not catch 21 October; 90% would |

- **`consolidate.py check` fixed** (session 476): a member copy older than the table is not compared, and the reasons are printed. All 6 families are ok here.
- **No queue file waits for this machine, by choice.** What remains that a session can do without a ruling needs today's daily runs (GitHub's at 14:00 UTC, this machine's at 17:00 UTC). Neither queue can hold a file until an hour, so a file in `queue/next/` would be taken at once and carried again. The work is below, under "To finish after 23:00 UTC". A "not before" line read by `chain_queue.py next` (waiting for you, 2) would let a chain hold it.

## To finish after 23:00 UTC (sessions 480 and 481, carried unchanged)

Session 480, 21 October's whole day. Pulls: none.
- `lock.py status`.
- Whether pg_cron dispatched `erw-daily` at 14:00 UTC (`runs/s387_dispatch.py`, read only).
- `warehouse/health.py summary --day 2026-10-21 --out runs/<folder>` copied over `queue/summary/2026-10-21-health.md`, sessions 387, 439 and 457's "## Root causes" kept. For every failed step after 09:11 UTC, its root cause, one paragraph each.
- This machine's daily run: when it took and released the lock, what it wrote and committed, and the Redivis uploads of `ercot_node_prices_hourly` and `eia930_all_storage` (session 437).
- One line on whether 21 October counts green; `site/data/health_days.json` read, not written.

Session 481, after this machine's daily commit. Pulls: none.
- `board.json` on main: ERCOT's day-ahead and real-time tiles against CAISO's, NYISO's and SPP's newest days.
- `map.json`'s build date (9 October before).
- `node_basis_daily`'s real-time days (22 before) and `ercot_node_prices_hourly`'s rows against 500,000.
- `prove.py --fresh --only '^datacenter_queue_positions$'`.

## What each session landed

| Session | Landed (on `task/460-482-day`) |
|---|---|
| 460 | `warehouse/archive/prove.py` (the latest run's own copy is equal) and `tests/test_session460.py`; the two tables and their coverage rows put back; the correction in session 454's report |
| 476 | `warehouse/consolidate.py` (older member copies not compared; the reasons printed) and `tests/test_session476.py` |
| 477 to 479 | their reports; the code on the three branches above |
| 480, 481 | one-line reports: not run (not before 23:00 UTC) |
| 482 | this note |

The record of this landing is in the next note.

## Pulls against their ceilings

| Session | Pull | Used | Ceiling |
|---|---|---|---|
| 460 | the archive bucket (the run log) | read | the bucket |
| 476 to 482 | none | 0 | 0 |

## Decisions made without you (one line each; the reasons are in each report)

- 460: the two tables back to the latest run's exact copies; session 454's report corrected by an appended section, not rewritten.
- 476: a file's modified time decides "older".
- 477: built on 455, so the loader's changes are ruled together.
- 478: `held` instead of `status: stale`, so no tile leaves the board.
- 479: the line at half, as asked, with the measure that 90% would be needed for 21 October.
- 482: no next file, the 23:00 UTC work written here instead of a file that would loop.

## Waiting for you, highest value first

1. **`node_basis_daily` out of the live set** (session 456): about 600 MB of `series`, no reader.
2. **A "not before" line for chain files** in `chain_queue.py next` and the chain worker, so that work tied to an hour can wait in the queue (sessions 457 and 482).
3. **The four branches above**: `wip/455-loader` with `wip/477-loader-gate`, `wip/478-stale-tile`, `wip/479-streak`.
4. **The compute tier** (session 431), with Supabase's disk graphs for the night of 20 to 21 October.
5. **Redivis**: storage (about 0.6 GB free) and whether an unattended session may upload to the draft.
6. Still open: `ercot_peak_premium` in `run_data_machine.sh`, pg_cron's connections, the waiting rule, Vercel's deployment limit, the license rulings, the permission letters, `nyiso_load_queue`, "One alert policy", the daily task with no console window, the move under Ben's organization.

## The other machines

- **The code machine**: `019-night-21-october-code.md` was taken by portable-laptop (`440a2c8f`). The board's rendering of `held` (session 478) would be its work.
- **This machine**: its daily run starts at 17:00 UTC; the chain worker starts a session only when a file waits and no Claude Code process is alive.
