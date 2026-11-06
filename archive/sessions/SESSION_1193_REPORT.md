# Session 1193 report: the held grids said once a group

23 October 2026, 23:24 to 23:30 UTC, on samueloldlaptop, unattended. Chain `queue/done/089-day-26-october-code-ask-board-4.md`. Model spend USD 0.

- **Done**: within a group, the rows of a grid held for a license are one line under the public rows: the grid, its count of rows, "license needed" with the hold's words on hover and, for a screen reader, in the line itself; a toggle ("Show the rows' names", `aria-expanded`, `aria-controls` naming each row) shows the rows, blank as they were. The rows stay in the page (hidden until asked), so "every row is in the page either way" holds, and nothing about the hold or its words changes. `lib/board.ts` `heldLines` (pure: the shown rows and the held rows by grid), `components/board/BoardView.tsx` (`GroupTable`, `PriceRow`'s `hidden` and `domId`).
- **On today's file** (the 16:19 build, with the day's hold): 10 lines in the groups' default views (Power by hub, on-peak and off-peak, spark and dark spreads, day-ahead minus real time, battery spread: NYISO and ISO-NE each), for 20 rows; 135 rows of the file are "license needed" across every filter's choices.
- **Tests**: `site/scripts/test-board-1193.mjs` (5: every row kept, a line one grid's rows, the shown rows' order unchanged, the drawing's marks, a group with no held row as before), run by `tests/test_session1193.py`; `check-board.mjs` checks each line on a build (its count, the words, the toggle closed, its rows hidden). The board's earlier tests (1116, 1137) pass. Type check: no error but the build's own generated files (route types, `content/waits.json`).
- **Not yet**: the screenshots at 390 and 1280 and `check-board.mjs` on a build: on the chain's one build, before its landing.
- On `wip/1190-ask`.

## Decisions made without you

1. The held rows kept in the page, hidden, rather than left out: the board's rule since session 240 is that every row is in the page; the toggle's words are "Show the rows' names" and "Hide the rows' names".

## For Samuel's ruling

None.
