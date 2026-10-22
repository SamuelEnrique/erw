# Session 761 report: the reads and the weight

22 October 2026, from 19:28 UTC, on samueloldlaptop, unattended, in the worktree `C:\Users\lossa\Documents\erw-761` on `wip/761-allgrids` (cut from `wip/760-allgrids`). Chain `queue/done/063-evening-22-october-code-allgrids-3.md`, session 761. Model spend USD 0. No warehouse data written; no request to a publisher. The reads: a local build with the read timer on.

## Read these first

- **The tab still reads nothing from the database**: 0 read lines across six addresses, three times each. "Your load" wrote 120 in the same run, so the timer was on.
- **The answers**: the hub table about 150 ms warm, the node list about 200 ms, a node's panel about 190 ms, as at 739.
- **The weight**:
  - the hub table is 1.58 MB, unchanged since 737;
  - the node list grew by 20 KB (the swing column), to 340 KB.
- The measure is a new section of `docs/reviews/siting-reads-2026-10-22.md`.

## What to review

1. `docs/reviews/siting-reads-2026-10-22.md`, "Again (session 761, chain 063)".

## Checks

| Check | Exit | Result |
|---|---|---|
| precheck | 0 | |
| `db_probe.py` (the build only on its 0) | 0 | |
| `npm ci`, `npm run build` (lock `s761`, beat) | 0 | |
| `times739.mjs`, six addresses three times; "Your load" | 0 | 0 read lines; 120 |
| `weigh.mjs`, the hub table and the node list | 0 | 1,584,788 and 340,129 bytes |

## The landing

With 757 to 764, in session 764.

## Decisions made without you

1. **No index**: no read is slower than at 739, and the tab makes none.

## For Samuel's ruling

- Nothing new.

## Files

- Changed: `docs/reviews/siting-reads-2026-10-22.md`.
- New: this report.
