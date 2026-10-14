# The Grid tool's gravity shape at 1280 and 390 px

Energy Research Warehouse (ERW), session 266 (14 October 2026). Branch `wip/266-grid-pack`, not landed: for Samuel's review. The shape is the third toggle of the Network view of `/grid`, beside "Map" and "Network"; its rule is in `docs/methods/grid_network.md`, "The gravity shape (session 266)", and the review pack is `docs/reviews/packs/grid.md`.

| | 1280 px | 390 px |
|---|---|---|
| `/grid?grid=ercot&view=network&shape=gravity` (ERCOT's panel open, as the grid in view) | [gravity_1280.png](gravity_1280.png) | [gravity_390.png](gravity_390.png) |
| `/grid?grid=caiso&view=network&node=CISO&shape=gravity` (CAISO selected) | [gravity_caiso_selected_1280.png](gravity_caiso_selected_1280.png) | [gravity_caiso_selected_390.png](gravity_caiso_selected_390.png) |

Each is the top of the view, from a local production build (port 3266) with the internal view open (the page is in review). The hour drawn is 2026-10-12 03:00 UTC, the newest hour every reporting pair held at the hourly refresh of 2026-10-14 09:05 UTC.

- **What the pictures show.** The Lower 48 at the center; the seven ISO grids around it, each circle's area its EIA-930 net generation in the hour; CAISO (net imports 35.6 percent of its EIA-930 generation) and NYISO (18.0 percent) pulled in, PJM and SPP (small net exporters) just outside the dashed ring. Colors are the network's own (carbon intensity of generation, from the brand's tokens).
- **The phone.** At 390 px the frame is 358 by 358 px, the page is 390 px wide (no sideways scroll), and the panel is under the frame. In these pictures the labels are small on the phone (about 9 px high): the brand's chart rule (`.brand-a svg[role="img"] text`, 12 px in the drawing's own units) shrank them with the frame. The fix (the gravity SVG is a group of buttons, not an image, so its labels keep 26 units, about 15 px on a phone) is committed; pictures of it are not yet taken (the build mutex was held by the landing; see the session report).
- **Selected.** The selected grid is outlined in ink; the grids that are not its neighbours are dimmed; the panel shows the same figures as in the other two shapes (CAISO: "6,591 MW, 25.79 percent of its 25,557 MW demand").
- **Hover.** The card names the grid ("New York Independent System Operator"), as on the map and the 3D network.
- **Not drawn.** In a story or a replayed day the frame says the shape is drawn for the live week only.
