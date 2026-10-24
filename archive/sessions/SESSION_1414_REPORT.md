# Session 1414 report: the Clean tab's large tables keyed whole

24 October 2026, on samueloldlaptop (the code machine, the old laptop), the fifth session of `queue/done/107-day-27-october-code-grid-tool-5.md`. Branch `wip/1414-grid`, cut from `wip/1413-grid` (sessions 1152 to 1413 stacked, not on main), worktree `C:\Users\lossa\Documents\erw-1414`. Code, tests and documents only (`runs/c077/brief.md`: no build, no server, no browser). Model spend USD 0. No warehouse data written, no Supabase write, no request to any publisher; light anon reads of Supabase's REST API (one same-figures walk, the answers held in memory).

## Read these first

- **A python run was stopped by the harness for low memory, not restarted (the brief).** Of the 129 modules that read a changed file or walk `site/lib`, `site/components` or the method notes, 75 ran, every one exit 0 (1166, 1167, 1168, 1403, 1404, 1413 and 133 among them); the loop was reaped at the 76th. The 54 not run are listed under "To finish". `tests.test_session1414` (new) ran alone afterwards: exit 0.
- **The three large tables of "How clean, and when" are keyed whole** (`site/components/mix/views.tsx` `CleanView`), for each grid not held:
  - "<grid>: an annual clean purchase against the hours": every purchase, shape, energy and hours, `fmt|n1|file|clean/<grid>.json|years.<Y>.match_<shape>_<p>_<energy|hours>_pct`.
  - "The cleanest hours by month": the share in the cleanest and the dirtiest hour, `fmt|n1|filecalc|clean_day_max|clean/<grid>.json|<YYYY-MM>` and `clean_day_min` (session 1413's kind; the expression that stood in the view moved as it stood into `lib/mixViewCalc.ts` `cleanDayHeld`, `cleanDayMax`, `cleanDayMin`); the month's share, `file|...|months.<M>.carbon_free_share_pct`. "The four cleanest hours" stay words.
  - "Moving a flat load into the cleanest hours", every year held: carbon (n1), each shift's change (sn1), days (n0), cost (n2), each shift's cost change (sn1), days priced (n0). A year without a hub price keeps its words, unkeyed.
- **Keys added, one grid at a time (default year):** ERCOT 118 (18 purchase, 36 by month, 64 by year), CAISO 102, PJM 86, SPP 86, ISO-NE, MISO, NYISO 0 (held). Over the seven grids drawn one at a time: 543 keys, 392 more than the 151 before.
- **The checkers' time:** `test-grid-file-keys.mjs` 3.23 to 3.28 s on the tree before (three runs), 3.83 to 3.96 s after (four runs): about 0.6 s more. check-values on its eight Clean pages: 685 keys in place of 175, and 78 row sets of `clean_energy_summary` read for the file-against-table lines in place of 12 (one light read a grid's year or month; `filecalc|` reads none).
- **Held grids:** no held cell keyed (session 1167's `lib/gridHeld.ts`); the node test asserts no key of ISO-NE, MISO or NYISO on any grid's drawing, and that a held grid's own tables carry none.
- **Each of the tab's five tables has a file, an anchor and a method line** (the headline two too: the file test holds every figure of a block to its files, and the tab is one block, `data-mix="clean"`):
  - Files: `erw_grid_clean_all_shares_<year>`, `erw_grid_clean_<grid>_purchase_<year>`, `_months_<year>`, `_shift`, `erw_grid_clean_all_grids_<year>`; the header names the grids held.
  - Anchors: `CLEAN_TABLE_ANCHOR` in `lib/gridAnchors.ts` (`#clean`, the id the first block had, `#clean-purchase`, `#clean-months`, `#clean-shift`, `#clean-grids`; a second grid `-<grid>`), outside `GRID_ANCHOR`, as 1402 to 1413.
  - Method: "Method: the Clean tab's tables, keyed", `METHOD_CLEAN_TABLES`, a new subsection of `docs/methods/generation_mix_hourly.md`'s chain 107 section (heading id checked by render).
  - Failed-read guard: not applicable (the files are built into the page, `lib/mixdata.ts`).
- **No figure moved.** `same-figures.mjs` on `/grid?grid=ercot&view=clean`, `caiso`, `isone`, `ercot&year=2021`, `caiso&year=2025`: 398 figures compared, exit 1 by additions only: on every page the list before is kept whole and in order in the list after, the 437 added are all `file|clean/` or `filecalc|clean_day_` keys, held figures, panels and errors identical; ISO-NE "same". A one-off drawing of the view by both trees (13 choices: each grid, two and four grids, three years, a held grid first): 3,325 table cells all equal; the text differs only by the new file and method lines.

## What to review

After the landing (none yet; below), on production:

1. Open `https://erw-flame.vercel.app/internal/open`, paste the token, press **Open the internal view**.
2. Open `https://erw-flame.vercel.app/grid?grid=ercot&view=clean`. Under "ERCOT: an annual clean purchase against the hours, 2024" every percent is dotted; hover one: `clean_energy_summary, iso:ercot: years.2024.match_mix_100_energy_pct (the committed file site/data/clean/ercot.json)`. Under the table: the download line and "Method: the Clean tab's tables, keyed"; click it to open the note's section.
3. Same page, "The cleanest hours by month": the cleanest and dirtiest shares dotted (hover names `lib/mixViewCalc.ts cleanDayMax`), the month's share dotted, the hours not.
4. Same page, "ERCOT: moving a flat load into the cleanest hours": every figure of every year dotted.
5. Open `https://erw-flame.vercel.app/grid?grid=isone&view=clean`: ISO-NE's blocks read "license needed", nothing of ISO-NE dotted; the seven grids table keeps CAISO, ERCOT, PJM, SPP dotted.
6. Download one file (e.g. `erw_grid_clean_ercot_shift.csv`): its header, a row a year.
7. View source and search `clean_day_max` and `clean-shift`.
8. Screenshots: not taken, no build.

## Checks

- Precheck for session 1414: run by the orchestrator, exit 0.
- Node, through the alias and tsx loaders, one at a time, exit 0 each: `test-grid-file-keys.mjs` (14 of 14; its held clean test extended in place), `test-mix-view-calc.mjs` (11 of 11; two tests extended), `test-grid-files.mjs` (135 cases; two pages, one entry extended, one check added), `test-grid-render.mjs` (85 cases; three `mixview_clean` cases), `test-clean-week.mjs` (9 of 9; the two drawings now at one time, below), `test-grid-methods`, `test-grid-addresses`, `test-grid-held`, `test-grid-failed-reads`, `test-grid-stress`, `test-hub-price`, `test-ercot-notices`, `test-mix`, `test-grid-keys`; `node scripts/test-check-values-run.mjs`.
- `node --check` on `check-filecalc`, `check-values`, `check-methods` and the four changed tests: exit 0 each.
- check-methods' own `figures()` and `named()` over every key of the view (four grids, five years) against `generation_mix_hourly.md`: 18 figures, 0 not named.
- `python -m unittest`, one module at a time: 75 of 129 exit 0, then reaped (above); `tests.test_session1414` (new, 6 tests) exit 0.
- `same-figures.mjs`: 5 addresses, exit 1 by additions only (above). The temporary worktree of `28a8e33f` and its junction removed.
- Type check through the junction: `npm run content` exit 0, `npx next typegen` exit 0, `npx tsc --noEmit -p .` exit 0; the junction removed with `rmdir`, the main copy's `node_modules` intact.
- Not run (the brief): build, check-values against a page, check-routes, check-links, screenshots.

## The landing

- None in this session. It lands with the chain's combined landing (`wip/1408-grid` and the sessions stacked on it, not on main). Pushed: `wip/1414-grid`.

## To finish

- The 54 python modules not run, one at a time, before the landing: test_session190_replication, 194, 195, 196, 199, 204, 215, 232, 233, 236, 238, 241a, 241b, 241c, 242, 258, 260, 262, 266, 267, 274, 299, 300, 301, 303, 306, 310, 314, 315, 317, 324, 332, 355, 371, 381, 408, 411, 412, 416, 473, 474, 502, 51, 53, 57, 58, 580, 582, 583, 65, 70, 78, 89_miso_pause, 94 (the orchestrator's whole suite covers them).
- At the landing: the build; check-values on `/grid,/network` (the eight Clean pages gain about 510 keys and 66 light reads; expect "same" lines for the `file|clean/` keys and "the committed file" for `filecalc|clean_day_`); floors rewritten from a passing restricted run; `check-methods.mjs --values <the run> --write`; check-links (the fragment `#the-clean-tabs-tables-keyed-whole-session-1414` and the anchors); the snapshots before and after, every difference listed (expected, on the Clean tab only: dotted figures, five download lines and five method lines, the new ids; no word or number moves); screenshots at 1280 and 390 under `docs/brand/review-1414/`.

## Decisions made without you

- **The cleanest and dirtiest hour are `filecalc|`**, not a `file|` key at the hour the page picked: the figure is the page's arithmetic on the day.
- **The headline tables gained files, anchors and method lines too**, though their keys are session 1166's: the file test needs every figure of the block filed.
- **"Months held" ("11 of 12") stays words**, as session 1166 left it: two figures in a cell would be filed as two bare numbers.
- **A method line of its own**, beside 1413's: `tests/test_session1413.py` counts six `<ViewMethod />`, and these tables are mostly file values.
- **Node tests extended in place**: tests 1168 and 1413 count their tests.
- **`test-clean-week.mjs`**: its comparison of the view drawn with and without the week now draws both at one fixed `Date.now`, because the new files name the drawing time and two drawings a few ms apart differed only by it; the assertion stands as it was.
- **The python run reaped for memory was not restarted** (the brief); the new test module was run alone.

## For Samuel's ruling

- The method line "Method: the Clean tab's tables, keyed" and a download line under each of the five tables. Recommendation: keep; every keyed table of the tool has both.
- check-values gains 66 light reads a run for the Clean pages' file-against-table lines. Recommendation: keep (ruling 4's lines); or read the clean summary once per grid in a later pass.

## Files

- New: `tests/test_session1414.py`, this report.
- Changed: `site/components/mix/views.tsx` (CleanView keyed, files, anchors, method lines), `site/lib/mixViewCalc.ts` (`cleanDayHeld`, `cleanDayMax`, `cleanDayMin`, two FILECALC entries, the clean source), `site/lib/gridAnchors.ts` (`CLEAN_TABLE_ANCHOR`, `cleanTableAnchor`, `METHOD_CLEAN_TABLES`), `site/scripts/check-filecalc.mjs` (two functions), `site/scripts/test-grid-file-keys.mjs`, `site/scripts/test-mix-view-calc.mjs`, `site/scripts/test-grid-files.mjs`, `site/scripts/test-grid-render.mjs`, `site/scripts/test-clean-week.mjs`, `docs/methods/generation_mix_hourly.md` (subsection "The Clean tab's tables, keyed whole (session 1414)" with Decisions).
- On this machine only, in `runs/s1414/` of the worktree: every test's output, the same-figures lists, the one-off scripts and their drawings.
