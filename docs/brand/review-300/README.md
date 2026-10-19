# Session 300: the home page

Screenshots in the internal view at 1280 and 390 px, quantized to 32 colors, 19 October 2026, the page in its default
state. "Before" is production serving session 299 (the home page of session 53: three audiences of tool cards, the
price cards with sparklines, "Gas and oil", "Open now", "In review" and the status strip); "after" is the local build
of branch `wip/300-home-page`, the page of the owner's ruling of 18 October 2026 (mockup A, `docs/brand/home-mockups/`).
Taken with `runs/chain_oct19/capture300.mjs`, which also kept the page's checked numbers and visible text under
`runs/chain_oct19/s300/` (not in git).

| File | Address | What it shows |
|---|---|---|
| `before_home_*.png`, `after_home_*.png` | `/` | top to bottom: the one line; "Right now", the six grids' newest real-time interval with its hour and the three fuels with their dates, each a link to the board; today's chart with its sentence; the five groups, each with one line and one live number; the latest Digest, its first five stories; the source line |

What to look at, after:

1. The one line stands as the page's title under the crumb "Energy Research Warehouse".
2. The strip: nine figures in three columns, each with its table's key; MISO's interval is 4 October (its connector is paused), said in its line.
3. Today's chart is the Digest's chart of 14 October (the newest held: the daily run has not completed since 15 October), its picture at the left and its sentence at the right, as /research draws it.
4. The five groups read Economics, Grid, Infrastructure, Analysis, Games, each a link to its first page, with USD 81.40 per kW, ERCOT's demand, the US fleet, 11 findings and ERCOT's fleet.
5. At 390 px nothing scrolls sideways (page width 390 in a 390 window); the strip is one column, the groups one column.

The page carries 14 checked numbers (17 before: the four catalogue counts of the status strip are gone, and the findings count is new, computed by the value checker from the library's catalogue); its floor in `check-values-floor.json` stays 10.
