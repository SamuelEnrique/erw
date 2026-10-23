# Session 1158 report: 390 pixels, accessibility, links

23 October 2026, from about 20:40 UTC, on samueloldlaptop (the code machine, the old laptop), session 1158 of `queue/done/077-day-23-october-code-grid-tool.md`, beside chain 075/076. Branch `wip/1158-grid`, cut from `wip/c077-land2` (sessions 1150 to 1156 merged with main), worktree `C:\Users\lossa\Documents\erw-1158`. Model spend USD 0. No warehouse data written, no Supabase read or write, no request to any publisher.

**The machine was short of memory** (1.6 GB free of 7.5 GB; the harness had stopped a landing gate): on the orchestrator's instruction, no `next build`, no `next start`, no browser for pages (no screenshots, no `audit_live`, no check-390, no check-links), no whole python suite. Every check below ran without a server. `site/node_modules` was a junction to the main checkout's (the same `package-lock.json`), not an `npm ci`, and was taken down before the hand-over.

## Read these first

- **AccessLint on production found nothing to fix on the four pages** session 1150 saved (`/grid`, `/grid?grid=caiso`, `/grid?grid=ercot&view=network`, `/grid/caiso/alerts`): 0 violations each. Read the limits: the HTML is what a visitor's fetch returns (every page in review, so every site link is a span), with scripts, styles and repeats taken out to fit the tool; no stylesheet, so colour contrast was not judged; the network, map and gravity drawings are drawn in the browser and are not in that HTML.
- **The chain's own panels, rendered without a server, held two real faults and one rule miss**, each mended in markup and classes only:
  1. **The energy mix panel's tables (session 1152) scrolled in a frame a keyboard cannot reach.** At 390 px the monthly table (380 px) is wider than its 324 px column. AccessLint `keyboard-accessible/scrollable-region` (serious), found on the panel rendered at 324 px. Now each frame is `scrollRegion(caption)` (`lib/cells.ts`, as `ToolTable` draws it: a named region, one keyboard stop, given back by `ScrollRegions.tsx` when it does not scroll); each fuel's name is the row's header cell (`<th scope="row">`), and its colour swatch is `aria-hidden`.
  2. **The network map's drawing was an image holding the regions a keyboard reaches and the seven grids' links (session 1156).** An image's children are presentational, so a screen reader is not given them. AccessLint `aria/presentational-children-focusable` (serious), shown on the map's own markup. `role="group"`, the gravity shape's role, is not allowed on an svg either: `aria/aria-allowed-role` (minor). Both drawings now carry their name and no role (the svg's own, a graphics document): 0 violations on the same markup.
  3. **On a phone the hover cards of the map's lines and the gravity shape were cut off and did not stay open.** A card was `max-w-xs` (320 px) from the pointer, in a frame that clips (`overflow-hidden`): from the middle of a 324 px drawing it ran 160 px past the edge. A tap fired no `pointermove`, and the `pointerleave` that follows a tap closed the card at once. Now a card's widest is `cardWidth(x, right)` (`lib/networkMap.ts`: at most 20rem, never past the frame); a tap on a line, the Lower 48 or a circle opens its card (`pointerdown`); a finger lifting leaves it, a tap on the empty drawing closes it. The mouse's hover is unchanged.
  4. **A stored answer's filter written without a space ran past the Ask column (session 1157).** `where={"status":"active","fuel_technology":[...]}` is set in monospace, about 500 px wide, in a 324 px column. `code` already wraps anywhere (`globals.css`), but the filter is a span. The `<details>` now has `break-words`.
- **No figure moved:** no `Num`, no `check` key, no value; the tests pin the `F` and `Num` lines as they were.
- **The links the new panels write all resolve, from the source:** 32 links, 0 unresolved (routes from `app/**/page.tsx`, method notes in `docs/methods/`, anchors from the code that writes each id).

## Each panel at 390 px, from the code

