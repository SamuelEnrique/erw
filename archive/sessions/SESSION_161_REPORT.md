# Session 161 report: Ask ERCOT's day as a line, the two slow shapes, the 120 asked again

Run on 8 October 2026 (UTC), 22:09 to 22:57, unattended. Mine from start to end; no agent. `/ask/ercot` and
`/grid/ercot` stay `review`.

## Not as you asked: read these first

- **The rerun stopped at 104 of the 120.** Your cap of USD 2 is below what the 120 cost in session 156 (USD 2.25).
  All 100 of session 137 were asked, and 4 of the 20 of the four pages. **16 page questions were not asked** (p04 to
  p18 and p20). Asking them is about USD 0.45.
- **There is no daily rollup of generation by fuel to read.** No such table is held. I made the read itself roll the
  hours up: one read gives every fuel over the period, a second gives the total by day. A derived daily table is
  yours to order.
- **Ideas and refusals were slower than in session 156**: 2.4 and 2.5 seconds at the median, against 2.1 and 2.1.
- **Your message came as pasted text with no line of yours around it.** I asked once and started on your "go".
- `wip/held-grid-network` is still held off main: you have not named it.

## Verdict

- **(a) Done and live in review.** The average day by hour is one line with hover; the 24 rows are folded under it.
  No chart on the three live pages changed.
- **(b) Done.** Neither slow shape is slow: no answer of the 104 took over 20 seconds (two did in session 156).
- **(c) Done as far as the cap allowed: 104 asked, 104 pass.** Numbers and cost hold at session 156's level; ideas
  and refusals are slower.
- **Ask ERCOT: ready to open on what was measured, as session 156 said.** What is left is below.

## Model spend: USD 1.7806 of the USD 2.00 cap

- One run, the stop before each question (stop 1.95, reserve 0.17). Building and checking made no model call.
- The site's own ledger agrees to the cent: 149 model calls, 104 questions.
- **A first attempt cost nothing.** The local server lacked `ASK_VISITOR_SALT`, so the route refused six questions
  before any model call. The runner had counted its reserve for each (USD 1.02); the ledger showed no call, and I
  removed that figure from the spend file by hand, with the evidence written beside it.
- Today's site ledger stands at USD 9.29, the month at 19.40 of 30. Production's ask route was not asked.

## (c) The rerun against session 156 (its figure in brackets)

| | Pass | Seconds to the words, median | Under the target | USD a question |
|---|---|---|---|---|
| About an idea (25; target 2 s) | 25 (25) | 2.4 (2.1) | 4 under 2 s (8) | 0.0103 (0.0102) |
| A chart (25; target 5 s) | 25 (25) | 4.6 (4.6) | 14 under 5 s (16) | 0.0269 (0.0241) |
| One figure (25; target 5 s) | 25 (25) | 4.7 (4.6) | 14 under 5 s (14) | 0.0201 (0.0232) |
| Refused (25) | 25 (25) | 2.5 (2.1) | 21 under 5 s (25) | 0.0110 (0.0103) |
| **The 100** | **100 (100)** | 2.8 (2.45) | | **0.0171 (0.0169)** |
| The 4 asked of the 20 | 4 of 4 | 4.15 | | 0.0181 |

- **Number questions together:** 4.65 seconds (4.6); 28 of 50 under 5 (30); 90th percentile 7.0 (7.8).
- **Cost, like for like:** the first question of a run pays to write the prompt to the cache. That fell on one of
  the 100 here (USD 0.16) and on one of the 20 in session 156. The other 99 cost 0.0156 each (0.0169).
- **Why ideas are slower is not known.** Same answer length; the model's first word came after 1.2 seconds, not 0.7.
  The prompt is about 3,500 characters longer. One asking cannot tell that from the hour of the day.
- **Slowest answer: 16.1 seconds**, daily peak demand over two weeks, written three times (5 seconds in session 156).
- Record: `warehouse/chat/eval_ercot_results_161.csv`. Each question was asked once.

## (b) The two slow shapes

| Question | Session 156 | Now |
|---|---|---|
| Highest hourly demand "this week" | 24.7 s, 10 model calls, USD 0.105 | 6.8 s, 2 calls, USD 0.024 |
| Generation by fuel over the past seven days | 28.6 s, 7 model calls, USD 0.101 | 2.8 s, 1 call, USD 0.016 |

- **"This week" is a form of the query** (`day "this_week"`): one read of the week, Monday to today. The result lists
  each day with its rows and answers for the days held. When no day of the week is held, it answers for the newest
  seven days held and says so.
