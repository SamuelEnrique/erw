# Session 1402 report: the hub price beside the hourly mix

24 October 2026, from about 05:45 to 06:20 UTC, on samueloldlaptop (the code machine, the old laptop), the third session of `queue/done/100-day-26-october-code-grid-tool-4.md`. Branch `wip/1402-grid`, cut from `wip/1400-grid` (sessions 1152 to 1401 stacked, not on main), worktree `C:\Users\lossa\Documents\erw-1402`. Code, tests and documents only (`runs/c077/brief.md`: no build, no server, no browser). Model spend USD 0. No warehouse data written, no Supabase write, no request to any publisher; light reads of Supabase's REST API with the anon key (the license check, one fixture of 624 rows, same-figures' answers held in memory, the 12 new keys recomputed live).

## Read these first

- **The license, checked first.** `iso_rtm_hub_prices` is held by grid for MISO only (`site/data/license_status.json`, `warehouse/metadata/license_status.csv`); no SPP table is held anywhere. So ERCOT, CAISO and SPP are drawn. The hubs are the site's own (`docs/grids/grids.json` `hub`): `ercot:HB_HUBAVG` (`spp_rtm`), `caiso:TH_SP15_GEN-APND` and `spp:SPPNORTH_HUB` (`lmp_rtm_15m_mean`).
- **The strip.** Under the Mix tab's 7-day hourly chart, a strip on the chart's own time axis with its own scale draws each hour's hub price. An hour's price is the mean of its four 15-minute prices, used only when all four are held (the rule of `docs/methods/cost_of_power.md`). An hour that is not held is a gap. On hover the hour's price stands under each fuel's MW and share. The chart's Table view gains a price column.
- **How it is drawn.** `TimeChart` takes a series marked `strip: true`, off by default. Its signature line, which session 303 pins, is unchanged. Without a strip, every chart is drawn exactly as before (the test renders the real `TimeChart` both ways).
- **The panel `grid_hubprice_<grid>`** sits under the chart (`components/grid/HubPricePanel.tsx`). It writes four keyed figures over the chart's hours: the hours held whole, their mean, the highest hour (its hour in words) and the last hour held. It also has its file (`erw_grid_hubprice_<grid>.csv`), its anchor (`#hub-price`, and `#hub-price-<grid>` for a second grid) and its method line, which opens the new section of `generation_mix_hourly.md`.
- **Three new key kinds**: `series_hn`, `series_hmean` and `series_hmax`, written as `|iso_rtm_hub_prices|<variable>|<start>|<end>|<entity>`. `check-values.mjs` recomputes them with the page's own `hubHourStat`, and `check-methods.mjs` reads them as table figures. The live values (anon read) were recomputed: **12 of 12 match**. On the live set, ERCOT holds 163 of 168 hours from 16 to 22 October with a mean of USD 27.01; SPP North Hub holds 96 of 168, a mean of USD 15.62, with its last hour 2026-10-21 04:00 UTC at USD -12.09. SPP's rows in the table stop at 21 October 04:45 UTC and have day-long gaps.
- **CAISO is drawn alone.** Its hourly mix is withheld (the session 118 ruling), so the price is drawn as a line by itself, over the 7 days to its newest day held whole (161 of 168 hours, a mean of USD 44.25). A grid whose generation read fails is drawn the same way.
- **The other grids get one line each, in the tool's one look:**
  - PJM: "license needed" (no PJM price is held);
  - MISO: "paused";
  - NYISO and ISO-NE: "license needed" (from 2026-10-21);
  - the Lower 48: "no hub of its own".
  For these grids no read is made.
- **A failed price read** says "could not be read" and draws no figure. The mix chart is still drawn, without its strip (tested for timeout, HTTP 500 and an empty answer).
- **No figure that stands moved.** `same-figures.mjs` compared the tip of `wip/1400-grid` with this tree on 14 addresses (2,198 figures). The pages without the panel are the same. On the 8 Mix pages that differ, the difference is additions only: with the `series_h*` figures and the `grid_hubprice_*` panel names taken out, every list of figures, held figures and panels is identical.
- **One visible change outside the panel:** the Clean tab's license line now names `iso_rtm_hub_prices` ("held for MISO: license needed"). This is because `MixView.tsx`, whose `MixClean` the tab draws, now reads it. It follows session 1174's precedent for ERCOT's notices, and `tests/test_session502.py` requires it.

## What to review

There is no landing yet (below). After the landing, on production:

