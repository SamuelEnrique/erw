# Session 5201: the faults file's open rows

Energy Research Warehouse (ERW). portable-laptop, window P3, 13 November 2026 (10:05 to 10:35 UTC), Fable, unattended. Chain 235. Branch `wip/5200-ask` (worktree `erw-p3-5200`), stacked on session 5200. No model call, nothing built, nothing landed.

## Read these first

- `docs/reviews/ask-faults-2026-11-05.md` now ends with "The state of every row": **no row is open**.
- The second thirty's newest asking regrades to **30 of 30** (28 as stored, 29 under the 2223 rules): t09 by the rule of session 2223, f09 by a new rule, `sign_in_words`.
- Both were the key's, not the chat's: the two answers were right to the cent. No prompt, tool or loop code changed.

## What was done

- **`warehouse/chat/eval/eval_s267.py`**: `RULES_5201` = the 2223 rules and `sign_in_words`. A negative expected figure is met by its magnitude when the figure's own sentence holds a word of the direction (less, lower, below, fell, minus and their kin, matched as whole words). A positive figure is never met by a negative one.
- **`warehouse/chat/eval/eval_loop.py`**: grades under `RULES_5201` from now on; `--rules 2223` and `--rules none` for the old ways.
- **`eval_s5201_regrade_s1133_grades.json`**: the stored regrade, named in `runs.json` under `left_out` (a regrade, not a run).
- **The faults file**: a state for each of its 21 items and the second set's five answers, each with the test that holds it.
- **`tests/test_session5201_ask.py`** (23 tests): the rule and its limits; the second thirty at 28, 29 and 30 under the three gradings; f09 the only answer the rule turns over five stored sets, none right before wrong after; items 9 and 10 (session 2222's fix, which had no test of its own): rule 1's words in both loops and the three sums to the cent in the four askings since; the faults file's states.

## Checks run

- `tests/test_session5201_ask.py` with the 71 other test files that read the grader, the runs list or the faults file: 797 passed, 69 skipped, exit 0 (3 min 16 s).
- `check_spec.py`, `replay.py --check`, `history.py --check`, `refusals.py --check`: each exit 0.
- Precheck (from the main checkout): exit 0.

## Model spend

- Session: USD 0.00. Chain: USD 0.00 of USD 20.

## Decisions made without you

- **f09 is fixed in the grader, not in the chat.** "3,369.62 USD/MW less at ERCOT" is a right answer in plain words; teaching the chat to write a minus sign for one key would be tuning to one question.
- **The new rule is a named rule, off for every stored grading.** The gradings of 20 October to 12 November stand as their tests pin them.
- **One worktree for the stack** (`erw-p3-5200`), not one a session: a checkout is 18,052 files and memory is short with three windows.
- **t09's table choice is left to the widened set** (the hourly source read where a monthly table holds the figure): a class to measure over many questions.

## For Samuel's ruling

- None new.
