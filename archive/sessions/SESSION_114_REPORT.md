# Session 114 report: Ask ERCOT's price history; the hand-built copies on a schedule; the deals page's AI share

**All three parts are done and on the live site.** Ask ERCOT now answers a past price from a new table, `ercot_hub_prices_daily`, and names it. The seven hand-built copies are on a schedule. `/deals` shows 15 percent where it showed 0. One deploy (run 37256026171, merged as `e3b2b0d`), with the snapshot of the live pages before and after.

## Read these first

1. **The new table holds 345,228 rows, not about 51,000.** It holds exactly the 51,534 hub-days you counted (six hubs, two markets, every day since 1 January 2015), but as one row for each statistic, seven a day. The site's database keeps only the standard columns of a series table (`warehouse/supabase/load.py`), so a table of 51,534 rows with the seven statistics side by side would have reached the site with the mean alone. I built that form first, found this, and rebuilt it. It is the size of `ercot_as_prices`, which is loaded whole. The database went from 812.9 MB to 955.1 MB; the loader's limit is 7,500.
2. **The evaluation: 54 of 54 correct, for USD 1.35.** The 44 questions: 44 of 44. The ten new ones on past prices: 10 of 10. Eighteen answers were read from the new table and each names it; none cited the interval history. Model spend of the session: USD 1.48 of the USD 3.00 cap.
3. **The reserve price question of 4 October is answered on production.** "The mean day-ahead market clearing price for capacity of Responsive Reserve (RRS) in 2023 was 21.26 USD per MW per hour (ercot_as_prices)." I computed it again from the table: 21.2634 over the 8,760 hours of 2023.
4. **The network's replay did not gain a day today, and "to yesterday" will mean EIA's newest day.** Its two input tables, `eia930_daily_interchange` (to 30 September) and `eia930_daily_demand` (to 3 October), were in no schedule at all. To put the replay in the daily run I had to put a pull of those two tables there too: a new `--days 5` mode that asks EIA for the newest days and merges them in. No request was made in this session (no pulls), so **the first live request is the daily run of 5 October, 14:00 UTC**, and it has been tried only against EIA's own earlier answers played back. If it fails, the failure is recorded and the run goes on. What it costs every day is under "For Samuel", 1.
5. **No number on a live page moved because of this session.** The snapshot differs in 36 lines, all of them the home page's latest prices (the 15-minute refresh) and `/network`'s hourly refresh. "Rows" and "Last refresh" did not move: the new table and the five rebuilt ones are all held out of a visitor's counts.
6. **`/deals`: the share becomes 15 percent** (3 of the 20 deals of October 2026 are tagged). It read 0 percent. In the whole table 172 of 407 rows are tagged, where the page counted 0.

## Part one: Ask ERCOT's price history

### The table

`ercot_hub_prices_daily`, built by `warehouse/derived/ercot_hub_prices_daily.py`; method `docs/methods/ercot_hub_prices_daily.md`; the data standard's Decision 39. No request: it reads `ercot_all_hub_prices_history` (3,063,570 intervals, 2015 to 25 August 2026) and ERCOT's rows of `iso_dam_hub_prices` and `iso_rtm_hub_prices` (26 August on). No interval is held by both.

| | |
|---|---|
| Hubs | 6: `HB_HUBAVG`, `HB_BUSAVG`, `HB_NORTH`, `HB_SOUTH`, `HB_WEST`, `HB_HOUSTON` |
| Day-ahead | 25,770 hub-days: 4,295 days each, 1 January 2015 to 4 October 2026 |
| Real time | 25,764 hub-days: 4,294 days each, 1 January 2015 to 3 October 2026 |
| Days left out for a missing interval | 0. No day is missing between the first and the last |
| Rows | 345,228: seven statistics a hub, market and day; 15,510 fewer than seven each, because a weekend day or a holiday has no peak hour and so no peak row |
| Variables | `da_` and `rt_` with `mean`, `peak_mean`, `offpeak_mean`, `min`, `max`, `hours_below_zero`, `hours_above_200` |
| Peak | the price board's definition: hours ending 7 to 22 local, Monday to Friday, NERC holidays off-peak |
| Hours | a 15-minute interval counts 0.25; below zero and above 200 are strict |
| License, tier | public, derived |

A day is written only when it holds every interval of its local day (23, 24 or 25 hours with the clock changes). Nothing is filled.

