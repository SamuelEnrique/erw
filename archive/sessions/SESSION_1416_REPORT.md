# Session 1416 report: "Yesterday" and the mix table at 390 and on hover

24 October 2026, from about 09:30 UTC, on samueloldlaptop (the code machine, the old laptop), the seventh session of `queue/done/107-day-27-october-code-grid-tool-5.md`. Branch `wip/1416-grid`, cut from `wip/1415-grid` (sessions 1152 to 1415 stacked, not on main), worktree `C:\Users\lossa\Documents\erw-1416`. Code, tests and documents only (`runs/c077/brief.md`: no build, no server, no browser). Model spend USD 0. No warehouse data written, no Supabase write, no request to any publisher; light anon reads of Supabase's REST API (one same-figures walk, 107 distinct requests, the answers held in memory only).

## Read these first

- **What was found** (`site/components/grid/Conditions.tsx`): "<grid>: yesterday" (`GridYesterday`, in the Mix tab's opening blocks) and "Generation mix, as a table" (`MixTable`, at the tab's foot) had session 1166's keys but were not named panels, had no file, no method line and no anchor constant; the mix table (ten columns) scrolled in a plain `overflow-x-auto` frame with no caption, no `scope` on its heads and each region's name in a `td`; the fuel colours' row carried an `aria-label` on an element with no role.
- **The two small charts already answered a hover and a tap.** The seven days' chart is `LineChart` over `TimeChart` (card: the hour start in UTC, demand and the day-ahead forecast in MW, the station's temperature in degrees F, a dashed guide at the hour); the day's mix is `ShareBar` over `ShareSegments` (card: the fuel, its MWh, its share). A tap fires the same mouse events. Session 1150's review lists them as "two small charts with tips". **Their drawing is unchanged** (same components, same props), so no old-against-new drawing test was needed (session 1412's case was a chart of its own). One sentence now says it under the block's opening: "A hover or a tap on the chart gives the hour (UTC) and its demand, forecast and temperature; on the bar, a fuel's MWh and share. Hover a dotted figure for its table and hour." (no temperature for the Lower 48, no bar for CAISO).
- **Now:**
  - `grid_yesterday_<grid>` (anchor the id it had, `#yesterday-<EIA-930 code>`, `yesterdayAnchor`): its file `erw_grid_yesterday_<grid>.csv`, one figure a row with its key and value (peak, forecast at the peak, the miss in MW and percent, the day's mean absolute miss and its hours, each degree day, the day's net generation; a degree day not computed or not read in the page's words); the line "Method: "Yesterday" and the mix table, keyed".
  - `grid_mixtable_all` (anchor `#mix-table`, as it was): the table in `scrollRegion(caption)` with an `sr-only` caption, `scope="col"` heads, each region a `<th scope="row">`; its file `erw_grid_mixtable_all.csv` (each share with its key, from `shareKey`); the same method line.
  - `lib/gridAnchors.ts`: `CONDITIONS_ANCHOR`, `yesterdayAnchor`, `METHOD_CONDITIONS`, outside `GRID_ANCHOR` and `GRID_METHOD` (pinned by 1183 and 1184), as 1413 to 1415.
  - Method: `docs/methods/generation_mix_hourly.md`, new subsection of the chain 107 section, `### "Yesterday" and the mix table, at 390 pixels and on hover (session 1416)`, with "Decisions (chain 107, session 1416)" (the rendered note's id checked equal to the constant's fragment).
- **No figure moved.** `same-figures.mjs --sizes` on `/grid?grid=ercot&view=mix`, `caiso`, `us48`, live answers, code before (`f24b3319`) and after: 203, 358 and 121 figures, every one the same and in order; held figures and errors the same; panels 5 to 7, 5 to 7, 4 to 6 (the two new names); the exit is 1 by those additions only. HTML +15 to 17 KB a page (the two files' data links), 0 pages over.
- **The 1166 keys are all kept**: `check=` in `Conditions.tsx` still 11 (`tests/test_session473.py`), every pinned `F` line of `tests/test_session1166.py` as it was; the files' figures are written as `{ check, raw }` objects, held to the drawn figures by `test-grid-files.mjs`.
- **A visible change, no number:** as a named panel the mix table takes session 1159's row rule (`[data-grid-panel]` in `app/tokens.css`): rows about 33 px tall where they were about 29, the full rule between rows.

## What to review

After the landing (none yet; below), on production:

1. Open `https://erw-flame.vercel.app/internal/open`, paste the token, press **Open the internal view**.
2. Open `https://erw-flame.vercel.app/grid?grid=ercot`. Under "ERCOT: yesterday": the new sentence under the opening; hover the seven days' chart (the hour in UTC, demand, forecast, temperature) and the bar (the fuel, MWh, share). Under the bar: "Download this table (CSV)..." and "Method: "Yesterday" and the mix table, keyed"; click it: `/data/methods/generation_mix_hourly` at the new subsection. Download `erw_grid_yesterday_ercot.csv`: one figure a row.
3. Same page, scroll to "Generation mix, as a table": its rows a little taller; the download line and the method line under the note.
4. At 390 px (a phone, or the browser's device view): the same page, the mix table. Press Tab until its frame is outlined, then the right arrow: the table scrolls. Tap the seven days' chart: the card opens; tap the bar: the fuel's card.
5. Add `#yesterday-erco` and `#mix-table` to the address: the page opens at each block. `https://erw-flame.vercel.app/grid?grid=caiso#yesterday-ciso`: no bar sentence (California's mix withheld).
6. Read `docs/methods/generation_mix_hourly.md`, the subsection above, and its Decisions.
7. From `site/`: `node --import ./scripts/alias-register.mjs --import ./scripts/tsx-register.mjs scripts/test-grid-render.mjs` (the six `grid_yesterday_` and `grid_mixtable_` cases).
8. Screenshots: not taken, no build.

## Checks

- Precheck for session 1416: run by the orchestrator, exit 0.
- Node, one at a time, through the alias and tsx loaders, exit 0 each: `test-grid-render.mjs` (99 cases: 6 new; `view_now` ercot 24 to 21 figures, `view_now` isone 14 to 11, `view_mix` 25 to 17, their keys still found), `test-grid-files.mjs` (145 cases: 1 new, every figure of the two blocks in its file and back, on ERCOT, CAISO, ISO-NE, the Lower 48), `test-grid-failed-reads.mjs` (113), `test-grid-addresses`, `test-grid-methods`, `test-grid-file-keys`, `test-grid-generation`, `test-grid-reads`, `test-clean-week`, `test-hub-price`, `test-mix-hourly`, `test-mix-view-calc`, `test-grid-ask` (602 of 602), `test-grid-390` (5, unchanged).
- The method link: the note rendered by `lib/markdown.ts` holds `id="yesterday-and-the-mix-table-at-390-pixels-and-on-hover-session-1416"` (a one-off, `runs/s1416/slug.mjs`): found.
- `same-figures.mjs --sizes`, 3 addresses (above): exit 1 by the added panel names only. The temporary worktree of `f24b3319` and its junction removed.
- `npx eslint` on the four changed code files: exit 0.
- `python -m unittest`, one module at a time, 48 modules (every module that names a changed file, and `1158`): all exit 0, none stopped for memory: `test_session1416` (new, 8 tests), `102`, `1152`, `1154`, `1155`, `1157`, `1158`, `1159`, `1160`, `1162`, `1165`, `1166`, `1167`, `1170`, `1171`, `1174`, `1176`, `1179`, `118`, `1180`, `1181`, `1182`, `1183`, `1184`, `1185`, `1188`, `133`, `1402`, `1403`, `1404`, `1406`, `1411`, `1412`, `1413`, `1414`, `1415`, `156`, `168_network`, `237`, `266`, `299`, `310`, `416`, `473`, `502`, `78`, `94`.
- Type check through the junction, once at the end: `npm run content` exit 0, `npx next typegen` exit 0, `npx tsc --noEmit -p .` exit 0; the junction removed with `rmdir`, the main copy's `node_modules` intact (333 entries).
- Not run (the brief): build, check-values against a page, check-routes, check-links, screenshots, AccessLint on a page. Not run (no changed file read): `test-ask-ready.mjs`, `test-ask-speed.mjs` (they name the table `generation_mix_hourly_profile`, not the note), and every python module that names no changed file.

## The landing

- None in this session. It lands with the chain's combined landing (`wip/1408-grid` and the sessions stacked on it, not on main). Pushed: `wip/1416-grid`.

## To finish

- At the landing: the build; check-values on `/grid?grid=ercot`, `/grid?grid=caiso`, `/grid?grid=us48` (no key added or removed by this session); check-links (`/data/methods/generation_mix_hourly#yesterday-and-the-mix-table-at-390-pixels-and-on-hover-session-1416`, `#yesterday-erco`, `#mix-table`); check-390 on `/grid?grid=ercot` (the mix table in a scroller, nothing past the right edge); AccessLint's live scan of the same page (the mix table's frame, the fuel colours' group); the snapshots before and after, every difference listed (expected, on every Mix tab only: the sentence under "Yesterday"'s opening, two download lines, two method lines, the mix table's caption, header cells and frame attributes, its rows taller; no number moves); screenshots at 1280 and 390 under `docs/brand/review-1416/`.

## Decisions made without you

- **No chart was redrawn**: both small charts were the shared charts, already answering a hover and a tap with the hour or the fuel and its MW or MWh; a card of their own would move their look on every page.
- **The anchors are the ids the blocks had** (`#yesterday-<code>`, `#mix-table`), named in `lib/gridAnchors.ts` outside the pinned lists.
- **The mix table is one panel, `grid_mixtable_all`**: it is the same on every grid's tab, and `<MixTable />` takes no prop (three python tests read that line); its file names `/grid?grid=us48` as its page.
- **"Yesterday" takes its grid from its code** (`GRID_OF`, the inverse of NowView's `CONDITIONS_CODE`): `<GridYesterday code={CONDITIONS_CODE[grid.slug]} />` is pinned by `tests/test_session237.py`.
- **The file's day's net generation uses `genTotal`, FuelBar's rule, not a copy of the line**: FuelBar's own line is unchanged; the other keys are written in the file's rows as in the figures, and `test-grid-files.mjs` holds the two lists equal.
- **The render cases of the two blocks are their own**; the older `view_now` and `view_mix` cases now count fewer own figures and keep every key they checked (`tests/test_session1166.py`'s "also covered by" lines still name those cases, which still hold the keys).
- **The fuel colours' row is `role="group"`**: an `aria-label` on an element without a role is not read.
- **The sentence on hover is per grid**: no temperature where the block has no station (the Lower 48), no bar where the mix is withheld (CAISO).

## For Samuel's ruling

- The sentence under "Yesterday"'s opening ("A hover or a tap on the chart gives ..."). Recommendation: keep, as the scorecard's (session 1412).
- The mix table's rows taller as a named panel (session 1159's rule). Recommendation: keep, one row height across the tool.
- Still open from session 1166: California's shares in the mix table (ruling 2); the minus sign against the hyphen in "Yesterday"'s miss (ruling 3).

## Files

- New: `tests/test_session1416.py`, this report.
- Changed: `site/components/grid/Conditions.tsx`, `site/lib/gridAnchors.ts` (`CONDITIONS_ANCHOR`, `yesterdayAnchor`, `METHOD_CONDITIONS`), `site/scripts/test-grid-render.mjs` (six cases, three counts), `site/scripts/test-grid-files.mjs` (one check), `docs/methods/generation_mix_hourly.md` (the subsection with Decisions).
- On this machine only, in `runs/s1416/` of the worktree: every test's output, the same-figures lists, the one-off scripts.
