# Session 723 report: the trader's path, walked

22 October 2026, from 15:00 UTC, on samueloldlaptop, unattended, in the worktree `C:\Users\lossa\Documents\erw-723` on `wip/723-allgrids` (cut from `wip/722-allgrids`). Chain `queue/done/062-day-23-october-code-allgrids-2.md`, session 723. Model spend USD 0. No warehouse data written; no request to a publisher. The reads were production's pages in the internal view, and the archive's copy of `node_basis_daily` on this machine.

## Read these first

- **The walk**: `docs/reviews/siting-trader-path.md`, 16 steps at a 1 GW load on production. Shots are in `docs/brand/review-723/`, the walk's script and its list of steps beside them.
- **What holds**: the cheapest and dearest nodes, a node's panel, hub against hub, the flexible profile at the peaks and above a strike, the four-peak charge, and the 390 layout.
- **What a trader cannot do today**, each fixed by session 724 in the chain's files:
  1. **Find the widest-moving nodes.** Sorting by energy and by basis gives the same order, since every node is HB_HUBAVG plus its basis. The day-to-day spread is in the panel only.
  2. **Know which days are missing.** Every node reads "335 of 365": `node_basis_daily` lacks 2026-08-21 to 2026-09-19 for every node, and the tip does not say so.
  3. **Set a node as A or B from the page.** The address takes one and the tab answers, but the box's lists hold hubs and zones only, and Show drops the node.
  4. **Find a node by name**: no filter in an 873-row list.
  5. **Take the numbers away**: no download.
- **Left as found**: two nodes with the same figures (a fact, not an error); a sort by real time (real time is held for some hubs only and for no node).
- **For the data machine**: the 30 missing days of `node_basis_daily` (the walk's last section).

## What to review

1. `docs/reviews/siting-trader-path.md`: the table of steps, then "What session 724 fixes".
2. `docs/brand/review-723/t03_basis_lowest_1280.png` against `t01_nodes_cheapest_1280.png`: the same order under two sorts.
3. `docs/brand/review-723/t07_ab_node_1280.png`: a node as A by the address, and the A list reading "none".

## Checks

| Check | Exit | Result |
|---|---|---|
| precheck | 0 | |
| `runs/chain_062/walk.mjs` on production, 13 addresses | 0 | 13 shots and texts; no page wider than its window |
| the missing days, on `runs/archive_restore/node_basis_daily.csv` | 0 | 30 days, 2026-08-21 to 2026-09-19 |

## The landing

Sessions 722 to 730 landed in one push at 16:15 UTC: see `SESSION_730_REPORT.md`, "The landing".

## Decisions made without you

1. **The walk ran on production**, not a local build: chain 050 had just been served whole, and the trader reads the site as it is.
2. **The page's text at each step stays on this machine.** It holds NYISO's and ISO-NE's prices, which wait on chain 050's ruling item 3; the screenshots of the first screen show ERCOT's, CAISO's and SPP's rows only.

## For Samuel's ruling

- Whether the hub table should sort by real time, or by day-ahead less real time, where real time is held (step 13).

## Files

- New: `docs/reviews/siting-trader-path.md`, `docs/brand/review-723/` (13 shots, the walk's script and steps), this report.
