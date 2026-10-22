# Session 716 report: the reads

22 October 2026, from 11:25 UTC, on samueloldlaptop, unattended, in the worktree `C:\Users\lossa\Documents\erw-716` on `wip/716-allgrids` (cut from `wip/715-allgrids`). Chain `queue/done/050-night-23-october-code-allgrids.md`, session 716. Model spend USD 0. No warehouse data written; no request to a publisher. The database was read only by "Your load", for the comparison.

## Read these first

- **The All grids tab makes no read of the database.** Session 580's timer was on (`ERW_READ_TIMING=1`) on a build of `wip/715-allgrids`, and the tab's nine addresses wrote no `[erw-read]` line: three warm tries each, and three first requests after a fresh start. "Your load", asked twice in the same run, made 40 distinct reads.
  - `tests/test_session716.py` holds that no file of the tab imports a database reader.
- **The site's build on this machine: 64 s, then 32 s warm** (under 90 s). The tab is drawn at each request.
- **Each address answers in 91 to 184 ms warm, and 224 to 679 ms on the first request after a start** (the rows computed once, then kept).
- **No index is needed**: migration 036 (session 580's, unapplied) is unchanged.
- **The finding**: the hub table's page is **1.73 MB of HTML** (the node list 0.32 MB). Its tips are long, and the server's payload repeats them. That is for Samuel's ruling, below; nothing was changed.
- **The twenty slowest reads of "Your load"** are listed for comparison, and two of them page past the end of their table. All in `docs/reviews/siting-reads-2026-10-22.md`.

## What to review

1. `docs/reviews/siting-reads-2026-10-22.md` on the branch: the table of addresses and times, the build, the twenty reads.
2. On this machine: `runs/chain_050/times716.txt` (every try), `runs/chain_050/serve715.out` (the server's log with the timer's lines), `runs/chain_050/slow716.md`.

## Checks

| Check | Exit | Result |
|---|---|---|
| precheck | 0 | |
| `tests.test_session716` | 0 | OK |
| the build of 715's branch with the timer (lock `s715`, beat; `db_probe` 0.73 s) | 0 | 64 s, then 32 s |
| `slow-reads.mjs` on the server's log | 0 | 80 requests, 40 distinct reads, all "Your load"'s |

## The landing

With sessions 716 to 721, or the next combined push (see the chain's note).

## Decisions made without you

1. **The tab's own page is drawn at request time**, so "the page's build" is read as the site's build, timed whole, and the tab's answers are timed per address.
2. **The heavy page is listed, not trimmed**: shortening the tips changes the words of the page's sources, which is a ruling.

## For Samuel's ruling

- Whether to shorten the tab's tips (the method once per column, each cell's tip only its own figures) to bring the hub table's page under 1 MB.

## Files

- New: `docs/reviews/siting-reads-2026-10-22.md`, `tests/test_session716.py`, this report.
