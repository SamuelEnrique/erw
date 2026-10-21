# Review 473: the brand on the Grid page and /board

Session 473, 21 October 2026, on portable-laptop. Before: production (https://erw-flame.vercel.app), read in the internal view by `site/scripts/shot.mjs`. After: the local build of `wip/473-brand`, once the database gate lets a build run (see the report's "To finish").

| File | Address | Width |
|---|---|---|
| `board_1280.png`, `board_390.png` | `/board` | 1280, 390 |
| `grid_1280.png`, `grid_390.png` | `/grid` (ERCOT, Now) | 1280, 390 |
| `grid_mix_1280.png`, `grid_mix_390.png` | `/grid?view=mix` | 1280, 390 |
| `grid_network_1280.png`, `grid_network_390.png` | `/grid?view=network` | 1280, 390 |
| `grid_clean_1280.png`, `grid_clean_390.png` | `/grid?view=clean` | 1280, 390 |

What to look at, before against after:

- **Notes, captions and table headers of the Grid's views** (the mix, the clean view, the storage, carbon, prices and projects parts, the network's ids): 11 px and 10 px became the brand's 12 px. Lines may wrap one word earlier; nothing else moves.
- **The source line's tier label** ("derived", "model"): square, sentence case, 12 px.
- **The fuel swatches** of the mix's legend and of the yesterday table: square.
- **The board's frequency label** beside a date ("hourly", "weekly"): square, as written.
- **The network's two hover cards** (the map and the gravity view): no shadow.
- The board's uppercase labels were already drawn in sentence case by `tokens.css`; removing the classes changes nothing on the screen.

Every number is the same: no checked-number key moved (`tests/test_session473.py`), and `check-values` on the build is the proof the landing runs.
