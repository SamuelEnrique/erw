# Session 1153 report: the network's gravity view, honest

23 October 2026, from about 19:25 UTC, on samueloldlaptop (the code machine, the old laptop), the fourth session of `queue/done/077-day-23-october-code-grid-tool.md`, beside chain 075. Branch `wip/1153-grid`, cut from `wip/1152-grid`, worktree `C:\Users\lossa\Documents\erw-1153`. Model spend USD 0. No warehouse data written, no Supabase write, no request to any publisher.

## Read these first

- **What already held, each with its line of code:**
  - Item 1, the importer-to-centre rule: `site/lib/networkGravity.ts` `sum += l.a === id ? -v : v;` (net import positive), `pull = clamp(Math.sign(share) * Math.sqrt(Math.abs(share) / S_FULL), -1, 1)` and `const d = clamp(D_MID - D_SPAN * pull, ...)`: an importer (pull above 0) sits nearer the center, square root, full at 0.25, as the method note and ruling 2c say. The rule in one line beside the shape: `site/app/network/Network.tsx`, `data-gravity-key="1"`: "Nearer the center: a net importer; farther out: a net exporter, by its net imports as a share of its generation (a quarter or more is the full pull); on the dashed ring: neither." Unchanged.
  - Item 4, the day kept in the address when the reader picks it: `Network.tsx` `sharedQuery({ view: view.key, t: ... isDayView ? ts.slice(0, 10) ...})` written by `window.history.replaceState(... netToPage(page.keep, withShape(shared, shape)))`, and read back at load (`if (want.view === "day" && want.t) { const f = await watchDay(want.t, false) ...`). It did not hold when switching grid: the picker's links were `gridHref(g.slug, view)`, with no day.
  - Item 5, the keys: the server panel `grid_gravity_<grid>` (session 1151, `components/grid/NetworkFigures.tsx`) keys every figure: `series|eia930_all_generation|...`, `net|import|...`, `calc|pct|...`. This session adds no figure to it (its count of `<F ` stays 10).
- **What this session added:**
  - **Edges with a figure, and only those.** The lines from the Lower 48 to the grids are drawn by `gravityEdges(lay)` (`lay.places.filter((p) => p.net !== null)`): a grid with no tie reported in the hour has no line. Each line answers a hover (a 16-unit clear stroke takes the pointer): its net import or export in whole MW, its share of the grid's net generation and its window ("In the hour from 2026-10-21 23:00 UTC, snapshot refreshed 2026-10-23 14:36 UTC"). A circle's hover card adds its net generation. The words are `gravityTip` in `site/lib/networkGravity.ts`.
  - **The source, said on the face.** Under the frame (`data-gravity-public="1"`): every place and size is drawn from EIA-930's public interchange and net generation only, for every grid, PJM, MISO, ISO-NE and NYISO included: no grid operator's own table places or sizes a circle. And, honestly, the one exception: the color is `carbon_intensity_hourly`, which since 16 December 2025 divides California's emissions by CAISO's own generation (the join). The server panel says the same of its figures, all EIA-930.
  - **The day, in the picker.** On the Gravity tab the grid picker carries `net=day&t=<day>` from the address (`site/lib/carry.ts`, `components/tool/CarryLink.tsx`, an optional `carry` on the shared `ToolPicker`), read with `useSearchParams`, which follows the component's `replaceState`. The server's first render carries it too. Other pickers are unchanged.
  - **The replayed day: the live hour only, said plainly.** The replay's files hold each day's interchange and demand but no generation, so the shape draws nothing for a day (as before) and now says the day stays in the address and the Network and Map shapes draw it. The server panel says: "These are the figures of the hour the shape opens on, in the live week. A day picked in the replay stays in the address, but neither the shape nor this table draws it ... no figure here is that day's." No day figure is drawn, so none is unkeyed.
- **`grid_network_nodes`:** a warehouse table (`warehouse/output/grid_network_nodes.csv`, by `warehouse/derived/grid_network.py`, in `coverage.csv`), **not in the live set** (`warehouse/supabase/live_set.yaml` names no `grid_network` table). The shape's nodes are the seven ISOs of `GRAVITY_GRIDS`; their names come from the snapshot's `nodes` (`site/data/grid_network.json`, or the hourly snapshot in Storage), written by the same script. Written into the method note.
- **No default figure moved:** no key was added, removed or changed; the rule, scale, source and what is drawn are as the rulings set them (1a, 2c, 6a).

## What to review

After the landing (none yet; see below), on production:

1. Open `https://erw-flame.vercel.app/internal/open`, paste the token, press **Open the internal view**.
2. Open `https://erw-flame.vercel.app/grid?grid=ercot&view=gravity&shape=gravity`. Hover the line from the Lower 48 to ERCOT: the card gives "Net import (or export) N MW, over its reporting ties (EIA-930 interchange)", the share of its net generation and "In the hour from ..., snapshot refreshed ...". Hover the ERCOT circle: its net generation is added.
3. Read the note under the frame: its last sentences say the shape is drawn from EIA-930's public interchange and net generation only, for every grid, and that the color for California since 16 December 2025 uses CAISO's own generation.
4. In "A day since 2019", pick 2025-07-01: the shape says it is drawn for the live week only and that the day stays in the address; the address holds `net=day&t=2025-07-01`. Press **CAISO** in the grid picker: the new address keeps `net=day&t=2025-07-01`, and the replay opens on that day.
5. Scroll to "What the gravity shape draws": the note says these are the live week's hour and no figure is the day's, and that every figure is EIA-930's.
6. Repeat 2 on `https://erw-flame.vercel.app/grid?grid=caiso&view=gravity&shape=gravity` and `https://erw-flame.vercel.app/grid?grid=us48&view=gravity&shape=gravity`.
7. Screenshots: `docs/brand/review-1153/before-gravity-{ercot,caiso,us48}-{desktop,mobile}.png` (production at about 19:45 UTC, the shape scrolled into view). No "after" shots: no build (below).

