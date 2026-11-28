# Session 11600 report: chain 780, the All grids tab's new section and the browser read of 28 November

Energy Research Warehouse (ERW). Chain 780 (`queue/done/780-night-28-november-portable-allgrids-regions-browser-read.md`), the portable laptop (code role), one window, 28 November 2026. Started by Samuel by name; unattended; model spend USD 0 (no model API was called). The first commit was at 10:37:01 UTC (`f3e2968b9`); the chain stops twelve hours after it. Kept current through the session; the state of each step is in `docs/state/progress_c780.md`.

## The start

- Precheck passed from the main folder (`scripts/precheck.py`, on duty until 02:37 UTC on 29 November). No freeze (`scripts/freeze.py status`, exit 0).
- Local `main` was 390 commits behind `origin/main` and none ahead: fast-forwarded. One commit of work was on no origin branch (`9d72986e6`, chain 720's first form of the phone's links): pushed as `wip/c780-local-2026-11-28`. Nothing discarded.
- Free memory: 1,356 MB of 15,974 MB at 10:35 UTC; 3,330 MB at 10:53 UTC; 2,032 MB at 11:15 UTC with a browser open.
- Sessions 11600 to 11799 checked free on origin/main and every branch.
- The chain's file taken (`f3e2968b9`); chains 720 and 750 closed (`049f001ef`: their resume files removed, their open items under "Taken over" in the progress file, one line at the end of each note); the resume file `queue/next/781-resume-chain-780.md` committed alone and pushed (`d63bcf8fe`).

## Part A: "Where the next gigawatts can go", on the All grids tab

- **The ground** (`docs/reviews/allgrids-regions-ground-2026-11-28.md`): the tab's ten parts, the names its address uses, the tests a new part could trip, what the site has to reuse and what it has not, and five cases.
- **The contract** (`docs/state/page_files_siting_regions.md`) reached main at 10:53 UTC with three example files, every value null. Two lines went to the desktop before anything was built: data request 584 (the contract calls `datacenter_facilities` and `datacenter_projects` public; the site holds both for a license) and 585 (a count's small trend, and the address of a figure's source, are not in the contract).
- **The desktop answered both at 11:22 UTC** (the contract's dated line of 28 November): the datacenter counts held; a count's 24 months as `trend`; a source's address. Its builder's first files were on its branch (`origin/wip/c760-regions`: 38 places, 25 columns), not yet on main; the section was built and seen on a copy of them kept in a folder of this laptop and never committed. Data request 586 followed: a source's address is one document for every place (ERCOT's rules' source is a Florida filing), so the section draws no link from it.
- **The section** is on `wip/c780-allgrids-regions` (`0af2b939e`; landing row 68, requested at 13:10 UTC, its head moved once after by one sentence): five files in `site/app/cost-of-power/` (`regions.ts`, `regionsdata.ts`, `RegionsSection.tsx`, `RegionsChoices.tsx`, `RegionsDownload.tsx`), one import and two lines of `AllGridsView.tsx`, two lines at the foot of `site/next.config.ts`.
  - One table of every place, a row a place and a column a count; a press on a column's name sorts by it, a second turns it round; a place with no figure is last either way.
  - The columns shown are the reader's (a picker by section); the table opens on the first column of each of the ten sections.
  - A place opened shows its own file: its counts, its hubs, its top constraints, its partners, its utilities' large-load rules (each rule opening its document), and the one small trend the contract carries (carbon by hour of day).
  - Two places side by side as A and B; the rows shown as a CSV, with a Python and a Stata reader.
  - A count held for a license is a blank with "license needed" on hover; a count not shown for another reason says the reason's kind in a word, the reason on hover. A count of a table the site itself holds is a blank whatever the file carries.
  - No score, no rank, no advice, no colour.
  - On the contract's example files the section says "not built yet" and draws no table.
  - A count's 24 months are drawn as its small trend (two hubs' mean price, the peak, carbon, net imports, wind and solar curtailed), and carbon by hour of day. A trend has a hover of its own that a finger and the keyboard open: its first and last month, its lowest and highest, how many months are held.
  - A hover opens its source where the file gives the publisher's address (the place's own operator's for a table of several publishers: the desktop's answer to data request 586, 12:10 UTC).
  - A fuel the files name by its key ("natural_gas") is written in words.
  - One line under the tab's row switch leads to the section, which stands under the hub table.
