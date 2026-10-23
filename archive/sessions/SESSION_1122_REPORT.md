# Session 1122 report: Ask reads the board

23 October 2026, 19:00 to 19:03 UTC, on samueloldlaptop, unattended, on `wip/1122-ask` (cut from `wip/1118-board`). Chain `queue/done/075-morning-23-october-code-ask-board.md`. Model spend USD 0. Reads of the live set with the anon key only (the fixture), no write.

## Read these first

- `warehouse/chat/tools.py` `board_rank` and `site/lib/chat/tools.ts` `boardRank`, `rankRows`, `BOARD_MEASURES`.
- `warehouse/chat/eval/questions_s1122.yaml` and `expected_s1122.json`: the five questions and their keys.

## What was done

- **A fifth tool, `board_rank(measure, order)`**: every hub's newest value of one of the board's measures (the day's day-ahead or real-time mean, the move on the day before in USD or percent, day-ahead less real time, the spark spread, the implied heat rate), ranked highest, lowest or by the size of the move, each value with its own date. It is `query` (latest by entity) and a sort, so its figures are the board's derived tables' own and the number check traces them as any query's; on the site the held grids' rows are left out by the same reads. In both languages; the spec the site reads carries it (exported).
- **Five questions with their keys** (`questions_s1122.yaml`), computed by `expected_s1122.py` from the rows of `price_board_latest` and `price_board_spreads` recorded from the live set at 19:08 UTC (`tests/fixtures/session1122/board_reads.json`), without the tools: the highest day-ahead mean (NP15, 44.9349 USD/MWh on 23 October), the largest move in percent (SPP South, -96.6103 percent on 23 October), the widest spark spread (SP15, 18.1182 USD/MWh on 23 October), the lowest real-time mean (SPP South, 16.021 USD/MWh on 20 October) and the largest day-ahead less real time (ZP26, -12.2604 USD/MWh on 22 October). Each hub's newest day is its own: the keys say which.
- The site's tool, on the same rows, gives each key first and the same ranking, with no row of ISO-NE or NYISO (a test).

## What to review

1. `warehouse/chat/eval/questions_s1122.yaml`: the five questions as a reader would ask them.
2. Session 1113's run asks the thirty of session 320; these five wait for the next asking (chain 076, session 1133), their keys computed again that day.

## Checks

- `node --import ./scripts/alias-register.mjs scripts/test-ask-1122.mjs` (in `site/`): exit 0, 3 of 3.
- `python -m unittest tests.test_session1122` with the Ask tests (sessions 35 to 320, 1109 to 1112, 1115, 314): exit 0, 269 tests.
- Em dashes: 0.

## The landing

With sessions 1113 to 1122.

## Decisions made without you

1. **One tool over the derived tables, not over the page's file**: the board page draws `site/data/board.json`, built by the builder from the source tables, and the derived tables are built by the same builder family; the tool reads the tables the live set holds, so the chat and the grid pages agree by construction, and the board's file and the tables are the builder's to keep equal. Reversible.

## For Samuel's ruling

- None new.
