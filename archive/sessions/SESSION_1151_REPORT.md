# Session 1151 report: every figure keyed and traced

23 October 2026, from about 18:00 UTC, on samueloldlaptop (the code machine, the old laptop), the second session of `queue/done/077-day-23-october-code-grid-tool.md`, beside chain 075. Branch `wip/1151-grid`, cut from `wip/1150-grid`, worktree `C:\Users\lossa\Documents\erw-1151`. Model spend USD 0. No warehouse data written, no Supabase write, no request to any publisher.

## Read these first

- **The Network tab now carries its figures on the page as served.** Under the network component, a server-drawn panel for the grid in view, in the hour the component opens on (the newest hour every reporting pair holds): each reporting tie's MW and direction, the net export or import, the number of ties, the grid's demand in that hour. For the Lower 48, the seven grids' net export and ties. Wrapped in `data-grid-panel="grid_network_<grid>"`. Keys: `net|tie`, `net|export`, `net|import`, `net|ties`, and `netsnap|...` or `series|eia930_all_demand|...` for the demand, chosen as the component chooses them.
- **The Gravity tab carries what the shape draws.** `data-grid-panel="grid_gravity_<grid>"`: each of the seven grids' net generation (`series|eia930_all_generation|...`), net import (`net|import|...`), and the import as a percent of generation (`calc|pct|<import key>|<generation key>`), the grid in view highlighted, the Lower 48's generation (the scale) in the note. The Exchange blocks under it are unchanged.
- **The Clean tab's "The last 24 hours" has its headline figures.** Under the chart, `data-grid-panel="grid_clean24_<grid>"`: each ISO's latest hour, lowest and highest of the 24 hours drawn, each `series|carbon_intensity_hourly|<entity>|intensity_generation|<hour>`, the grid in view highlighted.
- **Every new figure has a one-line hover tip**: table, filter (entity or tie), hour, and the snapshot's refresh time.
- **No new key kind.** Every key is one check-values already recomputes; check-values was not changed except for one address.
- **A build was possible**: `scripts/db_probe.py` (main checkout) answered open (0.68 s) at 18:11 UTC. Built in the worktree under the build lock, served on port 3151, check-values run on `/grid` and `/network`: 42 pages, 1,213 of 1,213 values match, every floor met, exit 0.

## What to review

After the landing (none yet; see below), on production:

1. Open `https://erw-flame.vercel.app/internal/open`, paste the token, press **Open the internal view**.
2. Open `https://erw-flame.vercel.app/grid?grid=ercot&view=network`. Scroll under the network: "ERCOT, the hour shown (...)". The sentence gives the net, the ties and the demand; the table each tie. Hover a dotted figure: one line, table, filter, hour, refresh. View source and search `grid_network_ercot`.
3. Open `https://erw-flame.vercel.app/grid?grid=caiso&view=network`: the same panel for CAISO (14 keys in it on the local build).
4. Open `https://erw-flame.vercel.app/grid?view=network` (the Lower 48): "The seven grids, the hour shown", each grid's net export and ties.
5. Open `https://erw-flame.vercel.app/grid?grid=ercot&view=gravity&shape=gravity`: under the shape, "What the gravity shape draws": ERCOT's row highlighted; hover a percent: it is the import over the generation.
6. Open `https://erw-flame.vercel.app/grid?grid=ercot&view=clean`: under "The last 24 hours" chart, the table of latest, lowest and highest, ERCOT's row highlighted.
7. Screenshots of the local build, each panel scrolled into view, at 1280 and 390: `docs/brand/review-1151/` (network-ercot, network-us48, gravity-ercot, clean24-ercot). No "before" shot: the panels did not exist; the page above them is unchanged.

## Keys on the local build (18:20 UTC), as served

| Page | Keys on the page | In the new panel |
|---|---|---|
| `/grid?grid=ercot&view=network` | 6 (production at 18:05: 1) | 5 (`grid_network_ercot`; ERCOT had 2 reporting ties) |
| `/grid?grid=caiso&view=network` | 15 | 14 |
| `/grid?grid=us48&view=network` and `/grid?view=network` | 15 (production: 1) | 14 |
| `/grid?grid=pjm&view=network` | 11 | 10 |
| `/grid?grid=ercot&view=gravity&shape=gravity` | 36 | 22 |
| `/grid?grid=us48&view=gravity&shape=gravity` | 38 | 22 |
| `/grid?grid=ercot&view=clean` | 53 | 21 |
| `/grid?grid=us48&view=clean` | 49 | 21 |

## Checks

