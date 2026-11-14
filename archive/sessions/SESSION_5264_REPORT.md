# Session 5264: the Ask panel read other grids' hub spreads; the failing test's cause, fixed

Energy Research Warehouse (ERW). portable-laptop, window P3, 14 November 2026 (08:42 to 08:56 UTC), Fable, unattended. The second step of window P3's close-out. Branch `wip/5200-ask-close` (worktree `erw-p3-5264`), stacked on `wip/5200-ask-guard` at `d759cc739`. Nothing built, nothing landed, no warehouse data written. Model spend USD 0.00: no model call.

## Read these first

- **The test failed for a real fault, not a stale test.** `tests/test_session137.py` runs the Ask panel's own script, `site/scripts/test-ask-panel.mjs`. Its search of the price board for ERCOT's panel returned `caiso-th-sp15-gen-apnd-ercot-hb-hubavg-da`: CAISO's SP15 less ERCOT's hub average.
- **Root cause.** The panel's page tool returns a grid's rows and the rows of no grid, and took a row with no `grid` tag for a row of no grid. The board's hub spreads (session 1606, 6 November 2026) carry a scope and no grid tag. So Ask ERCOT could read eight rows it should not: CAISO's NP15 less SP15 and SPP's North less South (day-ahead and real time), and four spreads across two grids.
- **No held grid's figure was reachable this way.** The board holds hub spreads of ERCOT, CAISO and SPP only, all public.
- **Fixed in the panel, not in the board's file.** A hub spread is of the grids of its two hubs; a panel reads a row only when every grid it is of is its own. The board's file is the data machine's and is not touched.
- **The script passes: 9 of 9.** Run in this worktree on the main checkout's packages.

## What was done

- **Reproduced** on main's code in the worktree: `node --import ./scripts/eval-register.mjs scripts/test-ask-panel.mjs`, exit 1 at the search test's last line. In a worktree the Python test skips (no `node_modules`), which is why this window's own runs never showed it.
- **Measured on the board's file** (`site/data/board.json`, built 12 November 2026, 1,313 rows): 14 rows of the group `hubspread`, none with a grid tag. Six are ERCOT's own, four another grid's alone, four across two grids. No other untagged row begins with a grid's name.
- **The fix** (`site/lib/chat/panel.ts`):
  - `gridsOf(row)`: a tagged row is its grid's. A hub spread (the group, or a scope of "within" or "across") is of the grids of the two hubs its id is made of, each hub a row of the board that carries its grid. Any other untagged row is the grid its id begins with, as the board itself reads it for the license hold (`lib/board.ts` `gridOfRow`), or no grid's.
  - `boardRows(grid)`: a row is returned only when every grid it is of is the panel's. A spread whose hubs cannot be told is returned to no panel.
- **The test** (`site/scripts/test-ask-panel.mjs`): a ninth test, on made rows and on the file as it stands, for ERCOT, CAISO, SPP and PJM: each spread is read by the panel of its one grid and by no other, and cannot be asked for by its id. The first test no longer holds the rule as the tag alone. The search test also refuses another grid's hub as a spread's second hub.
- **`tests/test_session137.py`** asks for "9 tests pass".
- **`tests/test_session5264_ask.py`** (6 tests, no node, no model): the source, the count, and the two facts the fix leans on, read from the board's file.
- **Written down:** `docs/methods/ask_ercot.md` (a section in plain words) and `docs/reviews/ask-faults-2026-11-05.md` (the fault and its state).

## Before and after, for ERCOT's panel

| Rows of the board | Before | After |
|---|---:|---:|
| Readable by Ask ERCOT | 8 more than it should | ERCOT's and no grid's |
| ERCOT's own hub spreads | 6 | 6 |
| Another grid's own spread | 4 | 0 |
| A spread across two grids | 4 | 0 |
| The panel's script | 8 tests, 1 failing | 9 of 9 |

## Checks run

- `site/scripts/test-ask-panel.mjs`: exit 0, "9 tests pass" (the main checkout's packages through `eval-register.mjs`).
- Type check of `panel.ts` with the main checkout's compiler, nothing built or installed: exit 0, no error.
- `tests/test_session5264_ask.py`, `test_session137.py` and the six other test files that name the panel or the faults file: 94 passed, 4 skipped. The skips are the Node runs that need the site's packages in the worktree.
- No em or en dash in the files changed.
- Not run: the whole suite, a build, a lint (this window never builds). The gate's run of `tests/test_session137.py` is the first with the site's own packages.

## Model spend

- Estimate before: USD 0.00. Actual: USD 0.00.

## Decisions made without you

- **A spread across two grids is not ERCOT's own.** The panel answers for ERCOT only, and the spread with ERCOT's price states the other grid's price. It stays on the price board. The other reading, that a spread with an ERCOT leg is ERCOT's, is one line to change (`g.every` to `g.some` in `boardRows`).
- **The fix is in the panel, where the rule is.** A grid tag on the spreads in the board's builder would also close it, and is the data machine's file.
- **A spread whose hubs cannot be told is read by no panel.** It is some grid's; which cannot be said.
- **The Python test does not run the script in a worktree.** Run there, the site's loader writes build files a later change makes stale (the one failure of row 28's test count was such a file).

## For Samuel's ruling

- **Should the board's builder tag a hub spread with its grids** (`warehouse/derived/board_page.py`)? The panel no longer needs it. **Default: no change**; named for the data window.
- **A spread across grids in Ask ERCOT.** **Default: not read**, as above.
