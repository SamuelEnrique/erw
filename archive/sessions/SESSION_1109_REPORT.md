# Session 1109 report: the tools return the right rows

23 October 2026, 18:06 to 18:12 UTC, on samueloldlaptop, unattended, on `wip/1109-ask` (cut from `wip/1108-ask`). Chain `queue/done/075-morning-23-october-code-ask-board.md`. Model spend USD 0. No database read, no web request.

## Read these first

- `site/lib/chat/tools.ts` `perKw` and `warehouse/chat/tools.py` `per_kw`: USD per kW beside USD per MW, behind the switch `ASK_PER_KW`, **off**.
- `tests/fixtures/session1109/battery_reads.json`: the 93 saved monthly rows behind the eight per-kW questions, with each question's sum and key.

## What was done

- **The rows, on the eight per-kW questions** (b01 to b06, b08, b09): one `query` call (aggregation `sum`, entity, variable, start, end) returns each question's figure in USD per MW over exactly its twelve months, and every one equals session 539's key times 1,000 within the key's tolerance (`python warehouse/chat/eval/fixture_s1109.py --check`: 8 of 8 agree). So the tool chooses the right table, window, entity and rows: no window off by a day or a zone (the rows are dated the first of the month at 00:00 UTC, and a start of `2025-10-01` takes October), no entity that fails to resolve. The tool calls the stored run spent beyond one (b01: 8) were the model's, not the tool's; which ones the run did not record (session 1111 turns the record on for an evaluation).
- **The unit, prepared for ruling 1 and left off.** With `ASK_PER_KW=on`, a query of `battery_stack_monthly` whose rows are all USD/MW carries `value_usd_per_kw` (the figure divided by 1,000, the method note's own conversion, `docs/methods/battery_stack.md`) and `per_kw: {unit, rule}`; the number check then traces the per-kW figure (a test). Off, which is the default and what the site runs, every result is key for key what it was (a test). Only the one table whose method names the conversion is listed.
- **The other 22 questions**: no tool fault can be read offline without a trace; the stored answers' figures were the table's in every case session 539 checked (`ask-thirty-2026-10-21.md`). Nothing changed for them.

## The grader on the stored answers

Unchanged, as it must be: no change here alters a stored answer. 17 of 30 on the keys now, 14 of 30 under the hold (session 539's counts, `eval_s539_regrade.json`). With the switch on and the eight asked again, the tool would hand back each key's own figure (8 of 8 in the fixture), so the count would be 22 of 30 under the hold with ruling 1 alone, before rulings 2 and 3.

## What to review

1. `https://github.com/SamuelEnrique/erw/blob/main/site/lib/chat/tools.ts`: search `perKw` (the switch, the one table, the rule's words).
2. `tests/fixtures/session1109/battery_reads.json`: under `questions`, each `sum_usd_per_mw` beside `key_usd_per_kw`.
3. To turn it on after a ruling: set `ASK_PER_KW=on` in Vercel's environment and on the local server; nothing else.

## Checks

- `node --import ./scripts/alias-register.mjs scripts/test-ask-1109.mjs` (in `site/`): exit 0, 5 of 5.
- `python -m unittest tests.test_session1109`: exit 0, 7 tests.
- `python -m unittest tests.test_session320 tests.test_session267 tests.test_session302 tests.test_session168_ask`: exit 0, 44 tests (2 skipped, as before).
- Em dashes in the changed files: 0.

## The landing

Lands with sessions 1108 to 1112 in one push (session 1108's decision 2).

## Decisions made without you

1. **The per-kW change is built and off** (`ASK_PER_KW`, default off), so ruling 1 is one setting. Reversible: the switch, or the 20 lines in each tool file.
2. **The fixture is copied from this machine's `battery_stack_monthly.csv`** (restored from the archive at the 21 October run), not read from the live set, under the chain's "no web request". It agrees with session 539's live-set keys on all eight.

## For Samuel's ruling

- Ruling 1 of session 320, now ready: turn `ASK_PER_KW=on` (the tools hand back USD per kW where the method names the conversion), or keep the answers in USD per MW and change the eight questions to ask in USD per MW.
