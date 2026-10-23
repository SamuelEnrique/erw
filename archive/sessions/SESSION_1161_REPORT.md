# Session 1161 report: the trader's path, walked again (the Grid tool)

23 October 2026, from about 21:30 UTC, on samueloldlaptop (the code machine, the old laptop), session 1161 of `queue/done/077-day-23-october-code-grid-tool.md`, beside chain 075/076. Branch `wip/1161-grid`, cut from `wip/1160-grid` (sessions 1150 to 1160 merged with main), worktree `C:\Users\lossa\Documents\erw-1161`. Model spend USD 0. No warehouse data written, no Supabase read or write, no request to any publisher. **No build, no server, no browser** (the orchestrator's memory rule for this evening: 1.6 to 1.9 GB free).

## Read these first

- **`docs/reviews/trader-path.md` had no Grid tool steps** (it walks the generator page, the battery page and the board, steps 01 to 16, then session 585's walk). So this session wrote them, in the file's own form, as "## The Grid tool, `/grid` (session 1161, 23 October 2026)": **eleven steps, 17 to 27**, then "## What the Grid walk found" (a row a step, four findings). The headings read "### Grid step NN" so that `tests/test_session382.py`, which pins every "### Step NN" to the three pages and their review-382 shots, still reads only its sixteen.
- **Walked two ways.** On production through the internal view (node's `fetch`, `unlockPost`, the token never printed), at 21:36 UTC, for landing A (on main since 19:41 UTC, `3075cec9`: sessions 1150, 1151, 1157): twelve addresses, each 200; every figure written with its key as the served HTML printed it. From the code for sessions 1152 to 1160 (landing B, not on production): steps 19, 20, 21 and 24, and parts of 22 and 25, marked "from the code; to be walked on landing B's build", each figure's key written for tonight's newest hour or window, the value left for the build (a value a session read on its own build or from the live set is quoted as that session's).
- **Every production figure matched its key's hour and table, and the sums close** (ERCOT's ties: 352 MW in from SPP less 2 MW out to CEN is the 350 MW net import). No landing B panel is on any page read, as expected.
- **What the walk found** (the doc's last table):
  1. For a ruling: every grid's Mix tab says "the latest EIA has published" of the newest hour the warehouse holds, 21.6 hours old at the read; EIA-930's demand and generation are loaded by whole UTC days.
  2. Not fixed, a pinned line: the **Network tab's grid picker drops the replay's day**, while the Gravity tab's picker (1153) and the map's region links (1156) keep it. The fix is one condition in `app/grid/page.tsx`, which `tests/test_session1153.py` pins word for word; changing a pinned assertion is not this session's to do (the brief), so the patch is under "To finish".
  3. Not built, for chain 078: ERCOT's tab has no alert state like CAISO's, though `ercot_grid_notices` (EEAs, conservation appeals, watches; 178 rows to 15 October 2026) is in the live set with no page.
  4. The rest held: each step's promise is kept on production or in the code and its tests.
- **No code fixed**: nothing broken was found that needs no ruling and is free of a pinned assertion. No `.ts` or `.tsx` file changed.

## What to review

1. Read `docs/reviews/trader-path.md` from "## The Grid tool, `/grid` (session 1161, 23 October 2026)" to "## What the Grid walk found" (on `wip/1161-grid` until it lands).
2. Open `https://erw-flame.vercel.app/internal/open`, paste the token, press **Open the internal view**.
3. Grid step 17: `https://erw-flame.vercel.app/grid`. The first sentence: "In the hour starting 2026-10-22 23:00 UTC, the latest EIA has published, the Lower 48 states used 492,641 MW" (the hour moves with the daily run). Compare the hour with the time of your read: finding 1.
4. Grid step 23: `https://erw-flame.vercel.app/grid?grid=ercot&view=network`. Under the network, "ERCOT, the hour shown": 350 MW net over 2 ties, SWPP -352 in, CEN 2 out. Hover a figure: its table, tie, hour and refresh.
5. Finding 2: on the same page, in the network's "A day since 2019", pick 2021-02-15; the address gains `net=day&t=2021-02-15`. Press **CAISO** in the grid picker: the address has no `net` or `t`, and the network opens on the live week. Do the same on `https://erw-flame.vercel.app/grid?grid=ercot&view=gravity&shape=gravity` after landing B: the day is kept.
6. Grid steps 25, 26, 27: `https://erw-flame.vercel.app/grid?grid=ercot&view=gravity&shape=gravity` ("What the gravity shape draws"), `https://erw-flame.vercel.app/grid?grid=ercot&view=clean` ("The last 24 hours", the table under the chart), `https://erw-flame.vercel.app/grid?grid=nyiso#ask` ("Four stored answers for NYISO so far", each "license needed").
7. The walk's record: `docs/brand/review-1161/walk-1161-prod.json` (each address, its status and time, every panel's figures and text); the script beside it.

## Checks

- Precheck for session 1161: run by the orchestrator, exit 0.
- `node runs/session1161/walk1161.mjs C:/Users/lossa/Documents/erw runs/session1161/prod` (the script committed as `docs/brand/review-1161/walk-1161.mjs`): exit 0; 12 addresses, each 200, 0.44 to 4.9 s; keys per page 6 to 267.
- `python -m unittest tests.test_session1161` (new, 9 tests: the section's form, eleven steps 17 to 27, the landing B marks and keys, the findings' rows, the record against the printed figures, the stored answers' counts, no token kept): exit 0 (first run exit 1, the test's own case asked for a key the doc writes as `...|`; the case moved to a key the doc writes whole).
- `python -m unittest tests.test_session382`: exit 0. `tests.test_session585`: exit 0 (both read `trader-path.md`).
- In `site/` (`node_modules` a junction to the main checkout's, as sessions 1158 to 1160, removed before the hand-over): `npm run content` exit 0, `npx next typegen` exit 0; `npx tsc --noEmit -p .` with `NODE_OPTIONS=--max-old-space-size=1400`: **exit 134**, the heap limit reached. Not run unbounded with 1.6 GB free. This session changed no `.ts` or `.tsx` file (`git diff --name-only origin/wip/1160-grid -- site` is empty), so session 1160's type-check of the same sources (exit 0) stands; the full one is under "To finish".
- No `db_probe`, no build lock, no build, no server, no browser, no screenshots (the memory rule).

## The landing

- None: the chain lands its sessions together once a build can be made (the brief). Pushed: `wip/1161-grid`.

## To finish

- **On landing B's build** (the lock free, `db_probe` 0, memory enough), each as its own command, exits read:
  - walk Grid steps 17 to 27 at 1280 and 390 in the internal view and take each step's shots under `docs/brand/review-1161/`, named as each step's "Shots" line says (`17-grid_1280.png` to `27-grid-ask-nyiso_390.png`);
  - fill the values of the steps marked "from the code" (19, 20, 21, 24, and the code parts of 22 and 25) from that build, with their keys as written; mark each "walked on landing B's build" and update the findings table;
  - `MSYS_NO_PATHCONV=1 CHECK_VALUES_PAGES=/grid,/network node scripts/check-values.mjs http://localhost:<port>`: every key of the steps matching.
- **The Network tab's picker (finding 2), a ready patch** for the orchestrator (it changes a pinned assertion of session 1153's test):
  - `site/app/grid/page.tsx`: `const pickerCarry = view === "gravity" ? KEEP_DAY : undefined;` becomes `const pickerCarry = view === "gravity" || view === "network" ? KEEP_DAY : undefined;` and its comment "the Gravity and Network tabs' picker carries the replay's day" (the network reads `net=day&t` at load and draws the day; the Gravity shape draws nothing for it but keeps it);
  - `tests/test_session1153.py` line 74: the same new line;
  - on the build, the review step 5 above: the day kept on the Network tab too.
- `npx tsc --noEmit -p .` unbounded, once memory allows (expected exit 0: no TypeScript changed).
- Remove this worktree's `site/node_modules` junction when the worktree is removed (done at the end of this session).

## Decisions made without you

- The Grid steps continue the file's numbering (17 to 27) under "### Grid step NN" headings, not "### Step NN": session 382's test pins every "### Step" block to the three pages and their shots, and its assertions are not to be loosened.
- The section stands after session 585's walk and before the On.Energy section, so the file reads in order: the three pages, their two walks, the Grid tool, then what is needed for On.Energy and the users' feedback. Session 585's test reads its own section up to "## The On.Energy walkthrough"; the Grid section inside that span adds no row it counts.
- Landing A's steps were read on production rather than a build (none was possible); landing B's from the code, with keys for tonight's newest hour or window: the window of a key moves with the data, so the build's keys may name a later hour.
- The walk's script and its record (no HTML, no token) are committed under `docs/brand/review-1161/`, beside where the shots will go, as sessions 382 and 585 kept theirs.
- Finding 2 was not fixed in code: the only fix is the pinned line. ERCOT's alert state (finding 3) is new work, not a fix.

## For Samuel's ruling

- "the latest EIA has published" (`components/grid/NowView.tsx`, every grid's Mix tab) and "EIA publishes each grid's hourly demand an hour or so after the hour" (`components/grid/YourGrid.tsx`) are said of the newest hour the warehouse holds, 21.6 hours old at 21:36 UTC. Recommendation: "the latest hour the warehouse holds", with its age in hours as session 1152's mix panel writes it.

## Files

- Changed: `docs/reviews/trader-path.md` (the Grid tool's eleven steps, "What the Grid walk found").
- New: `docs/brand/review-1161/walk-1161.mjs`, `docs/brand/review-1161/walk-1161-prod.json`, `tests/test_session1161.py`, this report.
- On this machine only: `runs/session1161/` (the pages' HTML and text, the test and type-check outputs).
