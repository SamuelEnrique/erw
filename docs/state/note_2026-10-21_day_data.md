# The data machine's note, 21 October 2026, morning

Energy Research Warehouse (ERW), session 389, for Samuel. The data machine's chain of 21 October, day (sessions 387 to 389, `queue/done/016-day-21-october-data.md`), unattended on lab-desktop, from 05:38 UTC to this note's push. Model spend USD 0 in every session. The night chain's note, before this one: [`docs/state/morning_2026-10-21_night.md`](morning_2026-10-21_night.md).

## Read these first

- **The jobs on a clock did not start for six hours last night; today's daily takes the same path at 14:00 UTC** (session 387, `queue/summary/2026-10-21-health.md`). From 23:30 UTC on 20 October to 05:15 UTC on 21 October, 47 of pg_cron's runs in Supabase failed with "job startup timeout". This had never happened before: 3,838 runs succeeded since 2 October. A failed run sends no `workflow_dispatch`, so no 15-minute run was made from 02:30 to 05:30 UTC. Every request that was sent was answered 204, and Postgres has not restarted. With `cron.use_background_workers` off, each job opens a connection to `localhost`, and that connection did not start in time. What held it is not visible from inside the database; Supabase's logs and resource graphs for those hours would show it. Runs succeed again from 05:30 UTC. **Yours, best before 14:00 UTC:** look at the project's resource use for those hours, or turn background workers on (a restart).
- **No step failed on 21 October by 06:05 UTC.** The streak (`health_days.json`) stands at 0, counted to 19 October; 20 October had 5 failures. The streak counts a day as missing only when a job made no run at all that day, so it does not see a six-hour gap.
- **Licensing** (session 388): of the 20 tables not settled, only `impact_tax_rules`'s publishers could be asked, since `license_read.py` reads a publisher once. The Louisiana Department of Revenue's page restricts reproduction. That verdict is drafted, not written: written, it would put `impact_tax_rules` on the "license needed" list (41 to 42) and hold it on `/impact`. The Legislature's page states no terms. 4 requests of 16.
- **Session 384's part (b) was session 387**, written for 21 October up to 06:05 UTC. GitHub's daily is dispatched at 14:00 UTC, not "about 05:00" as the chain file said, so its steps are the next chain's.
- **The next chain is written**: `queue/next/017-day-21-october-data-pm.md`, sessions 390 and 391 (21 October's whole day, after its daily runs; the note), pushed to main on its own.

## What each session landed

| Session | Landed |
|---|---|
| 387 | `queue/summary/2026-10-21-health.md` (to 06:05 UTC, with its "## Root causes": pg_cron's startup timeouts, and the streak's blind spot) |
| 388 | Records 83 and 84 in `license_reads.csv`; `docs/licenses.md` regenerated (84 publishers, 82 requests); the line of sweeps in `scripts/licenses.py` names session 388; the Revenue verdict drafted in its report |
| 389 | This note, and `queue/next/017-day-21-october-data-pm.md` |

Session 387 landed on `task/387-health` (pushed 06:13 UTC, `0ce7edc5`; checks passed, run 39554082506; merged as `d88b74ed`; deployed 06:26 UTC): snapshots `s387-land-before` and `-after`, **0 differences on 25 pages**, expected (every page in review). Sessions 388 and 389 land this note on `task/388-389`; the record of their checks is in session 391's note. The queue file `017-day-21-october-data-pm.md` went to main on its own (`cfcc5928`, 06:27 UTC): `s389-queue-before` and `-after`, 0 differences. Vercel made no deployment of `cfcc5928` or of the queue move `013ebdd8` by 06:35 UTC (each only touches `queue/`; `d88b74ed`, which holds `013ebdd8`, deployed), so each after snapshot is of the site as the last deployment left it.

## Pulls against their ceilings

| Session | Pull | Used | Ceiling |
|---|---|---|---|
| 387 | none (Supabase's health table and pg_cron's own tables, read only) | 0 | 0 |
| 388 | revenue.louisiana.gov and www.legis.la.gov: a robots file and one page each | 4 | 16 |
| 389 | none | 0 | 0 |

Nothing was asked of a paused publisher. Both hosts were new: their robots files were asked first (both 404, so the pages are allowed by the convention), and the page asked on each is its terms. GitHub's API was read with this machine's `GH_TOKEN` once its 60 public requests an hour were spent.

## Decisions made without you (one line each; the reasons are in each report)

- 387: 21 October written as it stood at 06:05 UTC rather than waiting for 14:00 UTC; no change to `health.py`'s count of a missing day; none to pg_cron.
- 388: only publishers not in the record asked; none where a search found no terms page (New Mexico, the Texas Comptroller); the Revenue verdict held as a draft.
- 389: the next chain from item 6 only; it writes no further chain if nothing can move without a ruling.
- The queue: `chain_queue.py next` commits the move but does not push it; the move of 016 was pushed by hand (`013ebdd8`), and no deployment of it had appeared by 06:04 UTC.

## Waiting for you, highest value first

1. **Redivis storage (10 GB, full)**: a refusal removes the table from the draft (session 385). The choices are in `docs/redivis/organization-move.md`, with the uploader's safer replace.
2. **pg_cron's connections** (session 387), before 14:00 UTC if you can.
3. **The move under Ben's organization**, and its order against the release click.
4. **Licensing** (session 388): the Revenue verdict, and so whether `impact_tax_rules` is held; whether a publisher read once with no sentence (FERC, 8 tables; the PUC of Texas and the Federal Register, 5; four commissions, 2; CME, 1) may have a second page read.
5. **The loader's guard** (session 384, part c) and **the daily task with no console window** (session 384).
6. **The streak**: whether a job far below its expected count ends a green day (session 387).
7. Still open: the four permission letters; `nyiso_load_queue`; "One alert policy"; `restore_tables.py`'s header note.

## The other machines

- **The code machine**: `queue/next/014-night-20-october-code.md` and `015-day-20-october-code-pm.md` are still in `queue/next/`, with their sessions' branches pushed (`wip/381-382-land`, seven of `wip/403-s` to `wip/414-s`). `task/367-372` holds the `test_session166` fix; session 386 took the same commit so that its landing's checks could pass, and main has it since `7e08c274`.
- **The third machine** (portable-laptop) reported "ready for review: queue/next/ holds nothing for portable-laptop" at 03:15 UTC.
- **This machine** stays on `main` in its main checkout, with the daily run of 20 October's page files uncommitted; its daily run of 21 October starts at 17:00 UTC.
