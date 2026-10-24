# Session 1424 report: the Gravity and Exchange tabs at 390, from the code

24 October 2026, from about 11:30 UTC, on samueloldlaptop (the code machine, the old laptop), the sixth session of `queue/done/111-day-28-october-code-grid-tool-6.md`. Branch `wip/1424-grid`, cut from `wip/1423-grid` (sessions 1152 to 1423 stacked, not on main), worktree `C:\Users\lossa\Documents\erw-1424`. Code, tests and documents only (`runs/c077/brief.md`: no build, no server, no browser). Model spend USD 0. No warehouse data written, no Supabase write, no request to any publisher; light anon reads of Supabase's REST API (one same-figures walk, 19 distinct requests, the answers held in memory only).

## Read these first

- **Session 1158's rules already held on every table of the Gravity tab's blocks.** The gravity table (`grid_gravity_<grid>`), the Exchange blocks (session 1167's seven-column ties table at 680 px, the twelve months at 560 px, the Lower 48's seven grids at 360 px), the balance (1165, on the Network tab) and the replayed day's table (1170) are all the shared `ToolTable`: a scroll frame a keyboard reaches (`lib/cells.ts` `scrollRegion`, one tab stop, named by the caption), an `sr-only` caption, `scope="col"` on every head, the first cell of every row a `<th scope="row">` (the tie, the grid, the part of the balance). The gravity day line is a line of words with its one figure. No block sets a fixed width above 358 px outside a frame. The download lines (1182) and method lines (1184) are short text.
- **One miss, mended in markup and classes only.** A failed read's reason is drawn as written; a database error's body (for example `{"code":"57014","details":null,"hint":null,"message":"canceling ...`) runs about 60 characters without a space, past a 324 px column. Now:
  - `components/grid/ExchangeView.tsx`: the twelve months' `NoData` on a failed `ba_supply_monthly` read sits in `<div className="break-words" data-reason-wraps="1">`;
  - `components/grid/NetworkView.tsx`: the line "The last twelve months could not be read, so the panel shows none: ..." takes `break-words` and `data-reason-wraps="1"` (drawn on the Network and Gravity tabs).
  - A visitor sees either only when that read fails; no page's markup moves otherwise (the page sizes are byte for byte the same).
- **The render test now checks the frames on the drawn markup.** `site/scripts/grid-render-standin.mjs` records, for each block, its tables (caption, the scroll frame round it with its tab stop and name, column heads with and without a scope, body rows and their row headers) and any fixed width above 358 px outside a frame (inline `width` or `minWidth` in px or rem, `w-[Npx]`, `min-w-[Npx]`, `w-N` without a breakpoint, an svg's or img's width). `site/scripts/test-grid-render.mjs`: 13 cases carry `tables` (the four `grid_gravity_`, the four `view_exchange`, the two `gravityday`, the three `balance_`), each listing every table of its block in order; plus one check of the width reader itself. 182 cases, all hold. A mutated copy (a caption changed, a table added to a case) failed as it should.
- **New** `site/scripts/test-gravity-390.mjs` (6 tests): the same rules from the source; `tests/test_session1158.py` pins `test-grid-390.mjs`'s "5 tests passed", so this is a file of its own.
- **No figure moved.** `same-figures.mjs --sizes` on `/grid?grid=ercot&view=gravity&shape=gravity`, `caiso`, `us48`, code before (`bf274bde`) and after: 44, 107 and 39 figures, every one the same and in order; held 0/0, panels 2/2, errors 0/0; sizes +0 bytes; exit 0.

## What to review

After the landing (none yet; below), on production:

