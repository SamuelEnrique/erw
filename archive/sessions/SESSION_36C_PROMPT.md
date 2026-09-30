# SESSION 36C: Event two, COVID-19 demand shock, seven grids

## Read first
archive/sessions/SESSION_36B_REPORT.md, warehouse/derived/event_window.py,
docs/methods/events.md, the /events pages, the saved per-BA extracts under
warehouse/raw/eia930_emissions/20260930T000657Z/, warehouse/supabase/load.py and its
live-set config.

## Budget and rules
- Expected Anthropic API spend: USD 0. Hard cap: USD 0. No model calls.
- No pulls. Everything from tables held and the saved extracts.
- Target 60 minutes. Three steps, in order. Pull and merge if the daily job lands,
  never force push.

## Step 1, first 10 minutes: Supabase headroom
List each live table's size and the window the site actually reads. Trim live windows
to what pages and /ask need, never below what a page shows, to at or under 330 MB after
VACUUM FULL. Redivis and CSVs keep everything. Add a loader warning at 350 MB.

## Step 2: event_window_daily generalized
Add `event` to the table's key (entity, variable, ts_utc, event) so events and their
baselines can share days. Rebuild Uri's rows unchanged and confirm they match. Record
it in docs/datastandard.md.

## Step 3: COVID-19, event "covid_2020"
- Window: 2020-03-01 to 2020-05-31, ERCOT operating days for ERCO and each BA's local
  day for the others, all seven BAs plus US48.
- Baseline: weekday-aligned, the same weekday 364 days earlier (2019) and 728 days
  earlier (2018), because demand depends on the day of the week. Record this choice in
  the method page.
- Variables per BA and day: demand served (MWh, hourly min and max), carbon intensity
  of generation, demand vs baseline (MWh and percent). ERCOT hub real-time and
  day-ahead daily mean for price context.
- Page /events/covid-2020: a cited framing (a primary source for the first US stay-at-
  home orders, read as text), one chart of demand vs baseline in percent for all seven
  grids on one axis, a small multiple per grid, and one line per grid read from the
  table: the deepest weekly drop against baseline and its week. Tier chips, citations,
  method link, Stanford palette. Listed on /events.
- check-routes and check-values cover it; validator, coverage, archive, Supabase (this
  table only), Redivis draft upload, llms.txt and the chat catalogue, deploy, live
  checks.

## Do not
No pulls, no model calls, no hourly tables into Supabase, no deletions from Redivis, no
force push.

## Report: archive/sessions/SESSION_36C_REPORT.md
Supabase per table before and after; Uri rows unchanged under the new key; COVID rows
and each grid's deepest drop with its row; spend USD 0; wall time; open questions.
Commit after each step. Push. Stop.