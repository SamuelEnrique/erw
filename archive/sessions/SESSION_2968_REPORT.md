# Session 2968 report: the Ask evaluation's weekly run

6 November 2026, about 09:38 to 09:52 UTC, on lab-desktop (the data machine), chain 157 (the owner's), unattended. **Model spend USD 3.26** (the thirty USD 1.952, the twenty USD 1.3115), within the USD 4 cap. Pulls: the Claude API; the live set's anon reads.

## Read these first

- **No regression.** The weekly run through the Python loop (`eval_loop.py`) on main's code as landed at `1b4caf85f`:
  - **the thirty** (`questions_s320.yaml`): 30 of 30 under the hold (26 on the figure keys, 29 if session 320's rulings went the answers' way), asked 30 of 30, USD 1.95. The same as session 2223's last;
  - **the twenty** (`questions_s2224.yaml`): 20 of 20, USD 1.31. The same as session 2224's;
  - **the board's five:** 5 of 5, session 2948's run of an hour earlier on the same code (USD 0.46). With all three the cap would have been passed (USD 4.6 at the last runs' costs), so it was not asked a second time.
- **The record:** `runs.json` lists the two runs (`eval_s2968_loop_run.json`, `eval_s2968_loop_s2224_run.json`, with their grades); their keys file is under `left_out`. `ask-history.md`, `ask-replay.md` and `ask-refusals.md` were written again.
  - Tests 1147 (16 runs) and 1304 now count the new runs' refusals: held 9 (the twenty's l01 to l04 again), pause 9 (g10 and l10 again). Ask's tests: 60 passed.

## Decisions made without you

- **The board's five not asked twice in the hour** under one cap.

## For Samuel's ruling

- None.
