# Session 1179 report: one read of a grid's generation a page

24 October 2026, from about 01:55 to 02:15 UTC, on samueloldlaptop (the code machine, the old laptop), the second session of `queue/done/091-day-25-october-code-grid-tool-3.md`. Branch `wip/1179-grid`, cut from `wip/1178-grid` (chains 077 and 078 stacked, not on main), worktree `C:\Users\lossa\Documents\erw-1179`. Code, tests and documents only (`runs/c077/brief.md`: no build, no server, no browser). Model spend USD 0. No warehouse data written, no Supabase write, no request to any publisher; light reads of Supabase's REST API with the anon key (below).

## Read these first

- **The Mix tab read the grid in view's `eia930_all_generation` four times a render**, every variable, each for its own window: 45 days (`site/lib/grid.ts` `load`, the grid's own blocks), 34 days (`lib/gridReads.ts` `latestHour`, the Now view's mix, two small requests since session 1160), 10 days (`components/grid/Conditions.tsx` `loadConditions`: "Yesterday" and the grid's own row of "Generation mix, as a table", the same request twice) and 9 days (`components/grid/MixView.tsx`, the hourly panel). Found by the walk (`time-grid-reads.mjs`), not by eye; session 1152's panel and 1160's `gridReads.ts` are two of them.
- **Now one read, at the widest window, kept for the render with React's `cache`** (`lib/gridReads.ts`): `shareGeneration(entity, since)` starts it; `generationSince(entity, since)` gives each reader the rows at or after its own start; `latestHour` takes the newest total at or after its start and every row from that hour on. Each reader still computes its own `daysAgo(n)` where it did; a start before the shared one, or another entity, reads as before.
- **Which window:** the seven ISO grids share `load`'s 45 days (Mix and Clean tabs). The Lower 48 (`/grid`, which has no `load`) shares 10 days from `app/grid/page.tsx`, its widest whole read; its Now view's 34 days stay `latestHour`'s two small requests (34 days whole would read more). The mix table's other seven regions are read as before (not the grid in view).
- **No figure moved, proved on live rows without a build:** the eleven Mix addresses and ERCOT's Clean tab drawn by the code before (`e9c08843`) and after on the same answers (a proxy on 127.0.0.1 kept every Supabase answer in memory; each distinct request sent once; the run after sent 0 new requests): 2,232 figures, every `data-check` key, `data-raw` value and text the same, page by page, in order; the held figures and the panel names the same.
- **The walk now runs each page as one render.** Outside Next, React's own `cache` calls the function every time, so the walk could not see a read shared through `cache`. `site/scripts/tsx-loader.mjs` gives the site's modules React with a `cache` kept in `globalThis.__erwRequestCache` (React's rule: a string by value, an object by identity, a throw kept); `time-grid-reads.mjs` sets a new Map a page. With none set it calls through, as before, so every other script is unchanged. The "before" run below used the new walk on the old code.

## Requests and rows, before and after

`site/scripts/time-grid-reads.mjs`, one request at a time, each distinct request three times; before 01:58:55 to 01:59:44 UTC, after 02:01:41 to 02:02:24 UTC; `db_probe` 0.60 s at 01:58:43 (exit 0). Requests are a page's distinct requests (Next's fetch cache sends a repeat once).

