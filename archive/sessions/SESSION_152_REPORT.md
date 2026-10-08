# Session 152 report: loose work landed

Run on 8 October 2026 (UTC), unattended, in the chain 150 to 153. An agent built it in a working copy of its own to
a written brief (`runs/session152/BRIEF.md`); I ran the locked steps, the merged build and the landing myself.

## Four things to know first

- **ERCOT's forecast archive was not pulled: there is no open one. 0 rows of the 1,500,000 allowed.** ERCOT lists
  seven days of the two hourly forecast reports openly (187 postings each) and no more. The history is offered only
  through its Data Access Portal, which answers a plain request with HTTP 401, "Access denied due to missing
  subscription key", and sends a signed-in user's token with every archive request. That is an account and a key
  tied to a person: recorded and left. No registration, no address sent. The mix page's forecast view is unchanged.
- **The demand-with-weather page is folded into `/demand`, not beside it.** `/demand` already existed, so by your
  rule (one tool, one page, one address) the weather page is its second view: `/demand?view=weather`;
  `/demand/weather` redirects there. Both are `review`. Nothing either page showed is dropped (below).
- **One row of main's metadata was wrong, and the branch's is kept.** Main's coverage said
  `ferc_eqr_contracts_history` holds 190,816 rows; the table on the data machine holds 571,115 (session 125's later
  build, validator passes). Main has described a third of that table since 5 October.
- **Sunday's chart, as the tables stand: CAISO Regulation Up, day-ahead.** It ties on score with WTI and wins on the
  second rule. WTI rests on a fuel price table that ends 29 September on this machine, so Sunday's pick can differ.

## Verdict: the page is landed and locked; the pull could not be made; the chooser's pick is reported

What is left, exactly:

1. **ERCOT's forecast history needs an account with ERCOT's data portal** (a person's, with its subscription key).
   Yours to decide whether to open one. Without it the view holds what the daily run has kept since it began: the
   connector reads the open week each day, so history grows by itself from now.
2. `/demand` has no menu entry (it had none on main). The line for the "Grid" group is in the agent's report, if you
   want it after 18:00 UTC.
3. A hover does not exist on a phone: the sentences moved off the face are in the Method notes, not on the page there.
4. `wip/129-demand-weather-finished`, `wip/126-demand-weather` and `wip/125-contracts` now hold nothing main lacks.
   I deleted their remotes after the landing (below).

## Part 1: demand with weather

- **The merge:** 33 files, nine conflicts, all in generated metadata and two lists; both sides kept, no row of
  main's lost (a resolver that stops if one would be; a test finds no key doubled). Six weather tables' rows, four
  contract tables' rows in the manifests, four sources added.
- **What rode in with the page:** session 125's contract tables' registry and method (four quarters), a fix to the
  contracts connector, the reports of sessions 124 to 126 and 129, the NOAA and Census connectors and the weather
  builder (none scheduled), the method. Their User-Agent holds the repository's address and no person's.
- **The tables:** six, all on the data machine, all passing the validator, each count equal to its coverage row
  (`noaa_station_weather_hourly` 4,714,333; `noaa_grid_weather_hourly` 1,894,465; `noaa_grid_weather_daily`
  117,814; `eia930_demand_weather` 1,057; `census_metro_population` 1,650; `noaa_grid_weather_stations` 245).
  **None is in the live set and none is loaded:** the view reads the site's own copy (408 figures compared with
  the table, all equal). No table a live page reads is touched.
- **What each old page showed, and where it is now:**
  - `/demand` (session 97): the sentence, three headline numbers, the years' chart and table, the heat map by month
    and hour, the bars, the ranking, California's check: all as they were, the first view ("As metered").
  - Its boxed paragraph "Weather is not removed" and its two folds: off the face. Short words with a hover, and the
    Method note. The counts of hours left out are now numbers under the chart.
  - `/demand/weather` (sessions 126 and 129, never on main): the sentence, the chart of explained and unexplained
    growth by grid, the table by grid and year, the four folds: the second view, each fold's prose now a hover.
  - Both old page files are kept, not routed.
- **Every chart answers the mouse** (five charts). No method prose on the face.

## Part 2: ERCOT's archived wind and solar forecast reports

| Pull | Ceiling | Read |
|---|---|---|
| ERCOT's archived wind and solar forecast reports | 1,500,000 rows; I allowed 400 requests and 2 GB | **0 rows.** 14 requests, 1.3 MB, all of them looking |

