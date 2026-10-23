# Session 1115 report: Ask on the page

23 October 2026, 18:52 to 18:57 UTC, on samueloldlaptop, unattended, on `wip/1115-ask` (cut from `wip/1112-ask`). Chain `queue/done/075-morning-23-october-code-ask-board.md`. Model spend USD 0. (This report was written by session 1141; session 1115 committed its code and test without one.)

## What was done

- **Every answer shows what its queries read** (`readsOf` in `site/lib/chat/ask.ts`; the panel `site/components/ask/AskPanel.tsx`): under the answer's sources, one line for each query or compare: the table, the entity, the variable, the window (the end not included) and the aggregation, never a figure; a held grid's answer and a failed call are not listed.
- **The time it took**, under it: "Answered in <seconds> seconds, <n> reads of the warehouse.", from the answer's own `seconds` and `tool_calls`.
- **The refusal in its own words**: the panel heads a refused answer "The warehouse does not hold that figure", the words session 1110 gave the refusal.
- **Not done here**: the thirty questions as examples a reader can click. `/ask` has redirected to the Grid tool's Ask panel since session 299, and chain 077's session 1157 (the Grid tool, the other chain on this machine) built clickable stored examples there (`site/components/grid/AskExamples.tsx`); this chain does not touch the Grid tool's files. The board's own Ask, with its five questions as examples, is chain 085's session 1145.
- Screenshots of an answer with its read lines need a question asked in a browser (a model call): left to chain 076's session 1138 with the board's keyboard walk.

## Checks

- `node --import ./scripts/alias-register.mjs scripts/test-ask-1115.mjs`: exit 0, 4 of 4; `tests.test_session1115`: exit 0; the Ask tests: exit 0.
- Em dashes: 0.

## Decisions made without you

1. **The examples left to the Grid tool's chain**, which built them the same day. Reversible.

## For Samuel's ruling

- None new.