| Page | Requests before | After | Rows before | After | Generation requests before | After | Generation rows before | After | Sum of medians ms before | After |
|---|---|---|---|---|---|---|---|---|---|---|
| `/grid` and `/grid?grid=us48&view=mix` | 43 | 39 | 28,300 | 24,974 | 27 | 23 | 21,231 | 17,924 | 2,792 | 2,562 |
| `/grid?grid=ercot&view=mix` | 67 | 61 | 41,716 | 37,956 | 33 | 27 | 27,134 | 23,396 | 4,321 | 3,911 |
| `/grid?grid=caiso&view=mix` | 75 | 70 | 52,587 | 48,432 | 32 | 27 | 28,139 | 24,006 | 4,924 | 4,597 |
| `/grid?grid=pjm&view=mix` | 54 | 48 | 35,875 | 32,115 | 33 | 27 | 27,134 | 23,396 | 3,438 | 3,100 |
| `/grid?grid=miso&view=mix` | 56 | 50 | 36,087 | 32,327 | 33 | 27 | 27,134 | 23,396 | 3,597 | 3,282 |
| `/grid?grid=nyiso&view=mix` | 55 | 49 | 35,886 | 32,126 | 33 | 27 | 27,134 | 23,396 | 3,507 | 3,199 |
| `/grid?grid=isone&view=mix` | 58 | 50 | 38,196 | 33,693 | 35 | 27 | 28,823 | 24,342 | 3,647 | 3,276 |
| `/grid?grid=spp&view=mix` | 60 | 53 | 38,269 | 34,103 | 34 | 27 | 28,150 | 24,006 | 3,794 | 3,452 |
| `/grid?grid=ercot&view=mix&mixp=month` | 68 | 62 | 42,191 | 38,431 | 33 | 27 | 27,134 | 23,396 | 4,388 | 3,962 |
| `/grid?grid=caiso&view=mix&mixp=month` | 76 | 71 | 53,062 | 48,907 | 32 | 27 | 28,139 | 24,006 | 4,993 | 4,670 |
| `/grid?grid=ercot&view=clean` | 22 | 22 | 13,901 | 13,882 | 8 | 8 | 7,416 | 7,416 | 1,527 | 1,476 |

