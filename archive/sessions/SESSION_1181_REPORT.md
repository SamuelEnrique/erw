# Session 1181 report: when a read fails

24 October 2026, from about 02:35 to 04:00 UTC, on samueloldlaptop (the code machine, the old laptop), the fourth session of `queue/done/091-day-25-october-code-grid-tool-3.md`. Branch `wip/1181-grid`, cut from `wip/1180-grid` (chains 077, 078 and 091 stacked, not on main), worktree `C:\Users\lossa\Documents\erw-1181`. Code, tests and documents only (`runs/c077/brief.md`: no build, no server, no browser). Model spend USD 0. No warehouse data written, no Supabase write, no request to any publisher; light reads of Supabase's REST API with the anon key (the walk's answers, held in memory, and one small fixture, below).

## Read these first

- **Every panel chains 077 and 078 added was drawn with a failing read, without a server.** A one-off walk (session 1160's: the page called as it is through `site/scripts/tsx-loader.mjs`, every server component called) on Supabase's live answers held in memory, each table of a page failed in turn as `site/scripts/failing-read-proxy.mjs` fails it: an HTTP 500 on the 36 addresses (346 renders), then a statement timeout past the two retries and an empty answer on 20 addresses (408 renders). No component threw in any render; the rest of each page was drawn.
- **Eight places drew a wrong statement or lost their panel on a failed read; each now says "could not be read"** (the tool's one look, `Missing`, the table and the reason on hover) and draws no figure of it:
  1. the balance (1165): net generation "not held", "a part is not held", "No hour of the week holds all three" when `eia930_all_generation` or `eia930_all_demand` failed;
  2. the gravity panel: each grid's net generation "not held", the Lower 48's "not held for the hour";
  3. the energy mix panel (1152): "Demand is not held for these hours" on a failed demand read; nothing in the panel on a failed generation read;
  4. the scarcity strip: "No 15-minute price of these days is in the live set" (and on every cell's hover) on a failed price read, nothing for ERCOT's daily price;
  5. the last 24 hours' table (`grid_clean24_`): its panel name gone from the page on a failed or empty read (the "no data" now stands under the name);
  6. the whole-table notice reads (CAISO's and ERCOT's): an **empty answer** drew "holds no notice", "0 days" of restricted maintenance (CAISO, 2 in the window) or of other notices (ERCOT, 3), "0" call days on the monthly mix (22): now a failed read for every reader, with session 537's short revalidation; CAISO's Reliability section's 1166 count read "The table holds 0 notices, the latest on no day" on a failed read;
  7. the replayed day on the Gravity tab (1170): the demand "not held" when the year's committed file could not be read;
  8. ERCOT's interconnection queue (beside 1167's held lines): "Not in the warehouse yet ... in the live set" on a failed `energy_projects` read.
- **Already right, left:** CAISO's and ERCOT's state lines on a failed read ("could not be read just now"), the scarcity strip on a failed `scarcity_hours_by_grid` read ("working on it"), the monthly mix on a failed profile read, the replayed day on the Network tab (NoData), the snapshot failing (the committed snapshot drawn, the source line says "the hourly copy was not reachable"), the Ask examples, the stress and committed-file views and the held queue line (no database read: the same with every read failing).
- **No Grid read made `required()`** (Decisions). `/grid` is drawn on demand (ƒ in the last landing's build): no page of it is cached, and Next keeps only a 200 in its data cache, so a timeout or HTTP error is never kept; what could be kept for an hour is an **empty** 200, which is why the two whole-table reads now treat no row as a failed read.
- **`site/scripts/test-grid-failed-reads.mjs`**: 58 cases, a panel and a failure kind each, on committed real rows; on the code before this session (the component changes stashed) 27 of its first 55 cases failed, on the code after all 58 hold.

## What to review

After the landing (none yet; below), on production:

1. Open `https://erw-flame.vercel.app/internal/open`, paste the token, press **Open the internal view**.
2. Open `https://erw-flame.vercel.app/grid?grid=ercot&view=network`, `...&view=gravity`, `/grid?grid=ercot`, `/grid?grid=caiso`, `/grid?grid=ercot&view=clean`: with every read answered, each panel reads as before (no figure, key or word moved on success: the changes are in the failure branches only).
3. A failed read cannot be made on production by hand. To see one locally (needs a build, not run tonight): `node --env-file=.env.local scripts/failing-read-proxy.mjs --port 54537 --fail eia930_all_generation --while <file>`, `SUPABASE_URL=http://127.0.0.2:54537 npm start`, then `/grid?grid=ercot&view=network`: "Net generation: could not be read", "The week's gap is not computed: its hours could not be read", hover for the table and reason.
4. Read `site/scripts/test-grid-failed-reads.mjs` (the header lists every check) and run it: from `site/`, `node --import ./scripts/alias-register.mjs --import ./scripts/tsx-register.mjs scripts/test-grid-failed-reads.mjs`.
5. Read `docs/methods/grid_network.md`, section "When a read fails (chain 091, 24 October 2026)", and its Decisions.
6. Screenshots: not taken, no build.

## Checks

- Precheck for session 1181: run by the orchestrator, exit 0.
- `scripts/db_probe.py` from the main checkout: exit 0, open, 0.66 s (02:39:56 UTC). No build all the same (the brief).
- The walk on live answers (one-off, scratchpad, not committed): HTTP 500 on 36 addresses, exit 0, 0 component errors, 226 distinct requests sent once; timeout and empty on 20 addresses before the fixes, exit 0, 45 named-panel findings; after the fixes, timeout, HTTP 500 and empty on the same 20, exit 0, **0 named-panel findings**.
- `node --import ./scripts/alias-register.mjs --import ./scripts/tsx-register.mjs scripts/test-grid-failed-reads.mjs` (new): exit 0, 58 of 58. On the code before (stashed): exit 1, 27 failed (of the 55 cases then).
- No figure moved on success: `site/scripts/same-figures.mjs` drew 25 addresses (`/grid`, the four tabs of the Lower 48, ERCOT, CAISO, PJM and ISO-NE, the two monthly mixes, the two replayed days) with the code before (`833665b9`, a temporary worktree, removed) and after on the same live answers: exit 0, every page the same, 2,512 figures, held figures and panel names equal; 161 distinct requests, 0 new after.
- Node tests that read a changed file, one at a time: `test-caiso-alerts`, `test-ercot-notices`, `test-grid-390`, `test-network-split`, `test-scarcity-strip`, `test-grid-balance`, `test-grid-keys`; `test-grid-addresses` (alias loader); `test-grid-reads`, `test-grid-replay`, `test-grid-stress`, `test-grid-units`, `test-grid-held`, `test-grid-file-keys`, `test-grid-generation`, `test-grid-failed-reads` (both loaders): 16, each exit 0. (A first try of the notices guard inside `lib/reliability.ts` failed `test-grid-reads` and sessions 1155, 1160 and 1174's pinned lines: moved to the readers, below.)
- `python -m unittest`, one module at a time, every module that reads a changed file: `test_session1181` (new, 11 tests), `109`, `1152` to `1160`, `1162`, `1165` to `1168`, `1170` to `1172`, `1174` to `1176`, `1179`, `118`, `1180`, `124`, `133`, `137`, `154_audit`, `168_mix`, `168_network`, `180`, `193`, `202`, `215`, `236`, `237`, `241c`, `247`, `266`, `299`, `377`, `411`, `412`, `416`, `428`, `473`, `502`, `54`, `58`, `583`, `61`, `695`, `78`, `92`, `93`: 56 modules, each exit 0 (skips as before). `test_session1165` and `473` failed on a first version (a pinned call, the allowed list): the call kept word for word, the list extended.
- `npx eslint` on the 15 changed or new code files: exit 0 (one warning, `app/network/Network.tsx` line 210, as before).
- Type check through the junction (`mklink /J` to the main checkout's `node_modules`): `npm run content` exit 0, `npx next typegen` exit 0, `npx tsc --noEmit -p .` exit 0; the junction removed with `rmdir`.
- Not run: the build, check-values, check-routes, screenshots (no build, the brief).

## The landing

- None in this session: chain 091 works code-only, stacked on `wip/1176-grid` (chains 077 and 078, not on main). This branch lands with them. Pushed: `wip/1181-grid`.

## To finish

- Land with the chain's combined landing. At that build: check-values on `/grid?grid=ercot`, `/grid?grid=caiso`, `/grid?grid=ercot&view=network`, `/grid?grid=ercot&view=gravity`, `/grid?grid=ercot&view=clean` (Git Bash, `MSYS_NO_PATHCONV=1`): every key as before; the snapshots before and after, every difference listed (expected: none from this session).
- With a running site (the chain file's note for 1181): the proxy check of "What to review" 3, one table at a time (`eia930_all_generation`, `eia930_all_demand`, `carbon_intensity_hourly`, `iso_rtm_hub_prices`, `caiso_grid_emergencies`), each panel's words read in the browser.
- Older blocks that still say "not held" or nothing on a failed read (found by the walk, not chains 077 and 078's, not changed; their failures are named at the foot of the grid's blocks, "Reads that failed"): the grid's own blocks in `components/grid/YourGrid.tsx` (carbon `carbon_intensity_hourly` and `carbon_intensity_monthly`, storage cycles `storage_daily_cycle`, the Batteries block `storage_capacity`, the price board `price_board_latest` and `price_board_peak_offpeak`), "Yesterday" (`weather_obs_hourly`), the table citations (`catalogue`), CAISO's daily series (`caiso_reliability_daily`), and the Flex Alert scorecard's type column (`/grid/caiso/alerts`, blank when its notice read fails). A later session of this chain (or the next) can take them with the same test.

## Decisions made without you

- **No Grid read is `required()`**: `/grid` is drawn on demand (ƒ in `runs/land_check/d3b4c998b5f0930331627bb23c4471577e29b4b6/build.out`), so a failed read is not kept in a page, and Next's data cache keeps only a 200; a required read would give the visitor an error page and a page drawn on demand has no last good page to keep. No method note says a panel must not be drawn without its read. The prerendered Grid page, `/grid/caiso/alerts` (an hour), keeps `attempt()` and session 537's one-minute mark.
- **An empty answer of a whole table that always holds rows is a failed read** (CAISO's notices since 1998, ERCOT's since 2011): it is the one failure an hourly cache could keep (a 200), and it drew "0 days" and "no alert" as facts. Made a failed read, not `required()`. An empty answer of a window says what the table holds for it, as before ("not held", "has no row in the last 7 days", "No 15-minute price of these days is in the live set").
- **CAISO's read is guarded at its Grid readers** (`lib/gridReads.ts` `wholeRead` over `attempt(() => gridNotices())`), not inside `lib/reliability.ts`: sessions 1155, 1160 and 1174 pinned those lines word for word, and the bounded reads of the scorecard and the heat event page must keep "no notice in the window". ERCOT's guard is inside `ercotNotices()` (`wholeTable`), its only readers being the Grid's.
- **The words**: `Missing` with "could not be read", the table and the reason on hover; never "not held". Words a panel already had for a failed read stay ("could not be read just now", "no data for", the mix view's "working on it").
- **The hour's demand in the network panel and the balance stays the snapshot's own** when `eia930_all_demand` fails (the hourly refresh read it into the snapshot): a figure held, not of the failed read; the week's gap, which needs the read, says it could not be read.
- **The balance's call is written twice** (one branch with the failed reads, one as it stood) so session 1165's pinned line stays word for word; `tests/test_session473.py`'s allowed list extended with `NetworkFigures.tsx`, `MixFigures.tsx` and `Reliability.tsx` (each takes `Missing` from `components/mix/Now.tsx`, as sessions 1154 and 1170 extended it); no assertion removed.
- **The test is offline, on real rows**: a stand-in for PostgREST and Storage over the committed fixtures of sessions 1154, 1155, 1165 and 1174 and one new one (`site/scripts/fixtures/grid_failed_reads.json`, 47 KB: ERCOT's generation and demand over 26 hours, the seven grids' carbon intensity over 26 hours, read once with the anon key at 02:47 UTC); the clock is the fixture's read time, so its windows hold their rows on any later day. The live walk that found the faults was a one-off (scratchpad), as session 1179's proof was.

## For Samuel's ruling

- None new.

## Files

- New: `site/scripts/test-grid-failed-reads.mjs`, `site/scripts/fixtures/grid_failed_reads.json`, `tests/test_session1181.py`, this report.
- Changed: `site/app/network/data.ts` and `Network.tsx` (the live week keeps its failed reads), `site/components/grid/NetworkFigures.tsx`, `MixView.tsx`, `MixFigures.tsx`, `Emissions.tsx`, `ScarcityPanel.tsx`, `CaisoAlertState.tsx`, `Reliability.tsx`, `ReplayDay.tsx`, `YourGrid.tsx`, `site/lib/gridReads.ts` (`wholeTable`, `wholeRead`, `CAISO_HOLDS`), `site/lib/gridErcotNotices.ts`, `site/lib/scarcityStrip.ts` (the hover's words on a failed price read), `tests/test_session473.py` (allowed list extended), `docs/methods/grid_network.md` (the section "When a read fails" with its Decisions).
- On this machine only: the scratchpad's walk, its outputs and the test outputs.
