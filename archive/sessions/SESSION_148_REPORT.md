# Session 148 report: Ask ERCOT, the last seconds

Run on 7 and 8 October 2026 (UTC), unattended, in the chain 146 to 149. An agent built it in a working copy of its
own to a written brief (`runs/session148/BRIEF.md`), in two phases; I ran the locked writes, the load and the
landings myself. `/ask/ercot` and `/grid/ercot` stay `review`.

## Five things to know first

- **The two new switches are OFF in the code, by your rule.** With the rollup, the rule-made plan and the lower
  effort all on, 98 of the 100 questions pass, not 100. Two charts failed (h14, h24), and neither failure can be
  laid to a change: h14 failed again with the lower effort off and again with the tool's guide as session 143 left
  it; h24 failed with the reserve tables offered (twice) and passed without them (twice). The money ended there.
- **With everything on, a number question takes 4.75 seconds to its words at the median** (6.2 before; the target
  is 5): 27 of 50 under 5 seconds (15 before). An idea takes 2.1 seconds (2.3 before; the target is 2): 7 of 25
  under 2. **The code as it stands, with both switches off, was not measured as a whole.**
- **The rollup stays, and it did what you asked.** A year of reserve prices by month: 43.9 seconds and 8 model
  calls before, 2.5 seconds and 1 now. No question reads a year of hourly rows: an hourly read with no start, or of
  more than 35 days, is refused once the two tables are in the catalogue, and the daily or monthly table is offered.
- **The shared reader changed, and the live pages did not.** One large query's pages are now asked four at a time.
  44 reads of the three live pages (40,647 rows) read both ways: 0 different. Landed alone, with its own snapshot:
  no number moved. `ERW_PAGES_TOGETHER=1` on the server is the old reader.
- **"Before" passes 100 of 100**: session 143's 77 recorded answers, and the 23 left from last night asked first
  today on the tool as session 143 left it (every new switch off, the rollup not offered).

## Verdict: not ready to open on speed. What is left, exactly

1. **Your decision on the two switches.** Either can be set on the server with no code change (`ASK_RULE_PLAN=on`,
   `ASK_READER_EFFORT=low`). The rule planned 16 questions and all 16 pass, in one model call each, at 3.0 seconds
   where they took 5.5. The lower effort took the reading turn from 2.96 to 2.04 seconds and lost no question that
   passed again without it. They are off only because 98 is not 100.
2. **Three things the query cannot do in one call**, which are the whole slow tail and both failures: the average
   day by hour (24 variables as one series), a date column grouped by year, and "the newest day held" for a table.
   Each is a change to the tool, not to the model.
3. **The "entity or node" filter**: one read of 30 rows of `ercot_hub_prices_daily` took 12.6 seconds. Warm, that
   filter is about five times slower than "entity" alone.
4. **Ideas are at 2.1 seconds**: one model call. Nothing in tonight's four changes reaches under 2 at the median.
5. **h24 with the two reserve tables offered**: two fails against two passes without. About USD 0.08 an asking.
6. Hourly demand in the live set stops at 4 October, which makes "yesterday" slow today.
7. Still open from before: `ASK_VISITOR_SALT` on production, the provider's spending limit, the words on `/terms`.

## Time to the words, before and after, all 100

Seconds, median (90th percentile). After: one run of all 100 with the rollup, pages together, the rule and the lower
effort on.

| Kind | n | Before | After | Under 5 s, before, after | Under 2 s, before, after |
|---|---|---|---|---|---|
| Conceptual (target 2 s) | 25 | 2.3 (4.4) | **2.1** (3.0) | 24, 25 | **2, 7** |
| Chart | 25 | 6.2 (23.3) | 4.8 (20.6) | 7, 14 | 0, 0 |
| Sentence | 25 | 6.2 (13.5) | 4.7 (12.0) | 8, 13 | 0, 2 |
| Refuse | 25 | 2.1 (3.7) | 2.0 (3.1) | 24, 24 | 3, 11 |
| Number, both (target 5 s) | 50 | 6.2 (17.4) | **4.75** (16.1) | **15, 27** | 0, 2 |
| All | 100 | 4.2 (11.9) | 2.8 (7.7) | 63, 76 | 5, 20 |

- Stage medians for a number question, before then after: planning 3.0 then 2.0 seconds; fetching 0.17 then 0.18;
  writing 3.6 then 3.4.
- 66 of the 100 answers were faster. Every answer's words came before the whole answer; none was withdrawn.

## Pass counts and cost

| Kind | Before | After | USD a question, before | After |
|---|---|---|---|---|
| Conceptual | 25 of 25 | 25 of 25 | 0.0119 | 0.0099 |
| Chart | 25 of 25 | **23 of 25** | 0.0331 | 0.0314 |
| Sentence | 25 of 25 | 25 of 25 | 0.0209 | 0.0201 |
| Refuse | 25 of 25 | 25 of 25 | 0.0084 | 0.0071 |
| **All** | **100 of 100** | **98 of 100** | 0.0186 | **0.0171** |

- The judge is a rule in code (`site/scripts/eval-judge.mjs`), the one session 143 used: it costs nothing.
- The 100 in all: USD 1.86 before, 1.71 after.

## What each change did, and whether it stayed

- **The reserve price rollup: stayed.** `ercot_as_prices_daily` (70,120 rows) and `ercot_as_prices_monthly` (2,325),
  from the hourly table: for each product and day or month, the mean, the lowest, the highest and the count of
  hours held. A short day or month is not filled: it carries its count (0 short days in 14,014 product-days; 6
  short months in 465). 25 of 25 hand-checked figures agree with the hourly rows. In the daily run after the hourly
  table's step. Method: `docs/methods/ask_ercot.md` and the rollup's own note.
