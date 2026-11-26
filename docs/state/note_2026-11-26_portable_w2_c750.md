# Note of chain 750 (the portable laptop's second window, 26 November 2026): the browser read

Energy Research Warehouse (ERW). The chain: `queue/done/750-night-26-november-portable-window2-browser-read.md`. Progress: `docs/state/progress_c750.md`. The review: `docs/reviews/browser-read-2026-11-26.md`. Model spend USD 0. Kept current while the chain runs; this is its state at 17:50 UTC on 26 November.

## First: prices the site holds back are served to any visitor as files

- Found at 17:52 UTC, older than tonight, nothing changed by this window. The pages draw a held price as "license needed"; the files under `site/public` are served to anyone. 234 of them hold prices, or figures from prices, of NYISO, ISO-NE and MISO: a year of hourly prices a file in `site/public/seller/prices/` (`isone_2025.json`, `nyiso_2019.json` to `nyiso_2025.json`, built 20 November, a month after the hold of 21 October), 36 hourly files in `site/public/board/h/` left from before the hold, and 190 gallery files. The first two sets are in the public repository too. Data request 576 (window A). Yours to rule: the copies in git's history, and MISO's.

## Pages read, and what was found

- **Read on production in a real browser, at 1280 px with a mouse and 390 px with a finger:**
  - part A: the five rows that waited for a browser, all seen;
  - part B: everything landed 20 and 21 November (`/conditions` and `/congestion` in full, the thirteen regions of the Grid tool, the four accessibility fixes, chain 620's ten fixes, the problem edition of 21 November, the events, demand and supply pages);
  - part D: the five sellable tools (battery, generator, Automated Analysis, the Grid tool, and what a datacenter pays, read only), then every other page with a fixed address by hand (43 pages), the first minute, and ten readers' cases taken on the Grid tool and Automated Analysis;
  - sweeps: every page with a fixed address and the Grid tool's 63 views at both widths, and the 173 addresses of the site's own check list at a phone's width with every chart switched to its table.
- **Figures set beside their source:** about 120,000 against the page files (15,553 on `/conditions`, 8,941 on `/congestion`, 94,435 on the regions' Mix tabs, 838 words and figures of the problem edition) and 5,142 against Supabase by the site's own check on the five tools' addresses (988, 1,377 and 2,777). The only disagreement was the alerts list of `/conditions`.
- **Part C began at 14:16 UTC** with tonight's first landing: this window's first three rows, seen fixed on production at both widths, and `/impact` with Datacenter (window C's), read in full. The four older plant types show exactly what they showed before (1,700 figures on eleven addresses saved before the deploy and after, none changed). 
- **Tonight's second landing (17:13 UTC), read on production from 17:19 UTC:**
  - `/forecast` (window E's): 43 addresses at each width, 38,042 figures agreeing with its files; nothing on it can be taken for a published figure; the score tables draw a loss exactly as a win (the operator is ahead in 24 of 29 places, and the page shows all 29); a held place's price is a blank;
  - `/equities` and the board: 19 addresses, 832 figures; a held price is a blank with its reason, never a zero; the board lost nothing (25 groups and 276 rows as before, one group of 30 rows added). The files hold no company yet, so "a company's filed figures open their filing" could not be read;
  - this window's rows 4, 5 and 6 seen fixed on production; the eight new labels of the method pages seen; the large-load rule newly read (Rhode Island) opens its order and the rule newly held is blank; 25 changed pages compared before and after, nothing lost.
- **Three more reads the chain does not ask for, each of which found something:** an accessibility audit of 39 pages (AccessLint), every link of 199 addresses read for a link told by color alone, and every address opened at 360, 320 and 768 px.
- **Faults, by owning window:**
  - no window's page tonight: 12 found, 12 fixed on eight branches, each with a test (rows 1 and 3 to 9 of `docs/state/landing_request_portable_w2.md`). Rows 1 and 3 landed at 14:16 UTC and are seen on production; rows 4, 5 and 6 landed at 17:13 UTC; rows 7 and 8 (three links told by their color alone on `/events`, `/curtailment` and `/play/ev`, found by an accessibility audit of 39 pages and a read of every link of 199 addresses) are seen in a build and requested; row 9 (`/learn/problems` wider than a 360 px phone, found by opening every address at 360, 320 and 768 px) is ready, to be seen;
  - the desktop's second window (B): 1 filed (two of its commits read landed and were not on main; row 2, landed at 14:16 UTC and seen on production);
  - window E (`/forecast`, `/equities`): 4 filed (the hour a forecast was made can be read only by hovering with a mouse, so not on a phone or by keyboard; the same hover gives the file's hour and a rule that states another; a held price's reason says its status twice; one blank's face says "license needed" over a reason that says "source needed");
  - window C (`/impact` with Datacenter): 6 small rows filed (the opening scenario moved with its file in the second landing, 1,000 to 1,400 MW, and the page does not say why;a default's own document cannot be opened from the page; the taxes' total does not say what it leaves out; Georgia's exemption reads "none" where it is held and not applied; a document's figure the tool does not take is not said; an address with the project's id alone shows its name over the default's figures);
  - the old laptop (D), on pages it audits tonight: 2 filed (`/cost-of-power` 1,677 px wide on a phone; a false sentence on `/research`);
  - window A (the data machine), with the old laptop: 4 filed (the All grids tab does not follow the back button; two regions of one name on it; `/data/licenses` wider than a 360 px phone and `/data` wider than a 320 px one, on files its branch changes tonight) and 1 data request (row 575: the Southeast's demand of 13 to 17 November is 4 to 6 percent higher in the forecast's files than in `/demand`'s); and 1 known to it already (the page files of 21 to 25 November);

## A slip of mine

- At 17:42 UTC the internal view's door closed to this laptop until 18:00 UTC: it allows 30 unlocks an hour from one address, and my read kit unlocked once a script. Nothing was changed by it; the first window was told; the kit now keeps the reviewer's cookie (one unlock). The site's own figure check on the new pages and the first minute wait for the door.

## The five worst things found

1. **`/grid?grid=caiso` scrolls sideways on a phone** (539 of 390 px) since 21 November: the accessibility fix made that day without a browser put 226 hidden labels in the reliability table, and those past the table's frame widen the page. Fixed, seen in a build, requested.
2. **`/conditions` dropped alerts without saying so:** 40 rows under a heading that counts 44 (CAISO's September 2022 heat wave lost its last day) and 40 of 79 (August 2020). Fixed, seen in a build, requested.
3. **On the All grids tab of `/cost-of-power` the back button changes the address and not the page** (8 of 8 tries): the screen shows the flexible load under the datacenter's address, on a page that tells its reader to copy the address. And its "Grid by grid" view becomes 1,677 px wide on a phone after one tap on a chart's Table switch. Both filed for the windows that own the page tonight.
4. **The Grid tool's "same day last week" loses its first 5 to 8 hours on every grid** whenever the loads are two days behind the clock, though the live set holds them. Fixed, seen in a build, requested.
5. **The same place and day read two ways on two pages:** the Southeast on 13 November is 606.1 GWh on `/forecast` and 570.6 GWh on `/demand` (4 to 6 percent apart on five days), because the demand files are those of 21 November: every page that draws the data machine's page files shows 18 to 20 November (data request 575; window A repairs the files tonight). And **two fixes marked landed on 21 November were not on main** (landed tonight).

Also fixed: `/companies`, where five of six fields had no name for a screen reader; and the back button on the three forms that submit with their button (`/companies`, `/prices/compare`, `/conditions`), whose fields kept the later choice over the earlier page.

## Where the pictures are

- `https://github.com/SamuelEnrique/erw/tree/main/docs/reviews/browser-read-2026-11-26` (a folder a page: `conditions`, `congestion`, `grid-regions`, `grid-caiso-reliability`, `grid-tool`, `battery`, `generator`, `automated-analysis`, `datacenter-pays`, `policy-week`, `severance`, `problem-edition`, `events-covid-2020`, `chain-620-fixes-on-production`, `first-minute`, `part-a`). Each picture has its line in the review.

## What waits for Samuel, with the page left as it is

In plain words; the same thirteen lines stand at the foot of the review.

1. Should the reason a figure is blank open on a tap, as the "i" marks do? Today only a mouse can read it.
2. `/congestion` prints "1080.08 USD/MWh" beside "330,132": a thousands comma in one column and none in the other. The gate's own check holds it that way.
3. `/congestion` calls CAISO's base case "contingency Base Case".
4. `/supply`: a year with a month left out makes the mix table half again as wide inside its frame on a phone.
5. The tour's Digest stop still quotes two headings the Digest page does not show.
6. `/conditions`: on the branch every alert is listed (79 rows for August 2020). If the list should stop at 40, the page should say so.
7. A chart switched to its table prints "not held" for a missing value and gives no reason.
8. `/research` says of its small example charts "hover reads them"; they give no value. Take the words out, or give the examples their values.
9. The All grids tab has more than 500 keyboard stops before its foot; so have `/data` and `/terms`.
10. The Grid tool's Network view says "copy the address to share the view"; while a Watch story plays the address is still the live week's. It takes the story once paused.
11. The Price years list: on the battery tool one step back leaves the tool; on the generator's page it undoes the choice. One way for both?
12. `/digest` says "No Digest yet for Thursday 26 November ... the daily run starts at 14:00 UTC" while the Digest is paused (the newest is 12 November). A line saying it is paused, and since when?
13. What a visitor sees at the home address today: the heading "/", "This tool is in review and will open when it is approved", and a list "Open now" whose one entry, Home, is itself marked "in review". The in-review page names a page from the menu's list and prints the address of any page not in it (18 of 75, `/forecast` and `/equities` among them). A name for the home page, at least?

Line 1 grew by one page: `/queues`' three charts give a year's figure only as the browser's tooltip, so a phone reads none of them.

## Stopped, and not started again unless asked

- Two runs were stopped by Claude Code at about 12:23 UTC, the laptop critically low on memory while this window waited on them: the sweep of all 616 method pages at a phone's width, and the site's figure check over its whole list. The figure check was since run in the foreground on the five tools' addresses only. The method pages were not swept; the six that chain 620's fix mended are 390 px wide.

## What waits for a window

- **Window A's desk:** rows 4, 5 and 6 of `docs/state/landing_request_portable_w2.md` are requested (rows 1, 2 and 3 landed at 14:16 UTC).
- **Window C:** rows I1 to I5 of the review. **The old laptop and window A:** rows CP1, CP2 and R1.
- **This window:** `/forecast`, `/equities` and the board's new group as they land, then the first minute once more with tonight's pages in the menu and the tour.
