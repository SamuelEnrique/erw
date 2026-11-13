# Landing requests: the old laptop's second window (chain 165, the price board)

Energy Research Warehouse (ERW). Written by chain 165 (`queue/done/165-day-6-november-oldlaptop-window2-price-board.md`), which never builds the site and never lands: the old laptop's memory holds one build, and its first window owns it. The desktop's second window (chain 164, its landing service) lands each row below through `scripts/land_check.py` with the task and port given, marks the row landed with the commit, and deletes the branch and its ancestors of this chain once they are ancestors of main.

| # | Branch | Head | Task | Port | Requested (UTC) | Tests on this machine | State |
|---:|---|---|---|---:|---|---|---|
| 1 | `wip/1605-board` | `19fd5c0c0` | `1600-1605-board` | 3600 | 2026-11-06 | the board's and the page's test files: 127 run, 1 skipped, 1 failure (below); the whole suite not run to the end (below) | landed: `0aa1dbd02` (task/1600-1610-board, the desktop's session 3008 and its merge, checks passed run 42218427806) |
| 2 | `wip/1610-board` | `edd783ea6` | `1600-1610-board` | 3600 | 2026-11-06 | the board's and the page's test files: 134 run, 1 skipped, 1 failure (the same, below); the whole suite not run here | landed: `0aa1dbd02` (task/1600-1610-board, the desktop's session 3008 and its merge, checks passed run 42218427806) |
| 3 | `wip/1615-board` | `93600319f` | `1600-1615-board` | 3600 | 2026-11-06 | the board's and the page's test files: 151 run, 1 skipped, 1 failure (the same, below); the whole suite not run here | landed at 6331a953a (row 8's branch, merged with main; chain 164, session 3016) |
| 4 | `wip/1619-board` | `643726a99` | `1600-1619-board` | 3600 | 2026-11-06 | every test file naming the board's code (40 files): 330 run, 1 failure (the same, below); this chain's 57 tests passed; the whole suite not run here | landed at 6331a953a (row 8's branch, merged with main; chain 164, session 3016) |
| 5 | `wip/1623-board` | `56766d6f1` | `1600-1623-board` | 3600 | 2026-11-06 | every test file naming the board's code and this chain's 63 tests (41 files): 334 run, 1 failure (the same, below); the whole suite not run here | landed at 6331a953a (row 8's branch, merged with main; chain 164, session 3016) |
| 6 | `wip/1627-board` | `eb471805b` | `1600-1627-board` | 3600 | 2026-11-06 | every test file naming the board's code and every `test_board_16*` (336 run, 1 failure, the same, below); the whole suite not run here | landed at 6331a953a (row 8's branch, merged with main; chain 164, session 3016) |
| 7 | `wip/1633-board` | `a60601ae6` | `1600-1633-board` | 3600 | 2026-11-06 | every test file naming the board's code and every `test_board_16*` (338 run, 1 failure, the same, below); the whole suite not run here | landed at 6331a953a (row 8's branch, merged with main; chain 164, session 3016) |
| 8 | `wip/1639-board` | `74e72ae26` | `1611-1639-board` | 3600 | 2026-11-06 | merged with `origin/main` after the landing of rows 1 and 2 (the conflicts in `tests/test_session166.py` and `tests/test_session247.py` resolved, the builder's `held = ls.held_grids()` lines four as main's `test_session207` asks); every test file naming the board's code and every `test_board_16*`: 338 run, 1 failure (the same, below); the whole suite not run here | landed at 6331a953a (row 8's branch, merged with main; chain 164, session 3016) |
| 9 | `wip/1905-revert` | `77e8916a0` | `1944-revert` | 3944 | 2026-11-13 | the gate's suite failed for memory twice (session 1916 at `2e599ff77`: 6 failures, 3 errors; session 1930 at `77e8916a0`: 8 failures, 2 errors, every one a `MemoryError`, a commitment-limit exit or a PowerShell timeout); the failed modules run alone at `77e8916a0` (1898, 1315, 157_refresh, 3701, 381, 422, 582): 76 run, OK, 2 skipped (`runs/s1944/failed_modules.out`) | landed at `3a82aebe4` (session 4000, chain 228, desktop window 2: `origin/main` merged as `428a0664f`; its gate on the desktop's 16 GB: the suite 8,633 tests OK, 382 skipped; build, check-routes, check-cross-checks (92) and check-csp (97 pages) pass; check-values' one failure main's own `/digest` floor (0 new, `runs/c147/cv_diff.py`); task/1944-revert, run 43406357288; snapshots before and after) |
| 10 | `wip/1973-periodicals` | `a898be5be` | `1973-periodicals` | 3973 | 2026-11-13 | the touched test files: `tests/test_periodicals_1973.py` (41) with `test_periodicals`, `test_session135`, `test_session150`, `test_session176`, `test_session177`, `test_session181`, `test_session192`, `test_session267`, `test_session402`, `test_session470`, `test_session802`, `test_session804`, `test_session805`, `test_session806`, `test_session810`, `test_session1882`, `test_session1894`, `test_session1895`, `test_session1907`, `test_session1908`, `test_session2206`: OK; `site/scripts/test-digest-numbers.mjs` 16 passed; `npm run build` exit 0 at `ce708f7c1` in the worktree; the whole suite not run here (this machine's rule). Merges with `origin/main` at `97c501a77` with no conflict (`git merge-tree`) | landed at `f06f7f3d2` (the branch to `a898be5be`, rows 79 to 145; in part before at `5fe21d6de` and `71f8442ed`; sessions 4007 and 4008, chain 228, desktop window 2: land-c (`1ae01929e`: window 3's row 6, window 4's row 4 to `7e30eed2e`, the old laptop's row 10 to `a898be5be`) gated in the blackout, then land-d (`15c54b483`: land-c with window 4's `000cce004`); every step of `land_check.py` passed on both (the suite 8,822 tests OK); pushed at 16:15 as task/4008-landing, run 43460893494; snapshots before and after, 0 differences) |
| 11 | `wip/3457-periodicals` | `66e8ea25a` | `3457-periodicals` | 3457 | 2026-11-13 | the touched test files: `tests/test_periodicals_3457.py` with every test file naming the changed modules (session 3457: the 13 naming `daily_chart`, 381 passed, 1 skipped; session 3458: the 62 naming `brief`, `roundup` or `digest.ts`, 1,196 passed, 20 skipped; session 3459: the same 62, 1,206 passed; session 3460: the same 62, 1,212 passed; session 3461: the 65 naming `brief`, `roundup`, `digest.ts` or `daily_chart`, 1,238 passed; session 3462: the same 65, 1,243 passed; session 3463: the same 65, 1,247 passed; session 3464: the same 65, 1,251 passed; session 3465: the 65 naming `brief`, `roundup`, `digest.ts`, `daily_chart` or `email_digest`, 1,256 passed, 20 skipped; session 3466, on the merge with `origin/main` at `d62c4a31e`: the same 65, 1,256 passed, and the 7 naming `digest.ts`, 238 passed; session 3467: the 66 naming the changed modules, 1,261 passed; session 3469: the 72 naming `brief`, `roundup`, `digest.ts`, `daily_chart`, `email_digest` or `topics`, 1,378 passed; session 3473: the same 72, 1,382 passed, 20 skipped); `site/scripts/test-digest-numbers.mjs` 17 passed; `npm run build` not run yet (MemFree under 2.5 GB); the whole suite not run here (this machine's rule) | requested; **landed in part at `f71fda27e`, to `e547f598f`** (session 4011, chain 228, desktop window 2: `wip/w2-land-g`, `896229157`; every step of `land_check.py` passed; task/4011-landing, run 43490914368; snapshots before and after, 0 differences); the newer head is in the desk's next gate (session 4012); the rest requested at head `66e8ea25a` (chains 252 and 254: rows 161 to 174 of `docs/reviews/periodicals-faults-2026-11-05.md`, on the merge with main at `1f45e5525`) |

## Row 1: what it holds

Sessions 1600 to 1605, stacked: `wip/1600-board` to `wip/1604-board` are ancestors of `wip/1605-board`.

- The audit, `docs/reviews/board-audit-2026-11-06.md` (29 gaps, their states).
- `warehouse/derived/board_page.py`: ERCOT's load zones; the zone history read; every power row's interval (`basis`); ERCOT's node basis by class with a link to `/cost-of-power`; ERCOT's real-time adders; one capacity placeholder an auction; a group "Natural gas in storage and LNG exports"; three more gas hubs named; North Dakota's first purchase price; US gasoline of all grades; a group "Delivery charges and transmission peaks" (ERCOT's coincident peaks, the Texas delivery charges' placeholder); RGGI, ISO-NE's reserves and RINs as "licensed source needed" with the publisher named.
- `site/lib/board.ts` (`basis`, `link`, `nameTitle`), `site/components/board/BoardView.tsx` (the hover through `nameTitle`, the row's link), `site/app/board/page.tsx` (ten more tables in `TABLES`). **Not built on this machine**: the gate's build is the first.
- `site/data/board.json` is not changed: the new rows appear on the first data machine run of `page_keep.py board` after the landing. That run reads two more large tables (`ercot_zone_prices_history`, about 560 MB here, and `iso_zone_prices_history`, about 360 MB).
- Tests: `tests/test_board_1601.py` to `test_board_1604.py` with their fixtures; `tests/test_session328.py`'s count of the page's tables, 19 to 29.

## Row 2: what it adds to row 1

Sessions 1606 to 1609, stacked on row 1 (`wip/1606-board` to `wip/1609-board` are its ancestors):

- A group "Hub spreads, within and across grids" (seven pairs, both markets); the spark spread at every public hub behind a Show filter; the stated heat rates beside EIA's fleet averages where `eia_heat_rates_annual` is on the machine.
- Cracks by product; a group "Gas spreads, monthly" from the World Bank; the regional basis and LNG netback placeholders.
- A fifth move, YTD (`moves.ytd`), a fifth column on the page; a stale row's moves blank with its status (`shownMove`, used by `check-board.mjs` and `check-board-v4.mjs` too).
- The trend line over 90 days (daily), a year (weekly), three years (monthly, quarterly), up to 90 points; the column named "Trend".
- `tests/test_session132.py` and `tests/test_session1139.py` take a file built before YTD as it is (both are daily-run board tests); `test_session132`'s trend cap 30 to 90.
- More TypeScript not built here: `site/lib/board.ts` (`MoveKey`, `shownMove`, the moves typed partial, `inputsWords` for a product crack, `hubspread` among the power groups), `BoardView.tsx` (the column count from `MOVES`).

## Row 3: what it adds to row 2

Sessions 1611 to 1614 (`wip/1611-board` to `wip/1614-board` are its ancestors):

- The power group's column "Day's high / low" (`ext`: the latest day's highest and lowest hour with their local times, and under them the last 7 and 30 days' peak hour and the hours above 100, 250 and 1,000 USD/MWh), a group flag `extremes`.
- A column "12-month avg" on every group (`avg365`: the trailing twelve-month mean and the latest less it).
- The rows' CSV widened to the board as shown; two new routes, `/board/rows/python` and `/board/rows/stata` (dynamic, like `/api/download`'s readers), linked from the footer.
- `ext` and `avg365` among the figures `holdRows` drops from a held grid's rows. `site/scripts/check-board.mjs` expects every new number.

## Row 4: what it adds to row 3

Sessions 1616 to 1618 (`wip/1616-board` to `wip/1618-board` are its ancestors):

- `boardFileChecks` in `site/lib/board.ts` and `check-board.mjs --file`: the file's own checks, with no server; `check-board.mjs` runs them first on a served page too.
- The method note's part by part at its head (`docs/methods/price_board.md`).
- Three older tests that this chain's changes broke, fixed: `tests/test_session207.py` (by renaming the two new `held =` lines), `tests/test_session166.py` and `tests/test_session247.py` (their expectations follow the chain's intended changes).
- `tests/test_board_1618.py`: the file's budget (2.5 MB as written, 400 KB compressed), with this chain's figures about 1.54 MB.

## Row 5: what it adds to row 4

Sessions 1620 to 1623: every row states its step (`STEP_BASIS`), a monthly row's extremes cell says "monthly", the adder's extremes; the keys the Digest and Ask read checked unchanged; the chain's note (`docs/state/note_2026-11-07_oldlaptop_window2.md`). Once row 5 is an ancestor of main, `wip/1600-board` to `wip/1623-board` can be deleted on origin.

## Row 6: what it adds to row 5

Chain 167's sessions 1624 to 1626: `cp4_price` in the builder, a row of the cost group, the hub average's 15-minute real-time price at each 4CP interval (read from `ercot_all_hub_prices_history` and `iso_rtm_hub_prices`, each filtered to the hub as it streams); `tests/test_session247.py`'s list of whole-table readers takes it. Once row 6 is an ancestor of main, `wip/1600-board` to `wip/1627-board` can be deleted on origin.

## Row 7: what it adds to row 6

Chain 167's sessions 1628 to 1632: the rows' CSV carries the week's and month's peak and hours above 100, 250 and 1,000 (eight columns inside the figures' span); `holdRows` drops `basis` and `heat_ref`, and the builder writes a row with no value without them, so a row with no figure prints its words and no digit; `boardFileChecks` catches a kept `basis`. Once row 7 is an ancestor of main, `wip/1600-board` to `wip/1633-board` can be deleted on origin.


## Row 9: what it holds (chain 224, session 1944)

Chain 219's session 1905, merged with main three times since: the grids view's public columns held again until the owner rules (datacenter faults row 4, state `ruling`). Five files against main: `site/components/Num.tsx` and `site/scripts/check-holds.mjs` (the held columns back), `tests/test_session1898.py`, `docs/reviews/lab-path.md`, `docs/reviews/five-tools-read-2026-11-11.md`.

The old laptop does not try this gate a third time: two chains' windows (220 and 222) were lost during or just after it, with about 0.6 to 1.0 GB of memory free. The lander: `origin/main` merged into the branch, then `python scripts/land_check.py --ref <the merge> --task 1944-revert --port 3944 --keep-worktree`, each printed command its own command with its exit read, the snapshots before and after, not between 14:00 and 16:15 UTC. Once it is an ancestor of main, `wip/1905-revert` can be deleted on origin, and the old laptop removes its worktrees `erw-1905` and `erw-land-77e8916a`.

Session 1972 (chain 228) removed `erw-land-77e8916a` (a gate leftover at the branch's head, saved on origin); `erw-1905` stays until the landing.

## Row 10: what it holds (chain 228, sessions 1973 to 1996)

The Daily Digest and the Weekly Roundup, read as a reader: `docs/reviews/periodicals-faults-2026-11-05.md` rows 79 to 99, each fixed with a test. Cut from `origin/main` at `ed7dc1779`; independent of row 9 (no file in common).

- `warehouse/news/brief.py`: the opening names the hub move it passed over; the market row and "What moved most" never rank a 0.0% move; EIA's closes dated; "Storage dispatched"; outlet names; no repeated parties; the policy line; the money style on printed titles; the subject and the first line; mover lines kept by the repeat checks.
- `warehouse/news/roundup.py`: a grid held for license prints no mean and its real-time table is not read (row 93: W44 and W45 printed NYISO's and ISO-NE's means); the subject without an outlet figure; the deal's outlet; the stand-in at the bar; the benchmark's close in a limitation.
- `warehouse/analysis/findings/findings_scanner.py` and `daily_chart.py`: the record until now (row 87); the chart's tie to a story (row 88). `scripts/check_digest.py` and `site/scripts/digest-figures.mjs` trace the new `held_record`.
- `site/lib/digest.ts` (`holdRoundupGrids`, the policy line's parser) and `site/lib/markdown.ts` (`renderRoundup`): the stored W44 and W45 pages hold the held cells. Read on the local build at 1280 and 390 (`runs/s1997/shots/`, not in git): W45's NYISO and ISO-NE cells read "license needed", neither figure is in the page's HTML, no horizontal scroll at 390.
- Docs: the faults file; `docs/methods/automated_analysis_scanner.md`; `docs/methods/periodicals.md`; two internal notes, `digest_scoring.md` and `roundup_selection.md` (`INTERNAL_METHODS` in `site/scripts/build-content.mjs`; `/data/methods/digest_scoring` answers 404 on the build).
- Tests whose expectation changed with the rule they pinned: `tests/test_periodicals.py` (rows 84 and 95), `tests/test_session2206.py` (row 90), `tests/test_session1907.py` (row 97).
- What a reader of a live page sees: nothing until the next Digest and Roundup are written (no live page; every page is in review), except the `/roundup` pages of W44 and W45, which hold two cells each. No warehouse table is changed.

## Known on this machine

- **`tests.test_session1116`, its node check 5** ("none of the top twelve is stale") fails on the committed `board.json` (ERCOT's day-ahead row at 30 October, built 5 November): **it fails the same way on `origin/main`**, so it is the file's state, not the branch. The gate's run may show it.
- **The whole suite** (`python -m unittest discover -s tests`) was stopped by the harness for low memory before it printed a result, and was not started again unattended. The gate's suite is the first whole run.

## Row 11: what it holds (chains 252 and 254, sessions 3457 onward)

The Daily Digest of 13 November 2026 as stored, read as a reader against a dry run of the same hour on main: rows 151 onward of `docs/reviews/periodicals-faults-2026-11-05.md`, each fixed with a test in `tests/test_periodicals_3457.py`. Cut from `origin/main` at `42bb28b1a`, after row 10 landed. Since session 3458 it changes one site file, `site/lib/digest.ts`.

- `warehouse/analysis/findings/daily_chart.py`: a month alone (a watch card's axis, "2026-08") read as its first day, and the section's lines written before its picture and record (row 151).
- `warehouse/news/brief.py`, `roundup.py`, `site/lib/digest.ts`: the Digest's real-time line in row 71's form, the variable on the Tables line, `lib/digest.ts` reading both forms (row 152). A site file: the gate's build is its first if this machine's memory never allows one.
- `warehouse/news/brief.py`: "oil major" kept by the voice's cleaner (row 153); an oil or gas market title under a power tag is that fuel's (row 154); the figures line leaves out a figure the why line gives (row 155) and a sum with no unit (row 156).
- `warehouse/news/roundup.py` (`phrase_back`, read by both subjects) and `brief.py`: a subject cut inside a phrase goes back to before it (row 157); one capacity in two units is one figure (row 158; `tests/fixtures/periodicals/why_lines.json`'s Dominion item follows).
- `warehouse/news/brief.py` and `daily_chart.py`: a gap in the hourly demand table is said to be one, not the window's (row 159); the no-chart line says why with no pointer to the run log (row 160).
- `warehouse/news/roundup.py`: the five's deal of the week is always in the Deals table (row 161); the five's datacenter load names its developer and a country other than the US, and one load "names" (row 162; row 118's pin in `tests/test_periodicals_1973.py` follows).
- `docs/methods/digest_scoring.md` and `roundup_selection.md` carry rows 151 to 164; `brief.py`: a gas forwards or LNG market title is gas's (row 163); a policy action an earlier issue printed is left out (row 164).
- `roundup.py` and `brief.py`: a subject's figure goes with its quantity words, a capacity with its "of", a percent is a figure (row 165); a fuel market title is oil's (row 166); the figures line opens with a capital (row 167).
- `brief.py`, `roundup.py`, `email_digest.py`: an agency's long name is its initials for one topic (row 168); a scale word reads the cluster's MW (row 169); "Also in deals:", and the also line's readers read capitals (row 170; `tests/test_session577.py` and `test_session801.py` follow).
- `warehouse/news/email_digest.py`: the plain-text email names the chart once (row 171).
- `warehouse/news/email_digest.py` and `topics.py`: the subscribers' topic filter reads the v2 issues and a sector in capitals (row 172: it read no story of a v2 issue); an LNG also line no longer takes its item's why line in the email (row 170, widened).
- `warehouse/news/roundup.py` (chain 254): Next week's empty line speaks of the week ahead (row 173); a story naming a benchmark is given its own day's close (row 174).
