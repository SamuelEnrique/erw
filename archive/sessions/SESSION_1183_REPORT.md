# Session 1183 report: every panel in the address

24 October 2026, from about 03:25 to 04:00 UTC, on samueloldlaptop (the code machine, the old laptop), the sixth session of `queue/done/091-day-25-october-code-grid-tool-3.md`. Branch `wip/1183-grid`, cut from `wip/1182-grid` (chains 077, 078 and 091 stacked, not on main), worktree `C:\Users\lossa\Documents\erw-1183`. Code, tests and documents only (`runs/c077/brief.md`: no build, no server, no browser). Model spend USD 0. No warehouse data written, no Supabase write, no request to any publisher; light reads of Supabase's REST API and the public snapshot object with the anon key, through `same-figures.mjs`'s proxy (answers held in memory, never written).

## Read these first

- **Session 1182's `data:` links, measured first: kept.** Drawn outside Next as `same-figures.mjs` draws them (now `--sizes`: each page's HTML and its flight payload, the two copies Next sends of what the server draws; a client component's own markup not counted, the same before and after), `wip/1181-grid` (`03704a3f`) against `wip/1182-grid` (`e25efb67`) on one set of live answers, 40 addresses: every page grew by 1.3 to 6.7 percent. The full table is below. No page passed 15 percent or 100 KB, so no route was made.
- **The CSP allows the download.** `site/next.config.ts` enforces fetch directives only (`default-src`, `script-src`, `style-src`, `img-src`, `font-src`, `connect-src`, `worker-src`, `frame-src`) and the four that cannot break a page. A followed or downloaded link is a navigation, and none of those directives covers one (`default-src` stands in for fetch directives only; `navigate-to` never shipped in a browser). `check-csp.mjs` clicks no download, so its own header says it cannot prove this. In a browser at the landing it is one click (under "To finish").
- **One list of anchors: `site/lib/gridAnchors.ts`** (`GRID_ANCHOR`, `PANEL_ANCHORS`, `anchorOf`, `panelAddress`). Seventeen anchors, the same on every grid where the panel is the same. A grid is added only where one page draws the same panel twice (`mix-panel-miso` with `grids=pjm,miso`; `stress-ramp-caiso` on a two-grid stress view), as the Mix view's older `today`/`today-<ba>` do. Each anchor has an address that opens it with its state, written as `gridHref` writes it:

| Anchor | Panel | Address |
|---|---|---|
| `#network-figures` | `grid_network_<grid>` | `/grid?grid=ercot&view=network&net=day&t=2021-02-15&node=BPAT` |
| `#replayed-day` | `grid_replay_<BA>` | `/grid?grid=ercot&view=network&net=day&t=2021-02-15&node=ERCO` |
| `#balance` | the balance | `/grid?grid=ercot&view=network` |
| `#gravity-figures` | `grid_gravity_<grid>` | `/grid?grid=ercot&view=gravity&shape=gravity&net=day&t=2021-02-15` |
| `#exchange-grids`, `#exchange-ties`, `#exchange-months` | the Exchange blocks | `/grid?grid=us48&view=gravity&shape=gravity`, `/grid?grid=ercot&view=gravity&shape=gravity` |
| `#last-24-hours` | `grid_clean24_<grid>` | `/grid?grid=ercot&view=clean` |
| `#mix-panel` | `grid_mix_<grid>` | `/grid?grid=ercot&mixp=month` |
| `#scarcity`, `#caiso-alerts`, `#ercot-notices` | kept as they were | `/grid?grid=ercot`, `/grid?grid=caiso` |
| `#stored-answers` | `grid_ask_<grid>` | `/grid?grid=ercot&ask=1&q=What+was+the+peak%3F` |
| `#stress-ramp`, `#stress-tight`, `#stress-calm`, `#stress-grids` | the stress tables | `/grid?grid=ercot&mix=stress&year=2024` |

- **Every panel's state was already in the address.** No panel keeps a state of its own in the browser: each is drawn on the server from the query, and the network component writes its words back through `netToPage`. One fix: the energy mix panel's two chips linked to `#hourly`, which is the first grid's section, on every grid of the page. They now link to the panel's own anchor.
- **The copy line: none added.** `components/CopyLine.tsx` is drawn only on `/data`. No block of `/grid` has one, old or new, so there is no placement to copy.
- **No figure moved:** `same-figures.mjs`, `e25efb67` against this tree on one set of answers, 43 addresses, 5,537 figures, every page the same. The pages grew by 622 bytes at most.

