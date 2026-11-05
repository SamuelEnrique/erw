# Ask's thirty questions, graded again offline (21 October 2026)

Energy Research Warehouse (ERW), session 539 (chain 024, the code machine, unattended). No model call of any kind: the 30 answers are the ones session 320's run wrote on 20 October 2026 between 04:21 and 04:36 UTC (`warehouse/chat/eval/eval_s320_first_run.json`), graded again with session 267's grader (`warehouse/chat/eval/eval_s267.py`) against two sets of keys: the keys of 19 October (`warehouse/chat/eval/questions_s320.yaml`, unchanged) and the keys as the live set holds them at 19:35 UTC on 21 October (`warehouse/chat/eval/eval_s539_keys.json`, read with the anon key by `warehouse/chat/eval/regrade_s539.py --keys`). The grades are in `warehouse/chat/eval/eval_s539_regrade.json`; `python warehouse/chat/eval/regrade_s539.py` writes them again from the files alone.

## The result

| | Right |
|---|---|
| The stored answers on the keys of 19 October | 17 of 30 (as session 320 graded them) |
| The stored answers on the keys now | 17 of 30 |
| On the keys now, under the license hold in force since 21 October (four keys become refusals) | 14 of 30 |
| On the keys now, if the three open rulings of session 320 went the answers' way (informative; nothing is ruled) | 30 of 30 |

**Which keys moved.** Two numbers: b08 (79.046 to 79.3083 USD per kW) and b09 (42.3137 to 42.5038 USD per kW), both CAISO SP15 battery sums. `battery_stack_monthly` was run again at 01:04 UTC on 20 October, after the keys were computed (19 October) and before the questions were asked, so these two keys were already stale at the asking: the answers' USD per MW figures (79,308.31 and 42,503.77) are the table now to the cent. The other 26 numeric keys are unchanged within their tolerance, b07's and d08's months (May 2025) included.

**Which keys moved to a refusal.** Since 00:00 UTC on 21 October `merchant_revenue_monthly` and `cost_of_power_monthly` are "license needed" for the rows of ISO-NE, MISO and NYISO (`site/data/license_status.json`; Ask's tools leave a held grid's rows out, `site/lib/chat/tools.ts`). Four questions read such rows: g07 (ISO-NE), g08 (NYISO), d05 (NYISO), d07 (ISO-NE). The live set still holds their figures (the anon reads returned them unchanged), but asked today Ask should answer "license needed" and state no figure. Three of them (g07, d05, d07) were right on 20 October; they are not wrong answers, their key moved after the asking.

## What the stored transcript holds

The run did not record the tool calls (`trace` is null on every answer: `ASK_RECORD_TOOLS` was not set). What there is: each answer, its citations, its count of tool calls and whether it was retried; and the local server's log of the run (`runs/chain_oct19/s320/server.out`, not in git), which holds the number check's findings on every first draft that failed it. Twelve first drafts failed: the eight per-kW questions each with an untraced `1000` (the draft converted USD per MW to USD per kW, and no tool returned 1,000), and d01, d02, d05 and d08 each with an untraced `930` (the EIA-930 form named as a number). Every one was retried and its final answer passed the check, and every final answer of status "answered" passed it: no final answer states a number that no tool returned. Eleven answers used all eight tool calls the loop allows (b01, b07, b08, g03, g04, g08, g09, g10, d03, d04, d10).

## The thirteen wrong answers, by cause

| Cause | Count | Questions |
|---|---|---|
| The tool did not return the figure | 8 | b01, b02, b03, b04, b05, b06, b08, b09 |
| The answer stated a figure no tool returned | 0 | |
| The question needs a table the tools cannot reach | 0 | |
| The expected value was wrong | 5 | g03, g06, g09 (the key's tolerance), g08, d10 (the key's tables) |

