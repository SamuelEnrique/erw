# Session 387 report: reliability, 21 October's scheduled runs

21 October 2026, from 06:05 UTC, unattended, on lab-desktop (the data machine), the first session of the chain of 21 October, day (`queue/done/016-day-21-october-data.md`), session 384's part (b). Model spend USD 0. Pulls: none (Supabase's health table and pg_cron's own tables read; GitHub's API for the runs).

## Read these first

- **The chain file's "from about 05:00 UTC" was wrong.** GitHub's daily run is dispatched at 14:00 UTC (`erw-daily`, `0 14 * * *`). The run of 20 October at 05:14 UTC was a manual dispatch. So this session wrote 21 October's file as the day stood at 06:05 UTC, with no daily step in it, rather than wait until after 14:00 UTC (Samuel's instruction of 05:15 UTC was not to wait for a time of day). The daily's steps of 21 October are left for a later session; session 389's chain file names them.
- **No step failed by 06:05 UTC** (46 steps).
- **The scheduled jobs did not start for six hours: pg_cron's "job startup timeout"** (`queue/summary/2026-10-21-health.md`, "## Root causes"). From 23:30 UTC on 20 October to 05:15 UTC on 21 October, 47 of pg_cron's runs failed this way. It had never happened before in this database: 3,838 runs succeeded since 2 October. A failed run makes no request, so GitHub received no dispatch, and no 15-minute run was made from 02:30 to 05:30 UTC. Every request pg_net did make was answered 204. Postgres has not restarted since 26 September. With `cron.use_background_workers` off, each job opens a connection to `localhost`, and that connection did not start in time; what held it is not visible from inside the database. Runs succeed again from 05:30 UTC. **This touches today's daily, which is dispatched by the same path at 14:00 UTC.**
- **The green streak cannot see such a gap.** `health_days.json` (read, not written): `green_days` 0, counted to 19 October. A day counts as missing only when a job made no run at all that day. So 21 October stays green with six hours of runs missing, if no step fails.

## Checks

| What | Exit | Notes |
|---|---|---|
| `scripts/precheck.py` | 0 | |
| `warehouse/health.py summary --day 2026-10-21 --out runs/s387_health_2026-10-21.md` | 0 | 46 steps; written under runs/, then copied, so `site/data/health_days.json` was not touched |
| `warehouse/supabase/scheduler.py --status` | 0 | read only: six jobs active, the last answers 204 |
| `runs/s387_dispatch.py`, `s387_cron_days.py`, `s387_cron_more.py`, `s387_pg_start.py` | 0 | read only: `cron.job`, `cron.job_run_details`, `net._http_response`, `pg_stat_activity`, settings |

## Landing

The queue move of `016-day-21-october-data.md` (`013ebdd8`): `chain_queue.py next` committed it and did not push it, and this session pushed it to main at 05:48 UTC. No deployment of `013ebdd8` appeared by 06:04 UTC, though the queue commit before it deployed in 3 minutes. The page snapshots: `s387-queue-before` (05:38 UTC) against `s387-queue-after2` (06:04 UTC): 0 differences on 25 pages, expected, since a queue file changes no page. A first `s387-queue-after` was taken at 05:48:54 UTC by a poll that had been stopped, before the push; it is not used. This session's files land on `task/387-health`.

## Decisions made without you

1. 21 October's file written as the day stood at 06:05 UTC, not after the daily run.
2. No change to `health.py`'s count of a missing day, and none to pg_cron's settings.
3. GitHub's API polled with this machine's `GH_TOKEN`, for reads only, once the public API's 60 requests an hour were spent (by the deploy polls of 386).

## For Samuel's ruling

- **pg_cron's connections**: turn `cron.use_background_workers` on, which is a database setting and needs a restart (Supabase's dashboard or support). Or first read the project's resource graphs and logs for 23:30 to 05:30 UTC, which a session cannot reach. Best before 14:00 UTC.
- **The streak**: should a job far below its expected count (for example under half) end the streak as a missing day does?

## Files

- New: `queue/summary/2026-10-21-health.md`, this report.
- On this machine (not in git): `runs/s387_health_2026-10-21.md/`, `runs/s387_*.py` and their `.out` files.
