# ERCOT evaluation, second set (session 121), before

Ask ERCOT (warehouse/chat/ercot.py), as it stood when the session began; model claude-sonnet-5-5; 2 of 2 questions run; today = 2026-10-04; backend local.

| Kind | Correct | Median seconds to the first thing shown | Median seconds to the full answer | Mean cost (USD) |
|---|---|---|---|---|
| premise | 1 of 1 | 12.5 | 12.5 | 0.0548 |
| outside | 1 of 1 | 22.3 | 22.3 | 0.0672 |
| all | 2 of 2 | 17.4 | 17.4 | 0.0610 |

| Measure | Result |
|---|---|
| Correct | 2 of 2 |
| status | 2 of 2 |
| number | 1 of 1 |
| citation | 1 of 1 |
| nearest | 1 of 1 |
| Retried after the check | 0 |
| Answers that came with a series | 0 (0 with every series checked against the rows the tool returned) |
| Seconds to the first thing shown: median, 90th percentile | 17.4, 22.3 |
| Seconds to the full answer: median, 90th percentile, longest | 17.4, 22.3, 22.3 |
| Cost of the questions | USD 0.1219 (mean 0.0610, highest 0.0672) |
| Cost of the first questions of the follow-ups | USD 0.0000 |
| Mean tool calls | 5.50 |
| Session 121 in the ledger | USD 0.0000 before this run, USD 0.1219 after; cap USD 0.30 |

| Id | Kind | Correct | Status | Calls | Seconds, first | Seconds, full | Cost (USD) | Checks |
|---|---|---|---|---|---|---|---|---|
| p15 | premise | yes | answered | 3 | 12.5 | 12.5 | 0.0548 | status ok, number ok, citation ok |
| o13 | outside | yes | not_in_warehouse | 8 | 22.3 | 22.3 | 0.0672 | status ok, nearest ok |
