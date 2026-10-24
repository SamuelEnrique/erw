# Session 1185 report: the Lower 48 in each new panel

24 October 2026, from about 04:05 to 04:45 UTC, on samueloldlaptop (the code machine, the old laptop), the eighth session of `queue/done/091-day-25-october-code-grid-tool-3.md`. Branch `wip/1185-grid`, cut from `wip/1184-grid` (chains 077, 078 and 091 stacked, not on main), worktree `C:\Users\lossa\Documents\erw-1185`. Code, tests and documents only (`runs/c077/brief.md`: no build, no server, no browser). Model spend USD 0. No warehouse data written, no Supabase write, no request to any publisher; light reads of Supabase's REST API with the anon key (the probes below, one fixture of 637 state months, same-figures' answers held in memory).

## Read these first

- **The Lower 48's view by month is drawn.** `/grid?mixp=month` (panel `grid_mix_us48`) said "not built for the Lower 48". It now draws the sum of the 48 contiguous states and DC in `state_generation_mix_monthly` (EIA-923): the last 24 months every one of the 49 holds (September 2024 to August 2026 today), stacked by the table's nine fuel groups, each group's MWh and share on hover; under it the newest month's MWh and share of each group, the twelve months' MWh, and the nine groups' total for both. The face says plainly: "the sum of the 48 contiguous states and the District of Columbia in EIA-923's monthly net generation by state (state_generation_mix_monthly), not EIA-930's US48 total, which adds up the balancing authorities hour by hour".
- **Why the states.** I searched the live set (`warehouse/metadata/coverage.csv` for every table holding US48, `live_set.yaml`, anon reads). No table holds EIA-930's US48 by month with its mix:
  - `eia930_all_generation` holds `eia930:US48` hour by hour from 26 August 2026 only.
  - `carbon_intensity_monthly` holds the Lower 48's intensity and not its generation.
  - `generation_mix_hourly_profile` is by ISO grid.
  - So the Lower 48 is the states' sum, as the chain file allowed.
- **One new key kind, `states_sum|state_generation_mix_monthly|<variables>|<start>|<end>|lower48`.** `check-values.mjs` reads the 49's rows of the range once and sums the key's variables over the months every one of the 49 holds. It uses the page's own function, `site/lib/lower48.ts` `statesSum`. A share is `calc|pct|<group>|<nine>`. `check-methods.mjs` knows the kind as a table figure (`TABLE_KEY`), and `components/Num.tsx`'s license gate reads its table, held as a whole table (public today). All 126 figures of the new keys are named by the notes.
- **A missing state month is not drawn and not summed.** It is named on the face with the locations it misses. No month of the live set misses one today: all 49 hold every month from 2024-01 to 2026-08, read 24 October 2026.
- **The two Lower 48 totals.** The sum of the 49 against EIA-923's own national row (`eia:US` less AK and HI) differs by at most 0.23 percent a month, January 2024 to August 2026. The sum is not compared with EIA-930's US48: the live set holds no month that both cover.
- **The scarcity strip's Lower 48 line stays, and now says why.** The method counts a grid's hours at its own hub's price and its own operator's signal, and the Lower 48 has neither one hub nor one operator. So the method defines no national scarcity measure, and none is summed from the grids. No table of the coverage with US48 holds a scarcity count, a reserve margin or an emergency signal.
- **Every other "not held" for the Lower 48 in chain 077, 078 and 091's panels, checked and kept:**
  - The replayed day's Lower 48 demand stays "not held". The replay's committed files hold 54 balancing authorities, not US48. Of the live set, only `event_window_daily` holds US48 by day, and only for the COVID window, March 2019 to May 2020. That is not a monthly table, and its rule is not the replay's.
  - The gravity panel's "not held for the hour" is the snapshot's own state, not a structural gap.
  - The Exchange blocks draw the Lower 48.
  - The last 24 hours, the stress views and the stored answers say no "not held" for the Lower 48.
- **No figure moved.** I ran `same-figures.mjs` on 20 addresses with `7c0d713b` (the tip of wip/1184) in a temporary worktree, since removed, against this tree. 2,586 figures matched, every page the same, with 0 new requests. The Lower 48's two monthly addresses (`/grid?mixp=month`, `/grid?grid=us48&view=mix&mixp=month`) lost none of their 102 figures, kept their order, and gained 30 figures (29 keys). I recomputed all 30 live as check-values does: 30 of 30 match.

## What to review

There is no landing yet (below). After the landing, on production:

