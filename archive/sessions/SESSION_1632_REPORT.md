# Session 1632 report: a row with no figure prints its words and no digit

6 November 2026, on samueloldlaptop's second window, chain 167. Branch `wip/1632-board`, cut from `wip/1631-board` with `origin/main` merged. Model spend USD 0.

## What it did

- `site/lib/board.ts`: `holdRows` drops `basis` and `heat_ref` with the figures; `boardFileChecks` counts a kept `basis` on a row with no value as a fault (audit row 40, closed).
- `warehouse/derived/board_page.py`, `Board.add`: a row with no value is written without `basis`, `ext`, `inputs` or `heat_ref`. The new check found this second case: the "not held yet" rows the builder writes (a load zone held in day-ahead only, a month with no priced 4CP interval) kept their words.
- The method note's section; `tests/test_board_1632.py` (1 test).

## Proof

- The wide set (every test file naming the board's code, every `test_board_16*`): 338 run, the known `test_session1116` failure only.

## Decisions made without you

- **A row with no value loses its interval's words too**, not only a held one: the chain's rule is about a series the board does not show, whatever the reason.

## For Samuel's ruling

- None new.