1. Open `https://erw-flame.vercel.app/internal/open`, paste the token, press **Open the internal view**.
2. At 390 px (a phone, or the browser's device view), open `https://erw-flame.vercel.app/grid?grid=ercot&view=gravity&shape=gravity`. Scroll to "What the gravity shape draws": press Tab until the table's frame is outlined, then the right arrow: the table scrolls. The same under "Each neighbour, that hour" (seven columns) and "Over the last twelve months".
3. Same page: nothing runs past the right edge (the paragraphs, the headline numbers, the download and method lines, the day line with `&net=day&t=2020-08-14`).
4. `https://erw-flame.vercel.app/grid?grid=us48&view=gravity&shape=gravity` at 390 px: "The seven grids, that hour" scrolls in its frame.
5. `https://erw-flame.vercel.app/grid?grid=caiso&view=network` at 390 px: "Does CAISO's balance close?" scrolls in its frame.
6. The failed read's wrap cannot be seen unless `ba_supply_monthly` fails; read the two lines in the code (above).
7. From `site/`: `node scripts/test-gravity-390.mjs`, and `node --import ./scripts/alias-register.mjs --import ./scripts/tsx-register.mjs scripts/test-grid-render.mjs` (the 13 cases with `tables`).
8. Screenshots: not taken, no build.

## Checks

- Precheck for session 1424: run by the orchestrator, exit 0.
- Node, one at a time, exit 0 each: `test-gravity-390.mjs` (new, 6 tests), `test-grid-390.mjs` (5, unchanged), `test-grid-exchange.mjs`, `test-grid-balance.mjs`; through the alias and tsx loaders `test-grid-render.mjs` (182 cases, every case holds), `test-grid-files.mjs` (161 cases), `test-grid-failed-reads.mjs` (113 cases), `test-grid-replay.mjs`, `test-grid-held.mjs`.
- A mutated copy of the render test (one caption changed, a table added to a gravity day case): exit 1, the two cases failed by name; the copy deleted.
- `same-figures.mjs --sizes`, 3 addresses (above): exit 0. The temporary worktree of `bf274bde` and its junction removed.
- `python -m unittest`, one module at a time, 48 modules (every module that names `ExchangeView`, `NetworkView`, `grid-render-standin` or `grid_network.md`, and `1158`, `1424`): all exit 0, none stopped for memory: `test_session1424` (new, 8 tests), `109`, `114_part2`, `1156`, `1158`, `1162`, `1165`, `1167`, `1170`, `1171`, `1172`, `1175`, `1176`, `1180`, `1181`, `1182`, `1183`, `1184`, `1186`, `1188`, `120_page`, `122`, `123`, `124`, `1404`, `1406`, `1411`, `1412`, `1415`, `1420`, `1421`, `1422`, `148`, `168_network`, `180`, `180b`, `193`, `237`, `247`, `266`, `299`, `381`, `473`, `502`, `538`, `54`, `78`, `93`.
- Type check through the junction, once at the end: `npm run content` exit 0, `npx next typegen` exit 0, `npx tsc --noEmit -p .` exit 0; the junction removed with `rmdir`, the main copy's `node_modules` intact (335 entries).
- Not run (the brief): build, check-values, check-390 and check-links against a page, AccessLint on a page, screenshots; eslint (the junction was down by then; tsc passed).

## The landing

- None in this session. It lands with the chain's combined landing (`wip/1417-grid` and the sessions stacked on it, not on main; production answers HTTP 402). Pushed: `wip/1424-grid`.

## To finish

- At the landing: the build; check-390 on `/grid?grid=ercot&view=gravity&shape=gravity`, `/grid?grid=us48&view=gravity&shape=gravity`, `/grid?grid=ercot&view=gravity&shape=gravity&net=day&t=2020-08-14`, `/grid?grid=caiso&view=network` (every table in a scroller, nothing past the right edge); AccessLint's live scan of the same pages (`keyboard-accessible/scrollable-region` 0); the snapshots before and after (expected: no difference from this session, its markup drawn only on a failed read); screenshots at 1280 and 390 under `docs/brand/review-1424/`.

## Decisions made without you

- **The rules held already on every table**, so the only page change is the failed read's reason; nothing else was touched for look's sake.
- **The wrapper is local** (a `div` round the twelve months' `NoData`, a class on the network's line), not in the shared `NoData`, so no other page's markup moves.
- **The 390 checks are a file of their own** (`test-gravity-390.mjs`): `tests/test_session1158.py` pins `test-grid-390.mjs`'s count.
- **A case's `tables` lists every table of its block, in order**, so a table added later without its frame or caption fails its case; a case without `tables` is checked as before.
- **The balance's cases are included**, though it is drawn on the Network tab: the chain file names it with the Gravity tab's blocks.
- **The width reader counts rem as 16 px** and ignores widths behind a breakpoint (`sm:` and up apply above 390).

## For Samuel's ruling

- None new. Still open from session 1158: a keyboard route to each line of the map and the gravity shape, and through the shared charts' points.

## Files

- New: `site/scripts/test-gravity-390.mjs`, `tests/test_session1424.py`, this report.
- Changed: `site/components/grid/ExchangeView.tsx`, `site/components/grid/NetworkView.tsx` (the two wraps), `site/scripts/grid-render-standin.mjs` (tables, frames, widths), `site/scripts/test-grid-render.mjs` (13 cases' `tables`, the check, the reader's check, its header), `docs/methods/grid_network.md` (the chain 111 section: session 1424's paragraph and Decisions).
- On this machine only, in `runs/s1424/` of the worktree: every test's output, the same-figures lists, the one-off scripts.
