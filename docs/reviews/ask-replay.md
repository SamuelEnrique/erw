# Ask's stored answers through today's checks

Energy Research Warehouse (ERW). Written by `python warehouse/chat/eval/replay.py` (session 1301) from the stored runs of `warehouse/chat/eval/` alone, with no model: every answer the loop let through, with its tool record, run again through the number check, the unit check and the citations of `warehouse/chat/ask.py` as they now stand. A test holds this file to what the runs give and holds that no answer graded right would now be sent back.

| Run | Answers let through | Graded right | Would now be sent back | Of them graded right |
|---|---|---|---|---|
| session 267 | 30 | 27 | 0 | 0 |
| session 302 | 29 | 29 | 0 | 0 |
| session 1113 | 30 | 19 | 0 | 0 |
| session 1114 | 30 | 24 | 0 | 0 |
| session 1149, first set | 30 | 19 | 0 | 0 |
| session 1149, second set | 8 | 8 | 0 | 0 |

In all: 157 answers, 0 would now be sent back.
