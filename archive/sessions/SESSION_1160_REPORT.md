# Session 1160 report: the reads

23 October 2026, from 21:17 to about 21:40 UTC, on samueloldlaptop (the code machine, the old laptop), session 1160 of `queue/done/077-day-23-october-code-grid-tool.md`, beside chain 075/076. Branch `wip/1160-grid`, cut from `wip/1159-grid` (sessions 1150 to 1159 merged with main), worktree `C:\Users\lossa\Documents\erw-1160`. Model spend USD 0. No warehouse data written, no Supabase write, no request to any publisher. No build, no server, no browser (the orchestrator's memory rule for this evening).

## Read these first

- **Every read of the three pages was found by calling the pages, not by reading the code by eye.** `site/scripts/time-grid-reads.mjs` imports `app/grid/page.tsx` and `app/grid/caiso/alerts/page.tsx` as they are (`site/scripts/tsx-loader.mjs` transpiles the `.tsx` with the site's TypeScript and stands in for every `"use client"` module, which never reads Supabase), calls each page with its address's query and walks what it returns as Next renders on the server: every server component is called, every read goes through `lib/supabase.ts` unchanged. 36 addresses: `/grid`, the 8 grids on the 4 tabs, the monthly mix for ERCOT and CAISO, `/grid/caiso/alerts` (`/network` redirects to `/grid?view=network`, the Lower 48's Network tab). Every request was sent to Supabase's REST API with the anon key, one at a time, three times, the pages of a large read one after another (`ERW_PAGES_TOGETHER=1`, as the build reads them).
- **Tonight no read is slow.** 302 distinct requests; the slowest median 117 ms; the median of medians 62 ms, the 90th percentile 73 ms; none failed. `db_probe` from the main checkout: open, 0.43 s at 21:21:15 UTC before the run, 0.42 s at 21:22:20 after (exit 0 both). So **no index was added to migration 036**: no read took a second, and each of the twenty slowest is served by an index the live set already has (table below). The slowness of 21 and 22 October (`db_probe` 3.89 s at 17:56 UTC today) is the database as a whole, a primary-key read of `iso_dam_hub_prices` included: no index of these pages would answer it.
- **The Mix tab made too many requests, and three of them were made smaller with the rows drawn unchanged** (below): the Mix tab of a grid went from 66 to 90 requests a page to 54 to 76, and the Lower 48's (the page `/grid` opens on) from 62 to 43 (43,660 rows to 28,775). Across the 36 addresses, 1,259 requests to 1,108 and 799,862 rows to 690,058.
- **gridNotices(), as session 1155 noted, is asked for three times on CAISO's Mix tab and four with the monthly mix.** Next's fetch cache already sent one request; now the rows are also read and parsed once per render (React's `cache`).

## The twenty slowest (before this session's changes, 21:21 to 21:22 UTC)

Median of three, milliseconds to the answer's headers (session 580's measure); the window filter written `ts_utc>=window` (9, 10, 34 or 45 days before the hour, or the network week).

| # | Table | Filter | Offset | Rows | Median ms (three times) | Pages | Index that serves it |
|---|---|---|---|---|---|---|---|
| 1 | carbon_intensity_monthly | entity=eq.eia930:CISO variable=eq.intensity_generation | 0 | 69 | 117 (117, 135, 50) | 3 | primary key |
| 2 | eia930_all_generation | entity=eq.eia930:MISO ts_utc>=window (45 days) | 1000 | 1000 | 109 (161, 95, 109) | 2 | primary key |
| 3 | caiso_grid_emergencies | event_date 2018-07-01 to 2025-10-31 | 0 | 314 | 99 (99, 285, 84) | 1 | events_date |
| 4 | caiso_grid_emergencies | (none) | 1000 | 906 | 98 (94, 98, 106) | 2 | primary key, sorted |
| 5 | energy_projects | entity_id=like.ercot_queue:* | 0 | 1000 | 93 (93, 86, 99) | 3 | entities_id_pattern (012) |
| 6 | caiso_grid_emergencies | (none) | 0 | 1000 | 92 (82, 92, 103) | 2 | primary key, sorted |
| 7 | storage_capacity | (none) | 0 | 1000 | 88 (88, 94, 86) | 16 | primary key |
| 8 | energy_projects | entity_id=like.isone_queue:* | 0 | 420 | 87 (87, 84, 91) | 2 | entities_id_pattern |
| 9 | eia930_all_generation | entity=eq.eia930:NYIS ts_utc>=window (45 days) | 1000 | 1000 | 86 (71, 86, 97) | 2 | primary key |
| 10 | energy_projects | entity_id=like.spp_queue:* | 1000 | 22 | 86 (72, 104, 86) | 2 | entities_id_pattern |
| 11 | energy_projects | entity_id=like.caiso_queue:* | 0 | 513 | 85 (94, 85, 85) | 3 | entities_id_pattern |
| 12 | energy_projects | entity_id=like.spp_queue:* | 0 | 1000 | 85 (94, 85, 81) | 2 | entities_id_pattern |
| 13 | catalogue | (none) | 0 | 134 | 84 (76, 84, 84) | 20 | its own primary key |
| 14 | caiso_reliability_daily | variable=like.notices_* | 0 | 1000 | 84 (85, 84, 84) | 2 | primary key, sorted |
| 15 | caiso_reliability_daily | variable=like.notices_* | 1000 | 806 | 83 (89, 83, 77) | 2 | primary key, sorted |
| 16 | energy_projects | entity_id=like.ercot_queue:* | 1000 | 758 | 81 (81, 82, 80) | 3 | entities_id_pattern |
| 17 | iso_rtm_hub_prices | entity=eq.caiso:TH_SP15_GEN-APND variable=eq.lmp_rtm_15m_mean ts_utc>=window (week) | 0 | 684 | 80 (55, 80, 80) | 16 | primary key |
| 18 | eia930_all_generation | entity=eq.eia930:CISO ts_utc>=window (45 days) | 6000 | 1000 | 80 (63, 94, 80) | 3 | primary key |
| 19 | eia930_all_generation | entity=eq.eia930:US48 ts_utc>=window (34 days) | 0 | 1000 | 79 (117, 54, 79) | 2 | primary key (read removed, below) |
| 20 | eia930_all_generation | variable=eq.net_generation_mw ts_utc>=window (week) | 0 | 1000 | 78 (141, 78, 77) | 16 | series_ts (table_name, ts_utc) |

Every request of every page, with its three times and the pages that ask for it: `runs/s1160/reads.json` (before) and `runs/s1160/reads_after.json` (after) on this machine, not committed.

## What changed in the code (no figure, key or word moved)

1. **The Now view's mix** (`components/grid/NowView.tsx`, the first block of every Mix tab): it drew the newest hour of `eia930_all_generation` holding the grid's total, and that hour's fuels, out of a read of the grid's last 34 days, every variable (about 8,000 rows and 8 requests for a grid, 13,000 and 14 for the Lower 48). Now `lib/gridReads.ts latestHour`: the newest total in the same 34-day window (one row), then the grid's rows from that hour on. For CAISO, whose EIA-930 generation the view does not draw (session 118), nothing is read. The same rows are drawn: proved on real rows by the node test, and on the live set tonight for the seven grids it draws (US48, ERCO, PJM, MISO, NYIS, ISNE, SWPP: the same hour, 2026-10-22 23:00 UTC, the same total and fuels; `runs/s1160/live_same.out`).
2. **"Generation mix, as a table"** (`components/grid/Conditions.tsx MixTable`, on every Mix tab) called `loadConditions` for the eight regions, which also read each one's station temperatures (`weather_obs_hourly`, 10 days); the table draws none. `loadConditions(ba, day, { weather: false })` now; the grid's own block (`GridYesterday`) reads its station as before.
3. **Every CAISO notice** (`lib/reliability.ts gridNotices()` with no bounds): React's `cache`, one read per render, shared by the alert state, the scarcity strip, the Reliability section and the monthly mix. The request, the rows and the failure are the ones they were; the callers do not change the rows (read: none sorts or edits them in place). The bounded form (the alerts page, the heat event page) is unchanged.

Requests a page, before and after (the other 25 addresses are unchanged):

| Page | Requests before | After | Rows before | After | Sum of medians, ms, before | After |
|---|---|---|---|---|---|---|
| `/grid` and `/grid?grid=us48&view=mix` | 62 | 43 | 43,660 | 28,775 | 3,870 | 2,643 |
| `/grid?grid=ercot&view=mix` | 78 | 66 | 50,487 | 42,005 | 4,771 | 4,109 |
| `/grid?grid=caiso&view=mix` | 89 | 75 | 62,345 | 53,058 | 5,656 | 4,822 |
| `/grid?grid=pjm&view=mix` | 66 | 54 | 44,806 | 36,325 | 4,050 | 3,303 |
| `/grid?grid=miso&view=mix` | 68 | 56 | 45,029 | 36,548 | 4,226 | 3,512 |
| `/grid?grid=nyiso&view=mix` | 67 | 55 | 44,823 | 36,342 | 4,163 | 3,465 |
| `/grid?grid=isone&view=mix` | 71 | 58 | 48,437 | 38,659 | 4,394 | 3,576 |
| `/grid?grid=spp&view=mix` | 72 | 60 | 48,013 | 38,738 | 4,459 | 3,673 |
| `/grid?grid=ercot&view=mix&mixp=month` | 79 | 67 | 50,962 | 42,480 | 4,834 | 4,162 |
| `/grid?grid=caiso&view=mix&mixp=month` | 90 | 76 | 62,820 | 53,533 | 5,710 | 4,878 |

(The counts are requests as the pages ask for them with a repeated request counted once, as Next's fetch cache sends it. The second run, 21:27:58 to 21:28:49 UTC, `db_probe` 0.50 s before and after.)

## What to review

1. Read the twenty slowest above and the "Index that serves it" column against `warehouse/supabase/migrations/001_shapes.sql`, `012_entities_id_pattern.sql`, `032_carbon_hourly_since.sql`. Migration 036 is unchanged.
2. Read `site/lib/gridReads.ts` and the change in `components/grid/NowView.tsx` (the `withheld` line now stands before the reads). After the chain's landing, open `https://erw-flame.vercel.app/internal/open`, paste the token, press **Open the internal view**, then `https://erw-flame.vercel.app/grid?grid=ercot`: the first block's sentence ("... was its largest source: N MW of the N MW generated in the hour starting ...") and the "Generation by fuel" table read as before; check-values recomputes their keys.
3. `https://erw-flame.vercel.app/grid?grid=caiso`: the "CAISO's alerts: today" block, the scarcity strip's alert days and the Reliability section read as before.
4. Run the timing yourself (light: 245 distinct requests, three times each, about a minute): from `site/`, `node --import ./scripts/alias-register.mjs --import ./scripts/tsx-register.mjs scripts/time-grid-reads.mjs --env <a file with SUPABASE_URL and SUPABASE_ANON_KEY> --out ../runs/x.json` (in Git Bash with `MSYS_NO_PATHCONV=1` for `--only /grid...`).

## Checks

- Precheck (by the orchestrator): exit 0.
- `scripts/db_probe.py` from the main checkout: exit 0 at 21:17:17 (0.92 s), 21:21:15 (0.43 s), 21:22:20 (0.42 s), 21:27:58 (0.50 s), 21:28:50 (0.50 s), all open. No build all the same (the memory rule).
- `site/node_modules`: a junction to the main checkout's copy (`mklink /J`, as session 1158); `npm run content`: exit 0; `npx next typegen`: exit 0.
- `npx tsc --noEmit -p .` in `site/`: exit 0.
- `node --import ./scripts/alias-register.mjs --import ./scripts/tsx-register.mjs scripts/test-grid-reads.mjs` (new): exit 0, 20 cases. A first run failed one case of its own (the loader's names of `export const B = 1, C = 2`): the loader fixed, then 20 of 20.
- `scripts/time-grid-reads.mjs` before the changes: exit 0 (36 pages, 0 component errors, 302 requests, 0 failed, 0 refused); after: exit 0 (245 requests).
- `runs/s1160/live_same.mjs` (one-off, not committed): exit 0, the seven grids the same.
- `python -m unittest`, one file at a time: `tests.test_session1160` (new, 7 tests), `1155`, `118`, `237`, `266`, `299`, `473`, `502`, `58` (3 skipped), `78` (3 skipped), `580`, `1152`, `1153`, `1154`, `1158`, `1159`, `168_network`, `301`: each exit 0. No assertion changed.
- Not run: the build, check-values, check-routes, screenshots (no build tonight).

## The landing

- None: the branch waits with the chain's combined landing (the brief). Pushed: `wip/1160-grid`.

## To finish

- **The build under 60 seconds on this machine: not measured** (no build tonight). The last two landing gates' builds on this machine: 69 s (session 1150's landing A, `runs/land_check/663b3a36d307851154e967c255f32791c14db058.txt`, 19:03 UTC) and 65 s (`a0a0089c...txt`, 20:35 UTC). At the chain's combined landing, read the gate's `build` line, and if a build can be run under the build lock, `ERW_READ_TIMING=1 npm run build > ../runs/s1160_build.out 2>&1` then `node scripts/slow-reads.mjs ../runs/s1160_build.out 20`: `caiso_grid_emergencies` should show once per CAISO page, and the Mix tabs 12 to 19 fewer requests.
- At that landing, check-values on `/grid` and `/network` (`CHECK_VALUES_PAGES=/grid,/network`): the Now view's keys (`series|eia930_all_generation|...`) recompute as before.
- Remove this worktree's `site/node_modules` junction with `cmd /c rmdir` when the worktree is removed (done at the end of this session).

## Decisions made without you

- The reads were found by calling the pages (a walker over the server components, `time-grid-reads.mjs`) rather than listed by hand: it catches the reads a shared component makes (the catalogue, through the table citations, asked 3 to 11 times a page), which a reading of the grid files misses.
- "One at a time" read as one request in flight at any moment, the next sent once the last answered; "three times" as each distinct request three times in all (the first by the page, two alone after).
- No index added: the task asks for indexes for reads slower than 1 s, and none was. The slow days are the whole database, not a missing index.
- Three reads made smaller (above), each giving the page the rows it drew. Left as they are, listed: the catalogue (one request through Next's cache; `lib/data.ts catalogue()` is shared by every page, so it is a change for a session that owns it); `storage_capacity` read whole (1,627 rows) on every grid's Mix and Clean tabs and filtered by ISO in `lib/grid.ts load` (`lib/data.ts storageUnits()` is shared by other pages, and a filter on `extra->>iso` has no index: left); the network snapshot read twice on the Gravity tab, at 3,600 s by the network and at 0 s by the Exchange blocks (two fetch settings on purpose: the Exchange blocks read it fresh); the grid's generation read for 45, 10 and 9 days by three components (each its own window).
- React's `cache` for `gridNotices()` (the site had no `cache()` until now; the only module-level memories, in `lib/chat/`, keep rows across requests, which a page read must not).
- The timing script reads only `SUPABASE_URL` and `SUPABASE_ANON_KEY` from the env file named, and drops `SUPABASE_SERVICE_KEY` from its environment; the output names requests by path and query (the key goes in a header).

## For Samuel's ruling

- None new. (Migration 036 still waits for session 580's ruling: apply or not.)

## Files

- New: `site/lib/gridReads.ts`, `site/scripts/time-grid-reads.mjs`, `site/scripts/tsx-loader.mjs`, `site/scripts/tsx-register.mjs`, `site/scripts/test-grid-reads.mjs`, `tests/test_session1160.py`, this report.
- Changed: `site/components/grid/NowView.tsx`, `site/components/grid/Conditions.tsx`, `site/lib/reliability.ts`.
- On this machine only: `runs/s1160/` (the two timing runs' JSON and output, the probes, the one-off live check).