- `scripts/db_probe.py` in the worktree: exit 1 (the worktree has no `.env`: "SUPABASE_DB_URL is not set"); from the main checkout: exit 0, open, 0.68 s.
- `scripts/buildlock.py acquire 1151-grid`: exit 0; `release 1151-grid`: exit 0.
- `npm ci` in `site/`: exit 0. `npm run content`, `npx next typegen`: exit 0 (the generated content and route types `tsc` needs in a fresh worktree).
- `npx tsc --noEmit -p .` in `site/`: exit 0.
- `node scripts/test-grid-keys.mjs` (new): exit 0, 8 tests.
- `npm run build` (anon read key only in the environment): exit 0, no "statement timeout" in the log.
- check-values, restricted to the eight network, gravity and clean addresses and `/network`: exit 0, 102 of 102.
- check-values, `CHECK_VALUES_PAGES=/grid,/network` (42 pages, read through the internal view): exit 0, 1,213 of 1,213 values match Supabase, every floor met; one note: `/grid?grid=caiso&view=network` carries 15 numbers and has no floor yet.
- `python -m unittest` on the 23 test files that read the Grid page, the network or the Clean tab (`tests.test_session168_network`, `237`, `237_visit`, `266`, `299`, `124`, `118`, `416`, `54`, `93`, `239`, `180`, `180b`, `109`, `122`, `123`, `148`, `473`, `502`, `538`, `78`, `120_page`, `114_part2`): first run 3 then 1 failure, each a source-text assertion of the old markup (below); after the four updates, the failing files again: exit 0.
- The local server stopped by its port (3151 free); no browser left running.

## The landing

- None in this session: the chain lands its sessions together once they are green (the brief). The branch is pushed: `wip/1151-grid`.

## To finish

- Land `wip/1151-grid` with the chain's combined landing: `scripts/land_check.py --ref <the combined branch>`, the snapshot before as its own command, the push to `task/`, the snapshot after once production shows the new commit, `compare`, every difference listed (expected: the new panels' text and numbers on the Network, Gravity and Clean tabs of `/grid`; nothing else).
- At that landing, rewrite the floors of these pages from a passing run: `CHECK_VALUES_WRITE_FLOOR=1 CHECK_VALUES_PAGES=/grid,/network node scripts/check-values.mjs <base>` (`/grid?grid=caiso&view=network` has none; the network pages' floors stand at 1 and should rise). No floor was edited by hand.

## Decisions made without you

- The Gravity tab's panel is `grid_gravity_<grid>` and shows what the gravity shape draws (generation, net import, the pull as a percent), not a second copy of the grid's ties: the Exchange blocks right under it already key the grid's ties, net and ties count in the same hour.
- The Clean tab's panel shows all seven ISOs' latest, lowest and highest (the chart draws seven lines), the grid in view highlighted; its name is `grid_clean24_<grid>`.
- `/grid?view=network` was not added to check-values' list: it is the Lower 48's Network tab, read already as `/grid?grid=us48&view=network` and through `/network`'s redirect. Only `/grid?grid=caiso&view=network` was added.
- The hub price the component shows for a grid in the hour stays in the browser only: the panel keys the interchange and demand the task names. A price key needs the price board's interval rules (`latest_prices`) or the market table's hourly mean, left to a later session.
- Four older source-text tests asserted the exact markup this session extended (`tests/test_session168_network.py`, `test_session237.py`, `test_session299.py`: the `grid={...}` prop; `test_session473.py`: Emissions.tsx's count of `check=` from 3 to 4). Each assertion was extended, none removed.
- `lib/gridKeys.ts` repeats lib/network.ts's tie sum rather than importing it (a node test loads it with type stripping, and a value import between `lib/` files would need a `.ts` extension); the test proves every key it writes is recomputed by `netValue` to the panel's own value on the committed snapshot.

## Numbers on `/grid` still without a key (item 3, not done)

Each prints a number computed from the database; keying it needs a new recomputation in check-values or a change to how the figure is written (which would move it), so each is left and listed:

- Mix tab, "Yesterday" (`components/grid/Conditions.tsx`): the forecast's error at the peak, MW and percent of demand; the day's mean absolute error; the degree days (from the weather table). Need an absolute difference, a mean of ratios, and a mean of a day's temperatures as key kinds.
- Mix tab, "Generation mix, as a table" (`Conditions.tsx` MixTable): each fuel's share of the day, written to one decimal with "%"; a share over several variables (wind and wind with battery) and the one-decimal text are not what `shown()` writes.
- Mix tab, the grid's 30-day mix table (`components/grid/YourGrid.tsx`): "Hours held" per fuel, a count of rows; no count key kind for series.
- Mix tab, CAISO (`components/grid/Reliability.tsx`): "The table holds N notices", a count of events.
- The network component's own panel in the browser (hub price, batteries, the replay's days): drawn client side; its interchange and demand now have server twins, the rest not.

Out of scope (committed files, chain 078 session 1166): the energy mix views (day, duck, records, stress, supply, forecast) and the Clean tab's "How clean, and when". Session 1152 takes the Mix tab's "hourly mix, last 7 days".

## For Samuel's ruling

- None new.

## Files

- New: `site/lib/gridKeys.ts`, `site/components/grid/NetworkFigures.tsx`, `site/scripts/test-grid-keys.mjs`, `docs/brand/review-1151/` (8 PNGs), this report.
- Changed: `site/components/grid/NetworkView.tsx` (the `grid` prop and the panel), `site/components/grid/Emissions.tsx` (the last 24 hours' panel, the `grid` prop), `site/app/grid/page.tsx` (passes the grid), `site/scripts/check-values.mjs` (one address), `tests/test_session168_network.py`, `tests/test_session237.py`, `tests/test_session299.py`, `tests/test_session473.py`.
