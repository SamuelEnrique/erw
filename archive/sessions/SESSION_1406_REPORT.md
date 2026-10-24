# Session 1406 report: the Lower 48 on the Network tab

24 October 2026, from about 07:00 to 07:35 UTC, on samueloldlaptop (the code machine, the old laptop), the seventh session of `queue/done/100-day-26-october-code-grid-tool-4.md`. Branch `wip/1406-grid`, cut from `wip/1405-grid` (sessions 1152 to 1405 stacked, not on main), worktree `C:\Users\lossa\Documents\erw-1406`. Code, tests and documents only (`runs/c077/brief.md`: no build, no server, no browser). Model spend USD 0. No warehouse data written, no Supabase write, no request to any publisher. Light reads of Supabase's REST API with the anon key: one read of `eia930:US48` (4 rows, to learn it is held), one fixture of 168 rows, and same-figures' answers held in memory.

## Read these first

- **The Lower 48's Network panel now draws the Lower 48.** Under the seven grids' net exchange (`grid_network_us48`), whose table, 14 figures and file stand as they were, a block "The seven grids' demand and the Lower 48's, the same hour (...)" (`site/components/grid/Lower48Demand.tsx`, `data-grid-lower48`, `#lower48-demand`), from the same hour and the same reads:
  - **each of the seven grids' demand**, the grid in view's own figure, chosen and keyed as its own panel does it (`demandAt`: `netsnap|<BA>|demand_mw|<hour>` from the hourly snapshot, else `series|eia930_all_demand|eia930:<BA>|demand_mw|<hour>`);
  - **the Lower 48's own demand**, EIA-930's US48 (`series|eia930_all_demand|eia930:US48|demand_mw|<hour>`);
  - **the seven's sum** (`calc|add|<D1>|...|<D7>`) and **its share of the Lower 48** (`calc|addpct|<D1>|...|<D7>|<US48>`), each only when all seven hold a demand in the hour;
  - **the seven's exchange in words**: "In the hour, the seven together took in, on net, 12,246 MW over their ties with the grids around them: they took in 7,190 MW from the rest of the Lower 48, and took in 5,056 MW from Canada's and Mexico's operators." Each of the three is a keyed figure: a size, its direction in words, keyed by the operands that give the size (`calc|add|` of `net|export|`/`net|import|` and `net|tie|` keys).
- **The rest of the Lower 48 is not the sum of the net exports alone.** Six of the seven hold ties to Canada or Mexico (CEN, HQT, NBSO, IESO, MHEB, SPC), so the sum is the exchange with every grid around them. The block says both, and the part abroad (`OUTSIDE_US48` in `lib/gridKeys.ts`).
- **On the committed snapshot** (built 2026-10-23 14:36 UTC), hour 2026-10-21 23:00 UTC: ERCOT 61,145, CAISO 29,340, PJM 93,776, MISO 76,710, NYISO 17,501, ISO-NE 14,120, SPP 34,680 MW; the seven 327,272 MW, 65.77 percent of the Lower 48's 497,563 MW.
- **No new key kind.** Two ops of `calc` in `site/scripts/check-calc.mjs`: `add` (two operands or more) and `addpct` (three or more, the last the whole). check-values and check-methods read a calc key by its operands, every one of a kind they know and the note names. The op is not `sum`: session 1165's test holds `calc|sum` to no value.
- **One line of the read**: `app/network/data.ts` `liveExtras` keeps `eia930:US48`'s rows of the demand read it already makes (the read returns every entity), aligned as the seven's. The network draws no US48 node, so nothing on the map moves; no new request.
- **A failed read** of `eia930_all_demand`: the Lower 48's demand and the share say "could not be read" (session 1181's look); each grid's demand the hourly snapshot holds stands, and the sum with it. An empty read says "not held".
- **A fault found in three tests' stand-ins, fixed.** `test-grid-files.mjs`, `test-grid-failed-reads.mjs` and `grid-render-standin.mjs` read `fixtures/grid_balance.json`'s week as one value an hour, but it holds `[ts_utc, value]` rows: six grids' demand and generation were NaN in every render (ERCOT's came from another fixture). Now read as rows. In the render test, CAISO's and ISO-NE's balance gain their week (4 to 6 figures) and the four gravity tables their seven shares (15 to 21); a NaN now counts as a figure without a value.

