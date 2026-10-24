# Session 1420 report: the older blocks' files

24 October 2026, from about 10:15 UTC, on samueloldlaptop (the code machine, the old laptop), the second session of `queue/done/111-day-28-october-code-grid-tool-6.md`. Branch `wip/1420-grid`, cut from `wip/1419-grid` (sessions 1152 to 1419 stacked, not on main), worktree `C:\Users\lossa\Documents\erw-1420`. Code, tests and documents only (`runs/c077/brief.md`: no build, no server, no browser). Model spend USD 0. No warehouse data written, no Supabase write, no request to any publisher; light anon reads of Supabase's REST API (one same-figures walk, 117 distinct requests, the answers held in memory only). Production was not read (HTTP 402 since about 10:00 UTC).

## Read these first

- **Skipped, already done:** "Yesterday" and the mix table (`grid_yesterday_<grid>`, `grid_mixtable_all`) had their files from session 1416, and the Clean tab's carbon blocks from session 1415. Nothing of theirs moved; their files are now also in the check scripts' default list (below).
- **Now, six named panels, each with its file** (`components/grid/PanelFile.tsx`, session 1182: the CSV written into the link from the same figure nodes the block draws, its provenance in the first lines):
  - `grid_rightnow_<grid>` ("Right now: demand"): `erw_grid_rightnow_<grid>.csv`, three figures (the latest hour, the same hour a week earlier, the day's highest hour).
  - `grid_batteries_<grid>` ("Batteries"): `erw_grid_batteries_<grid>.csv`, the latest day's discharge, charge and hour of most discharge, the units by status.
  - `grid_cost_<grid>` ("What it costs"): `erw_grid_cost_<grid>.csv`, the five price figures.
  - `grid_building_<grid>` ("What is being built"): `erw_grid_building_<grid>.csv`, the queue by kind, the datacenters' two figures as `Figure:` lines (held whole today, so written "license needed").
  - `grid_reliability_caiso` ("Reliability"): three files, `_days_per_year` (the notice count and newest day as `Figure:` lines), `_highest_peaks`, `_latest_days` (the batteries' share and MW in two columns).
  - `grid_nowmix_<grid>` ("The mix in that hour", the Now view): `erw_grid_nowmix_<grid>.csv`, each fuel's MW, the total as a `Figure:` line.
- **Held grids:** ISO-NE's prices and queue draw their held lines only, no figure and no file; no file holds a held value (`test-grid-files.mjs` reads every file of ISO-NE's page).
- **No figure moved:** `same-figures.mjs --sizes` on the Mix tab of ERCOT, CAISO and PJM: 203, 358 and 143 figures, every one the same and in order; held figures and errors the same; panels 7 to 12, 7 to 13, 6 to 11 (only the added names); exit 1 by those additions only. HTML +24, +40 and +14 KB (the files' data links), 0 pages over.
- **Python pins kept:** `YourGrid.tsx` still holds 18 `check=` (session 473; the figures moved into constants drawn once and filed), every pinned line stands (1166, 1167, 1180, 1181, 1411, 237, 58); `test_session1182.py`'s PanelFile counts extended (YourGrid 4, Reliability 3, NowView 1) and its block list (six names), nothing removed.

## What to review

After the landing (none yet; below), on production:

1. Open `https://erw-flame.vercel.app/internal/open`, paste the token, press **Open the internal view**.
2. Open `https://erw-flame.vercel.app/grid?grid=ercot`. Under "The mix in that hour", "Right now: demand", "Batteries" and "What it costs": a line "Download this table (CSV), its source, filter and hour (or window) in the file's first lines."; click each: the file opens with its `#` lines, then the figures (each its value before rounding).
3. `https://erw-flame.vercel.app/grid?grid=caiso`: the same under Right now and Batteries; under "Reliability" three download lines (days per year, the twelve highest peaks, the latest fourteen days); under "What is being built" the queue's file, its two datacenter lines "license needed".
4. `https://erw-flame.vercel.app/grid?grid=isone`: "What it costs" and the queue say "license needed" and offer no file; Right now and Batteries offer theirs.
5. The tables of these blocks: rows a little taller (session 1159's row rule now reaches them as named panels).
6. Read `docs/methods/grid_network.md`, the new section "The older blocks' files, anchors, method links and render cases (chain 111, 24 October 2026)" and its Decisions.
7. Sample files drawn from the fixtures: `runs/s1420/files/` of the worktree (this machine only).
8. Screenshots: not taken, no build.

## Checks

- Precheck for session 1420: run by the orchestrator, exit 0.
- Node, one at a time, through the alias and tsx loaders, exit 0 each: `test-grid-files.mjs` (161 cases: 16 new, among them the older blocks' check, the held-count check of the checks' reader, three pages added), `test-grid-render.mjs` (117 cases: 18 new; `view_now` ERCOT 21 to 9 figures, ISO-NE 11 to 6, their keys still found), `test-grid-failed-reads.mjs` (113; one case reads the Reliability panel's words, its assertion unchanged), `test-grid-addresses`, `test-grid-file-keys`, `test-grid-methods`, `test-grid-reads`, `test-grid-units`, `test-lower48`, `test-network-split`, `test-policy-week`.
- `node --check` on `check-download.mjs`, `check-table-downloads.mjs`, `grid-files.mjs`, `test-grid-files.mjs`, `grid-render-standin.mjs`: exit 0 each. The check scripts not run against a server (no build).
- `same-figures.mjs --sizes`, 3 addresses (above): exit 1 by the added panel names only. The temporary worktree of `bd9b4246` and its junction removed.
- `npx eslint` on the 10 changed code files: exit 0.
- `python -m unittest`, one module at a time, 62 modules (every module that names a changed file): all exit 0, none stopped for memory: `test_session1420` (new, 8 tests), `109`, `1152`, `1154` to `1157`, `1159`, `1160`, `1162`, `1165` to `1167`, `1170` to `1172`, `1174` to `1176`, `1179`, `118`, `1180` to `1186`, `1188`, `124`, `137`, `1402` to `1404`, `1406`, `1411` to `1416`, `168_network`, `180`, `180b`, `193`, `237`, `247`, `266`, `299`, `333`, `368`, `381`, `411`, `416`, `473`, `502`, `535`, `538`, `58`, `583`, `78`, `92`.
- Type check through the junction, once at the end: `npm run content` exit 0, `npx next typegen` exit 0, `npx tsc --noEmit -p .` exit 0; the junction removed with `rmdir`, the main copy's `node_modules` intact (333 entries).
- Not run (the brief): build, check-values, check-routes, the two check scripts against a server, screenshots.

## The landing

- None in this session: production answers HTTP 402 and this window runs no gate (chain 107's note). It lands with the chain's combined landing (`wip/1417-grid` and the sessions stacked on it). Pushed: `wip/1420-grid`.

## To finish

- At the landing: the build; `node scripts/check-table-downloads.mjs http://localhost:3000` and `node scripts/check-download.mjs http://localhost:3000 --grid` (Git Bash, `MSYS_NO_PATHCONV=1`), each exit read: the default list now asks ERCOT's page for 9 files, CAISO's for 9 and ISO-NE's for 3; ERCOT's queue is not in the fixtures, so its Building file is not in the list (add it if production draws it).
- check-values on `/grid?grid=ercot`, `caiso`, `isone`, `pjm` (no key added or removed).
- The snapshots before and after, every difference listed: expected, on every Mix tab only, the download lines under the six blocks, their tables' rows taller (session 1159's rule); no number moves.

## Decisions made without you

- **A held block draws no figure and offers no file**; a held figure inside a file is written "license needed" (the datacenters' today).
- **A block with no figure offers no file** (a failed read, not in the warehouse yet, California's mix withheld).
- **Reliability's batteries cell is two columns of the file** (share in percent, MW), so each figure is a cell of its own; the days per year write a blank where the page draws a dot.
- **The figures are drawn once and filed**: inline `Num`s moved to constants (and Reliability's row cells to `dayParts`), the HTML the same (same-figures).
- **The panels are wrapped in `data-grid-panel`, the pinned `Section` lines unchanged**; Reliability names its own panel inside, `<Section id="reliability" ...>` as pinned.
- **The fixtures now hold the older blocks' rows** in both stand-ins (four tables of `grid_older_reads.json`, CAISO's `caiso_queue_positions.json`); the queue rows, which carry no id, are given `caiso_queue:standin-<n>` for the read's prefix filter only, no id drawn or keyed.
- **The check scripts' default list also asks for 1415's and 1416's files** (the Clean tab's carbon blocks, "Yesterday", the mix table) and a held grid's page; `gridFileProblems` fails a file whose held figures are not each written "license needed".
- **One failed-read case reads the Reliability panel's words** with the page's (its assertion unchanged): the section is now a block of its own in that walk.
- Anchors and method links of these blocks are left to session 1421.

## For Samuel's ruling

- The download line under each of the six blocks (the words of session 1182). Recommendation: keep, one line across the tool.
- The tables of these blocks take the named panels' row height (about 33 px where they were about 29). Recommendation: keep, one row height across the tool.

## Files

- New: `tests/test_session1420.py`, this report.
- Changed: `site/components/grid/YourGrid.tsx`, `site/components/grid/Reliability.tsx`, `site/components/grid/NowView.tsx`, `site/scripts/grid-files.mjs`, `site/scripts/check-table-downloads.mjs`, `site/scripts/check-download.mjs`, `site/scripts/grid-render-standin.mjs`, `site/scripts/test-grid-files.mjs`, `site/scripts/test-grid-render.mjs`, `site/scripts/test-grid-failed-reads.mjs`, `tests/test_session1182.py`, `docs/methods/grid_network.md` (the chain 111 section with Decisions).
- On this machine only, in `runs/s1420/` of the worktree: every test's output, the same-figures lists, the sample files, the one-off scripts.
