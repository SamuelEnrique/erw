# Session 8420 report: `/demand` for the whole country (chain 503, part C)

19 November 2026, samueloldlaptop (code role), unattended. Branch `wip/8420-demand-regions`, from `wip/8410-events-regions` at `bbefd6dd0` (part B), which is from `origin/main` at `2bca0266c`. Model spend USD 0: no model call. Nothing landed, no table written, `site/lib/release.ts` not touched: the page stays in review.

## What was built

- **A fourth view of `/demand`, "The whole country"** (`/demand?view=country`; `site/components/demand/Country.tsx`, mounted by `site/app/demand/page.tsx`; its tab is the fourth in the row). Any of EIA's thirteen regions of the lower 48 and any balancing authority that files Form EIA-930 can be chosen, two side by side: place A and place B, from two lists or from the tables at the foot. The address carries every choice: `?a=ten&b=ba-tva&days=2025&figure=summer&year=2024`.
  - **Demand by day** (the file's new `daily` series): for each place the day's highest hour and its average, on the site's time chart (it answers the mouse and turns into a table); a table of the days drawn (how many hold a whole day, the days of most and least demand, the highest hour and when, in the place's own time); the newest seven days, both places on one line a day. "Days drawn" chooses every day held or one year.
  - **Year by year**: the as-metered view's chart of the years for each place, and its table with one row a place and year (average, growth since 2019 and on the year before, peak, when, hours used, the year so far), with the hours left out.
  - **Where the growth is**: the as-metered view's chart by month and hour for each place, the largest and smallest cell, the change by month and by hour.
  - **With the weather taken out** (regions only, as the files hold it): the weather view's own chart with a row a place, its table by place and year, the choice of figure and year, and the check on years left out of the fit. A balancing authority reads "not held" there, with why.
  - **A region beside its grid** (Texas and ERCOT, New York and NYISO, New England and ISO-NE, the Mid-Atlantic and PJM): both averages year by year from the file's `alike` object, and the data machine's own sentence on why they differ as the hover of each difference. Both figures stand. A link draws the region beside the grid as two places.
  - **Every region and balancing authority**: the thirteen regions by name (the Southeast, Florida, the Carolinas, Tennessee, the Northwest and the Southwest marked "new to the site", each with a hover), and under a fold every balancing authority of the index (region, time zone, whether it files demand, active or retired, hours held). A name chooses the place.
