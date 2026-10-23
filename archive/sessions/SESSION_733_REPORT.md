# Session 733 report: the node's place

22 October 2026, from 15:44 UTC, on samueloldlaptop, unattended, in the worktree `C:\Users\lossa\Documents\erw-733` on `wip/733-allgrids` (cut from `wip/732-allgrids`). Chain `queue/done/062-day-23-october-code-allgrids-2.md`, session 733. Model spend USD 0. No warehouse data written; no request. The read: the archive's copy of `node_basis_daily` on this machine.

## Read these first

- **None there.** Neither ERCOT's settlement point mapping nor its resource registration is held: coverage on main lists neither, and no connector for them is on main.
- **The fallback: what the node table's own columns carry.** `node_basis_daily`'s columns are `x_hub`, `x_resource_type` and `x_class`, beside the standard ones:
  - `x_hub` is HB_HUBAVG on every row (960,627 rows): the hub each node's basis is measured against, not the node's own settlement hub.
  - `x_resource_type` and `x_class` are already drawn (the panel's "ERCOT's resource types", the list's Class).
  - `node` repeats the settlement point's name. No column names a load zone, a wires utility, a county or coordinates.
  - **So nothing more about a node's place can be drawn from the table.** The panel's "not held" items stay, as do open items 11 and 12.
- **What the table holds that the tab does not use** (for the next chain, not drawn here):
  - `dam_spread_4h`: each day's four dearest hours' mean less the four cheapest, for 888 points over the same twelve months as the basis. It is a node's intraday swing, the figure a battery or a flexible load reads.
  - `rtm_basis` and `rtm_mean`: real time, from 2026-09-28 only (23 days, 886 points). Too short for a twelve-month figure, so the panel's "real time is not held at the nodes for twelve months" stands.

## What to review

- Nothing on the page changed.

## Checks

| Check | Exit | Result |
|---|---|---|
| precheck | 0 | |
| the columns and variables of `runs/archive_restore/node_basis_daily.csv` | 0 | `x_hub` HB_HUBAVG on all 960,627 rows; `dam_*` 2025-10-01 to 2026-10-20 (888 points); `rtm_*` 2026-09-28 to 2026-10-20 (886) |

## The landing

Sessions 731 to 740 landed in one push at 17:19 UTC: see `SESSION_740_REPORT.md`, "The landing".

## Decisions made without you

1. **`x_hub` is not read as a node's hub**: it is the reference every node's basis is taken against, the same for all.

## For Samuel's ruling

- Nothing new. The intraday spread at the nodes (`dam_spread_4h`) is listed for the next chain as work, not a ruling.

## Files

- New: this report.
