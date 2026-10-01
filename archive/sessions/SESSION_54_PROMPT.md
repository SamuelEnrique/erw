# SESSION 54: The network refreshes every hour

## Read first
CLAUDE.md, archive/sessions/SESSION_42_REPORT.md and SESSION_49_REPORT.md (Part A),
warehouse/connectors/eia930_interchange.py, the network snapshot builder,
site/data/grid_network.json and the /network page, .github/workflows/ (the daily and
weekly jobs, their concurrency groups), the Supabase client setup.

## Budget and rules
- USD 0, no model calls.
- Approved by Samuel: an hourly refresh of EIA-930 interchange and demand for the
  network, each run pulling only the last 48 hours (a few thousand rows), the same
  public source and license as the daily connector.
- The hourly job must never write to the Supabase database, never commit to git, and
  never run at the same time as the daily or weekly job (share their concurrency
  group or skip if one is running). If it fails, nothing else is affected.
- Target about 70 minutes. Pull and merge if the daily job lands, never force push.

## The work
1. A script that pulls the last 48 hours of interchange and demand, rebuilds the
   network snapshot (same nodes, same fixed positions, the latest 168 hours of links,
   keeping older hours from the previous snapshot), and uploads it as one JSON object
   to a public Supabase Storage bucket (object storage, not the database), with the
   build time and the newest hour inside the file.
2. .github/workflows/hourly-network.yml: on the hour (plus workflow_dispatch), runs
   the script, records success or failure in the job log only.
3. /network reads the Storage snapshot with a one-hour revalidation, and falls back to
   the committed site/data/grid_network.json if Storage is unreachable. The page shows
   "newest hour: <UTC and Eastern>, refreshed <time>" and, beside carbon intensity,
   that color still updates daily.
4. The daily job keeps building the committed snapshot as today (the fallback).
5. Dispatch the hourly workflow once and confirm the page shows the new newest hour.
6. Docs: the runbook and the method page say what refreshes hourly, what daily, and
   why EIA's own lag means the newest hour is one to two hours old.
7. check-routes, tests/ (the merge keeps 168 hours, positions unchanged, the fallback
   works), deploy, live check.

## Report: archive/sessions/SESSION_54_REPORT.md
What runs hourly, the dispatched run's result, the newest hour shown before and after,
rows per run, wall time, spend USD 0 confirmed, open questions. Commit. Push. Stop.