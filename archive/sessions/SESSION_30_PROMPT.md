# SESSION 30: Price board v2 and the cost layer

## Read first
CLAUDE.md, PRIORITIES.md, docs/datastandard.md, archive/sessions/SESSION_29_REPORT.md,
docs/migrations/2026-09-29-consolidation.md, warehouse/metadata/table_migrations.csv,
the price board page and its queries in site/, warehouse/news/ (brief.py, roundup.py,
scoring), the Thesis Builder, the chat eval, and every place the Anthropic client is
constructed.

## Budget and rules
- Expected Anthropic API spend: USD 5. Hard cap: USD 8. Build the cost ledger (Part B1)
  before any other model call in this session, then every model call goes through it.
  When the session's ledger total passes USD 8, make no further model calls, finish the
  non-model work, and say so in the report.
- Model calls allowed in this session, and nothing else: the Haiku backtest on stored
  stories (Part B4, approved by Samuel in chat), one shadow digest and one shadow Roundup
  to Samuel only, one Thesis Builder run, one chat eval run, and the caching measurement.
  No re-pull of any source. No backfill. Re-scoring stored stories with Haiku is not a
  backfill; re-scoring them with Sonnet would be, and is not allowed.
- No time cap. Do not stop for time. What Samuel cares about is no redundant work: never
  re-run a step that already succeeded, never read a large table twice when once will do,
  never rebuild what a previous step produced. One family, one table, one page at a time.
- Memory: stream with pyarrow, one table in memory at a time. The laptop has about 3 GB
  free and has killed sessions before.
- The GitHub daily job runs at 14:00 UTC (7am Pacific). If it lands while you work,
  git pull and merge before pushing, exactly as session 28 did. Never force push.
- Every number on every page comes from a table in the warehouse. No placeholders, no
  invented values, no hard-coded assumptions except the one heat rate in A3, labeled.

## Health check (first, no changes)
Last daily run status, failures vs the known-gap list, gate state. Report it. This
session adds no source, so the gate does not block it.

## Part A: price board v2 (the tool the demo video will feature)
Ship derived tables first, then the page. Every derived metric is a table in the
warehouse with tier = derived and its formula in docs/methodology, never computed
ad hoc in the site.

A1. `price_board_latest` (one row per ISO hub per market): latest day-ahead and real-
    time price, previous day, day-over-day change in $/MWh and percent, 7-day and 30-day
    average, 30-day min and max, last 30 daily values for a sparkline, day-ahead minus
    real-time spread, from iso_dam_hub_prices, iso_rtm_hub_prices and the ISO-NE and
    NYISO zone tables. Six ISOs; where a series does not exist (SPP real-time) the row
    says so, it is not blank.
A2. `price_board_peak_offpeak`: peak (HE 7 to 22, weekdays) and off-peak averages per
    ISO per day for the last 90 days, from the hourly tables, with the ISO's own peak
    definition where it differs and documented.
A3. `price_board_spreads`: daily Henry Hub, spark spread per ISO at a 7.0 MMBtu/MWh
    heat rate (the one labeled assumption), implied heat rate (power price / gas price),
    Brent minus WTI, last 365 days.
A4. `price_board_carbon`: latest CARB and RGGI auction and secondary prices we hold,
    with dates; CARB is a known gap, show its last held value with its date, never a
    stale value presented as current.
A5. The page: one screen, dense, Stanford palette (cardinal 8C1515, black 2E2D29, fog
    F7F3EA, stone greys), inline SVG sparklines, moves colored by sign, tier chips and
    source citations on every block, methodology link, works on a phone. The ERCOT
    history back to 2015 gets its own strip on the page (annual averages and the
    peak-premium view) because that is the shot in the demo. No new dependencies.
A6. Load the four derived tables into the Supabase live set, validator, archive,
    coverage, llms.txt, chat catalogue, Redivis draft upload of the four (public,
    derived). Deploy is the last step of the session (Part D), not here.

## Part B: the cost layer
B1. `api_cost_ledger` (internal tier, never public): run_id, session, step, model,
    input_tokens, cached_input_tokens, output_tokens, usd, ts_utc. One wrapper around
    the Anthropic client that every call in the repo uses; grep for every client
    construction and route it through the wrapper. Prices per model in one config file
    with a date. The daily run writes to it. An internal page at /internal/costs (no nav
    link, gated by an env token) shows spend per day, per step, per model, last 30 days,
    plus the projected monthly bill.
B2. Prompt caching: cache_control on the system prompt and the shared context of the
    digest, Roundup, extraction, chat and Thesis Builder calls. Measure on one day of
    stored stories: cost with and without caching, into the report.
B3. Story cap: MAX_STORIES_PER_RUN and MAX_STORIES_PER_SOURCE as env vars with defaults
    you justify from the last 14 days of run logs; when a cap cuts, the cut is logged
    with the count and the lowest score that made it in.
B4. Haiku shadow scorer. SHADOW_MODEL env var (default claude-haiku-4-5, kill switch is
    unsetting it). Every story scored by Sonnet in the daily run is also scored by Haiku
    into `news_scores_shadow` (internal), never touching the public tables. The run
    then builds a second Digest and a second Roundup from the shadow scores, subject
    prefixed SHADOW HAIKU, sent to Samuel's address only, for 7 days from tonight, with
    the expiry date in config. Backtest now: score the stored stories of the last 30
    days with Haiku, and write `warehouse/news/shadow_agreement.py`, which reports
    agreement with Sonnet on selection (top-N overlap), on significance score
    (correlation and mean absolute difference), on AI-power tag, per day and overall,
    and the cost of each model for the same stories. It also accepts Samuel's 50-story
    eval file once it exists and reports both models against his labels. Run it, put
    the numbers in the report.
B5. Thesis Builder toward USD 1: cache the shared context, cut retries to one, cap the
    span count, batch the small calls. Run it once on the cheapest existing thesis and
    report the bill before and after.

## Part C: small carried items
C1. Rename the three callers that still use old table names (brief.py, roundup.py, the
    analysis templates). Keep the migration map itself.
C2. Run the chat eval once, report the score and the spend.

## Part D: verify and ship, last
site/scripts/check-routes.mjs and check-values.mjs pass, plus the new price board
blocks added to check-values. Package tests pass. Then deploy. Then the live route
check again. If anything fails, fix it before the report; if it cannot be fixed, roll
the deploy back to the previous build and say so.

## Do not
No new sources, no backfills, no Sonnet re-scoring, no digest rubric changes, no
changes to the public tables' schemas, no deletions from Redivis, no gate changes,
no force push.

## Report: archive/sessions/SESSION_30_REPORT.md
1. Spend: the ledger total for this session by step and model, against the USD 8 cap.
2. Price board v2: what is on the page, the four derived tables with row counts and
   formulas, what is missing and why.
3. Caching measurement, story cap defaults and reasoning, shadow agreement numbers,
   Thesis Builder bill before and after.
4. Anything you decided without a human, each reversible, and why.
5. Run health, gate state, whether the 14:00 UTC run landed during the session.
6. Open questions for Samuel. What was skipped.
Commit after every working step. Push at the end.

## Chain
When the report is written and pushed, read SESSION_31_PROMPT.md and execute it. If
it is absent, stop.