# Session 431 report: the database, read before anything is written

21 October 2026, from 07:07 UTC, unattended, on lab-desktop (the data machine), the first session of the owner's chain of 21 October, night (`queue/done/016-night-21-october-data.md`, sessions 431 to 440). Model spend USD 0. Pulls: none. Nothing written to the database, nothing cancelled. Pushed on `wip/431-440-night`; landed nothing, as the part says.

## Read these first

- **`scripts/db_probe.py`, the database gate**, with `tests/test_session431.py` (6 tests). It makes one page-shaped read of `series` (1,000 rows of `iso_dam_hub_prices` in the key's order) under a statement timeout of 5 seconds, through `SUPABASE_DB_URL`. Exit 0 under 3 seconds, exit 1 when slower, empty, timed out or not connected. Each probe is a line of `runs/db_probe.log`. The chain's text names "the series table" without a table: `iso_hub_prices_history`, tried first, is held for its license and not in the live set (no rows), so the probe reads `iso_dam_hub_prices`, which the battery, seller and cost-of-power pages read.
- **The note: [`docs/state/database_2026-10-21.md`](../../docs/state/database_2026-10-21.md).**
  - The database was answering again by 07:08 UTC (probe 0.40 to 0.59 s all session).
  - The site's role `anon` has a 3-second statement timeout, and 25 of its statement shapes have a slowest run at about 2.9 s.
  - `series` is 2,142 MB against 512 MB of shared buffers.
  - This machine's load of 20 October (session 374, 20:26 to 20:48 UTC) wrote `node_basis_daily`'s 957,969 rows whole, 27% of `series`, and grew the database from 2,063 to 2,318 MB.
  - pg_cron's connections failed from 23:30 UTC (session 387).
  - The three likeliest causes, in order: the compute's disk throughput spent by the evening's writes; the series table outgrowing the compute's memory; many reads at once (no evidence found).
  - The compute tier, with `node_basis_daily` and `ercot_rtm_price_adders` in the live set, for your ruling.
- **Not the builds.** Every branch push of the night is "Canceled by Ignored Build Step", and production built 34 times in the 25 hours to 07:00 UTC. **Vercel now refuses deployments**: "Deployment rate limited, retry in 24 hours", on main's commits from about 06:30 UTC. So the site stays as `d88b74ed` left it, whatever lands, until the limit lifts.
- **The probe through the session**: 20 probes, 07:08 to 08:11 UTC, 17 open, between 0.45 and 0.59 s. The three closed probes are the first table's (no rows). The five-minute loop was stopped at 07:52 UTC by Claude Code for low memory and not restarted; a probe was run before and after each load of sessions 432 and 438 instead.

## Checks

| What | Exit | Notes |
|---|---|---|
| `scripts/precheck.py` | 0 | |
| `tests.test_session431` | 0 | 6 tests |
| `scripts/db_probe.py` | 0 | from 07:08:47 UTC, open |
| `runs/s431_db.py` and its three follow-ups, `runs/s431_anon.py`'s reads | 0 | read only; outputs in `runs/s431_*.out` |
| GitHub's deployments and commit statuses (this machine's `GH_TOKEN`, reads) | 0 | |

## Decisions made without you

1. The probe's table: `iso_dam_hub_prices`, a page's read of the live set.
2. The anon role's reads timed as `postgres` with `set role anon`: the role's 3-second timeout does not apply under `set role`, so the times are measured, not cut.
3. The probe loop not restarted after the memory stop.

## For Samuel's ruling

- The compute tier (the note's first two causes).
- `node_basis_daily` in the live set: a window, or the pages reading their own files.
- `ercot_rtm_price_adders` out of the live set (no page reads it).
- The loader: `VACUUM (ANALYZE)` of `series` after every load, and whole-table writes when only `retrieved_at` moves (found in sessions 432 and 438).
- Vercel's deployment limit: whether the branch pushes, each a deployment cancelled by the ignored build step, count towards it (Vercel's dashboard would say).

## Files

- New: `scripts/db_probe.py`, `tests/test_session431.py`, `docs/state/database_2026-10-21.md`, this report.
- On this machine (not in git): `runs/db_probe.log`, `runs/s431_*`.
