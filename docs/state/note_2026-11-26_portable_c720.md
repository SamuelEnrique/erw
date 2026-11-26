# Chain 720, the portable laptop's first window: the ERW forecast page and the energy equities pages (note for Samuel)

Energy Research Warehouse (ERW). Kept current; state at 15:25 UTC on 26 November 2026. Sessions 10400 to 10405. Progress, step by step: `docs/state/progress_c720.md`. Reports: `archive/sessions/SESSION_10400_REPORT.md` to `SESSION_10405_REPORT.md`.

## Where things stand

- **Two new pages and one new group on the price board are built, tested, seen in a build and requested for landing.** Neither has landed yet, so nothing below can be clicked on production until window A's desk lands rows 54 and 55 of `docs/state/landing_request_portable.md`.
- **The desk held both rows back once** (13:10 UTC): its whole suite failed three tests that keep lists of the site's files (the pages the value check reads, the files that read the disk, the routes that read the address), and the new pages were in none. That was this window's miss. Both rows were mended and requested again (13:31 and 13:42 UTC, heads `bf0430170` and `7d1ffc26b`).
- **The other windows' files landed on main at 14:16 UTC.** The two pages have not yet: the desk's next gate holds them.
- **One more fault was found and mended before the landing** (14:25 UTC). The site's own value check, run on a build with the real files, failed 70 figures of `/forecast` and 21 of `/equities`. No number was wrong: the check did not know that `/forecast` writes a megawatt whole and that `/equities` writes a rise with a plus sign. The check now knows both; the pages are unchanged. Rows 54 and 55 moved one commit each (`abdf999f2`, `b06045762`).
- **A problem set for the forecast page is written and requested** (row 56, section 4 below). It waits for your approval: it is on its own page only.
- **`/forecast` gained the day's peak and the days after tomorrow** (row 57, 15:22 UTC), from two things window B added to its files after the page was built. What to click is under section 1.
- **The desk's next gate holds the newest heads of rows 54 to 56** (read 15:06 UTC). Nothing of this window's has landed yet.
- **Both pages are in review and in no menu.** `site/lib/release.ts` and the menu were not touched.
- **Both were read on the real files before those files landed** (copies taken from the other windows' branches into a folder of this laptop, never committed here).

## 1. The ERW forecast: `https://erw-flame.vercel.app/forecast`

What to click, once the page and window B's files have landed:

- Open the address. **You should see** "ERW forecast" as the title, Texas chosen, and under "Tomorrow" three figures (the highest hour of the ERW forecast, the operator's forecast for that same hour, the lowest hour), then a chart of the 24 hours with a grey band around the line.
- Put the mouse on the chart. **You should see** the hour, the ERW forecast in MW and the band's low and high.
- Press "Hour by hour" under the chart. **You should see** a table of 24 rows.
- Scroll to "How it has done". **You should see** a past day (the newest held) with three lines: the ERW forecast, the operator's forecast, what happened; then four tables of scores.
- Read the table "By month". **You should see** every month since July 2019 in a frame that scrolls, with the ERW forecast beside the operator and the two simple rules. **For Texas the operator's forecast is the better one in every one of the 89 months** (2.39 percent against the ERW forecast's 5.86 percent over the whole backtest), and the page shows that as it is. Over the whole backtest the ERW forecast is the better one in 5 of the 29 places (California, the Northwest, CAISO, Duke Energy Florida, PacifiCorp East) and the operator's in 24: the table "Every place" lists all 29 in one order, with no mark on either.
- Under "Choices" at the left, choose a second place under "Place B, side by side". **You should see** two charts side by side and each score table with both places' columns.
- Press the "Price" tab. **You should see** tomorrow's day-ahead price forecast for the hub named beside the place. For a place whose price the ERW may not show (the Mid-Atlantic, New York, New England) **you should see** a dashed box that says "license needed"; the reason is on hover.
- At the foot, "Downloads": the place's hours, the report card and the ledger (every forecast as it was made, never rewritten), each as CSV with a reader in Python and in Stata.
- **Once row 57 has landed,** under "Tomorrow", below the hours: **you should see** "Texas: the days after Friday 27 Nov 2026", a chart of four more days with the grey band, and a table of four rows. The first row today reads Sat 28 Nov, highest hour 52,812 at 18:00, lowest 45,567 at 03:00, the forecast's error 6.34 percent, the week-ago hour's 8.13, the operator's day-ahead error 1,178 MW, 80.70 percent in band.
- **Once row 57 has landed,** under "How it has done", after the first table: **you should see** "The day's peak" with six rows. For Texas over the last two years: the ERW forecast missed the peak's size by 6.30 percent and the operator by 2.19; the ERW forecast had the peak's hour on 44.20 percent of days and the operator on 59.00.
- Choose "Price" in the tab: **you should see** neither block. They are of demand.

What is real and what is not:

- **Real, from window B's files:** every figure. A check drew the page for all 29 places, both series and both scores and set 60,474 figures beside the files: none differed.
- **Blank, and why:** the operator's forecast for tomorrow where the operator has not published it yet ("not held"); the price for 23 of the 29 places (15 have no organised day-ahead market, 6 need a license, 2 are MISO's, paused).
- **Until window B's files land** the page is its title and one box that says "not built yet".

