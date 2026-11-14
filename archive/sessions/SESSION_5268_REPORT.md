# Session 5268: rule 11, to stop

Energy Research Warehouse (ERW). portable-laptop, window P3, 14 November 2026 (09:16 to 09:21 UTC), Fable, unattended. Chain 256. Branch `wip/5200-ask-close` (worktree `erw-p3-5264`). Nothing built, nothing landed, no model call, no warehouse data written.

## Read these first

- **The chat's rules now say when to stop.** Rule 11 of the shared prompt, so in both loops: answer when a result holds the figure; the same rows asked another way are not a second source; a further call is for something that can be named.
- **It keeps the care for a short window.** Whether a window is complete is in the result (`window`, session 5267). When it is not whole, the answer says which part is held and gives a figure only as the figure of the steps held.
- **It keeps one check a window cannot make:** a row of a table of days, months or years that covers part of its period. The table says so in a variable of its own; the rule asks for it once.
- **Ask ERCOT's own rules are not changed.** The limit of 12 calls is not changed.

## What was done

- Precheck from the main checkout: exit 0.
- `warehouse/chat/ask.py` `RULES`: rule 11. `warehouse/chat/tools.py`: the query tool's description says what `window` is.
- `site/lib/chat/spec.json` exported again (`ask.py --export-spec`): two lines changed, the system prompt and the query tool's description. `check_spec.py` exit 0.
- `docs/methods/ask.md`: the section "A window says whether it is whole, and the chat is told to stop".
- `tests/test_session5268_ask.py` (9 tests): the rule's words, the description, the exported spec, Ask ERCOT's rules untouched.

## The rule

- "11. Stop when you have the answer. When a tool result holds the figure the question asks for, write the answer. Do not ask the same rows again with another grouping, time zone, aggregation or filter to confirm a figure you already have: the same rows read another way are not a second source."
- "Whether a window is complete is said by the result itself: a query of a series with start and end returns window (steps_held, steps_in_window, whole, and the runs of steps missing), so no count and no regrouping is needed for it; when window.whole is false, say which part is held and give a figure only as the figure of the steps held, never as the whole period's."
- "One check the window cannot make: a row of a table of days, months or years may cover only part of its period, and such a table says so in a variable of its own (the hours or days behind the row, such as da_hours or days_held); where the table has one, read it once before giving the row's figure as the period's."
- "Make any other further call only for something you can name: a figure the results do not hold, or a second figure the question asks for."

## Checks run

- `tests/test_session5268_ask.py`: 9 passed.
- The wide run on this tree is under "The wide run" below.

## Model spend

- Estimate before: USD 0.00. Actual: USD 0.00. Chain 256: USD 0.00 of USD 20.

## Decisions made without you

- **A rule of the prompt, and the tool beside it.** Session 5257 held back a rule alone, because the calls after the figure are also how the chat found a month held in part. With the window in the result the rule can ask for less.
- **No lower limit of calls.** The figure was in hand by the fourth call in all 80 answers, but a refusal for a missing day took 10 to 12; the limit stays 12 until the askings say what a question needs.
- **Not in Ask ERCOT's rules.** Its prompt, its planner and its fast path are another design, measured by other sets.

## For Samuel's ruling

- None new.
