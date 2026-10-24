# Session 1413 report: the computed views keyed

24 October 2026, from about 08:00 to 09:30 UTC, on samueloldlaptop (the code machine, the old laptop), the fourth session of `queue/done/107-day-27-october-code-grid-tool-5.md`. Branch `wip/1413-grid`, cut from `wip/1412-grid` (sessions 1152 to 1412 stacked, not on main), worktree `C:\Users\lossa\Documents\erw-1413`. Code, tests and documents only (`runs/c077/brief.md`: no build, no server, no browser). Model spend USD 0. No warehouse data written, no Supabase write, no request to any publisher; light reads of Supabase's REST API with the anon key (one same-figures walk, 95 requests, the answers held in memory).

## Read these first

- **A new key kind, `filecalc|<function>|<data file>|<args>`**, always behind `fmt|<form>|`. Its recomputation applies the page's own function to the committed file in the repository, as `ercotn|` applies `lib/ercotNotices.ts`.
  - `site/scripts/check-filecalc.mjs` (new): `filecalcParts` (function, file, the shape of each argument, else no key) and `filecalcValue`. It imports `lib/mix2.ts` and `lib/mixViewCalc.ts` when a key needs them.
  - `site/scripts/check-values.mjs`: one branch (`if (p[0] === "filecalc")`), and its line says "the committed file". No "same" or "DIFF" line: a computed figure is no live-set row.
  - `site/scripts/check-methods.mjs`: `MEASURE_AT.filecalc = 1`, so a figure is the family `filecalc|` and its function.
