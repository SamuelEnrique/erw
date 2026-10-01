# SESSION 48: Weather, the 2018 baseline, Texas wells, and issue cleanup

## Read first
archive/sessions/SESSION_47_REPORT.md, PRIORITIES.md, docs/datastandard.md, the
erw-add-connector skill, event_window.py, event_study.py, the severance lease tool
(site/lib/lease.ts, /severance/lease), weather_obs_hourly and its connector.

## Part 0
1. GitHub issues: close #6 to #10 (daily run failures) with a comment naming the fix
   commit, once a daily run has passed; if none has, leave them. For #3 (CARB), #4
   (NYISO queue) and #5 (ERCOT large-load queue): add each to the known-gap list with
   its reason (CARB and NYISO answer HTTP 202, refreshed from local runs; ERCOT
   publishes no request-level list), make the three-day issue opener skip known gaps,
   and close the three with that note.
2. The gate: read the latest daily-prices run. Passed: Parts A and B. Otherwise the
   fallback.

## Budget and rules
USD 0, no model calls. Approved pulls (Samuel, Sept 30), each with its ceiling, license
checked before loading, raw files saved, resumable, history out of Supabase:
- NOAA NCEI hourly station data (ISD or LCD, public domain), temperature and dew point,
  one or two stations per grid (ERCOT DFW and IAH; CAISO SAC and LAX; PJM PHL and ORD;
  MISO MSP; NYISO JFK; ISO-NE BOS; SPP OKC), for every event window and its baseline
  days. Ceiling 100,000 rows.
- EIA-930 six-month files for 2018-01-01 to 2018-06-30, eight BAs, demand and net
  generation. Ceiling 100,000.
- Texas Railroad Commission well-level monthly production: first read the RRC's data
  terms and record them; proceed only if public reuse is allowed. One county (choose a
  major Permian county and state why), the latest 24 months, oil, gas and condensate
  per lease or well as RRC publishes it. Ceiling 500,000 rows. Internal license if the
  terms are unclear.
Pull and merge if the daily job lands, never force push, commit after every step.

## Part A: weather and the 2018 baseline into the events
1. Connectors, validator, archive, coverage, Redivis draft.
2. event_window_daily: COVID's 728-day baseline restored; daily temperature rows (mean,
   min, max, heating and cooling degree days at 65 F) per station for every event and
   baseline day.
3. event_study.py: add a temperature-controlled specification (degree days, and their
   square) beside the session 47 one; each /events page shows both estimates and one
   sentence on how much the weather explains, read from the table. The methods page
   and the replication notebook include it.

## Part B: Texas wells into the lease tool
1. Connector and table (tier source, license as the terms allow), validator, archive,
   coverage, Redivis (internal if needed).
2. /severance/lease: "Load a real lease" picks an operator and lease in the pilot
   county and fills the tool with its real monthly production, prices from the
   warehouse, and the flags. If the license is internal, the option is behind the
   internal token.
3. Tests, check-routes, deploy, live checks.

## Fallback (gate closed)
No pulls. Draft the first deep-dive report, internal only, not in the nav: "What flat
load pays: the shape premium across six ISOs", 1,500 words, every number read from a
table with a check key, charts in the Stanford palette, at /reports/draft/shape-premium
behind the internal token.

## Report: archive/sessions/SESSION_48_REPORT.md
Issues closed and known gaps added; gate state; rows per pull against its ceiling;
RRC terms; the weather-controlled estimates next to the originals; the pilot county
and a sample lease; decisions made without a human; open questions; wall time; spend
USD 0 confirmed. Push. Stop.