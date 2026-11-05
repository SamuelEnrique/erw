# Session 759 report: the replication, extended

22 October 2026, from 19:26 UTC, on samueloldlaptop, unattended, in the worktree `C:\Users\lossa\Documents\erw-759` on `wip/759-allgrids` (cut from `wip/758-allgrids`). Chain `queue/done/063-evening-22-october-code-allgrids-3.md`, session 759. Model spend USD 0. No warehouse data written; no request to a publisher. The reads: the live set with the anon key, the warehouse's CSVs in `runs/archive_restore/`, production's pages.

## Read these first

- **The one figure chain 063 added, the node's intraday swing (746), is replicated** from `node_basis_daily`'s daily rows by 746's addition to `warehouse/replication/siting.py --tables`. Against production, which serves it since 19:20 UTC: **92 figures computed, 80 beside the page, 0 differ**. The three nodes read 48.1828, 56.5073 and 56.5073, the same as the page.
- **No other figure was added**: 747 to 756 changed nothing (no ruling, no table), and 757's fix is a word's case.
- **The landing the chain file puts here is moved to 764**, with 757 to 763, so the site deploys once more instead of twice. Vercel refused two of today's deployments past its daily count.

## What to review

1. `runs/chain_062/repl759.out` on this machine: one line a figure.

## Checks

| Check | Exit | Result |
|---|---|---|
| precheck | 0 | |
| the replication against production, `--tables runs/archive_restore` | 0 | 92 / 80 / 0 differ |

## The landing

Sessions 757 to 765 landed in one push at 19:59 UTC: see `SESSION_765_REPORT.md`, "The landing".

## Decisions made without you

1. **One landing for 757 to 764**, not one here and one at 764: the pages change little (757's word), and each push is a deployment.

## For Samuel's ruling

- Nothing new.

## Files

- New: this report.
