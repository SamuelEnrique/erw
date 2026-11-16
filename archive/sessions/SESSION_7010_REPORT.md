# Session 7010 report: the price board's replication (the done line's tool 17)

Energy Research Warehouse (ERW). Chain 301, data machine (lab-desktop), 16 November 2026. Opus 5.5. Model spend USD 0.

## What was built

- **`replication/board/replicate.py`**: an independent replication of `site/data/board.json` and its series files from `docs/methods/price_board.md` and the tables alone: every row's latest, change and window figures from its series file by the method's column rules, and in a second part the power rows' series checked day by day against the warehouse's hourly tables. 30,587 of 30,587 figures equal (commit `e897a9b16`). Session 7013 extended its day test to the days of a clock change (a day's hours counted in UTC): 30,607 of 30,607.
- **`replication/board/replicate.do`**: five day-ahead figures in Stata, expected values at its top (not run: Stata is not on this machine).
- The method note `docs/methods/price_board.md` names the replication.

## Faults found

- None: every figure equal.

## Landing

- In gate e (`de68a6669`), landed at `f4cc50518` (session 7013's report).

## For Samuel's ruling

- None new.
