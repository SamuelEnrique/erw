# SESSION 58: The daily jobs, private inputs, California reliability v1

## Read first
CLAUDE.md, PRIORITIES.md, .github/workflows/ (every workflow), the last ten runs of
each workflow through the GitHub API, archive/sessions/SESSION_54_REPORT.md and
SESSION_55_REPORT.md (the scheduler), SESSION_52_REPORT.md (the bill intake),
warehouse/news/ (digest, Roundup, shadow), the chat's latest-prices handling,
/grid/caiso, caiso_outlook, caiso_battery_storage, storage_daily_cycle,
event_window_daily and event_window.py, event_study.py, noaa_isd_hourly.

## Budget and rules
- Expected Anthropic API spend: USD 1 (the digest and Roundup if a dispatched daily
  run sends them). Hard cap: USD 4.
- Approved (Samuel, Oct 2): one workflow_dispatch of the daily job after any fix; a
  pull of CAISO's public history of Flex Alerts, Energy Emergency Alerts and Restricted
  Maintenance Operations notices (ceiling 20,000 rows); NOAA hourly station data for
  SAC and LAX over the September 2022 heat window and its baseline days (ceiling
  10,000 rows). License checked first.
- Private folders (private/bills, private/newsletters) never go to git, the site or any
  public place; only de-identified fixtures and aggregate comparisons leave them.
- No time cap, no redundant work, pull and merge if the daily job lands, never force
  push, commit after every step. If a part fails, record it and continue.

## Part 1: why the daily outputs stopped
1. For each workflow: when it last ran, on what trigger, and its result. State plainly
   whether the daily job is running on schedule, whether its last runs passed, whether
   the digest and Roundup were sent (and to whom), and why Ask the ERW has no prices for
   today.
2. Fix what is in our code. Dispatch the daily job once and watch it to the end;
   confirm the digest arrives at the subscriber list and prices for today reach
   Supabase.
3. Prepare a reliable trigger outside GitHub's scheduler (a free scheduler such as
   cron-job.org, or Supabase pg_cron with pg_net, calling workflow_dispatch on time).
   Write docs/runbook.md steps Samuel follows himself: create a fine-grained GitHub
   token limited to this repository with Actions read and write, paste it into the
   scheduler, set the times. Never store a token in the repo.
4. Close the stale failure issues if the token now allows it; otherwise list them for
   Samuel.

## Part 2: private inputs (skip each if its folder is empty)
1. Bills in private/bills/ (PDFs or photos, personal details crossed out): transcribe
   each into the intake CSV, run bill-intake.mjs to make de-identified fixtures, run
   test-bill-fixtures.mjs, and fix any line our calculator gets wrong where a cited
   tariff supports the fix. Report per bill: total ours against real, lines that differ.
2. Newsletters in private/newsletters/: for each issue, list its headline stories
   (titles only, no text copied), match them against our digest for the same days, and
   report coverage both ways: stories they had that we missed, and ours they lacked.
   Store only the aggregate comparison, never their text.

## Part 3: California reliability v1 (/grid/caiso, a new "Reliability" section)
1. The alert history pull, a table (tier source, license as stated), and a timeline on
   the page: every Flex Alert and emergency since the history starts.
2. A second California event, caiso_heat_2022 (2022-08-31 to 2022-09-09, with the
   weekday-aligned baselines), on the event template with weather from the NOAA pull,
   its event-study estimates (both specifications), and an /events page.
3. "How tight was it": per day, peak demand against the day's available supply from
   caiso_outlook where held, the evening ramp (the rise from the 12:00 to 15:00 mean to
   the 17:00 to 21:00 peak), and batteries' share of the evening peak from CAISO's own
   battery series; the alert days marked. Every number from a table with its check key.
4. docs/methods/california_reliability.md, and docs/reviews/clara-questions.md: ten
   questions for someone who worked at the California Energy Commission, each tied to
   a part of the section, aimed at the grid-stress tool (what the state needs to see
   before a tight evening, and how early).
5. check-values, check-routes, tests/, deploy, live checks.

## Report: archive/sessions/SESSION_58_REPORT.md
Part 1 in plain words first (what was wrong, what was fixed, what Samuel must do); Part
2 per bill and the newsletter coverage numbers; Part 3 rows against each ceiling, the
event estimates, the tightest days; spend from the ledger; wall time; open questions.
Push. Stop.