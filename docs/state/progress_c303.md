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
| The method note `docs/methods/deal_tracker.md` | done `ffda8bc69` (twelve sections and the sign-off block; its figures held to the day's by a test) | 7405 |
| The replication `replication/deals/replicate.py`, N of N | done `9e2b61d17`: 1,123 of 1,124 inside the tolerance on the live set's 590 rows of 16 November 09:49 UTC; the one difference named (the capital view's file says 529 rows, built 6 November) | 7404 |
| The Stata do-file | done `ffda8bc69` (six lines and a table by year and kind, expected values at its top; not run, Stata is not on this machine; its Python mirror prints the same) | 7406 |
| The cross-check: published tallies, and the twenty largest rows against their headlines | done `ffda8bc69`: six rows against CEBA, BloombergNEF and LevelTen, each read from the publisher's own page, robots first; all twenty of today's lists read against their stories: 17 figures in a headline, 3 rows of 11 and 13 November not checkable on this machine | 7406 |
| The decisions block on the page | done `ffda8bc69`: thirteen choices, each with its default and source on hover, above session 465's list; type checked, not built | 7405 |
| The faults; the three `ruling` rows in plain words | done `ffda8bc69`: rows 22 to 29 (22, 23 and 28 `ruling`, defaults unchanged; 24 to 27 `data machine`; 29 `open`, needs a build); the three rulings restated with their defaults | 7404 to 7406 |
| What the re-extraction would change (not run) | needs the key: of the 529 older rows, by a reading of their stories' titles, about 22 would leave as not a deal, about 51 as not energy's (only if that rule is written into the prompt: it is in none), about 4 would change kind, about 19 cannot be told, about 433 stand. USD 3.0 (814 stories) to USD 10.6 (2,899 stories) | 7405 |
| The landing request row | done (row 33, the same branch: the final head below) | 7407 |

## The last session

| Step | State | Session |
|---|---|---|
| `/companies`, only if no branch of the data machine holds `replication/companies` | not taken: `origin/wip/c301-data` holds it (checked after a fetch at 10:08 UTC), so the chain stops after its two goals | 7407 |
| The signature pack `docs/reviews/trackers-signature-pack-2026-11-16.md` | done `7a39daafa` (a file only: nothing published) | 7407 |
| The note `docs/state/note_2026-11-17_portable_c303.md` | done `7a39daafa` | 7407 |
| The landing request row for the final stack | done: row 33, `wip/7400-trackers` at `7a39daafa` (main merged at `e77e1ed3a`), requested | 7407 |
| The resume file removed from `queue/next/` | done `07ebc2690` (alone) | 7407 |
| The after snapshot of the live pages and its comparison (rule 8) | done: `runs/snapshots/c303-after`, 25 pages, 0 failed, 10:19 UTC; `compare c303-before c303-after`: **0 differences in all** (expected: every push of this chain to main held a queue file, this file or a landing row, and no page is live) | 7407 |
| `chain_queue.py next` (exit 3 expected) | done: exit 3, "queue/next/ holds nothing for portable-laptop" (the one file left, 310, is the data machine's). **CHAIN DONE.** This line's own push is the chain's last: a docs file, after the snapshot above | 7407 |

## Needs the key

- **Four megawatt rows of the datacenter tracker found wrong against their stories' own words** (faults rows 18 to 21: a tenant named as operator, 1,000 MW; a fuel-cell plant's 702 MW; a turbine project's 1,200 MW; the Utah join, 9,400 MW). A re-extraction of those facilities' stories would correct them. Estimated cost: under USD 1 for the four rows' stories; USD 2.9 for every story the datacenter extraction has checked (1,077 at USD 0.00273). Not run.
- **A second reading of the 529 deals extracted before 6 November** (the deal tracker's method note, section 10; deals faults rows 25 and 27). Estimated cost: USD 3.0 for the 814 stories behind those rows, USD 10.6 for every story the deals extraction has checked (2,899 at USD 0.00365). Not run.
- **Sum: about USD 4 for the two narrow readings, about USD 13.5 for both tables whole.** No model was called by any session of this chain; no other key or route was tried.

## For Samuel's ruling (each with the default taken)

- **The public repository tracks the held tables' own files** (`warehouse/output/datacenter_facilities.csv`, `energy_deals.csv`, both evidence tables and three more). Default: nothing changed (session 7400's report).
- **The views by operator read the operator alone**, so "operator not stated" holds 26,124 of the 28,254 MW stated (datacenter faults row 17). Default: unchanged, said in the page's decisions.
- **PJM's two figures in the cross-check** (its load report, and Dominion's presentation on its committee page). Default: kept, as facts with links.
- **The deal tracker's two readings of a grid** (deals faults row 22: the table reads a grid a story names, the three views the state alone). Default: unchanged.
- **A folded pair drops a figure only the folded row states** (deals faults row 23: 433 MW of the loan to Vistra is in no sum). Default: the row kept stands as extracted.
- **"A deal is energy's where its asset is energy" is written in no prompt and no rubric** (deals faults row 28). Default: not written; the note and the page's decisions say what the table holds.
- The seven rulings of the faults read of 11 November (datacenter rows 1, 4, 7 and 11; deals rows 1, 16 and 17) are restated in plain words with their defaults in the two faults files and in the signature pack, section 3.