- **The functions.**
  - Already pure, in `lib/mix2.ts` (no import), applied as they are: `acrossYears` (the duck view), `periodOf` and `highest` (the average day's peaks).
  - Inline until now, moved as they stood into `site/lib/mixViewCalc.ts` (new, no import), which the views now call: `historyTotal` and `historyCell` (the history by state), `availOf`, `availMean`, `availMin`, `availMax` (availability).
  - Ten functions: `duck_solar_peak`, `duck_low`, `duck_evening`, `duck_ramp`, `day_peak`, `hist_share`, `hist_mwh`, `avail_mean`, `avail_min`, `avail_max`.
- **What is keyed, one grid at a time on the committed files:**
  - `mix=duck`, "<grid>: <month> by year": every figure but the hours. 40 keys for CAISO, ERCOT, ISO-NE, MISO and PJM (eight Aprils, four computed figures and the days held each), 35 for SPP, 32 for NYISO. The days held are `file|mix/<grid>.json|months.<M>.days_held`, the file's own value.
  - `mix=day`, "Solar and wind at their peak hour": the two MW figures, 2 a grid (NYISO 1: its file reports no solar).
  - `mix=supply`, "Mean availability": mean, lowest and highest hour, 18 a grid (NYISO 12).
  - `mix=history`, each state's table: every share and every million MWh drawn. 66 for the United States (the default), 134 for Texas and California.
  - Why these: they are each view's top numbers and its table's cells, all small tables (at most 40 cells a grid, 66 a state), so each table is keyed whole.
  - Not keyed: the hours (words, as session 1166 left the records' hours), and the charts' points (they answer a hover).
- **Every keyed table has its file, its anchor and its method line.**
  - Files: `erw_grid_mixday_all_shares`, `_peak`, `erw_grid_duck_<grid>`, `erw_grid_history_<state>`, `erw_grid_supply_all_mean`, `erw_grid_supply_<grid>_tight`.
  - Anchors: `MIX_VIEW_ANCHOR` in `lib/gridAnchors.ts` (`#day-shares`, `#day-peak`, `#duck-by-year`, `#history-shares`, `#supply-mean`, `#supply-tight`; a second grid or state adds `-<name>`), outside `GRID_ANCHOR`, as sessions 1402 and 1403 did.
  - Method line: "Method: the computed views, keyed", to `METHOD_MIX_VIEWS`, the new section of `docs/methods/generation_mix_hourly.md`.
  - Failed-read guard: not applicable. The files are imported into the build (`lib/mixdata.ts`), so a missing file fails the build, not the page.
- **The figures are drawn by a new component, `components/mix/CalcKey.tsx`.** Session 1166's one `K` line in `views.tsx` (pinned by `tests/test_session1166.py`, which counts one `check=`) stays as it was.
- **No figure moved, in text or value.**
  - `same-figures.mjs` ran on 8 addresses: `/grid?grid=ercot&mix=duck`, `caiso&mix=duck`, `ercot&mix=history`, `caiso&mix=history&states=CA,TX`, `ercot&mix=supply`, `caiso&mix=supply`, `ercot&mix=day`, `caiso&mix=day`. It compared 2,204 figures on the code before (`17d06149`) and after, with the same live answers. Exit 1, because every page gains figures. With the 320 new figures taken out, every page's list of figures (key, value, text, in order), held figures, panels and errors is identical.
  - A one-off drew the four views with the old `views.tsx` and the new one (41 drawings: every grid, two and four grids, other months, periods, years, seasons, four choices of states, both scales). All 5,012 table cells and the whole text are the same, once the new file and method lines are set aside.
- **`same-figures.mjs` needs `%2C` for a comma inside an address of `--only`** (`states=CA%2CTX`): `--only` splits at commas. Found, not changed.

## What to review

After the landing (none yet; below), on production:

1. Open `https://erw-flame.vercel.app/internal/open`, paste the token, press **Open the internal view**.
2. Open `https://erw-flame.vercel.app/grid?grid=ercot&mix=duck`. Scroll to "ERCOT: April by year". Each MW figure and the days held are dotted. Hover one: it names `generation_mix_hourly_profile, iso:ercot`, what the figure is, its case, `lib/mix2.ts acrossYears` and the file. Under the table: the file line and "Method: the computed views, keyed"; click it to open the note's section.
3. Open `https://erw-flame.vercel.app/grid?grid=ercot&mix=day`. In "Solar and wind at their peak hour of the average day" the two MW figures are dotted. Both tables have a file line and a method line.
4. Open `https://erw-flame.vercel.app/grid?grid=ercot&mix=supply`. In "Mean availability" every percent is dotted. The tightest hours table now has a file line and a method line.
5. Open `https://erw-flame.vercel.app/grid?grid=ercot&mix=history&states=TX,CA`. Every share and million MWh in both state tables is dotted; there is a file a state.
6. View source and search `filecalc|`.
7. Screenshots: not taken, no build.

## Checks

- Precheck for session 1413: run by the orchestrator, exit 0.
- `node --import ./scripts/alias-register.mjs --import ./scripts/tsx-register.mjs scripts/test-mix-view-calc.mjs` (new): exit 0, 11 of 11.
  - Each moved function equals the old inline expression on every state, year and fuel of `mix_history.json` (over 10,000 cells) and on every grid, year, season and fuel of `mixplus/` (over 500 cases).
  - Every key's value equals the page's figure on over 3,000 cases.
  - A right value and its text pass check-values' rule; a wrong value, a wrong text and another year's value fail; a key that does not fit is no key.
  - Each view is drawn on every grid: its keys are recomputed, and they are exactly the old figures.
  - The note names every function, and its heading is the link's fragment.
- Through the same loaders, one at a time, exit 0 each:
  - `test-grid-file-keys.mjs`: 14 of 14, its recompute extended to `filecalc|`, the duck and history views added.
  - `test-grid-files.mjs`: 125 cases; 5 pages and one check added.
  - `test-grid-render.mjs`: 82 cases; 8 added, two a view.
  - `test-grid-methods.mjs`, `test-grid-addresses.mjs`, `test-hub-price.mjs`, `test-clean-week.mjs`, `test-grid-failed-reads.mjs`, `test-grid-stress.mjs`, `test-ercot-notices.mjs`.
- `node scripts/check-methods.mjs` (the recorded keys): exit 0. `node --check` on the 7 changed or new scripts: exit 0 each.
- `python -m unittest`, one module at a time, every one exit 0. That is 129 modules: every test that reads a changed file (views, anchors, check-values, check-methods, the three node tests, the method note), session 1168's list of tests that walk `site/lib` and `site/components` (502 among them), and `tests.test_session1413` (new, 7 tests).
- `same-figures.mjs`: 8 addresses, 2,204 figures. Exit 1, by additions only (above). The temporary worktree of `17d06149` and its junction were removed.
- Type check through the junction: `npm run content` exit 0, `npx next typegen` exit 0, `npx tsc --noEmit -p .` exit 0. The junction was removed with `rmdir`; the main copy's `node_modules` is intact.
- Not run (the brief): build, check-values against a page, check-routes, check-links, screenshots.

## The landing

- None in this session. It lands with the chain's combined landing (`wip/1408-grid` and the sessions stacked on it, not on main). Pushed: `wip/1413-grid`.

## To finish

- Land with the chain: the build, check-values on `/grid,/network` and on the views' addresses if they are added to its list (they are not read today: session 1166's note). Expect `filecalc|` lines saying "the committed file", 40 on `mix=duck`, 2 on `mix=day`, 18 on `mix=supply` and 66 on `mix=history` for ERCOT.
- Then `check-methods.mjs --values <the run> --write`, check-links (the new fragment `#the-computed-views-keyed-chain-107-24-october-2026` and the six anchors), and the snapshots before and after, every difference listed.
  - Expected differences, on the four views only: the dotted rule and tip on the keyed figures, a file line and a method line under each keyed table, and the new ids. No word or number moves.
- Screenshots at 1280 and 390 under `docs/brand/review-1413/` from that build.

## Decisions made without you

- **One kind for every computed view, named by its function**, not one kind a view: the rule is always "read the committed file, apply the page's function". The function is the figure's measure, so the note names each.
- **`lib/mix2.ts`'s functions stay where they are**; only the inline arithmetic moved. `check-filecalc.mjs` imports both libraries.
- **The duck view's days held are a `file|` key**, not a function: the value is the file's own (`generation_mix_hourly_profile`'s `days_held`).
- **The hours are not keyed** (times written as words), as in sessions 1166 and 1168.
- **The tightest hours table of `mix=supply` gained a file, an anchor and a method line** though its keys are session 1166's: the file test holds every figure of a block to its files.
- **The supply file's header begins with `generation_mix_hourly_profile`** (the hours availability is computed over), because the file test needs a table first. No table name new to the Mix or Clean tab is written in the views, so the tabs' license lines stand (`tests/test_session502.py`).
- **The history's render cases are on two choices of states**, not two grids: the view is by state, the same for every grid.
- **`test-grid-file-keys.mjs` was extended in place** (its recompute reads `filecalc|`, and the duck and history views joined its list), not given a new test: `tests/test_session1168.py` pins its count at 14.

## For Samuel's ruling

- The new method line "Method: the computed views, keyed" and the file lines under six tables of the four views. Recommendation: keep; every keyed table of the tool has both.
- Whether the views' addresses (`mix=duck`, `day`, `supply`, `history`) join check-values' page list with floors at the landing. Recommendation: yes, the ERCOT address of each.

## Files

- New: `site/lib/mixViewCalc.ts`, `site/scripts/check-filecalc.mjs`, `site/components/mix/CalcKey.tsx`, `site/scripts/test-mix-view-calc.mjs`, `tests/test_session1413.py`, this report.
- Changed: `site/components/mix/views.tsx` (the four views keyed, files, anchors, method lines), `site/lib/gridAnchors.ts` (`MIX_VIEW_ANCHOR`, `mixViewAnchor`, `METHOD_MIX_VIEWS`), `site/scripts/check-values.mjs`, `site/scripts/check-methods.mjs`, `site/scripts/test-grid-file-keys.mjs`, `site/scripts/test-grid-files.mjs` (5 pages and one check), `site/scripts/test-grid-render.mjs` (8 cases), `docs/methods/generation_mix_hourly.md` (the chain 107 section, with Decisions), `tests/test_session473.py` (one line: `CalcKey.tsx`, one key).
- On this machine only, in `runs/s1413/` of the worktree: every test's output, the same-figures lists and the additions proof, the before-and-after text one-off.
