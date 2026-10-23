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
