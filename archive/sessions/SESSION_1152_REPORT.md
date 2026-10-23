# Session 1152 report: the energy mix, hourly and live

23 October 2026, from about 18:20 to 19:25 UTC, on samueloldlaptop (the code machine, the old laptop), the third session of `queue/done/077-day-23-october-code-grid-tool.md`, beside chain 075 and session 1157. Branch `wip/1152-grid`, cut from `wip/1151-grid`, worktree `C:\Users\lossa\Documents\erw-1152`. Model spend USD 0. No warehouse data written, no Supabase write, no request to any publisher (Supabase's REST API read lightly with the anon key, as the brief allows).

## Read these first

- **The Mix tab's hourly block has its figures, keyed.** At the top of "<grid>: hourly mix, last 7 days", a panel `data-grid-panel="grid_mix_<grid>"`: the 24 hours that end with the newest hour held, their net generation (MWh), each fuel's MWh and share of that net generation, the hour of peak demand with its MW, and the newest hour held with its net generation and its age against the page's drawing time. Every figure has a one-line hover tip (table, entity, variables, window).
- **The chart answers a hover with each fuel's MW and share**, and marks the peak demand hour (a dashed accent line, named "Peak demand, HH:MM UTC" at its top and in the hover card). It runs on to the newest hour held when that is later than the last complete day (it never is today: the table is loaded by whole UTC days).
- **The monthly mix by grid is the second view**, `mixp=month` in the address (chips "Hourly, last 7 days" and "By month" at the top of the panel): the grid's last 24 months of `generation_mix_hourly_profile` (EIA-930 by month over its complete days, CAISO's own data for California since January 2026), stacked, each fuel's MWh and share on hover; under it the newest month's MWh and share and the twelve months' MWh, keyed. The state monthly view below stays as it was.
- **No EIA-930 sub-region generation table exists in the live set**, and none can: EIA-930 publishes sub-region (sub-BA) data for demand only (`eia930_subba_demand_hourly`, out of the live set). `generation_mix_hourly` is not a table either: the hourly mix is `eia930_all_generation` (by balancing authority, the live set's 35-day window, read 9 days). The only monthly mix by balancing authority in the live set is `generation_mix_hourly_profile` (the seven ISOs, `iso:<grid>`, in the live set as "review": loaded and readable, kept out of the public catalogue's counts), so the Lower 48 has no monthly view by grid: its panel says "not built for the Lower 48" and the state view below is its monthly mix.
- **California's hourly mix stays withheld** by the session 118 ruling, in its words, not as "license needed": the panel for CAISO carries only the two chips and a line that the monthly mix (CAISO's own data since January 2026) is under "By month". No grid of these tables is held for a license.
- **One key kind extended, none added:** `series_sum`'s variable part may now name several variables, comma separated (a fuel group such as wind and wind with battery), recomputed with `in.(...)`. No existing key has a comma, so no existing key changes what it computes.
- **A chart fault found and fixed:** on production the hourly chart drew the "Other" band as a tall red wedge from below zero to the top of the stack every night (`docs/brand/review-1152/before-mix-hourly-ercot-desktop.png`): `TimeChart` drew each stacked band from the band before it, and when ERCOT's batteries charge (storage below zero) the band after storage started from storage's negative value. Each band is now drawn from the running sum of its own side of zero. A stack whose values are all held and positive draws exactly as before; only the Grid tool's stacked charts use `stack` (`components/mix/Now.tsx`, `components/grid/YourGrid.tsx`, the new monthly view), so no other page's chart changes.
- **A build was possible:** `scripts/db_probe.py` (main checkout) answered open at 18:37 and 19:10 UTC; the build lock was held by chain 075 (`s1112`) and then by the orchestrator's landing (`land-c077a`) until 19:10 UTC. Built in the worktree, served on port 3152, check-values on every `/grid?grid=` address and `/mix`: 991 of 991 values match, exit 0, before and after the chart fix.

## What to review

After the landing (none yet; see below), on production:

1. Open `https://erw-flame.vercel.app/internal/open`, paste the token, press **Open the internal view**.
2. Open `https://erw-flame.vercel.app/grid?grid=ercot`. Scroll to "ERCOT: hourly mix, last 7 days". At its top: the chips, the sentence "The 24 hours from ... (24 of 24 hours held): ... MWh net generation. Peak demand ... MW, in the hour from ...", the newest hour's line with its age, and the table of fuels (MWh, share). Hover a dotted figure: one line, its table and window.
3. Hover the chart: the card gives each fuel's MW and its share of the hour (one decimal); at the dashed line it adds "Peak demand, HH:MM UTC".
4. Press **By month** (`https://erw-flame.vercel.app/grid?grid=ercot&mixp=month#hourly`): the 24 months, hover for MWh and share; the table of the newest month and the twelve months. Press **Hourly, last 7 days** to come back.
5. Open `https://erw-flame.vercel.app/grid?grid=caiso`: the hourly block is withheld as before, with the chips; **By month** draws California's months.
6. Open `https://erw-flame.vercel.app/grid` (the Lower 48): the hourly panel for `eia930:US48`; **By month** says "not built for the Lower 48".
7. View source, search `grid_mix_ercot`.
8. Screenshots: `docs/brand/review-1152/`.

## Checks

- `scripts/db_probe.py` from the main checkout: exit 0 at 18:37 (0.54 s) and at 19:10 UTC (0.71 s).
- `scripts/buildlock.py acquire 1152-grid --wait-min 60`: exit 0 at 19:10 UTC (waited from 18:37); `release 1152-grid`: exit 0 at 19:19 UTC.
- `npm ci`: exit 0. `npm run content`, `npx next typegen`: exit 0. `npx tsc --noEmit -p .`: exit 0 (after the panel and again after the chart fix).
- `node scripts/test-mix-hourly.mjs` (new, 10 tests on the committed fixture): exit 0.
- `node --import ./scripts/alias-register.mjs scripts/test-mix.mjs` (one test added, `mixp`): exit 0, 11 tests. `node scripts/test-grid-keys.mjs`: exit 0.
- `npm run build` (twice: the panel, then the chart fix; the anon key, no service key, in the environment): exit 0 both, no "statement timeout" in either log.
- check-values, `CHECK_VALUES_PAGES=/grid?grid=,/mix`, `http://localhost:3152` (every tab of the eight grids, the two new monthly addresses, `/mix` and `/mix?ba=erco&state=TX` through their redirects): exit 0, 991 of 991 values match, 0 failures, every floor met; notes: `/grid?grid=ercot&mixp=month` (111 numbers), `/grid?grid=caiso&mixp=month` (293) and `/grid?grid=caiso&view=network` (15) have no floor yet. Run again after the chart fix: the same, exit 0.
- `python -m unittest` on `tests.test_session1152` (new, 9 tests), `303`, `473`, `318`, `332`, `584`, `416`, `417`, `133`, `118`, `168_mix`, `237`, `502`, `161`, `144_page`: exit 0. One earlier run of `tests.test_session502` failed with node's Windows exit crash (`UV_HANDLE_CLOSING`, exit 3221226505) after its node test printed "11 of 11 passed"; run again alone: exit 0.
- Screenshots, local build, the panel scrolled into view: `docs/brand/review-1152/` (hourly ERCOT at 1280 and 390, hourly ERCOT with the hover card, by month ERCOT at 1280 and 390 and with the hover card, CAISO hourly, the Lower 48 by month), and production before at 1280 and 390 (`before-mix-hourly-ercot-*`). The hover cards read "2026-10-22 16:00 UTC: Natural gas 19,775 MW, 36.0% ... Storage -5,016 MW, -9.1%" and "2025-09: Natural gas 20,830,622 MWh, 47.4% ...".
- The local server stopped by its port (3152 free); no browser left running.

## The landing

- None in this session: the chain lands its sessions together once they are green (the brief). The branch is pushed: `wip/1152-grid`.

## To finish

- Land `wip/1152-grid` with the chain's combined landing (it stacks on `wip/1151-grid`): `scripts/land_check.py --ref <the combined branch>`, the snapshot before as its own command, the push to `task/`, the snapshot after once production shows the new commit, `compare`, every difference listed (expected: on the Mix tab of `/grid` and on `/mix`'s redirect, the panel's new text and numbers above the hourly chart; the hourly chart's hover card gains shares and the peak mark; the Grid tool's stacked charts draw a negative band below zero without the wedge above it; nothing else).
- At that landing, rewrite the floors of the Grid pages from a passing run: `CHECK_VALUES_WRITE_FLOOR=1 CHECK_VALUES_PAGES=/grid node scripts/check-values.mjs <base>` (the two new addresses `/grid?grid=ercot&mixp=month` and `/grid?grid=caiso&mixp=month` have no floor yet; the Mix tab pages' floors should rise by the panel's keys).

