# Session 1422 report: the older blocks' render cases

24 October 2026, from about 10:55 to 11:35 UTC, on samueloldlaptop (the code machine, the old laptop), the fourth session of `queue/done/111-day-28-october-code-grid-tool-6.md`. Branch `wip/1422-grid`, cut from `wip/1421-grid` (sessions 1152 to 1421 stacked, not on main), worktree `C:\Users\lossa\Documents\erw-1422`. Code, tests and documents only (`runs/c077/brief.md`: no build, no server, no browser). Model spend USD 0. No warehouse data written, no Supabase write, no request to any publisher. Light anon reads of Supabase's REST API: 8 reads for one fixture (below), the key never printed or written. Production was not read (HTTP 402).

## Read these first

- **No site source changed.** Nothing a visitor sees moved. The work is in the render test, its stand-in, one fixture, five comment lines and the method note.
- **The inventory: 39 older blocks** (stood before chain 077) are drawn by `/grid`:
  - **Now view (4):** the sentence, the headline numbers, the mix in that hour, the source line.
  - **YourGrid (10):** the opening lines, Right now, Who runs this grid, Batteries, What it costs, What is being built, In the news, About ISO, Where the power comes from, How clean.
  - **Conditions (2):** Yesterday, the mix table.
  - **Reliability (1):** its three tables.
  - **The energy mix views on the Mix tab (11):** now, today so far, the hourly section, monthly mix since 2001, day, duck, year after year, records, stress, supply, forecasts.
  - **The Clean tab (6):** the last 24 hours, CAISO's break note, its source line, How clean and when, now ranked, monthly since 2018.
  - **The Exchange blocks (1).**
  - **The network component's server lines (1).**
  - **The page (3):** the header, the Ask panel, the decisions.
