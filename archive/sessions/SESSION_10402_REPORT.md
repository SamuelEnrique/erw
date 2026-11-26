# Session 10402 report: chain 720 part D, energy equities (a group on `/board`, and `/equities`)

Energy Research Warehouse (ERW). 26 November 2026, the portable laptop's first window (code role), unattended. Branch `wip/c720-equities`, stacked on `wip/c720-forecast`, pushed.

## What was built

- **A group on the price board, "Energy equities".** The rows of window A's `site/data/equities/board.json` are turned into the board's own rows and added after the board's own groups (`withEquities`, `site/lib/equities.ts`). The group's table has the series, its latest value, its date, the change over a day, a week, a month, a year and the year to date, and the trend line the board's other rows have. A held row is the board's own blank ("licensed source needed" or "not held yet") with the file's reason on hover. A row with a value opens its series on `/equities`: by a click, or by the keyboard through the row's name.
- **`/equities`, "Energy equities", a new page, in review and in no menu.**
  - **The line.** A segment, an index or a company over a window (a week to every day held), with its latest value and its five changes. A segment has two lines, named "Every company counts the same" and "Larger companies count more". An energy price the files carry can be laid over the line on its own axis with its own unit; a monthly price keeps its own dates.
  - **Filed figures.** For a company: the newest period it filed (revenue, net income, capital spending, debt, shares outstanding, in USD million) beside the other company's, then every period behind a fold. Each period is a link to its filing on the SEC's site; each figure's hover gives the exact figure, its XBRL concept, the form and the day filed.
  - **Two side by side** (A and B): two segments, two companies, or one of each.
  - **Every company.** One table: name, ticker, exchange, segment, industry, the days of its shown prices, whether its filed figures are shown. It filters by segment, by words and by "share price shown", and sorts on a column's head.
  - **Segments and indices,** each a link that draws it, the segment's rule on hover.
  - **Downloads:** a series' days, a company's filed figures and the list of companies, each as a CSV with its provenance first and a reader in Python and in Stata.
- **Held and missing.** A share price the ERW may not show is a blank that says "license needed" with the file's reason on hover, and the company's filed figures are still drawn. An example file shows nothing, its names included.
- **No advice, no view.** Levels and plain changes as published. A test refuses the words of a recommendation in the page's code.

## What was checked

- `site/scripts/test-equities.mjs`: 93 of 93. The board's file with and without the group; the page drawn with no files, with the contract's example files at their real path, and with files of the contract's shape holding a test's made-up values.
- `tests/test_session10402_equities.py`: 11 passed. The 111 test files that name the board, the tour, the routes or the config: 1,228 passed, 53 skipped, 1 failed, `tests/test_session8430_supply_regions.py`, which fails on main on this laptop.
- **Five builds** with this branch's code (exit 0, each through `scripts/buildlock.py`, 2.1 to 2.8 GB free before each), the server stopped by its PID after each look.
- **As main stands** (the contract's example files): `/board` has its own 25 groups as they were and "Energy equities" last with one blank row; `/board/rows` carries that row with no figure; `/equities` is its title and one blank; 390 of 390 px at a phone's width.
- **With the test's fixture** (made-up values, on this machine only, a build never deployed): the group's rows with their latest value, moves and trend; a held row with its reason on hover; the filter; a row opens `/equities` by a click and by the keyboard and the back button returns; a row of the board's own still opens the workbench. `/equities` with a segment, two companies side by side with an oil price laid over, an index with a monthly price, the table filtered and sorted: no sideways scroll at 390 px, 49 stops of the keyboard each with a ring, the back button after three choices, the nine downloads.
- **The phone's width under a finger** (part E, taken early for both pages): the chart answers a tap; the folds, the sort heads, a company's name and the filter's box answer a finger. Found and mended: this page's small links (a column's head, a segment's count, "Draw it") were under 24 px. Left: a period's link in the filed table is 18 px tall in a row 30 px tall (the rule's spacing exception); the shared charts' Chart and Table switch is 22 px (a line for Samuel's ruling in session 10401's report).
- **Not checked, because the files do not exist yet:** the five cases on real figures and every figure beside the files. No real equities file is on main or on any branch (read 12:55 UTC).

## The standing step

- Row 3 of the second window's file (`wip/c750-conditions`) was seen in a build at 1280 and 390 px and marked requested: 44 notices under a heading that counts 44; 79 rows at 390 px with the page 390 px wide; each operator's line says its clock once.

## What the board keeps

- Every group, row, column and source it had, in its order. A test compares the board's file before and after the group is added.
- The lines of the board's code that older tests pin were restored exactly after the first cut broke five of them (the hold applied on the server, the column count, a row's name as a button, the rows' CSV).
- **Found: the board already carries a row named "Energy equities"** in its group "Capacity and equities", with the words "licensed source needed". It is the board builder's and it stays. Once the new group holds real rows the two will stand on one page. Filed for window A (data request 573) and for Samuel's ruling below.

## Decisions made without you

- **The group's table has fewer columns than the board's other groups** (no 7-day, 30-day or 12-month mean, no 30-day low to high, no one-year range): the contract's rows do not carry them, and the chain asks for the latest value, the changes and the trend. The other cells are asked of window A (data request 572) and are drawn by the board's own code if the rows come to carry them and the group's `lean` mark is dropped.
- **An equities row opens `/equities`, not the board's workbench.** The workbench reads the board's own series files, which these rows do not have.
- **With the contract's example files the group is one blank row** named "Segments and indices", not the examples' three rows: one of them is named "Example index".
- **The table of every company shows no price and no change,** because the list does not hold them and opening one file a company for one table is too heavy. Asked of window A (data request 571).
- **Statement lines are written in USD million** (shares in millions), the exact figure on hover.
- **Only an address of `https://www.sec.gov/` is made a link** for a filing.
- **A commit of this chain that touches `site/app/board/page.tsx` does not begin "Session 104":** an older test holds that the file's last commit does not say session 104's name, which every session name of this chain begins with. The commit is named "Chain 720 part D (s10402)".

## For Samuel's ruling

- **The board's older row "Energy equities: licensed source needed"** (in "Capacity and equities") beside the new group of the same name. Default taken: both are left as they are.
- **Where `/equities` sits in the menu and what it is called.** Default taken: in no menu; its title is "Energy equities".
- **Where the group sits on the board.** Default taken: last, after the board's own groups.

## Needs the key

- Nothing. No model was called.

## What to review

- Nothing to click on production yet: the branch waits for its landing (row 55 of `docs/state/landing_request_portable.md`) and for window A's files. After both: `https://erw-flame.vercel.app/board#equities` (the group at the board's foot; press a row), then `https://erw-flame.vercel.app/equities` (choose a company under "A", a second under "B", an energy price under "Energy price laid over").
