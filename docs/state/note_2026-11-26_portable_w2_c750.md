# Note of chain 750 (the portable laptop's second window, 26 November 2026): the browser read

Energy Research Warehouse (ERW). The chain: `queue/done/750-night-26-november-portable-window2-browser-read.md`. Progress: `docs/state/progress_c750.md`. The review: `docs/reviews/browser-read-2026-11-26.md`. Model spend USD 0. Kept current while the chain runs; this is its state at 14:10 UTC on 26 November.

## Pages read, and what was found

- **Read on production in a real browser, at 1280 px with a mouse and 390 px with a finger:**
  - part A: the five rows that waited for a browser, all seen;
  - part B: everything landed 20 and 21 November (`/conditions` and `/congestion` in full, the thirteen regions of the Grid tool, the four accessibility fixes, chain 620's ten fixes, the problem edition of 21 November, the events, demand and supply pages);
  - part D: the five sellable tools (battery, generator, Automated Analysis, the Grid tool, and what a datacenter pays, read only), fourteen more pages of the menu by hand, the first minute;
  - sweeps: every page with a fixed address and the Grid tool's 63 views at both widths, and the 173 addresses of the site's own check list at a phone's width with every chart switched to its table.
- **Figures set beside their source:** about 120,000 against the page files (15,553 on `/conditions`, 8,941 on `/congestion`, 94,435 on the regions' Mix tabs, 838 words and figures of the problem edition) and 5,142 against Supabase by the site's own check on the five tools' addresses (988, 1,377 and 2,777). The only disagreement was the alerts list of `/conditions`.
- **Part C has not begun:** none of tonight's pages (`/forecast`, `/equities`, the board's new group, `/impact` with Datacenter, the All grids tab's new rows) was on main at 14:05 UTC.
- **Faults, by owning window:**
  - no window's page tonight: 6 found, 6 fixed on four branches, each with a test (rows 1, 3, 4 and 5 of `docs/state/landing_request_portable_w2.md`; rows 1, 3 and 4 seen in a build by the first window and requested);
  - the desktop's second window (B): 1 filed (two of its commits read landed and are not on main; row 2, seen in a build and requested);
  - the old laptop (D), on pages it audits tonight: 2 filed (`/cost-of-power` 1,677 px wide on a phone; a false sentence on `/research`);
  - window A (the data machine), with the old laptop: 1 filed (the All grids tab does not follow the back button); and 1 known to it already (the page files of 21 to 25 November);
  - windows C and E: none yet (their pages had not landed).

## The five worst things found

1. **`/grid?grid=caiso` scrolls sideways on a phone** (539 of 390 px) since 21 November: the accessibility fix made that day without a browser put 226 hidden labels in the reliability table, and those past the table's frame widen the page. Fixed, seen in a build, requested.
2. **`/conditions` dropped alerts without saying so:** 40 rows under a heading that counts 44 (CAISO's September 2022 heat wave lost its last day) and 40 of 79 (August 2020). Fixed, seen in a build, requested.
3. **On the All grids tab of `/cost-of-power` the back button changes the address and not the page** (8 of 8 tries): the screen shows the flexible load under the datacenter's address, on a page that tells its reader to copy the address. And its "Grid by grid" view becomes 1,677 px wide on a phone after one tap on a chart's Table switch. Both filed for the windows that own the page tonight.
4. **The Grid tool's "same day last week" loses its first 5 to 8 hours on every grid** whenever the loads are two days behind the clock, though the live set holds them. Fixed, seen in a build, requested.
5. **Two fixes marked landed on 21 November are not on main,** and **every page that draws the data machine's page files shows 18 to 20 November** (its daily commits of 21 to 25 November sit on `wip/red-dm-*` branches; window A repairs it tonight).

Also fixed: `/companies`, where five of six fields had no name for a screen reader and the lists kept a choice after the back button.

## Where the pictures are

- `https://github.com/SamuelEnrique/erw/tree/main/docs/reviews/browser-read-2026-11-26` (a folder a page: `conditions`, `congestion`, `grid-regions`, `grid-caiso-reliability`, `grid-tool`, `battery`, `generator`, `automated-analysis`, `datacenter-pays`, `policy-week`, `severance`, `problem-edition`, `events-covid-2020`, `chain-620-fixes-on-production`, `first-minute`, `part-a`). Each picture has its line in the review.

## What waits for Samuel, with the page left as it is

In plain words; the same nine lines stand at the foot of the review.

1. Should the reason a figure is blank open on a tap, as the "i" marks do? Today only a mouse can read it.
2. `/congestion` prints "1080.08 USD/MWh" beside "330,132": a thousands comma in one column and none in the other. The gate's own check holds it that way.
3. `/congestion` calls CAISO's base case "contingency Base Case".
4. `/supply`: a year with a month left out makes the mix table half again as wide inside its frame on a phone.
5. The tour's Digest stop still quotes two headings the Digest page does not show.
6. `/conditions`: on the branch every alert is listed (79 rows for August 2020). If the list should stop at 40, the page should say so.
7. A chart switched to its table prints "not held" for a missing value and gives no reason.
8. `/research` says of its small example charts "hover reads them"; they give no value. Take the words out, or give the examples their values.
9. The All grids tab has more than 500 keyboard stops before its foot.

## Stopped, and not started again unless asked

- Two runs were stopped by Claude Code at about 12:23 UTC, the laptop critically low on memory while this window waited on them: the sweep of all 616 method pages at a phone's width, and the site's figure check over its whole list. The figure check was since run in the foreground on the five tools' addresses only. The method pages were not swept; the six that chain 620's fix mended are 390 px wide.

## What waits for a window

- **Window A's desk:** rows 1 to 4 of `docs/state/landing_request_portable_w2.md` are requested; row 5 waits for the first window's next build.
- **The old laptop and window A:** rows CP1, CP2 and R1 of the review.
- **This window:** tonight's pages as they land, then the first minute once more with them in the menu and the tour.