- **Before this session:** 17 of the 39 had cases of their own. 2 more had a case on one grid only: the mix view's now (ERCOT) and the server lines (inside `view_gravity`, ERCOT's Gravity tab). The other 20 were checked only inside their tab's case (`view_now`, `view_mix`, `view_clean`) or not at all (the Network tab has no view block).
- **Cases added: 64**, for 22 blocks (the 20, and more grids for the 2). `test-grid-render.mjs` now holds 181 cases, up from 117.
  - Each case is one grid kind where the block is drawn differently: ERCOT, CAISO, ISO-NE as the held grid, the Lower 48.
  - Each checks the block's name, its own figures by kind and count, its words, its held line, its anchors, its method links and its files.
  - A block drawn the same on every grid (the grid's name aside) has one case. 12 such repeats were left out.
- **How a block without a name on the page is found:** the stand-in names it, the page does not. `grid-render-standin.mjs` has `OLDER_MARKS` (attributes the page already draws: `data-now-sentence`, `data-grid-parts`, `data-grid-network`, `data-ask-side`) and `OLDER_COMPONENTS` (`ToolHeader`, `HeadlineRow`, `SourceLine`, `CaisoBreakNote`, `Decisions`). It also names a `Section` or `ToolSection` by its title and a `<section>` by its id.
  - Each such block is an overlay, `older_<name>`. It takes nothing from the blocks around it. Its own figures, ids, links, files and held line are those not inside a named panel within it.
  - The 117 cases of before hold unchanged except one, below.
- **The walk now reads a written block's markdown** (`dangerouslySetInnerHTML`, tags taken out). Before, "Who runs this grid" and "About ISO" drew no words.
- **One fixture is new: `site/scripts/fixtures/grid_mix_now.json`** (115 KB).
  - It holds real rows of two tables no fixture held, read once with the anon key: `eia930_generation_latest` for ERCOT, ISO-NE and the Lower 48 (1,378 rows), and `state_generation_mix_monthly` for the United States (2,484 rows, 2001-01 to 2026-08). CAISO's generation is not drawn (session 118), so it is not held.
  - With it, "today so far" and "monthly mix since 2001" draw their figures. The ERCOT case `mixview_now` counts 9 figures (8 `series`, 1 `series_esum`) where it counted 0. That is the one case of before that changed.
- **Pins annotated: 5**, in 5 files, one comment line each, as session 1404 did. No assertion changed.
  - `test_session54` → the server lines, Network tab, ERCOT.
  - `test_session133` (a loop of four words) → the forecasts, Lower 48.
  - `test_session157_page` → the forecasts, Lower 48.
  - `test_session266` → the sentence, ERCOT.
  - `test_session502` → the Ask panel, ERCOT.
  - A script found 239 `assertIn` pins that read these blocks' source files; 17 already carried a line. The rest hold markup or code that a render does not show, or a loop mixing words and code.
- **Mutation check:** I changed three words in `NowView.tsx`, `YourGrid.tsx` and `NetworkView.tsx`. The test exited 1 and named the 8 cases that read them. The files were restored with `git checkout`.

## What to review

No landing yet, and nothing a visitor sees changed.

1. Read `site/scripts/test-grid-render.mjs`: its header paragraph "Session 1422", then the block of cases under "session 1422 (chain 111)" at the end of `CASES`.
2. Read `site/scripts/grid-render-standin.mjs`: `OLDER_MARKS`, `OLDER_COMPONENTS`, `over()` and the walk's lines marked session 1422; then the fixture's `about`.
3. From `site/` (with `node_modules`), run `node --import ./scripts/alias-register.mjs --import ./scripts/tsx-register.mjs scripts/test-grid-render.mjs`. It should print "every case holds (181 cases)".
4. Run `git diff wip/1421-grid -- tests/ ':!tests/test_session1422.py'`: 5 comment lines and nothing else.
5. Read `docs/methods/grid_network.md`, the paragraph "Session 1422, each older block's render case." and its Decisions.
6. Screenshots: not taken, no build.

## Checks

- Precheck for session 1422: run by the orchestrator, exit 0.
- `test-grid-render.mjs`: exit 0, 181 of 181. Run before the changes (117, exit 0), after them, and again at the end some minutes later (no word depends on the clock). The mutation run exited 1, naming 8 cases.
- `node --check` on both scripts: exit 0. `npx eslint` on both: exit 0.
- `python -m unittest`, one module at a time, 61 modules, each exit 0, 691 tests:
  - every module that names the render test, the stand-in, `grid_network.md` or the fixtures folder, or walks `site/`;
  - the 5 annotated modules;
  - `test_session1404` (its comment check holds the 5 new lines);
  - `test_session1422` (new, 8 tests).
  - None was stopped for memory.
- Type check through the junction, once at the end: `npm run content`, `npx next typegen` and `npx tsc --noEmit -p .` exited 0 each. The junction was removed with `rmdir`; the main copy's `node_modules` is intact.
- Not run (the brief): the build, check-values, same-figures (no site source changed), screenshots.

## The landing

- None in this session: production answers HTTP 402 and this window runs no gate (chain 107's note). It lands with the chain's combined landing (`wip/1417-grid` and the sessions stacked on it). Pushed: `wip/1422-grid`.

## To finish

- At the landing, the gate's suite runs `tests.test_session1404` and `tests.test_session1422`. Each runs the render test (about 6 seconds).
- A later session that names one of these blocks on the page (a `data-grid-panel`) moves its case to the panel's name. The family check then asks for that panel's case.

## Decisions made without you

- **The older blocks are named in the test's walk, not on the page.** No markup moved. A `data-grid-panel` would make each a panel family with a file, anchor and method, which sessions 1420 and 1421 gave the blocks of figures.
- **A block drawn the same on every grid has one case.** This covers monthly since 2001, the last 24 hours, In the news on CAISO, the header on CAISO and ISO-NE, the Gravity tab's server lines on ISO-NE and the Lower 48, and the records on the Lower 48, which open on ERCOT's.
- **A held line is the block's own.** "license needed" inside a named panel belongs to that panel, not to the block around it.
- **Words are the block's headings and its own first sentence**, written by hand where the drawn text runs together (the headline numbers, the header). No word that holds the clock ("this page was drawn") is used.
- **The source reports' line stays as the fixtures draw it** ("could not be read"). No fixture holds the `catalogue` table, as in every case before.
- **The fixture holds every row of the two reads the blocks make** (the US monthly mix whole, 3 pages of at most 1,000 rows), not a sample, so the share columns are the page's own.
- **The ERCOT `mixview_now` case's count was raised to what is drawn** (0 to 9) and its other fields kept.
- **No pin is retired.** Retiring one is the owner's ruling.

## For Samuel's ruling

- Whether the older blocks should become named panels on the page (`data-grid-panel`, each with a file, anchor and method), as the blocks of figures did in sessions 1420 and 1421. Recommendation: only the blocks with figures (the sentence, the headline numbers, Where the power comes from, How clean, today so far, monthly since 2001); the written blocks stay as they are.

## Files

- New: `site/scripts/fixtures/grid_mix_now.json`, `tests/test_session1422.py`, this report.
- Changed:
  - `site/scripts/grid-render-standin.mjs` (overlays, markdown words, the fixture);
  - `site/scripts/test-grid-render.mjs` (64 cases, the ERCOT `mixview_now` count, the header);
  - `docs/methods/grid_network.md` (the session 1422 paragraph and its Decisions);
  - one comment line in each of `tests/test_session54.py`, `133`, `157_page`, `266` and `502`.
- On this machine only, in `runs/s1422/` of the worktree: the dump of every older block drawn, the pin finder and its list, the case writer, the fetch scripts and their raw answers, every test's output.