- **The page's charts are reused, not written twice.** The three charts of the as-metered view stood inside the page file, which may export nothing; they are moved, unchanged, to `site/components/demand/Growth.tsx`, and both views draw them. The weather view's chart (`Weather.tsx`, `Explained`) is exported with three optional props. `site/lib/demandgrowth.ts` and `site/lib/demandweather.ts` read a place's `growth` and `weather` objects as they read the page's own files (types loosened, an optional list of codes; nothing they return for the seven grids moved).
- **The library** `site/lib/countrydemand.ts`: the types of `index.json` and the demand files, their reader (through part B's `readRegionFile`), the place an address names (letters and digits only, since the value becomes a file name), and the three sums the view computes from the daily series.
- **The server trace** (`site/next.config.ts`): `/demand` names `data/regions/index.json` and `data/regions/demand/**/*.json`, as the site does for every file read by a name built at request time. Without it the deployed page would not find the files.
- **The method note** `docs/methods/demand_growth.md`: a new section "The whole country (session 8420, 19 November 2026)".

## The files it waits for

- The data machine's `site/data/regions/index.json`, `demand/<region>.json` and `demand/ba/<code>.json` (contract `docs/state/page_files_regions.md`, steps B3 and B4 of chain 501) were **not on origin/main**: checked at the start and before the push (`git ls-tree -r origin/main --name-only site/data/regions`: nothing).
- Until a file is there its place reads "not built yet" and draws no figure; without the index the lists offer the thirteen regions and the table of regions stands with the contract's names. Nothing was waited on.
- The view was coded against the contract with fixtures in its form (`site/scripts/regions-fixture-demand.mjs`). Their values are made by a rule a test recomputes; they are not data, each says so, and the site's reader refuses a fixture in the site's own folder.
- When the files land: merge `origin/main` into the branch and run `node --import ./scripts/battery-awards-page-register.mjs scripts/test-demand-regions.mjs` in `site/`. Its last block reads the real files' form and prints, for each of the four pairs, whether the grid's average in `alike` is the as-metered view's and which way `difference_pct` is taken (notes, not failures).

## Add, never change: how it is held

- **The pin, written first from unchanged code** (commit `36bbcfee8`, before any change): `site/scripts/test-demand-pin.mjs` draws 50 addresses of the page with its own function (the page with nothing chosen; each of the eight areas under each of the three rankings; the weather view at each of four figures in each of five years; the consumption view on made-up rows; three addresses the page does not understand), cuts out the one thing added to them (the new tab's anchor, which carries `data-tab="country"`), and compares the rest, byte for byte, with the page as the base drew it (`site/scripts/pins/demand-page-8420.json`: a hash, the length and the count of checked figures of each). 101 of 101, before the change (it repeats) and after.
- **The view:** `site/scripts/test-demand-regions.mjs`, 90 of 90: the library against the fixture's rule; the view drawn with two regions, a region and an authority, an authority whose record begins after 2019, a generation-only authority, one place alone; the weather view; the four pairs; held; not built (no file, one file, no index, a file that is not JSON); a file that lacks a line of the contract (nothing is made up and nothing breaks); the whole page with and without files.
- **Python:** `tests/test_session8420_demand_regions.py` (17 tests) runs both and holds the source rules. With the older tests that name a changed module (`test_session152, 239, 97, 331, 281, 404, 412, 7018_demand_done, 7517_demand_growth_read, 7508_demand_growth, 468, 349, 3304_companies, 126, 129, 114_part2, 2204, 2877, 472, 538, 8410_events_regions`): the counts are in the hand-back. `site/scripts/test-demand-read.mjs` (the planner's read of chain 304): 24 of 24.
- **Types and lint:** `tsc` on the changed files (a scratch tsconfig, deleted after), exit 0; `eslint` on them, exit 0.
- **Not done here:** no site build (this machine's memory does not hold one), no browser, no `check-values`, no `check-routes`, no `check-demand`. No screenshot is claimed.

## What to review

The page needs the review cookie (every page is in review). Until the data machine's files land, each place reads "not built yet".

- `https://erw-flame.vercel.app/demand`: the row of tabs has a fourth, "The whole country"; everything else as before. The same on `https://erw-flame.vercel.app/demand?view=weather` and `https://erw-flame.vercel.app/demand?view=consumption`.
- `https://erw-flame.vercel.app/demand?view=country`: once the files are there: Tennessee as place A and the Carolinas as place B, each "new to the site"; two charts of demand by day; move the mouse over one; choose "2025" in "Days drawn": the charts and the table under them follow.
- `https://erw-flame.vercel.app/demand?view=country&a=tex&b=ba-erco`: Texas (EIA's region) beside ERCOT (the balancing authority). Scroll to "A region beside its grid": Texas and ERCOT year by year; rest the mouse on a figure of "Difference, percent": the data machine's sentence on why the two differ.
- `https://erw-flame.vercel.app/demand?view=country&a=se&b=fla`: the Southeast beside Florida. In "With the weather taken out" click "The summer peak", then a year: the chart and the highlighted rows follow.
- `https://erw-flame.vercel.app/demand?view=country&a=ba-tva&b=ten`: the Tennessee Valley Authority beside Tennessee. The weather table reads "not held" for the authority, with why on hover.
- At the foot of any of them: "Every region and balancing authority": click "Northwest": it takes place A. Open "The balancing authorities": click a name.

Browser reads wanted: rows 383 to 391 of `docs/state/browser_reads_wanted.md`. Landing: row 52 of `docs/state/landing_request_oldlaptop.md`.

## Needs the key

- Nothing.

## Decisions made without you

- **How the choice enters the page: a fourth view in the address** (`?view=country`), with its tab added after the three in `site/lib/tabs.ts` and `site/lib/demandpage.ts`. The shared tabs component is not changed. Before this session `?view=country`, like any view the page did not know, drew the page as metered; that one address now draws the new view.
- **Two older tests follow the addition**, as `tests/test_session239.py` did for the map's Queues tab in session 349: its list of `/demand`'s tabs gains `country`, and `tests/test_session152.py` expects four views and reads the three charts' `data-tip` in `Growth.tsx`, where they now stand. Nothing else in an older test changed, and none fails that passed on the base.
- **The three charts were moved out of the page file** so both views draw the same ones. The pin holds that the page's HTML did not move by a byte.
- **A place in the address**: a region by its code (`a=ten`), a balancing authority as `a=ba-tva` (a bare `a=tva` is read too). With the index held, a code EIA does not list falls back to the first place.
- **Hours are in the place's own time zone** (the file's `tz`), as the as-metered view writes them. Part B's section writes UTC because its files carry no zone.
- **A day's average is computed here**: the day's MWh over the hours used. The file gives MWh and the highest hour in MW; one chart in MW needs both in one unit. Said on hover.
- **The fit's years** of a region's weather view are read from a `train` line where the file gives one, else from the years its `holdout` is keyed by: the contract's weather object has no such line (a data request asks for it). With neither, the weather section reads "not held".
- **No decisions block and no downloads line on the new view.** A new line in the page's decisions block would change the block the pin holds and the note's list an older test compares word for word; each default is a hover inside the view. The tables the files read are named in the source line, from the files' own `tables`.
- **The rule for a held file** is part B's (`heldWhy`), written again as `heldWhyOf` in the view, because part B's function takes an event's file and part B's files are not edited.
- **`check-routes.mjs` is not extended** with the new address: its own note says a baseline that still draws an address another way would read it as new. It can be added once the view is on production.
- **`choices` of `site/lib/demandweather.ts` is as it was** (an older test holds its lines word for word); the view takes the figure and the year with the same two rules over its own places.

## For Samuel's ruling

- **The places drawn first: Tennessee and the Carolinas.** Two of the six new regions, and the two part B's page of Winter Storm Elliott draws first. No publisher's default stands behind it; the hover says so. Default taken: Tennessee and the Carolinas. Other choices: Texas beside ERCOT (it opens on the section that sets a region beside its grid); the Southeast beside Florida.
- **The days drawn: every day held.** About 3,000 days a line, two lines a place: the page carries about 12,000 points. Default taken: every day held, with one year as a choice. Other choice: open on the newest year.
- **The tab's name, "The whole country",** as part B's section is named, and its place as the fourth tab.
- **EIA's figures for New England, New York and the Midwest, and for ISO-NE, NYISO and MISO as balancing authorities, drawn in this view.** The files are EIA's Form EIA-930 and public by the contract, and `/demand` already draws the seven grids from EIA; the view reads each file's license line and the status file. Default taken: drawn. (The same question as part B's second, and entry 71 of the ranked list.)
- **A generation-only balancing authority can be chosen** and then reads "not held" with why (EIA lists it; it files no demand). Default taken: listed in both lists, marked "generation only". Other choice: left out of the lists and kept in the table only.
