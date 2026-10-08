# Session 153 report: Ask ERCOT learns this week's tables

Run on 8 October 2026 (UTC), unattended, the last session of the chain 150 to 153. An agent built it in a working
copy of its own to a written brief (`runs/session153/BRIEF.md`), in two phases; I checked the landing myself.
`/ask/ercot` and `/grid/ercot` stay `review`.

## Five things to know first

- **19 of the 20 new questions pass, and 98 of the old 100.** All 120 were asked; the stop left none out.
- **Nothing was loaded.** Everything behind the four pages is either one of ten public tables already in the live
  set, or a file the site ships. The files are read by a new tool through the pages' own functions, so Ask's figure
  is the page's figure, never a second copy.
- **Ask refuses the Texas transmission matrix and the utilities' delivery charges, although `/cost-of-power` prints
  them.** Both tables are internal, and a tool that reads them would hand out what the page only shows. The refusal
  says the 2026 matrices are filed, not approved. Yours to reverse.
- **"Ask ERCOT" now answers for CAISO, NYISO, ISO-NE and SPP, but only for what these four pages show.** All ten
  older refusals about another grid still hold. The two new refusals still say "this chat speaks for ERCOT only",
  which is no longer the whole truth.
- **Two of the old 100 are lost against session 148's record: the same two kinds of chart the tool cannot fetch in
  one query** (h13, the average day by hour; h14, a date column by year). Neither read a new table or the new tool.
  One asking each does not say whether the longer briefing played a part; there was no money to ask again.

## Verdict: fit to land in review; not a reason to open Ask. What is left, exactly

1. **One sentence in the briefing** would settle the one new failure (p14): two sources hold Texas's curtailment
   estimate over different days, and the briefing does not say which holds the share. Described, not applied: no
   word of the briefing was changed after the measurement.
