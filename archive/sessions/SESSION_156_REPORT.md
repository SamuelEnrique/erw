# Session 156 report: Ask ERCOT, to ready

Run on 8 October 2026 (UTC), unattended, in the chain 155 to 159. An agent built it in a working copy of its own to
a written brief (`runs/session156/BRIEF.md`), in two phases; I checked the merged build and the landing.
`/ask/ercot` and `/grid/ercot` stay `review`.

## Four things to know first

- **All 120 questions pass: 100 of 100 and 20 of 20**, each asked once (98 and 19 last night). Nothing failed, so
  nothing was asked again.
- **A number question takes 4.6 seconds to its words at the median, and 30 of 50 are under 5** (4.75 and 27 last
  night; the target is 5). The slow tail fell most: the 90th percentile went from 15.9 to 7.8 seconds. **An idea
  takes 2.1 seconds; 8 of 25 are under 2. The target of 2 is still missed.**
- **Your precedence ruling, as applied:** the year's highest hourly demand now leads with 91,134 MW, ERCOT's own
  hourly load, and names 91,075 MW from the derived table. (My brief's example had the two the wrong way round;
  the agent followed your ruling, not my example.)
- **The two switches are on by default** (`site/lib/chat/switches.ts`); a server variable still turns either off.

## Verdict: ready to open on what was measured. What is left, exactly

1. Ideas at 2.1 seconds, not 2: one model call; nothing in tonight's changes reaches under it at the median.
2. Two passing answers still take over 20 seconds: "this week" when the week is not held (24.7 seconds, 10 model
   calls), and generation by fuel over seven days (28.6 seconds, 7 calls).
3. 20 of the 50 number questions are over 5 seconds: that time is the model's two turns, not the reads.
4. Each question was asked once. A second asking of all 120 costs about USD 2.25.
5. The 24 hours of a day show as a table of 24 rows, not a line: the shared chart has no hour-of-day axis and a
   shared component was not touched.
6. Not checked in this session, from session 148's list: `ASK_VISITOR_SALT` on production, the provider's spending
   limit, the words on `/terms`. The Python reference loop does not have the three new forms.

## What was built

- **Three things the query now does in one call**, each 0.1 to 0.8 seconds on the live set, no migration:
  - the average day by hour: 24 values as one series, with the days behind each hour; nothing filled;
  - a date column grouped by year (the queue by planned year: 628 requests, 118,906 MW, 8 years);
  - the newest day held for a table (demand's newest whole day is 3 October; 4 October holds 19 of 24 hours).
- **The slow filter**: the entity is asked first (0.05 to 0.08 seconds against 0.35 to 0.47).
- **The briefing sentence** on which source holds Texas's curtailment share, from the page's Method note.
- **Source precedence** as a rule in the briefing and in what a page file's view returns.
- **The refusals close in the tool's own name**; the judge now asks 13 refusals for the new words, so it is
  stricter than last night's. Assertions in four older test files that pinned the switches off, the old filter and
  the old words were changed; each is listed in the agent's report.

## The seven questions named in the earlier reports

| Question | Before | Now |
|---|---|---|
| h13, batteries across the hours of a day | 28.0 s, 9 model calls | 5.3 s, 2 calls |
| h14, queue capacity by year | failed | 4.4 s, passes |
| h24, wind across the hours of a day | failed | 4.5 s, passes |
| h03, demand hour by hour for yesterday | 23.9 s, 10 calls | 4.8 s |
| s12, lowest hourly demand yesterday | 19.3 s, 7 calls | 4.6 s |
| p14, Texas output below the reported limit | failed | 3.5 s, passes (4.57 percent) |
| s16, the year's highest hourly demand | one source | leads with ERCOT's 91,134 MW, names 91,075 MW |

## Pass rate, time and cost

| | The 100 | The 20 |
|---|---|---|
| Pass | **100 of 100** (98 in sessions 148 and 153) | **20 of 20** (19) |
| Time to the words, number questions, median | 4.6 s; 30 of 50 under 5 s | 4.15 s; 13 of 18 under 5 s |
| Ideas, median | 2.1 s; 8 of 25 under 2 s | |
| USD a question | 0.0169 (0.0171; 0.0202 with the switches off) | 0.0279 (0.0281) |

## Every pull against its ceiling

- **No data pull. Nothing loaded. No request to production's ask route. No MISO or PJM request.**

## Model spend: USD 2.2513 of the USD 4.00 cap (stop at 3.70)

- Phase 1 made no model call. One run of all 120, the stop before each question; nothing refused, no paid answer
  discarded; USD 1.45 left under the stop, unspent.
- The site's own ledger agrees to the cent (194 model calls, 120 questions). **Today's site ledger stands at USD
  7.51**, over production's daily ceiling of 3: production would refuse questions until 00:00 UTC on 9 October. It
  is closed to visitors anyway.

## The landing

- **Added after the landing.** Pushed with sessions 156, 157 and 159 as `task/156-157-159` (`bc1fba0`): checks passed (run
  37764344933), merged as `a161ec5`. **Vercel built it:** "Deployment has completed" at 10:43:19 UTC on 8 October.
- **Snapshot before** (`157_before`, 10:34:04 UTC) **and after** (`157_after`, 10:43:32 UTC): **0 differences** on the
  25 live addresses, 3,357 checked number keys. Nothing was reverted.
- **On production, in the internal view:** the policy page's check 45 of 45, the resource map's 97 of 97, the Ask
  panel's 13 of 13 (recorded answers).
- Nothing a live page renders or reads is changed; `site/lib/supabase.ts` and `site/lib/pages.ts` are untouched.

## Checks

- On the merged build: the Ask panel 13 of 13 and the words-before-chart check 9 of 9 (recorded answers);
  `check-routes` 0 failed. `test-ask-ready.mjs` 20; `tests/test_session156.py` 18. The whole suite in a clean copy
  of the merged commit: 2,440 tests, passed.

## Decisions made without you

1. The precedence as you ruled it, against my own brief's example.
2. The line under the title on `/ask/ercot` and the first line of "What it does not answer" reworded with the
   refusals.
3. One switch (`ASK_FORMS=off`) shows the model the tools as session 153 left them.

## The five most interesting numbers

1. **120 of 120**, for USD 2.25.
2. **15.9 to 7.8 seconds**: the 90th percentile of a number question's time to its words.
3. **28.0 seconds and 9 model calls to 5.3 seconds and 2**: batteries across the hours of a day.
4. **2028**: the largest planned year in ERCOT's queue held, 251 requests and 45,624 MW of 628 and 118,906.
5. **2.1 seconds**: an idea, still over the target of 2.