| Page | Before 1182 (bytes) | After 1182 | Growth |
|---|---|---|---|
| `/grid` (and `grid=us48&view=mix`) | 329,834 | 335,689 | +5,855, 1.8% |
| `grid=ercot&view=network` | 225,464 | 235,788 | +10,324, 4.6% |
| `grid=ercot&view=mix` | 811,260 | 828,979 | +17,719, 2.2% |
| `grid=caiso&view=mix` | 816,654 | 827,414 | +10,760, 1.3% |
| `grid=ercot&view=clean` | 194,863 | 200,944 | +6,081, 3.1% |
| `grid=caiso&view=gravity` | 337,248 | 357,705 | +20,457, 6.1% |
| `grid=pjm&view=gravity&net=day&t=2025-06-24` | 290,477 | 309,828 | +19,351, 6.7% (the largest share) |
| `grid=ercot&mix=stress` | 832,353 | 865,863 | +33,510, 4.0% |
| `grid=caiso&view=mix&mixp=month` | 848,313 | 864,704 | +16,391, 1.9% |
| stress view, the seven grids | 1,299,291 | 1,383,323 | +84,032, 6.5% (the largest growth: 15 files) |

Every page of the 40: `runs/s1183/sizes.out` and `sizes/sizes.json`; the worst case: `runs/s1183/sizes_worst.out`. Both are on this machine and not committed.

## What to review

There is no landing yet (below). After the landing, on production:

1. Open `https://erw-flame.vercel.app/internal/open`, paste the token, press **Open the internal view**.
2. Open `https://erw-flame.vercel.app/grid?grid=ercot&mixp=month#mix-panel`: the page opens at the energy mix panel, on "By month". Press "Hourly, last 7 days": the address becomes `/grid?grid=ercot#mix-panel`.
3. Open `https://erw-flame.vercel.app/grid?grid=ercot&view=network&net=day&t=2021-02-15&node=ERCO#replayed-day`: the page opens at ERCOT's figures of 15 February 2021.
4. Open `https://erw-flame.vercel.app/grid?grid=ercot&view=gravity&shape=gravity#exchange-months`: the page opens at "Over the last twelve months". Then open `https://erw-flame.vercel.app/grid?grid=ercot&mix=stress&year=2024#stress-calm`: the page opens at "ERCOT: dark, calm stretches, by year".
5. Open `https://erw-flame.vercel.app/grid?view=mix&grids=pjm,miso`: hover MISO's chips under its hourly mix. Each points at `#mix-panel-miso`, where it used to point at `#hourly`.
6. On any Grid panel, click "Download this table (CSV)": the file downloads (session 1182's link, which the CSP allows).
7. Read `site/lib/gridAnchors.ts` and the method note's section "Every panel in the address (chain 091, 24 October 2026)" with its Decisions.
8. Screenshots: not taken, no build.

## Checks

- Precheck for session 1183: run by the orchestrator, exit 0.
- `same-figures.mjs --sizes`, `03704a3f` against `e25efb67` (a temporary detached worktree `C:\Users\lossa\Documents\erw-1183-before`, removed): 40 addresses, exit 0, every page the same (4,192 figures), 0 pages over the bound. Worst case (the seven-grid stress view, ERCOT's 2021): exit 0, 0 over. The first two runs failed on usage (a Git Bash path, then a comma in an address that the list splits on: `%2C`). Neither result was used.
- `same-figures.mjs --sizes`, `e25efb67` against this tree: 43 addresses, exit 0, every page the same, 5,537 figures; 217 distinct requests, 0 new after; largest growth 622 bytes.
- Node tests, one at a time:
  - `test-grid-addresses` (alias loader): exit 0, "12 tests passed, 61 addresses, 17 panels". Four new tests: each panel's address is `gridHref`'s, opens its tab and grid unredirected, and has its state read back; the anchors are unique and none is an older id of the page; the route check lists each address with its anchor; the note names each anchor.
  - `test-grid-files` (both loaders): exit 0, 73 cases, 20 of them new: each of 18 drawn pages carries every panel's anchor with no id twice, every anchor is drawn somewhere, and a second grid takes the anchor plus the grid.
  - Mutation check: with `#balance` removed and the mix anchor fixed to one value, the test exits 1 and names the five failures. The code was restored before the commit.
  - `test-grid-units`: exit 0, with four new cases for `reduceTree`, `htmlOf`, `sizeOf` and `sizeRows`.
  - Also exit 0: `check-revised`, `grid-390`, `grid-ask`, `grid-exchange`, `grid-failed-reads`, `grid-file-keys`, `grid-held`, `grid-replay`, `grid-stress`, `network-map`, `network-split`.
- `node --check scripts/check-routes.mjs`: exit 0. It was not run against a server (no build).
- `python -m unittest`, one module at a time, on 77 modules: every one that reads a changed file (the grep of `tests/` for the 14 names), plus the new `test_session1183` (8 tests). Each exit 0, with skips as before. No assertion was removed or changed.
- `npx eslint` on the 13 changed or new code files: exit 0.
- Type check through the junction (`mklink /J` to the main checkout's `node_modules`): `npm run content` exit 0, `npx next typegen` exit 0, `npx tsc --noEmit -p .` exit 0. Both junctions were removed with `rmdir`, and the main copy's `node_modules` is intact.
- Not run (the brief): the build, check-values, check-routes against a server, check-csp, screenshots.

## The landing

- None in this session. Chain 091 works code-only, stacked on `wip/1176-grid` (chains 077 and 078, not on main), and this branch lands with them. Pushed: `wip/1183-grid`.

## To finish

- Land with the chain's combined landing. At that build, against the running site, run `node scripts/check-routes.mjs http://localhost:3000` and read its exit. Its new block "the Grid panels' anchors" asks 17 addresses (some already in pass 1) and expects `17 of 17 drawn`.
- check-values on the addresses of "What to review": every key as before. No key changed.
- The snapshots before and after, every difference listed. Expected: none in the visible text. Only the `id` attributes, and the mix chips' `href` hash (`#hourly` to `#mix-panel`), are new in the HTML.
- In a browser at the landing, one click on a "Download this table (CSV)" link: Chrome downloads `erw_<id>.csv`, and the console shows no CSP report (`check-csp.mjs` does not click).

## Decisions made without you

- **The `data:` links stay.** No page passed the brief's bound: the largest growth was 6.7 percent, and the largest in bytes was 84 KB on the seven-grid stress view. The CSP does not cover the download. `--sizes` stays in `same-figures.mjs` for the next panel that adds to a page.
- **The anchor names the panel, not the grid.** The grid is added only to a repeat on the same page, after the first, as the Mix view's older sections do.
- **Where a session's test pins the panel's element word for word** (mix: 1152 and 1159; last 24 hours: 1159 and 1181), the `id` sits on an element that wraps the panel alone. The pinned lines stand. Everywhere else the `id` is on the panel's own element.
- **`scarcity`, `caiso-alerts` and `ercot-notices` are kept** on the panel's one section. Links point to them, and sessions 1155, 1159 and 1174 pin them.
- **The mix chips point at the panel**, which fixes the second grid's chips that opened the first grid's section. They keep `scroll={false}`.
- **The network panel's sample address carries a replayed day and a node** (`net=day&t=...&node=BPAT`), so each of its state words is tested. Its bare address is in the route check already.
- **The page size is an estimate made outside Next**: HTML plus flight payload, with client components' own markup left out. Bytes are counted the same way before and after, and the 15 percent test errs high because the baseline omits the client markup.

## For Samuel's ruling

- Whether each Grid panel should get a "copy this view's address" control (`CopyLine` with the panel's address and anchor). None of the older blocks has one. Recommendation: no; the browser's bar holds the address with its anchor.
- The anchor names, which are words a reader sees in an address (`mix-panel`, `last-24-hours`, `stored-answers` and the rest). Recommendation: keep them.

## Files

- New: `site/lib/gridAnchors.ts`, `tests/test_session1183.py`, this report.
- Changed: `site/components/grid/NetworkFigures.tsx` (the network, balance and gravity anchors), `ReplayDay.tsx`, `ExchangeView.tsx` (three sections), `Emissions.tsx` (two wrappers), `MixView.tsx` (the wrapper; `PanelToggle` takes `at`), `AskExamples.tsx`, `site/components/mix/views.tsx` (the four stress blocks).
- Changed: `site/scripts/check-routes.mjs` (`GRID_ANCHORS` and its check in pass 1), `same-figures.mjs` (`--sizes`: `reduceTree`, `htmlOf`, `sizeOf`, `sizeRows`), `test-grid-addresses.mjs`, `test-grid-files.mjs`, `test-grid-units.mjs`, `docs/methods/grid_network.md` (the section "Every panel in the address (chain 091, 24 October 2026)" with its Decisions).
- On this machine only: `runs/s1183/` in the worktree (the size runs, same-figures' output and figure lists, every test's output).