2. **The three things the query cannot do in one call** (session 148's list) are still the whole of the old
   failures: the average day by hour, a date column by year, the newest day held.
3. **Which source wins when two hold a figure.** The year's highest hourly demand now answers 91,134 MW from the
   datacenter page's file, where session 143 answered 91,075 MW from EIA's demand. Each is said with its source.
4. The refusals' closing words ("speaks for ERCOT only") want rewording, with the tool's name, if the other grids
   stay.
5. Session 148's two switches are still off (your decision); this run was made with them off.

## What Ask can now read, and what it refuses

- **Reads: ten public tables** already in the live set: `iso_curtailment_monthly`, `caiso_curtailment_daily`,
  `spp_curtailment_daily`, `ercot_wind_solar_hsl_daily`, `caiso_curtailment_profile`; `eia930_demand_growth`,
  `interconnection_queue_summary`, `ercot_large_load_status`, `cost_of_power_hourly_profile`,
  `cost_of_power_carbon`.
- **Reads: the pages' own files** (a new tool, 12 views):
  - `/cost-of-power`: what a flat load paid at a hub or zone (last twelve months, a bad month, by year and month),
    every region of a grid, the hours a grid was tight.
  - `/cost-of-power/seller`: the capture price of solar and wind at a hub and at every hub of a grid.
  - `/curtailment`: the share of available output curtailed, where free energy is (hours below zero and under USD
    5 by place and month), what curtailed energy was worth.
  - `/resources`: the 12 layers with unit, publisher, vintage and range; the value at a longitude and latitude; a
    basin, play, county, lease area or hydrothermal system by name.
- **What each is not, in its briefing**, taken from each page's Method note: the capture price is a fleet's shape,
  not a site's; the hybrid's "Combined" is two revenues added (Ask never adds them); a resource layer is not a
  siting study, and the wind capacity factor is not called gross; Texas's curtailment estimate begins on 28
  September 2026; 2026's transmission figures are filed, not approved.
- **Refuses by name, "held, not shown", with the publisher's sentence and no figure:** `isone_zone_prices_history`,
  `isone_ddg_undelivered_monthly`, `isone_zone_load_hourly`, `nyiso_load_queue`, `texas_transmission_matrix`,
  `texas_delivery_charges`.
- **Words and no figure:** MISO "paused while terms are reviewed"; PJM "licensed source needed".
- **Does not read, and says so:** a siting judgment; a place given by name only; another grid's price on a day,
  demand, mix or batteries.
- One switch (`ASK_PAGES=off`) puts the panel back as session 148 left it.

## Pass rates and cost

| | Asked | Pass | USD a question |
|---|---|---|---|
| New: sentence | 12 | 11 | |
| New: chart | 6 | 6 | |
| New: refuse | 2 | 2 | |
| **New, all** | **20** | **19** | **0.0281** (0.0223 without the first, which wrote the longer briefing to the cache) |
| Old: conceptual | 25 | 25 | |
| Old: chart | 25 | 23 | |
| Old: sentence | 25 | 25 | |
| Old: refuse | 25 | 25 | |
| **Old, all** | **100** | **98** | **0.0202** (0.0186 in session 148's record with the switches off) |

- By page, the new questions: `/cost-of-power` 4 of 4; the generator page 5 of 5; `/curtailment` 6 of 7;
  `/resources` 4 of 4.
- **The one new failure (p14):** what percent of the reported limit Texas output was below. It read the daily table
  instead of the page's file and gave two ratios over other days; the page's figure is 4.57 percent. Asked once
  more with money left (USD 0.026) it read the page's file and passed. The first answer stays the record.
- **The two refusals, as given:** ISO-NE's monthly curtailment, "held, not shown", with the reason and no figure; a
  MISO capture price, "paused while terms are reviewed", no figure.
- Time to the words, the new questions: 5.0 seconds at the median (7 of the 18 number questions under 5 seconds);
  the two refusals 2.25.
- The judge is the rule in code that sessions 143 and 148 used; every expected number of the new questions was
  computed from its file or table by a script that is kept.

## Every pull against its ceiling

- **No data pull. Nothing loaded. No MISO request, no PJM request, no request to production's ask route.**

## Model spend: USD 2.6096 of the USD 3.00 cap (stop at 2.80)

| Run | Questions | USD | Planned before the first call |
|---|---|---|---|
| The 20 new, first | 20 | 0.5613 | 0.55 |
| The old 100, one of each kind in turn | 100 | 2.0219 | 2.04 |
| p14 once more | 1 | 0.0264 | none planned; money remained |
| **Total** | **121** | **2.6096** | 2.59 |

- Phase 1 made no model call. **Nothing was refused by the stop; no paid answer was discarded; no question errored.**
- The site's own ledger agrees to the cent (237 calls, 121 questions).
- **Today's site ledger stands at USD 5.26**, with session 148's of the same day: over production's daily ceiling
  of 3, so production would refuse questions until 00:00 UTC on 9 October. It is closed anyway
  (`ASK_VISITOR_SALT` is not set). October stands at USD 15.37 of 30.

## The landing

- **Added after the landing.** Pushed as `task/153-ask-tables` (`7b0fd94`): checks passed (run 37714785350), merged
  as `9103f10`. The whole suite in a clean copy: 2,109 tests, passed. On the merged build: `check-routes` 0 failed,
  the Ask panel 13 of 13, the words before the chart 9 of 9, `check-values` 7,026 of 7,026.
- **Vercel built it:** "Deployment has completed" for `9103f10` at 01:55:45 UTC on 8 October.
- **Snapshot before** (`153_before`, 01:48:40 UTC) **and after** (`153_after`, 01:55:55 UTC): **0 differences** on
  the 25 live addresses, 3,357 checked number keys. Nothing was reverted.
- **On production, in the internal view, with recorded answers and no model call:** the panel's check 13 of 13 and
  the words-before-chart check 9 of 9.
- Nothing a live page renders or reads is changed: `site/lib/supabase.ts`, `site/lib/pages.ts`, `next.config.ts`,
  the live set and every `site/data` file are untouched.

## Checks

- `site/scripts/test-ask-tables.mjs` 14 of 14; `tests/test_session153.py` 15 tests; the Ask sessions' and the four
  pages' neighbouring tests (392); the whole suite on the merged branch in the working copy: 2,094 tests, passed.
- One assertion of `tests/test_session149.py` changed: it forbade any file under `site/` to name ISO-NE's internal
  curtailment table, and the tool must name the table to refuse it by name. The test now exempts that one file.

## Decisions made without you

1. Ask refuses the Texas matrix and delivery charges (above).
2. Ask answers for the other grids only for what the four pages show.
3. ISO-NE's zones since 26 August 2026 stay readable from its public tables; only the internal history is refused.
4. The page files are read through a tool, not loaded as tables: no second copy that can drift.
5. p14 was asked once more with the money left; the first answer stays the record.

## The five most interesting numbers

1. **19 of 20 and 98 of 100**, for USD 2.61 of 3.00.
2. **USD 0.0281 against 0.0202**: a question about the new pages costs about four tenths more than an old one,
   most of it the first question's write of the longer briefing to the cache.
3. **4.57 percent**: Texas wind and solar output below the reported limit on the page's days, the figure the one
   failed answer missed by reading the other source.
4. **91,134 against 91,075 MW**: the year's highest hourly demand from two sources Ask can now both read.
5. **6 tables refused by name, 10 added, 12 views of the pages' own files**: what the briefing gained.