## What to review

After the chain's combined landing (none yet; below), on production:

1. Open `https://erw-flame.vercel.app/internal/open`, paste the token, press **Open the internal view**.
2. Open `https://erw-flame.vercel.app/grid?grid=us48&view=network` (or `/grid?view=network`). Scroll under the network: "The seven grids, the hour shown" as before, then "The seven grids' demand and the Lower 48's, the same hour". Read the two sentences (the exchange, the demand), then the table: seven rows, "The seven together" and the share highlighted, "The Lower 48 (EIA-930's US48)".
3. Hover each dotted figure: its table, entity or ties, hour and the snapshot's refresh. Hover "took in ... from Canada's and Mexico's operators": the ties it sums are named.
4. Press "Download this table (CSV)" under the new table: `erw_grid_network_us48_demand.csv`, its header with the three exchange figures and their keys.
5. Open `https://erw-flame.vercel.app/grid?grid=us48&view=network#lower48-demand`: the page opens on the block. Press "Method: the Lower 48 on the Network tab": the section of `grid_network` opens.
6. View source, search `data-grid-lower48` and `calc|addpct|`.
7. Screenshots: not taken, no build.

## Checks

- Precheck: run by the orchestrator, exit 0.
- `node scripts/test-grid-lower48.mjs` (new, 8 tests, on `data/grid_network.json`, `fixtures/grid_balance.json` and the new `fixtures/lower48_demand.json`): exit 0. Every one of the 13 keys recomputed by check-values' rules (netValue, the rows, check-calc) to the block's value; each grid's demand equal to its own panel's; the exchange's parts add up and equal the ties to grids outside the seven; the Lower 48's table of net exchange keeps its 14 keys and values; the not held and failed cases; `add` and `addpct`, and `sum` still no op.
- Node tests, one at a time (`--import` the alias and tsx loaders where the test needs them), each exit 0: `test-grid-render` 72 of 72 (the Lower 48's Network case updated: 27 figures, its words, keys, two anchors, two methods, two files; six cases' counts raised, above), `test-grid-files` 104 cases (one new: the block's figures, files, anchor, and its method id rendered by `lib/markdown.ts`), `test-grid-failed-reads` 74 cases (three new: `eia930_all_demand` timeout, HTTP 500, empty on the Lower 48's Network tab), `test-check-values-light` 8, `test-clean-week`, `test-grid-addresses` 12, `test-grid-balance` 11, `test-grid-exchange`, `test-grid-file-keys`, `test-grid-keys` 8, `test-grid-methods`, `test-hub-price`, `test-network-map` 9.
- `same-figures.mjs`: before `93c0269e` (the tip of `wip/1405-grid`, a temporary detached worktree with its own junction, both removed), after this tree, 7 addresses: the Lower 48's Network tab (`/grid?grid=us48&view=network` and `/grid?view=network`) and Gravity tab (`shape=gravity`), ERCOT's and CAISO's Network tabs, ERCOT's Gravity tab, `/grid`. Exit 1 because the two Lower 48 Network addresses differ by additions only: a one-off (`runs/s1406/additions.mjs`) holds each after list to the before list with one run of 16 figures (13 keys, three drawn twice) taken out, held figures and panels the same. The other 5 pages are the same. 267 figures compared, 57 distinct requests, 0 new after.
- The new keys recomputed live (a one-off, one anon read): on the live hour 2026-10-22 03:00 UTC, the 8 `series` keys and the sum and share, 10 of 10 (the seven 286,179 MW, 65.58 percent of the Lower 48's 436,394 MW); the exchange total (8,335 MW taken in) equals the page's seven net exports summed, its parts 6,165 and 2,170.
- check-methods' `figures` and `named` on the new keys: 55 of 55 figures named by `grid_network.md`. `node scripts/check-methods.mjs` (no server): exit 0, 553 of 553. `node --check` on `check-values.mjs` and `check-calc.mjs`: exit 0.
- `python -m unittest`, one file at a time, the 72 files that read a changed file (grep of `tests/` for the changed files' names, and the files that walk `site/`): 72 exit 0, 1,039 tests. `tests.test_session1406` (new, 7 tests, it runs the node test) among them.
- Type check through the junction: `npm run content` exit 0, `npx next typegen` exit 0, `npx tsc --noEmit -p .` exit 0; the junction removed (`cmd /c rmdir`), the main copy's `node_modules` intact.
- No build, no check-values run against a page: none possible without a build.

## The landing

- None: waits for the database, with the chain's combined landing (`wip/1188-grid` and the sessions stacked on it). The branch is pushed: `wip/1406-grid`.

## To finish

- At the combined landing: the build; check-values on `/grid?grid=us48&view=network` and `/grid?view=network` (13 new keys each: 8 `series` of `eia930_all_demand`, 5 `calc` of the two new ops), the floors rewritten from a passing restricted run (`CHECK_VALUES_WRITE_FLOOR=1`); `check-methods.mjs --values <the run> --write`; check-links on `#lower48-demand` and `METHOD_NETWORK_US48`; check-390 on the new table; screenshots at 1280 and 390 under `docs/brand/review-1406/`; the snapshots before and after (expected: no difference on the snapshot's addresses, none of which is the Lower 48's Network tab).

## Decisions made without you

- The rest of the Lower 48 is the seven's net exports less their ties to Canada's and Mexico's operators; the sum alone is said as the exchange "with the grids around them", and the part abroad beside it.
- Two ops of `calc` (`add`, `addpct`), not a new key kind; named `add` because session 1165's test holds `sum` to no value.
- A size and a direction in words for each exchange figure, keyed by the operands that give that size, as the grid in view's own sentence writes its net.
- The sum and the share only when all seven hold a demand in the hour; the Lower 48's demand has no fallback (the snapshot has no US48 node).
- The block is its own file (`Lower48Demand.tsx`): `tests/test_session1153.py`, `1159` and `1182` count `<F `, `className="mt-10">` and `<PanelFile ` in `NetworkFigures.tsx`, which gains one line (the block) and one import. Its anchor and method sit outside `GRID_ANCHOR` and `GRID_METHOD`, as sessions 1402 and 1403 placed theirs (`LOWER48_DEMAND_ANCHOR`, `METHOD_NETWORK_US48`).
- The stand-ins' reading of `grid_balance.json` fixed in the three tests, and the six render cases' counts raised to what is drawn: the counts encoded NaN figures, not a decision of 1404's.
- `tests/test_session473.py`: `Lower48Demand.tsx` added to its own components (one `check=`) and to the files that may take `Missing` from `components/mix/Now.tsx`, as 1170, 1402 and 1403 did; no assertion removed.

## For Samuel's ruling

- Whether the Lower 48's share should also be said against the Lower 48 less the seven ("the other balancing authorities"), a figure the block leaves to the reader.

## Files

- New: `site/components/grid/Lower48Demand.tsx`, `site/scripts/test-grid-lower48.mjs`, `site/scripts/fixtures/lower48_demand.json`, `tests/test_session1406.py`, this report.
- Changed: `site/lib/gridKeys.ts` (`OUTSIDE_US48`, `lower48DemandAt`, `lower48Demand`), `site/scripts/check-calc.mjs` (`add`, `addpct`), `site/components/grid/NetworkFigures.tsx` (one line, one import), `site/app/network/data.ts` (US48 kept), `site/lib/gridAnchors.ts`, `site/scripts/test-grid-render.mjs`, `site/scripts/grid-render-standin.mjs`, `site/scripts/test-grid-files.mjs`, `site/scripts/test-grid-failed-reads.mjs`, `docs/methods/grid_network.md` (the section "The Lower 48 on the Network tab (chain 100, 24 October 2026)" with its Decisions, and the key list), `tests/test_session473.py`.
