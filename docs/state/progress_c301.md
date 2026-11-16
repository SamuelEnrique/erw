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
| companies | 24 | done (rebuild 347fde024; gate a passed, landing as task/7002-landing) | 7001 |
| policy | 5 | not a fault now: monitor.json built 2026-11-15 | 7002 |
| policy | 7 | done (ef3c63cc1, rebuild 0a710ba33, wip/c301-data; gate a passed, landing as task/7002-landing) | 7002 |
| policy | 12 | done (ef3c63cc1, rebuild 0a710ba33, wip/c301-data; gate a passed, landing as task/7002-landing) | 7002 |
| policy | 13 | done (ef3c63cc1, rebuild 0a710ba33, wip/c301-data; gate a passed, landing as task/7002-landing) | 7002 |
| policy | 15 | data side done (0a710ba33); page change in data_ready_c301.md row 7 | 7002 |
| policy | 18 | done (ef3c63cc1, rebuild 0a710ba33, wip/c301-data; gate a passed, landing as task/7002-landing) | 7002 |
| policy | 25 | check done (ef3c63cc1); needs the key for the read redone, about USD 0.02 | 7002 |
| attention | 2 | done (wip/c301-data, after gate a); rides in gate b | 7003 |
| attention | 7 | done (wip/c301-data, after gate a); rides in gate b | 7003 |
| attention | 15 | prompt v4 done; needs the key to classify again, about USD 0.10 | 7003 |
| attention | 16 | done (wip/c301-data, after gate a); rides in gate b | 7003 |
| attention | 17 | done (wip/c301-data, after gate a); rides in gate b | 7003 |
| attention | 18 | done (wip/c301-data, after gate a); rides in gate b | 7003 |
| attention | 20 | done (wip/c301-data, after gate a); rides in gate b | 7003 |
| battery | 7 | not a fault now: battery_stack_monthly holds October 2026 (chain 267) | 7004 |
| battery | 10 | not a fault now: price_years_by_window rebuilt 14 November (CAISO 79.80) | 7004 |
| generator | 2 | ruling: data_requests_five_tools row 2 (six tests vs 7 October CSV); default steps off | 7004 |
| grid | 2 | not a fault now: chain 278 wrote the five files 14 November | 7004 |
| datacenter cost | 4 | not a fault now: LZ_NORTH 34.07 (price_years_by_window, 14 November) | 7004 |
| periodicals | 48 | not a fault now: US48 to 2026-11-14 in the live set | 7004 |
| periodicals | 61 | waiting: CAISO, SPP, EIA-930 days of 5 to 9 November being refilled (lock); ERCOT a ruling | 7004 |
| periodicals | 77 | needs the key: datacenter re-extraction, about USD 0.70 | 7004 |
| periodicals | 129 | ruling: Google News titles (ruling 3); default titles as held | 7004 |

## Goal 2: the large-load waits

- Robots and terms read again; new copies pulled: NYISO, Bonneville, Alberta October and November 2026 (111 of 300 requests). Code for the summary table and the dated totals on wip/c301-data (7008). Waiting for the data lock: --write, the two new tables, registrations. (7008)
- Written, validated, covered, archived and registered: `large_load_wait_summary` and `utility_large_load_queue_totals` (license record, release list, package catalogue, Redivis draft); landed at `f4cc50518`. (7008, 7013)

## Goal 3: the CAISO's FERC compliance filing on large loads

- 16 November 15:08 UTC: not filed (the same bytes, sha256 578c69995d9a0388). (7017)

