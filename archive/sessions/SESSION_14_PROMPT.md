Session 14 of the Energy Research Warehouse (ERW). Read CLAUDE.md, .github/workflows/daily-prices.yml, .github/workflows/latest-prices.yml, warehouse/run_daily.sh and SESSION_13_REPORT.md first. Same non-negotiables: real data only, fail loudly, no em dashes, never delete existing files, commit after each task, do not push, do not stop to ask questions.

Human rulings: CAISO stays lmp_rtm_5min; ISO-NE hourly real-time gets per-day completeness; the two datacenter digest scores are acceptable, no rubric change.

The site is live at https://erw-flame.vercel.app and reads Supabase correctly. The daily-prices workflow failed on GitHub 50 seconds after starting; the latest-prices workflow has not produced a run. The failed step's log follows between the markers.

=== GITHUB LOG START ===
Run set -o pipefail
set -o pipefail
bash warehouse/run_daily.sh 2>&1 | tee daily.log
shell: /usr/bin/bash -e {0}
env:
  PYTHON: python
  DAYS: 3
  EIA_API_KEY: ***
  ANTHROPIC_API_KEY: ***
  PJM_API_KEY:
  REDIVIS_API_TOKEN: ***
  REDIVIS_OWNER:
  SUPABASE_URL:
  SUPABASE_SERVICE_KEY:
  RESTORE_FROM_REDIVIS: 1
== ERW daily refresh 2026-09-26T22:59:54Z: ISOs: ercot caiso nyiso miso spp isone; days: 3
== restore rolling-window tables from the Redivis draft (session 10)
REDIVIS_OWNER is not set (.env or environment); nothing uploaded
restore from Redivis failed: stopping, so a partial window is never uploaded over a full one
Error: Process completed with exit code 1.
=== GITHUB LOG END ===

The human has since added the five missing secrets (REDIVIS_OWNER, SUPABASE_URL, SUPABASE_SERVICE_KEY, SUPABASE_ANON_KEY, SUPABASE_DB_URL) and re-triggered the workflow. Task 1 should confirm that missing secrets were the only cause, make the workflow fail with a clear message naming any missing secret before doing any work, and still check the latest-prices workflow.

TASK 1. CI fixes. Diagnose the failure from the log and the workflow files, add a first step to both workflows that checks every required secret is non-empty and fails with the secret's name if not, and check the workflow logic locally the way session 3 did (run the same commands the runner would, with GITHUB_ACTIONS=1 and RESTORE_FROM_REDIVIS=1, in a fresh temporary clone of this repo so the missing-tables condition is real). Also check why latest-prices.yml has not run: cron syntax, the workflow's on: block, and that its Python install and secrets are correct; test its command in the same fresh clone. Commit.

TASK 2. Per-day completeness for isone_rtm_zone_prices_hourly, mirroring session 13's mode; rerun it for 30 days; validate; coverage; Supabase load. Commit.

TASK 3. Re-run the chat evaluation on questions_s13.yaml with the timezone fix in place; report beside the session 12 and 13 results. Commit.

TASK 4. Public face. Rewrite the root README.md for a first-time visitor: what the ERW is (positioning paragraph), the site link, what is in it today (from coverage, with counts), how to install the package and fetch one table in five lines, how the daily and 15-minute refresh work, the license rule, the IRW lineage with credit, and the session log as a table. Embed three screenshots from site/screenshots. Add a STATUS.md that the daily workflow regenerates: tables, rows, last successful run per workflow, open gaps from run_status.csv. Commit.

TASK 5. SESSION_14_REPORT.md in the usual format, including the exact cause of the CI failure and what proves it is fixed. Final commit.