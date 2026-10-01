# SESSION 49: The big data push

## Read first
CLAUDE.md, PRIORITIES.md, docs/datastandard.md, the erw-add-connector skill,
SESSION_42_PROMPT.md, archive/sessions/SESSION_46_REPORT.md, SESSION_47_REPORT.md and
SESSION_48_REPORT.md (open questions), the untracked
warehouse/connectors/eia930_interchange.py.

## Budget and rules
- Expected Anthropic API spend: USD 0. Hard cap: USD 0. No model calls.
- The gate is open: daily run 14 passed (2026-10-01 00:20 UTC). No gate routing.
- Supabase is at 382 MB after Samuel's manual VACUUM FULL of public.series. History
  tables never go into Supabase; a small derived table goes in only if the live set
  stays under 395 MB after its load.
- Approved pulls (Samuel, Sept 30), each with its ceiling, license checked before
  loading, raw files saved, resumable:
  a. EIA-930 interchange, last 30 days, every BA pair: 150,000 rows.
  b. One year (2025-09-01 on) of main-hub day-ahead and real-time prices: CAISO SP15
     and the NP15 zone, MISO Indiana Hub, NYISO N.Y.C., ISO-NE .H.INTERNAL_HUB, SPP
     SPPNORTH_HUB; kept as history past the rolling window: 1.5 million rows.
  c. NOAA NCEI hourly station data (public domain), temperature and dew point,
     stations DFW, IAH, SAC, LAX, PHL, ORD, MSP, JFK, BOS, OKC, for every event window
     and its baseline days: 100,000 rows.
  d. EIA-930 six-month files, 2018-01-01 to 2018-06-30, eight BAs, demand and net
     generation: 100,000 rows.
  e. Texas Railroad Commission well-level monthly production: read and record the
     RRC's data terms first; proceed only if reuse is allowed (internal license if
     unclear). One major Permian county (state why), latest 24 months: 500,000 rows.
- No time cap; no redundant work; one table in memory at a time; pull and merge if the
  daily job lands, never force push; commit after every working step. If one part
  fails, record it and move to the next part.

## Part 0 (small)
1. Weekly maintenance workflow (approved by Samuel): .github/workflows/weekly-vacuum.yml,
   Sunday 10:00 UTC, runs VACUUM (FULL, ANALYZE) on the Supabase shape tables and
   records the size in run_status; runbook updated. If your tool permissions refuse to
   write it, say so in the report and continue.
2. upload.py: a --tables option to upload named tables only; upload
   event_study_estimates to the public draft with it.
3. /deals: at the start of a month with no deals yet, show the previous month,
   labeled.

## Part A: the 3D network
Execute SESSION_42_PROMPT.md's Parts A to C (pull a; check the drafted connector's
field names against the API first), writing SESSION_42_REPORT.md.

## Part B: a year of hub prices
Pull b. Connectors, validator, archive, coverage, Redivis draft, run_status, source
registry; the daily run appends to the histories, never trims. Then rebuild
cost_of_power_* with twelve months for every ISO (ranked bar and calculator on the
latest complete month every ISO holds; report old and new defaults side by side);
/learn/bill switches PG&E's wholesale reference to NP15, labeled; the shape-premium
draft rereads with a twelve-month view for every hub.

## Part C: weather and the 2018 baseline in the event studies
Pulls c and d. event_window_daily: COVID's 728-day baseline restored; per station and
day: temperature mean, min, max, heating and cooling degree days at 65 F.
event_study.py: add a temperature-controlled specification (degree days and their
square) and, as a robustness row only, a linear-trend specification; each /events
page shows the original and the temperature-controlled estimate and one sentence on
how much weather explains, read from the table; the methods page and the notebook
include both. Say only what the numbers show.

## Part D: Texas wells into the lease tool
Pull e (terms first). Table, validator, archive, coverage, Redivis (internal if
needed). /severance/lease gets "Load a real lease": pick an operator and lease in the
pilot county, fill the tool with its real monthly production and warehouse prices,
show the flags; behind the internal token if the license is internal.

## Verify and ship, after each part
check-values, check-routes, tests/, deploy, live checks.

## Report: archive/sessions/SESSION_49_REPORT.md
Per part: done or not, rows against its ceiling, licenses, what each page now shows
(old against new where rebuilt); the weather-controlled estimates beside the originals;
RRC terms and the pilot county; Supabase before and after; decisions made without a
human; open questions; wall time; spend USD 0 confirmed. Push. Stop.