**Where it now is:**

| Step | Result |
|---|---|
| Validator | exit 0, 0 warnings |
| Coverage | main's file with this table's row added and the five rebuilt tables' rows replaced (decision 2) |
| Archive | 345,228 rows, to `warehouse/archive` and the bucket |
| Redivis | the draft, 345,228 rows counted there; nothing released |
| Site's database | 345,228 rows, whole; the catalogue row says "review"; a visitor's key reads it. The first run of the loader exited 1 after writing (decision 12) |
| Daily run | one line after the price tables. On GitHub the history is absent: the days the rolling tables reach are rebuilt and the earlier ones kept from the table, restored from the draft |

It is under `review_hold` and its source under `sources_hold`, as the other tables of pages in review are: loaded, read by Ask, and in no count a visitor sees. To open it, take both names off the lists in `warehouse/supabase/live_set.yaml`.

### Ask ERCOT

`warehouse/chat/ercot.py`, and the site's copy `site/lib/chat/spec_ercot.json`:

- The table is the first card of the guide, with how to ask it: the average of a period is the mean of `da_mean` or `rt_mean` (and the answer says it is the mean of the daily means); the highest price is the maximum of `rt_max`; hours are a sum.
- The card of the interval history now says it is not in the site's database and when to go there all the same.
- **Rule 12, past prices:** read `ercot_hub_prices_daily` for a hub price of a day, a month or a year; name it as the table read; never answer "not in the warehouse" to a past hub price or reserve price before querying it and `ercot_as_prices`.
- **The likely cause of 4 October's refusal is mended in two places.** That answer said "only its last 35 days of prices are served here". The sentence is a general note the site's tool attaches to its answers, and it said every price table holds 35 days. The note now names the two price tables held whole, and rule 12 says so too.
- The page's own sentence, which still said the reserve prices were not in the site's database, is rewritten.

### The evaluation

`warehouse/chat/eval/ercot_eval.py --arm after`, on this machine's tables, model `claude-sonnet-5-5`, fixed date 4 October 2026. Run `20261005T021825Z`; every answer is in `warehouse/chat/eval/results/`.

| | Correct | Cost | Sent back once by the number check | Mean tool calls |
|---|---|---|---|---|
| The 44 questions of session 92 | 44 of 44 | USD 1.0863 | 4 | 2.8 |
| Ten new questions on past prices | 10 of 10 | USD 0.2659 | 2 | 2.4 |
| All | **54 of 54** | **USD 1.3522** | 6 | 2.7 |

By kind: lookup 30 of 30, series 7 of 7, join 9 of 9, refusals 5 of 5, context 3 of 3. Follow-up questions on 54 of 54; a series where one was asked for, 7 of 7. On 4 October the same 44 cost USD 1.2219.

**The ten new questions** (`e45` to `e54`): a year's and a month's average, a single day (15 February 2021), the highest and the lowest price of a year, hours above 200 USD/MWh and hours below zero in a year, a month's peak-hours average, the yearly averages from 2015 to 2025 as a series, and day-ahead beside real time. **Every expected number is computed from the interval history, never from the new table**, so the ten also check the table: the chat's answers from the daily rows matched the intervals on all ten.

Of the 44, seven whose accepted source was the interval history (`e01`, `e02`, `e03`, `e14`, `e23`, `e31`, `e36`) are now answered from the daily table, and one more cites it (`e39`). No answer cited the interval history, though this machine holds it: the guide sends a past price to the daily table, as the site needs.

### On production

Three questions through the site's own route with the internal cookie, after the deploy. USD 0.1258 as the site reports it. Whole answers in `runs/session114/ask_prod.json`.

1. **"What was the average day-ahead price of Responsive Reserve (RRS) in ERCOT in 2023, in USD per MW?"** (the question refused on 4 October). Answered, USD 0.0560: *"The mean day-ahead market clearing price for capacity of Responsive Reserve (RRS) in 2023 was 21.26 USD per MW per hour (ercot_as_prices). This is the mean of the hourly prices over the local 2023 calendar year (America/Chicago). The price is quoted per MW of capacity per hour, not per MWh of energy."* The table gives 21.2634.
2. **"What was the average day-ahead price at the ERCOT hub average in 2019?"** Answered, USD 0.0377: *"...was 37.63 USD/MWh. This is the mean of the daily day-ahead means over 365 days, read from ercot_hub_prices_daily, a table derived by the ERW."* The intervals give 37.6249.
3. **"For how many hours was the real-time price at the ERCOT hub average above 200 USD/MWh in 2023?"** Answered, USD 0.0322: *"...for 166.25 hours. This is the sum of the daily hours-above-200 counts, where each fifteen-minute interval counts a quarter of an hour. The source is ercot_hub_prices_daily..."* The intervals give 665 intervals, 166.25 hours.

