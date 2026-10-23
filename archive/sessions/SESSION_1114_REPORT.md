# Session 1114 report: thirty more questions, the ones a lab asks (written; the asking waits for a build)

23 October 2026, 18:58 to 19:20 UTC, on samueloldlaptop, unattended, on `wip/1113-ask`. Chain `queue/done/075-morning-23-october-code-ask-board.md`. Model spend USD 0: the thirty were not asked.

## Read these first

- `warehouse/chat/eval/questions_s1114.yaml`: the thirty, ten from a power trading lead (t), ten from an infrastructure-finance lead (f), ten from a policy lead (p), each with its key and a note naming table, entity, variable, period and aggregation.
- `warehouse/chat/eval/expected_s1114.py`: computes every key from the live set (the anon key, reads only) and writes the file; `keys_s1114.json` holds the keys with their parts.

## What was done

- **The set**, written by a background agent of this session from the brief of the chain file and the live set's own names, and run again here at 19:20 UTC (exit 0, all thirty computed; every key the same as the agent's run, only the computed time moved). Grids ERCOT, CAISO and SPP and national series only: no key is a row of a grid held for a license (ISO-NE, NYISO, MISO), none is PJM's. No question asks in USD per kW. Every period was checked whole: a missing month, day or hour, a partial month or a tie at a high or low stops the run. Eight are single months, ten sums or means, twelve highs, lows or differences.
- **What the agent found**: the hourly price and demand tables of the live set start on 18 September 2026 (not 26 August), so their two questions (t07, p09) use stated UTC ranges in October; their rows leave the live set's 35-day window from about 5 November, so those two keys are to be kept, not computed again, after that. SPP North's day-ahead lacks 15 October, and ERCOT's real-time and demand have gaps: no question uses them.
- **The grading** (`eval_s1113.py --grade --set s1114`): session 267's grader on each key, a date in a question's required words accepted either way ("September 3" or "3 September").
- `expected_s1114.py` reads the keys from this checkout's `.env`, else the main checkout's beside it (it named this machine's path first).
- **Not done: the asking**, for the reason in session 1113's report (no build: the lock held and the machine low on memory). `docs/reviews/ask-sixty-2026-10-23.md` waits for it.

## Checks

- `python warehouse/chat/eval/expected_s1114.py`: exit 0 (the agent's run, then this session's at 19:20 UTC: the same thirty keys).
- Em dashes in the three files: 0.

## To finish

1. After session 1113's step 3: `python warehouse/chat/eval/expected_s1114.py` (the hour of the asking), `python warehouse/chat/eval/eval_s1113.py --ask --set s1114 --base http://localhost:3713 --cap <the day's step spend plus 6>`, `--grade --set s1114`; `docs/reviews/ask-sixty-2026-10-23.md` with both sets; the wrong answers' causes into chain 076's session 1127.

## Decisions made without you

1. **The set was written by an agent** of this session, its keys computed by code from the live set and checked here by running the script once more (the same keys). Reversible.

## For Samuel's ruling

- None new.
