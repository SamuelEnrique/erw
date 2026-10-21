# Session 435 report: the real-time node prices, the days held

21 October 2026, from 07:27 UTC, unattended, on lab-desktop (the data machine), the fifth session of the chain of 21 October, night (`queue/done/016-night-21-october-data.md`). Model spend USD 0. Pulls: ERCOT 0 of 40 (below). No load.

## Read these first

- **`dm_node_rt` has not run on a schedule yet.** Session 376 added it to `warehouse/run_data_machine.sh`, and that landed at 21:14 UTC on 20 October, after that day's run (which stopped at 18:06 UTC). Its first scheduled run is today's, at 10:00 Pacific (17:00 UTC). It did not run at 10:00 Pacific on 21 October because that hour has not come; this session ran at 00:27 Pacific.
- **Held now** (this machine, `warehouse/output`):
  - `node_basis_daily`: 957,969 rows, operating days 1 October 2025 to 20 October 2026; its real-time columns (`rtm_mean`, `rtm_basis`, `rtm_spread_4h`) for **22 days, 28 September to 19 October** (as session 376 left them).
  - `ercot_node_prices_hourly`: **499,080 rows of the owner's 500,000** (920 to spare), 16 July to 21 October 04:00 UTC, its real-time hours to 20 October. The builder keeps the newest days under the ceiling, so each day gained drops the oldest.
  - `ercot_rtm_node_prices` (the saved 15-minute files): 674,232 rows, 28 September 04:45 UTC to **20 October 16:45 UTC** (the run of 20 October saved 96 files, 29,952 rows counted against the day's ceiling of 500,000).
- **No request to ERCOT, so no day gained.** The next whole Central day, 20 October, needs the files from 17:00 UTC on 20 October to 05:00 UTC on 21 October: about 49 files and the list, over this session's ceiling of 40. A part of a day adds nothing, because `node_basis.py --daily` takes only whole days. ERCOT's list keeps seven days, so today's `dm_ercot_node_prices` (17:00 UTC) saves every file from 16:45 UTC on 20 October on, in one pass under its own ceiling, and `dm_node_rt` then adds 20 October (and 21 October once it is whole, the next day).
- **No load into the live set.** `node_basis_daily` is the table whose whole write of 958,000 rows at 20:35 UTC on 20 October heads the causes in `docs/state/database_2026-10-21.md`. Nothing changed here to load, and the run script itself leaves its load to a session or a person.

## Checks

| What | Exit | Notes |
|---|---|---|
| `scripts/precheck.py` | 0 | |
| the three tables read (rows, first and last time, the real-time days) | 0 | no request |

## Decisions made without you

1. No pull: 40 requests cannot complete a day, and a part day is not used; the scheduled step gets them all at 17:00 UTC.
2. No load: nothing changed, and `node_basis_daily`'s loads are the first suspect for the database's night.

## For Samuel's ruling

- `node_basis_daily` in the live set (the database note's ruling): each real-time day gained rebuilds the table, and its load must go through the gate.

## Files

- New: this report.