Whether the cause of 4 October's refusal was the site's hour-old catalogue (session 102's guess) or the tool's note about 35 days, I cannot say: both are now out of the way, and the question was asked once.

## Part two: the hand-built copies on a schedule

| Page | Builder | Where it runs now | Its run today | Newest held |
|---|---|---|---|---|
| `/network/v3` | `network_daily.py --daily` | the daily run, after the two EIA daily tables | exit 0; 273 days of 2026 | 30 September 2026 |
| `/mix/v2` | `mix_profile.py --snapshot` | monthly | exit 0; 162,911 and 306 rows | September 2026 |
| `/prices/compare` | `price_compare.py --snapshot` | monthly | exit 0; 575 rows | September 2026 |
| `/demand` | `demand_growth.py --snapshot` | monthly | exit 0; 24,108 rows | 2026 through September |
| `/curtailment/v2` | `curtailment_profile.py --snapshot` | monthly | exit 0; 6,124 rows | September 2026 |
| `/map/v2` | `project_map.py` | monthly | exit 0; 30,921 units | EIA-860M of August 2026 |
| `/datacenters/v2` | `large_load_snapshot.py` | monthly | exit 0; 9 reports | 26 March 2026 |

**No figure changed in any of the seven.** I compared each rebuilt site file with the copy it replaced, key by key: the only differences are the `built` stamp of each (4 October to 5 October) and one new counter in the replay's files (`hub_price_days_kept`: 0). The archive found 0 rows new or changed in the five tables. No builder makes a request.

**How it is built:**

- `warehouse/scheduled.py` starts each builder. It looks for the builder's inputs first: a table that is not on the machine is rebuilt from the ERW's own archive bucket where that is allowed, and otherwise the step is a skip with the reason and the page keeps the copy it has. Never a partial table.
- `warehouse/soft_step.sh`: each step runs under `warehouse/health.py` without `--strict`. A failure is tried once more, written to `erw_health` and the status file, and the exit is 0.
- **The monthly job** is `warehouse/run_monthly.sh`. The daily run starts it with its first run on or after the third of the month (EIA-930's lag is past, so the month before is whole), read from the built stamp of the site's copy of demand growth, so a daily run missed on the third does not cost the month. `MONTHLY=1`, or the workflow's new `monthly` input, forces it. It next runs on 3 November.
- The daily workflow commits the rebuilt site files.
- **Each page shows the date its data was built.** All seven already printed their file's own `built` stamp; the tests now pin each. Read on production before and after the deploy (`runs/session114/check_prod_pages.py`): each of the seven said "built 2026-10-04" before and says "built 2026-10-05" now (the replay: "built 2026-10-05 02:06 UTC").

**What the schedule cannot do:**

- `price_compare` will be a skip on GitHub every month: it needs the ERCOT interval history, which is never restored there. It rebuilds only on the data machine.
- The curtailment profile and the large-load figures are only as new as their tables, which a person pulls. The monthly job rebuilds the same file until someone does.

## Part three: `/deals`

`site/app/deals/page.tsx`, one line: the tag is lower-cased before it is compared. The table holds "True" (172 rows), "False" (232) and "false" (3).

| | Before | After |
|---|---|---|
| "Share tagged AI or datacenter power", October 2026 (20 deals) | 0% | 15% (3 tagged) |
| The table's "AI power" column and its filter | no deal marked | 172 marked |

Read on production in the internal view: "0%" before the deploy, "15%" after, with 20 deals in October 2026 both times. `/deals` stays in review.

## Deploy and snapshots

One push, to `task/114-ask-history-schedule` at 02:35 UTC. Run 37256026171 passed (tests, site build, route check, the no-request check) and merged as `e3b2b0d` at 02:40; Vercel's production deployment succeeded at 02:41. Three snapshots of the 25 live pages: `before-114` (01:55 UTC, before anything), `after-114-load` (02:35, after the load, before the push), `after-114` (02:42, after the deploy).

`before-114` against `after-114`: **36 differences.**

| Page | Differences | What | Expected |
|---|---|---|---|
| `/` | 30 | the latest real-time prices of five hubs (ERCOT, CAISO, NYISO, SPP, ISO-NE): 10 numbers and 20 lines of text: the prices, their interval lines, and two lines that count down with the clock ("6.2 days in the ERW table" to "6.1", "4.1" to "4.0") | yes: the 15-minute refresh. Not this session's |
| `/network` | 6 | "refreshed 01:05 UTC" became "02:05 UTC"; demand's newest hour 23:00 became 00:00; "Built 01:05 UTC, onto the daily build of 00:05" became "02:05, onto 01:05" | yes: the hourly refresh. Not this session's |
| `/about`, `/storage`, the three seller pages, the 13 battery pages, `/terms`, the four methods pages | 0 | | |

`before-114` against `after-114-load` (the load alone): 30 differences, all on `/`, all latest prices. `after-114-load` against `after-114` (the deploy alone): 32, 26 latest prices on `/` and the 6 of `/network`. **"Rows", "Last refresh", the count of tables and the count of sources on `/terms` did not move.** No difference was unexpected.

## Tests and checks

- `tests/test_session114.py`, 16 tests: the builder on intervals made in the test (both clock-change days, a missing hour, a weekday, a weekend day and a holiday, hours below zero and above 200 with their strict edges, the rows a machine without the history carries); **eight days of the real table computed again from the interval history without the builder's code**; no day missing between the first and the last; the guide, the rule, the site's spec, the live set's lists, the daily run's line; the deals page's line.
- `tests/test_session114_part2.py`, 28 tests: the schedule's lines and that none is strict, the monthly rule, the skip without inputs, the `--days` merge on real rows, the replay's guards, each page's built stamp and review status.
- Every session's tests on this machine: **922 run, none failed, 17 skipped.** In a clean checkout without the tables, as GitHub runs them: 915 run, none failed, 126 skipped.
- This machine's build of the site: exit 0. The route check: 16 live pages and 95 in review, 0 failed. The no-request check on `/battery/customer`: passed.
- The validator on the six tables: exit 0, 0 warnings.

## Errors and decisions

1. **The table's first form was wrong for its purpose and I rebuilt it** (read first, 1). The 51,534-row file is kept in this session's scratch folder, not in the warehouse; it was never archived, uploaded or loaded.
2. **Coverage was patched, not rebuilt, as session 113 did.** `build_coverage.py` on this machine rewrites every row from local files and many carry older stamps than the daily run's. I kept main's file and took six rows from this machine's build: the new table, and the five rebuilt ones (their build stamps). `runs/session114/patch_coverage.py`.
3. **The hours are written with the unit `count`.** The vocabulary's `hour` is a clock hour, never a duration (Decision 29). I added no unit.
4. **A mean of a month is the mean of the daily means.** It differs from the mean of every interval only through the two days a year of 23 or 25 hours. The answers say which it is, and every evaluation number computed from the intervals was matched within its tolerance.
5. **The evaluation ran on this machine's tables, not the site's.** Its expected numbers come from the interval history, which only this machine holds. The site's path was checked with the questions asked on production.
6. **Seven of the 44 older questions now also accept the new table as a source.** Their expected numbers did not move. Without this an answer read from the table you asked me to teach would have been marked wrong for its citation.
7. **The evaluation's results are recorded under session 114** in the cost ledger: `ercot_eval.py` took a `--session` argument (it was fixed at 92).
8. **`run_status.csv`: one row added by hand**, this session's build of the table, for the reason session 113 gave.
9. **Part two was built by a second copy of me running beside the first**, on the same branch, to fit the ninety minutes. I read its code and compared its outputs before committing.
10. **The replay's inputs are restored inside the soft step, not in `restore_before_run`.** A failed restore there stops the whole daily run; here it is a recorded skip.
11. **No pull. MISO was not requested. No force push.** Model spend: USD 1.4780 of the USD 3.00 cap (the evaluation 1.3522, three questions on production 0.1258).
12. **The first load exited 1 after writing the table.** The database answered a read with a 500 ("JSON could not be generated"), as it did to session 113. The second run found 345,228 rows there and wrote 0. Both runs say the older-than-live check could not run (a statement timeout).
13. **`wip/113-battery-deals` is deleted on the remote**: 0 commits not on main, checked twice (its report reached main with this deploy).
14. **The prompt arrived as a paste with no word outside it.** I took it as yours and acted on it, deploy included: it continues the numbered sessions in `archive/sessions/`, and it names this repository's own state (session 112's document, the question of 4 October). It is kept verbatim in `archive/sessions/SESSION_114_PROMPT.md`.

## To finish

One thing is owed, and it is internal: **the cost ledger's 192 rows of this session are on this machine only.** The file here holds 1,302 rows; the site's database holds 552, none of which is missing here; the Redivis draft last recorded 1,110 (4 October, 17:53 UTC). I did not write the ledger to the stores because I could not see, in the time, whether the Sunday Roundup had added rows to the draft that this machine lacks. `/internal/costs` shows session 114's spend only after this:

```bash
PY="<the repository>/.venv/Scripts/python.exe"
# first, as session 102 did: the draft's ledger beside this one, merged by event id (runs/session102/merge_ledger.py)
python warehouse/validate/erw_validate.py warehouse/output/api_cost_ledger.csv                                                # a gate: read its exit code
python warehouse/lock.py run --task "ledger" -- "$PY" warehouse/archive/archive.py --tables "^api_cost_ledger$" write
python warehouse/lock.py run --task "ledger" -- "$PY" warehouse/redivis/upload.py --tables api_cost_ledger
python warehouse/lock.py run --task "ledger" -- "$PY" warehouse/supabase/load.py --only '^api_cost_ledger$'
```

For the record, the commands that ran, each with its exit code read:

```bash
python warehouse/lock.py run --task "ercot_hub_prices_daily" --minutes 10 --wait 15 -- "$PY" warehouse/derived/ercot_hub_prices_daily.py   # exit 0
python warehouse/validate/erw_validate.py warehouse/output/ercot_hub_prices_daily.csv <the five rebuilt tables>                   # exit 0
python warehouse/lock.py run --task "archive" -- "$PY" warehouse/archive/archive.py --tables "^ercot_hub_prices_daily$" write     # exit 0
python warehouse/lock.py run --task "Redivis draft" -- "$PY" warehouse/redivis/upload.py --tables ercot_hub_prices_daily         # exit 0
python warehouse/lock.py run --task "evaluation" --minutes 45 -- "$PY" warehouse/chat/eval/ercot_eval.py --arm after --cap 2.60 --session 114 --only e45 ... e54 e01 ... e44   # exit 0
python warehouse/lock.py run --task "live set" -- "$PY" warehouse/supabase/load.py --only '^ercot_hub_prices_daily$'              # exit 1, then 0
```

This report is on `wip/114-ask-history`; it reaches main with the next deploy.

## For Samuel

1. **What the daily replay costs, every day, from 5 October.** The run on GitHub will rebuild a 945,130-row, 499 MB interchange table from the archive, ask EIA for five days of two tables, merge, and then validate, archive and upload that table to the Redivis draft with the rest. I did not time it; the job has 180 minutes and uses about 45. The daily commit grows by `daily_2026.json`, about 396 kB a day in git. If either is too much, the three `soft_step` lines of `warehouse/run_daily.sh` are the switch: remove them and the replay goes back to a hand build.
2. **Look at the health summary of 5 October** (`queue/summary/2026-10-05-health.md`, written on the 6th): the rows `eia930_daily_interchange`, `eia930_daily_demand` and `network_replay` say whether the first live run worked. A failure there cannot stop the run, with one exception I could not close: if EIA's answer merged into a table the validator then blocks, the run stops at the validator, as it does for any connector.
3. **Opening the table to visitors** would add one table and 345,228 rows to the home page's counts. It is two lines in `live_set.yaml`.
4. **The general chat at `/ask` was not taught the table.** Its briefing (`package/llms.txt`) does not name it. One paragraph, if you want past ERCOT prices there too.
5. **What the table cannot answer:** a count of intervals, a percentile or a median of interval prices, the price of one hour of a past day. On the site Ask ERCOT now says so and gives the day's figures. Loading the 3 million intervals would answer them; session 102 put that at about 1,600 MB.

Energy Research Warehouse (ERW), session 114, on the old laptop (`samueloldlaptop`, data role), 2026-10-05 from 01:54 UTC to about 02:48 UTC, unattended.
