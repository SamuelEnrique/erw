# Session 1421 report: the older blocks' anchors and method links

24 October 2026, from about 10:45 UTC, on samueloldlaptop (the code machine, the old laptop), the third session of `queue/done/111-day-28-october-code-grid-tool-6.md`. Branch `wip/1421-grid`, cut from `wip/1420-grid` (sessions 1152 to 1420 stacked, not on main), worktree `C:\Users\lossa\Documents\erw-1421`. Code, tests and documents only (`runs/c077/brief.md`: no build, no server, no browser). Model spend USD 0. No warehouse data written, no Supabase write, no request to any publisher; light anon reads of Supabase's REST API (one same-figures walk, the answers held in memory only). Production was not read (HTTP 402).

## Read these first

- **Skipped, already done:** "Yesterday" and the mix table (session 1416: `#yesterday-<code>`, `#mix-table`, `METHOD_CONDITIONS`) and the Clean tab's carbon blocks (session 1415: `#carbon-now`, `#carbon-monthly`, `METHOD_EMISSIONS_BLOCKS`) had their anchors and method links. Nothing of theirs moved.
- **One list:** `site/lib/gridAnchors.ts` `OLDER_ANCHOR` and `OLDER_BLOCKS`, with one `METHOD_` constant a link. They sit outside `GRID_ANCHOR` and `GRID_METHOD`, whose 17 panels are pinned by sessions 1183 and 1184, as 1402 to 1416 did.

