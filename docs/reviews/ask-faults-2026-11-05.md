# Ask's faults, read from the sixty's newest run (5 November 2026)

Energy Research Warehouse (ERW), session 2220 (chain 152, `queue/done/152-night-5-november-portable-ask-quality.md`, portable-laptop, unattended). The sixty's newest run is session 1149's asking of 23 October 2026 (`docs/reviews/ask-sixty-2026-10-25.md`): the first set, session 320's thirty (`questions_s320.yaml`, `eval_s1133_s320_run.json`, graded under the hold in `eval_s1133_s320_grades.json`), 19 of 30; the second set, session 1114's thirty (`questions_s1114.yaml`, `eval_s1133_s1114_run.json`), 8 of 8 asked, 22 stopped by the cap. Ask landed on main on 6 November at 00:08 UTC (`task/1314-ask`, merge `efda9bba7`). Nothing here was asked anew: every line below is read from the stored runs and their grades, with no model.

Each fault is put in one of the five classes the chain names: **table** (the wrong table chosen), **aggregation** (the wrong aggregation, period or unit), **hold** (a held table answered, or a public one refused), **unfetched** (a number not fetched), **form** (a form or chart fault). Where the answer is right and the key is wrong, the class says so: the loop is not changed for a key.

## The eleven failures of the first set

