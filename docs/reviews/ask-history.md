# Ask's evaluations: the history

Energy Research Warehouse (ERW). Written by `python warehouse/chat/eval/history.py` from the stored runs of `warehouse/chat/eval/` alone (session 1147); a test holds this file to what they give. A row is a run: the day it was asked (or graded), the set, what was graded, how many were right, its cost through the model, and where it is described.

| Day | Set | What | Right | Cost | Described in |
|---|---|---|---|---|---|
| 2026-10-14 | `questions_s267.yaml` | every public grid, asked through `/api/ask` (the stored answers as fixed) | 27 of 30 | USD 2.47 | session 267's report; `tests/test_session267.py` |
| 2026-10-19 | `questions_s302.yaml` | asked as the pages ask them (the stored answers after the fix at the cause) | 30 of 30 | USD 2.22 | session 302's report |
| 2026-10-20 | `questions_s320.yaml` | the three economics pages, first asking | 17 of 30 | USD 2.21 | session 320's report |
| 2026-10-21 | `questions_s320.yaml` | session 320's answers graded again on the keys of the day, under the license hold | 14 of 30 (17 on the figure keys) | none (no model) | `docs/reviews/ask-thirty-2026-10-21.md` |
| 2026-10-23 | `questions_s320.yaml` | asked again, graded under the hold | 19 of 30 (15 on the figure keys; 30 if session 320's rulings went the answers' way) | USD 2.76 | `docs/reviews/ask-thirty-2026-10-23.md` |
| 2026-10-23 | `questions_s1114.yaml` | thirty a trading, a finance and a policy lead ask, first asking | 24 of 30 | USD 2.84 | `docs/reviews/ask-sixty-2026-10-23.md` |
| 2026-10-23 | `questions_s320.yaml` | asked again after chains 076 and 085, graded under the hold | 19 of 30 (15 on the figure keys; 30 if session 320's rulings went the answers' way) | USD 2.90 | `docs/reviews/ask-sixty-2026-10-25.md` |
| 2026-10-23 | `questions_s1114.yaml` | asked again after chains 076 and 085, 30 of the thirty (the cap) | 28 of 30 | USD 2.42 | `docs/reviews/ask-sixty-2026-10-25.md` |
| 2026-11-06 | `questions_s320.yaml` | asked through the Python loop (eval_loop.py) after USD per kW on by default (chain 152), graded under the hold | 26 of 30 (22 on the figure keys; 26 if session 320's rulings went the answers' way) | USD 2.49 | `docs/reviews/ask-faults-2026-11-05.md` |
| 2026-11-06 | `questions_s320.yaml` | asked through the Python loop after a repeated call is counted and not read and a figure is written as returned (chain 152), graded under the hold | 29 of 30 (25 on the figure keys; 29 if session 320's rulings went the answers' way) | USD 1.96 | `docs/reviews/ask-faults-2026-11-05.md` |
| 2026-11-06 | `questions_s320.yaml` | asked through the Python loop and graded under the grader's two rules of session 2223 (session 320's ruling 3; chain 152), under the hold | 30 of 30 (26 on the figure keys; 29 if session 320's rulings went the answers' way) | USD 2.31 | `docs/reviews/ask-faults-2026-11-05.md` |
| 2026-11-06 | `questions_s2224.yaml` | twenty a lab's energy team asks (PPA prices, the datacenter tracker, the queues, storage, a grid's prices and reserve margin, a node's basis), through the Python loop, graded under the grader's rules (chain 152) | 20 of 20 | USD 1.82 | `docs/reviews/ask-faults-2026-11-05.md` |
| 2026-11-06 | `questions_s2918.yaml` | the board's five questions, first asking, graded on the keys of their own day (session 2918, from the rows of 6 November 2026, 05:16 UTC) | 4 of 5 | USD 0.18 | session 2918's report |
| 2026-11-06 | `questions_s2948.yaml` | the board's five questions through the Python loop (eval_loop.py), keyed on the rows of the asking hour (chain 157) | 5 of 5 | USD 0.46 | session 2948's report |
| 2026-11-06 | `questions_s320.yaml` | the weekly run through the Python loop on main as landed (chain 157), graded under the hold | 30 of 30 (26 on the figure keys; 29 if session 320's rulings went the answers' way) | USD 1.95 | session 2968's report |
| 2026-11-06 | `questions_s2224.yaml` | the twenty, the weekly run through the Python loop on main as landed (chain 157) | 20 of 20 | USD 1.31 | session 2968's report |
| 2026-11-06 | `questions_s2918.yaml` | the board's five questions asked again on the build of main of 6 November 2026, 08:30 UTC, after session 2918's k03 failed in the route; graded on session 2918's keys | 5 of 5 | USD 0.52 | session 1486's report |