- 16 November about 09:45 UTC: not filed (the process page's bytes unchanged, sha256 578c69995d9a0388). Checked again at a later session's start. (7004)

## Goal 4: replication mirrors (companies, policy, attention)

- companies: replicate.py 381,721 of 381,721; replicate.do (7005)
- policy: replicate.py found row 32 (27 kept DOE rows without fields; fill_bare); N of N after the next pull; replicate.do (7006)
- attention: replicate.py 3,407 of 3,407; replicate.do (7007)

## Landings

- Gate a (sessions 7000 to 7002) landed at `bce9303d6`, 0 differences. (7009)
- Gates b, c and d failed (tests 4101 and 5506; 5161 and 7202; 726), each fixed. (7009, 7012)
- Gate e (`de68a6669`, sessions 7003 to 7013 and the desk's rows: old laptop 15 and 16, portable 33) landed at `f4cc50518` (run 43870558464), snapshots `before-de68a666` and `after-de68a666`: 0 differences. (7013)
- Gate f (`wip/c301-tail`, `f04c808e3`) failed on test 204 alone (the order of `DATA_MACHINE`), fixed on `wip/c301-after`. (7015, 7016)
- Gate g (`wip/c301-after`, `4f2d076f5`) started 14:12 UTC; lands after 16:15 UTC. Later work on `wip/c301-later`. (7016)
- Gate g passed (14:46 UTC); gate h (`wip/c301-later`, `44d82be7a`, gate g's content and the eight tools' done line) passed every step at 15:44 UTC; it lands at 16:15 UTC alone. Later work on `wip/c301-last`. (7018, 7019)

## The eight lab-desktop tools of the done line

| # | Tool | Replication | Findings | Session |
|---:|---|---|---|---|
| 17 | `/board` | 30,607 of 30,607 | none | 7010, 7013 |
| 18 | `/prices` | 74,258 of 74,258 | none | 7011 |
| 19 | `/prices/compare` | 578 of 578 | an hour of zero was counted below zero (fixed) | 7012 |
| 20 | `/supply` | 5,125 of 5,125 | the file three weeks behind (refreshed) | 7013 |
| 21 | `/storage` | 63,075 of 63,075 | CAISO's revised battery values not in the tables of record (read again) | 7014 |
| 22 | `/demand` | 24,241 of 24,245 | the four are EIA's late Lower 48 hours (not a fault) | 7014 |
| 23 | `/curtailment` | 11,515 of 11,515 | the profile and `/mix/v2` a month behind (fixed at the cause); ERCOT's limit at the autumn hour (ruling) | 7014 |
| 24 | `/queues` | 17,254 of 17,254 | none | 7014 |

Each has `replication/<tool>/replicate.py` and `replicate.do` (not run: no Stata here). Not yet: the browser read of each as its reader, and the curtailment shares, free energy and worth files.

## The done line's data requests (`docs/state/data_requests_done_line.md`)

- Done: 4 (code; the rebuild waits for the data lock), 7, 10, 11, 12, 13, 14 (answered), 15, 16, 17, 18, 24, 26, 27, 29, 33 (code; the tables at the next vintage), 34. (7015 to 7017)
- Done or answered in session 7019: 2, 3, 23 (the old laptop's files), 5, 28 (wait for their branches), 9, 19 (migration 037 for a person to apply), 20, 21, 22 (for Samuel), 6 and 25 (a) (the register's site copy waits for the lock), 8 (the tables wait for the lock); code and trials for 30, 31, 35, 36. (7019)
- Waiting for the data lock (the GitHub daily run holds it from 14:10 UTC): `runs/c301/lock_all.sh` (requests 4, 6, 8, 20, 31, 32, 36), then the two new tables of 30 and 35 with their registrations.
- Open: none unread; the writes above.

## Needs the key

- Policy row 25: the BOEM read redone, about USD 0.02.
- Attention row 15: opposition rows classified again under prompt v4, about USD 0.10 (all rows USD 2.20).
- Periodicals row 77: datacenter_projects re-extraction, about USD 0.70.

- Deals rows 10, 11, 13: the re-extraction of the 899 stories behind energy_deals with the v2 prompt (Sonnet 5.5), about USD 3. Until then the rows stand (held whole under the license hold).

## For Samuel's ruling

- Generator row 2: the six landing tests and 7 October's CSV (default: steps off, page ends September 2026).
- Periodicals row 129: Google News titles cut at 128 (default: as held).
- ERCOT's price days of 7 to 9 November: only through the paths ruling 2 freezes (default: not refilled).
- large_load_wait_summary: Bonneville's and Grant County PUD's terms unclear for derived statistics (default internal).

## Decisions made without you
