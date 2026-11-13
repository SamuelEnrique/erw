# The Grid tool (`/grid`, with `/network`, `/mix` and `/ask`): faults of 13 November 2026

Energy Research Warehouse (ERW). Chain 233, window P1 of the portable laptop, session 5005. Read on the local production builds of sessions 5001 and 5004 in the internal view at 1280 and 390, and its done line for roadmap item 2 read against the method note, the replication and the cross-check table. The Ask engine and its evaluation are window P3's and were not read. States as in `battery-faults-2026-11-13.md`.

| # | Where | Fault | Fix | State |
|---:|---|---|---|---|
| 1 | `replication/grid/replicate.py` | A reader's run with no argument stops (exit 2): "the snapshot given was built 2026-11-12T21:46:53Z; page_figures.json is of the snapshot built 2026-11-05T23:09:35Z". The daily run rewrites `site/data/grid_network.json` every day, and nothing rewrites the replication's figures with it, so the package fails the day after it is written | `figures_of_the_page.py` keeps the snapshot it read beside the figures (`replication/grid/snapshot.json`, the one of 5 November restored from `e2794ff0`), and `replicate.py` reads it by default: the network group meets 85 of 85 computed figures; the note says so; `tests/test_session5005.py` | fixed (session 5005) |
| 2 | `page_figures.json`, the carbon and Ask groups | Not set beside a newer snapshot or newer tables since 5 November | Not this laptop's: it holds no copy of the tables they read (`carbon_intensity_monthly`, `eia930_all_generation`, ...), and restoring them is a data write. The data machine runs `python replication/grid/figures_of_the_page.py` and commits the four files and `snapshot.json` | data machine |
| 3 | The page's decisions block | Its five lines are written in the page, not in `site/lib/decisions.ts`, so no test holds them to the note as the economics pages' are | Not a fault: the five lines are the owner's rulings of 18 October word for word, held by `tests/test_session299.py`; the note's "Decisions" section holds the 25 assumptions | not a fault |

## The read

| View | 1280: width, keys, errors | 390: width, keys, errors |
|---|---|---|
| `/grid` (the Lower 48) | 1265, 38, 0 | 390, 38, 0 |
| `/grid?view=mix` | 1265, 38, 0 | 390, 38, 0 |
| `/grid?view=clean` | 1265, 46, 0 | 390, 46, 0 |
| `/grid?view=gravity` | 1265, 38, 0 | 390, 38, 0 |
| `/network` (resolves to `/grid?grid=us48&view=network`) | 1265, 15, 0 | 390, 15, 0 |
| `/ask` (resolves to `/grid?grid=us48&ask=1`) | 1265, 38, 0 | 390, 38, 0 |

## One page

Network, energy mix and Ask are one page since session 299: `/grid` draws four tabs (Network, Mix, Clean, Gravity) with the grid picked once above them and Ask as a panel beside every tab; `/network`, `/mix` and `/ask` resolve into it (read above). Nothing was composed further here: the page's design waits for the brand's mockups (roadmap item 3), and the Ask engine is window P3's.

## The done line after session 5005

| Item | State |
|---|---|
| Method note | `grid_network.md` with its sign-off block (session 1743), ready for signature; unsigned |
| Replication | `replication/grid/replicate.py` runs with no argument: 85 of 85 network figures met; the carbon and Ask groups where the tables are held (row 2); the do-files never run |
| Cross-check table | `docs/methods/crosschecks/grid.md` |
| Decisions block | the page's rulings block and the note's 25 assumptions (`replication/grid/assumptions.json`) |
| One page | yes, since session 299 |

## The wider read (session 5009)

Session 5004's build, internal view, 1280 and 390: each of the eight grids (ERCOT, CAISO, PJM, MISO, NYISO, ISO-NE, SPP, the Lower 48) on each of the four tabs, 64 views, and Research's week `/research/2026-W45` at both widths. No console error, no broken text, nothing scrolls sideways at 390. No new fault.
