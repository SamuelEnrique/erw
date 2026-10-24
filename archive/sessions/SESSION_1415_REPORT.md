# Session 1415 report: the Clean tab's emissions blocks

24 October 2026, on samueloldlaptop (the code machine, the old laptop), the sixth session of `queue/done/107-day-27-october-code-grid-tool-5.md`. Branch `wip/1415-grid`, cut from `wip/1414-grid` (sessions 1152 to 1414 stacked, not on main), worktree `C:\Users\lossa\Documents\erw-1415`. Code, tests and documents only (`runs/c077/brief.md`: no build, no server, no browser). Model spend USD 0. No warehouse data written, no Supabase write, no request to any publisher; light anon reads of Supabase's REST API (one read of `carbon_intensity_monthly` for a committed fixture, one same-figures walk, the answers held in memory).

## Read these first

- **What was found** (`site/components/grid/Emissions.tsx`, the Clean tab's three blocks): "Carbon intensity now, ranked" had its 14 keys and "Monthly since 2018" its 14, but neither was a named panel, neither had a file, an anchor or a method link, and the monthly chart's note wrote two figures without a key ("Left out of this chart: 13 months", "7,869 hours in a row"). No block asked `lib/gridHeld.ts`. Both charts already answer a hover with the period and each ISO's value in kg CO2/MWh (`components/TimeChart.tsx`'s card: the hour start in UTC on the minute axis, the UTC month on `x="month"`; and its Chart | Table toggle): nothing to add there.
- **Now:**
  - `grid_carbonrank_<grid>` (anchor `#carbon-now`): the 14 keys as they were, each with its table, entity, variable and hour on hover; its file `erw_grid_carbonrank_<grid>.csv`; the line "Method: the Clean tab's carbon blocks, keyed".
  - `grid_carbonmonth_<grid>` (anchor `#carbon-monthly`): the 14 keys as they were, the month on hover; the note's two figures keyed on the committed `site/data/carbon_left_out.json`: `fmt|n0|filecalc|carbon_left_out_n|carbon_left_out.json|intensity_generation` (a new function of session 1413's kind, `lib/mixViewCalc.ts leftOutCount`, the length of the list the note writes) and `fmt|n0|file|carbon_left_out.json|hydro_gap.hours`; its file `erw_grid_carbonmonth_<grid>.csv` (the two figures as `Figure:` header lines); the same method line.
  - Held ISOs (all three blocks, the last 24 hours included): `heldCarbonRow` (new in `lib/gridHeld.ts`, `heldCarbon`'s rule by entity, for `carbon_intensity_hourly` and the new `CARBON_MONTHLY_TABLE`): a held ISO reads "license needed" with the publishers on hover, is not ranked, its line is not drawn, its file cells read "license needed". Both tables are public: none is held today.
  - The rows are chosen as before by pure functions moved from the component, `lib/gridKeys.ts` `carbonRanked` and `carbonMonthEnds` (and `carbonTip` for the hovers).
- **No figure moved.** `same-figures.mjs` on `/grid?grid=ercot&view=clean`, `caiso`, `us48`, `isone`: exit 1 by additions only. On each page the 199, 183, 195 and 76 figures before are kept whole and in order in the list after; the 2 added are the note's two keys; held figures and errors identical; panels 3 to 5 (`grid_carbonrank_`, `grid_carbonmonth_`).
- **Method:** a new section of `docs/methods/emissions.md`, "On the Grid tool's Clean tab, keyed (chain 107, session 1415)", with its Decisions (the note fits better than `grid_network.md`: Decisions); the new function also named in `generation_mix_hourly.md` (a short subsection), where every `filecalc|` function is named.
- **Failed read:** each block's place keeps its name and says "no data for ..., <reason>" (as since session 32), no figure, its method line kept; `test-grid-failed-reads.mjs` fails both tables three ways (six new cases).

## What to review

After the landing (none yet; below), on production:

1. Open `https://erw-flame.vercel.app/internal/open`, paste the token, press **Open the internal view**.
2. Open `https://erw-flame.vercel.app/grid?grid=ercot&view=clean`. Under "Carbon intensity now, ranked" every intensity is dotted; hover one: `carbon_intensity_hourly, entity eia930:CISO, intensity_generation, the latest hour: hour ... UTC`. Under the note: the download line and "Method: the Clean tab's carbon blocks, keyed"; click it: `/data/methods/emissions` at the new section.
3. Same page, "Monthly since 2018": each ISO's first and latest figure dotted (hover names the month); in the note, "13" and "7,869" dotted (hover names `site/data/carbon_left_out.json`). Hover the chart: the month and seven values in kg CO2/MWh. Download `erw_grid_carbonmonth_ercot.csv`: its header has two `Figure:` lines.
4. Hover the last 24 hours' chart: the hour (UTC) and seven values; nothing else changed in that block.
5. Add `#carbon-now` and `#carbon-monthly` to the address: the page opens at each block.
6. `https://erw-flame.vercel.app/grid?grid=isone&view=clean`: the same blocks, ISO-NE's rows drawn (the carbon tables are public).
7. Screenshots: not taken, no build.

## Checks

- Precheck for session 1415: run by the orchestrator, exit 0.
- Node, one at a time, exit 0 each, through the alias and tsx loaders: `test-grid-render.mjs` (93 cases: 8 new, `view_clean` now 4 figures, below), `test-grid-files.mjs` (144 cases; one new check, two blocks added to the ercot clean page, a us48 clean page), `test-grid-failed-reads.mjs` (113 cases; 6 new), `test-grid-held.mjs` (6 tests; the new checks inside the last test, see Decisions), `test-mix-view-calc.mjs` (11 tests; two extended), `test-grid-methods`, `test-check-values-light`, `test-clean-week`, `test-grid-addresses`, `test-grid-balance`, `test-grid-exchange`, `test-grid-file-keys`, `test-grid-keys`, `test-grid-lower48`, `test-hub-price`, `test-network-map`; `test-grid-keys` and `test-grid-exchange` also with plain node.
- The two new keys recomputed as check-values does (plain node, `check-filecalc.mjs`, `check-file.mjs`, `check-format.mjs`): 13 written "13", 7869 written "7,869", no table row (checked against the file alone). check-methods' own `figures()` and `named()` over the blocks' keys against `emissions.md` and `generation_mix_hourly.md`: every one named; `/grid`'s notes include `emissions`.
- `npx eslint` on the 13 changed code files: exit 0.
- `python -m unittest`, one module at a time, 59 modules (every module that names a changed file, and ten that walk `site/` or the notes): all exit 0, none stopped for memory. `tests.test_session1415` (new, 7 tests) exit 0.
- `same-figures.mjs`: 4 addresses, exit 1 by additions only (above). The temporary worktree of `52b1882a` and its junction removed.
- Type check through the junction: `npm run content` exit 0, `npx next typegen` exit 0, `npx tsc --noEmit -p .` exit 2 on a first run (a type predicate in `carbonRanked`), fixed, then exit 0; the junction removed with `rmdir`, the main copy's `node_modules` intact.
- Not run (the brief): build, check-values against a page, check-routes, check-links, screenshots.

## The landing

- None in this session. It lands with the chain's combined landing (`wip/1408-grid` and the sessions stacked on it, not on main). Pushed: `wip/1415-grid`.

## To finish

- The python modules not run: every module that does not name a changed file and was not in the ten picked (the orchestrator's whole suite covers them; the fixtures directory gained `carbon_monthly.json`, so a test that lists fixtures would be the one to watch).
- At the landing: the build; check-values on `/grid?grid=<grid>&view=clean` (two keys more a page, read from the committed file, no row); `check-methods.mjs --values <the run> --write`; check-links (`/data/methods/emissions#on-the-grid-tools-clean-tab-keyed-chain-107-session-1415`, `#carbon-now`, `#carbon-monthly`); the snapshots before and after, every difference listed (expected, on the Clean tab only: dotted figures in the two blocks, two download lines, two method lines, one sentence more under the ranked table, the new ids; no number moves); screenshots at 1280 and 390 under `docs/brand/review-1415/`.

## Decisions made without you

- **The method section is in `emissions.md`**, not `grid_network.md`: no `carbon_intensity*.md` exists; `emissions.md` defines the three carbon tables and already held the page's section ("On /emissions").
- **The months left out are a `filecalc|` key** (a new function, `carbon_left_out_n`), not words: it is a number the page writes; the function is the list's length, and it is named in `generation_mix_hourly.md` too, because `test-mix-view-calc.mjs` holds every function of that kind to that note.
- **The hours without hydro are a `file|` key**: the file's own value.
- **No key moved, no kind added**: the 28 figures keep their keys; a hover tip and the dotted underline were added (as the last 24 hours' figures); the ranked note gained "Hover a figure for its table, entity and hour.".
- **One method line for both blocks, anchors without a grid**, outside `GRID_ANCHOR` and `GRID_METHOD` (pinned by 1183 and 1184), as 1402 to 1414.
- **The held rule also covers the last 24 hours** (its chart, table and file), so no held ISO's rows would be drawn on the tab.
- **A held ISO's look is a `data-license-held` span**, not `Missing`: `tests/test_session473.py` lists which components may import `components/mix/Now.tsx`.
- **Pinned counts kept**: `Emissions.tsx` still holds four `check=` (473, 1159); the held checks went inside the last test of `test-grid-held.mjs` (1167 reads "pass 6"); `test_session1182.py`'s PanelFile count for `Emissions.tsx` extended from 1 to 3 (its only change).
- **A committed fixture**: `site/scripts/fixtures/carbon_monthly.json`, 636 rows of `carbon_intensity_monthly` (`intensity_generation`, 8 entities), read once with the anon key at 09:17 UTC, added to the render and file-test stand-ins. With it the older "How clean" block draws its four figures there: the render case `view_clean` now counts 4 figures (the ranked table's 14 are its own panel's).
- **The render cases' words do not name the two note figures' numbers** (13, 7,869): the file is rebuilt by the warehouse; their keys are checked instead.

## For Samuel's ruling

- The method line "Method: the Clean tab's carbon blocks, keyed" and a download line under each of the two blocks. Recommendation: keep; every keyed block of the tool has both.
- The dotted underline on the ranked and monthly figures (a source on hover). Recommendation: keep, as the last 24 hours.

## Files

- New: `site/scripts/fixtures/carbon_monthly.json`, `tests/test_session1415.py`, this report.
- Changed: `site/components/grid/Emissions.tsx`, `site/lib/gridKeys.ts` (`carbonTip`, `carbonRanked`, `carbonMonthEnds`), `site/lib/gridHeld.ts` (`CARBON_MONTHLY_TABLE`, `heldCarbonRow`), `site/lib/gridAnchors.ts` (`EMISSIONS_ANCHOR`, `METHOD_EMISSIONS_BLOCKS`), `site/lib/mixViewCalc.ts` (`leftOutCount`, the FILECALC entry, `sourceOf`), `site/lib/carbonLeftOut.ts` (`CARBON_LEFT_OUT_FILE`, `CARBON_LEFT_OUT_NAME`), `site/scripts/check-filecalc.mjs` (the function), `site/scripts/grid-render-standin.mjs`, `test-grid-render.mjs`, `test-grid-files.mjs`, `test-grid-failed-reads.mjs`, `test-grid-held.mjs`, `test-mix-view-calc.mjs`, `tests/test_session1182.py`, `docs/methods/emissions.md` (the section with Decisions), `docs/methods/generation_mix_hourly.md` (a subsection).
- On this machine only, in `runs/s1415/` of the worktree: every test's output, the same-figures lists, the one-off scripts.
