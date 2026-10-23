# Session 1156 report: the network map

23 October 2026, from about 20:00 UTC, on samueloldlaptop (the code machine, the old laptop), the seventh session of `queue/done/077-day-23-october-code-grid-tool.md`, beside session 1155 (`erw-1155`, the CAISO alerts) and chain 075. Branch `wip/1156-grid`, cut from `wip/c077-land2` (sessions 1150 to 1154 merged with main), worktree `C:\Users\lossa\Documents\erw-1156`. Model spend USD 0. No warehouse data written, no Supabase write, no request to any publisher. No new dependency.

## Read these first

- **What the Map shape already did, each with its line of code:**
  - Item 1, the projection: `site/app/network/NetworkMap.tsx` `const projection = geoAlbersUsa().scale(1300).translate([W / 2, H / 2]);` with `const W = 975, H = 610;`: the project map's numbers (`site/app/map/ProjectMap.tsx` `geoAlbersUsa().scale(1300).translate([487.5, 305])`). The state outlines were **not** drawn: added (below).
  - Item 2, the edges and their direction: each tie with both ends on the map was a `<line>` between the two areas' points with `markerEnd={`url(#${dim ? "erw-flow-head-dim" : "erw-flow-head"})`}` (an arrowhead at the importer) and a dash from the exporter; a tie with no figure was not drawn (`Network.tsx` `linksAt`: `l.mw[h] !== null && l.mw[h] !== undefined && l.mw[h] !== 0`). The lines took no pointer (`<g pointerEvents="none" fill="none">`): **no MW, no window on hover**: added.
  - Item 3, no price on the map: `NetworkMap` takes no price at all (its props: nodes, flows, maxMw, colorOf, pick, neighbours, onPick); the price ring is drawn `pricesOn && shape === "network"` only. Held. The note did not say the lines are EIA-930's public interchange: added.
  - Item 4, a click: `onClick={() => onPick(r.id)}` opened the panel for every region. **No link to `/grid`**: added for the seven ISO grids.
  - Item 5, the keys: the map drew no number (`check=` count 0, `tests/test_session473.py`). Kept at 0.
