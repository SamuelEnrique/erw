# Session 54 report: the network refreshes every hour

Energy Research Warehouse (ERW), session 54, run 2026-10-01 from 17:00 UTC to about 18:28 UTC. **Wall time about 1 hour 28 minutes,** against a 70-minute target. Over the target: about 30 minutes of it was spent waiting for a scheduled run of the new workflow, which did not come (below).

**API spend: USD 0.00, confirmed.** No model call. The only data pulled was the approved EIA-930 interchange and demand pull: one probe, one local dry run, the dispatched run and one local run of the script. The hourly job wrote nothing to the Supabase database and nothing to git. No force push.

## What runs hourly

| What | How often | Where it goes |
|---|---|---|
| **Links:** EIA-930 interchange between each pair of balancing authorities (BAs), the latest 168 hours | every hour on the hour, except 14:00 UTC | one JSON object in the public Supabase Storage bucket `erw-public` (`network/grid_network.json`) |
| **Demand** of the seven ISO BAs (sphere size), with the last 48 hours kept in `demand_recent` | every hour | the same object |
| **Carbon intensity** (sphere color), the nodes, their names and fixed positions | daily, by the daily run's `warehouse/derived/grid_network.py`; the hourly run carries them over unchanged | `site/data/grid_network.json`, committed: the page's fallback |

### `warehouse/derived/network_hourly.py`

It is self-contained (requests only).

1. **Base.** It reads the Storage object and the committed snapshot, and takes the newer-built one as the base.
2. **Pull.** It pulls:
   - interchange for the 48 hours ending at the API route's own newest period (see "EIA's lag" below);
   - demand for the last 48 clock hours.
3. **Merge.** It keeps the base's nodes and positions. For links, each pulled pair-hour replaces the old one, older hours come from the base (else from the other snapshot), and the window is the 168 hours ending at the newest complete hour. It recomputes interchange volumes.
4. **Refuse.** It will not upload a snapshot whose nodes or positions moved, whose hours are not 168 contiguous ones, or whose newest hour has fewer than 100 pairs.
5. **Upload.** It uploads one object that holds `built`, `newest_hour`, `base_built` and the EIA URLs it read, with the key removed.

The newest complete hour is the latest hour in which at least 90 percent as many pairs reported as in the median hour. The partial hours after it wait for a later run.

### `.github/workflows/hourly-network.yml`

- **When:** cron `0 0-13,15-23 * * *`, plus `workflow_dispatch`.
- **Permissions:** `contents: read` and `actions: read`.
- **Concurrency:** its own group, `hourly-network`.
- **Skipping the daily and weekly jobs:** `--skip-if-busy` asks the GitHub API, before the pull and again before the upload, whether the daily or weekly job is queued or running. If either is, the run exits 0 and uploads nothing.
- **Why not their concurrency group:** GitHub keeps one pending run per group, so an hourly run arriving behind a pending daily run would cancel the daily run.
- **Record:** success or failure goes to the job log only.

## The page

`/network` fetches the Storage object with a one-hour revalidation.

- **Which snapshot it draws:** the Storage object when it is whole and not older than the committed snapshot; otherwise the committed one, and it says so. The rule is `site/lib/network.ts`, `pickSnapshot`.
- **The new line:** "Newest hour: <UTC> (<Eastern> Eastern), refreshed <time>", with the source (the hourly refresh or the daily snapshot), the newest demand hour, and EIA's lag.
- **The legend:** beside carbon intensity, "The color updates daily (latest hour ...); the links and demand, hourly".
- **The check key:** demand from the hourly run carries `netsnap|<BA>|demand_mw|<hour>`. check-values reads it from the object's `demand_recent`, since the job writes nothing to the database.

The daily job is unchanged and keeps building the committed snapshot.

## EIA's lag: a finding that changes the prompt's premise

The prompt expected the newest hour to be one to two hours old. That holds for demand, but not for the links.