## Decisions made without you

- **The peak is peak demand** (`eia930_all_demand`, `demand_mw`), not peak net generation: a trader's peak is the load peak (prices, reserves, 4CP and the evening ramp all key off demand); net generation differs from it by the grid's net imports. It is the highest hour of the same 24 hours as the headline, keyed `series_max|eia930_all_demand|demand_mw|<start>|<end>|<entity>` (the checker proves it is the highest of the window).
- **The headline's window is the 24 hours that end with the newest hour held** (an hour is held when its `net_generation_mw` is), and its "hours held" says how many of the 24 are; the share's denominator is `net_generation_mw` over the same hours, as the task says. The hover card's share is of the sum of the fuels drawn at that hour (the method note's rule for a share), so the two can differ by the gap between EIA's total and its sources (on ERCOT's fixture the eight shares of the headline add to 99.9997 percent).
- **The age** is whole hours from the newest hour's end to the page's drawing time (`renderTime()`, the page is cached up to an hour); the clock is not a key, the hour is (`series|eia930_all_generation|<entity>|net_generation_mw|<hour>`).
- **The monthly view's table:** the newest month's MWh and share (stored in the table, `series|...`), and the MWh of the twelve calendar months to it (`series_esum|...`); a month the build did not write is named on the face (ERCOT: 2025-12). No twelve-month share is drawn: the table's shares are of the sum of its eight sources, and a share of two sums would need a third convention.
- **The stacking fault was fixed in `TimeChart`, not around it:** the task said to keep the chart's look, but the look on production was a drawing fault (a band spanning both sides of zero), not a design; the fix changes only stacks with a value below zero or a gap below a band, and only the Grid tool draws stacks. A test pins the new base (`tests/test_session1152.py`).
- **The monthly chart's first month (ERCOT, 2024-09) shows a thin white diagonal** at its left edge on the local build (`mix-month-ercot-desktop.png`), where storage is not yet itemized; left as it is, for the brand pass (session 1159) to look at.
- **`TimeChart` gained two optional props**, `share` and `marks`, both off by default; `StackedArea` and `Now.tsx`'s `Hourly` pass them through. No other chart sets them. `tests/test_session303.py`'s signature assertion was extended to the new signature, with two new assertions.
- **The monthly view is drawn with `TimeChart` directly** (stacked, by month), not `StackedArea`: `tests/test_session473.py` lets only the Grid and board files draw `StackedArea`; the new `components/grid/MixFigures.tsx` was added to that test's list of the tool's own components (brand rules, one `check=`), and the toggle stands in `MixView.tsx`, which already draws the mix's chips.
- **`mixp` is a field of the mix page's choice** (`lib/mixpage.ts`), set only on "Now and by state" and only when it is `month`, so the opening choice and every existing address are unchanged; `scripts/test-mix.mjs` gained a round-trip test. The state form carries `mixp` as a hidden input.
- **The fixture** (`tests/fixtures/session1152/mix_hourly_erco.json`) is real rows read with the anon key on 23 October 2026: ERCOT's generation and demand from 20 October, and `iso:ercot`'s months from September 2025. The test adds one made-up row set only inside one test (a zero `wind_with_battery` copy of the wind rows, to prove a group of two variables is one key) and says so.

## For Samuel's ruling

- None new.

## Files

- New: `site/lib/mixHourly.ts`, `site/components/grid/MixFigures.tsx`, `site/scripts/test-mix-hourly.mjs`, `tests/test_session1152.py`, `tests/fixtures/session1152/mix_hourly_erco.json`, `docs/brand/review-1152/` (10 PNGs), this report.
- Changed: `site/components/grid/MixView.tsx` (the panel, the toggle, the demand and monthly reads), `site/components/mix/Now.tsx` (`Hourly`: share, marks, through), `site/components/StackedArea.tsx` and `site/components/TimeChart.tsx` (the two optional props; `TimeChart`'s stacking base), `site/lib/mixpage.ts` (`mixp`), `site/scripts/check-values.mjs` (the comma list in `series_sum`, two addresses), `site/scripts/test-mix.mjs`, `tests/test_session303.py`, `tests/test_session473.py`.
