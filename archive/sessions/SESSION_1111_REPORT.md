# Session 1111 report: the loop finishes the question

23 October 2026, 18:18 to 18:22 UTC, on samueloldlaptop, unattended, on `wip/1111-ask` (cut from `wip/1110-ask`). Chain `queue/done/075-morning-23-october-code-ask-board.md`. Model spend USD 0. No database read, no web request.

## Read these first

- `warehouse/chat/ask.py`: `MAX_TOOL_CALLS`, `why_refused`, `Asker(record_tools=...)`.
- `site/app/api/ask/route.ts`: `ledgerOpts` (an evaluation now records its tool calls).

## What was done

- **The limit, from the stored counts.** Session 320's thirty used 2 to 8 calls; 11 used all 8 (b01, b07, b08, d03, d04, d10, g03, g04, g08, g09, g10), so 8 is a floor of what they needed, not a measure. The limit is now **12** in `ask.py`, in the rule the model reads ("You have at most 12 tool calls") and in the spec the site reads (`site/lib/chat/spec.json`, exported). No answer of the thirty was wrong because of the limit (five that reached it were right), so this buys room, not points; session 1113's run, with the calls recorded, measures what the questions take. The route's own time limit (120 seconds) stays: the longest of the thirty took 32.4.
- **The tool calls, recorded in every evaluation.** The site records every tool call and its result when a request is admitted as an evaluation (its header and the server's `ASK_EVAL_TOKEN`, session 314), not only under `ASK_RECORD_TOOLS=1`; a visitor's answer never carries it. `eval.py` asks with `Asker(record_tools=True)`; the CLI and the grid chats do not.
- **A refusal says why, in one sentence with no figure.** After the second miss the answer is the refusal of session 1110 and one sentence: "Why: the draft was checked twice and a figure in it was in no tool result." (or a unit no tool gave it in, a table no tool read, an empty or uncited draft, this chat's own checks), joined when there are several. The record carries it as `why`. No digit is in it, so the reader is told what failed and never the untraced number. The same words in both languages (a test).

## What to review

1. `https://github.com/SamuelEnrique/erw/blob/main/warehouse/chat/ask.py`, search `why_refused`: the five sentences.
2. `tests/test_session1111.py`: the nine-call question answered by a scripted client, no model.

## Checks

- `python -m unittest tests.test_session1111`: exit 0, 7 tests.
- The Ask test files (sessions 35 to 320, 1109, 1110, 1111): exit 0 after one change to an old test: session 267's test read the trace line of `ask.ts` word for word; it now reads the new line (the trace is still off for a visitor).
- Em dashes in the changed files: 0.

## The landing

Lands with sessions 1108 to 1112 in one push.

## Decisions made without you

1. **12 calls, not a measured number**: the stored run cannot say what a question needs past 8. Reversible: one constant, one rule line, an export.
2. **Ask ERCOT's own prompt still says "at most 8"** (`warehouse/chat/ercot.py` rule 6, and its exported spec), while the loop it shares now allows 12: changing it changes the reference profile's spec, which its tests hold byte for byte, for no answer that needed it. Reversible.

## For Samuel's ruling

- None new.