Each with its question, the answer given (its figure as written), the answer expected (the key as computed from the live set at 22:49 UTC on 23 October, `eval_s1133_s320_keys.json`, with the key's tolerance) and the class.

1. **b01** (ERCOT's chat). Question: a 4-hour battery at ERCOT's hub average with perfect foresight, total revenue over 2025-10 to 2026-09, in USD per kW. Given: "81,402.19 USD/MW (battery_stack_monthly)", with "I have not converted this to USD per kW". Expected: 81.40 USD per kW (key 81.4022, tolerance 0.01). Class: **aggregation (unit)**. The table holds USD per MW; the tool handed back no per-kW figure (`ASK_PER_KW` off), and the loop, rightly, states no number it did not fetch. Sent back once by the number check, then passed with the per-MW figure.
2. **b02** (ERCOT). Question: the energy part of b01, in USD per kW. Given: "54,598.58 USD per MW from energy alone". Expected: 54.60 USD per kW (54.5986). Class: **aggregation (unit)**, as b01.
3. **b03** (ERCOT). Question: the ancillary part of b01, in USD per kW. Given: "26,803.61 USD/MW from ancillary services". Expected: 26.80 USD per kW (26.8036). Class: **aggregation (unit)**, as b01. The answer adds the monthly low and high (973.63 and 6,653.40 USD/MW), both fetched.
4. **b04** (ERCOT). Question: a 2-hour battery on the day-ahead strategy, total over 2025-10 to 2026-09, in USD per kW. Given: "51,067.14 USD/MW" and the monthly mean 4,255.60 USD/MW. Expected: 51.07 USD per kW (51.0671). Class: **aggregation (unit)**, as b01.
5. **b05** (ERCOT). Question: the 4-hour perfect-foresight battery in calendar year 2021, in USD per kW. Given: "3,430,556.56 USD/MW", February 2021 alone "3,115,947.33 USD/MW". Expected: 3,430.56 USD per kW (3430.5566). Class: **aggregation (unit)**, as b01. Used all 12 tool calls.
6. **b06** (ERCOT). Question: the same battery in calendar year 2025, in USD per kW. Given: "87,439.61 USD/MW". Expected: 87.44 USD per kW (87.4396). Class: **aggregation (unit)**, as b01.
7. **b08** (CAISO's chat). Question: a 4-hour battery at CAISO's SP15 hub with perfect foresight, total over 2025-10 to 2026-09, in USD per kW. Given: "79,308.31 USD per MW". Expected: 79.31 USD per kW (79.3083). Class: **aggregation (unit)**, as b01.
8. **b09** (CAISO). Question: the 4-hour day-ahead battery's energy revenue at SP15 in calendar year 2025, in USD per kW. Given: "42,503.77 USD per MW of energy revenue". Expected: 42.50 USD per kW (42.5038). Class: **aggregation (unit)**, as b01.
9. **g03** (ERCOT). Question: a gas peaker at ERCOT's hub average, margin over fuel in calendar year 2025, USD per MW, the twelve months summed. Given: "about 50,424 USD/MW (merchant_revenue_monthly, peaker_revenue_per_mw)". The tool's sum was 50,424.0741. Expected: 50,424.07 (50424.0741, tolerance 0.01). Class: **form**. The right figure from the right table and aggregation, written rounded to the unit against a key to the cent; the number check lets a coarser precision through. The record also shows the same sum asked six times over (the last five identical calls), so the answer used 11 of 12 calls.
10. **g06** (SPP's chat). Question: wind at SPP's North hub in calendar year 2025, the twelve monthly revenues per MW summed, in USD. Given: "about 66,963 USD per MW", with the monthly low and high (3,943 and 8,182 USD/MW, each rounded to the unit from the tool's rows). The tool's sum was 66,963.0112. Expected: 66,963.01 (66963.0112, tolerance 0.01). Class: **form**, as g03. The same sum was asked seven times over; all 12 calls used.
11. **d10** (the general chat). Question: the load-weighted real-time price at PJM's Western hub in August 2026, in USD per MWh. Given: "Not in the warehouse. It holds no PJM energy prices, day-ahead or real-time, and no PJM Western hub series", no figure, citing `ba_supply_monthly` (a count it read: zero rows for `pjm:WESTERN_HUB`). Expected: a refusal with "not in the warehouse" and no figure (`refuse: true`, `expected: []`), and the key also asks that `cost_of_power_monthly` be cited. Class: **none of the loop's; the key's**. PJM's prices are licensed for internal use and the live set holds none, so the refusal is right; the key grades a refusal on a cited table, which a right refusal need not cite (session 320's open ruling 3). Under the five classes it is nearest **hold** (a licensed source's question rightly refused, graded as if a public figure were expected).

The nineteen right: b07, b10, g01, g02, g04, g05, g07 to g10, d01 to d09. g07, g08, d05 and d07 are held grids (ISO-NE, NYISO) answered with the hold's words and the public grids' figures; g10 is MISO refused with the pause's words.

## The ten classed refusals

`docs/reviews/ask-refusals.md` (written by `refusals.py` from the tool records) lists ten refusals across the stored runs: three MISO's pause, seven the warehouse lacking the figure. Each read the same way.

12. **Session 267, q30**: the average real-time price at ERCOT's HB_HUBAVG over calendar year 2012. Given: "Not in the warehouse. ERCOT hub prices in the warehouse start on 2015-01-01 (ercot_all_hub_prices_history, ercot_hub_prices_daily)", no figure. Expected: a refusal. Class: the warehouse lacks the figure; **no fault**.
13. **Session 302, q26**: the average day-ahead price at PJM's Western Hub in 2025. Given: "Not in the warehouse. It holds no PJM day-ahead or real-time energy prices", no figure; five calls, three of them the same `grid_notes` read of `docs/grids/pjm.md`. Expected: a refusal. Class: lacks (PJM's prices licensed internal); **no fault** of the answer; the three identical reads are a **form** fault of the loop (repeated calls), as in g03 and g06.
14. **Session 302, q27**: the real-time price at ERCOT's HB_HUBAVG in July 2027. Given: "Not in the warehouse: it holds what happened, not forecasts", no figure, no tool call. Expected: a refusal. **No fault**.
15. **Session 302, q28**: ERCOT's peak demand in August 2010. Given: "Not in the warehouse. The warehouse holds no ERCOT demand data for August 2010", no figure. Expected: a refusal. **No fault**: one `list_tables` call, whose rows carry each table's first time, so "begin much later" rests on a result.
16. **Session 302, q29**: the load-weighted real-time price at MISO's Indiana hub in August 2026. Given: "Not in the warehouse. MISO data is paused while its terms are reviewed (since 4 October 2026)", no figure. Expected: a refusal with the pause's words. Class: MISO's pause; **no fault**.
17. **Session 302, q30**: electric vehicles registered in Texas in 2025. Given: "Not in the warehouse. It has no table of electric vehicle registrations", no figure. Expected: a refusal. **No fault**.
18. **Session 1113, g10**: the solar capture price at MISO's Indiana hub in July 2026. Given: "Not in the warehouse: MISO is paused while terms are reviewed (since 4 October 2026)", no figure, `merchant_revenue_monthly` named as the table that would hold it; nine calls, the last four the same count query, each answered with the pause. Expected: the pause's refusal. Class: MISO's pause; **no fault** of the answer; the repeated calls a **form** fault of the loop.
19. **Session 1113, d10**: as item 11, asked on 23 October at 19:29 UTC. Given: "Not in the warehouse. It holds no PJM energy prices", no figure, nothing cited, one call. Expected: as item 11. Class: **the key's**, as item 11.
20. **Session 1149, g10**: as item 18, asked again. Given: the pause's refusal, no figure; 12 calls, the last five the same count query. Class: MISO's pause; **no fault** of the answer; the repeated calls a **form** fault of the loop.
21. **Session 1149, d10**: item 11.

## By class

| Class | Items | Count |
|---|---|---|
| aggregation (unit: USD per kW asked of a table in USD per MW) | 1 to 8 | 8 |
| form (a figure of five digits or more written rounded to the unit against a key to the cent) | 9, 10 | 2 |
| the key's, not the loop's (a right refusal graded on a cited table) | 11, 19, 21 | 1 of the thirty (3 records) |
| no fault (a right refusal) | 12 to 18, 20 | 8 records |
| form, found on the way (the same tool call repeated with the same arguments, up to seven times, spending the limit of 12) | 9, 10, 13, 18, 20 | 5 records |

No failure is of the classes **table** or **hold** proper: every wrong answer read the table its key names, and no held table was answered nor a public figure refused. The eleven are session 320's three open rulings (`docs/reviews/ask-board-rulings-2026-10-23.md`, items 1 to 3), unmoved since 20 October.

## What the chain does with them (sessions 2221 to 2223)

One class a session, in order of count, in the code both loops share, each fix with a scripted test in both loops, never by adding a number the loop did not fetch:

- **2221, the unit (8)**: the query tool hands back the per-kW figure beside the per-MW one for a table whose method note states the conversion (`battery_stack_monthly`: `value_usd_per_kw`, prepared behind `ASK_PER_KW` in session 1109), on by default in both loops, so a per-kW answer is a fetched number; the prompt says the per-kW key is there to use.
- **2222, the form (2)**: a figure is written as the tool returned it, to the cent for money, not rounded to the unit; and the loop refuses to repeat a tool call whose arguments equal one already made in the turn, handing the earlier result back without spending a call.
- **2223, the key (1)**: a refusal is graded on refusing and stating no figure, not on a cited table (ruling 3's recommendation), in the grader both runs use; and the keys of the second set that name one table among several holding the figure accept every table that holds it.

## The second set

Its newest run asked t01 to t08 (8 of 8); t09 to p10 stand unasked since the cap of 23 October. Their last grading (23 October, `eval_s1114_grades.json`) was 24 of 30, four of the six wrong being the right figure read from another table that holds it (t06, t09, f05, f07: ruling 3). Session 2223's grading change reaches them; the twenty-two are asked again when a session's cap allows.

## The count after each session

| Session | The thirty | Note |
|---|---|---|
| before (23 October 2026) | 19 of 30 | 15 on the figure keys alone; 30 if the three rulings went the answers' way |
| 2221 (6 November 2026, 01:19 to 01:31 UTC) | **26 of 30** | the Python loop (`eval_loop.py`, `eval_s2221_loop_run.json`, graded under the hold in `eval_s2221_loop_grades.json`; 22 on the figure keys alone), USD 2.49, Sonnet 5.5, 30 of 30 asked under the cap of USD 3. All eight per-kW questions right (b01 to b06, b08, b09: the answer states the tool's `value_usd_per_kw`). Still wrong: g03 and g06 ("50,424" and "66,963", rounded to the unit against a key to the cent) and g09, right on 23 October to the cent and now "about 58,534" (the form class, session 2222); d10 (the key's, session 2223). Repeated identical calls still spend the limit (b03, b04, b05, b07, b09, g06, g10 at 12): session 2222. |
| 2222 (6 November 2026, 01:38 to 01:49 UTC) | **29 of 30** | the Python loop (`eval_s2222_loop_run.json`, graded under the hold in `eval_s2222_loop_grades.json`; 25 on the figure keys alone), USD 1.96, Sonnet 5.5, 30 of 30 asked. The form class fixed: g03, g06 and g09 write the sum to the cent (50,424.07; 66,963.01; 58,533.70). A repeated call is counted and not read: 12 answers repeated one call each, none more; 155 tool calls in all against 2221's 205, median 5 against 6, two answers at 12 (g03, d04), none sent back. Still wrong: d10 (the key's, session 2223). |
| 2223 (6 November 2026, 01:47 to 01:59 UTC) | **30 of 30** | the Python loop (`eval_s2223_loop_run.json`, graded under the hold and under the grader's two rules of this session in `eval_s2223_loop_grades.json`; 26 on the figure keys alone), USD 2.31, Sonnet 5.5, 30 of 30 asked. The key class fixed in the grader (`eval_s267.py` `RULES_2223`, session 320's ruling 3 as recommended): d10's refusal is graded on refusing and stating no figure. 185 tool calls, median 6, three at 12 (b03, b08, g04), 13 repeats counted and not read, none sent back. The second set's stored answers of 23 October regraded under the same rules: 29 of 30 (`eval_s2223_regrade_s1114_grades.json`; f08 read the wrong variable, before rule 9 of session 1142), from 24. |
| 2224 (6 November 2026, 02:05 to 02:25 UTC), the twenty | **20 of 20** (the thirty untouched: 30 of 30) | the third set, `questions_s2224.yaml` (`scripts/ask_eval/lab_questions.py`), through the Python loop (`eval_s2224_loop_s2224_run.json`, graded under the hold and the grader's rules in `eval_s2224_loop_s2224_grades.json`), USD 2.60 over 26 askings, Sonnet 5.5. The first asking (02:05 to 02:14): 15 of 20 on the keys as first written. Its faults: l17 and l18, review tables (`grid_peak_vs_capacity`, `node_basis_summary`) the Python loop could not read (the package's live backend listed the published tables alone) where the site reads them: fixed (`ERW_LIVE_REVIEW=on`, set by the chat's tools), l18 right at the second asking; l15 and l16, keys on a month the table held in part (October 2026: 48 of 744 day-ahead hours): the keys moved to September 2026, checked whole, both right; l03, the datacenter tracker asked in ERCOT's chat, which cannot see the tracker's tables, so no hold words: asked through the general chat, right; l08, ISO-NE's queue, a table held by grid: the loop's answer (the hold's words, no figure) was right and the key wrong, so the key is the hold's and the script now refuses to write a figure key for a held table; l17, the reserve margin, asked in ERCOT's chat, which does not see a table whose entities are `grid_peak_vs_capacity:ercot`: asked through the general chat, right. Four of the five held-table questions were answered with "license needed" and no figure at the first asking; MISO's queue with the pause's words; the question outside the warehouse with "not in the warehouse". |

## The state of every row (session 5201, chain 235, 13 November 2026)

Written by session 5201 from the stored runs, the grades and the tests on `origin/main` at `a57b7079`, with no model. No row is open. `tests/test_session5201_ask.py` holds this table: every item has a state, and every test it names exists.

| Row | Class | State | Held by |
|---|---|---|---|
| 1 to 8 (b01 to b06, b08, b09) | aggregation (unit) | fixed: session 2221, `value_usd_per_kw` beside the per-MW figure, rule 10 | `tests/test_session2221_ask.py`; the scenario `a_per_kw_question` of `tests/test_session1300.py`, both loops |
| 9, 10 (g03, g06; g09 found by 2221) | form (rounded to the unit) | fixed: session 2222, rule 1 writes a money figure to the cent | `tests/test_session5201_ask.py` `TheFormClass` (the rule's words in both loops; the three sums to the cent in the four askings since) |
| 9, 10, 13, 18, 20 (the same call repeated) | form (found on the way) | fixed: session 2222, a repeated call is counted and not read | the scenario `a_repeated_call` of `tests/test_session1300.py`, both loops |
| 11, 19, 21 (d10) | the key's | the key's, fixed in the grader: session 2223, the rule `refusal_no_table` | `tests/test_session2223_ask.py` |
| 12, 14, 15, 16, 17 | none | no fault: a right refusal | `docs/reviews/ask-refusals.md`, held by its test |
| 13, 18, 20 (the answers) | none | no fault: a right refusal (their repeated calls are the row above) | as above |
| second set, t06, f05, f06, f07 (23 October) | the key's | the key's, fixed in the grader: session 2223, the rule `table_by_evidence` | `tests/test_session2223_ask.py` |
| f08 (23 October) | table (the wrong variable read) | fixed: rule 9 of session 1142; right in the newest asking | `tests/test_session5201_ask.py` `TheSecondThirty` (the newest asking 30 of 30) |
| t09 (the newest asking) | the key's | the key's, fixed in the grader: the answer is right (May 2025, 5.64 USD per MW per hour) from `ercot_as_prices`, the hourly source, where the key names `ercot_as_prices_monthly`; met by `table_by_evidence`. The stored grading was made with no rules | `tests/test_session5201_ask.py` `TheSecondThirty.test_t09_is_met_by_the_2223_rule` |
| f09 (the newest asking) | the key's | the key's, fixed in the grader: the three figures are right to the cent, and the difference is written "3,369.62 USD/MW less at ERCOT" where the key holds -3369.6241. A new rule, `sign_in_words` (`eval_s267.py` `RULES_5201`): a negative expected figure is met by its magnitude when its own sentence holds a word of the direction | `tests/test_session5201_ask.py` `TheRule`, `TheSecondThirty.test_f09_is_met_by_the_new_rule`, `NothingElseMoves` |

The second thirty's newest asking (`eval_s1133_s1114_run.json`, t01 to t08 on 23 October, t09 to p10 on 6 November) regraded under `RULES_5201`: **30 of 30** (`eval_s5201_regrade_s1133_grades.json`), from 28 as stored and 29 under the 2223 rules. Over the five stored sets that carry their keys in a set file, f09 is the only answer the new rule turns, and no answer right before is wrong after. `eval_loop.py` grades under `RULES_5201` from this session on (`--rules 2223` for the old way).

What the rule does not settle: t09's answer read 744 hourly rows where a monthly table holds the figure in 12. That is the table choice class, measured on the widened set (`docs/reviews/ask-eval-2026-11-13.md`), not tuned here to one question.
