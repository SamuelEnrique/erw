# Chain 720, the portable laptop's first window: the ERW forecast page and the energy equities pages (note for Samuel)

Energy Research Warehouse (ERW). Kept current; state at 10:00 UTC on 27 November 2026. Sessions 10400 to 10409. Progress, step by step: `docs/state/progress_c720.md`. Reports: `archive/sessions/SESSION_10400_REPORT.md` to `SESSION_10409_REPORT.md`.

## 27 November: what changed since you took the laptop (sessions 10408 and 10409)

You asked for two things first. Both are done on branches and requested for landing; neither is on production yet.

- **Rows 59, 60 and 61 landed on 26 November** (the line "with the weather known", the small "i" mark, the two hovers). Everything under sections 1 to 4 below that says "once row 59 has landed" is on production now.

**Equities on the SEC's company figures (row 62, `wip/c720-equities-sec`).**

- **What production shows today** (read at 09:13 UTC on the real files): 307 companies, every share price a dashed box that says "license needed", each company's newest filing in a table. And no chart at all once a company is chosen, which is what this row mends.
- **What to click once row 62 has landed.** Open `https://erw-flame.vercel.app/equities?a=NEE&b=DUK`.
  - **You should see** two dashed boxes, "Share price, NEE, NEXTERA ENERGY INC: license needed" and the same for Duke.
  - Under "Filed figures": two figures, "Revenue, 3 months to 2026-03-31", 6,701 and 9,178 USD million, each with its filing's link, and under each a line of revenue by quarter since 2009.
  - Put the mouse on a line. **You should see** the quarter and its revenue.
  - Under "Choices" at the left, change "Filed figure" to "Debt" and "Its periods" to "12 months". **You should see** each company's debt at the end of each year reported.
  - Under the charts: "Newest period filed", one column a company and a length of period. For a company whose newest filing is for June or September you should see two columns, the 3 months and the year to date.
  - Under "Energy prices": WTI crude oil as a line of its own, as before the companies came.
  - In the table "Every company": tick "Filed figures shown" and press Filter. **You should see** 243 of 307 companies.