| Id | Asked | Key then | Key now | The answer | Cause | What it rests on |
|---|---|---|---|---|---|---|
| b01 | ERCOT 4-hour foresight, total, 2025-10 to 2026-09, USD per kW | 81.4022 | 81.4022 | 81,402.19 USD per MW; refuses the per-kW conversion | The tool did not return the figure | No table holds USD per kW; the stated figure is the key times 1,000; the first draft's `1000` was untraced |
| b02 | the same, energy part | 54.5986 | 54.5986 | 54,598.58 USD per MW | The tool did not return the figure | as b01 |
| b03 | the same, ancillary part | 26.8036 | 26.8036 | 26,803.61 USD per MW | The tool did not return the figure | as b01 |
| b04 | ERCOT 2-hour day-ahead, total, 2025-10 to 2026-09 | 51.0671 | 51.0671 | 51,067.14 USD per MW | The tool did not return the figure | as b01 |
| b05 | ERCOT 4-hour foresight, 2021 | 3,430.5566 | 3,430.5566 | 3,430,556.56 USD per MW | The tool did not return the figure | as b01 |
| b06 | ERCOT 4-hour foresight, 2025 | 87.4396 | 87.4396 | 87,439.61 USD per MW | The tool did not return the figure | as b01 |
| b08 | CAISO SP15 4-hour foresight, 2025-10 to 2026-09 | 79.046 | **79.3083** | 79,308.31 USD per MW | The tool did not return the figure | as b01; and the key of 19 October was stale (the table's run of 20 October, 01:04 UTC): the stated figure is the key now times 1,000 |
| b09 | CAISO SP15 4-hour day-ahead, energy, 2025 | 42.3137 | **42.5038** | 42,503.77 USD per MW, 3 days left out | The tool did not return the figure | as b08; the 3 days left out are the table's (`dayahead_4h_days_left_out`) |
| g03 | ERCOT peaker margin, 2025 | 50,424.0741 | 50,424.0741 | "about 50,424 USD/MW" | The expected value was wrong | The figure is right; an absolute tolerance of 0.01 on a five-digit sum fails an answer rounded to the dollar |
| g06 | SPP North wind revenue, 2025 | 66,963.0112 | 66,963.0112 | "about 66,963 USD per MW" | The expected value was wrong | as g03 |
| g09 | ERCOT generator-rule battery, energy, 2025-10 to 2026-09 | 58,533.7042 | 58,533.7042 | "about 58,534 USD per MW" | The expected value was wrong | as g03 |
| g08 | NYISO N.Y.C. flat real-time price, July 2026 | 73.8689 | 73.8689 (held since 21 October) | 73.87 USD/MWh, cited `cost_of_power_monthly` | The expected value was wrong | The figure is right; the key accepts `merchant_revenue_monthly` only, and `cost_of_power_monthly`'s `rt_simple_mean` holds the same 73.8689 |
| d10 | PJM Western hub, August 2026 (must refuse) | refusal | refusal | "Not in the warehouse", no citation | The expected value was wrong | The refusal is right and states no figure; the key grades a refusal on a cited table, and a refusal cites none (g10 passed only because its answer cited the table it tried) |

## What a later session with a model budget would change, by cause

**The tool did not return the figure (8).** The battery page shows USD per kW; `battery_stack_monthly` holds USD per MW, and Ask's rule forbids a conversion it was not handed. Each of the three ways out is Samuel's ruling, and none needs a model to build: (a) the tools hand back the per-kW value beside the per-MW one where the table's method note names the conversion (`docs/methods/battery_stack.md`), so the number check can trace it; (b) the number check accepts a figure that is a returned figure divided by 1,000 when the question and the table name the two units; (c) the questions ask in USD per MW. After the ruling, with a budget: the eight asked again (`--only b01,...,b09`, about USD 0.68 at the first run's cost of those eight), with b08's and b09's keys taken from `eval_s539_keys.json` and every key computed again the same hour as the asking, after the day's run of `battery_stack_monthly`.

**The answer stated a figure no tool returned (0).** Nothing to change in the loop: the number check caught the twelve first drafts that did. What a later run should change is the record: ask with `ASK_RECORD_TOOLS=1` on the local server (as session 267 did), so that the fixtures hold every tool call and result and a regrade like this one can read what each tool returned, not only the answer and the server's log.

**The question needs a table the tools cannot reach (0).** None of the thirty on 20 October. Since 21 October four (g07, g08, d05, d07) read rows held for a license. With a budget: their keys rewritten as refusals ("license needed", no figure, no table graded) or the four questions moved to an unheld grid's hub (ERCOT, CAISO or SPP), then the four asked again to show that Ask refuses a held row (about USD 0.27 at the first run's cost). Which of the two is a choice for the eval's owner; the hold itself is Samuel's ruling of 12 October and stays.

**The expected value was wrong (5).** No model call is needed: the stored answers pass once the keys change, as the "if ruled" column of `eval_s539_regrade.json` shows (30 of 30 with the other two causes). For g03, g06 and g09: a key whose figure is 1,000 or more accepts the figure rounded to the unit (a relative tolerance in the question, or the grader's coarser-precision rule extended to whole numbers). For g08: the key's `tables` accept every table that holds the figure (`cost_of_power_monthly` beside `merchant_revenue_monthly`). For d10: a refusal is graded on the refusal and the absence of a figure, not on a cited table. Session 320 left each as a ruling (its report, "For Samuel's ruling"); this note does not change `questions_s320.yaml`. A session with a budget would only confirm, on one fresh asking of all thirty after the rulings, that the run writes `eval_s320_fixtures.json` with every answer right (about USD 2.21 at the first run's cost).
