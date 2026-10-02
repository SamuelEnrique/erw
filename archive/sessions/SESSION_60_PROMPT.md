# SESSION 60: The Flex Alert scorecard (California grid-stress tool v1)

Machine: Samuel's portable laptop. Samuel's decision (Oct 2): this laptop is the data
machine until the lab machine arrives; the home laptop (8 GB RAM) will be a code
machine. First, set this machine's role to data (the one-command switch from session
59) and take the data lock for every write; release it at the end.

## Read first
CLAUDE.md, docs/machines.md, archive/sessions/SESSION_58_REPORT.md and
SESSION_59_REPORT.md, caiso_grid_emergencies, caiso_reliability_daily,
event_window.py and event_study.py, noaa_isd.py, the saved EIA-930 per-BA extracts
(CISO hourly demand from 2018-07), iso_hub_prices_history, docs/reviews/
clara-questions.md, the grid-stress-tool notes in docs/ if any.

## The question
How much did California's demand actually fall during Flex Alerts and grid
emergencies, after accounting for weather and the calendar, and what was that worth?
An independent, replicable scorecard: alerts are being debated (funding, and how
uncertain their load reduction is), and nobody publishes one.

## Budget and rules
- Expected Anthropic API spend: USD 0. Hard cap: USD 0. No model calls.
- Approved pulls (Samuel, Oct 2), license checked first, raw saved, resumable, history
  out of the live database unless small:
  a. NOAA hourly temperature and dew point for SAC, FAT and LAX, May through October
     of 2018 to 2025 (the alert season), ceiling 150,000 rows.
  b. CAISO day-ahead hourly prices at the SP15 and NP15 hubs (OASIS) for every alert
     or emergency day since 2018-07 and its model's comparison days, ceiling 60,000
     rows. CAISO's server is slow: pull day by day, resume, never restart.
- Never wait idle; pull and merge if the daily job lands; never force push; commit
  after every step. If a part fails, record it and continue.

## The method
1. Alert days: from caiso_grid_emergencies, every Flex Alert, EEA and related notice
   day since 2018-07, with its stated hours where the report gives them (default 4 to
   9 p.m. Pacific, labeled when assumed).
2. A counterfactual load model for CAISO hourly demand fitted on non-alert days of the
   same seasons: temperature (cooling degree hours and their square, population-
   weighted across the three stations with stated weights), hour of day by weekday
   type, month, year, and holidays. Report its out-of-sample error on held-out
   non-alert hot days, so a reader can judge it.
3. Per alert day: actual minus predicted demand in the alert hours, in MW and MWh,
   with an interval (prediction error plus a block bootstrap over days). Pooled over all
   alert days and by year.
4. Value: MWh reduced times the hour's day-ahead hub price, summed, labeled as a
   wholesale lower bound (scarcity and reliability value are higher and not
   estimated).
5. What it cannot separate: on alert days the state also dispatches paid programs
   (DSGS, ELRP) and other actions, so the estimate is the combined demand-side effect
   on alert days, not the Flex Alert message alone. Alerts fall on the hottest days, so
   the model's fit at extreme heat is the main risk; show the residuals on the hottest
   non-alert days as the check. Say all of this on the page.

## The tool
1. Tables (tier derived, public): flex_alert_effects (per alert day: hours, actual,
   predicted, effect, interval, value) and flex_alert_model (fit statistics,
   coefficients). Into Supabase only if small.
2. Page /grid/caiso/alerts, linked from the Reliability section and /events: a ranked
   list of alert days with the estimated MW cut and its interval; a pooled headline; a
   year-by-year chart; one chart per day of actual vs predicted through the evening; the
   wholesale value; the caveats above in plain words. Every number a warehouse value
   with its check key. Stanford palette.
3. docs/methods/flex_alert_scorecard.md written like a paper's methods section, and a
   replication notebook that reproduces every number on the page.
4. docs/reviews/clara-questions.md: add five questions about the scorecard for a former
   California Energy Commission analyst (which alerts matter most, what a credible
   counterfactual needs, how the state measures program impact today, what data would
   make it better, who would use it).
5. check-values, check-routes, tests (the estimator recovers a known effect on a
   synthetic panel), deploy, live checks.

## Report: archive/sessions/SESSION_60_REPORT.md
Rows pulled against each ceiling; the model's out-of-sample error; the pooled effect
with its interval; the five largest and five smallest alert-day effects; the total
wholesale value; what the estimate can and cannot say; anything only Samuel can do, in
one list; wall time; spend USD 0 confirmed. Release the lock. Push. Stop.