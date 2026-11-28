# Chain 780, the portable laptop: the All grids tab's new section, and the browser read of 28 November (note for Samuel)

Energy Research Warehouse (ERW). Kept current through the night; state at 13:35 UTC on 28 November 2026. Session 11600. The chain's first commit was at 10:37 UTC; it stops twelve hours after. Step by step: `docs/state/progress_c780.md`. The read: `docs/reviews/browser-read-2026-11-28.md`. The report: `archive/sessions/SESSION_11600_REPORT.md`.

## 1. The new section: "Where the next gigawatts can go"

**Where:** `https://erw-flame.vercel.app/cost-of-power?view=allgrids#regions`, on the All grids tab of "What a datacenter pays", under the hub table and above "Large-load rules by utility". The tab is in review, so you see it in the internal view.

**It is not on production yet.** Two things must land first, both the desktop's desk's: the section's code (landing row 68 of `docs/state/landing_request_portable.md`) and the desktop's regions files (its branch `wip/c760-regions`). Until the files land, production's tab draws the section's title and "not built yet" (hover: the files there are the contract's examples), and no table.

**What to click once both have landed** (the figures below are those of the desktop's files built 28 November 11:18 UTC; they move with each daily build):

- Open the address above. **You should see** "38 places side by side, a row a place and a column a count: 13 regions, 7 market operators and 18 balancing authorities", three lists ("Places listed", "A, side by side", "B, side by side"), a fold "Columns shown: 10 of 25", and a table of 38 rows and ten columns: one column from each of the ten subjects (price, congestion, how tight the grid runs, what waits to connect, large loads, carbon, neighbours, what is spare, the forecast, datacenters).
  - California's row: day-ahead price 30.27 USD/MWh, peak demand 61,700 MW, active requests 228,966 MW.
  - A blank cell is a count held for a license (Mid-Atlantic's price; every cell of the datacenter column). Put the mouse on it: "license needed" and why.
  - "not a market", "paused", "not held": a count not shown for another reason, in a word; the reason is on hover.
- **Put the mouse on a column's unit** ("USD/MWh" under "Day-ahead price, mean"). You should see what the count is, the period it covers and where it comes from, and, where the file gives the publisher's address, a link "Open its source".
- **Put the mouse (or a finger) on a small line beside a figure.** You should see its first and last month, its lowest and its highest month, and how many of the 24 months are held.
- **Press a column's name** ("Peak demand"). You should see the table sorted by it, largest first, the column moved to the front, and the line above the table say so and add "The order is the column's, not a ranking of places." Press again: smallest first. A place with no figure there is last either way. The back button undoes each press.
- **Open the fold "Columns shown"**, tick and untick, press "Show these columns". The table keeps your columns; the address carries them, so a link you copy opens the same table.
- **Press a place's name** ("ERCOT"). You should see a panel above the table with everything its file holds:
  - its hubs' prices, each mean with a small line of its last 24 months (ERCOT Hub Average, day-ahead: 34.57 USD/MWh);
  - how tight it runs: peak 91,075 MW, 8.90 percent above the year before, the hour of the peak, days with a notice, the planning reserve margin 11.40 percent for summer 2027;
  - what waits to connect: 408,002 MW in 1,796 active requests, 70.10 percent withdrawn historically, 3.80 years from request to operation, and the queue by fuel;
  - the large-load rules of its utilities, each utility's name opening its document, and the long words of a rule cut with the whole on hover;
  - carbon by hour of day as a small line with its lowest and highest hour; its partners; how well its demand is forecast (the operator's error 2.08 percent, the ERW forecast's 4.91);
  - "Datacenters already there": one blank, license needed.
  - "Close" puts the panel away.
- **Press A on one row and B on another** (or use the two lists). You should see "A and B, side by side": all 25 counts, A beside B.
- **Press "CSV of these 38 places and 10 columns".** A file of the rows and columns shown, with a Python and a Stata reader beside it.
- **On your phone:** the table scrolls sideways inside its own frame and its first column stays in place; the page itself does not scroll sideways; every mark opens on a tap.
- **Near the top of the tab,** under "Hubs and zones / ERCOT nodes": one line, "Under the table: where the next gigawatts can go, every region side by side", which jumps to the section.

**What is real and what is blank:**

- **Real:** every figure, from the desktop's files, each with its key into its file. Set beside the files in a build: 1,255 figures at each width, and 10,802 with every one of the 38 places opened; none differs. The site's own value check passes the tab on that build.
- **Blank, license needed:** PJM's, NYISO's and ISO-NE's prices; every datacenter count and the list of datacenters (the site holds both datacenter tables since 21 October). The contract first called those two tables public; the desktop corrected it within the hour (data request 584), and the section itself blanks a count of any table the site holds, whatever a file carries.
- **In a word, with the reason on hover:** MISO's prices ("paused"); a price for a place that is no market; carbon and curtailment where the warehouse holds none for the place.
- **A link from a hover to the publisher's report** is drawn where the file gives an address: the place's own operator's for a table of several publishers. The first files gave one address a source, the wrong document for most places; the desktop corrected it at 12:10 UTC (data request 586). Where a file gives none, the source is in words.
- **No score, no rank, no advice, no colour.** No map: the site has none of the regions to reuse.

**Seen:** seven builds, at 1280 px with a mouse and 390 px with a finger, on a copy of the desktop's branch files kept on this laptop and never committed; the keyboard alone from the top of the tab to its foot. An accessibility audit of the section found no violation.

## 2. A fault of the whole tab, found on the way and mended: the back button

- **What you would have met** (row CP2 of the read of 26 November): on the All grids tab, change the Profile list to "flexible", press the browser's back button: the address goes back and the page does not.
- **Why:** two parts of the tab wiped what the site's router keeps on the address the page was opened on.
- **Mended** on a branch of its own (landing row 69). Once it has landed: change the Profile, press back: the list and the sentence read "datacenter" again.

## 3. The browser read: what landed since 26 November

Read on production at 1280 and 390 px. In full: `docs/reviews/browser-read-2026-11-28.md`.

- **`/forecast`** (79 addresses, all 64 places): 158,232 figures agree with the files at each width. **"Tomorrow" is Friday 27 November, a day past:** the place files were not rebuilt with the daily run. The desktop found the cause and says tonight's run (from 17:00 UTC) writes them (data request 582). One place marked shown holds no hour (583).
- **`/equities`** (45 addresses): 22,111 figures agree. Eight small companies' newest revenue reads "0", because the table writes whole USD million.
- **`/impact`:** all 93 announced datacenters picked, each opening its document; coal, biopower and the trough clean at both widths. Where a document's figure is not taken, the page now says so and why.
- **The held grids' price files:** all 44 answer "not found" to a visitor.
- **The Grid tool on a phone is 506 px wide** on ten addresses, under a note that prints a failed run's raw error text; its newest whole day is 24 November (data request 587). The width is mended on a branch (landing row 70); the note's words are the desktop's.
- **Chart labels printed over each other** on three pages: the datacenter tracker's Grids view, the datacenter page's "Cost by year" on a phone, and the Clean view's heat map on a phone. Each is mended at its cause on a branch (landing rows 71 and 72). Pictures before and after are in the review's folder.
- **Every bar chart of one kind is shrunk to the screen on a phone,** its figures under 6 px (the datacenter tracker's Grids view, a company's page, the seller tab, the capital page, demand growth). The brand's rule for a phone stopped reaching it when the chart got its hover. Mended on a branch (landing row 73): 600 px wide in a frame that scrolls, its figures readable.
- **The site's own figure check, run whole:** 15,217 of 15,244 match; the rest were of the hour or are a floor to lower (`/policy`).
- **The first minute:** every one of the 54 addresses of the menu, the home page, the foot and the tour answers.

**Fixed here, each on its own branch with a test, each waiting for the desk to land it:** the tab's back button; the Grid tool's width on a phone; the years and the hours printed over each other; the bars' figures on each other; the bar chart's width on a phone. **Filed for the desktop:** data requests 582 to 589. **Filed for the old laptop's audits:** the heading "Tomorrow" over a past day, the small companies' "0", one doubled period on `/impact`. **Filed for the desk:** the floor of `/policy`.

## 4. What waits for you (each left as it is; nothing was decided for you)

- **The section's name.** Today: "Where the next gigawatts can go".
- **Its place on the tab.** Today: under the hub table, above the large-load rules; one line near the top leads to it.
- **The columns it opens on.** Today: the first of each of the ten subjects.
- **Figures worked out from held grids' prices, in two public files** (a problem edition's data file of 15 October, and a finding's file): the same question as line 14 of the read of 26 November.
- **What `/forecast` calls the day it draws when that day is not tomorrow.** Today: "Tomorrow".
- **A small company's revenue on `/equities`** when it is under half a million dollars. Today: "0".
- **Keyboard stops:** the new section adds about 320 to a tab that had more than 500; `/equities` has 662 before its foot.
- **A chart of twelve names or fewer on a phone, when two neighbouring names meet.** Today on production: printed over each other. On the branch: every second name written, the rest in the hover and the Table switch.
- **Five mends on pages this laptop does not own tonight** (the Grid tool's width, two charts' labels, the bars' figures, the bar chart's width on a phone). The chain says such a fault is a row for its owner; each is that, and each also has a branch and a landing row (70 to 73). Nothing of them is on main. Say "drop them" and the desk leaves the rows.
