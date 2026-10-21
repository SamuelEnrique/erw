# Session 433 report: the board's ERCOT day-ahead, stopped on 15 October

21 October 2026, from 07:24 UTC, unattended, on lab-desktop (the data machine), the third session of the chain of 21 October, night (`queue/done/016-night-21-october-data.md`). Model spend USD 0. Pulls: ERCOT 0 of 12 (every day-ahead hour of 16 to 20 October is already held here).

## Read these first

- **The tiles' table.** The board's ERCOT tiles are rows of `site/data/board.json`, written by `warehouse/derived/board_page.py` from its hourly store of nine price tables (ERCOT's from `ercot_all_hub_prices_history`, then `iso_dam_hub_prices` and `iso_rtm_hub_prices`). `warehouse/derived/page_keep.py` then takes the new build row by row: a held row is kept when the new one is older or its history shorter (the owner's rule of 6 October: "never writes a thinner board").
- **Where they stop.** On main the ERCOT day-ahead tiles end on 15 October and real time on 14 October. Every commit of the board from 15 October (this machine's of 15 to 19 October, GitHub's two of 20 October) holds those dates, while CAISO, NYISO and SPP reach 20 October in GitHub's builds.
- **Why, in three parts, each with its fix already on main:**
  1. **From 15 to 19 October Redivis refused every export** ("Cannot export more than 100GB within a 30 day period"; the root causes of 16 to 19 October in `queue/summary/`). GitHub's daily run stopped at its restore, so no ERCOT day-ahead was pulled until its runs of 19 and 20 October. This machine's `dm_sync` reads Redivis to decide what is behind, so its tables fell behind too: its board log of 19 October reads 819,276 complete hours of the ERCOT history, against 820,572 on 20 October (1,296 hours more: nine days across six hubs). Fixed: the restore reads the archive first (session 305), and session 373 restored this machine (201 tables current).
  2. **The runner never advances ERCOT's tiles, by design.** It holds no long ERCOT history, so its ERCOT rows are always shorter than the held ones, and `page_keep.py` keeps the held rows. The ERCOT tiles move only with this machine's daily commit.
  3. **This machine's run of 20 October built them current and did not commit them.** Its board build at 17:41 UTC holds ERCOT day-ahead through 20 October (`board_page_20261020T174126Z.log`; the uncommitted `site/data/board.json` in the main checkout, `built` 17:42:53 UTC). The run then ended at 18:06 UTC with 0xC000013A before its commit step, which is session 384's cause, fixed by its `lock.py` change.
- **The days regained**: none committed by this session. The main checkout keeps the daily run's uncommitted page files as they are (the chain's rule). This machine's daily run of 21 October (17:00 UTC) builds and commits the board from tables now current, and GitHub's run of 14:00 UTC pulls 21 October's day-ahead. Every day-ahead hour of 14 to 20 October for `ercot:HB_HUBAVG` is held here, 24 a day, in both `iso_dam_hub_prices` and `ercot_all_hub_prices_history`, so no request to ERCOT was needed.
- **No code fault found that is not already fixed**, so no new fix and no new test. One weakness stays: a held tile five days old still reads `status: ok`.

## Checks

| What | Exit | Notes |
|---|---|---|
| `scripts/precheck.py` | 0 | |
| the board's ERCOT, CAISO, NYISO and SPP dates in the last twelve commits of `site/data/board.json` | 0 | git only |
| the board build logs of 15 to 20 October | | `warehouse/output/logs/board_page_*.log` |
| ERCOT day-ahead hours a day, 14 to 21 October, in the two tables | 0 | 24 each day to 20 October |

## Decisions made without you

1. No pull from ERCOT: the days are held here; 21 October's day-ahead comes with today's scheduled runs.
2. The board not rebuilt and not committed by this session, since that would overwrite the daily run's uncommitted page files that the chain's rule keeps.

## For Samuel's ruling

- A tile kept by `page_keep.py` and two or more days behind the board's newest day could say so (`status: stale`, a line on the tile) instead of `ok`. That changes what the board shows, so it is yours.

## Files

- New: this report.
