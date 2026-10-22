# Session 781 report: the replication, extended

22 October 2026, from 21:40 UTC, on samueloldlaptop, unattended, in the worktree `C:\Users\lossa\Documents\erw-781` on `wip/781-allgrids` (cut from `wip/780-allgrids`). Chain `queue/done/064-night-22-october-code-allgrids-4.md`, session 781. Model spend USD 0. No warehouse data written; no request to a publisher. The reads: the live set with the anon key, the warehouse's CSVs in `runs/archive_restore/`, production's pages.

## Read these first

- **The third card (773) is computed a second time** from `node_basis_daily`'s daily rows (`--tables`): every storage node's mean day-ahead swing over the node file's twelve months, among those holding 90 percent of the most days any node holds.
  - 195 nodes; the narrowest 34.2165, the widest 105.8621, the median 49.3103.
  - All four equal the card's own figures.
- **Against production, with `--tables`: 96 figures computed, 84 beside the page, 0 differ.**
- **The rest of this chain's work needs no new replication**:
  - 772's filter shows the same rows;
  - 777's hand-over sends the same values (its own test);
  - 774 and 775 are checks.
- **The landing the chain file puts here moves to 787**, with 778 to 787, so the site deploys once more.

## What to review

1. `runs/chain_062/repl781.out` on this machine.

## Checks

| Check | Exit | Result |
|---|---|---|
| precheck | 0 | |
| the replication against production, `--tables runs/archive_restore` | 0 | 96 / 84 / 0 differ |

## The landing

With 778 to 787, in session 787.

## Decisions made without you

1. **The card's rule followed exactly**, the 90 percent of the most days held read from the node file, so the replication and the card cannot drift apart.

## For Samuel's ruling

- Nothing new.

## Files

- Changed: `warehouse/replication/siting.py` (the storage nodes' swing, the third card's figures).
- New: this report.