- **Pages read together: stayed.** Its effect cannot be told apart in the 100 questions; on the live pages' own 16
  reads of more than one page it took 7.1 seconds to about 3.
- **A plan made by rule: built, off.** Three shapes (a hub price over a named period, generation over a named
  period, a reserve price), 16 of the 100 questions; it must account for every word and never fills a default.
- **Lower effort on the reading turn: built, off.** A question answered without reading has only one call, so with
  the switch on its words are written at the lower effort too.

## Every pull against its ceiling

- **No data pull.** The hourly table on the data machine was two days behind; I restored it from Redivis (336,572
  rows, to 7 October) before the rollup was written. No request to ERCOT.
- **No MISO request. No PJM request. No request to production's ask route.**

## Model spend: USD 2.6531 of the USD 3.00 cap (stop at 2.80)

| Run | Questions | USD | Planned before the first call |
|---|---|---|---|
| The 23 left from last night, on the tool as session 143 left it | 23 | 0.5201 | 0.47 |
| All 100, every change on | 100 | 1.7140 | 1.70 |
| h14 and h24 again, the lower effort off | 2 | 0.1858 | 0.50 for all re-asks |
| h14 and h24 again, the reserve tables not offered | 2 | 0.2331 | |
| **Total** | **127** | **2.6531** | 2.67 |

- Phase 1 made no model call. The first call was at 00:00:18 UTC on 8 October.
- **Nothing was refused and no paid answer was discarded.** A 128th question was not asked: the costliest answer
  of the night was USD 0.17, and one like it would have passed the stop.
- The site's own ledger agrees to the cent (245 calls, 127 questions). **Today's site ledger stands at USD 2.65 of
  production's daily ceiling of 3.** October stands at USD 12.76 of 30.

## The landings

- **Phase 1** (the rollup's code, pages together, the two switches, and `REVIEW_FREEZE` with its new end): pushed as
  `task/148-ask` (`3b0e5db`), checks passed (run 37702309122), merged as `cb511a3`. **Vercel built it:**
  "Deployment has completed" at 23:35:33 UTC on 7 October.
- **Snapshot before** (`148_before`, 23:26:23 UTC) **and after** (`148_after`, 23:35:50 UTC): **6 differences, all on
  `/network`, all its own hourly refresh at 23:05 UTC** (the refresh stamp, the newest demand hour from 20:00 to
  21:00 UTC, the source line's build stamp): expected, and not this deploy. **No checked number moved** (3,357 keys).
  Nothing was reverted.
- **The load** of the two rollup tables (72,445 rows; the loader also wrote the registry of sources whole, 281
  rows): Supabase matched both counts. **Snapshot before** (`148_load_before`, 23:36:19 UTC) **and after**
  (`148_load_after`, 23:37:28 UTC): **0 differences.**
- Written under the lock, nothing released: validator, coverage, the archive and the Redivis draft, exit 0 each.
- **Phase 2** (the record of all 100, its script, the method's paragraph, the tests, this report): pushed as
  `task/148-record` (`f24e5e4`), checks passed (run 37708506009), merged as `74e9ab3`. **Vercel built it:**
  "Deployment has completed" at 00:41:56 UTC on 8 October. The whole suite in a clean copy: 1,968 tests, passed.
- **Snapshot before** (`148b_before`, 00:34:31 UTC) **and after** (`148b_after`, 00:42:08 UTC): **6 differences, all
  on `/network`, all its own hourly refresh at 00:05 UTC** (the refresh stamp, the newest demand hour from 21:00 to
  22:00 UTC, the source line's build stamp): expected, and not this deploy, which holds no site code. **No checked
  number moved** (3,357 keys). Nothing was reverted. (Line added after the landing.)

## Checks

- The whole suite in a clean copy of the phase 1 commit: 1,809 tests, passed. `tests/test_session148.py`;
  `site/scripts/test-ask-speed.mjs`: session 143's 13 unchanged, 21 new (recorded reads and a stand-in for the
  model: no request).
- **One thing seen twice:** on a machine's first request after a build, a page can be served from that machine's
  older fetch cache and refreshed behind it. It showed 10 differing values on two battery addresses in the agent's
  first local take, and 6 in my first `check-values`; a second run each time showed 0. Production's snapshots
  showed no such thing.

## Decisions made without you

1. Two tables, not one (a day's and a month's row would share a key on the first of each month).
2. 35 days is "a few weeks": the window the site keeps of every other interval table.
3. **The hourly refusal covers every aggregation**: a median or a count of hours of hourly reserve prices over more
   than 35 days is no longer answered from the site. None of the 100 asks one. Say if you want those let through.
4. The rule never fills a default: the hub, the market and the period must be named, and it plans a first question
   only.
5. The before run of the 23 was made on this build with every new switch off, not from a build of the old commit.
6. The 148 landing went first and alone, so the shared reader's snapshot would be its own.

## The five most interesting numbers

1. **43.9 seconds and 8 model calls, now 2.5 seconds and 1**: a year of reserve prices by month.
2. **6.2 to 4.75 seconds** to the words for the 50 number questions, and **15 to 27** of them under 5 seconds.
3. **16 of 16**: every question the rule planned passes, in one model call, at 3.0 seconds where it took 5.5.
4. **2.96 to 2.04 seconds**: the reading turn at the lower effort, with no question lost to it.
5. **12.6 seconds for 30 rows**: the slow tail is now one filter on one table, and three things the query cannot ask.