1. Open `https://erw-flame.vercel.app/internal/open`, paste the token, press **Open the internal view**.
2. Open `https://erw-flame.vercel.app/grid?mixp=month#mix-panel` (the Lower 48, "By month"). The first paragraph reads "The Lower 48 by month, 2024-09 to 2026-08: the sum of the 48 contiguous states and the District of Columbia in EIA-923's ... not EIA-930's US48 total ...", with the net generation of August 2026 dotted (447,868,944.56 MWh today).
3. Hover the chart: each group's MWh and share in a month. Hover a dotted figure in the table: its table, "the 48 contiguous states and DC, summed", the variable and the month or months.
4. Under the table: "Method: the Lower 48 by month, the sum of the states" opens `generation_mix`'s new section. "Download this table (CSV)" gives `erw_grid_mix_us48_monthly.csv`. "Method: the Mix tab's energy mix, keyed, hourly and by month" is there as before.
5. Open `https://erw-flame.vercel.app/grid#scarcity`. After the two links, read "The Lower 48 has no strip of its own: ...".
6. Read `docs/methods/generation_mix.md`, section "The Lower 48 by month, the sum of the states (chain 091, 24 October 2026)", with its Decisions.
7. Screenshots: not taken, no build.

## Checks

- Precheck for session 1185: run by the orchestrator, exit 0.
- `node scripts/test-lower48.mjs` (new, 9 tests, on the committed real rows): exit 0. It recomputes every key as check-values does, shows a state month taken out inside one test is not drawn, not summed and named, and covers a group absent from the newest month.
- Node tests extended, one at a time, both loaders:
  - `test-grid-files`: exit 0, 98 cases. New: the Lower 48 monthly page's block, its file and both method links, and its entry in `GRID_FILE_PAGES`.
  - `test-grid-failed-reads`: exit 0, 61 cases. New: `state_generation_mix_monthly` on timeout, HTTP 500 and an empty answer.
