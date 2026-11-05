# The data machine's note of the chain of 21 October, day (written 21 October 2026, about 09:15 UTC)

Energy Research Warehouse (ERW), session 459, for Samuel. The data machine's chain of 21 October, day (sessions 452 to 459, `queue/done/018-day-21-october-data.md`, written by session 440), unattended on lab-desktop, from 08:40 UTC to this note's push. Model spend USD 0 in every session. Before it: the morning note of 22 October, [`docs/state/morning_2026-10-22.md`](morning_2026-10-22.md) (sessions 431 to 440, landed as `d874e467`, deployed 08:39 UTC, 0 differences).

## Read these first

- **`node_basis_daily` has no reader in Supabase** (session 456, [`docs/state/live_set_size_2026-10-21.md`](live_set_size_2026-10-21.md)). The pages read `node_basis_summary`, and nothing in the site, the package or Ask names the daily table. Its 957,969 rows are 27% of `series`, about 600 MB: the write of 20 October that heads the database note's causes. Out of the live set, no visitor loses anything. `ercot_rtm_price_adders` is read for one variable of eight: about 310 MB could go. Yours to rule.
- **The loader, values not stamps** (session 455, [`wip/455-loader`](https://github.com/SamuelEnrique/erw/tree/wip/455-loader), not landed). Three changes, with 10 tests and the earlier loader tests passing:
  - a row is written when its values move, not when only `retrieved_at` does (session 438's 30,232 rows would have been 8);
  - an older copy equal in value loads as unchanged (session 374's 31 refusals);
  - `series` is analysed, not vacuumed, after a load that changed 1% of it or less.
- **`ercot_peak_premium` built again, to October** (session 452). It had not run since 29 September: since the daily append step began writing live days into the year's history, every interval of the rolling table was in both, and the builder refused all 62,208. The same interval at the same price is now read once. The consolidated tables were split and rebuilt unchanged (hashes equal). Loaded.
- **The NOAA weather to 18 October** (session 453): 35 requests, 2,829,911 of the year's 6,000,000 rows. Not in the live set.
- **Four of the archive's five mismatches closed** (session 454). One finding: `restore_tables.py` restored an older stored copy from the bucket for two tables, rather than the archive's latest run. `restore.py --from-bucket` put the latest in place.
- **The day's runs are still to come** (sessions 457 and 458): the chain ran faster than its long ends. 21 October to 09:11 UTC: 134 steps, 0 failed; pg_cron on time since 05:30 UTC. GitHub's daily (14:00 UTC), this machine's (17:00 UTC), their commit and whether the day counts green are carried to the next file, marked "not before 23:00 UTC".

## What each session landed

| Session | Landed (on `task/452-459-day`) |
|---|---|
| 452 | `ercot_peak_premium.py` reads a repeated interval at the same price once, with `tests/test_session452.py` (3 tests); the two tables refreshed (monthly to October 2026), archived, coverage, loaded |
| 453 | The four NOAA tables to 17 and 18 October, validated, archived, coverage |
| 454 | `policy_reads_evidence` (5,143 rows), `price_board_spreads` (2,436), `grid_network_links` and `caiso_reliability_daily` as the archive's latest run; coverage; the proof equal for four |
| 455 | The report; the code on `wip/455-loader` |
| 456 | `docs/state/live_set_size_2026-10-21.md` |
| 457 | `queue/summary/2026-10-21-health.md` to 09:11 UTC |
| 458 | The report: the uncommitted board holds ERCOT through 20 October; `map.json` still 9 October |
| 459 | This note, and the next file (below) |

Also on the branch: the archive manifest's and the source registry's rows for the tables archived by sessions 432, 438 and 452. The record of this landing is in the next chain's note.

## Pulls against their ceilings

| Session | Pull | Used | Ceiling |
|---|---|---|---|
| 452 | none | 0 | 0 |
| 453 | NOAA | 35 requests; 17,165 rows counted | 6,000,000 rows a year (2,829,911 used) |
| 454 | the archive bucket | read | the bucket |
| 455 to 459 | none | 0 | 0 |

Nothing was asked of a paused publisher, and no new host.

## The database through the day

`runs/db_probe.log`: every probe open, 0.45 to 0.59 s, before and after session 452's load (08:44 UTC) and before session 456's reads (09:10 UTC). The live set's size: 2,322.3 MB before 452's load, 2,326.1 MB after.

## Decisions made without you (one line each; the reasons are in each report)

- 452: a repeated interval at the same price read once, two prices still refused; the fixed builder run by copying it into the main checkout and restoring the file after.
- 453: no load (not in the live set).
- 454: `datacenter_queue_positions` left for the daily (a tracked, uncommitted file); the rolling `grid_network_links` taken from the archive although it has fewer rows.
- 455: on a branch, not landed.
- 457, 458: no waiting; the daily runs' parts carried with an hour.

## Waiting for you, highest value first

1. **`node_basis_daily` out of the live set** (session 456): about 600 MB, no reader.
2. **The compute tier** (session 431), with Supabase's disk graphs for the night of 20 to 21 October.
3. **`wip/455-loader`**: values, not stamps; the vacuum after a large write only.
4. **Redivis storage** (about 0.6 GB free), and whether an unattended session may upload to the draft.
5. **A "not before" line for chain files** (session 457): `chain_queue.py next` holding a file until its hour, so that no session waits.
6. **`ercot_peak_premium` in `run_data_machine.sh`** (sessions 438 and 452).
7. Still open from the morning note: pg_cron's connections, the streak's blind spot, the stale-tile flag, the waiting rule, Vercel's deployment limit, the license rulings, the permission letters, `nyiso_load_queue`, "One alert policy", the daily task with no console window, the move under Ben's organization.

## The other machines

- **The code machine**: `019-night-21-october-code.md` (sessions 461 to 475) waits for it in `queue/next/`.
- **The third machine** runs `017-night-21-october-third.md` (sessions 441 to 451).
- **This machine**: its daily run starts at 17:00 UTC; the chain worker starts a session only when no Claude Code process is alive.
