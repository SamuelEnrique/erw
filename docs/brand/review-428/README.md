# Session 428: shots before and after

Session 428 (chain 021's "session 420"), 21 October 2026. Before: the build of `wip/461-combined` at `2289156d` (worktree `erw-461`), served on port 3527. After: the build of `wip/428-performance`, served on port 3528. Both on localhost, the internal view open, viewport shots (`site/scripts/shot.mjs`).

| File | What to look at |
|---|---|
| `before/research_1280.png`, `after/research_1280.png` | the same page: the chart of the day now reserves its own shape (1200 by 880) before it arrives, so nothing under it moves when it does; the page drawn after load is the same |
| `before/research_390.png`, `after/research_390.png` | the same at 390 px |
| `before/network_1280.png`, `after/network_1280.png` | the same page: the 3D scene's frame is on the first screen at 1280 px, so its chunk is fetched at once, as before |
| `before/network_390.png`, `after/network_390.png` | the same first screen: the scene's frame is below it on a phone, so its 841 KB chunk is fetched only as the reader scrolls within 200 px of it |

No figure moved: check-values on the five pages touched read 1,526 of 1,526 values equal (`runs/chain_021/s428/values.out`).
