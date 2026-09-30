# SESSION 36B: Historical Event Analyzer v0, Winter Storm Uri (ERCOT, Feb 2021)

## Read first
CLAUDE.md, docs/datastandard.md, archive/sessions/SESSION_36A_REPORT.md,
ercot_all_hub_prices_history, carbon_intensity_hourly and _daily, the saved per-BA
extracts under warehouse/raw/eia930_emissions/20260930T000657Z/ (ERCO: demand and net
generation hourly), the /emissions and /grid/ercot pages as the page pattern.

## Budget and rules
- Expected Anthropic API spend: USD 0. Hard cap: USD 0. No model calls.
- No pulls. Everything comes from tables already held and files already saved.
- Target about 60 minutes. Supabase is at 376 of 400 MB: load only the small derived
  table below, never an hourly history.
- Pull and merge if the daily job lands, never force push.

## The tool
1. Derived table `event_window_daily` (tier derived, public): one row per event, BA,
   day and variable, for the window 2021-02-07 to 2021-02-24 and the same calendar
   days of 2019 and 2020 as the baseline. Variables: ERCOT hub average real-time and
   day-ahead price (daily mean and max), demand served (daily MWh and hourly minimum and
   maximum, from the ERCO extract), net generation (daily MWh), carbon intensity of
   generation (daily). An `event` column ("uri_2021") so later events append.
   Method in docs/methods/events.md: sources, the baseline definition, and that
   demand served during load shed is served load, not what customers wanted.
2. Page /events/uri-2021, and /events listing it: a short cited framing of the event
   (dates from the EIA page already cited on /grid/ercot), then four charts, event year
   against the 2019 and 2020 baseline: price, demand served, net generation, carbon
   intensity. A one-line number beneath each (the peak price, the lowest demand hour,
   the largest daily drop against baseline) read from the table. Tier chips, citations,
   method link, Stanford palette, mobile-safe. Nav: a new "Events" entry.
3. check-routes and check-values cover the page; validator, coverage, archive,
   Supabase (this table only), Redivis draft upload (public), llms.txt and the chat
   catalogue, deploy, live checks.

## Do not
No pulls, no model calls, no hourly tables into Supabase, no other events yet, no
deletions from Redivis, no force push.

## Report: archive/sessions/SESSION_36B_REPORT.md
Rows in the new table, the page's headline numbers and where each comes from,
Supabase size before and after, spend USD 0, wall time, open questions. Commit after
each step. Push. Stop.