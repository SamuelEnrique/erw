# Session 1403 report: the cleanest hours, live

24 October 2026, from about 06:15 to 06:40 UTC, on samueloldlaptop (the code machine, the old laptop), the fourth session of `queue/done/100-day-26-october-code-grid-tool-4.md`. Branch `wip/1403-grid`, cut from `wip/1402-grid` (sessions 1152 to 1402 stacked, not on main), worktree `C:\Users\lossa\Documents\erw-1403`. Code, tests and documents only (`runs/c077/brief.md`: no build, no server, no browser). Model spend USD 0. No warehouse data written, no Supabase write, no request to any publisher. Light reads of Supabase's REST API with the anon key: the newest hour of each grid, one fixture of 1,344 rows, same-figures' answers held in memory, and the 28 new keys recomputed live.

## Read these first

- **What the committed view draws.** The Clean tab's "the cleanest hours of the average day" (`components/mix/views.tsx` `CleanView`) is the **carbon-free share** of each month's average day by local hour, from `site/data/clean/<grid>.json` (`clean_energy_summary`, built 19 October 2026). It is not a carbon intensity. The share is of the grid's own generation, in **local clock time** (the file's `tz`, so 23 or 25 hours on clock-change days).
- **Which variable the live week uses: `intensity_generation`.** It is the intensity of the same generation the committed share is of, and the variable the tab's "The last 24 hours" draws. `intensity_demand` counts imports and takes exports out, so it is not used. Lower is cleaner in the week; higher is cleaner in the committed view.
- **The panel `grid_cleanweek_<grid>`** sits under each grid's cleanest-hours block, titled "<grid>: the cleanest hours of the last 7 days held" (`components/grid/CleanWeekPanel.tsx`, `lib/cleanWeek.ts`).
  - **The drawing:** the shared `HeatChart`, in the committed view's shape: the hour across, the day down, darker where dirtier, the week's cleanest hour marked. The hover gives the day, the local hour with its zone, the UTC hour and the kg per MWh.
  - **The window:** the 7 local days that end with the newest local day whose hours are all held, read from the grid's last 12 days. EIA's CO2 estimates run 3 days or more late: today every grid's newest hour is 2026-10-20 23:00 UTC, so the week is 13 to 19 October.
  - **The four keyed figures under it:** the hours held (`series_n`), the cleanest hour (`series_min`, new), the dirtiest (`series_max`) and the mean of the hours held (`series_mean`, new). Each extreme's hour is said in words.
  - **One line against the committed average day of the week's month,** in words and hours only: is the week's cleanest hour one of that month's four cleanest, and is its dirtiest that month's dirtiest. The month is October, in the year the view shows (2024 for ERCOT and CAISO, whose 2025 is not whole).
  - **For California,** the line adds that the week and that month rest on two series (the join, `caisoJoinDay()`, never the literal).
- **Held grids:**
  - `carbon_intensity_hourly` is public in every status file, so all seven grids are drawn. `lib/gridHeld.ts` `heldCarbon` asks `lib/license.ts` on the day, so a grid that becomes held will read "license needed", with no read.
  - `clean_energy_summary` is held for ISO-NE, MISO and NYISO. For those three the week is drawn, but its comparison line reads "license needed" and names no hour of the held file.
- **Two new key kinds, `series_min` and `series_mean`** (`|<table>|<variable>|<start>|<end>|<entity>`). `check-values.mjs` recomputes them with the page's own `weekStat` (each hour once), and `check-methods.mjs` reads them as table figures. All 28 new figures on the 10 Clean addresses were recomputed live: **28 of 28 match**.
- **What the panel shows on today's live data:**
  - ERCOT holds 168 of 168 hours. The cleanest is 131.19 kg per MWh (Friday 16 October, 16:00 CDT), the dirtiest 446.28 (Saturday 17 October, 23:00 CDT), the mean 288.66.
  - California holds 144 of 168: the table holds no hour of Thursday 15 October, Pacific time, so that row is blank.
- **A failed read** says "could not be read" and draws no figure. The committed view beside it is unchanged (tested for timeout, HTTP 500 and an empty answer).
- **No figure that stands moved.** `same-figures.mjs` compared the tip of `wip/1402-grid` with this tree on 16 addresses (1,913 figures).
  - The 6 addresses that are not on the Clean tab are the same.
  - On the 10 Clean addresses, the difference is additions only: with the new `carbon_intensity_hourly` figures and the `grid_cleanweek_*` panel names taken out, every list of figures, held figures and panels is identical.
- **The time zone, one difference:** for MISO, `docs/grids/grids.json` says `Etc/GMT+5` (no clock change), while the committed file says `America/Chicago`. The panel follows the committed file, so both drawings share one clock. This is listed for a ruling.