- **What is real:** every filed figure, from the SEC's own filings, each with its filing's address. Checked against the files: 1,179,547 figures on 2,329 pages, none differing.
- **What is blank, and why:** every share price, index and segment line ("license needed": no source's terms let the ERW keep daily prices). 64 companies' filed figures ("source needed": foreign filers and some partnerships).
- **Three things I asked the data machine about** (requests 578 to 580): eighteen large utilities (Duke, NextEra, Southern, AEP and others) show nothing after the quarter to March 2026, while 206 companies reach September; Exxon shows two quarters only, because its SEC number is a new holding company's; one company's last filing is from 2016. The page draws what the files hold.

**The forecast's new outputs (row 63, `wip/c720-forecast-lines`).** What to click once it has landed, at `https://erw-flame.vercel.app/forecast`:

- Under "Tomorrow", below the days after tomorrow: **"Texas: wind, solar and net demand"**. Four figures (in the files of 27 November: lowest net demand 22,342 MW at 14:00, highest 42,817 MW at 17:00, highest wind hour 16,297 MW, highest solar hour 24,395 MW), a chart of four lines (demand, net demand, wind, solar), a table of how each has scored, and the hours behind a fold.
- Under "How it has done", below the past day: **wind and solar on that day**, the forecast as a line and what happened as a dashed line of the same color.
- Below the report card: **"the operator's filed forecast, checked by month"**. For Texas: "In 1 of 89 months the forecast filed on Form EIA-930 is more than 5 percent from the demand it forecasts over the whole month. In those months the filed forecast is not the operator's own forecast." Then the scores on every month beside the months that pass, and every month behind a fold. Choose Duke Energy Florida (FPC) to see a place where all 89 months are flagged.
- Below it: **"with the weather forecast (a separate line, not the ERW forecast), KDFW: 17 of the 30 days needed, too few days to judge"**, one row of scores, and its hours for tomorrow behind a fold. It is in no chart.
- Below it: **"the band, and how often what happened fell inside it"**. For Texas: demand 80.30 percent inside, 9.40 below, 10.30 above; a chart by hour of the day; each month behind a fold.
- Press the "Price" tab and scroll past "How it has done": **"Real-time price"**. For Texas, at ercot:HB_NORTH: a dashed box that says "no forecast yet" for tomorrow (the file's own words: the day-ahead price for the day was not held when the forecast was made), a past day with the forecast, the day-ahead price and what happened, and the report card (over the last two years the ERW forecast missed by 12.33 USD/MWh, the day-ahead price by 11.83).
- **What is real:** every figure, from window B's files, each with its key into its file. Checked: 104,171 figures on 120 pages (all 29 places), none differing.
- **Not drawn, and asked of window B** (its requests 11 and 12): CAISO's own wind and solar lines, which no place's file names; net demand for tomorrow in four regions, where the file is empty and gives no reason.

## One thing first: a held price is drawn on production

- **Where:** the Grid tool's Network view with Prices on (`https://erw-flame.vercel.app/grid?grid=us48&view=network&net=day&t=2025-07-24&node=NYIS&prices=1`), in the internal view. The page is in review, so a visitor does not see it.
- **What:** New York's hub price (47.50 USD/MWh on 24 July 2025; 65.11 on 20 November 2026) and New England's (47.59) are printed in the panel and drawn as a ring. Both grids' prices are held since 21 October ("license needed").
- **Who found it and what is done:** the second window (its review's row H2). Its mend is row 10 of `docs/state/landing_request_portable_w2.md`; this window built it, saw both panels read "license needed" with no figure, read production once as the control, and marked the row requested for the desk's next gate at 18:37 UTC. The files that still carry the prices are the second window's data request 576.
- **Not this window's page, and nothing of it was edited here.**

## Where things stand

- **The two new pages, the board's new group and the forecast's problem set are on production since 17:13 UTC** (landing 3 of window A's desk, `693a4a3f5`: rows 54, 55 and 56). They are in review: you see them in the internal view, a visitor sees the in-review page.
- **Read on production at 17:30 to 17:40 UTC:** both pages and the board at 1280 and 390 px, no sideways scroll; the site's value check, 1,950 of 1,950 figures of `/forecast`, `/equities` and the problem set equal to the files; all 18 download addresses answer, a reader's address carries only the checked value, an unknown place answers 404; the problem set draws its 6 questions and 83 figures and is not in the list of sets. Against main's files on this laptop: every drawn figure of `/forecast` (69,888, all 29 places) and of `/equities` (1,092), none differing.
- **Rows 57 and 58 landed at 18:35 UTC** (landing 4, `b80148122`): the day's peak, the days after tomorrow and the hover's word on `/forecast`; the equities fields no file carries yet. Read on production at 18:48 to 18:52 UTC: both blocks drawn at 1280 and 390 px, one place and two, no sideways scroll; the new download answers and a visitor with no cookie gets the in-review page at every new address, never the data; the value check, 2,000 of 2,000; on main's files every drawn figure of `/forecast`, 73,200, none differing.
- **Not yet landed:** rows 59 (the line "with the weather known"), 60 and 61 (the second window's findings).
- **The figures move with each rebuild of window B's files** (11:49, 14:05 and 15:51 UTC today). The figures quoted below are those of the files built at 15:51 UTC unless a line says otherwise.
- **The second window read both pages on production** (43 addresses of `/forecast`, 19 of `/equities` and the board, 18:25 UTC in its review). Every figure agreed with the files and the board lost nothing it had. It filed four small faults for this window, all mended (rows 57, 60 and 61): the hour a forecast was made could not be read on a phone or with the keyboard (a small "i" mark beside the place's name now opens on a tap); the hover gave two different hours with no word between them; a held price's hover said "License needed: license needed"; the first blank of `/equities` said "license needed" over a hover that began "source needed".
- **Window B's files were rebuilt at 14:05 UTC** and landed with the pages: Texas now uses the fourth method ("regression with the recent days"), every figure moved a little, and the line "with the weather known" is now filled for all 29 places. The page on production does not draw that line yet; it is requested as row 59 (18:15 UTC).
- **Two new pages and one new group on the price board were built, tested, seen in a build and requested for landing** in sessions 10401 and 10402.
- **The desk held both rows back once** (13:10 UTC): its whole suite failed three tests that keep lists of the site's files (the pages the value check reads, the files that read the disk, the routes that read the address), and the new pages were in none. That was this window's miss. Both rows were mended and requested again (13:31 and 13:42 UTC, heads `bf0430170` and `7d1ffc26b`).
- **The other windows' files landed on main at 14:16 UTC.** The two pages have not yet: the desk's next gate holds them.
- **One more fault was found and mended before the landing** (14:25 UTC). The site's own value check, run on a build with the real files, failed 70 figures of `/forecast` and 21 of `/equities`. No number was wrong: the check did not know that `/forecast` writes a megawatt whole and that `/equities` writes a rise with a plus sign. The check now knows both; the pages are unchanged. Rows 54 and 55 moved one commit each (`abdf999f2`, `b06045762`).
- **A problem set for the forecast page is written and requested** (row 56, section 4 below). It waits for your approval: it is on its own page only.
- **`/forecast` gained the day's peak and the days after tomorrow** (row 57, 15:22 UTC), from two things window B added to its files after the page was built. What to click is under section 1.
- **The equities page is ready for the fields window A added to its contract** (row 58, 15:44 UTC): a company's last close, changes and market value, and a board row's averages and range. No file carries them yet, so you will see no change until the equity side opens.
- **A fault the second window found in the forecast page's hover is mended** (on row 57, 15:46 UTC): the hover gave the hour the file says a forecast was made (12:00 UTC today) beside the rule's hour (20:00 UTC) with no word between them. It now says the two differ and which one it gives.
- **The hover's fix above is on production since 18:35 UTC** (row 57).
- **Both pages are in review and in no menu.** `site/lib/release.ts` and the menu were not touched.
- **Both were read on the real files before those files landed** (copies taken from the other windows' branches into a folder of this laptop, never committed here).

## 1. The ERW forecast: `https://erw-flame.vercel.app/forecast`

What to click, once the page and window B's files have landed:

- Open the address. **You should see** "ERW forecast" as the title, Texas chosen, and under "Tomorrow" three figures (the highest hour of the ERW forecast, the operator's forecast for that same hour, the lowest hour), then a chart of the 24 hours with a grey band around the line.
- Put the mouse on the chart. **You should see** the hour, the ERW forecast in MW and the band's low and high.
- Press "Hour by hour" under the chart. **You should see** a table of 24 rows.
- Scroll to "How it has done". **You should see** a past day (the newest held) with three lines: the ERW forecast, the operator's forecast, what happened; then four tables of scores.
- Read the table "By month". **You should see** every month since July 2019 in a frame that scrolls, with the ERW forecast beside the operator and the two simple rules. **For Texas the operator's forecast is the better one in every one of the 89 months** (2.39 percent against the ERW forecast's 5.47 percent over the whole backtest, in the files built at 14:05 UTC), and the page shows that as it is. Over the whole backtest the ERW forecast is the better one in 6 of the 29 places (California, the Northwest, CAISO, Duke Energy Florida, PacifiCorp East, Southwest Power Pool) and the operator's in 23: the table "Every place" lists all 29 in one order, with no mark on either.
- Under "Choices" at the left, choose a second place under "Place B, side by side". **You should see** two charts side by side and each score table with both places' columns.
- Press the "Price" tab. **You should see** tomorrow's day-ahead price forecast for the hub named beside the place. For a place whose price the ERW may not show (the Mid-Atlantic, New York, New England) **you should see** a dashed box that says "license needed"; the reason is on hover.
- At the foot, "Downloads": the place's hours, the report card and the ledger (every forecast as it was made, never rewritten), each as CSV with a reader in Python and in Stata.
- Under "Tomorrow", below the hours (on production since 18:35 UTC): **you should see** "Texas: the days after Friday 27 Nov 2026", a chart of four more days with the grey band, and a table of four rows. The first row read on production at 18:50 UTC: Sat 28 Nov, highest hour 53,151 at 18:00, lowest 47,035 at 03:00, the forecast's error 6.33 percent, the week-ago hour's 8.14, the operator's day-ahead error 1,179 MW, 81.00 percent in band.
- Put the mouse on "Texas" at the head of "Tomorrow" (on production since 18:35 UTC): **you should see**, in the hover, "The file records this forecast as made at 15:00 UTC, not at the rule's 20:00 UTC: the hour given here is the file's."
- Under "How it has done", after the first table (on production since 18:35 UTC): **you should see** "The day's peak" with six rows. For Texas over the last two years, in the files built at 14:05 UTC: the ERW forecast missed the peak's size by 6.10 percent and the operator by 2.19; the ERW forecast had the peak's hour on 47.50 percent of days and the operator on 58.90.
- **Once row 59 has landed,** under "The day's peak": **you should see** "With the weather known (not a forecast), beside the regression and the operator on the same hours", a table of two rows. For Texas over the last two years it reads 3.90 percent (with the weather known), 5.26 (the regression), 2.06 (the operator). The line reads the day's own weather, so it is not a forecast, and it is in no chart.
- Choose "Price" in the tab: **you should see** none of the three blocks. They are of demand.

What is real and what is not:

- **Real, from window B's files:** every figure. A check drew the page for all 29 places, both series and both scores and set 60,474 figures beside the files: none differed.
- **Blank, and why:** the operator's forecast for tomorrow where the operator has not published it yet ("not held"); the price for 23 of the 29 places (15 have no organised day-ahead market, 6 need a license, 2 are MISO's, paused).
- **Until window B's files land** the page is its title and one box that says "not built yet".

## 2. Energy equities on the price board: `https://erw-flame.vercel.app/board#equities`

- Open the address. **You should see** the board as it was, and a new group at its foot, "Energy equities". Press its title to open it.
- **With window A's files as they stand (27 November) you should see 30 rows that each say "not held yet".** Put the mouse on one: the reason is there (no price source has terms that let the ERW keep daily share prices or index levels; for seven segments, also that no SEC industry code holds the segment alone). Read on production at 09:13 UTC on 27 November: 30 rows, none with a figure.
- Once a row holds a value: its latest value, its date, its change over a day, a week, a month, a year and the year to date, and a small trend line. Pressing the row opens `/equities` on that series.

## 3. Energy equities, the page: `https://erw-flame.vercel.app/equities`

- **Since 27 November the files hold 307 companies** (your ruling on the SEC's data): the page as landed, and what row 62 adds, are at the head of this note. The lines below describe the page as it was on 26 November, while no company was in the files; the energy prices and the segments read the same today.
- Open the address. **On 26 November's files you saw** a dashed box under "The line" that says "Companies, indices and segment lines: license needed", then "Energy prices": WTI crude oil as a line over the last year (89.53 USD per barrel on 17 November), and a table of 12 energy prices with each one's latest value, its date under it, and its changes. Uranium says "monthly" under Day and Week; four power prices say "license needed" or "paused".
- Press another price in the table, for example "Henry Hub natural gas, spot". **You should see** its line in place of WTI's.
- Under "Choices", change "Window" to "5 years". **You should see** the line over five years.
- Scroll to "Segments and indices". **You should see** the 15 segments, each saying "source needed" for its companies and "license needed" for its line, with the reason on hover.
- **Once a company's series exists** (not today): choose it under "A", a second under "B"; **you should see** two price lines side by side, the newest filed figures of both in one table, and every period filed behind a fold, each period a link to its filing on the SEC's site.

What is real and what is not:

- **Real:** the eight energy prices shown (from the ERW's own price tables), their changes, and the list of segments.
- **Blank, and why:** every company, index and segment line (above); four power prices (PJM, NYISO and ISO-NE need a license, MISO is paused).
- **Built and tested against made-up values only, because no real series exists yet:** the company and segment charts, the filed figures, the table of every company. The made-up values were used on this laptop alone and are in no file of the site.

## 4. A problem set for the forecast page: `https://erw-flame.vercel.app/learn/problems/a-forecasts-report-card`

What to click, once row 56 has landed:

- Open the address. **You should see** the title "A forecast's report card: the ERW forecast against the operator's and two simple rules", a worked example with its answer open, and six questions, each with "Show answer".
- Press "Show answer" under Question 1. **You should see** "The ERW forecast 2,838.95 MW, the operator's 1,177 MW: 2.41 times" (read on production at 17:35 UTC; the figures move when window B's file is rebuilt, as they did at 14:05 UTC), the computation in one line, and the steps that name the rows of the file.
- Put the mouse on any figure. **You should see** the file it was read from and the path inside it.
- Open `https://erw-flame.vercel.app/learn/problems`. **You should not see** this set in the list: it waits for you.

What is real and what is not:

- **Real, from window B's file `site/data/predict/scores.json`:** every figure. Each is read by its key when the page is drawn, so the answers move when the file is rebuilt.
- **It takes no side.** For Texas the operator's forecast has the smaller error in every question that sets the two side by side (5.47 percent against 2.39 over the whole backtest; 2,838.95 MW against 1,177 over the last two years). For California the ERW forecast's is the smaller (4.01 percent against 4.68). The set writes both as the file holds them.
- **Not in any dated edition, not in the list of sets, no CSV download,** until you approve it.
- **The equities page has no problem set.** The chain asks for a segment beside an energy price, and no segment has a line today (license needed).

## What was seen and requested for the second window

- Row 1, `/grid?grid=caiso` at a phone's width (it was 539 px wide, it is 390).
- Row 2, the curtailment trend names the fuel it sums; the COVID page keeps to a phone's width.
- Row 3, `/conditions`: the alerts table lists every notice its heading counts.
- Row 4, the Grid tool's chart "today so far and the same day last week": last week's line holds all 24 hours on four grids' pages.
- Row 5, `/companies`: after a choice, Show and the back button, the lists read what the page shows; the six fields have names for a screen reader.
- Row 6, `/prices/compare` and `/conditions`: the same mend of the back button. With row 5, 8 of 8 fields read the page's value in the build; on production today, 0 of 8.

## What waits for you (each left as it is; nothing was decided for you)

- **Where the two pages sit in the menu and what they are called there.** Today: in no menu; their titles are "ERW forecast" and "Energy equities".
- **The place `/forecast` opens on.** Today: Texas.
- **The board already had a row named "Energy equities"** (in its group "Capacity and equities") that says "licensed source needed". The new group of the same name stands beside it. Today: both left.
- **Thirty blank rows in the board's new group** while nothing is held. Today: every row drawn, the group closed until pressed. The other way is one line with the count and the reason.
- **What `/equities` opens on while no company is held.** Today: the first energy price the files show.
- **Whether the line "with the weather known" belongs on `/forecast`.** Today (row 59): one table, labelled "not a forecast".
- **The internal view allows 30 unlocks an hour for the whole laptop,** and two windows reading production in a browser reach it (the door was closed to both from 17:42 to 18:00 UTC). Today: left as it is.
- **Whether the days after tomorrow belong on `/forecast`,** and where. Today (row 57): under "Tomorrow", demand only.
- **Whether the peak's table should also be in "Every place".** Today: drawn for the place or the two places chosen.
- **Whether the forecast's problem set joins the listed sets.** Today: it waits on its own page, in no list and no edition.
- **Whether a problem set that shows the ERW forecast scoring worse than the operator's in Texas is wanted as it is.** Today: written as the file holds it.
- **The Chart and Table switch of the site's charts is 22 px tall** on every page (24 is the least for a finger). Today: left.
- **Which company `/equities` opens on** (27 November). Today: the list's first by ticker, ProFrac Holding (ACDC). A large, familiar company would say more at a glance.
- **Whether a quarter that was only filed inside a year's total may be worked out** (the year less its nine months). Today: not; the page shows only what was filed, so most companies have no point for their fourth quarter.
- **Where the forecast's new blocks sit.** Today: net demand under "Tomorrow"; the operator's filing, the weather forecast line and the band after the report card; the real-time price as a section of its own under "Price".
- **Whether the page should say, of the operator's filing, anything where no month is flagged.** Today: no sentence; the months are in a fold that says "none flagged".

## What waits on others

- **Window A's desk:** landing row 62 (equities on the SEC's figures, requested 09:25 UTC on 27 November) and row 63 (the forecast's new views; requested once its newest head is seen in a build, which waits for 2 GB of free memory on this laptop). Rows 54 to 61 have landed.
- **Window A:** data requests 578 to 580 (27 November): the list's newest filed period; eighteen utilities' missing quarters, Exxon's short history, one stale filer; the board's own check on two held rows.
- **Window B:** its requests 11 and 12 (27 November): CAISO's wind and solar lines that no place names, and net demand empty with no reason in four regions; the words of the real-time price's cuts.
- **Window B:** nothing asked. Its files of 14:05 UTC hold the fourth method (on production its name reads "regression recent" until row 57 lands with its words) and the line "with the weather known" for all 29 places, which the page does not draw yet.
- **Window A:** data requests 571 to 574 in `docs/state/data_requests_done_line.md` (the list's last close and changes; the board rows' other cells; the board's older row; what the built files carry beyond the contract's text). And the two rulings its own work waits on: the SEC's contact string and a price source.
- **Window B:** nothing asked. Its contract and files were enough.
