# The tour (`/tour`): review of 13 October 2026

Energy Research Warehouse (ERW), session 261. Taken end to end on a local production build of `origin/main` (`811328fe`), at 1280 and 390 px: the tour's page, then each of its five stops as the link opens it. Screens: `tour/before/` (12) and `tour/after/` (12).

## What it is, and for whom

- One page: five boxes, each a stop with a sentence on what the page is, a sentence on what to look at, the seconds it takes and a link. The network, one grid (ERCOT), the price board, an event study (Winter Storm Uri), and what a generator earns. "About three minutes in all" (the five add to 185 seconds).
- For whom: a first-time visitor of any kind. It is the one item of the four with no student, investor or operator in mind, and it reads that way: stops 1 and 2 are a student's, stops 3 and 5 an investor's.
- **What it teaches, in one line:** where the five most telling pages of the site are and one thing to look at on each. It teaches the site, not energy.

## Can a first-time user finish it without help?

- **The first stop: yes. The whole tour: only with the browser's Back button.** Where they get stuck:
  1. **No stop knows it is a stop.** Each link opens the ordinary page. None of the five has a link back to the tour or on to the next stop (0 on each page, counted). The tour's own words are "come back here for the next one": on a phone that is Back, or Games, then The tour, five times.
  2. **The tour does not remember where the reader was.** Back on `/tour`, nothing marks stop 1 as done.
  3. **What to look at was written for older pages** (below, bugs 1 to 3): a reader looked for a heading that was not there.
  4. The stops are long pages. Stop 1 opens on a grid picker, six tabs, a row of stories and a slider before the network; "press play" is one of two Play buttons ("Play" and "Play the year").
- For a visitor today the question does not arise: `/tour` and all five stops are in review (`site/lib/release.ts`), so the tour answers the "in review" page. Opened alone, it would list five greyed stops.

## Bugs, dead ends, numbers, layout

Numbers: the tour holds none of the warehouse's (by design, session 53). Its own counts were checked: five stops; 30 + 40 + 30 + 45 + 40 seconds = about three minutes; "seven ISO grids" (the grid page lists seven).

| # | What | Where | Fixed here |
|---|---|---|---|
| 1 | **Stop 2 named a heading the page does not have**: "Where the power comes from". The page a reader lands on (`/grid?grid=ercot`) has "The mix in that hour"; the old heading is on the grid's Mix view. The order was also the page's old one | `before/01-tour-desktop.png`, `before/03-stop-2-desktop.png` | yes |
| 2 | **Stop 5 said "the worst three months and the coverage line"**: the page has "The worst month" and "Debt coverage" | `before/06-stop-5-desktop.png` | yes |
| 3 | **Stop 3 said "the six hubs' real-time prices"**: the board holds a real-time price for five hubs of seven (MISO "paused while terms are reviewed", PJM "licensed source needed") | `before/04-stop-3-desktop.png` | yes |
| 4 | Stops 1 and 2 are old addresses: `/network` answers at `/grid?grid=us48&view=network` and `/grid/ercot` at `/grid?grid=ercot`, each by a redirect. They work; the stop's title "The network" lands on a page titled "The Lower 48 states" | `before/02-stop-1-desktop.png` | no: the address is also the release gate's key |
| 5 | No way back from a stop (above) | all five | no: needs a shared component |
| 6 | Stops 2 and 4 scroll sideways on a phone: the page is 500 px wide on a 390 px screen (`/grid?grid=ercot` and `/events/uri-2021`) | `before/03-stop-2-390.png`, `before/05-stop-4-390.png` | no: not the tour's files |
| 7 | On the local build the price board's ERCOT prices were dated 7 and 8 October where the other hubs' were 11 to 13 October. Seen on this build only; not checked on production | `before/04-stop-3-desktop.png` | no: not the tour's files |
| 8 | On the first local build stop 2 carried "Reads that failed: queue: ... statement timeout": a build that cached a database timeout (a known trap of local builds) | `before/03-stop-2-desktop.png` | no: the local build |

Not broken: all seven links answer (two by redirect), no page error, the tour's own page fits a phone with no sideways scroll, and every stop's page opens.

## Against the brand (`docs/brand.md`)

- Before: the old look (cream paper, the old text face), no `<Brand>` wrapper, while all five stops it opens wear the brand: the tour was the odd page of its own tour.
- After this session: the page draws inside `<Brand>`. White page, serif titles, links underlined. Nothing else was restyled.
- Still off: a stop's link is a line of running text; the brand's "one action of a form" in cardinal would suit "Open stop 1" better. A reading, not a ruling.

## Henry's review and Kelsey's conversation

- **Henry:** his ten questions are about the battery game. None touches the tour.
- **Kelsey's conversation of 5 October:** nothing of it is in the repository. Needs Samuel: what it asked of the tour, if anything. If the conversation was about a first visit, this is the item it bears on most.

## Done for real users

| # | What | Effort |
|---|---|---|
| 1 | Samuel's ruling on what the tour is (README, question 11): a list of links as now, or a guided path with a bar on each stop | S |
| 2 | If guided: a tour bar on each stop when it is opened from the tour ("Stop 2 of 5", what to look at, Next, Back to the tour), as one shared component read from `site/lib/tour.ts` | M |
| 3 | Each stop opens at the thing to look at (the network view playing, ERCOT chosen; the estimates' section of the Uri page), by an address that says so | M |
| 4 | The stops' words kept true by a check: a script that opens each stop and fails when a quoted heading is not on the page (bugs 1 to 3 would have been caught) | S |
| 5 | The five stops chosen again against today's pages and the three audiences (the battery page is the brand's reference and is not a stop) | S |
| 6 | Stops 1 and 2 at today's addresses, with their lines in `site/lib/release.ts` | S |
| 7 | The tour opens only when all five stops are live: its release line last | S |

## Fixes made on the branch

1. Stop 2 reads: Read "The mix in that hour", then "Right now: demand" and "Who runs this grid".
2. Stop 5 reads: Look at "The worst month" and "Debt coverage", then switch the asset to a battery.
3. Stop 3 reads: Compare the hubs' real-time prices with each other and with the day before.
4. The page draws inside `<Brand>` (its own commit: it can be dropped without the others).

No stop is added, removed or moved, and no address is changed.