Across the twelve: 677 requests to 614, 444,370 rows to 401,920. On ERCOT's Mix tab the grid's own generation is now the 45-day read's 8 pages and nothing else; the 27 left are those 8 and the mix table's other seven regions. (The Clean tab's row count moved by 19 rows of other tables between the two runs, an hour apart in `daysAgo`; its reads are the same.) Every request, its three times and its pages: `runs/s1179/reads_before.json`, `reads_after.json` on this machine, not committed.

## What to review

After the landing (none yet; below), on production:

1. Open `https://erw-flame.vercel.app/internal/open`, paste the token, press **Open the internal view**.
2. Open `https://erw-flame.vercel.app/grid?grid=ercot`. The first blocks (the latest hour's mix, "ERCOT: yesterday"), the energy mix's "ERCOT: hourly mix, last 7 days" panel, the 30-day mix under it and "Generation mix, as a table" read as before; hover a dotted figure: its key as before.
3. Open `https://erw-flame.vercel.app/grid`: the Lower 48's same blocks read as before.
4. Read `site/lib/gridReads.ts` (the session 1179 header and the four new functions) and the five call sites (`lib/grid.ts` `load`, `app/grid/page.tsx`, `MixView.tsx`, `Conditions.tsx`, `latestHour`).
5. Run the timing yourself: from `site/`, `node --import ./scripts/alias-register.mjs --import ./scripts/tsx-register.mjs scripts/time-grid-reads.mjs --env <file with SUPABASE_URL and SUPABASE_ANON_KEY> --only "/grid,/grid?grid=ercot&view=mix" --out ../runs/x.json` (Git Bash: `MSYS_NO_PATHCONV=1`).
6. Screenshots: not taken, no build.

## Checks

- Precheck for session 1179: run by the orchestrator, exit 0.
- `scripts/db_probe.py` from the main checkout: exit 0, open, 0.60 s (01:58:43 UTC). No build all the same (the brief).
- `time-grid-reads.mjs` on twelve addresses, before (the new walk, the old code): exit 0, 223 distinct requests, 0 failed, 0 refused, 0 component errors; after: exit 0, 192 distinct requests, 0 failed, 0 refused, 0 errors.
- The before and after figures on the same live answers (one-off in the scratchpad, not committed; `C:\Users\lossa\Documents\erw-1179-before`, a temporary worktree of `e9c08843`, removed after): exit 0, 12 pages the same, 2,232 figures; 223 requests sent once, 0 new in the run after.
- `node --import ./scripts/alias-register.mjs --import ./scripts/tsx-register.mjs scripts/test-grid-generation.mjs` (new): exit 0, 20 of 20.
- Node tests that read a changed file, one at a time: `test-grid-reads` (20 cases), `test-grid-file-keys`, `test-grid-held`, `test-grid-replay`, `test-grid-stress` (tsx loader), `test-grid-addresses`, `test-ask-ready` (20 of 20), `test-ask-speed` (21), `test-mix-hourly` (10): each exit 0. `test-network-split`: exit 1, the same on the old code (`e9c08843`): its assertion "ready once the graph is built" looks for `\n` in `app/network/Network.tsx`, which this Windows checkout holds with CRLF; not this session's file (left; it should pass on GitHub's Linux runner).
- `python -m unittest`, one module at a time, every test that reads a changed file: `test_session102`, `1152`, `1153`, `1154`, `1155`, `1157`, `1160`, `1162`, `1166`, `1167`, `1168`, `1170`, `1171`, `1172`, `1174`, `1176`, `1179` (new, 7 tests), `118`, `133`, `156` (1 skipped), `168_mix`, `168_network`, `237`, `299`, `310`, `322`, `401`, `473`, `502`, `538`, `54`, `78` (3 skipped), `94` (5 skipped): each exit 0. No assertion changed.
- Type check through the junction (`mklink /J` to the main checkout's `node_modules`): `npm run content` exit 0, `npx next typegen` exit 0, `npx tsc --noEmit -p .` exit 0; the junction removed with `rmdir`.
- Not run: the build, check-values, check-routes, screenshots (no build, the brief).

## The landing

- None in this session: chain 091 works code-only, stacked on `wip/1176-grid` (chains 077 and 078, not on main; session 1178's two lines). This branch lands with them. Pushed: `wip/1179-grid`.

## To finish

- Land with the chain's combined landing (after `wip/1176-grid`): the build; **check-values on the Mix tab pages** (`CHECK_VALUES_PAGES=/grid,/grid?grid=ercot,/grid?grid=caiso,/grid?grid=pjm,/grid?grid=miso,/grid?grid=nyiso,/grid?grid=isone,/grid?grid=spp,/grid?grid=ercot&mixp=month,/grid?grid=caiso&mixp=month`, Git Bash with `MSYS_NO_PATHCONV=1`): every key recomputes as before; the snapshots before and after, every difference listed (expected: none from this session, no word or number moves).
- At that build, `ERW_READ_TIMING=1` and `node scripts/slow-reads.mjs <the build log> 20`: each ISO grid's Mix page shows `eia930_all_generation` for its own entity at one window (45 days), the Lower 48's at 10 days and the `latestHour` pair.

## Decisions made without you

- **Shared inside the readers, not through props:** the calls tests pin (`latestHour(GEN, entity, "net_generation_mw", daysAgo(34))`, `loadConditions(ba, conditionsDay())`, `<MixTable />`) stay word for word; the readers find the render's share themselves.
- **The share is declared before the tab is drawn:** in `load` (awaited by the page before it returns its tree) and in the page for the Lower 48, so every reader of the render sees it, whatever order React renders them in.
- **A reader keeps its own start and the rows at or after it**, so the rows equal its own read; when the hour turns between the share and a reader, the reader's later start is still covered. A reader before the shared start reads alone.
- **A failed shared read fails every reader of the render with its error** (each says so in its own words, as before), and is not asked again in the render; before, each of the four could fail alone.
- **The Lower 48 shares 10 days, not 34 or 45**: the widest window it reads whole; `latestHour`'s two small requests stay for it.
- **The mix table's other regions are not shared:** reading them for 45 days would add rows; only the grid in view is.
- **The walk's `cache` is the loader's, not React's server build:** a stand-in of `cache` with React's comparison rule, kept per page, rather than running node under the `react-server` condition (which would change how every package resolves).
- **The proof on live rows ran through a local proxy holding the answers in memory**, two node processes (the old tree and the new) reading the same answers; nothing of the rows written or committed (the figures compared were written to the scratchpad only).

## For Samuel's ruling

- None new.

## Files

- New: `site/scripts/test-grid-generation.mjs`, `tests/test_session1179.py`, this report.
- Changed: `site/lib/gridReads.ts` (`GENERATION`, `rowsSince`, `latestHourOf`, `shareGeneration`, `generationSince`; `latestHour`'s shared branch), `site/lib/grid.ts` (`load`), `site/components/grid/MixView.tsx`, `site/components/grid/Conditions.tsx`, `site/app/grid/page.tsx` (the Lower 48's share), `site/scripts/tsx-loader.mjs` (React's `cache` for one render), `site/scripts/time-grid-reads.mjs` (a render a page, `--only` a list), `docs/methods/generation_mix_hourly.md` (the chain 091 section with its Decisions).
- On this machine only: `runs/s1179/` (the two timing runs, the summary, the test outputs, the probe).
