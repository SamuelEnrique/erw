# Session 1167 report: no held grid's rows on the Grid tool; the Exchange blocks under the gravity shape

23 October 2026, from about 23:20 UTC, on samueloldlaptop (the old laptop), the fourth session of `queue/done/078-day-24-october-code-grid-tool-2.md`. Branch `wip/1167-grid`, cut from `wip/1166-grid` (chain 077's landing B is not on main), worktree `C:\Users\lossa\Documents\erw-1167`. Code-only, as the brief sets chain 078: no build, no server, no browser. Model spend USD 0. No warehouse data written, no Supabase write, no request to any publisher; two light anon reads of Supabase's REST API (`energy_projects`, `limit=3` and `limit=2`, below).

## Read these first

- **Part 1 (the orchestrator's order), the standing rule "no held grid's rows are drawn"** (`site/lib/license.ts`). Four places of the Grid tool drew a held grid's rows; each now reads "license needed" (the tool's one look, session 1159: `Missing` or a `data-license-held` span with the publishers on hover), the rule in one file, `site/lib/gridHeld.ts`:
  1. **The Clean tab's "The seven grids"** (`components/mix/views.tsx` `CleanView`): ISO-NE's, MISO's and NYISO's six cells now read "license needed" (the view's own `LW`, as its other blocks); the four other grids' text and keys are as they were (tested).
  2. **The hub price beside the mix** (Mix tab, "The average day" and "Year after year", Price): `data/mixplus` holds ISO-NE's and NYISO's hub prices from `iso_hub_prices_history` (held by grid); the lines were drawn. Now "Factor: license needed". MISO keeps "paused while terms are reviewed" (its file holds none); PJM keeps "licensed source needed".
  3. **The network's replayed days and stories** (`app/network/Network.tsx`, the Network and Gravity tabs, and `/network`): `public/network/daily_2024..2026.json` and `story_east_heat_2025.json` hold ISNE's, NYIS's and MISO's hub prices; the Prices switch drew their rings and the panel their price. Each view's price now goes through `shownPrice`: no ring, the panel reads "license needed" (MISO in version 3 still "paused"). The live week's were already refused by the read.
  4. **ISO-NE's interconnection queue** ("What is being built", `components/grid/YourGrid.tsx`): `lib/grid.ts` reads `energy_projects` by `entity_id`; `lib/supabase.ts`'s hold filters by `entity`, so ISO-NE's rows came through (an anon read confirmed `isone_queue:137`, `isone_queue:1515` are in the live set). The read now drops them (`shownQueue`) and the block reads "ISO-NE's interconnection queue: license needed".
  - And words, no rows: a held grid's hub prices in "What it costs" said "Not in the warehouse yet: ISO-NE's hub prices" (the read is refused); they now say "license needed".
- **Checked, nothing drawn**: every other read of a table held by grid goes through `lib/supabase.ts` (rows filtered by `entity`, or the read refused) or `Num` (a held key drawn as the words): `scarcity_hours_by_grid` (ScarcityPanel already says license needed), `price_board_latest` and `price_board_peak_offpeak` (refused), `clean_energy_hourly` (not drawn on /grid), the stress, forecast, history and mix files (EIA-930, NRC, NOAA: no held table).
- **Part 2, the Exchange blocks under the gravity shape** (`components/grid/ExchangeView.tsx`): "Each neighbour, that hour" keeps each flow's key and text, now with a hover line (the tie, the hour, the refresh, the week in words), four new keyed columns of the same tie over the snapshot's week (mean in whole MW, lowest, highest, hours with a flow), a new kind `nettie|<mean|min|max|hours>|<BA>|<other>|<from>|<to>` recomputed by check-values with `nettieValue` (`lib/gridKeys.ts`); the direction in words, "ERCOT takes from SWPP" (was "in"), also in the twelve months' table ("..., net"); the hour's age said once per branch, keyed `net|lag|<hour>|<refresh>`, not in rows. No figure that stood moved.
- On the committed snapshot (refreshed 2026-10-23 14:36 UTC; the hour shown 2026-10-21 23:00 UTC, 40 hours before): ERCOT takes 51 MW from SPP, the week's mean -96 MW over 144 hours, from -804 to 722 MW; CAISO's 11 ties, 44 week figures, each recomputed by the test.

## What to review

After the landing (none yet; below), on production:

1. Open `https://erw-flame.vercel.app/internal/open`, paste the token, press **Open the internal view**.
2. Open `https://erw-flame.vercel.app/grid?grid=ercot&view=clean`, scroll to "The seven grids": ISO-NE, MISO and NYISO read "license needed" in each cell (hover: the publishers); CAISO, ERCOT, PJM, SPP as before.
3. Open `https://erw-flame.vercel.app/grid?grid=isone&view=mix&mix=day&factor=price`: under the chart, "Factor: license needed". Same with `grid=ercot`: the price lines are drawn.
4. Open `https://erw-flame.vercel.app/grid?grid=isone&view=mix`, "What is being built": "ISO-NE's interconnection queue: license needed"; "What it costs": "ISO-NE's hub prices: license needed".
5. Open `https://erw-flame.vercel.app/grid?grid=ercot&view=network`, pick a day of 2025 in "A day since 2019", turn **Prices: on**: rings on CAISO, ERCOT and SPP only; click ISO-NE: "Hub price this day: license needed".
6. Open `https://erw-flame.vercel.app/grid?grid=ercot&view=gravity&shape=gravity`, scroll to "Each neighbour, that hour": the sentence of the hour's age; seven columns; hover a flow (the tie and the week in words) and each week figure (its source).
7. Same page, "Over the last twelve months": a Direction column ("ERCOT takes from SWPP, net").
8. Open `https://erw-flame.vercel.app/grid?grid=us48&view=gravity&shape=gravity`: one sentence of the age under the first paragraph.
9. Screenshots: not taken, no build.

## Checks

- `node --import ./scripts/alias-register.mjs --import ./scripts/tsx-register.mjs scripts/test-grid-held.mjs` (new, 6 tests): exit 0. Against the branch's former `views.tsx` it fails 2 of 6 (the clean table, the price factor), as it should.
- `node scripts/test-grid-exchange.mjs` (new, 7 tests): exit 0.
- `test-grid-file-keys.mjs` (tsx loader), `test-caiso-alerts`, `test-check-values-run`, `test-check-values-slow`, `test-grid-balance`, `test-grid-keys`, `test-mix-hourly`, `test-network-map`, `test-scarcity-strip`, `test-gravity`, `test-session502` (alias loader): exit 0 each.
- `node --check` on `check-values.mjs`, `check-network-v3.mjs`, `check-methods.mjs`: exit 0. check-methods' own `figures()` and `named()` on the new keys against `grid_network.md`: every one named.
- `python -m unittest`, one file at a time: the 105 files that read a changed file (grep of `tests/` for each: views.tsx, YourGrid.tsx, ExchangeView.tsx, Network.tsx, lib/grid.ts, gridtables, gridKeys, check-values.mjs, check-network-v3.mjs, the two notes) and `tests.test_session1167` (new, 9 tests, it runs both node tests): first pass on Part 1, `tests.test_session502` exit 1 (its lists of tables read by each view against the code: `iso_hub_prices_history`, now named in `lib/gridHeld.ts`); `lib/gridtables.ts` extended (Decisions), no assertion changed; then all 105 exit 0.
- Type check through the junction: `npm run content` exit 0, `npx next typegen` exit 0, `npx tsc --noEmit -p .` exit 0; the junction removed (`cmd /c rmdir`), the main copy's `node_modules` intact.
- No build, no check-values or check-methods run against a page, no `check-network-v3.mjs` (a browser check): none possible without a build.

## The landing

- None: chain 078 is code-only until a person lands chain 077's landing B (`wip/1162-grid`); this branch stacks on it.

## To finish

- Land with the chain's combined landing (after landing B): the build; check-values on `/grid,/network` (new keys `nettie|...` and `net|lag|...` on every Gravity tab with ties; no key removed: the held cells of the clean table had none); floors rewritten from a passing restricted run (`CHECK_VALUES_WRITE_FLOOR=1`); `check-methods.mjs --values <the run> --write`; `check-network-v3.mjs` (its 2025 ring count now leaves out the held grids, read from `data/license_status.json`); check-390 on the Exchange table (seven columns, `minWidth` 680, scrolls); screenshots at 1280 and 390 under `docs/brand/review-1167/`; the snapshots before and after, every difference listed (expected: the words and cells above; the Gravity tab's new columns and sentence; no number that stood moves).

## Decisions made without you

- **Visitor-facing words changed by the rule, not by design**: the Clean tab's seven grids (ISO-NE, MISO, NYISO: six cells each now "license needed"), the mix's Price factor for ISO-NE and NYISO, the network's price rings and panel for ISO-NE, MISO and NYISO (on `/grid` and `/network`), ISO-NE's queue block, and the held grids' "What it costs" (was "Not in the warehouse yet"). Every page is in review.
- One rule file, `site/lib/gridHeld.ts`, over `licenseHeldRow`; the table named for the replay's and the mix's prices is `iso_hub_prices_history` (the builders' source for every grid but ERCOT).
- The queue: `energy_projects` is held for ISO-NE only (the status file), so NYISO's and MISO's positions stay drawn though their own queue tables are held (ruling 1).
- `site/lib/gridtables.ts`: `iso_hub_prices_history` joins the Network, Gravity, Mix and Clean lists (test 502 reads the code: the network and mix draw its rows for the grids not held; the clean files are priced from it), so those license lines name it.
- `tests/test_session124.py` pins `priceOf`; it stands, and each view's own price goes through `shownPrice` instead.
- `check-network-v3.mjs`'s floor of five rings on a 2025 day becomes five less the held grids not already paused (three today), plus a new check that no held grid has a ring.
- Part 2: the week's figures are written (each keyed) and in words on the flow's hover; a new kind `nettie|` (a tie's own window), mean rounded to whole MW in the rule; the age once per branch of the block, though the network above it on the Gravity tab also says it (ruling 2).

## For Samuel's ruling

1. NYISO's and MISO's queue positions in `energy_projects` are drawn (that table is held for ISO-NE only) while `nyiso_interconnection_queue` and `miso_interconnection_queue` are held. Recommendation: hold them too, or record why `energy_projects` differs.
2. The Gravity tab now says the hour's age twice (the network's line and the Exchange block's, the same hour unless the hourly refresh lands between the two reads). Recommendation: keep the Exchange block's only on the Gravity tab.
3. `lib/supabase.ts` filters a table held by grid by `entity` only; a read naming rows by `entity_id` is not filtered (found here for `energy_projects`). Recommendation: filter by `entity_id` too, in the shared reader (outside this chain's files).

## Files

- New: `site/lib/gridHeld.ts`, `site/scripts/test-grid-held.mjs`, `site/scripts/test-grid-exchange.mjs`, `tests/test_session1167.py`, this report.
- Changed: `site/components/mix/views.tsx`, `site/components/grid/YourGrid.tsx`, `site/components/grid/ExchangeView.tsx`, `site/app/network/Network.tsx`, `site/lib/grid.ts`, `site/lib/gridtables.ts`, `site/lib/gridKeys.ts`, `site/scripts/check-values.mjs`, `site/scripts/check-network-v3.mjs`, `docs/methods/grid_network.md` (the chain 078 section, the key list), `docs/methods/generation_mix_hourly.md`.
