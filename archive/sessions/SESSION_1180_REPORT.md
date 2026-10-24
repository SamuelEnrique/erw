# Session 1180 report: a test fixed for Windows, and the storage units and the snapshot, read once

24 October 2026, from about 02:10 to 02:40 UTC, on samueloldlaptop (the code machine, the old laptop), the third session of `queue/done/091-day-25-october-code-grid-tool-3.md`. Branch `wip/1180-grid`, cut from `wip/1179-grid` (chains 077, 078 and 091 stacked, not on main), worktree `C:\Users\lossa\Documents\erw-1180`. Code, tests and documents only (`runs/c077/brief.md`: no build, no server, no browser). Model spend USD 0. No warehouse data written, no Supabase write, no request to any publisher; light reads of Supabase's REST API and the public snapshot object with the anon key (below).

## Read these first

- **Part 1: `site/scripts/test-network-split.mjs` (session 1175) now passes on this checkout.** It matched `"graph.current = g;\n      setSceneReady(true);"` in `app/network/Network.tsx`, which git checks out here with CRLF (`core.autocrlf=true`), so it exited 1 on Windows and would have failed the landing gate. It now reads every source it scans or matches with line endings normalised (`lf(...)`, `.replace(/\r\n/g, "\n")`, in `read` and in `parse`); no assertion changed. Every other test chains 077, 078 and 091 added was run here, one at a time: the 19 other node tests (`site/scripts/test-*.mjs` added since session 1150) and the 23 python modules (`tests/test_session1152` to `1179`) each exit 0; three already normalise (`test-check-revised`, `test-grid-ask`, `test-grid-stress`), and python's text mode reads CRLF as LF. None other assumes LF.
- **The battery units: one small read a grid, not the whole table.** The Mix and Clean tabs of each ISO grid read `storage_capacity` whole (`lib/data.ts storageUnits`: 1,627 units, two requests, seven columns) and kept the grid's units in `lib/grid.ts load`. Now `load` calls `lib/gridReads.ts gridStorageUnits(g.iso)`: `extra->>iso=eq.<ISO>` (the filter `lib/chat/tools.ts` already uses on this table), the three columns the Batteries block draws (`capacity_mw`, `status`, the MWh), ordered by `entity_id` as the whole read was, so each sum adds the same numbers in the same order. `storageUnits` is unchanged for `/storage`, the home page and the battery game.
- **The snapshot on the Gravity tab: read once, fresh.** Session 1160 called the double read "on purpose": the Exchange blocks read the snapshot fresh (`fetchHourly(0)`) since session 237 so a number shown is the object's own (check-values reads it fresh; an hourly refresh between a cached read and the check had revised four of PJM's ties). **That reason holds for the fresh read, which is kept; it does not call for the second, hourly-cached read beside it.** Now `lib/gridReads.ts freshSnapshot` (React's `cache` over `fetchHourly(0)`) is read once a render by the Exchange blocks and by the network component when its shape is the Gravity tab's (`shape="gravity"`, passed only there), so the tab's panel `grid_gravity_<grid>` and the Exchange blocks draw one version of the snapshot. The Network tab keeps its one hourly read (the pinned `pickSnapshot(await fetchHourly(HOURLY), committed)`), the Now view its own fresh one.
- **No figure moved, proved on live answers without a build:** `site/scripts/same-figures.mjs` (new, session 1179's one-off made a script) drew 25 addresses with the code before (`43b031af`, a temporary worktree, removed) and after on the same answers (a proxy on 127.0.0.1 kept every answer in memory, each distinct request sent once): 2,569 figures, every `data-check` key, `data-raw` value and text the same, page by page, in order, the held figures and panel names the same; the 28 battery figures (`storage|iso_mw|...`, `storage|iso_mwh|...`) and 390 network figures (`net|`, `nettie|`, `netbal|`, `calc|bal|`) among them. The seven requests only the tree after made are the seven narrowed units reads.
- **The Clean tab draws no battery units** (the Batteries block is the Mix tab's) yet `load` reads them there too: one small request now; left (decision below).

## Requests and rows, before and after

`site/scripts/time-grid-reads.mjs` (session 1179's walk, one render a page), one request at a time, each distinct request three times; before 02:19:04 to 02:19:51 UTC, after 02:21:13 to 02:21:57 UTC; `db_probe` 0.70 s at 02:18:57 (exit 0). "Asks" counts each time a page asked (the snapshot is one distinct request either way: both readers asked for the same object).

| Page | Requests before | After | Rows before | After | Units requests | Units rows | Snapshot asks |
|---|---|---|---|---|---|---|---|
| `/grid?grid=ercot&view=mix` | 61 | 60 | 37,956 | 36,735 | 2 to 1 | 1,627 to 406 | 1 to 1 |
| `/grid?grid=caiso&view=mix` | 70 | 69 | 48,432 | 47,210 | 2 to 1 | 1,627 to 405 | 1 to 1 |
| `/grid?grid=pjm&view=mix` | 48 | 47 | 32,115 | 30,559 | 2 to 1 | 1,627 to 71 | 1 to 1 |
| `/grid?grid=miso&view=mix` | 50 | 49 | 32,327 | 30,766 | 2 to 1 | 1,627 to 66 | 1 to 1 |
| `/grid?grid=nyiso&view=mix` | 49 | 48 | 32,126 | 30,589 | 2 to 1 | 1,627 to 90 | 1 to 1 |
| `/grid?grid=isone&view=mix` | 50 | 49 | 33,693 | 32,247 | 2 to 1 | 1,627 to 181 | 1 to 1 |
| `/grid?grid=spp&view=mix` | 53 | 52 | 34,103 | 32,506 | 2 to 1 | 1,627 to 30 | 1 to 1 |
| each grid's `view=clean` (7) | 17 to 23 | one fewer each | 11,627 to 13,882 | 1,221 to 1,597 fewer | 2 to 1 | as its Mix tab | 0 |
| each grid's `view=gravity` (8, the Lower 48's too) | 19 | 19 | 9,894 | 9,894 | 0 | 0 | 2 to 1 |

Across the 22 addresses: 674 requests to 660, 419,636 rows to 399,356, 796 asks to 774, the sum of the medians 44,612 ms to 42,159 ms. Distinct requests across the run 203 to 208 (the two shared whole-table pages became seven per-ISO reads, each page asking one). Every page: `runs/s1180/summary.md`; every request, its times and pages: `runs/s1180/reads_before.json`, `reads_after.json` (this machine, not committed).

## What to review

After the landing (none yet; below), on production:

1. Open `https://erw-flame.vercel.app/internal/open`, paste the token, press **Open the internal view**.
2. Open `https://erw-flame.vercel.app/grid?grid=ercot`, scroll to **Batteries**: "Operating: 18,204.50 MW, 30,019.80 MWh", under construction and planned read as before (values of 24 October 02:25 UTC); hover a dotted figure: `storage|iso_mw|ERCOT|operating` as before. The same on `grid=pjm` and `grid=spp`.
3. Open `https://erw-flame.vercel.app/grid?grid=ercot&view=gravity`: the panel under the shape and the Exchange blocks under it read as before; their hour is the same hour.
4. Read `site/lib/gridReads.ts` (the session 1180 block), `lib/grid.ts load`, `components/grid/NetworkView.tsx` (the one line) and `components/grid/ExchangeView.tsx`.
5. Run the proof yourself: from `site/`, with a checkout of the commit before as `<before>`, `node scripts/same-figures.mjs --env <file with SUPABASE_URL and SUPABASE_ANON_KEY> --before <before> --after .. --only "/grid?grid=ercot&view=mix,/grid?grid=ercot&view=gravity" --out ../runs/x` (Git Bash: `MSYS_NO_PATHCONV=1`; the before tree needs `site/node_modules` and `npm run content`).
6. Screenshots: not taken, no build.

## Checks

- Precheck for session 1180: run by the orchestrator, exit 0.
- `scripts/db_probe.py` from the main checkout: exit 0, open, 0.70 s (02:18:57 UTC). No build all the same (the brief).
- Part 1: `node scripts/test-network-split.mjs`: exit 1 before the change (the assertion "ready once the graph is built"), exit 0 after (7 tests). The 19 other node tests of chains 077, 078 and 091, one at a time (`caiso-alerts`, `check-revised`, `ercot-notices`, `gravity`, `grid-390`, `grid-balance`, `grid-exchange`, `grid-keys`, `mix-hourly`, `network-map`, `scarcity-strip`; `grid-addresses`, `grid-ask` with the alias loader; `grid-file-keys`, `grid-generation`, `grid-held`, `grid-reads`, `grid-replay`, `grid-stress` with both loaders): each exit 0. `python -m unittest tests.test_session<N>` for 1152 to 1162, 1165 to 1168, 1170 to 1176, 1179: each exit 0.
- `time-grid-reads.mjs` on 22 addresses, before: exit 0, 203 distinct requests, 0 failed, 0 refused, 0 component errors; after: exit 0, 208, 0, 0, 0.
- `same-figures.mjs` on 25 addresses: exit 0, every page the same, 2,569 figures; 215 distinct requests (208 by the tree before, 7 new by the tree after: the narrowed units reads).
- `node --import ./scripts/alias-register.mjs --import ./scripts/tsx-register.mjs scripts/test-grid-units.mjs` (new): exit 0, 20 cases. With `ExchangeView` put back on `fetchHourly(0)`: exit 1 ("the Gravity tab ... 2 fetch(es)"); restored.
- Node tests that read a changed file, one at a time: `test-check-revised`, `test-grid-exchange`, `test-network-split`, `test-grid-addresses`, `test-grid-generation`, `test-grid-reads`, `test-grid-units`, `test-grid-held`, `test-grid-file-keys`: each exit 0.
- `python -m unittest`, one module at a time, every test that reads a changed file: `test_session109`, `114_part2`, `1156`, `1160`, `1162`, `1165`, `1166`, `1167`, `1170`, `1171`, `1172`, `1175`, `1176`, `1179`, `118`, `1180` (new, 10 tests), `120_page`, `122`, `123`, `124`, `137`, `148`, `168_network`, `180`, `180b`, `193`, `237`, `247`, `266`, `299`, `381`, `411`, `473`, `502`, `538`, `54`, `58`, `583`, `78`, `92`, `93`: each exit 0 (skips as before). No assertion changed or removed.
- `npx eslint` on the eight changed or new code files: exit 0.
- Type check through the junction (`mklink /J` to the main checkout's `node_modules`): `npm run content` exit 0, `npx next typegen` exit 0, `npx tsc --noEmit -p .` exit 0; the junction removed with `rmdir`.
- Not run: the build, check-values, check-routes, screenshots (no build, the brief).

## The landing

- None in this session: chain 091 works code-only, stacked on `wip/1176-grid` (chains 077 and 078, not on main). This branch lands with them. Pushed: `wip/1180-grid`.

## To finish

- Land with the chain's combined landing: the build; **check-values** on `CHECK_VALUES_PAGES=/grid?grid=ercot,/grid?grid=pjm,/grid?grid=spp,/grid?grid=ercot&view=gravity,/grid?grid=pjm&view=gravity` (Git Bash, `MSYS_NO_PATHCONV=1`): the `storage|iso_*` keys and the gravity tab's `net|`, `nettie|` keys recompute as before; the snapshots before and after, every difference listed (expected: none from this session).
- At that build, `ERW_READ_TIMING=1` and `node scripts/slow-reads.mjs <the build log> 20`: `storage_capacity` read with `extra->>iso=eq.<ISO>` once per ISO grid page, never whole on `/grid`.
- The landing gate's suite on this machine: `test-network-split.mjs` (and `tests/test_session1175`, `1180`) now pass on Windows.

## Decisions made without you

- **Part 1 normalises in the test, not in `.gitattributes`**: pinning `Network.tsx` to LF would change a site source's checkout for one test; the test reads LF whatever the checkout.
- **The Gravity tab's double read was not left**: its reason (the Exchange blocks' numbers are the object's own) is met by the one fresh read; the hourly read beside it only allowed the panel and the blocks to draw two versions. Reading fresh once costs the tab no more requests than before (it already sent the fresh one).
- **The shared read is a `cache` in `lib/gridReads.ts`, not in `lib/network.ts`**, which keeps no imports beyond types (a test loads it in Node); the network component takes it only for `shape="gravity"`, so the pinned hourly call stands for every other tab.
- **The units are filtered by PostgREST with no index**: `extra->>iso` has none, but the filter runs over the 1,627 rows `table_name` finds; no migration.
- **The Clean tab's units read is kept**: `load` serves both tabs and knows no tab; one small request.
- **The fixture is a subset of real rows** (`site/scripts/fixtures/grid_units.json`: PJM, SPP and MISO whole, every tenth other unit, 313 of 1,627, in the warehouse's order, which is its collation's, not the code points'), to keep the file at 42 KB.
- **The proof tool is committed** (`same-figures.mjs`) as the prompt asked, since 1179's was not in the repository; it writes only the two figure lists, never the answers. A request only the tree after makes is listed, not counted as a failure.

## For Samuel's ruling

- None new.

## Files

- New: `site/scripts/same-figures.mjs`, `site/scripts/test-grid-units.mjs`, `site/scripts/fixtures/grid_units.json`, `tests/test_session1180.py`, this report.
- Changed: `site/scripts/test-network-split.mjs` (line endings normalised), `site/lib/gridReads.ts` (`GridUnit`, `gridUnitsQuery`, `gridStorageUnits`, `freshSnapshot`), `site/lib/grid.ts` (`load`'s units), `site/components/grid/YourGrid.tsx` (the Batteries sums' types), `site/components/grid/NetworkView.tsx` (the Gravity tab's read), `site/components/grid/ExchangeView.tsx`, `docs/methods/grid_network.md` (the section "The storage units and the snapshot, read once (chain 091, 24 October 2026)" with its Decisions).
- On this machine only: `runs/s1180/` (the two timing runs and the summary, the figure lists, the test outputs).
