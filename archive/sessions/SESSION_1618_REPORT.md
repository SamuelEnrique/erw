# Session 1618 report: the file's size and the build's time

6 November 2026, on samueloldlaptop's second window, chain 165. Branch `wip/1618-board`, cut from `wip/1617-board` with `origin/main` merged. Model spend USD 0.

## What it did

- Measured `board.json` under this chain's builder: every row with values made again from its own series file with the new `stats()`, the new rows added at the measured size. 992,915 bytes today (176,261 compressed); about 1.54 MB with this chain's figures and rows (about 265 KB compressed), about 55 percent more.
- The decision, in the method note: not paged, not summarized; a budget of 2.5 MB as written and 400 KB compressed, held by `tests/test_board_1618.py` on the site's file.
- The build's time estimated from this machine's builder logs (65 to 112 seconds on 6, 9 and 12 October) and the two larger tables this chain reads: about 3 to 4 minutes here.
- Tried and reverted: dropping a held grid's rows before the hourly store. It would change what the held rows say (a held grid's zones would leave the build, and its main hub's spark row would read "not held yet" instead of "license needed").

## Proof

- `tests.test_board_1618`: passed. The builder file is as session 1617 left it (`git checkout` of the trial).

## Decisions made without you

- **No paging**: the file grows by about half, and compressed by about 90 KB; the chain's rule pages only a row set that doubles the file.
- **No full build here**: its memory belongs to the first window's build; the estimate is from the logs and the tables' sizes, and says so.

## For Samuel's ruling

- None new.
