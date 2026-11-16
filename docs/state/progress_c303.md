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
| The method note `docs/methods/datacenter_tracker.md` | open | |
| The replication `replication/datacenter_tracker/replicate.py`, N of N | open | |
| The Stata do-file, five headline figures | open | |
| The cross-check table with its sources | open | |
| The decisions block on the page | open | |
| The faults this work finds; the four `ruling` rows in plain words | open | |
| The landing request row | open | |

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

None yet.