1. Open `https://erw-flame.vercel.app/internal/open`, paste the token, press **Open the internal view**.
2. Open `https://erw-flame.vercel.app/grid?grid=ercot#hub-price`. Under "ERCOT: hourly mix, last 7 days" you should see the strip "HB_HUBAVG real-time" under the stacked chart. Hover the chart: the card gives each fuel's MW and share, then, under a rule, the hour's price in USD/MWh. Press **Table**: the last column is the price.
3. Under the chart, check the sentence "Under the chart, ERCOT Hub Average (HB_HUBAVG)'s real-time price by hour, the same hours: ...". Its four figures are dotted; hover one for its table and window. Then check "Download this table (CSV)" and "Method: the hub's price beside the hourly mix", which opens the new section.
4. Open `https://erw-flame.vercel.app/grid?grid=spp#hub-price`. The strip has gaps where SPP's rows are not held, and its last hour is earlier than the mix's.
5. Open `https://erw-flame.vercel.app/grid?grid=caiso#hub-price`. The mix is withheld, as before; the price is drawn alone, with the sentence and the reason.
6. Open `https://erw-flame.vercel.app/grid?grid=pjm`, then `grid=miso`, `grid=nyiso`, `grid=isone` and `https://erw-flame.vercel.app/grid`. Each has one line under the hourly chart with the word and the reason.
7. Open `https://erw-flame.vercel.app/grid?grid=ercot&view=clean`. The license line now names `iso_rtm_hub_prices` (above).
8. Read `docs/methods/generation_mix_hourly.md`, section "The hub's price beside the hourly mix (chain 100, 24 October 2026)", with its Decisions.
9. Screenshots: not taken, no build.

## Checks

- Precheck for session 1402: run by the orchestrator, exit 0.
- `node --import ./scripts/alias-register.mjs --import ./scripts/tsx-register.mjs scripts/test-hub-price.mjs` (new, 10 tests, on the committed real rows): exit 0. The first two runs failed on the test's own reach: the tsx loader stubs client components, so `TimeChart` is now transpiled from its own source for the test, and the method link is found in the tree.
- Extended, exit 0 each: `test-grid-files` (101 cases, 3 new); `test-grid-failed-reads` (68 cases, 7 new: the panel on timeout, HTTP 500 and an empty answer for ERCOT and CAISO, and the price drawn alone on a failed generation read; `NAMED` gains `hubprice`).
- Every other node test that reads a changed file, one at a time, 33 in all, each exit 0:
  - plain node: grid-balance, grid-keys, lower48, mix-hourly, network-split, scarcity-strip, caiso-alerts, check-revised, check-values-light, check-values-run, check-values-slow, ercot-notices, grid-390, grid-exchange, network-map, gravity, check-links;
  - alias loader: grid-addresses, ask-ready, ask-speed, grid-ask, mix, session502;
  - both loaders: grid-file-keys, grid-methods, grid-replay, grid-held, grid-units, grid-reads, grid-generation, grid-stress.
- `python -m unittest`, one module at a time: the 101 modules that read a changed file (grep of `tests/`), then 502, 1154, 1167, 1174 and `test_session1402` (new, 8 tests) again. The first pass: 100 exit 0, and `test_session502` exit 1, because the Clean view's tables now include `iso_rtm_hub_prices` through `MixView.tsx`. I extended `lib/gridtables.ts` (Decisions), and 502 then exited 0. No assertion was removed or changed. `test_session473.py` gained the new component, with 1 `check=`, in both lists.
- `same-figures.mjs` (before: `b5d7ac94`, in a temporary worktree, since removed with its junction; after: this tree): 14 addresses, 2,198 figures. Exit 1, because 8 pages differ by additions only, proved by the comparison above. On the 6 other addresses every page is the same.
- The 12 new keys recomputed live, as check-values does (a one-off, anon reads): 12 of 12.
- `node scripts/check-methods.mjs` (no server): exit 0, 553 of 553. A one-off with its `figures` and `named` exports showed all 12 new figures named by the note.
- `node --import ./scripts/alias-register.mjs scripts/test-markdown-safe.mjs` (the note and this report rendered): exit 0. `node --check scripts/check-values.mjs`: exit 0. `npx eslint` on the 13 changed or new code files: exit 0 (7 warnings, none in lines added).
- Type check through the junction: `npm run content` exit 0, `npx next typegen` exit 0, `npx tsc --noEmit -p .` exit 0. The junction was removed with `rmdir`, and the main copy's `node_modules` is intact (333 entries).
- Not run (the brief): the build, check-values against a server, check-routes, check-links, screenshots.

## The landing

- None in this session. Chain 100 works code-only, stacked on `wip/1400-grid` (chains 077, 078 and 091, not on main). This branch lands with them. Pushed: `wip/1402-grid`.

## To finish