| Block | Anchor | Address (route check) | Method: note, section |
|---|---|---|---|
| Right now: demand | `#right-now` (new) | `/grid?grid=ercot` | `grid_network`: "Right now" and the mix in that hour, what each figure is (session 1421), **new** |
| Batteries | `#batteries` (new) | `/grid?grid=ercot` | `storage`: The figures on the page and their keys |
| What it costs | `#what-it-costs` (new) | `/grid?grid=ercot` | `price_board`: The figures on the page and their keys |
| What is being built | `#what-is-being-built` (new) | `/grid?grid=caiso` | `energy_projects`: The figures on the grid page and their keys; `datacenter_facilities`: Grid pages: which grid a facility belongs to (session 36A) |
| Reliability | `#reliability` (kept, pinned), `#reliability-days`, `#reliability-peaks`, `#reliability-latest` (new, on each table's heading) | `/grid?grid=caiso` | `california_reliability`: 1. Every notice since 1998 (days per year); 2. How tight was it (the two daily tables) |
| The mix in that hour | `#now-mix` (kept) | `/grid?grid=ercot` | `grid_network`: the same new section |

- **Where a block already linked a whole note**, the link now opens the section and its words are unchanged. This covers Batteries' "Method", What it costs' "Method", What is being built's two "Method" links, and Reliability's "the method".
- **New visible words, three lines:**
  - under Right now: `Method: "Right now" and the mix in that hour.`;
  - under the mix in that hour: the same line;
  - under Reliability's latest fourteen days: `Method: how tight was it, the daily figures.`.
- **Fragments come from the renderer.** `site/scripts/test-grid-older-methods.mjs` (new, 3 tests) renders each committed note with `lib/markdown.ts` `render`. It holds each fragment to the id `headingSlugs` writes for the named heading, among the note's headings in order. It also checks that the section names the block, runs check-links' `judge` and `anchorOk`, and checks that the link is in the component and that check-methods reads the note. With one fragment cut short by a letter, the test exits 1 and names the constant.
- **check-links needed no change.** It already checks every `#fragment` of every internal link against the ids of the method page, and its page list (check-values' `--list`) holds `/grid?grid=<each grid>`. `node --check` passes.
- **No figure moved.** `same-figures.mjs --sizes` compared `96dcb34d` with this tree on the Mix tab of ERCOT, CAISO, ISO-NE and the Lower 48: 834 figures, every page the same, panels the same, exit 0. The pages grew by 418 to 1,792 bytes.

## What to review

There is no landing yet (below). After the landing, on production:

1. Open `https://erw-flame.vercel.app/internal/open`, paste the token, press **Open the internal view**.
2. Open `https://erw-flame.vercel.app/grid?grid=ercot#right-now`: the page opens at "Right now: demand". Under it, click "Method: "Right now" and the mix in that hour". `/data/methods/grid_network` opens at the new section.
3. On the same page, add `#batteries`, `#what-it-costs` and `#now-mix` to the address: each opens its block. Click Batteries' "Method": `storage` opens at "The figures on the page and their keys". Do the same for What it costs' "Method" (`price_board`).
4. Open `https://erw-flame.vercel.app/grid?grid=caiso#what-is-being-built`. Click its two "Method" links: `energy_projects` and `datacenter_facilities` open at their sections.
5. Open `https://erw-flame.vercel.app/grid?grid=caiso#reliability-peaks`, then `#reliability-days` and `#reliability-latest`. In the days per year footnote, "the method" opens section 1 of `california_reliability`. Under the latest fourteen days, "Method: how tight was it, the daily figures" opens section 2.
6. Read `docs/methods/grid_network.md`, section "The older blocks' files, anchors, method links and render cases (chain 111, ...)". Read the paragraph of session 1421, its Decisions and the new subsection.
7. Screenshots: not taken, no build.

## Checks

- Precheck for session 1421: run by the orchestrator, exit 0.
- Node tests, one at a time, through the junction's loaders. Each exit 0:
  - `test-grid-older-methods.mjs` (new, 3 of 3; its mutation run exit 1, restored);
  - `test-grid-methods.mjs` (5 of 5, unchanged);
  - `test-grid-addresses.mjs` (13 tests, one new: the older anchors are plain ids, none is another panel's, each address opens the Mix tab of its grid, and the route check lists each one);
  - `test-grid-render.mjs` (117 cases; the 18 older-block cases carry their anchors and methods);
  - `test-grid-files.mjs` (161 cases);
  - `test-grid-failed-reads.mjs` (113);
  - `test-markdown-safe.mjs`.
- `node scripts/check-methods.mjs` (no server): exit 0, 553 of 553 figures named. `node --check` on `check-routes.mjs` and `check-links.mjs`: exit 0 each. Neither was run against a server (no build).
- `same-figures.mjs --sizes`, 4 addresses: exit 0, every page the same. The temporary worktree of `96dcb34d` and its junction were removed.
- `npx eslint` on the 8 changed or new code files: exit 0.
- `python -m unittest`, one module at a time, about 60 modules: every module that names a changed component, `gridAnchors`, the render, methods or addresses test or `page_tables`, plus the `grid_network.md` modules 109, 1156, 1162, 1175, 1176, 1186, 1188, 180, 180b, 193 and 247. None was stopped for memory.
  - The first pass had two failures:
    - `test_session1184` counts `test-grid-methods.mjs`'s five tests ("pass 5"). The older tests moved to a file of their own.
    - `test_session137` reads `<Section title="..."` in order. The `id` now follows the `title`.
  - Then all exit 0, including `test_session1421` (new, 9 tests), 1184, 137, 1420, 237, 58, 1183, 502 and 1404. No assertion was removed or changed.
- Type check through the junction, once at the end: `npm run content` exit 0, `npx next typegen` exit 0, `npx tsc --noEmit -p .` exit 0. The junction was removed with `rmdir`, and the main copy's `node_modules` is intact (333 entries).
- Not run (the brief): the build, check-values, check-routes and check-links against a server, screenshots.

## The landing

- None in this session. Production answers HTTP 402 and this window runs no gate (chain 107's note). The branch lands with the chain's combined landing (`wip/1417-grid` and the sessions stacked on it). Pushed: `wip/1421-grid`.

## To finish

- At the landing, after the build, run `node scripts/check-routes.mjs http://localhost:3000`. Its block "the Grid panels' anchors" now asks 26 addresses and expects `26 of 26 drawn` (17 and the 9 older).
- `node scripts/check-links.mjs http://localhost:3000` (a browser: one heavy process): no `anchor` finding for the eight new fragments.
- check-values on `/grid?grid=ercot`, `/grid?grid=caiso` and `/grid?grid=isone`. No key was added or removed.
- The snapshots before and after, every difference listed. Expected, on the Mix tab only:
  - the three new method lines;
  - the changed `href` of five existing method links;
  - the new `id` attributes.
  - No number moves.

## Decisions made without you

- **An existing whole-note link opens its section, its words unchanged**, as session 1184 did for the scarcity strip and CAISO's alerts.
- **The ids the blocks had are kept** (`reliability`, pinned by sessions 58 and 1420; `now-mix`). The new ids go on each block's own `Section`, inside the panel element whose line session 1420 pins, or on each Reliability table's `h3`.
- **Batteries opens `storage.md`'s keys section**, which names the block. `storage_daily_cycle`'s section defines only the day's cycle, and CAISO's block draws only the units.
- **One new section, where no note defined the block**: Right now and the mix in that hour. It has its Decisions in the chain 111 paragraph.
- **The new lines are drawn in every state of their block** (no data, CAISO's mix withheld), and never in a failure's words. The existing links stay where they stood: What it costs' link and the queue's appear only where their figures are drawn.
- **`id` after `title`** on each `Section`, for session 137's reader.
- **A separate test file** for the older fragments, for session 1184's count.

## For Samuel's ruling

- The three new method lines' words. Recommendation: keep them, in the tool's one form ("Method: <the section's words>").
- Batteries' method: `storage.md`'s keys section, or `storage_daily_cycle (derived)`. Recommendation: the keys section, which names the block.
- The older blocks' existing bare "Method" links could take the tool's "Method: <words>" form. Recommendation: leave them as they are (no words moved).

## Files

- New: `site/scripts/test-grid-older-methods.mjs`, `tests/test_session1421.py`, this report.
- Changed: `site/lib/gridAnchors.ts` (`OLDER_ANCHOR`, `OLDER_BLOCKS`, eight `METHOD_` constants), `site/components/grid/YourGrid.tsx`, `Reliability.tsx`, `NowView.tsx`, `site/scripts/check-routes.mjs` (`GRID_ANCHORS`, 9 more), `site/scripts/test-grid-addresses.mjs` (one test), `site/scripts/test-grid-render.mjs` (18 cases, header), `docs/methods/grid_network.md` (the session 1421 paragraph, Decisions, the new subsection).
- On this machine only, in `runs/s1421/` of the worktree: every test's output, the same-figures lists, the one-off scripts.