## 2. Energy equities on the price board: `https://erw-flame.vercel.app/board#equities`

- Open the address. **You should see** the board as it was, and a new group at its foot, "Energy equities". Press its title to open it.
- **With window A's files as they stand today you should see 30 rows that each say "not held yet".** Put the mouse on one: the reason is there (SEC EDGAR refuses the ERW's contact string, so no company is put in a segment; no price source has terms that let the ERW keep daily share prices).
- Once a row holds a value: its latest value, its date, its change over a day, a week, a month, a year and the year to date, and a small trend line. Pressing the row opens `/equities` on that series.

## 3. Energy equities, the page: `https://erw-flame.vercel.app/equities`

- Open the address. **With today's files you should see** a dashed box under "The line" that says "Companies, indices and segment lines: license needed", then "Energy prices": WTI crude oil as a line over the last year (89.53 USD per barrel on 17 November), and a table of 12 energy prices with each one's latest value, its date under it, and its changes. Uranium says "monthly" under Day and Week; four power prices say "license needed" or "paused".
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
- Press "Show answer" under Question 1. **You should see** "The ERW forecast 3,012.92 MW, the operator's 1,178.26 MW: 2.56 times", the computation in one line, and the steps that name the rows of the file.
- Put the mouse on any figure. **You should see** the file it was read from and the path inside it.
- Open `https://erw-flame.vercel.app/learn/problems`. **You should not see** this set in the list: it waits for you.

What is real and what is not:

- **Real, from window B's file `site/data/predict/scores.json`:** every figure. Each is read by its key when the page is drawn, so the answers move when the file is rebuilt.
- **It takes no side.** For Texas the operator's forecast has the smaller error in every question that sets the two side by side (5.86 percent against 2.39 over the whole backtest; 3,012.92 MW against 1,178.26 over the last two years). For California the ERW forecast's is the smaller (4.09 percent against 4.68). The set writes both as the file holds them.
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
- **Whether the days after tomorrow belong on `/forecast`,** and where. Today (row 57): under "Tomorrow", demand only.
- **Whether the peak's table should also be in "Every place".** Today: drawn for the place or the two places chosen.
- **Whether the forecast's problem set joins the listed sets.** Today: it waits on its own page, in no list and no edition.
- **Whether a problem set that shows the ERW forecast scoring worse than the operator's in Texas is wanted as it is.** Today: written as the file holds it.
- **The Chart and Table switch of the site's charts is 22 px tall** on every page (24 is the least for a finger). Today: left.

## What waits on others

- **Window A's desk:** landing rows 54, 55, 56 and 57 (each at its newest head).
- **Window B:** the line "with the weather known" and the fourth method are in its contract and in none of the 29 files on main yet. The page has the method's words; the line is not drawn until a file holds it.
- **Window A:** data requests 571 to 574 in `docs/state/data_requests_done_line.md` (the list's last close and changes; the board rows' other cells; the board's older row; what the built files carry beyond the contract's text). And the two rulings its own work waits on: the SEC's contact string and a price source.
- **Window B:** nothing asked. Its contract and files were enough.