- **What this session added:**
  - **The project map's state outlines**, from the same file (`us-atlas/states-albers-10m.json`, already on the map's plane): the land under the regions (`data-map-nation`), the borders between states over them (`data-map-state-lines`, no pointer). The derived areas, their label and colors are unchanged.
  - **A line answers a hover** (the middle 60 percent of it, `hitSegment`, so a click near a region's point is still the region's): "From SPP to ERCOT", its MW where held, its window ("In the hour from 2026-10-21 23:00 UTC, snapshot refreshed 2026-10-23 14:36 UTC", the gravity shape's words; a replay day "On 2021-02-15, EIA's Eastern day (the day's average MW)"), "EIA-930's public interchange".
  - **A line's MW only where the panel under the map holds it** (`edgeHeld`): a tie of the grid in view, in the hour `grid_network_<grid>` is drawn for (the component's opening hour), in the live week. Every other line says where the checked figure is; its width follows the flow as before. The node test proves, for each of the seven grids on the committed snapshot, that every MW the map would write is the panel's own tie figure (same magnitude, same direction, key `net|tie|<ba>|<other>|<hour>`), and that no other line writes one.
  - **A grid clicked:** one of the seven ISO grids other than the grid in view is a link (`<a href>` around its region, `data-region-href`) to `gridHref(slug, "network", { shape: "map" })`, the moment carried (`net` and `t`: the replay's day, a story, an hour moved to). The grid in view and every other balancing authority open the panel as before.
  - **The note under the map** (`data-map-public`, `data-map-checked`): the lines are EIA-930's public interchange for every grid, PJM, MISO, ISO-NE and NYISO included; no price is drawn; the panel under the map carries the checked figures.
- **No default figure moved:** no key added, removed or changed; the server panels are untouched; the map draws no key.

## What to review

After the landing (none yet; see below), on production:

1. Open `https://erw-flame.vercel.app/internal/open`, paste the token, press **Open the internal view**.
2. Open `https://erw-flame.vercel.app/grid?grid=ercot&view=network&shape=map`. The state borders show over the colored areas. Read the note under the map: its last two sentences say the lines are EIA-930's public interchange, no price is drawn, and the panel under the map carries the checked figures.
3. Hover the middle of the line between ERCOT and SPP: "From ... to ...", "N MW, the figure checked in the panel under the map", the hour and the refresh. Scroll to "ERCOT, the hour shown": the same tie, the same MW (signed from ERCOT's side there).
4. Hover a line that is not ERCOT's (for example in the West): no MW, the words say the panel holds the grid in view's ties only.
5. Move the hour slider back one hour and hover ERCOT's line again: no MW; the words name the hour the panel holds.
6. Hover CAISO's area: "Click to open its row on the Grid tool". Click it: `/grid?grid=caiso&view=network&shape=map`, the map again, CAISO's panel open, its lines now give their MW.
7. Click BPAT (Bonneville, the Northwest): its panel opens beside the map, as before.
8. Open `https://erw-flame.vercel.app/grid?view=network&shape=map` (the Lower 48): no line gives an MW; each of the seven ISO grids is a link.
9. Repeat 2 to 4 at 390 px wide.

## Checks

- `scripts/db_probe.py` from the main checkout: exit 0 at 20:16 UTC (open, 0.84 s).
- `scripts/buildlock.py acquire 1156-grid --wait-min 5`, four tries with `duty.py beat` before each, exit 1 each time (held by `s1126`): no build.
- `npm ci` in `site/`: exit 0. `npm run content`, `npx next typegen`: exit 0.
- `npx tsc --noEmit -p .` in `site/`: exit 0 (after the last edit).
- `node scripts/test-network-map.mjs` (new, 9 tests: the direction from a tie's sign, no edge without a figure, the panel's grid and hour, MW only for the panel's figures and equal to them for each of the seven grids, none for the Lower 48, another hour, a replay day or a story, the hover words, the click's slug, the carried moment, the hit segment): exit 0.
- `node scripts/test-grid-keys.mjs`: exit 0. `node scripts/test-gravity.mjs`: exit 0.
- `node --check scripts/check-network-map.mjs`: exit 0 (a browser check; not run, no server).
- `node scripts/check-methods.mjs`: exit 0, 553 of 553 figures named.
- `python -m unittest` on `tests.test_session1156` (new, 9 tests) and the 22 files that read these sources (`109`, `114_part2`, `1153`, `120_page`, `122`, `123`, `124`, `148`, `168_network`, `180`, `180b`, `193`, `237`, `241c`, `266`, `299`, `412`, `428`, `473`, `502`, `54`, `93`): exit 0, 369 tests, 24 skipped. No assertion changed.
- `scripts/test-network.mjs` (a browser test against a running site): not run, no server.

## The build

- **No build.** The build lock was held by chain 075's `s1126` (since 19:28 UTC) through four tries of five minutes each, 20:16 to 20:36 UTC, `duty.py beat` before each: given up, as the brief says. So no local server, no check-values run, no browser check, no screenshots (`docs/brand/review-1156/` not written). The lock was never held by this session, so there is nothing to release.

## The landing

- None in this session: the chain lands its sessions together once they are green (the brief). The branch is pushed: `wip/1156-grid`.

## To finish

- With a build (the lock free, `db_probe` 0): `npm run build` in `site/` (the anon key only), `next start -p 3156`; `MSYS_NO_PATHCONV=1 CHECK_VALUES_PAGES=/grid,/network node scripts/check-values.mjs http://localhost:3156` (expected: no key added or removed, every value matching); `node scripts/check-network-map.mjs http://localhost:3156` (its click check now follows ERCOT's link from the Lower 48 and clicks BPAT for a panel); `node scripts/test-network.mjs http://localhost:3156`; screenshots at 1280 and 390 of `/grid?grid=ercot&view=network&shape=map` and `/grid?grid=pjm&view=network&shape=map`, a line hovered, under `docs/brand/review-1156/`; stop the server by its PID and its port; release the lock.
- Land `wip/1156-grid` with the chain's combined landing. Expected differences: on the Network tab's Map shape only (drawn in the browser): the state outlines, the note's two new sentences, the hover cards, the seven ISO grids as links; the served HTML of `/grid` is unchanged except the Map shape's hint line, which is drawn in the browser too; no number.

## Decisions made without you

- **A grid clicked opens its row on the Network tab, in the Map shape** (`gridHref(slug, "network", { shape: "map" })`), not the Mix tab: the reader clicked on the map, so the map stays; the page's grid becomes the clicked one, its panel opens (its node is the grid's own) and the server panel under the map then holds its ties, so its lines gain their MW. The Mix tab is one click away in the tabs. The moment shown (the replay's day, a story, an hour) is carried as `net` and `t`; the open panel of another grid is not.
- **The grid in view, clicked, opens its panel as before** rather than reloading the same address; every balancing authority that is none of the eight opens its panel as before. On the Lower 48 all seven ISO grids are links.
- **A line's MW is written only where the panel holds it**, read strictly from item 5: a tie of the grid in view, in the panel's hour, in the live week. So the Lower 48 (whose panel holds net exports, not ties) shows no line's MW, and neither does another hour or a replay day. The direction and the window are written for every line: neither is a number of the panel's.
- **A zero flow stays undrawn**, as the network has always drawn it (no direction); the panel lists a zero tie. The node test counts it.
- **The ends of a line take no pointer** (the middle 60 percent does): every tie of a region begins at its point, so without this a click near the point would land on a line, not the region.
- **The lines' hover is not reachable by keyboard** (as the gravity shape's edges): about a hundred lines in the tab order would bury the regions; the same figures are in the panel under the map, which is.
- **The panel's grid and hour are read in the component** from the query the page keeps and from `complete.hour` (`mapPanelOf`), rather than a new prop, so the `page={{ keep, node, shape }}` line that two older tests pin is unchanged.
- **`check-network-map.mjs`'s click step was changed**, not removed: on the Lower 48, ERCOT is now a link, so the step checks the link, clicks BPAT for a panel, then follows ERCOT's link and compares ERCOT's panel word for word as before. Not run (no server).

## For Samuel's ruling

- Whether a line's MW may be written for every tie on the map (the browser's own figure, as the side panel already shows it), not only for the grid in view's ties in the panel's hour.

## Files

- New: `site/scripts/test-network-map.mjs`, `tests/test_session1156.py`, this report.
- Changed: `site/app/network/NetworkMap.tsx` (outlines, line hovers, links), `site/lib/networkMap.ts` (`edgesAt`, `edgeHeld`, `edgeTip`, `mapWindowWords`, `mapPanelOf`, `regionSlug`, `carryMoment`, `hitSegment`), `site/app/network/Network.tsx` (`linksAt` through `edgesAt`, the map's props, the hint and the note), `site/scripts/check-network-map.mjs` (the click step), `docs/methods/grid_network.md` (one paragraph in "The map (session 180)").
