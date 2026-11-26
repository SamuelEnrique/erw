# Note of chain 750 (the portable laptop's second window, 26 November 2026): the browser read

Energy Research Warehouse (ERW). The chain: `queue/done/750-night-26-november-portable-window2-browser-read.md`. Progress: `docs/state/progress_c750.md`. The review: `docs/reviews/browser-read-2026-11-26.md`. Model spend USD 0. Kept current while the chain runs; this is its state at 12:25 UTC on 26 November.

## Pages read, and what was found

- **Read on production in a real browser, at 1280 px with a mouse and 390 px with a finger:** the five rows that waited for a browser; `/conditions` and `/congestion` in full (five readers' cases each, every table cell and marked figure against the page files, everything that answers to the hand); the thirteen regions of the Grid tool; the four accessibility fixes of 20 November; chain 620's ten fixes; the problem edition of 21 November; a sweep of 146 addresses and of the method pages at a phone's width.
- **Figures set beside their files:** about 120,000 (15,553 on `/conditions`, 8,941 on `/congestion`, 94,435 on the regions' Mix tabs, 838 words and figures of the problem edition). Two disagreed, both the same fault (the alerts list, below).
- **Faults, by owning window:**
  - no window's page tonight: 3 found, 3 fixed on branches with tests (to be seen in a build, then landed by window A's desk);
  - the desktop's second window (B): 1 filed (two of its commits read landed and are not on main);
  - window A (the data machine): 1 known to it already (the page files of 21 to 25 November), no request filed;
  - windows C, E and the old laptop: none yet (their pages of tonight had not landed when this was written).

## The five worst things found

1. **`/grid?grid=caiso` scrolls sideways on a phone** (539 of 390 px) since 21 November: the accessibility fix made that day without a browser put 226 hidden labels in the reliability table, and the ones past the table's frame widen the page. Fixed (`wip/c750-grid-reliability`), seen in a build by the first window, requested.
2. **`/conditions` dropped alerts without saying so:** 40 rows under a heading that counts 44 (CAISO's September 2022 heat wave lost its last day) and 40 of 79 (August 2020). Fixed (`wip/c750-conditions`), to be seen.
3. **Two fixes marked landed on 21 November are not on main** (`/curtailment/where-when`'s table heading, `/events/covid-2020` at a phone's width); both faults are still on production. Seen in a build by the first window, requested.
4. **Every page that draws the data machine's page files shows 18 to 20 November:** its daily commits of 21 to 25 November sit on `wip/red-dm-*` branches. Window A repairs it tonight (chain 701, part C).
5. **A reason given on hover cannot be opened by a finger:** why a strip or a cell is blank, on `/conditions`, `/congestion`, `/demand`, `/supply`, `/events`. For Samuel's ruling.

## Where the pictures are

- `https://github.com/SamuelEnrique/erw/tree/main/docs/reviews/browser-read-2026-11-26` (a folder a page: `conditions`, `congestion`, `grid-regions`, `grid-caiso-reliability`, `policy-week`, `severance`, `problem-edition`, `events-covid-2020`, `chain-620-fixes-on-production`, `part-a`). Each picture has its line in the review.

## What waits for Samuel, with the page left as it is

In plain words; the same six lines stand at the foot of the review.

1. Should the reason a figure is blank open on a tap, as the "i" marks do? Today only a mouse can read it.
2. `/congestion` prints "1080.08 USD/MWh" beside "330,132": a thousands comma in one column and none in the other. The gate's own check holds it that way.
3. `/congestion` calls CAISO's base case "contingency Base Case".
4. `/supply`: a year with a month left out makes the mix table half again as wide inside its frame on a phone.
5. The tour's Digest stop still quotes two headings the Digest page does not show.
6. `/conditions`: on the branch every alert is listed (79 rows for August 2020). If the list should stop at 40, the page should say so.

## What waits for a window

- **Window A's desk:** rows 1 and 2 of `docs/state/landing_request_portable_w2.md` are requested; row 3 waits for the first window's next build.
- **This window:** tonight's pages as they land (`/forecast`, `/equities` and the board's new group, `/impact` with Datacenter, the All grids tab), then the five sellable tools and the first minute.