## What to review

There is no landing yet (below). After the landing, on production:

1. Open `https://erw-flame.vercel.app/internal/open`, paste the token, press **Open the internal view**.
2. Open `https://erw-flame.vercel.app/grid?grid=ercot&view=clean#clean-week`. Under "ERCOT: the cleanest hours of the average day, 2024" you should see "ERCOT: the cleanest hours of the last 7 days held": a grid of 7 days by 24 hours. Hover a cell for its day, hour and kg per MWh. Press **Table** for the cells as a table.
3. Under it, check the sentence with its four dotted figures (hover each for its table and window), the line "Against the committed average day of October 2024: ...", "Download this table (CSV)" and "Method: the cleanest hours, live", which opens the new section.
4. Open `https://erw-flame.vercel.app/grid?grid=caiso&view=clean#clean-week`. The row for Thursday 15 October is hatched (not held), and the line names the join of 16 December 2025.
5. Open `https://erw-flame.vercel.app/grid?grid=nyiso&view=clean#clean-week`, then `grid=miso` and `grid=isone`. The committed block reads "license needed", the week is drawn under it, and its line reads "Against the committed average day: license needed".
6. Open `https://erw-flame.vercel.app/grid?grid=ercot&view=clean&grids=ercot,caiso`. The second panel has the anchor `#clean-week-caiso`.
7. Read `docs/methods/generation_mix_hourly.md`, section "The cleanest hours, live (chain 100, 24 October 2026)", with its Decisions.
8. Screenshots: not taken, no build.

## Checks

