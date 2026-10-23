# Session 1154 report: the scarcity hours

23 October 2026, from about 19:25 UTC, on samueloldlaptop (the code machine, the old laptop), the fifth session of `queue/done/077-day-23-october-code-grid-tool.md`, beside session 1153 (the network component) and chain 076. Branch `wip/1154-grid`, cut from `wip/1152-grid`, worktree `C:\Users\lossa\Documents\erw-1154`. Model spend USD 0. No warehouse data written, no Supabase write, no request to any publisher (Supabase's REST API read lightly with the anon key, as the brief allows).

## Read these first

- **The scarcity hours are on the Mix tab**, after the mix blocks and before "Generation mix, as a table": a panel `data-grid-panel="grid_scarcity_<grid>"`, `id="scarcity"`, for the grid in view (`site/components/grid/ScarcityPanel.tsx`, `site/lib/scarcityStrip.ts`). No existing figure moved.
- **ERCOT and CAISO: a strip by day (across) and hour of day in the grid's standard time (down)**, drawn by the shared `HeatChart` (`components/svgchart.tsx`, with its Chart | Table toggle). A cell for each held hour: filled where `rt_hour_ge_1000` or `da_hour_ge_1000` is 1, faint where both are 0, hatched where not held; an ink square where `own_signal` is 1; a line under the chart names the square.
- **The window: 1 to 30 September 2026**, the latest 30 days the table holds (session 1150's decision), counted in the grid's standard-time days as the method counts them. The face names the newest hour (2026-10-01 05:00 UTC for ERCOT, 07:00 UTC for CAISO), how many days before the page was drawn it was, and that these are not the 30 days before today.
- **The hover on a cell:** the hour in standard time and UTC, the variables at 1, `rt_intervals_ge_1000` of 4, `own_signal` (or why it is not held: ERCOT's adder ends 4 December 2025), the hour's highest 15-minute real-time price at the hub (`iso_rtm_hub_prices`: held from 18 September 2026 15:45 UTC, the live set's 35 days), for ERCOT before that the highest of ERCOT's local day (`ercot_hub_prices_daily`, `rt_max`, said as the day's), else "no price of this hour is in the live set". Every tip ends "Level: USD 1,000 per MWh, docs/methods/scarcity_hours_by_grid.md; prices: ERCOT." (or CAISO).
- **The counts under the strip, each keyed:** real-time hours at or above USD 1,000 of the hours held, the 15-minute intervals, day-ahead hours of held, the own signal's hours of held (CAISO), the highest 15-minute price held, and for ERCOT the highest of its local days. On the live set today every count is 0: no hour of September 2026 reached USD 1,000 at either hub, and no EEA or Flex Alert was in force at CAISO (ERCOT's own signal is not held after 4 December 2025, said on the face).
- **One new key kind, `series_n|<table>|<variable>|<start>|<end>|<entity>`:** the distinct hours the rows hold ("of N hours held"), recomputed in `check-values.mjs` by the page's own function (`lib/scarcityStrip.ts heldHours`), tested in the node test; `check-methods.mjs` knows it as a table figure. The other keys are kinds check-values knew (`series_sum`, `series_max`).
- **The other grids say why in one line:** PJM "license needed" (no PJM price is held); MISO "paused" (since 4 October 2026); NYISO and ISO-NE "license needed" (their prices need a license from 2026-10-21, read from `lib/license.ts`); SPP "not in the table yet" (its hub prices are public, `iso_rtm_hub_prices` is held for MISO only; SPP's own signal is not held as a table). The Lower 48: the table is by grid, with links to ERCOT's and CAISO's panels.
- **No build, so no screenshots and no check-values run:** `scripts/db_probe.py` (main checkout) answered open (0.51 s) at 19:41 UTC, but the build lock was held by chain 076 (`s1126`, since 19:28 UTC) through the 20 minutes the rules allow (waited 19:42 to 20:03 UTC, `duty.py beat` every five minutes); the wait was stopped and nothing was built. The keys are proved on the fixture by the node test, which recomputes each one as check-values does.

## What to review

After the landing (none yet; see below), on production:

1. Open `https://erw-flame.vercel.app/internal/open`, paste the token, press **Open the internal view**.
2. Open `https://erw-flame.vercel.app/grid?grid=ercot#scarcity` (the Mix tab). Under "Where the power comes from": "ERCOT: the scarcity hours, last 30 days held". Read the first paragraph: the window, the newest hour and its age.
3. Hover any cell of the strip: the card gives the hour (CST and UTC), "Variables at 1: none", the intervals, the price (from 18 September the hour's highest 15-minute price; before it the local day's highest) and the level's source line.
4. Press **Table** above the strip: the 24 by 30 values. Press **Chart** to come back.
5. Hover a dotted count under the strip: its table, entity, variable and window.
6. Open `https://erw-flame.vercel.app/grid?grid=caiso#scarcity`: the same for CAISO (PST), with the own signal's count (EEA or Flex Alert), no daily price line.
7. Open `https://erw-flame.vercel.app/grid?grid=pjm#scarcity`, then `miso`, `nyiso`, `isone`, `spp`: one line each, the word on the face, the reason beside it. `https://erw-flame.vercel.app/grid#scarcity`: the two links.
8. View source, search `grid_scarcity_ercot`.
9. Screenshots: not taken, no build (session 1158 or the combined landing's build can take them at 1280 and 390 under `docs/brand/review-1154/`).

## Checks

- Precheck for session 1154: run by the orchestrator, exit 0.
- `npm ci` in `site/`: exit 0. `npm run content`, `npx next typegen`: exit 0.
- `npx tsc --noEmit -p .` in `site/`: exit 0.
- `node scripts/test-scarcity-strip.mjs` (new, on the committed fixture): exit 0, 10 of 10.
- `node --import ./scripts/alias-register.mjs scripts/test-session502.mjs`: exit 0, 11 of 11. `node scripts/test-grid-keys.mjs`: exit 0.
- `python -m unittest` on `tests.test_session168_network`, `207`, `237`, `247`, `254`, `265`, `280`, `299`, `401`, `409`, `467`, `468`, `473`, `502`, `538`, `54`, `1152`, `133`, `303` (every test file that reads the Grid page, its tables list, the scarcity table, check-methods or the mix components): exit 0, 220 tests, 2 skipped. `tests.test_session1154` (new, 8 tests): exit 0.
- `scripts/db_probe.py` from the main checkout: exit 0 at 19:41 UTC (0.51 s).
- `scripts/buildlock.py acquire 1154-grid`: waited 19:42 to 20:03 UTC behind `s1126`, stopped at the 20-minute limit (the process ended, the lock never held by this session, so no release needed); `status` at 20:04: held by `s1126`.
- Supabase reads (anon key, light, for the fixture and to learn the tables): `scarcity_hours_by_grid` (the newest hours, September 2026 at 0 for both grids; CAISO's one hour at or above USD 1,000 in 2026 is 27 August 05:00 UTC), `iso_rtm_hub_prices` (held from 18 September 2026 15:45 UTC; ERCOT's variable `spp_rtm`, CAISO's `lmp_rtm_15m_mean`), `ercot_hub_prices_daily` (`rt_max` by local day). The live set's series rows carry no `x_detail`, so CAISO's notices are not on the hover.

## The landing

- None in this session: the chain lands its sessions together once they are green (the brief). The branch is pushed: `wip/1154-grid`.

## To finish

- Land `wip/1154-grid` with the chain's combined landing (it stacks on `wip/1152-grid`; session 1153 works beside it on the network files, and the two touch `site/app/grid/page.tsx`, `site/lib/gridtables.ts` and `site/scripts/check-values.mjs` only in separate places): `scripts/land_check.py --ref <the combined branch>`, the snapshot before as its own command, the push to `task/`, the snapshot after once production shows the new commit, `compare`, every difference listed (expected: on the Mix tab of every `/grid` address and on the redirects that open it (`/mix`, `/grid/<iso>`), the scarcity panel's text and, for ERCOT and CAISO, its strip and keyed counts; nothing else).
- At that landing, rewrite the floors of the Grid pages from a passing run (`CHECK_VALUES_WRITE_FLOOR=1 CHECK_VALUES_PAGES=/grid node scripts/check-values.mjs <base>`), and if `scripts/check-methods-keys.json` is rewritten, the panel's figures are named in the method note's new section.

## Decisions made without you

- **The days are the grid's standard-time days**, so the window is 1 to 30 September 2026, not "2 September to 1 October" as session 1150 wrote it in UTC days: the strip's rows are the hours of a standard-time day (the method's own clock), and the table's last hour (23:00 standard time on 30 September) ends that day.
- **The price on hover is the hour's highest 15-minute price** from `iso_rtm_hub_prices` (about 1,200 rows a grid for the window, under the 3,000 the task allowed); the live set holds those from 18 September only, so for ERCOT the 1 to 18 September hours give the local day's highest from `ercot_hub_prices_daily` (ERCOT's clock day, which can differ by an hour from the strip's standard-time day, said as "local day"), and CAISO's say no price is in the live set. No other table was read.
- **The cell is the price count; the own signal is a square on it.** An hour whose own signal alone is held (CAISO before its prices, 1 September 2024) keeps a hatched cell and its square; the test pins it on the EEA Watch of 24 July 2024.
- **`series_n` counts distinct hours**, as `lib/datacenter/answers.ts` reads an hour written twice once. The counts are `series_sum` sums of 0 or 1 values, which equal the panel's per-hour reading as long as the table writes each hour once (its key does).
- **The constants are not imported from `lib/datacenter/answers.ts`**: importing it would put that file's other tables on the Mix tab's license line (`tests/test_session502.py` reads the imports). `lib/scarcityStrip.ts` keeps its own `SCARCITY_TABLE`, `SCARCITY_LEVEL` and hubs; the node test holds them equal to `SBG_TABLE`, `SBG_LEVEL`, `SBG_HUBS`. `answers.ts` is unchanged.
- **The newest hour's age in days is not a key**, as the mix panel's age in hours is not (session 1152): it is the clock against the page's drawing time; the newest hour is written as text.
- **The Mix tab's license line gains three tables** (`scarcity_hours_by_grid`, `iso_rtm_hub_prices`, `ercot_hub_prices_daily`, all public in coverage); `iso_rtm_hub_prices` shows its existing "held for MISO" words.
- **Older tests extended, none loosened in what they pin:** `tests/test_session502.py` (the Mix view's components gain `ScarcityPanel`), `tests/test_session473.py` (the panel among the tool's own components, one `check=`; and in the list of files allowed to draw `mix/Now.tsx`'s `Missing`).
- **The fixture** (`site/scripts/fixtures/scarcity_strip.json`) is real rows read once with the anon key on 23 October 2026: ERCOT 28 to 30 September 2026 with its prices and days, CAISO 29 and 30 September 2026 with its prices, CAISO 26 and 27 August 2026 (its one real-time hour at or above USD 1,000, 21:00 PST on 26 August), CAISO 24 and 25 July 2024 (the EEA Watch's seven hours).

## For Samuel's ruling

- None new.

## Files

- New: `site/lib/scarcityStrip.ts`, `site/components/grid/ScarcityPanel.tsx`, `site/scripts/test-scarcity-strip.mjs`, `site/scripts/fixtures/scarcity_strip.json`, `tests/test_session1154.py`, this report.
- Changed: `site/app/grid/page.tsx` (one import, the panel), `site/lib/gridtables.ts` (three tables in the Mix list), `site/scripts/check-values.mjs` (`series_n`), `site/scripts/check-methods.mjs` (`series_n`), `docs/methods/scarcity_hours_by_grid.md` (the section "On the Grid tool"), `tests/test_session473.py`, `tests/test_session502.py`.
