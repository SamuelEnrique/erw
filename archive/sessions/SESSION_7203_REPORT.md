# Session 7203 report: the All grids tab read as the reader it is for (chain 302, goal 4)

Energy Research Warehouse (ERW). 16 November 2026, samueloldlaptop (code role), unattended. Branch `wip/7200-large-load`, stacked on session 7201's work (landing request row 15). Model spend: USD 0.00.

## At the top

- **Read from drawn HTML, not in a browser.** No site build on this machine on the day (2.0 GB of memory free at most, the chain asks 2.5 GB). The whole tab was drawn with the site's own components and files and read cell by cell with every hover; "Your load" was run through its own model on the same files. A fault only a browser shows is not in the list.
- **Four of the five cases have no row of their own.** Only ERCOT West does. Dominion's Virginia and AEP's Ohio fall into PJM's one row, which has no price (license). Arizona and Georgia are in no ISO and have no row at all.

## The read

- `docs/reviews/allgrids-read-2026-11-16.md`: 17 numbered rows.
  - 6 site faults, each fixed with a check on the drawn tab;
  - 8 data faults, each a row of `docs/state/data_requests_large_load.md` (rows 20 to 25) or already known;
  - 1 that only a license closes (PJM's prices; default: stays "license needed");
  - 2 for a ruling.

## What was fixed (`site/scripts/test-allgrids-read.mjs`, 25 checks)

- **The energy cell names its market in place:** "da 37.21 rt 35.35". "Your load" opens on real time, so one zone read 37.21 on the tab and 35.35 there with nothing in the cell to say why.
- **The all-in hover says what is not modelled:** the prices are the market's as they were; what a load of 1,000 MW would do to them is not in the figure.
- **The transmission hover of a Texas row names the wires utilities' own lines** for the same load (Oncor 8.58, CenterPoint 6.92, AEP Texas 8.16, Texas-New Mexico Power 7.06, USD per MWh) and says the figure drawn (7.83) is the Commission's rate for every wires utility together.
- **PJM's one row is no place.** Its hover no longer calls Allegheny County "a county this row's name places it in"; both cells open "22 large-load rules in PJM", and the panel counts them by state, each a link to the table filtered (Virginia 8, Ohio 4).
- **A and B say how B less A is rounded.** The arithmetic is unchanged.
- **A doubled word** in PJM's carbon hover.

## The two views agree

- "Your load" and the tab give the same flat price for ERCOT's West zone and West hub, day-ahead and real time, to the last digit (four figures, held by the test).
- "Your load" holds no PJM and nothing outside the seven grids, and says so in the same way.
- Not compared: "Your load"'s four-peak block and its three answers read the live set, which this worktree does not reach.

## What a lab's reader still cannot get from the tab, and why

- **A price anywhere in PJM,** where Virginia and Ohio are: PJM's terms close its prices to a non-member.
- **A row outside the seven grids** (Arizona, Georgia, the Carolinas, Tennessee, the Northwest): the tab was built on the hubs the page prices; the tables for those balancing authorities are in the warehouse and the rows are not built.
- **A utility's own rate for a large load:** the rules print what a customer must sign, not what a megawatt-hour costs; the registry of filed schedules holds rates for 6 utilities, none of the five cases'.
- **A load's own wait:** "Time to connect" is the median of generators that came online; the rules' timed steps are words; the measured large-load waits are held under a license.
- **Headroom at the site:** every headroom figure is the grid's.

## Tests

- `site/scripts/test-allgrids-read.mjs` (25), `tests/test_session7203_allgrids_read.py` (6).
- The touched test files after the fixes: 184 files, each in its own process, 2,086 tests. 182 passed as they were; 1 was this branch's own earlier tally, updated for PJM's row; 1 fails on main too (`tests/test_session705.py`).

## What to review (after the landing)

1. `https://erw-flame.vercel.app/cost-of-power?view=allgrids&mw=1000&a=ercot%3ALZ_WEST&b=ercot%3AHB_WEST`
   - Row "ERCOT LZ_WEST", Energy: "da 37.21 rt 35.35". All-in: hover it; the last sentence says the load's own effect on prices is not modelled.
   - Transmission and 4CP: hover 7.83; the hover ends with the four utilities' own lines.
   - "A and B, side by side": the note under the table says how B less A is rounded.
2. `https://erw-flame.vercel.app/cost-of-power?view=allgrids&llrow=pjm%3Agrid#large-load-rule`
   - "The large-load rules in PJM": 22 rules, and the states with their counts. Click VA: the table below shows PJM's 8 rules in Virginia.
   - In the table, row "PJM", Utility: the last line reads "22 large-load rules in PJM".

## Decisions made without you

- **B less A is not recomputed from the rounded figures.** The page's rule elsewhere is to compute exactly and round each figure; the note says so.
- **The energy cell gains two letters ("da").** Every row's cell changes by that; no figure and no check key moved.
- **PJM's utility figure is still drawn** (one county's utility). Dropping it is the builder's, on the data machine (request row 23); the words around it are now true.

## For Samuel's ruling

- **Which transmission figure a Texas row's all-in should count:** the Commission's rate for all wires utilities (as now, and as "Your load"'s four-peak block does), or the row's own utility's lines where the utility is known. Default: as now.
- **Evergy Kansas South and Evergy's Kansas rule** (carried from session 7201). Default: not matched.
