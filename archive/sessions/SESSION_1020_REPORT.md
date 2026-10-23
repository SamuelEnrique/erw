# Session 1020 report: the next file, then chain 070's end, checked

23 October 2026, from about 06:28 UTC, on samueloldlaptop, unattended, in the worktree `C:\Users\lossa\Documents\erw-1020` on `wip/1020-allgrids` (cut from `wip/1019-records`, main merged). Chain `queue/done/071-night-23-october-code-allgrids-packages.md`, session 1020, the first. Model spend USD 0. No warehouse data written; no request to a publisher. The reads: the live set with the anon key, production's pages with the internal cookie, the warehouse's CSVs rebuilt earlier into `runs/archive_restore/`.

## Read these first

- **The next file is on main**: `queue/next/072-day-23-october-code-allgrids-packages-2.md`, sessions 1042 to 1063 for this machine, committed alone and pushed at 06:29:55 UTC (`452e39ef`; snapshots `s1020q-before` and `s1020q-after`, 0 differences). Its starting point: chain 070's last landing not yet served; the data machine's chain 049 (reserve margins for every grid, an ERCOT node's county and zone) as the tables this machine wires next; four new rules from chain 070's slips.
- **Chain 070 is on main but not all served.** 1000 to 1014 were served by 05:05 (0 differences). 1015 to 1019 merged at 05:42 (`2e31b027`); Vercel answered "rate limited", and production still lacked `/data`'s copy controls (`data-copy-line`) at 06:27 and again at 06:29. The records are on `wip/1019-records` and land with this session.
- **The replication against production: 123 figures, 111 beside the page, 0 differ**, the same counts as chain 065's session 799.
- **The live set ceiling was passed**: about 32 requests against 20. The replication reads the hourly intensity for three grids' twelve months a thousand rows a request (about 9,000 rows each, so 10 requests each), plus the four peaks and the durations. The script did not count; it now does (below).

## What to review

1. `queue/next/072-day-23-october-code-allgrids-packages-2.md` (on main).
2. `warehouse/replication/siting.py`'s last line, and `docs/methods/siting.md`, "The replication", the line "What it costs".

## What was done

- **The queue's move**: `chain_queue.py next` took 071 at 06:28 (`e17ce84d`), pushed to main at once (snapshots `s071move-before` and `s071move-after`, 0 differences). `chain_queue.py list` after the 072 push: 3 waiting, 1 for this machine (072); 051 (data) and 080 (portable laptop) left for their machines.
- **Session numbers**: 1042 to 1063 were held by no queue file, no remote branch and no report when 072 was written. The personal laptop's 080 says "the old laptop holds 1000 to 1049"; 072 says so for 1050 to 1063, and its first session checks again.
- **The replication's count**: `rest()` counts each request (`LIVE_REQUESTS`), and the script prints `N requests to the live set` after the figures' line. Test 1020: three fake pages of 1,000, 1,000 and 5 rows are three requests and 2,005 rows; the count's line comes after the figures' line.

## Checks

| Check | Exit | Result |
|---|---|---|
| precheck | 0 | on duty until 22:28 UTC |
| freeze status | 0 | no freeze |
| the 071 move's push, with snapshots | 0 | 0 differences |
| the 072 file's push, with snapshots | 0 | 0 differences |
| the replication against production, `--tables runs/archive_restore` | 0 | 123 / 111 / 0 differ; about 32 live set requests (counted from the rows, after the run) |
| tests 1020, 746, 712 | 0 | 9 tests OK |

## The landing

Lands with the next landing of this chain (with `wip/1019-records`, from which this branch was cut).

## Decisions made without you

1. **072 numbers 1050 to 1063 as well as 1042 to 1049**, the rule chain 071 gave it; the other machines' files say only that this machine holds 1000 to 1049, so 072 names its numbers and its first session checks them.
2. **The replication was not run a second time to count its requests**: that would have doubled the overrun. The count is from the rows the three reads return (`runs/archive_restore/carbon_intensity_hourly.csv`, 8,904 to 9,096 rows a grid from October 2025).
3. **The after snapshot of 1015 to 1019 was taken at 40 minutes with the change not served**, as the rule says; the record says "not yet served", and the next landing's probe looks for `data-copy-line` with its own mark.

## For Samuel's ruling

- None new. The ceiling's overrun is reported here; it published nothing and wrote nothing.

## Files

- New: `queue/next/072-day-23-october-code-allgrids-packages-2.md` (on main), `tests/test_session1020.py`, this report.
- Changed: `warehouse/replication/siting.py` (the count), `docs/methods/siting.md` (one line).