| Panel (session) | Stacks | Tables scroll in their frame | Chart: viewBox, full width | Hover by tap or keyboard | Before | After |
|---|---|---|---|---|---|---|
| Page layout `app/grid/page.tsx` | yes (`lg:` two columns, `min-w-0` both) | n/a | n/a | n/a | holds | holds |
| `grid_network_<grid>` NetworkFigures (1151) | yes | `ToolTable` (380 and 420 px, scroll region) | none | tips are `title` only (as every keyed figure) | holds | holds |
| `grid_gravity_<grid>` GravityFigures (1151) | yes | `ToolTable` (460 px) | none | as above | holds | holds |
| `grid_clean24_<grid>` (1151) | yes | `ToolTable` | shared chart | shared chart | holds | holds |
| `grid_mix_<grid>` MixFigures (1152) | yes | **no**: frames not keyboard reachable, rows without a header cell | `TimeChart`, viewBox, measured width | tap fires a mouse move; the Chart/Table toggle carries every value | does not hold | holds |
| `grid_scarcity_<grid>` ScarcityPanel (1154) | yes | the Table view is `DataTable` (scroll region) | `HeatChart`, viewBox, measured width (about 9 px cells at 390) | tap fires a mouse move; Chart/Table toggle | holds | holds |
| `grid_caisoalert_caiso` CaisoAlertState (1155) | yes | no table | none | `title` tips | holds | holds |
| `grid_ask_<grid>` AskExamples (1157) | yes, under the tabs | no table | none | each answer a `<details>` with its summary | **no**: long filters overflow | holds |
| Map shape, NetworkMap (1156) | yes (the map's proportions) | n/a | viewBox, `w-full h-full` | regions by focus, lines by pointer only; **image role over focusables; cards cut off and closed by a tap's leave** | does not hold | holds (lines by tap; still no keyboard route to a line, see "For Samuel's ruling") |
| Gravity shape, NetworkGravity (1153) | yes (square) | n/a | viewBox, `w-full h-full` | circles by focus; **group role on svg; cards cut off, closed by a tap's leave** | does not hold | holds |
| `/grid/caiso/alerts` line (1155) | yes | unchanged | unchanged | unchanged | holds | holds |

Count: **7 of 11 held before, 11 of 11 after** (from the code; the live measure is check-390 on a build, under "To finish").

## AccessLint counts, by rule

| Page or panel | Source | Before | After |
|---|---|---|---|
| `/grid` (Lower 48, Mix) | production HTML, session 1150 | 0 | waits for a build (same markup plus the new panels below) |
| `/grid?grid=caiso` (Mix) | production HTML | 0 | waits for a build (`grid_caisoalert_caiso` and the scarcity strip are async server reads) |
| `/grid?grid=ercot&view=network` | production HTML | 0 | waits for a build |
| `/grid/caiso/alerts` | production HTML | 0 | waits for a build |
| `grid_network_ercot`, `grid_network_us48`, `grid_gravity_ercot` | rendered on the committed snapshot | 0 | 0 |
| `grid_mix_ercot` hourly and monthly, at 324 px | rendered on session 1152's fixture | 1 (`keyboard-accessible/scrollable-region`, serious) | 0 |
| `grid_ask_spp`, `grid_ask_nyiso` | rendered on the committed examples | 0 | 0 |
| The map's drawing (its regions and links) | its markup, by hand | 1 (`aria/presentational-children-focusable`, serious) | 0 (with `role="group"` instead: 1, `aria/aria-allowed-role`, minor; so no role) |
| The gravity shape's drawing | its markup, by hand | 1 (`aria/aria-allowed-role`, minor) | 0 |

Rendered without a server: `react-dom/server` `renderToStaticMarkup` on each component with no server-only import and no database read (NetworkFigures, GravityFigures, HourlyFigures, MonthlyFigures, AskExamples), the `.tsx` transpiled by the site's own `typescript`. `CaisoAlertState` and `ScarcityPanel` read the database in the component (async): their after count waits for a build. Classes, `data-*` and `title` were stripped, each `tbody` cut to two rows and each svg to its title before `audit_html`; the scroll frames kept their overflow and the tables their `min-width` as inline styles, in a 324 px wrapper (390 less the gutters).

## Links, from the source

32 links written by the new panels and the pages they touch, each to a route that exists, each fragment to an id the page's code writes: CaisoAlertState (4), ScarcityPanel (4), the alerts page's line and its links (7), the mix chips (2, to `#hourly`), the map's seven grid links, the Gravity tab's picker (8). 0 unresolved. `check-links.mjs` itself needs a server and a browser: under "To finish".

## What to review

After the chain's combined landing, on production:

1. Open `https://erw-flame.vercel.app/internal/open`, paste the token, press **Open the internal view**.
2. On a phone, or with the browser at 390 px wide: open `https://erw-flame.vercel.app/grid?grid=ercot&mixp=month#hourly`. Press Tab until the monthly table's frame is outlined, then press the right arrow: the table scrolls.
3. Open `https://erw-flame.vercel.app/grid?grid=ercot&view=network&shape=map` at 390 px. Tap the middle of the line from SPP to ERCOT: the card opens and stays inside the map. Tap an empty part of the map: it closes.
4. Open `https://erw-flame.vercel.app/grid?grid=ercot&view=gravity&shape=gravity` at 390 px. Tap a line, then a circle: each card stays inside the square.
5. Open `https://erw-flame.vercel.app/grid?grid=spp#ask` at 390 px. Open the fifth stored answer: the `where=` filter wraps inside the column.
6. At 1280 px: the same addresses look as before (the cards are as wide as before, 20rem, where there is room).

## Checks

- Precheck for session 1158: run by the orchestrator, exit 0.
- `audit_html` (AccessLint MCP), 4 production pages and 3 groups of rendered panels before, 2 after, 3 markup cases for the drawings: results above.
- `node scripts/test-grid-390.mjs` (new, 5 tests): exit 0.
- `node scripts/test-network-map.mjs`: exit 0, 9 tests (unchanged; session 1156's test pins "9 tests passed", so the new checks are in their own file).
- `node scripts/test-mix-hourly.mjs`: exit 0. `node --import ./scripts/alias-register.mjs scripts/test-grid-ask.mjs`: exit 0, 269 of 269. `node scripts/test-grid-keys.mjs`, `test-caiso-alerts.mjs`, `test-scarcity-strip.mjs`: exit 0 each.
- `python -m unittest`, one file at a time: `tests.test_session1158` (new), `1152`, `1155`, `473`, `1156`, `180`, `193`, `237`, `1153`, `266`, `299`, `583`, `1157`, `412`, `1154`, `168_network`: exit 0 each (1156 failed once, on the node test's count, before the new checks moved to their own file).
- The source link check (scratch script, routes and ids): exit 0, 32 links, 0 unresolved.
- `npm run content`, `npx next typegen`, `npx tsc --noEmit -p .` in `site/`: exit 0 each.
- No `db_probe`, no build lock, no build (the orchestrator's memory instruction).
- `audit_html` starts a headless Chrome of its own (AccessLint's, a debugging port, launched 20:46 UTC): stopped by its PID at 21:00 UTC; no Chrome left running.

## The landing

- None in this session: no build, and the chain lands its sessions together once the database answers (the brief). The branch is pushed: `wip/1158-grid`.

## To finish

- With a build of the chain's landing B (the lock free, `db_probe` 0, memory enough): `npm run build` in `site/`, `next start -p 3158`, then each as its own command, exits read:
  - `node scripts/check-390.mjs http://localhost:3158 runs/session1158/w390.json docs/brand/review-1158 --pages /grid,/grid?grid=ercot,/grid?grid=caiso,/grid?grid=ercot&mixp=month,/grid?grid=ercot&view=network&shape=map,/grid?grid=ercot&view=gravity&shape=gravity,/grid?grid=spp,/grid/caiso/alerts,/network` (`MSYS_NO_PATHCONV=1`); expected: no table outside a scroller, nothing past the right edge.
  - `CHECK_LINKS_PAGES=/grid,/grid/caiso/alerts,/network node scripts/check-links.mjs http://localhost:3158`; expected 0 findings.
  - AccessLint's live scan (`audit_live`) on `http://localhost:3158/grid`, `/grid?grid=caiso`, `/grid?grid=caiso#scarcity`, `/grid?grid=ercot&view=network&shape=map`, `/grid?grid=ercot&view=gravity&shape=gravity`, `/grid/caiso/alerts`, in the internal view: the after counts for the async panels and the client drawings, contrast included.
  - Screenshots at 1280 and 390 of the same pages under `docs/brand/review-1158/`.
  - `MSYS_NO_PATHCONV=1 CHECK_VALUES_PAGES=/grid,/network node scripts/check-values.mjs http://localhost:3158`: no key added or removed, every value matching.
  - Stop the server by its PID and its port; release the lock.
- Land `wip/1158-grid` with the chain's combined landing. Expected differences: the served HTML of the Mix tab's energy mix panel (the two table frames gain `tabindex`, `role="region"` and a name; each fuel's cell becomes a row header; the swatch `aria-hidden`) and the Ask column's `<details>` (`break-words`); everything else is drawn in the browser (the map and gravity svgs lose their role; the cards' width; the tap). No number.

## Decisions made without you

- The AccessLint before counts were taken on the saved production HTML reduced to fit the tool (scripts, styles, svg drawing data and repeated rows and options cut), not on the whole files: they are 240 to 590 KB, mostly the page's script payload, which the rules do not read.
- The new panels' after counts were taken on the components rendered on their tests' fixtures, not on a build, as the orchestrator allowed; the two async panels are listed as waiting.
- Neither drawing takes a role: the svg's own (graphics document) with its name, since AccessLint flags `img` over focusable children and does not allow `group` on an svg. The gravity shape had `group` since session 583; it was a minor finding, changed with the map's.
- A finger's card stays open until the next tap (on another line, a circle or the empty drawing), as a phone has no hover to leave.
- The checks of this session are a new node test, `scripts/test-grid-390.mjs`, not more tests in `test-network-map.mjs`, whose count session 1156's python test pins.
- `site/node_modules` was a junction to the main checkout's (identical lock file) instead of an `npm ci`, to spare memory; it was removed (the link only) before the hand-over.

## For Samuel's ruling

- A line of the map and of the gravity shape answers a pointer and a tap but not the keyboard: its figure is in the keyed panel under the drawing; a keyboard stop on each line (dozens on the map) is a design choice, not made here.
- The shared charts (`svgchart.tsx`, `TimeChart.tsx`) answer a mouse or a tap, not the keyboard; their Chart/Table toggle carries every value. A keyboard walk through a chart's points is a shared-component change for the brand pass or a session you name.
- Colour contrast was not judged on these pages without the stylesheet: the live scan under "To finish" does it.

## Files

- `site/components/grid/MixFigures.tsx`: the two table frames as scroll regions, row header cells, swatches hidden.
- `site/app/network/NetworkMap.tsx`, `site/app/network/NetworkGravity.tsx`: no role on the svg, the cards' width, the tap, the touch-aware leave.
- `site/lib/networkMap.ts`: `cardWidth`.
- `site/components/grid/AskExamples.tsx`: `break-words`.
- `site/scripts/test-grid-390.mjs` (new), `tests/test_session1158.py` (new).
- `archive/sessions/SESSION_1158_REPORT.md`.
