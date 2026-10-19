# Session 299: the Grid tool as one page of four tabs

Screenshots in the internal view at 1280 and 390 px, quantized to 32 colors, 19 October 2026. "Before" is production
serving session 298 (the six views of session 237: the four here, with `view=now` for the Mix tab's new blocks and
`view=exchange` for the Gravity tab's); "after" is the local build of branch `wip/299-grid-one-page`. Taken with
`runs/chain_oct19/capture299.mjs`, which also kept each page's checked numbers and visible text under
`runs/chain_oct19/s299/` (not in git).

| File | Address (after) | What it shows |
|---|---|---|
| `*_network_*.png` | `/grid?grid=us48&view=network` | the Network tab: the picker once, the four tabs, the network of 70 balancing authorities, the lag line that now gives the hour's age twice, the decisions block, the Ask panel on the right (under the page at 390) |
| `*_mix_*.png` | `/grid?grid=us48` | the Mix tab, the opening tab: the Now view's blocks (the latest hour) above the Mix view's, every number as before |
| `*_clean_*.png` | `/grid?grid=us48&view=clean` | the Clean tab, as it was, with the panel beside it |
| `*_gravity_*.png` | `/grid?grid=us48&view=gravity&shape=gravity` | the Gravity tab: the gravity shape with its note (EIA-930 one source, CAISO's break, the square-root pull, the 63 undrawn), the Exchange view's blocks under it |
| `*_ercot_network_*.png` | `/grid?grid=ercot&view=network` | ERCOT on the Network tab (before: the same address) |
| `*_ercot_ask_*.png` | `/grid?grid=ercot&ask=1` | ERCOT with the Ask panel open: Ask ERCOT's profile in the panel beside the Mix tab (before: the Ask view alone at `view=ask`) |

What to look at, after:

1. The tabs read Network, Mix, Clean, Gravity; nothing above them but the picker and the lead; the "Ask" heading sits at the right at 1280 and after the tab's blocks at 390.
2. The Mix tab opens with "The mix in that hour" and the grid's latest hour, then the Mix view's own blocks: 36 checked numbers on the Lower 48 (27 on the old Now view and 9 more from the Mix view, none changed).
3. The Gravity tab's note under the shape, and "The seven grids, that hour" under it. The seven circles are dashed outlines in these shots: EIA-930's generation for the hour shown is not in the live set this week (production draws them the same way; the replication check against the committed file fails on production too, on its stale hour).
4. The line under the network: "began 50 hours before this week's latest hourly refresh (...), and 54 hours before this page was drawn (...)".
5. At 390 px nothing scrolls sideways (page width 390 in a 390 window, every address).

Every checked number common to production and the local build is the same (1,163 keys before, 1,207 after: the 44 new ones are the two Gravity addresses added to the value checker and the Now blocks now drawn on the Mix tab; no key gone, no common value changed).
