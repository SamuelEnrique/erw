# Progress of chain 303: the datacenter tracker and the deal tracker to the five tools' done line (sessions 7400 to 7429, portable-laptop)

Energy Research Warehouse (ERW). The chain file: `queue/done/303-night-16-november-portable-trackers-done-line.md`. One line a step, with its state and the session. The work is on `wip/7400-trackers` (worktree `C:\Users\lossa\Documents\erw-c303`); this file, the resume pointer and the landing request rows are on main. Model spend: USD 0 (rule 1, `ERW_SPEND_CAP_USD=0`).

States: `done` with the commit, `needs the key` with the cost, `ruling` with the default taken, `waiting` with what for, `open`.

## The ground

| Step | State | Session |
|---|---|---|
| Precheck, fetch, memory and disk | done (precheck passed 09:11 UTC; 1.7 GB of memory free of 15.6, so no build; 277 GB of disk; no freeze) | 7400 |
| Session numbers 7400 to 7429 and queue numbers 330 to 339 | done (free on origin/main, every branch and every queue file) | 7400 |
| Worktrees of landed branches removed | done (six removed: `erw-p2-row`, `erw-p3-5200`, `erw-p3-5250`, `erw-p3-5264`, `erw-p4`, `erw-p4-row`, their ignored `runs/` entries kept in `runs/kept/<worktree>/` of the main checkout; the seventh, `erw-p1-269`, moved to `erw-c303` and reused for this chain; `erw-p2-5150` and `erw-p2-5157` are not landed and stay) | 7400 |
| Resume files of this machine in `queue/next/` | done (none: 310 is the data machine's, 321 the old laptop's; both left) | 7400 |
| The resume file `queue/next/330-resume-chain-303.md` | done `debaa965f` | 7400 |
| The before snapshot of the live pages (rule 8) | done (`runs/snapshots/c303-before`, 25 pages, 0 failed, 09:15 UTC) | 7400 |
| This progress file | done (this commit) | 7400 |

## Goal 1: the datacenter tracker, `/datacenters`

| Step | State | Session |
|---|---|---|
| The method note `docs/methods/datacenter_tracker.md` | done `8ae74bfef` (thirteen sections and the sign-off block; its figures held to the day's by a test) | 7401 |
| The replication `replication/datacenter_tracker/replicate.py`, N of N | done `1e0eb26ba`: 454 of 454 inside the tolerance on the live set's 458 rows of 16 November 09:18 UTC, against the page's own functions | 7400 |
| The Stata do-file, five headline figures | done `dd059732e` (expected values at its top; not run, Stata is not on this machine; its Python mirror prints the same five lines) | 7403 |
| The cross-check table with its sources | done `dd059732e`: ten rows (Berkeley Lab, EIA, ERCOT, PJM, Dominion, AEP), each read from the publisher's own file, robots first; MISO not requested (paused) | 7403 |
| The decisions block on the page | done `8ae74bfef`: twelve choices, each with its default and source on hover, at the foot of both views; type checked, not built | 7402 |
| The faults this work finds; the four `ruling` rows in plain words | done `8ae74bfef`: rows 15 to 21 (15 fixed with a test; 17 `ruling`, default the page unchanged; 16 and 18 to 21 `data machine`); the four rulings restated with their defaults | 7400 to 7403 |
| The landing request row | done (row 33 of `docs/state/landing_request_portable.md`, head `dd059732e`, marked not yet requested while the deal tracker moves the head) | 7403 |

## Goal 2: the deal tracker, `/deals`

| Step | State | Session |
|---|---|---|
| The method note `docs/methods/deal_tracker.md` | open | |
| The replication `replication/deals/replicate.py`, N of N | open | |
| The Stata do-file | open | |
| The cross-check: published tallies, and the twenty largest rows against their headlines | open | |
| The decisions block on the page | open | |
| The faults; the three `ruling` rows in plain words | open | |
| What the re-extraction would change (not run) | open | |
| The landing request row | open | |

## The last session

| Step | State | Session |
|---|---|---|
| The signature pack `docs/reviews/trackers-signature-pack-2026-11-16.md` | open | |
| The note `docs/state/note_2026-11-17_portable_c303.md` | open | |
| The landing request row for the final stack | open | |
| The resume file removed from `queue/next/` | open | |
| `chain_queue.py next` (exit 3 expected) | open | |

## Needs the key

- **Four megawatt rows of the datacenter tracker found wrong against their stories' own words** (faults rows 18 to 21: a tenant named as operator, 1,000 MW; a fuel-cell plant's 702 MW; a turbine project's 1,200 MW; the Utah join, 9,400 MW). A re-extraction of those facilities' stories would correct them. Estimated cost: under USD 1 for the four rows' stories; the whole news table's rebuild is the data machine's to price. Not run.

## For Samuel's ruling (each with the default taken)

- **The public repository tracks the held tables' own files** (`warehouse/output/datacenter_facilities.csv`, `energy_deals.csv`, both evidence tables and three more). Default: nothing changed (session 7400's report).
- **The views by operator read the operator alone**, so "operator not stated" holds 26,124 of the 28,254 MW stated (datacenter faults row 17). Default: unchanged, said in the page's decisions.
- **PJM's two figures in the cross-check** (its load report, and Dominion's presentation on its committee page). Default: kept, as facts with links.
