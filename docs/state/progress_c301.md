# Progress of chain 301 (data machine, lab-desktop, sessions 7000 to 7049)

The one record a restarted session needs (`queue/done/301-day-16-november-desktop-open-faults.md`, "The progress file"). One line a row or step: its state and the session. States: `done (<commit>)`, `not a fault now` (what was checked), `needs the key` (the cost), `ruling` (the default taken), `waiting` (what for), `open` (not yet taken).

The chain's code branch: `wip/c301-data` (worktree `C:\Users\Shared\Documents\erw-c301`). Tables are written in the main checkout under the data lock.

## Session 7000: the ground

- Precheck: passed, on duty until 2026-11-17 00:52 UTC. Freeze: none. Session numbers 7000 to 7003 free on every branch. Memory 6.9 GB free of 16; disk 236 GB free. Chain 285's session not running; the data lock free. (7000)
- Worktree `erw-c278q` (detached, merged) removed, its one ignored folder `scripts/__pycache__/` listed first; the others hold unlanded commits and stay. (7000)
- File 286 parked (`queue/parked/`); 284 and 300 already parked by session 7200; no data machine resume file in `queue/next/`. (7000)
- Resume pointer `queue/next/310-resume-chain-301.md` pushed. (7000)
- Landing desk: no row requested in the four landing request files; no data request row since 16 November. (7000)

## Goal 1: the open `data machine` rows

| Tool | Row | State | Session |
|---|---|---|---|
| deals | 9 | not a fault now: both rows kind compute_capacity in the live set | 7000 |
| deals | 10 | needs the key: v2 re-extraction, about USD 3 | 7000 |
| deals | 11 | needs the key: v2 re-extraction, about USD 3 | 7000 |
| deals | 12 | not a fault now: v2 fields in the live set (kind 590 of 590) | 7000 |
| deals | 13 | needs the key: v2 re-extraction, about USD 3 | 7000 |
| datacenters | 8 | not a fault now: v2 keys in the live set (grid 178 of 458; PJM, MISO loads; timeline 9 rows) | 7000 |
| companies | 17 | done (b67b7cf92, rebuild 347fde024, wip/c301-data); lands with the chain | 7001 |
| companies | 18 | done (b67b7cf92, rebuild 347fde024, wip/c301-data); lands with the chain | 7001 |
| companies | 19 | done (b67b7cf92, rebuild 347fde024, wip/c301-data); lands with the chain | 7001 |
| companies | 20 | done (b67b7cf92, rebuild 347fde024, wip/c301-data); lands with the chain | 7001 |
| companies | 21 | done (b67b7cf92, rebuild 347fde024, wip/c301-data); lands with the chain | 7001 |
| companies | 22 | done (b67b7cf92, rebuild 347fde024, wip/c301-data); lands with the chain | 7001 |
| companies | 23 | done (b67b7cf92, rebuild 347fde024, wip/c301-data); lands with the chain | 7001 |
| companies | 24 | done (b67b7cf92, rebuild 347fde024, wip/c301-data); lands with the chain | 7001 |
| policy | 5 | open | |
| policy | 7 | open | |
| policy | 12 | open | |
| policy | 13 | open | |
| policy | 15 | open | |
| policy | 18 | open | |
| policy | 25 | open | |
| attention | 2 | open | |
| attention | 7 | open | |
| attention | 15 | open | |
| attention | 16 | open | |
| attention | 17 | open | |
| attention | 18 | open | |
| attention | 20 | open | |
| battery | 7 | open | |
| battery | 10 | open | |
| generator | 2 | open | |
| grid | 2 | open | |
| datacenter cost | 4 | open | |
| periodicals | 48 | open | |
| periodicals | 61 | open | |
| periodicals | 77 | open | |
| periodicals | 129 | open | |

## Goal 2: the large-load waits

- open

## Goal 3: the CAISO's FERC compliance filing on large loads

- open

## Goal 4: replication mirrors (companies, policy, attention)

- open

## Needs the key

- Deals rows 10, 11, 13: the re-extraction of the 899 stories behind energy_deals with the v2 prompt (Sonnet 5.5), about USD 3. Until then the rows stand (held whole under the license hold).

## For Samuel's ruling

## Decisions made without you