- Tried: ERCOT's open lists of both reports (seven days each); the report's product page ("Retention Policy: N/A";
  its one way to history is the portal); the portal (a script that sends a signed-in user's token and a
  subscription key); the archive address, plainly (401); ERCOT's generation page (no yearly or monthly file of the
  forecasts; the one yearly file is output only, held since session 144).
- User-Agent: the connector's own, which holds the repository's address and no person's. No cookie, key or form.
- **No MISO request. No PJM request.**
- ERCOT's terms, as session 144 quoted them, checked against today's page: "The publicly available contents of
  this website may be used, reproduced, and redistributed, provided that the contents are not modified and that
  you maintain all copyright and other notices contained in the contents, including this Agreement."

## Part 3: the weekly chart chooser

- **The choice is made by a rule, not a model**; the only model call is the two-sentence note written after it. A
  new `--dry-run` makes the choice, prints every candidate and writes nothing. Run once against the data machine's
  tables: 40 measures ran, 28 compete, the week is 2026-W41.
- **The rule:** the measure whose newest change ranks highest among its own earlier changes (the last 104 weekly or
  36 monthly). The score is the percent of earlier changes that were smaller. A tie goes to the higher robust z.
- **The pick for Sunday 11 October: CAISO Regulation Up, day-ahead**: 5.04 USD/MW in the week of 28 September to 4
  October, up 1.73 from 3.31. Of the 104 weekly moves before it, 7 were as large. Score 93.3, z 4.79.
- **The runner-up: WTI**, 93.57 USD/bbl in the week of 21 to 27 September, down 9.97. Score 93.3, z 3.77. Its table
  ends 29 September on this machine: with the runner's newer week it may score differently.
- Then: New York Harbor diesel 88.5; SPP Regulation Up 88.5; NYISO regulation 83.7; Brent 82.7.

## Model spend: none

- No model or API call from code. No cap was set for this session.

## The landing

- **Added after the landing.** Landed with session 150 in one push (`task/150-152`, commit `e705393`): checks
  passed (run 37711233439), merged as `b7684f6`. The whole suite in a clean copy: 2,077 tests, passed.
- **Vercel built it:** "Deployment has completed" for `b7684f6` at 01:15:32 UTC on 8 October.
- **Snapshot before** (`150_before`, 01:06:08 UTC) **and after** (`150_after`, 01:15:53 UTC): **6 differences, all on
  `/network`, all its own hourly refresh at 01:05 UTC**: expected, and not this deploy. **No checked number moved**
  (3,357 keys). Nothing was reverted.
- **On production, in the internal view:** the demand page 102 of 102, the weather view 78 of 78.
- Under the lock, nothing released and nothing loaded: coverage rebuilt from the ten tables (the weather tables and
  the contract tables), the archive (0 rows new), the Redivis drafts (12 of 12 tables, counts equal).
- The remotes of `wip/129-demand-weather-finished`, `wip/126-demand-weather`, `wip/125-contracts` and
  `wip/124-network-v3` are deleted: each was wholly on main.
- `site/lib/pages.ts` and `site/lib/supabase.ts` are untouched. `site/next.config.ts` gains one redirect.

## Checks

- On the agent's build: the demand page 102 of 102, the weather view 78 of 78 (65 on its old branch),
  `check-routes` 0 failed, the whole suite 2,041 tests passed.

## Decisions made without you

1. The weather page became a view of `/demand`.
2. The four contract tables' coverage rows are the branch's (they describe the tables).
3. No registration with ERCOT's portal.
4. The chooser's dry run turns its value cache off, so nothing is written.

## The five most interesting numbers

1. **Plus 24.2 percent**: Texas's 2025 demand growth over 2019 that weather does not explain, give or take 4.0
   (growth 26.5, weather 2.4).
2. **571,115 against 190,816**: the rows of the contracts history table against main's coverage row for it.
3. **7 of 104, twice**: CAISO Regulation Up (up 1.73 to 5.04 USD/MW) and WTI (down 9.97 to 93.57 USD/bbl) each had
   7 larger weekly moves in two years; z 4.79 against 3.77 decides Sunday's chart.
4. **187 postings, 7 days**: all that ERCOT lists openly of each forecast report; the request for more answers 401.
5. **180 of 180**: the two views' checks on the built page, five charts read under the mouse.
