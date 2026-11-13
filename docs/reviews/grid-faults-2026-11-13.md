# The Grid tool (`/grid`, with `/network`, `/mix` and `/ask`): faults of 13 November 2026

Energy Research Warehouse (ERW). Chain 233, window P1 of the portable laptop, session 5005. Read on the local production builds of sessions 5001 and 5004 in the internal view at 1280 and 390, and its done line for roadmap item 2 read against the method note, the replication and the cross-check table. The Ask engine and its evaluation are window P3's and were not read. States as in `battery-faults-2026-11-13.md`.

| # | Where | Fault | Fix | State |
|---:|---|---|---|---|
| 1 | `replication/grid/replicate.py` | A reader's run with no argument stops (exit 2): "the snapshot given was built 2026-11-12T21:46:53Z; page_figures.json is of the snapshot built 2026-11-05T23:09:35Z". The daily run rewrites `site/data/grid_network.json` every day, and nothing rewrites the replication's figures with it, so the package fails the day after it is written | `figures_of_the_page.py` keeps the snapshot it read beside the figures (`replication/grid/snapshot.json`, the one of 5 November restored from `e2794ff0`), and `replicate.py` reads it by default: the network group meets 85 of 85 computed figures; the note says so; `tests/test_session5005.py` | fixed (session 5005) |
| 2 | `page_figures.json`, the carbon and Ask groups | Not set beside a newer snapshot or newer tables since 5 November | Not this laptop's: it holds no copy of the tables they read (`carbon_intensity_monthly`, `eia930_all_generation`, ...), and restoring them is a data write. The data machine runs `python replication/grid/figures_of_the_page.py` and commits the four files and `snapshot.json` | data machine |
| 3 | The page's decisions block | Its five lines are written in the page, not in `site/lib/decisions.ts`, so no test holds them to the note as the economics pages' are | Not a fault: the five lines are the owner's rulings of 18 October word for word, held by `tests/test_session299.py`; the note's "Decisions" section holds the 25 assumptions | not a fault |
| 4 | MISO's grid page: the Mix sentence, the hour cards and the conditions (found in session 5403, on production at 1280 and 390) | "In the hour starting Nov 12, 6:00 PM GMT-5" where every other grid's page names its zone (EST, CST, PST): MISO keeps Eastern Standard Time all year, the zone `Etc/GMT+5`, which the browser names "GMT-5" | `zoneWords` in `site/lib/gridtool.ts` names it "EST" in every season and leaves every other zone as the browser names it; `components/grid/NowView.tsx`, `YourGrid.tsx` and `Conditions.tsx` use it; `tests/test_session5403.py` | fixed (session 5403) |
| 5 | `site/scripts/a11y-axe.mjs`, the accessibility read (found in session 5423, reading the five's default pages at 390 on production) | It reported `scrollable-region-focusable` (serious, 2 elements) on `/grid` and MISO's view: the monthly mix table's scrolling box. Not the page's: the same box carries `tabindex="0"`, `role="region"` and its name four seconds after the load, and axe run after a wait finds nothing. The script ran axe straight after the load, before `components/ScrollRegions.tsx` (150 ms after it mounts) had marked the box | The script waits after each load before axe runs (`A11Y_WAIT_MS`, default 2000); run again: 0 rules broken on `/grid`, MISO's view and `/cost-of-power` at 390; `tests/test_session5423.py` | fixed (session 5423) |

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

## The read as one page (session 5076, chain 243)

Read on production (`https://erw-flame.vercel.app`, main as deployed on 13 November 2026 between 19:59 and 20:12 UTC) in the internal view, the token posted as the site's form does, at 1280 by 900 and at 390 by 844 as a phone, with the site's own browser helper (`site/scripts/browser.mjs`): each page's end address, its scroll width against the window, the exceptions it threw, the words that betray a broken value (NaN, undefined, [object Object], Infinity), its text and a picture of the window and of the whole page (four looked at: the Grid's Ask flag and Network at 1280, Gravity at 390, the battery's CAISO view at 390; the others read by their measures and text). Not on a local build: the build of `wip/5072-analysis` was stopped by Claude Code when the laptop ran low on memory (three windows on 16 GB), and the stack changes no page's code.

- **The one page.** In the internal view `/ask` and `/ask?q=...` answer 307 to `/grid?grid=us48&ask=1` (the question carried); `/network`, `/network?shape=gravity`, `/network?view=uri_2021&grid=ERCO`, `/mix`, `/mix?view=clean`, `/mix?view=stress` and `/emissions` answer 308 to the view of `/grid` that holds them, each word carried. As a visitor every address is the in-review page.
- **Nine views at both widths:** the Lower 48 (the opening view, Network, Gravity by `view=gravity` and by `shape=gravity`, Clean, Mix, the Ask flag) and ERCOT (the opening view and Clean): no sideways scroll, no exception, no broken word. The Ask panel stands beside every view (at 390, below it).
- **No new fault.** An address tried here, `/network?view=gravity`, opens the Network view: no page ever wrote it (the network's views were live, evening, uri_2021, east_heat_2025 and day; the gravity shape was `shape=gravity`, which opens Gravity), so it is not a fault.