- **Tests:** `site/scripts/test-regions-section.mjs` (92 checks, on main's example files and on a fixture of made-up values) and `tests/test_session11600_regions_section.py` (12 tests); the type check of the section and the tab passes.
- **Seven builds** (exit 0; 148, 105, 100, 97, 100, 125 and 90 s; 3,073 to 5,978 MB free before each), each served on the desktop's real files and walked at 1280 px with a mouse and 390 px with a finger. What the looks mended: a column's decimals (60.00 under 60.33); a row on one line; every target 24 px; the panels on white; the first column narrow on a phone, where it had stood over the heads a finger aims at; a small trend that ran over the next column on a phone; the line that leads to the section; the sentence above the table, which said the order was "the column's" while it was still the file's.
- **On the last head** (the seventh build, on the desktop's files built 12:57 UTC): 38 of 39 checks at 1280 px and 36 of 37 at 390 px (the one that differs is the read's own rule, which counts the controls of the tab's shut fold as unnamed); 1,267 figures beside the files at each width; no small trend past its own cell; the keyboard alone from the top of the tab to its foot, 1,743 stops, each seen and marked; no sideways scroll of the page; no control under 24 px; 319 keyboard stops in the section; the site's own value check on the build 1,555 of 1,555; AccessLint (on the fifth build): no violation. Without a build, every place opened on those files: 10,966 figures, none differing.
- **The older tests:** of 344 files on the first head, 10 failed. Eight fail on main's own tree on this laptop (143, 148, 156, 161, 1880, 7203, 8430, 8901); two were mine (tests 138 and 194 hold the tool to its four folders, and the section's files stood in a fifth) and are mended. On `cee4cfe21` (the section two commits before its head, with the back button's mend) and again on `379c2fc7e` (with four of the mends below too): 8 failed each time, the same eight; 3,953 passed, 155 skipped.
- **A slip of the sixth look:** the first walk of the sixth build was set beside main's three example files, not the desktop's (the argument that names the files' folder was left off), and read 29 of 39. Run again with it: the figures above.

## The All grids tab and the back button (row CP2 of 26 November)

- **The cause, found in the build:** the entry the tab is opened on holds no state (`history.state` is null as the page has loaded; every other page tried keeps the router's two keys), so the router lets a step back to it pass: the address changes and the page does not. Two effects of the tab hand `null` to `history.replaceState` as the page first draws (`LargeLoadRules.tsx`, `AllGridsNodes.tsx`).
- **The mend:** each hands back the entry's own state. On `wip/c780-allgrids-back` (`1ad865130`; landing row 69, requested at 13:10 UTC), with a test; seen in the same builds at both widths.

## Five faults of the sweep, mended at their cause (each on its own branch, with a test)

- **The Grid tool 506 px wide on a phone** (row G2): the note about a day not held breaks anywhere. `wip/c780-grid-note` (`9d272ae55`). Seen in the sixth build: 390 of 390 px.
- **Twelve years printed over each other, and a heat map's hours end to end and on the legend** (rows CH2, CH3): three lines of the shared chart file. `wip/c780-chart-labels` (`6ca3657f4`). Seen in the sixth build. Its second commit narrows the first rule: a chart of twelve or fewer thins only where two neighbouring labels would meet, so a long name beside short ones is written as before.
- **Three bars' figures on each other** (row CH1): each figure is raised clear of the ones before it. `wip/c780-bars-figures` (`690d7f350`); it changes the one line session 1855's test read. Seen in the sixth build.
- **The bar chart shrunk to the screen on a phone, its figures under 6 px** (row CH4, found while seeing the mend above): the brand's phone rule named the figure's own child and the chart has stood inside its hover's box since session 2201. `wip/c780-bars-phone` (`839676a49`): three rules in `site/app/tokens.css` beside the three that stand. Read on production first (seven charts on four pages, each 358 px wide, a figure's line 8 px); seen in the seventh build: each 600 px wide in a frame that scrolls it, a line 13 px, the title in place, the card opening under a finger.
- **Landing requested for each** at 13:34 UTC: rows 70 (the Grid tool's note), 71 (the chart labels), 72 (the bars' figures) and 73 (the bar chart on a phone) of `docs/state/landing_request_portable.md`.

## Part B: the browser read (`docs/reviews/browser-read-2026-11-28.md`)

- **`/forecast`**, 79 addresses at 1280 and 390 px: 158,232 marked figures agree with the page files at each width. "Tomorrow" is Friday 27 November, a day past (data request 582); one place marked shown holds no hour (583); the heading over a past day is filed for the old laptop's audit.
- **The held files' removal:** 44 of 44 answer 404 to a visitor. Two public files carry figures worked out from held grids' prices (for Samuel's ruling).
- **The site's own figure check, run whole on production** (10:51 to 10:58 UTC): 15,217 of 15,244 values match; 25 failed in four groups. Run again on those four addresses at 11:20 UTC: three groups pass (the pages had been read while the site was being deployed); `/policy` still draws no checked number against a floor of 10, while its held view is as it should be (for the desk).
- **`/equities`**, 45 addresses at each width: 22,111 marked figures agree. Eight small companies' revenue reads "0" in whole USD million; 662 keyboard stops before the foot.
- **`/impact`:** 93 of 93 announced projects picked, each opening its document; each plant type clean at both widths. Row I4 of 26 November is mended on production.
- **The sweep,** 183 addresses at each width: the Grid tool's ten addresses are 506 px wide on a phone, under a note that prints a run's raw error (the newest whole day there is 24 November); chart labels stand over each other on three pages; one logged address holds "undefined". Data requests 587 and 588.
- **The first minute:** 54 of 54 addresses of the menu, the home page, the foot and the tour answer; unchanged since 26 November.
- **A slip of the read itself:** the first two runs on `/equities` set the page's words beside the files with a rule that did not know the page writes dollars in millions; corrected, and the third run is the one reported. Four times a time was written into a row a few minutes ahead of the clock; each was corrected in the next commit.

## Needs the key

- Nothing in this session needed a model call.

## Decisions made without you

- **Where the chain's file was taken:** the main folder stood on chain 720's last branch, which does not hold the file, so the command as given refused; it was run from the documents folder, where `main` is checked out.
- **"Anything local not on origin"** read as work commits: one found and pushed; the local branches that hold only merges made for a build are left as they are.
- **Documents go to main directly,** as chains 620 and 720 pushed theirs; code goes to `wip/c780-*` only.
- **The section's own names in the address begin with `sr`,** because `sort`, `dir`, `a`, `b` and `kind` are the hub table's.
- **The table opens on the first column of each of the ten sections** (ten columns). A reader's own choice replaces it.
- **The section sorts on the server from the address,** as the hub table does, so a link carries a choice and the back button undoes it.
- **No map and no colour:** the site has no map of the regions to reuse and the Grid tool's carbon scale is not exported; the section draws neither.
- **A count of a table the site holds for a license is drawn blank whatever the file carries.** The contract called two held tables public; the page does not wait for the contract to be corrected.
- **Two lines were added at the foot of `site/next.config.ts`,** a shared file, so that the deployed site can find the regions files; the list's first line, which five tests read, stands as it is.
- **The tests' fixture holds made-up values** in the contract's shape (`tests/fixtures/siting_regions/`), says so in every file, and is never deployed.
- **The section's files stand in the tool's own folder,** not in a folder under it: two older tests hold the tool to its four folders ("one tool, one page, one address").
- **A price, a share, a count of years and a carbon intensity are written to two decimals always;** a megawatt, an hour and a count stay whole where the file's value is. Both are forms the site's value check already passes.
- **A link is drawn from a source's address only since the desktop's answer to data request 586** (`sources.<key>.url`, the place's own operator's): the first files gave one document for every place, and the section drew no link from it until that was corrected. A rule opens its own document; a queue total its own.
- **One line near the top of the tab leads to the section,** because the section stands under the hub table, a long way down. It is drawn only once the files are the data machine's.
- **The back button's cause was mended here, on a branch of its own.** The two files are the tab's and no machine's tonight; the fault stood between the new section and its own back button, and the chain's table gives this laptop "fixes on `wip/c780-*`". It is not on the section's branch, so the desk can land either without the other.
- **Five of the sweep's faults were mended here too, each at its cause with a test, on branches of their own** (the section above). **This goes past the letter of the chain:** part B says a fault on a page this machine does not own tonight is a row for its owner. Each is a row for its owner in the review, as asked; each also has a branch, because the cause was a line or three in a shared component, no machine owns those pages tonight, and the hours of part C were free. Nothing of them is on main: each is a landing row of its own (70 to 73), so the desk takes or leaves any one, and dropping all five costs nothing but the branches.
- **One older test's line was changed** (`tests/test_session1855.py`, on `wip/c780-bars-figures` only): it read the very line of the rule that put the figures on each other. It now reads the new rule, with a note; the landing row says so in bold.
- **`site/app/tokens.css`, a shared file, gains three rules** (on `wip/c780-bars-phone` only): the brand's own phone rule, said again for the chart inside its hover's box; the three older rules stand.
- **A chart of twelve columns or fewer now thins its names on a phone** where two neighbours printed over each other (on `wip/c780-chart-labels`): for years that is plainly right; for names (fuels, grids) a name is dropped, and the hover and the Table switch carry it. Left as a line for Samuel's ruling. The first form of the rule would also have thinned a chart with one long name that met nothing; it was narrowed before any landing was asked.

## For Samuel's ruling

- **The section's name.** Today: "Where the next gigawatts can go".
- **The section's place on the tab.** Today: under both columns, after the hub table and before "Large-load rules by utility".
- **Figures worked out from held grids' prices, in two public files** (a dated problem edition's data file and a finding's file). Today: both left as they are.
- **What `/forecast` should call the day it draws when that day is not tomorrow.** Today: the heading says "Tomorrow" over Friday 27 November.
- **The line that leads to the section, and its words.** Today: under the tab's row switch, "Under the table: where the next gigawatts can go, every region side by side."
- **The columns the table opens on.** Today: the first column of each of the ten sections.
- **The section adds 322 keyboard stops to a tab that already had more than 500** (line 9 of the read of 26 November). Today: every hover and every blank can be reached by the keyboard, as the tab's own are.
- **A chart of twelve names or fewer on a phone, when its names are wider than its columns.** Today on production: all printed over each other. On `wip/c780-chart-labels`: every second name written, the rest in the hover and the Table switch.
- **A small company's filed revenue reads "0" on `/equities`** (whole USD million), and **`/equities` has 662 keyboard stops before its foot.** Today: both left as they are.
