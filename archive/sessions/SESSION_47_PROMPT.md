# SESSION 47: Supabase size, event studies, then the gate path

## Part 0 (first)
1. Supabase is at 447.9 MB after run 13's load (plain vacuum does not shrink it).
   Approved: run VACUUM (FULL, ANALYZE) on the six shape tables directly, without a
   load, at once. Report the size before and after.
2. Add a weekly GitHub workflow (Sunday 10:00 UTC) that runs VACUUM (FULL, ANALYZE) on
   the shape tables and records the size in run_status; the daily load keeps its plain
   vacuum. Update the runbook. Commit.
3. The untracked warehouse/connectors/eia930_interchange.py from session 46: keep it
   for Part B.
4. Read daily-prices run 14 (workflow_dispatch, 374f8fd). Do not wait idle: start
   Part A now and check run 14 between Part A's steps.

## Part A: event study module (research)
Rules: USD 0, no model calls, no data pulls, no Supabase table beyond one small
results table.
1. warehouse/derived/event_study.py: for each event in event_window_daily and each
   grid in it, estimate the event effect on daily demand served (and, where held,
   daily hub price) with a regression on event days against the weekday-aligned
   baseline days: event-day indicators (and a single pooled event-window effect),
   day-of-week effects, and year effects; heteroskedasticity-robust standard errors;
   95 percent intervals. Where hourly data are held (demand from the extracts), also
   an hour-of-day profile of the effect. Where weather is not held, say plainly that
   the estimates do not control for temperature.
2. Results table event_study_estimates (tier derived, public): event, grid, outcome,
   term, estimate, std error, ci_low, ci_high, n, specification id. Into Supabase only
   if the live set stays under 360 MB after Part 0.
3. On each /events/<slug> page, a "What the estimates say" block: the pooled effect
   with its interval, a coefficient plot of the event days, and one sentence read from
   the table. docs/methods/event_study.md written like a paper's methods section:
   specification, identification, what it assumes, what it cannot rule out (weather,
   concurrent events), and each result's table.
4. A replication notebook, notebooks/event_study.ipynb, using the erw package to
   fetch event_window_daily and reproduce every estimate on the pages exactly; linked
   from the methods page.
5. Tests: the estimator against a synthetic panel with a known effect; check-values
   covers every estimate shown; check-routes; tests/; deploy; live checks.

## Part B (only if run 14 passed)
Read SESSION_42_PROMPT.md and execute it end to end (its approved interchange pull,
using the drafted connector after checking its field names against the API; the 3D
network at /network), writing SESSION_42_REPORT.md. Then, if time allows, the approved
year of hub prices (2025-09-01 on; CAISO SP15 and NP15, MISO Indiana Hub, NYISO
N.Y.C., ISO-NE .H.INTERNAL_HUB, SPP SPPNORTH_HUB; ceiling 1.5 million rows; history
tables out of Supabase), rebuilding cost_of_power_* and the bill page's NP15
reference.
If run 14 failed: read its log, fix it on main, trigger one workflow_dispatch
(approved), and stop after Part A.

## Always
Pull and merge if the daily job lands, never force push, commit after every working
step.

## Report: archive/sessions/SESSION_47_REPORT.md
Supabase before and after; the weekly job; run 14's outcome and which path ran; every
event estimate with its interval; rows pulled against each ceiling if Part B ran;
decisions made without a human; open questions; wall time; spend USD 0 confirmed.
Push. Stop.