# Sessions 1634 to 1637 report: the faults, none open

6 November 2026, on samueloldlaptop's second window, chain 167. Branch `wip/1634-board`, cut from `wip/1633-board` with `origin/main` merged. Model spend USD 0.

## What they did

- Read `docs/reviews/board-audit-2026-11-06.md` for open rows: every one of the 40 has a state. Rows 1 to 23 and 26 to 40 are closed or noted; rows 24 and 25 (CFTC positions, EIA's STEO forecasts) are out of the board's scope and wait for your ruling (chain 165's note, item 1). There is no open fault for sessions 1634 to 1637 to close, so no code changed in them, and they are recorded here together.
- The checks of the file (`check-board.mjs --file`) on the site's file: 8 of 8, as at session 1622.

## Decisions made without you

- **No work invented for empty sessions**: the four sessions' step is "the open rows of the audit, one a session"; with none open they are recorded as done in one report, not filled with changes the board does not need.

## For Samuel's ruling

- Rows 24 and 25, as in chain 165's note.
