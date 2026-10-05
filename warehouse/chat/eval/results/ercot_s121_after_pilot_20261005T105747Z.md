# ERCOT evaluation, second set (session 121), after

Ask ERCOT (warehouse/chat/ercot.py), with the session changes; model claude-sonnet-5-5; 11 of 11 questions run; today = 2026-10-04; backend local.

| Kind | Correct | Median seconds to the first thing shown | Median seconds to the full answer | Mean cost (USD) |
|---|---|---|---|---|
| join | 1 of 1 | 7.6 | 17.2 | 0.0557 |
| vague | 2 of 2 | 7.2 | 13.1 | 0.0231 |
| followup | 2 of 2 | 2.3 | 7.2 | 0.0174 |
| premise | 2 of 2 | 2.9 | 12.8 | 0.0265 |
| outside | 4 of 4 | 3.6 | 3.9 | 0.0187 |
| all | 11 of 11 | 3.6 | 11.7 | 0.0240 |

| Measure | Result |
|---|---|
| Correct | 11 of 11 |
| status | 11 of 11 |
| number | 5 of 5 |
| text_any | 2 of 2 |
| citation | 7 of 7 |
| nearest | 4 of 4 |
| Retried after the check | 2 |
| Answers that came with a series | 3 (3 with every series checked against the rows the tool returned) |
| Seconds to the first thing shown: median, 90th percentile | 3.6, 7.6 |
| Seconds to the full answer: median, 90th percentile, longest | 11.7, 17.2, 19.6 |
| Cost of the questions | USD 0.2644 (mean 0.0240, highest 0.0581) |
| Cost of the first questions of the follow-ups | USD 0.0252 |
| Mean tool calls | 1.82 |
| Session 121 in the ledger | USD 3.1064 before this run, USD 3.3959 after; cap USD 3.75 |

| Id | Kind | Correct | Status | Calls | Seconds, first | Seconds, full | Cost (USD) | Checks |
|---|---|---|---|---|---|---|---|---|
| j20 | join | yes | answered | 3 | 7.6 | 17.2 | 0.0557 | status ok, number ok, citation ok |
| v01 | vague | yes | answered | 3 | 7.9 | 14.5 | 0.0267 | status ok, citation ok |
| v10 | vague | yes | answered | 2 | 6.4 | 11.7 | 0.0195 | status ok, citation ok |
| f01 | followup | yes | answered | 1 | 2.7 | 8.9 | 0.0211 | status ok, number ok, citation ok |
| f09 | followup | yes | answered | 1 | 1.9 | 5.4 | 0.0137 | status ok, number ok, citation ok |
| p02 | premise | yes | answered | 2 | 3.1 | 12.0 | 0.0235 | status ok, number ok, text_any ok, citation ok |
| p18 | premise | yes | answered | 2 | 2.7 | 13.7 | 0.0294 | status ok, number ok, text_any ok, citation ok |
| o01 | outside | yes | not_in_warehouse | 0 | 3.6 | 3.6 | 0.0056 | status ok, nearest ok |
| o05 | outside | yes | not_in_warehouse | 0 | 4.2 | 4.2 | 0.0058 | status ok, nearest ok |
| o10 | outside | yes | not_in_warehouse | 6 | 3.5 | 19.6 | 0.0581 | status ok, nearest ok |
| o13 | outside | yes | not_in_warehouse | 0 | 3.6 | 3.6 | 0.0053 | status ok, nearest ok |
