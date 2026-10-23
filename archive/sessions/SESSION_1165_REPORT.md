# Session 1165 report: a balance that closes, said where the figures are

23 October 2026, from about 22:35 UTC, on samueloldlaptop (the old laptop), the second session of `queue/done/078-day-24-october-code-grid-tool-2.md`. Branch `wip/1165-grid`, cut from `wip/1164-grid` (chain 077's landing B is not on main), worktree `C:\Users\lossa\Documents\erw-1165`. Code-only, as the brief sets chain 078: no build, no server, no browser. Model spend USD 0. No warehouse data written, no Supabase write, no request to any publisher; one light read of Supabase's REST API with the anon key (the fixture, below).

## Read these first

- **The Network tab now says whether the grid's balance closes.** Under the ties in `grid_network_<grid>`, a block `data-grid-balance="<BA>"`, "Does <grid>'s balance close? The hour shown, and the week", for each of the seven ISO grids (the three that close too). In the hour shown: net generation (`series|eia930_all_generation|...`), demand (the panel's own demand figure and key), the net export over the reporting ties (`net|export|...`, signed) and the gap, net generation less demand less net export (`calc|bal|<G>|<D>|<X>`). Over the snapshot's week: the mean size of the gap (its absolute value, session 360's measure) and the count of hours (`netbal|absmean|<BA>|<from>|<to>`, `netbal|hours|...`).
- **Two additions to check-values.** `calc` takes a new op `bal` with three operands (A less B less C); its arithmetic moved to `site/scripts/check-calc.mjs` (ratio, diff and pct as before, with a test). A new kind `netbal`, recomputed with the page's rule (`netbalValue`, `site/lib/gridKeys.ts`) on the snapshots the `net|` keys read (Storage first, then committed, each hour from the first that holds it) and the grid's rows of the two tables in the window.
- **The split of session 360 is in the hover tip** of the gap and of the week's figures, in one line (`BALANCE_SPLIT`); the block's note says in words, without a figure, where 360 found this grid's gap (`BALANCE_WHERE`) and links `/data/methods/eia930_balance`.
- **California.** CAISO's net generation in the block is EIA-930's total, the figure the gravity shape already draws (ruling 1a); the session 118 ruling withholds the hourly mix by fuel, not this total, so it is drawn, and the note says it reads below CAISO's own since December 2025 and that the mix stays withheld.
- **No figure that stood moves**: every earlier key and value of the panel is unchanged; the gravity panel's generation is now drawn through `generationAt`, the same key and value (tested).
- **On the fixture's week** (15 to 21 October, 144 hours with all three): mean gap CAISO 2,705.76 MW (10.0 percent of mean demand), MISO 1,598.32, PJM 544.07, SPP 192.49, NYISO 2.38, ERCOT 1.40, ISO-NE 0.00; the order is session 360's.

## What to review

After the landing (none yet; below), on production:

1. Open `https://erw-flame.vercel.app/internal/open`, paste the token, press **Open the internal view**.
2. Open `https://erw-flame.vercel.app/grid?grid=caiso&view=network`. Scroll under "CAISO, the hour shown": "Does CAISO's balance close?". Four rows (net generation, demand, net export, the gap, the gap highlighted) and the line "Over the N hours of the week that hold all three, the gap's mean size is M MW". Hover the gap: its parts, then session 360's split in one line. The note names where CAISO's gap sits and the California line.
3. Open `https://erw-flame.vercel.app/grid?grid=ercot&view=network`: the same block; the gap near zero, the note "nowhere of note".
4. Open `https://erw-flame.vercel.app/grid?grid=pjm&view=network` and `...?grid=spp&view=network`: the note says where each gap sits (both places; between the ties and the total).
5. Open `https://erw-flame.vercel.app/grid?view=network` (the Lower 48): no balance block (the seven grids' table only, as before).
6. View source on step 2 and search `data-grid-balance` and `calc|bal|`.
7. Screenshots: not taken, no build.

## Checks

- `node site/scripts/test-grid-balance.mjs` (new): exit 0, 11 tests.
- `node site/scripts/test-grid-keys.mjs`: exit 0, 8 tests. `node site/scripts/test-network-map.mjs`: exit 0, 9 tests.
- `python -m unittest` one file at a time on the 88 test files that read `NetworkFigures.tsx`, `gridKeys.ts`, `NetworkView.tsx`, `check-values.mjs` or `check-methods.mjs`: 87 exit 0, `tests.test_session1153` exit 1 (its count of figures in `NetworkFigures.tsx`, 16 against 10); the assertion extended (below), then exit 0.
- The same, on the 104 files that read `grid_network.md`, `eia930_balance` or a fixture, and the 7 that read the Grid pack: every one exit 0 (`tests.test_session360` too).
- `tests.test_session1165` (new): exit 0, 10 tests (it runs the node test).
- Type check through the junction: `npm run content` exit 0, `npx next typegen` exit 0, `npx tsc --noEmit -p .` exit 0; the junction removed (`cmd /c rmdir`), the main copy's `node_modules` intact.
- No build, no check-values run, no check-methods run against a page: none possible without a build.

## The landing

- None: chain 078 is code-only until a person lands chain 077's landing B (`wip/1162-grid`); this branch stacks on it.

## To finish

- Land with the chain's combined landing (after landing B): the build, check-values on `/grid,/network` (the new keys: `calc|bal|...` and `netbal|...` on every ISO grid's Network tab), the floors rewritten from a passing restricted run (`CHECK_VALUES_WRITE_FLOOR=1`; the network pages gain six keys each), `check-methods.mjs --values <the run> --write` (the new keys are named in `grid_network.md`), check-390 on the block, the screenshots at 1280 and 390 under `docs/brand/review-1165/`, the snapshots before and after, every difference listed (expected: the new block's text and numbers on the Network tab of `/grid` for the seven ISO grids; nothing else).

## Decisions made without you

- The gap is signed as net generation less demand less net export (negative where generation reads short, CAISO); session 360's tests run the other way; the mean size is the same.
- The week's figure is the mean absolute gap (session 360's measure), not the signed mean.
- An hour of the week needs every tie of the grid that holds a flow in some hour of the window; the hour shown keeps the panel's own net export over its reporting ties.
- The week's demand is `eia930_all_demand` alone (no fallback to the hourly snapshot's), so check-values reads one table; the hour's demand is the panel's figure, keyed as before.
- A three-operand op `bal` rather than a nested calc (a nested key cannot be parsed once its "|" are "~"); check-methods now reads a calc key as all its operands' figures (two keys as before).
- CAISO's net generation is drawn (EIA-930's total, as the gravity shape draws it); the 118 ruling covers the mix by fuel.
- The fixture is self-contained (the snapshot's hours and the seven grids' links, plus the two tables' rows), since `site/data/grid_network.json` is rewritten each day; 120 KB.
- `tests/test_session1153.py`'s count of figures in `NetworkFigures.tsx` (10, "the gravity panel adds no figure") now counts outside the new `Balance` function (10) and the function's own (6); no assertion removed.
- One sentence added to the Grid pack's item 3 (`docs/reviews/packs/grid.md`) and a section "On the Grid tool" to `eia930_balance.md`, pointing to the block.

## For Samuel's ruling

- Whether the week's gap should also show its signed mean beside the mean size (the sign tells which way the balance reads).

## Files

- New: `site/scripts/check-calc.mjs`, `site/scripts/test-grid-balance.mjs`, `site/scripts/fixtures/grid_balance.json`, `tests/test_session1165.py`, this report.
- Changed: `site/lib/gridKeys.ts` (`generationAt`, `windowOf`, `alignHours`, `balanceGaps`, `balanceWeek`, `netbalValue`, `balancePanel`, `BALANCE_SPLIT`, `BALANCE_WHERE`), `site/components/grid/NetworkFigures.tsx` (`Balance`), `site/scripts/check-values.mjs` (calc through check-calc, `netbal`), `site/scripts/check-methods.mjs` (calc's operands), `docs/methods/grid_network.md` (the chain 078 section, the key list), `docs/methods/eia930_balance.md`, `docs/reviews/packs/grid.md`, `tests/test_session1153.py`.