- Precheck for session 1403: run by the orchestrator, exit 0.
- `node --import ./scripts/alias-register.mjs --import ./scripts/tsx-register.mjs scripts/test-clean-week.mjs` (new, 9 tests, on the committed real rows, including ERCOT's clock-change weeks of 2 November 2025 and 8 March 2026): exit 0. The first run failed on the test's own count of figures, since a file's link carries keys in its text, not in `data-check`. The expectation was corrected.
- Extended, exit 0 each:
  - `test-grid-files`: 103 cases, 2 new (the Clean page's panel, and a check of the figures, file, anchor, second grid and method);
  - `test-grid-failed-reads`: 71 cases, 3 new (timeout, HTTP 500, empty). `NAMED`'s words are kept, because `test_session1402` pins them; `NAMED_1403` is added beside it.
  - `tests/test_session473.py`: the new component, with 1 `check=`, in both lists.
- Every other node test that reads a changed file, one at a time, 34 in all including the new one, each exit 0:
  - plain node: grid-balance, grid-keys, lower48, mix-hourly, network-split, scarcity-strip, caiso-alerts, check-revised, check-values-light, check-values-run, check-values-slow, ercot-notices, grid-390, grid-exchange, network-map, gravity, check-links;
  - alias loader: grid-addresses, ask-ready, ask-speed, grid-ask, mix, session502, markdown-safe;
  - both loaders: grid-file-keys, grid-methods, grid-replay, grid-held, grid-units, grid-reads, grid-generation, grid-stress, hub-price, clean-week.
- `python -m unittest`, one module at a time, the 103 modules that read a changed file (grep of `tests/`). The first pass gave 101 exit 0 and two exit 1:
  - `test_session1402` pinned the `NAMED` words (see above).
  - `test_session502`: the Mix tab's computed tables gained `eia930_all_emissions`, because `MixView.tsx` imports the panel, and the panel's file header named that table. The header now names the method note instead.
  - Rerun, both exit 0. No assertion was removed or changed. `test_session1403` (new, 6 tests): exit 0.
- `same-figures.mjs` (before: `ccf478a0`, in a temporary worktree, since removed with its junction; after: this tree): 16 addresses, 1,913 figures. Exit 1, because 10 Clean pages differ by additions only, proved as above. The other 6 pages are the same. The 7 requests made only after are the panel's reads, one a grid.
- The 28 new keys recomputed live, as check-values does (a one-off, 7 anon reads): 28 of 28.
- `node scripts/check-methods.mjs` (no server): exit 0, 553 of 553. A one-off with its `figures` and `named` exports showed all 28 new figures named by `generation_mix_hourly.md`. `node --check scripts/check-values.mjs`: exit 0.
- `npx eslint` on the 11 changed or new code files: exit 0, 5 warnings, none in lines added.
- Type check through the junction: `npm run content` exit 0, `npx next typegen` exit 0, `npx tsc --noEmit -p .` exit 0. The junction was removed with `rmdir`, and the main copy's `node_modules` is intact.
- Not run (the brief): the build, check-values against a server, check-routes, check-links against a server, screenshots.

## The landing

- None in this session. Chain 100 works code-only, stacked on `wip/1400-grid` (chains 077, 078, 091 and 100, not on main). This branch lands with them. Pushed: `wip/1403-grid`.

## To finish

- Land with the chain's combined landing. At that build, against the running site (Git Bash, `MSYS_NO_PATHCONV=1`):
  - check-values on `/grid?grid=ercot&view=clean` and `/grid?grid=caiso&view=clean`: the new `series_min` and `series_mean` keys and the `series_n` and `series_max` keys beside them, four a grid. Then rewrite the Clean pages' floors from a passing run (`CHECK_VALUES_WRITE_FLOOR=1`).
  - `check-table-downloads.mjs` and `check-download.mjs --grid`: the new files `grid_cleanweek_<grid>`, which are not yet in `GRID_FILE_PAGES`.
  - `check-links.mjs`: the new fragment `#the-cleanest-hours-live-chain-100-24-october-2026`.
  - In a browser, at 1280 and 390: the heat grid, its hover card, its Table view, and the legend's two words. Screenshots go under `docs/brand/review-1403/`.
- The snapshots before and after, every difference listed. Expected:
  - on every Clean tab address, the new block under each grid's cleanest hours;
  - nothing else (the tab's license line is unchanged: `test_session502`).

## Decisions made without you

- **`intensity_generation`** (above). It matches the committed share and "The last 24 hours".
- **The committed file's clock, not `grids.json`'s, for MISO**, so the two drawings share hours. The other six zones agree, and the test holds them equal.
- **Whole local days**, ending with the newest whole one. Each hour of the day then stands once a day in the week's mean, and the newest row is not mostly blank. The partial newest day is in "The last 24 hours" above.
- **Hours only in the comparison line.** A share and an intensity are different measures. The week's single cleanest and dirtiest hours are the keyed figures, and the line says whether those hours fall among the average day's.
- **The month in the year the view shows** (October 2024 for ERCOT and CAISO today), else the newest year that holds it.
- **Two new key kinds** rather than `series_sum` over `series_n`: the sum counts an hour written twice, while the count of distinct hours does not.
- **The panel is given to the view by its caller** (`CleanView`'s `live`, passed only by the Grid tool's `MixClean`, which is now async and makes one read a grid). Where no caller passes it, the view is drawn exactly as before (tested). The anchor and method stand outside the 17 pinned panels, as 1402's do.
- **The legend says "cleaner" and "dirtier"**, not the scale's two numbers, which would be unkeyed figures.
- **The fixture** (`site/scripts/fixtures/clean_week.json`, 46 KB) is real rows read once with the anon key at about 06:25 UTC:
  - ERCOT, California and MISO from 8 October to the newest hour;
  - ERCOT's weeks of 27 October to 4 November 2025 and of 3 to 11 March 2026, for the clock changes.
  - One test writes a row twice, inside itself, and says so.

## For Samuel's ruling

- MISO's time zone: `docs/grids/grids.json` says `Etc/GMT+5`, while the committed clean file (`mix_profile.py`) says `America/Chicago`. Recommendation: say which one is MISO's clock for the Grid tool. The panel follows the committed file until then.
- The block's title "<grid>: the cleanest hours of the last 7 days held", and the comparison line "Against the committed average day of <month>: the week's cleanest hour, HH:00, is (not) one of <month>'s four cleanest hours ...". Recommendation: keep them.
- The comparison uses the week's single cleanest and dirtiest hours. Another option is the week's own average day: the mean of each local hour over the 7 days, which would be keyed figures of a new kind. Recommendation: keep the single hours, which are the figures the panel keys.

## Files

- New:
  - `site/lib/cleanWeek.ts`, `site/components/grid/CleanWeekPanel.tsx`;
  - `site/scripts/test-clean-week.mjs`, `site/scripts/fixtures/clean_week.json`, `tests/test_session1403.py`;
  - this report.
- Changed:
  - `site/components/mix/views.tsx` (`CleanView`'s `live`), `site/components/grid/MixView.tsx` (`MixClean`'s read and panel);
  - `site/lib/gridHeld.ts` (`heldCarbon`), `site/lib/gridAnchors.ts` (`CLEAN_WEEK_ANCHOR`, `cleanWeekAnchor`, `METHOD_CLEAN_WEEK`);
  - `site/scripts/check-values.mjs` (the two kinds), `site/scripts/check-methods.mjs` (`TABLE_KEY`);
  - `site/scripts/test-grid-files.mjs`, `site/scripts/test-grid-failed-reads.mjs`, `tests/test_session473.py`;
  - `docs/methods/generation_mix_hourly.md` (the chain 100 section with its Decisions, and a line in "The figures on the page and their keys").
- On this machine only: `runs/s1403/` in the worktree (every test's output, same-figures' figure lists, the live recomputation), and the scratchpad's one-off scripts.