- Land with the chain's combined landing. At that build, against the running site (Git Bash, `MSYS_NO_PATHCONV=1`):
  - check-values on `/grid?grid=ercot`, `/grid?grid=caiso`, `/grid?grid=spp`: the new `series_h*` keys, four a page. Then rewrite the Mix pages' floors from a passing run (`CHECK_VALUES_WRITE_FLOOR=1`).
  - `check-table-downloads.mjs` and `check-download.mjs --grid`: the new files `grid_hubprice_<grid>`, which are not yet in `GRID_FILE_PAGES`.
  - `check-links.mjs`: the new fragment.
  - In a browser, at 1280 and 390: the strip, its hover card and its table view. Screenshots go under `docs/brand/review-1402/`.
- The snapshots before and after, every difference listed. Expected:
  - on every Mix tab address, the strip under the hourly chart (ERCOT, SPP), CAISO's price chart, the panel's text and figures, and the one-line reason on the other grids;
  - on the Clean tab, the license line's new table;
  - nothing else.

## Decisions made without you

- **A strip under the chart, not a second axis.** A price line over a stacked area in MW would cross the bands, and its scale (negative at night in SPP) shares nothing with the stack's. The strip keeps one time axis and one hover.
- **The strip is a field of the series** (`strip`, with its `unit`), not a new `TimeChart` prop. This keeps session 303's pinned signature line word for word. The right gutter is the widest name's, the strip's included.
- **Its own panel, `grid_hubprice_<grid>`, under the chart.** The mix panel's element and its files are pinned. Its anchor and method stand outside `GRID_ANCHOR` and `GRID_METHOD`, whose 17 panels `tests/test_session1183.py` pins ("17 panels"), as `METHOD_MIX_US48` does (session 1185).
- **The window is the chart's own** (`chartWindow`, held equal to `Hourly`'s by the test). Where no chart is drawn (CAISO, or a failed generation read), it is the 7 UTC days ending with the price's newest day held whole. For CAISO this means nothing of the withheld EIA-930 series decides what is drawn.
- **The last hour held is the last of the chart's hours that holds its four prices**, not the table's newest row: the figures are of the hours drawn.
- **Three new key kinds**, rather than `series_sum` and a `calc`: a sum over four would count an hour missing an interval.
- **The Clean tab's license line names `iso_rtm_hub_prices`** (`lib/gridtables.ts`). `scripts/page_tables.py` reads every import of `MixView.tsx` for each of its exports, as session 1174 found for ERCOT's notices.
- **The fixture** (`site/scripts/fixtures/hub_price.json`, 24 KB) is real rows read once with the anon key at about 05:50 UTC: ERCOT from 20 to 22 October (the days of session 1152's mix fixture), SPP from 19 October to its newest row (gaps included), and CAISO from 21 October to 23 October 06:45 UTC. Two tests take rows out or write a row twice inside themselves, and say so.

## For Samuel's ruling

- The words under the chart, "Under the chart, <hub>'s real-time price by hour, the same hours: ...", and the strip's name "<hub> real-time". Recommendation: keep them.
- The Clean tab's license line now names `iso_rtm_hub_prices`, which that tab does not draw (the shared file's reach). Recommendation: keep it, as session 1174 did, or have `page_tables.py` read only the imports an export uses (a change to a shared reader).
- `docs/grids/grids.json` still says `prices_public: true` for NYISO, ISO-NE and MISO, while `lib/license.ts` holds their prices. The page goes by the license file. Recommendation: have the data machine refresh the file.

## Files

- New:
  - `site/lib/hubPriceHourly.ts`, `site/components/grid/HubPricePanel.tsx`;
  - `site/scripts/test-hub-price.mjs`, `site/scripts/fixtures/hub_price.json`, `tests/test_session1402.py`;
  - this report.
- Changed:
  - `site/components/TimeChart.tsx` (the `strip` series), `site/components/StackedArea.tsx` (`strip`), `site/components/mix/Now.tsx` (`Hourly`'s `hub`);
  - `site/components/grid/MixView.tsx` (the read, the window, the panel), `site/lib/gridAnchors.ts` (`HUB_PRICE_ANCHOR`, `hubPriceAnchor`, `METHOD_HUB_PRICE`), `site/lib/gridtables.ts` (the Clean list);
  - `site/scripts/check-values.mjs` (the three kinds), `site/scripts/check-methods.mjs` (`TABLE_KEY`);
  - `site/scripts/test-grid-files.mjs`, `site/scripts/test-grid-failed-reads.mjs`, `tests/test_session473.py`;
  - `docs/methods/generation_mix_hourly.md` (the chain 100 section with its Decisions, and a line in "The figures on the page and their keys").
- On this machine only: `runs/s1402/` in the worktree (every test's output, same-figures' figure lists, the live recomputation, the drawn sample files), and the scratchpad's one-off scripts.
