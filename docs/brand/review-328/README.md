# Session 328: /board and /prices, finished (lighter)

Each page's main at 1280 and 390 px, before (production, 20 October 2026 at about 04:45 UTC, with sessions 316 to 319
landed) and after (the local build of `wip/328-board-prices`).

- `board_before_*` against `board_after_*`: at the board's foot, "Download the tables:" with each public table the board
  is built from (a CSV with a Python and a Stata reader where the table is in the live set; "on Redivis" where it is
  not). The distribution's threshold, in the workbench, now says its default in grey beside the box, with a Reset
  (open a row, then Distribution, to see it: the shots are of the board as it opens).
- `prices_before_*` against `prices_after_*`: the first tab's lead ends with "Method" (the new note
  `docs/methods/power_prices.md`); under the six grids, each grid's real-time and day-ahead table to download.
- `prices_ercot_before_*` against `prices_ercot_after_*`: the ERCOT tab's two tables to download; the box plot's
  caption no longer speaks of a slider (gone since session 317); at 390 a median's label that ran past the drawing's
  right edge (a whisker cut at the axis) is written inside it, above its line.
- `prices_compare_*`: `/prices/compare`, unchanged (the shots are the same file before and after).

No number moved: `check-values` on `/board`, `/prices` and the explorer reads every checked number as before.