- **Demand** (`region-data`, type D) is one to two hours behind the clock. At 17:00 UTC the newest demand hour was 15:00 UTC.
- **Interchange between pairs of BAs** (the API's `interchange-data` route) had an `endPeriod` of 2026-09-30T07, about 34 hours behind the clock.
- **Each BA's total interchange** (`region-data`, type TI) was current, but it is not pairwise.

EIA's own Grid Monitor serves fresher interchange from an undocumented endpoint (`/electricity/930-api/`). I did not use it: it has no stated terms, and the approval named the same source as the daily connector.

What this means:
- The links still run more than a day behind the clock.
- The hourly run moves them forward as soon as EIA publishes, instead of waiting for the daily build. The daily build keeps complete UTC days only, and its newest hour was 2026-09-28 23:00.

**Rows per run, more than the prompt's estimate:**
- If the pull ended at the clock, 48 hours would hold only about 14 hours of interchange (4,269 rows in the probe). That would leave a 17-hour hole between the daily build and the pull, which no later hourly run would fill.
- So the run pulls the 48 hours ending at the route's own `endPeriod`: **15,535 interchange rows and 329 demand rows.**
- That is more than the prompt's "a few thousand", because most pairs are reported by both BAs (about 337 reports an hour). It is the same 48 hours of the same route.

## The dispatched run, and the scheduled runs

**Dispatched run 36897939530** (17:14 UTC, the one approved dispatch): **failed at the upload.**
- It pulled 15,535 interchange rows (newest EIA period 2026-09-30T07) and 329 demand rows.
- It merged 155 pairs. The newest complete hour was 2026-09-30T03:00 (155 pairs); the partial hours 04:00 (121 pairs), 05:00 (87) and 06:00 (75) were left out.
- It built a 191 KB snapshot that passed every check.
- Creating the bucket then failed with `HTTP 404 PGRST125 "Invalid path specified in request URL"`. The repository's `SUPABASE_URL` secret carries the REST path, so `<url>/storage/v1/bucket` reached PostgREST instead of Storage. My local `.env` has no path, so the local dry run did not show it.
- Nothing was uploaded and nothing else was affected: the page kept the committed snapshot.
- **Fix** (`e12ab81`): Storage is reached at the origin of `SUPABASE_URL`, as `grid_network.py` and the site already do, and a test covers a URL with a path. A read-only request to the bucket route then answered from Storage ("Bucket not found").

I did not dispatch again: the approval was for one dispatch.

### Waiting for the schedule, then one local run

I waited for the 18:00 UTC scheduled run. By 18:24 none had started, although the workflow was registered and `active`.

GitHub runs this repository's frequent schedules far less often than their crons say. "latest prices" (`*/15 * * * *`, 96 runs a day) ran five times in the 24 hours before 18:00 UTC: at 19:15, 23:06, 02:06, 08:51 and 15:50. Today's 14:00 daily run had not started either.

So I ran the fixed script once from this machine, at 18:17 UTC, with `--skip-if-busy`. It is the same approved 48-hour pull, not a second dispatch of the workflow.

**The local run's result:** ok in 58 s.
- It pulled 15,535 interchange rows (EIA's `endPeriod` still 2026-09-30T07, an hour later) and 329 demand rows.
- The newest complete hour was 2026-09-30T03:00, with 155 pairs; 156 links, 69 nodes.
- It created the public bucket `erw-public` and uploaded 191 KB. The object answers anonymously with `Cache-Control: public, max-age=60`.
- Every EIA URL in the object has the key removed; a search of the object for the key found nothing.

**The workflow itself, after the fix, has not yet completed a run.** Its first scheduled run will be the first proof on GitHub. The dispatched run had already shown that everything up to the upload works on the runner: secrets, the pull, the merge and the checks.

## The newest hour shown, before and after

| | Newest hour (links) | Demand, newest hour | Built |
|---|---|---|---|
| Before (live, 17:11 UTC) | 2026-09-28 23:00 UTC (Sep 28, 19:00 Eastern) | 2026-09-29 23:00 UTC (ERCOT 78,210 MW) | 2026-10-01 04:02 UTC, the daily snapshot |
| After (live, 18:20 UTC) | **2026-09-30 03:00 UTC (Sep 29, 23:00 Eastern)**, refreshed 2026-10-01 18:17 UTC ("the hourly refresh") | 2026-10-01 16:00 UTC (ERCOT 65,789 MW, key `netsnap`) | 2026-10-01 18:17 UTC, merged onto the daily build of 04:02 |

## Checks

- **check-values:**
  - Local, on the fallback build: 3,811 of 3,811 values match, including both keys on `/network`.
  - Live, after the deploy: **3,609 of 3,609** match, including `netsnap|ERCO|demand_mw|2026-10-01T16:00:00Z` (65,789) and ERCOT's carbon intensity from the database. The live page reports `data-network-source="storage"`.
- **check-routes:** 62 of 62 locally. Live: **62 of 62.**
- **Tests:** `tests/test_session54.py`, 13 tests:
  - the merge keeps 168 contiguous hours ending at the newest hour, and every position unchanged;
  - the older hours are the base's, moved;
  - a pulled hour replaces the base's, and the other snapshot fills a hole;
  - unknown nodes are left out, and a moved position is refused;
  - demand, the pair rule and the newest complete hour;
  - the fallback: Storage unreachable, broken, or older than the committed snapshot each give the committed one, and a newer whole object gives Storage;
  - the page reads with a one-hour revalidation;
  - the workflow has no database, no git and no shared group;
  - the URL origin;
  - no em dashes.

  With sessions 49 and 53: 42 tests, OK.
- **Lint and types:** eslint and tsc are clean on the changed files.

## Docs

- **`docs/runbook.md`:** a new section, "The hourly network refresh": what it does, what refreshes hourly and what daily, what it never does, its record, its secrets, and how to run or stop it.
- **`docs/methods/grid_network.md`:** a new section, "What refreshes hourly, and what daily", with a subsection, "Why the newest hour is not the current hour" (EIA's lag, with the numbers above).

## Commits

- `6811b65`: the script, the workflow, the runbook and the method page.
- `e12ab81` and `a006c66`: the Storage URL fix.
- `99214c2`: the page, `lib/network.ts`, check-values and the tests (pushed after the first object was in Storage, so Vercel's first fetch of it found it).
- This report, with the prompt moved to `archive/sessions/SESSION_54_PROMPT.md`.

## Open questions

1. **The schedule is not hourly in practice.** GitHub's scheduler ran a 15-minute cron five times in a day, so "hourly" on GitHub Actions may mean every few hours. A trigger outside GitHub, calling `workflow_dispatch` on the hour, would fix it: a Vercel cron or Supabase `pg_cron` with `pg_net`. That needs a token stored in that service. Should the ERW add one?
2. **Fresher links.** Interchange through the documented API runs about a day and a half behind the clock. Should the ERW ask EIA about the Grid Monitor's `930-api` endpoint (its terms and its stability), or accept the lag? Until then, an hourly refresh mostly moves demand.
3. **The check on hourly demand** compares the page with the Storage object, not with EIA. A drift between the object and EIA (EIA revises recent hours) would not be caught. Should check-values also query EIA for the one ERCOT hour it checks? That would be one EIA call per check run.
4. **Fewer pulls.** Each hourly run pulls about 15,900 rows even when EIA's interchange `endPeriod` has not moved. Should the run skip the interchange pull when `endPeriod` equals the object's last pull, and refresh demand only? That would cut the rows to about 330 for most hours.
5. **The 14:00 UTC hour** is left out of the schedule, and runs skip while the daily job runs (up to about three hours), so the page can go up to about four hours without a refresh each afternoon. Is that acceptable?