- **Its answer on the run:** 73,194 MW, "only part of 6 and 7 October is held; 5 and 8 October are not held yet".
- **Generation by fuel is planned by rule**: no reading turn. 17 of the 100 are now planned by rule (16).
- **Its answer on the run** (1 to 7 October, mean MW): gas 31,783, solar 7,945, coal 6,965, wind 6,836, nuclear 4,999.

## (a) The hour-of-day axis

- The shared chart draws an hour axis only when asked for it; every other axis is written as it was.
- **Only Ask ERCOT asks for it.** In a real browser, locally and on production's internal view: 10 of 10 checks.
  One line, 24 points, each the row fetched; hover gives "07:00 ... 1,120.93 MW"; no range slider.
- The two questions it serves pass: batteries across a day 6.3 seconds (5.3), wind across a day 5.9 (4.5).

## The landing and the snapshot

- Pushed 22:45:58 UTC as `task/161-ask-line` (`ffca9ca`): checks passed (run 37855509428), merged as `9f1f4d2`.
  **Vercel: "Deployment has completed"** at 22:53:59 UTC. No freeze (`freeze.py status` exit 0). No force push.
- **Snapshot before** (`161_before`, 22:45:15) **and after** (`161_after`, 22:54:06), 25 addresses: **6 differences,
  all on `/network`, all expected, none of them a checked number** (3,357 keys):
  - "refreshed 2026-10-08 21:05 UTC" became 22:05: the hourly refresh. Expected.
  - "Demand of the seven ISOs: newest hour 19:00 UTC" became 20:00, in two lines. Expected.
  - "Built 21:05 UTC, onto the daily build of 20:05" became 22:05 and 21:05. Expected.
- **The charts, which that snapshot cannot see.** A new script reads each chart's settings and points in a browser
  (`site/scripts/chart-options.mjs`). Before and after: 3 charts, all on `/storage`; **0 differences in settings, 0
  in points.** `/cost-of-power/battery` and `/network` hold no chart of the shared kind. **Nothing was reverted.**
- As a visitor, `/ask/ercot` still answers the in-review page. The workflow removed the task branch.
- This report is on `wip/161-report` and reaches main with the next landing.

## Checks

- On the landed commit, main copy: site build exit 0 (one build at a time); `check-routes` 0 failed;
  `check-values` 7,003 of 7,034 match, 31 latest prices replaced by a newer interval inside 45 minutes.
- The whole suite in a clean copy: 2,505 tests, passed (209 skipped, as on GitHub's runner).
- New: `test-ask-161.mjs` 8 and `tests/test_session161.py` 11, on reads recorded from the live set today.
- Recorded answers in a browser: the Ask panel 13 of 13; words before the chart 9 of 9.
- **Earlier tests changed on purpose:** session 156's "24 rows, 0 points" is now 24 points; its `day` list gains
  `this_week`; session 148's list of planned questions gains h05 (15 becomes 16 without the reserve tables);
  sessions 121 and 137 pinned one line of the panel that now names the group.
- No data lock was taken: nothing was written to a table. No pull. Gates were not piped.

## What is left, exactly

1. 16 of the 20 page questions, not asked this session.
2. Ideas at 2.4 seconds against a target of 2; a second asking would say whether today's 0.3 is noise.
3. Hourly demand for ERCOT has holes in the live set (below). The slowest answer and "this week" both met them.
4. A derived table of generation by fuel by day, if you want one held; "last week" and "this month" are not forms.
5. The Python reference loop has none of the forms of sessions 156 and 161.
6. From session 148's list, still not checked: `ASK_VISITOR_SALT` on production, the provider's spending limit,
   the words on `/terms`.

## Decisions made without you

1. The 100 first, then the 20 until the cap, so the comparison by kind is whole.
2. The six changed questions asked first, so the cap could not leave them out.
3. "The daily rollup" read as one read rolled up by day, since no daily table by fuel is held.
4. "This week" is the calendar week, Monday to today, on Texas's clock.
5. The 24 rows are kept, folded under the line, not removed.
6. A chart check of my own, because the live snapshot reads numbers and words, not charts.

## The five most interesting numbers

1. **104 of 104** pass, for USD 1.78 of 2.00; 16 questions not asked.
2. **28.6 seconds and 7 model calls to 2.8 and 1**: generation by fuel over seven days.
3. **24.7 seconds and 10 model calls to 6.8 and 2**: the highest hourly demand "this week".
4. **0 of 24**: the hours of ERCOT's demand held for 5 October (19, 5 and 19 for 4, 6 and 7 October), read at
   22:17 UTC from the live set.
5. **7,945 MW of solar against 6,836 MW of wind**: ERCOT's mean output, 1 to 7 October, the last day partial.
