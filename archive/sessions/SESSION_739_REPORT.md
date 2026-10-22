# Session 739 report: the reads and the build

22 October 2026, from 16:46 UTC, on samueloldlaptop, unattended, in the worktree `C:\Users\lossa\Documents\erw-739` on `wip/739-allgrids` (cut from `wip/738-allgrids`). Chain `queue/done/062-day-23-october-code-allgrids-2.md`, session 739. Model spend USD 0. No warehouse data written; no request to a publisher. The reads: a local build of `wip/738-allgrids` with the read timer on.

## Read these first

- **The tab still reads nothing from the database**: 0 `[erw-read]` lines across ten addresses, three times each. They include this chain's new ones: the node list by spread, the link's address, the headroom sort.
  - "Your load", asked four times in the same run, wrote 120 lines (40 distinct reads), so the timer was on.
- **The answers**:
  - the hub table: 142 ms warm (1,236 ms the first time after the start);
  - the node list: 187 to 230 ms;
  - a node's panel: 190 ms (716: 166 to 168).
- **The build**: about 70 seconds, as at 716.
- **The hub table's page**: 1.59 MB of HTML, from 1.82 at 716, after 737's change.
- **The twenty slowest reads** (all of "Your load") are the same tables as at 716. The slowest is 27 ms, `scarcity_hours_by_grid`. No index is needed; migration 036 stays unapplied.
- The second measure is a new section of `docs/reviews/siting-reads-2026-10-22.md`.

## What to review

1. `docs/reviews/siting-reads-2026-10-22.md`, "Again (session 739, chain 062)".

## Checks

| Check | Exit | Result |
|---|---|---|
| precheck | 0 | |
| `next start` with `ERW_READ_TIMING=1` on 738's build | | |
| `runs/chain_062/times739.mjs`, ten addresses three times | 0 | all 200; 0 read lines |
| "Your load" four times | 0 | 120 read lines |
| `site/scripts/slow-reads.mjs` on the log | 0 | 240 requests, 40 distinct reads, slowest 27 ms |

## The landing

With the next landing.

## Decisions made without you

1. **738's build stood for this branch**: 739 changes no code, so its build is the same.

## For Samuel's ruling

- Nothing new.

## Files

- Changed: `docs/reviews/siting-reads-2026-10-22.md`.
- New: this report.