- Other node tests that read a changed file, one at a time, each exit 0:
  - plain node: `test-scarcity-strip`, `test-mix-hourly`, `test-grid-keys`, `test-check-values-run`, `test-check-values-slow`, `test-grid-390`, `test-caiso-alerts`, `test-ercot-notices`, `test-check-revised`;
  - alias loader: `test-grid-addresses`, `test-mix`, `test-grid-ask`;
  - both loaders: `test-grid-methods` (unchanged, 5 of 5; its "others" test holds `METHOD_MIX_US48`'s fragment to the rendered note), `test-grid-file-keys`, `test-grid-units`, `test-grid-held`, `test-grid-reads`, `test-grid-generation`, `test-grid-replay`, `test-grid-stress`.
- `node scripts/check-methods.mjs` (no server): exit 0, 553 of 553 named, 57 pages. `/grid`'s notes now include `generation_mix (components/grid/Lower48Mix.tsx)`. The 126 figures of the new keys are named (a one-off with check-methods' own `figures` and `named`).
- `node --check` on `check-values.mjs` and `check-methods.mjs`: exit 0 each.
- `same-figures.mjs`: two runs, above. The 20 addresses: exit 0. The two Lower 48 monthly addresses: exit 1 (they differ), each by additions only.
- Live recomputation of the 30 new figures (a one-off, anon reads, 2 requests' ranges): 30 of 30.
- `python -m unittest`, one module at a time: every module that reads a changed file (a grep of `tests/` for the changed names, 110 modules with `test_session1185` among them), then `test_session1185` again: 110 of 111 runs exit 0 (skips as before). The one failure was `test_session1185`'s first run: its own assertion matched the word "components/mix/Now" in Lower48Mix.tsx's header comment. The assertion now reads the import (`from "@/components/mix/Now"`); run alone and again at the end, exit 0, 13 tests. No assertion of an older module was removed or changed; `tests/test_session473.py` gained one entry.
- `npx eslint` on the 12 changed or new code files: exit 0 (5 warnings, all in `check-values.mjs` lines 1265 to 1487, none in the lines added).
- Type check through the junction (`mklink /J` to the main checkout's `node_modules`): `npm run content` exit 0, `npx next typegen` exit 0, `npx tsc --noEmit -p .` exit 0. Both junctions (this worktree's and the temporary before worktree's) were removed with `rmdir`, and the main copy's `node_modules` is intact (333 entries).
- Not run (the brief): the build, check-values, check-routes, check-links and the two download checks against a server, screenshots.

## The landing

- None in this session: chain 091 works code-only, stacked on `wip/1176-grid` (chains 077 and 078, not on main). This branch lands with them. Pushed: `wip/1185-grid`.

## To finish

- Land with the chain's combined landing. At that build, against the running site (Git Bash, `MSYS_NO_PATHCONV=1`):
  - check-values on `/grid?grid=us48&mixp=month` (new in its list, no floor yet: rewrite the floors from a passing run, `CHECK_VALUES_WRITE_FLOOR=1`);
  - `check-table-downloads.mjs` and `check-download.mjs --grid` (the new file `grid_mix_us48_monthly`);
  - `check-links.mjs` (the new `#the-lower-48-by-month-...` fragment).
- The snapshots before and after, every difference listed. Expected:
  - on `/grid?mixp=month` and `/grid?grid=us48&view=mix&mixp=month`, the view's text, chart, table, file and method line in place of "not built for the Lower 48";
  - on every Lower 48 Mix address, the scarcity line's new sentence;
  - nothing else.

## Decisions made without you

- **The sum of the 49 locations, not `eia:US` less Alaska and Hawaii.** The national row has no `not_itemized` group and holds sources EIA withholds by state (hydro, August 2026: 62,291 MWh more than the states' sum). A subtraction would be a figure no table holds row by row. The chain file asked for the sum.
- **A new key kind** rather than `series_sum` over a list of 49 entities. A list would put 49 names in each of about 30 keys. And `series_sum` would recompute the twelve months over a month a state misses.
- **A state month is held when the location has a row of any group.** The table writes a location's month only when EIA publishes its total. A location's group with no row (nuclear in Colorado) adds nothing.
- **The view is its own file, `components/grid/Lower48Mix.tsx`.** `tests/test_session1158.py` and `1182` pin MixFigures.tsx's two tables and two files by count, and the new file imports nothing of `components/mix/Now.tsx` (`tests/test_session473.py`). Its one `check=` was added to 473's list of the tool's own components.
- **Its method link is a second link of the mix panel** (`METHOD_MIX_US48` in `lib/gridAnchors.ts`), drawn under the Lower 48's monthly view only. It is not in `GRID_METHOD`, which is one method a panel. Its test is in `test_session1185.py` and in `test-grid-files.mjs`, not a sixth test in `test-grid-methods.mjs`, whose count `tests/test_session1184.py` pins at 5.
- **The read** is the 49's rows since the first of the month 800 days back (the grids' view reads the same window), through `series()`: about 9,200 rows in 10 requests, only on the Lower 48's `mixp=month` address.
- **The chips, the section title ("monthly mix, by grid") and the "By month" chip's title were kept.** The view's first paragraph and its source line say what it draws.
- **The replayed day's Lower 48 demand stays "not held"**, its words unchanged: no table holds the Lower 48 by day for the replay's years, and the chain file's rule is a table by month.
- **The fixture** (`site/scripts/fixtures/lower48_mix.json`, 60 KB) is every row of the 49 from 2025-08 to 2026-08, read once with the anon key at 04:20 UTC. Two tests take rows out inside themselves (DC's 2026-06, the newest month's `not_itemized`) and say so.

## For Samuel's ruling

- The words on the face, "the sum of the 48 contiguous states and the District of Columbia in EIA-923's monthly net generation by state ..., not EIA-930's US48 total ...". Recommendation: keep them.
- Whether the Lower 48's view by month should be EIA-923's national row less Alaska and Hawaii instead of the sum of the states. Recommendation: the sum, as built (decision above).
- Whether the "By month" chip's title and the section's title ("monthly mix, by grid") should change for the Lower 48. Recommendation: "The Lower 48's monthly mix, the sum of the states" in both (a words change).

## Files

- New: `site/lib/lower48.ts`, `site/components/grid/Lower48Mix.tsx`, `site/scripts/test-lower48.mjs`, `site/scripts/fixtures/lower48_mix.json`, `tests/test_session1185.py`, this report.
- Changed:
  - `site/components/grid/MixView.tsx` (the read and the view for the Lower 48), `site/components/grid/ScarcityPanel.tsx` (the Lower 48's why), `site/components/Num.tsx` (the license gate reads a `states_sum` key's table), `site/lib/gridAnchors.ts` (`METHOD_MIX_US48`);
  - `site/scripts/check-values.mjs` (`states_sum`, the address), `site/scripts/check-methods.mjs` (`TABLE_KEY`), `site/scripts/grid-files.mjs` (the file's page), `site/scripts/test-grid-files.mjs`, `site/scripts/test-grid-failed-reads.mjs`, `tests/test_session473.py`;
  - `docs/methods/generation_mix.md` (the section with its Decisions), `docs/methods/generation_mix_hourly.md` (a pointer to it), `docs/methods/scarcity_hours_by_grid.md` (the Lower 48's line).
- On this machine only: `runs/s1185/` in the worktree (every test's output, same-figures' figure lists, the one-off probes), and the probes in the session's scratchpad.
