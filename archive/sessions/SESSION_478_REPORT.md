# Session 478 report: the stale tile (a branch, not landed)

21 October 2026, from 09:50 UTC, unattended, on lab-desktop (the data machine), the fourth session of the chain of 21 October, day and evening (`queue/done/020-day-21-october-data-2.md`). Model spend USD 0. Pulls: none. **On [`wip/478-stale-tile`](https://github.com/SamuelEnrique/erw/tree/wip/478-stale-tile) (`0f465e76`), not landed, for Samuel's ruling.**

## Read these first

- **Not `status: stale`, as the part asked, but a `held` mark with the status kept "ok".** The site keeps only rows whose status is "ok" (`site/lib/board.ts`, lines 230, 267, 279 and 314). So a status of "stale" would have taken the ERCOT tiles off the board, a change visitors see, which the chain rules out without a ruling. The mark leaves the board as it is until the code machine's page reads it.
- **`warehouse/derived/page_keep.py`, `mark_held()`**: after the merge, a held row whose last day is 2 or more days (`HELD_LAG_DAYS`) behind the newest day of its group and frequency gets `held = {since, newest, why}`. The `why` is the merge's own reason ("the new build's history is shorter ..."). A row taken new loses an old mark. Because its status stays "ok", `choose()` judges a marked row the next day exactly as before.
- **Tests**: `tests/test_session478.py`, 5 tests. Every test that names `page_keep` passes: 206, among them `test_page_keep` and sessions 121, 132, 134, 166, 170, 202, 247 and 284.
- **Measured on main's board at `e37f529f`** (GitHub's of 20 October, 06:22 UTC). The file does not record which rows a merge kept, so every row was treated as kept. At most 159 of 794 rows would carry the mark. Among them are the 12 ERCOT hub tiles, day-ahead held from 15 October and real time from 14 October, against the group's 20 October. Most of the rest are EIA's weekly and monthly prices (75), which lag their group by the publisher's own schedule. They are marked only if a merge actually kept them, so the real count is smaller.
- **For the code machine**: `/board` can read `held` and show "held from <since>: <why>" on the tile. That is a page change and theirs.

## Checks

| What | Exit | Notes |
|---|---|---|
| `tests.test_session478` | 0 | 5 tests |
| every test that names `page_keep` | 0 | 206 tests, 22 skipped |
| the mark applied to `e37f529f`'s board | 0 | `runs/s478_board_e37f.json` |

## Decisions made without you

1. A `held` field instead of `status: stale`, so that no tile leaves the board.
2. The measure taken within a group and its frequency, so that a quarterly row is not judged against daily ones.

## For Samuel's ruling

- Merge `wip/478-stale-tile`; then the board's rendering of `held` (the code machine).

## Files

- On `wip/478-stale-tile`: `warehouse/derived/page_keep.py`, `tests/test_session478.py`.
- On this chain's branch: this report.
