# Session 1411 report: the older blocks on a failed read

24 October 2026, from about 07:50 to 08:30 UTC, on samueloldlaptop (the code machine, the old laptop), the second session of `queue/done/107-day-27-october-code-grid-tool-5.md`. Branch `wip/1411-grid`, cut from `wip/1410-grid` (sessions 1152 to 1410 stacked, not on main), worktree `C:\Users\lossa\Documents\erw-1411`. Code, tests and documents only (`runs/c077/brief.md`: no build, no server, no browser). Model spend USD 0. No warehouse data written, no Supabase write, no request to any publisher; light reads of Supabase's REST API with the anon key (one fixture read, two same-figures walks of 126 requests each).

## Read these first

- **Session 1181's list of older blocks, each now "could not be read" on a failed read** (the tool's one look, `Missing`: the table and the reason on hover), no figure of the read drawn, every other figure of the block as before:
  1. YourGrid's battery cycle (`storage_daily_cycle`): was "EIA-930 has no battery series for this grid";
  2. YourGrid's battery units (`storage_capacity`): was "Not in the warehouse yet: battery units mapped to ...";
  3. the price board (`price_board_latest`): was "Not in the warehouse yet: ...'s hub prices"; its peak and off-peak cells (`price_board_peak_offpeak`): were "none";
  4. the carbon intensity: the hour (`carbon_intensity_hourly`) was "Not in the warehouse yet"; the months (`carbon_intensity_monthly`) drew nothing;
  5. "Yesterday" (`weather_obs_hourly`): every degree day was "not computed (0 of 24 hours in weather_obs_hourly)"; now "Degree days at KDFW: could not be read";
  6. CAISO's daily series (`caiso_reliability_daily`): a failed peak read drew two empty tables with no word; a failed ramp, battery or notice read drew "not held" or a blank cell; now the tables or the cells say "could not be read"; an empty answer of the daily peaks is a failed read (it holds every day since 2018), with session 537's short revalidation;
  7. the table citations (`components/Cite.tsx`, every page's): a failed `catalogue` read dropped the source reports without a word; now "(the source reports could not be read)";
  8. the Flex Alert scorecard's notices column (`/grid/caiso/alerts`): blank on every day; now each day's cell "could not be read".
- **With every read answered nothing moved**: `same-figures.mjs` on the Mix tab of ERCOT, CAISO and PJM, the Clean tab of ERCOT and `/grid/caiso/alerts`, live answers, code before (`21488cf9`) and after: every page the same, 1,218 figures, the scorecard's **433**; the HTML byte for byte the same size on all five (`--sizes`), the flight payload 5 to 60 bytes larger (the `null` of each failure branch).
- **`site/scripts/test-grid-failed-reads.mjs`: 33 new cases, 107 in all, every case holds.** On the code before (the six source files stashed) 24 of the 33 failed. The blocks are recorded under their Section's title beside the block they are drawn in; the fixture is new (`site/scripts/fixtures/grid_older_reads.json`, 80 KB of real rows).
- `same-figures.mjs` now also walks `/grid/caiso/alerts` (its own page file).

## What to review

After the landing (none yet; below), on production:

1. Open `https://erw-flame.vercel.app/internal/open`, paste the token, press **Open the internal view**.
2. Open `https://erw-flame.vercel.app/grid?grid=ercot&view=mix`: Batteries, What it costs, ERCOT: yesterday, as before (the changes are in failure branches only). Then `/grid?grid=ercot&view=clean` (How clean), `/grid?grid=caiso&view=mix` (Reliability) and `/grid/caiso/alerts` (the notices column): as before.
3. A failed read cannot be made on production by hand. Locally, with a build: `node --env-file=.env.local scripts/failing-read-proxy.mjs --port 54537 --fail storage_daily_cycle --while <file>` (and `price_board_latest`, `weather_obs_hourly`, `caiso_reliability_daily`, `catalogue`, `caiso_grid_emergencies`), `SUPABASE_URL=http://127.0.0.2:54537 npm start`, each block's words read in the browser.
4. From `site/`: `node --import ./scripts/alias-register.mjs --import ./scripts/tsx-register.mjs scripts/test-grid-failed-reads.mjs`, section 11 of the file.
5. Read `docs/methods/grid_network.md`, section "The older blocks when a read fails (chain 107, 24 October 2026)", and its Decisions.
6. Screenshots: not taken, no build.

## Checks

- Precheck for session 1411: run by the orchestrator, exit 0.
- `test-grid-failed-reads.mjs`: exit 0, 107 of 107 (before the cases: 74 of 74 with the new fixture rows added; on the code before, the components stashed: exit 1, 24 failed).
- `same-figures.mjs` (5 addresses, live answers, a temporary worktree of `21488cf9`, removed): exit 0, every page the same, 1,218 figures; with `--sizes`: exit 0, HTML equal, 0 pages over.
- Node tests that read a changed file, one at a time: `test-grid-render` (72 cases), `test-grid-files` (104), `test-grid-file-keys`, `test-grid-reads`, `test-grid-units`, `test-grid-generation`, `test-grid-addresses`, `test-network-split`, `test-lease`, `test-policy-week`: each exit 0.
- `python -m unittest`, one module at a time, each exit 0 (skips as before): `test_session1411` (new, 5 tests), `473` (allowed list extended), `1155`, `1159`, `1160`, `1166`, `1167`, `1179`, `118`, `1180`, `1181`, `1183`, `1185`, `137`, `1402`, `1403`, `1406`, `1404`, `237`, `241a`, `322`, `411`, `502`, `58`, `583`, `78`, `92`, `126`, `328`, `403`, `188_idle`, `202`, `243`, `60`; and the readers of `grid_network.md`: `109`, `1156`, `1162`, `1165`, `1170`, `1171`, `1172`, `1175`, `1176`, `1182`, `1184`, `1186`, `1188`, `124`, `168_network`, `180`, `180b`, `193`, `247`, `266`, `299`, `381`, `538`.
- `npx eslint` on the eight changed code files: exit 0.
- Type check through the junction (`mklink /J` to the main checkout's `node_modules`): `npm run content` exit 0, `npx next typegen` exit 0, `npx tsc --noEmit -p .` exit 0; the junction removed with `rmdir`, the main copy's `node_modules` intact.
- Not run (the brief): the build, check-values, check-routes, screenshots.

## The landing

- None in this session: chain 107 works code-only, stacked on `wip/1410-grid`. This branch lands with the chain's combined landing. Pushed: `wip/1411-grid`.

## To finish

- Land with the chain. At that build: check-values on `/grid?grid=ercot`, `/grid?grid=caiso`, `/grid?grid=ercot&view=clean`, `/grid/caiso/alerts` (Git Bash, `MSYS_NO_PATHCONV=1`): every key as before; the snapshots before and after, every difference listed (expected: none from this session).
- With a running site: the proxy check of "What to review" 3, one table at a time.

## Decisions made without you

- **An empty answer of CAISO's daily peaks is a failed read** (`lib/gridReads.ts` `wholeSeriesRead`, beside 1181's `wholeRead`, whose fixed words name the events endpoint): `peak_demand_mw` holds every Pacific day since 2018 and an empty 200 is the one answer the hourly cache could keep. Every other block's empty answer says what an empty answer is, as before; the scorecard's notices read is a window and stays blank when empty (1181's rule).
- **The citation's words are written in `Cite.tsx`** in `Missing`'s look, not imported: `Cite` is every page's and `tests/test_session473.py` keeps `Missing` to the Grid tool's files. `Conditions.tsx` and the scorecard page take `Missing` and join that test's allowed list (no assertion removed).
- **A failed hourly carbon read ends the block**, as no hour held did; the months are not drawn alone.
- **A failed battery MW read leaves the share drawn** (its own read), the MW said not read; a failed share read says the cell could not be read.
- **The test answers the catalogue only in session 1411's cases**, so the 74 cases before them draw as they did (with it answered, their "same with every read failing" checks would compare a citation read against one not read).
- **The fixture is a cut of real rows**, not whole tables: CAISO's daily series for the twelve highest peak days and the latest fourteen held (227 of 20,624 rows), the scorecard's effects for its yearly rows and seven days (393 of 2,973); the rest as the blocks read them, to the test's clock.

## For Samuel's ruling

- None new.

## Files

- New: `site/scripts/fixtures/grid_older_reads.json`, `tests/test_session1411.py`, this report.
- Changed: `site/components/grid/YourGrid.tsx` (`Unread`, five branches, the peak cells), `site/components/grid/Conditions.tsx` (`weatherError`), `site/components/grid/Reliability.tsx` (`RowUnread`, the peaks' guard), `site/components/Cite.tsx`, `site/app/grid/caiso/alerts/page.tsx`, `site/lib/gridReads.ts` (`wholeSeriesRead`), `site/scripts/test-grid-failed-reads.mjs` (section 11, the stand-in's rows, `not.`, the Section blocks), `site/scripts/same-figures.mjs` (the scorecard's page), `tests/test_session473.py` (allowed list extended), `docs/methods/grid_network.md` (the chain 107 section).
- On this machine only, in `runs/s1411/` and the scratchpad: the one read of the fixture's rows, every test's output, the same-figures lists.
