# Session 1182 report: each new panel's table, to download

24 October 2026, from about 03:00 to 03:50 UTC, on samueloldlaptop (the code machine, the old laptop), the fifth session of `queue/done/091-day-25-october-code-grid-tool-3.md`. Branch `wip/1182-grid`, cut from `wip/1181-grid` (chains 077, 078 and 091 stacked, not on main), worktree `C:\Users\lossa\Documents\erw-1182`. Code, tests and documents only (`runs/c077/brief.md`: no build, no server, no browser). Model spend USD 0. No warehouse data written, no Supabase write, no request to any publisher; light reads of Supabase's REST API with the anon key (two fixture reads, 204 and 475 rows, and same-figures' answers held in memory).

## Read these first

- **What "the older blocks' file" is today.** `ShareBar`'s `file=` is only a chart id since session 318 (its PNG download is gone), and `TableDownloads` offers whole tables through `/api/download`. The one way the site offers a block's own figures as a file is session 793's (`app/cost-of-power/AllGridsDownload.tsx`): a CSV made from the page's own figures, no route, no read. This session follows it, made on the server.
- **`site/components/grid/PanelFile.tsx` (new).** Under each table of the panels chains 077 and 078 added, a line "Download this table (CSV)": a link whose `href` is a `data:text/csv` address with the `download` attribute, holding the CSV written from **the same cells the panel draws** (`cellOf` reads each cell without drawing it: a `Num` is its value as read, a held figure "license needed", the rest its words). No script, no route, no read: the file holds what the page drew.
- **24 files**, by id (`erw_<id>.csv`): `grid_network_<grid>` (the ties; the Lower 48's seven grids), `grid_network_<grid>_balance`, `grid_replay_<BA>`, `grid_gravity_<grid>`, `grid_exchange_<grid>_ties`, `grid_exchange_<grid>_twelve_months`, `grid_exchange_us48`, `grid_clean24_<grid>`, `grid_mix_<grid>_hourly`, `grid_mix_<grid>_monthly`, `grid_scarcity_<grid>`, `grid_caisoalert_caiso`, `grid_ercotnotice_ercot`, `grid_stress_<grid>_ramp`, `_tight_<year>`, `_calm`, `grid_stress_all_<year>`.
- **The header** (non-negotiable 5), one `#` line each: the tool and the table; the panel and the page's address; the tables, each with its source (the snapshot's build time where it is the snapshot); the filter; the hour or the window; the time the page was drawn; the figures the panel writes in its sentences (the net, the ties, the demand, the week's gap, the Lower 48's scale, the replayed day's demand, the alert days), one line each with its value and check key; then the columns and rows.
- **The files' figures are exactly the page's**: `site/scripts/test-grid-files.mjs` (new, 53 cases) draws 14 addresses on committed real rows (session 1181's stand-in) and holds, block by block, the files' figures (key and value) to the block's `data-check`/`data-raw` figures, no more and no fewer; each file is the one `panelFile()` writes from the panel's cells; held figures are written "license needed" (a cell and a header line, on a day `iso_hub_prices_history` is held for ISO-NE).
- **The two check scripts** read the files from a served page through `site/scripts/grid-files.mjs` (new): `check-table-downloads.mjs` (by default; `CHECK_GRID_FILES=<addresses>` or `0`) checks each page offers every panel's file and each opens with its provenance; `check-download.mjs --grid` reads each file whole (rows as the link states, cells per column, every number past the first column a figure of the page). Not run (no server); `node --check` on both, and the reader tested offline on the drawn pages.
- **No figure moved**: `same-figures.mjs` on 20 addresses, 2,878 figures, every page the same.

## What to review

After the landing (none yet; below), on production:

1. Open `https://erw-flame.vercel.app/internal/open`, paste the token, press **Open the internal view**.
2. Open `https://erw-flame.vercel.app/grid?grid=ercot&view=network`: under the ties table, "Download this table (CSV), its source, filter and hour in the file's first lines."; click it: `erw_grid_network_ercot.csv` opens with eleven `#` lines (the panel, the tables, the filter, the hour, the time drawn, the net, ties and demand with their keys), then `Neighbour,"Flow, MW",Direction`. The same under the balance (`erw_grid_network_ercot_balance.csv`).
3. `https://erw-flame.vercel.app/grid?grid=ercot&view=gravity`: one file under the gravity table, two under the Exchange blocks (the ties with the week's columns; the twelve months).
4. `https://erw-flame.vercel.app/grid?grid=ercot`: under the mix panel's table, the scarcity counts and ERCOT's notice line; `...&mixp=month` under the monthly table; `https://erw-flame.vercel.app/grid?grid=caiso` under CAISO's alert line; `https://erw-flame.vercel.app/grid?grid=ercot&mix=stress` under each of the four stress tables; `https://erw-flame.vercel.app/grid?grid=ercot&view=clean` under the last 24 hours.
5. Open one file beside its panel: each figure is the panel's, before rounding (hover the figure on the page for its key; the header's "Figure:" lines carry theirs).
6. Read `site/components/grid/PanelFile.tsx`, `site/scripts/grid-files.mjs`, and the method note's section "Each panel's table, to download" with its Decisions. Sample files drawn from the fixtures are on this machine (below).
7. Screenshots: not taken, no build.

## Checks

- Precheck for session 1182: run by the orchestrator, exit 0.
- `node --import ./scripts/alias-register.mjs --import ./scripts/tsx-register.mjs scripts/test-grid-files.mjs` (new): exit 0, 53 of 53. (`GRID_FILES_OUT=<dir>` writes the 24 files drawn, to read.) A first run failed 2 cases (CAISO's monthly mix not in the fixture: added from the live set; the check scripts' case before they were extended).
- `site/scripts/same-figures.mjs` (before: `03704a3f` in a temporary worktree, removed; after: this tree; one set of live answers): 20 addresses (the Network tab of ERCOT, CAISO and the Lower 48 with two replayed days, the Gravity tab of ERCOT, the Lower 48 and PJM with a replayed day, the Clean tab of ERCOT and CAISO, the Mix tab of ERCOT, CAISO, PJM, ISO-NE and the Lower 48, both monthly views, two stress views): exit 0, every page the same, 2,878 figures, held figures and panel names equal; 161 distinct requests, 0 new after.
- Node tests that read a changed file, one at a time: `test-grid-390`, `grid-exchange`, `network-map`, `network-split`, `scarcity-strip`, `grid-keys`, `grid-balance`, `caiso-alerts`, `ercot-notices`, `mix-hourly`, `gravity`, `check-revised`; `grid-addresses` (alias loader); `grid-file-keys`, `grid-held`, `grid-replay`, `grid-stress`, `grid-units`, `grid-failed-reads`, `grid-reads`, `grid-generation` (both loaders): 21, each exit 0.
- `python -m unittest`, one module at a time: `test_session1182` (new, 10 tests), `109`, `1152` to `1156`, `1158` to `1160`, `1162`, `1165` to `1168`, `1170` to `1172`, `1174` to `1176`, `118`, `1180`, `1181`, `124`, `133`, `139`, `149`, `154_page`, `157_page`, `168_mix`, `168_network`, `177`, `180`, `180b`, `182_flow`, `193`, `215`, `237`, `238`, `247`, `266`, `299`, `301`, `321`, `333`, `368`, `371`, `381`, `411`, `416`, `473`, `502`, `535`, `538`, `78`, `896`: each exit 0 (skips as before). `test_session411` failed once (it holds `hrefOf` out of `components/mix/views.tsx`): the stress files' address is now written without it; the assertion kept.
- `node --check` on `check-download.mjs`, `check-table-downloads.mjs`, `grid-files.mjs`: each exit 0. Not run against a server (the brief).
- `npx eslint` on the 14 changed or new code files: exit 0.
- Type check through the junction (`mklink /J` to the main checkout's `node_modules`): `npm run content` exit 0, `npx next typegen` exit 0, `npx tsc --noEmit -p .` exit 0; the junction removed with `rmdir`.
- Not run: the build, check-values, check-routes, the two check scripts against a server, screenshots (no build, the brief).

## The landing

- None in this session: chain 091 works code-only, stacked on `wip/1176-grid` (chains 077 and 078, not on main). This branch lands with them. Pushed: `wip/1182-grid`.

## To finish

- Land with the chain's combined landing. At that build, against the running site (Git Bash, `MSYS_NO_PATHCONV=1`): `node scripts/check-table-downloads.mjs http://localhost:3000` (the Grid pages by default, after `/board` and `/prices`) and `node scripts/check-download.mjs http://localhost:3000 --grid`, each exit read; a missing file on a page whose read failed is said by name, then that page read again.
- check-values on the addresses of "What to review": every key as before (no key changed).
- The snapshots before and after, every difference listed: expected, on each Grid page, the new line "Download this table (CSV), ..." under each panel's table (visible text), and nothing else.
- In a browser at the landing: the link downloads `erw_<id>.csv` (Chrome, Firefox, Safari take a `data:` link with `download`; the CSP governs no download).

## Decisions made without you

- **A file made from the cells the panel draws, on the server, in the link**, not a route (a second read could differ from the page by an hourly refresh) and not a button building a Blob (needs script; the checks could not read it from the HTML). The pages grow by the files' size: the largest drawn from the fixtures is about 2 KB, two to four on a page (three more for each grid added on the stress view).
- **Where a panel built its rows inline, the rows are one constant handed to both the table and the file**; the lines sessions 1165, 1170 and 1181 pin stand word for word (the balance's and the replayed day's calls are unchanged, so those two blocks name their own page from the grid's code).
- **The sentence's figures in the header, one line each with its key**, the table keeping the panel's columns; a figure drawn twice (the Exchange net, sentence and headline) is written once. The test compares sets, so a figure twice on the page is one figure of the file.
- **A held grid's figure is the page's words, "license needed"**, in the cell where its value would stand, never its value (`Num`'s `heldBy`); none of these panels draws a held grid's figure today (EIA-930 is public), so the rule is tested on a held key by itself.
- **The replayed day's file is `grid_replay_<BA>`**, named for its node: the block is drawn on the Network tab of whichever grid the address names.
- **The stress files' address is written from the view's choice** (its base address, grids and year), not by `hrefOf`, which session 411 holds out of `views.tsx`.
- **The check scripts carry each default page's files** (`GRID_FILE_PAGES`, ids or prefixes for a year), so a panel losing its file fails; check-download's `--grid` reads no database and makes no download, so it stays outside the route's sixty an hour.
- **Two light reads for the fixture** (ERCOT's `ba_supply_monthly`, CAISO's monthly mix since 2024-08), real rows, committed in `site/scripts/fixtures/grid_files.json` with their source line.

## For Samuel's ruling

- The words of the link, "Download this table (CSV), its source, filter and hour in the file's first lines.", the same under every table (a words change, if another is wanted).

## Files

- New: `site/components/grid/PanelFile.tsx`, `site/scripts/grid-files.mjs`, `site/scripts/test-grid-files.mjs`, `site/scripts/fixtures/grid_files.json`, `tests/test_session1182.py`, this report.
- Changed: `site/components/grid/NetworkFigures.tsx` (the ties, the Lower 48, the balance, the gravity table), `ReplayDay.tsx`, `ExchangeView.tsx`, `Emissions.tsx`, `MixFigures.tsx`, `ScarcityPanel.tsx`, `CaisoAlertState.tsx`, `ErcotNoticeState.tsx`, `site/components/mix/views.tsx` (the local `Table` takes a `file`; the four stress tables), `site/scripts/check-download.mjs` (`--grid`), `site/scripts/check-table-downloads.mjs` (the Grid pages), `docs/methods/grid_network.md` (the section "Each panel's table, to download (chain 091, 24 October 2026)" with its Decisions).
- On this machine only: `runs/s1182/` (same-figures' output and figure lists, every test's output), the 24 sample files in the scratchpad (`C:\Users\lossa\AppData\Local\Temp\claude\s1182\files`).
