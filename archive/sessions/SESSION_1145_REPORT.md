# Session 1145 report: Ask beside the board

23 October 2026, 21:41 to 21:47 UTC, on samueloldlaptop, unattended, on `wip/1145-ask` (cut from `wip/1147-ask`). Chain `queue/done/085-day-25-october-code-ask-board-3.md`. Model spend USD 0.

## What was found first

- The general chat (the Lower 48) and the six other grids' chats are drawn by `site/app/ask/AskForm.tsx`, through the Grid tool's Ask view; only Ask ERCOT uses `components/ask/AskPanel.tsx`. Chains 075 and 076 brought the panel to the route's new fields (the read lines, the time, the nearest tables, the series, the refusal's words, the conversation), so those reached Ask ERCOT's readers only: the general chat's form drew the answer and its sources alone, and sent no earlier turn.

## What was done

- **The form draws what the route returns**, as the panel does: the lines of what each query read and the time the answer took (session 1115), the nearest tables of a refusal (1132), the series an answer rests on (1142, with the panel's own `SeriesBlock`, now exported), the refusal's words (1110). It keeps the conversation (1129): the last three turns sent with the next question, "Ask next" and "New conversation" once one has begun.
- **The board asks its own questions**: under the board's table downloads, "Ask the board", the same form with the five board questions (`questions_s1122.yaml`) as examples a reader can click; a click places the question in the box and sends nothing. The questions are in `site/data/board_questions.json`, written by `warehouse/chat/eval/expected_s1122.py` (the site reads no file outside `site/`). Their stored answers wait for their first asking (session 1142's item 3).
- The Grid tool's own view (`components/grid/AskView.tsx`, chain 077's) is not touched: it draws the form, and the form changed.

## Checks

- `tests.test_session1145`; the board's and Ask's tests (504): exit 0, after session 241b's test of the form's button moved with it ("Ask next").
- `npx tsc --noEmit`: no error in a changed file. A build and screenshots: with session 1142's item 4 (the board at a keyboard), on the next build this machine has room for.
- Em dashes: 0.

## Decisions made without you

1. **The general chat's form, not a new component**: the form is this chain's (`site/app/ask/`), and every chat but Ask ERCOT's already draws it. Reversible.

## For Samuel's ruling

- None new.
