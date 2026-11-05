# Review 502: each live view says what it holds and under which license

Session 502, 21 October 2026, on portable-laptop. Before: production (https://erw-flame.vercel.app), read in the internal view by `site/scripts/shot.mjs`. After: the local build of `wip/502-license-lines` (from `wip/429-combined`), when the database gate let a build run (see the report).

| File | Address | Width |
|---|---|---|
| `board_1280.png`, `board_390.png` | `/board` | 1280, 390 |
| `prices_1280.png`, `prices_390.png` | `/prices` | 1280, 390 |
| `prices_ercot_1280.png`, `prices_ercot_390.png` | `/prices?tab=ercot` | 1280, 390 |
| `grid_1280.png`, `grid_390.png` | `/grid` (the Lower 48, Mix) | 1280, 390 |

What to look at, before against after:

- **One new line under each title**, in the downloads line's small muted type: "Tables read, with their licenses:" then each table in mono with "public", "held: license needed" (a table held whole) or "held for <grids>: license needed" (a table held by grid). Its hover names the publishers whose sentence decides the hold.
- **The board**: the line sits below the board's header row, inside its frame (session 473's classes unchanged).
- **The Grid**: the line sits in the header under the lead, and lists the tables of the view on screen (Mix: 24). In the Ask panel, one more line says the panel reads the public tables of the site's live set and how a held table is answered.
- Nothing else moves: no number, no chart, no table.
