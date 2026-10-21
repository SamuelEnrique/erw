# Session 382 report: the trader path, click by click

21 October 2026, about 01:50 to 03:10 UTC, unattended, on samueloldlaptop (the code machine), in the worktree `C:\Users\lossa\Documents\erw-382` on `wip/382-trader-path` (from `origin/main` at `dc4d5ba6`). Roadmap "This week", item 8, "First users ready" (`queue/next/014-night-20-october-code.md`, session 382). Model spend USD 0; no pull from any publisher; no warehouse data written.

## Read these first

- **The path is `docs/reviews/trader-path.md`**: sixteen steps for Pirro Prifti and Christian Mira through `/cost-of-power/seller` (6), `/cost-of-power/battery` (6) and `/board` (4), each with its address, the click, the figure to check with its key, and what a trader would ask that the page does not answer (listed, not built). 32 shots, one a step at 1280 and at 390 px, in `docs/brand/review-382/`, each looked at before its step was written. Not yet walked by its users: the feedback table at the end is empty.
- **One fault found and fixed under `site/`**: since 21 October 00:00 UTC every model figure of the generator page (`mr|` and `ms|` keys) read "license needed" on ERCOT, CAISO and SPP, not only on ISO-NE and NYISO: the license hold of 12 October's ruling holds `merchant_revenue_monthly` grid by grid, and `components/Num.tsx` could not see the grid in these keys (`iso=ercot`, an input, where it looked for `iso:ercot`, an entity). `lib/license.ts` gains `gridEntityOfKey`; `Num.tsx` falls back to it. Commit `c5c3b806`, test `tests/test_session382.py` (fails without the fix). Every page is in review, so no visitor saw it; it lands with the next landing.
- **Found, not fixed** (in the path's "What the walk found"): the board's ERCOT rows and top tiles stop on 15 October while its week table holds 20 October (the data machine's `board_page.py`); NYISO's and ISO-NE's prices are still on the board on 21 October because `data/board.json` was built on 20 October (the daily run's rebuild applies the hold); two board downloads answer 502 tonight (fixed by session 368 on `task/367-372`, not yet on main).
- **The On.Energy walkthrough is not written**: `docs/reviews/` holds no scope for it. The path's last section but one lists what a session needs to write it.

## What to review

- `docs/reviews/trader-path.md` on `wip/382-trader-path`: `https://github.com/SamuelEnrique/erw/blob/wip/382-trader-path/docs/reviews/trader-path.md`
- The shots: `https://github.com/SamuelEnrique/erw/tree/wip/382-trader-path/docs/brand/review-382`
- The fix: `site/components/Num.tsx`, `site/lib/license.ts`, `tests/test_session382.py` (commit `c5c3b806`).
- After the landing, on the site in the internal view: `/cost-of-power/seller` (revenue 59.85 USD/kW, debt coverage 0.67 where it read "license needed"), `/cost-of-power/seller?asset=battery`, `/cost-of-power/seller?iso=nyiso&asset=wind` (still held, as it should be).

## Checks

Every gate redirected to a file under `runs/chain_oct21/s382/`, never piped; the exit code read before the next step.

| Check | Exit | Result |
|---|---|---|
| `npm ci` in the worktree's `site/` | 0 | |
| `npm run build`, first three tries (before the fix) | 1, 1, 1 | the home page's required read (`entities`, `storageUnits`) met Supabase statement timeouts (57014) each time; the mutex was let go between tries |
| `npm run build`, fourth try (before the fix) | 0 | no timeout |
| `npm run build` at `c5c3b806` (with the fix) | 0 | one timeout, retried by the reader |
| `walk-382.mjs`, both widths, before the fix | 0 | 16 steps, 32 shots; the seller's model figures read "license needed": the fault |
| `walk-382.mjs`, both widths, after the fix | 0 | 16 steps, 32 shots; 137 same-origin links, 2 not 200 (the two downloads above) |
| `walk-382.mjs` steps 15 and 16 again (clicks corrected) | 0 | 4 shots |
| `check-values.mjs http://localhost:3382` (full run, the one asked for) | 1 | "check-values FAILED: The operation was aborted due to timeout": a request passed its 60 s limit; no value reported failed |
| `check-values.mjs`, `CHECK_VALUES_PAGES=/cost-of-power/seller` (restricted, 120 s a request) | 0 | 240 of 240 values match, 63 of them `mr|` and `ms|` keys the fix restored |
| `check-values.mjs`, `CHECK_VALUES_PAGES=/cost-of-power/battery` (three tries, 02:59, 03:03, 03:06) and with `/board` (two tries) | 1 | each "check-values FAILED: series: HTTP 500 ... statement timeout": the script's own read of `battery_stack_monthly` timed out; the page itself had read the same rows |
| `check-board-v4.mjs http://localhost:3382` (the board's figures against `data/board.json`) | 0 | 12 of 12 |
| `tests.test_session382` and `tests.test_session215` | 0 | 20 tests OK |
| The modules that read `Num.tsx` or `lib/license.ts` (207, 215, 248, 264, 281, 282, 315, 329, 382) | 0 | 92 tests OK |
| `tests.test_session382.TheHoldIsByGrid` with the fix stashed | 1 | errors, as it should |
| `duty.py beat` before each build | 1, 1, then 0 | the first two before `npm ci` timed out on Supabase; every beat before a build passed |

## Decisions made without you

1. **The fix was made**: the ruling of 12 October holds a table decided by grids row by row, session 264 wrote "every check key names its grid" for `mr|` and `ms|`, and session 264's report says `merchant_revenue_monthly` "is held by grid (ISO-NE, MISO, NYISO)". Reading `iso=` and `grid=` in a key is that rule as written, so no ruling was needed. It also reaches `/learn/problems` pages that carry `mr|` keys (`lib/problems.ts`): the same grids are held there, the others shown.
2. **The walk script and its records are kept beside the shots** (`docs/brand/review-382/walk-382.mjs`, `explore-382.mjs`, four JSON files), so the walk can be made again on the next build; nothing under `site/scripts/` was added.
3. **The full `check-values` run was not repeated** after its timeout, as the prompt asked for one run; the trader pages were checked with restricted runs instead, and the battery's could not complete tonight. The battery figures in the path are as the page showed them, each with its key; none was described without being seen.
4. **The board's stale ERCOT rows and the NYISO and ISO-NE rows were not touched**: both are `data/board.json`, written by the data machine's `warehouse/derived/board_page.py` from warehouse tables; rewriting it is warehouse work. The second ends with the next daily run.
5. **The link check reads one link at a time**: the first walk asked for 137 links at once and met statement timeouts; the second asked one by one.
6. **No landing**: the brief allows only `wip/382-trader-path`. The fix needs the next landing (its build, the full suite in a clean copy, the snapshot pair).

## For Samuel's ruling

- **On a phone the first figure is two and a half screens down** on the generator and the battery pages (2,140 to 2,375 px at 390 px wide, below the whole form; on the board 319 px). Options: (a) the summary and the headline above the form at phone width; (b) the form folded at phone width; (c) leave it.
- **Two figures for one thing**: at a hub other than the main one, the generator page's headline capture price (the capture file, 23.86 at West) and its spans table (the hub model, 23.85) differ by a cent, and the headline revenue there carries no check key. (a) One source for both; (b) a key on the hub revenue only; (c) leave it.
- **The On.Energy walkthrough**: who walks it, on which pages and grids, and how an outside reader sees pages that are all in review (the internal view for a person outside the project, or the pages set live). The list is in `docs/reviews/trader-path.md`.
- **The traders' walk itself**: when Pirro Prifti and Christian Mira walk the path, and how they see it (the same question of the internal view).
- **The board's ERCOT tiles** (for the data machine, perhaps no ruling): the top block's ERCOT day-ahead is 43.95 on 15 October while the week table says 30.98 on 20 October.

## Files

- `docs/reviews/trader-path.md` (new); `docs/brand/review-382/` (32 shots, `walk-382.mjs`, `explore-382.mjs`, four walk records).
- `site/components/Num.tsx`, `site/lib/license.ts` (the fix); `tests/test_session382.py` (new).
- This report.