## Checks

- `scripts/db_probe.py` from the main checkout: exit 0 at 19:38 UTC (open, 0.62 s).
- `scripts/buildlock.py acquire 1153-grid --wait-min 20`: exit 1 at 19:59 UTC, the lock held by chain 075's `s1126` since 19:28 UTC; `duty.py beat` every five minutes while waiting (exit 0). So **no build**: no local server, no check-values run, no "after" screenshots, and `scripts/test-network.mjs` (a browser test against a running site) not run.
- `npm ci` in `site/`: exit 0. `npm run content`, `npx next typegen`: exit 0.
- `npx tsc --noEmit -p .` in `site/`: exit 0 (after the last edit).
- `node scripts/test-gravity.mjs` (new, 6 tests: the rule's sign and square-root scale on typed cases, edges only with a figure, the hover words, the committed snapshot's edges, the carried day): exit 0.
- `node scripts/test-grid-keys.mjs`: exit 0.
- `node scripts/check-methods.mjs` (the keys recorded): exit 0, 553 of 553 figures named.
- `python -m unittest` on `tests.test_session1153` (new) and the 18 files that read these sources (`109`, `124`, `168_network`, `180`, `193`, `237`, `241c`, `266`, `299`, `401`, `412`, `428`, `473`, `502`, `538`, `54`, `583`, `93`): exit 0, 259 tests, 7 skipped. A first run failed `test_session502` (it finds each tab's block by `{view === "gravity" ?`, which the picker's `carry` expression matched first): the expression moved to a `const pickerCarry` line; no assertion changed.

## The landing

- None in this session: the chain lands its sessions together once they are green (the brief). The branch is pushed: `wip/1153-grid`.

## To finish

- The build and its checks, when the build lock is free and `db_probe` answers 0: `python scripts/buildlock.py acquire 1153-grid`; in `site/`, `npm run build` (the anon key only); `next start -p 3153`; `MSYS_NO_PATHCONV=1 CHECK_VALUES_PAGES=/grid,/network node scripts/check-values.mjs http://localhost:3153` (expected: no key added or removed, every value matching); `node scripts/test-network.mjs http://localhost:3153`; the after screenshots at 1280 and 390 of the Gravity tab for ERCOT, CAISO and the Lower 48, with an edge and a circle hovered, under `docs/brand/review-1153/`; stop the server by its PID and its port; `release 1153-grid`.
- Land `wip/1153-grid` with the chain's combined landing (it stacks on 1151 and 1152): `scripts/land_check.py --ref <the combined branch>`, the snapshot before as its own command, the push to `task/`, the snapshot after once production shows the new commit, `compare`. Expected differences: on the Gravity tab of `/grid`, the two new sentences of the panel "What the gravity shape draws" (served), and in the browser the note's new sentences, the hover line under the shape and the hover cards; no number.

## Decisions made without you

- **The shape draws nothing for a replayed day, as before**, and now says why and that the day stays in the address. The replay's files hold interchange and demand by day but no generation; placing or sizing a circle from demand would change the rule (ruling 1a: one source, net generation). So the server panel says plainly that it draws the live hour only (the task's second branch). No day figure is drawn, so none is unkeyed.
- **The color is named as the one input that is not EIA-930's alone.** For places and sizes, no grid operator's own table is read; but the circles' color (`carbon_intensity_hourly`) divides California's emissions by CAISO's own generation since 16 December 2025 (`warehouse/derived/carbon_intensity.py`, the join). The note says "no grid operator's own table places or sizes a circle" and names the color's exception, rather than a sentence that would be false.
- **An edge is the line from the Lower 48 to a grid**, the only lines the shape draws; its figure is the grid's net exchange over its reporting ties (the sum the pull uses). A grid with no tie reported in the hour loses its line; on today's snapshot every grid has one in the opening hour, so no line disappears.
- **The picker carries the day through a shared piece**, `ToolPicker`'s optional `carry` (`components/tool/CarryLink.tsx`, `lib/carry.ts`), on the Gravity tab only and for `net=day` with its `t` only: the live week's hour and the stories are not carried, nor do the tabs carry it. A picker without `carry` (the map's queues) draws exactly as before.
- **The hover cards' numbers are not keys**: they are drawn in the browser on hover, as session 1152's chart cards are; the same figures are keyed in the server panel.
- **The rule in one line beside the shape already held** (the `data-gravity-key` line); not rewritten.

## For Samuel's ruling

- None new.

## Files

- New: `site/lib/carry.ts`, `site/components/tool/CarryLink.tsx`, `site/scripts/test-gravity.mjs`, `tests/test_session1153.py`, `docs/brand/review-1153/` (6 PNGs, production before), this report.
- Changed: `site/lib/networkGravity.ts` (`gravityEdges`, `netWords`, `gravityTip`, `windowWords`; the rule untouched), `site/app/network/NetworkGravity.tsx` (edges, hover card, the note, the replayed day's words), `site/app/network/Network.tsx` (the `at` window, the hover line), `site/components/grid/NetworkFigures.tsx` (two sentences, no figure), `site/components/tool/Choose.tsx` (`carry`), `site/app/grid/page.tsx` (the Gravity tab's picker carries the day), `docs/methods/grid_network.md` (four bullets in "The gravity shape").
