# Session 1032 report: the package reads the tab's figures

23 October 2026, from about 07:00 UTC, on samueloldlaptop, unattended, in the worktree `C:\Users\lossa\Documents\erw-1022` on `wip/1032-packages` (cut from `wip/1031-allgrids`). Chain `queue/done/071-night-23-october-code-allgrids-packages.md`, session 1032. Model spend USD 0. No request (the live set's and Redivis's ceilings, 50 each, were not used); no warehouse data written. The reads: this machine's tables, through the package's local backend.

## Read these first

- **Four of the All grids tab's figures are reproduced by the Python package**, exactly, from the tables the tab's files were built from: HB_HUBAVG's twelve-month day-ahead price (34.302056), a node's basis spread (7.8679) and intraday swing (48.1828), and New York City's zone demand growth (1.0759). `package/tests/test_tab_figures.py`, 5 passed with the tables; 4 skipped and 1 passed without them.
- **The fifth, the second card's HB_HUBAVG all-in (42.12709), is named, not reproduced**: it adds ERCOT's four-peak charge, whose rate is `texas_delivery_charges`'s, an internal table. The test checks that the package's record says "internal".
- **The hub's price is two tables, not one**: this machine's `ercot_all_hub_prices_history` ends on 26 August 2026, and the price files take the later hours from `iso_dam_hub_prices`; with the first table that holds an hour keeping it, the 8,760 hours give the page's figure. The order is now written beside the figure (`tab_figures.json`).
- **No fault was found** in the package or in the tab.

## What to review

1. `docs/methods/packages.md`, "The package reads the All grids tab's figures (session 1032)".
2. `package/tests/tab_figures.json`: each figure's window and tables in words.

## Checks

| Check | Exit | Result |
|---|---|---|
| precheck | 0 | |
| `ERW_DATA_DIR=runs/data1032 pytest package/tests/test_tab_figures.py` | 0 | 5 passed (40 s) |
| the same without `ERW_DATA_DIR` | 0 | 1 passed, 4 skipped |

`runs/data1032/` holds hard links to five of this machine's table files (two from `warehouse/output/`, three rebuilt from the ERW's archive into `runs/archive_restore/`); nothing was copied or written.

## The landing

Lands with the next landing of this chain.

## Decisions made without you

1. **The local backend, not the live set or Redivis**: `node_basis_daily` is out of the live set (session 483) and the released Stanford dataset holds only the starter table, and the hub history is not in the live set; the local files are the tables the tab was built from.
2. **The page's values from production's run of the replication at 06:30 UTC** (`runs/repl1020.out`), where each of the four keys equalled the replication's own.
3. **NYISO's New York City zone and the node 7RNCHSLR_ALL** stand for their kinds: the replication's own rows.

## For Samuel's ruling

- None new.

## Files

- New: `package/tests/test_tab_figures.py`, `package/tests/tab_figures.json`, this report. Changed: `docs/methods/packages.md` (a section).
