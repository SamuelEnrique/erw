# The tour (`/tour`): review of 14 October 2026

Energy Research Warehouse (ERW), session 279. Taken end to end on a local production build of `wip/279-games` (session 261's fixes merged with `origin/main` at `eb64c7a5`), at 1280 and 390 px: the tour's page, then each of its five stops as the link opens it. Screens: `tour/before/` (12) and `tour/after/` (12). Session 261's review of 13 October is the base.

## What it is, and for whom

- One page of five stops, each with what the page is, what to look at, the seconds it takes and a link: the network, one grid (ERCOT), the price board, Winter Storm Uri, what a generator earns. "About three minutes in all" (30 + 40 + 30 + 45 + 40 = 185 seconds).
- For whom: a first visit of any kind. Stops 1 and 2 suit a student, 3 and 5 an investor.
- **What it teaches, in one line:** where five of the most telling pages are and one thing to look at on each. It teaches the site, not energy.

## Can a first-time user finish it without help?

- **The first stop: yes. The whole tour: only with the browser's Back button.** No stop links back to the tour or on to the next (0 links to `/tour` inside each of the five pages, counted again today), and the tour does not mark a stop as done.
- Stop 1's title "The network" lands on a page titled "The Lower 48 states" (`/network` answers at `/grid?view=network`).
- The stops' words, corrected by session 261, still match today's pages: stop 2's "The mix in that hour", stop 5's "The worst month" and "Debt coverage", stop 3's hubs without a count.

## Bugs, dead ends, numbers, layout

Numbers: the tour holds none of the warehouse's by design; its own counts hold (five stops, about three minutes).

| # | What | Where | Status |
|---|---|---|---|
| 1 | Stop 2 named a heading the page does not have | | fixed by 261, holds |
| 2 | Stop 5 named "the worst three months and the coverage line" | | fixed by 261, holds |
| 3 | Stop 3 counted six hubs | | fixed by 261, holds |
| 4 | Stops 1 and 2 are old addresses, answered by redirect | `after/02-stop-1-desktop.png` | open: the address is also the release gate's key |
| 5 | No way back from a stop | all five | open: a ruling (README question 11) |
| 6 | **Stops 2 and 4 scroll sideways on a phone**: 500 px wide on a 390 px screen (`/grid?grid=ercot` and `/events/uri-2021`) | `after/03-stop-2-390.png`, `after/05-stop-4-390.png` | open: not the tour's files; for the Grid and Analysis finish sessions |
| 7 | The site menu's closed dropdown measures 418 px at 390 px | every 390 px screen | not the tab's files |

Not broken: all seven links answer (two by redirect), no page error, the tour's own page fits a phone.

## Against the brand (`docs/brand.md`)

Inside `<Brand>` since session 261's commit `46fd7338` (on this branch, not on main): white page, serif titles, links underlined. A stop's link is a line of running text where the brand's one cardinal action would read better; a reading, not a ruling.

## Henry's review

His ten questions are about the battery game; none touches the tour. Kelsey's conversation of 5 October: still nothing in the repository; if it was about a first visit, this is the item it bears on most.

## Done for real users

| # | What | Effort |
|---|---|---|
| 1 | Samuel's ruling on what the tour is (question 11) | S |
| 2 | If guided: a tour bar on each stop opened from the tour ("Stop 2 of 5", what to look at, Next, Back), one shared component read from `site/lib/tour.ts` | M |
| 3 | Each stop opens at the thing to look at, by an address that says so | M |
| 4 | A check that opens each stop and fails when a quoted heading is gone | S |
| 5 | The five stops chosen again against today's pages | S |
| 6 | Stops 1 and 2 at today's addresses | S |
| 7 | The tour opens last, when all five stops are live | S |

## Fixes made on the branch in this session

None: the words session 261 corrected still match, and nothing else is plainly broken in the tour's own files.
