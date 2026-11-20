# The "whole country" views of `/supply`, read as their reader (started 19 November 2026)

Energy Research Warehouse (ERW). Chain 503, part E (session 8460, the old laptop). The form is part B of chain 304: five real cases a named reader would bring, each taken start to finish on the page; every gap a numbered row; every fault fixed at its cause with a test. Then the done line for the new views: the method note, the replication, a cross-check against a published figure, the decisions. The views are session 8430's: net imports by month and by neighbour, who trades with whom, the generation mix by region (`site/components/supply/Country.tsx`).

## The reader and the five cases

The reader: **the energy lead of an AI lab, choosing between two regions for a 300 MW campus to be energized in 2028**, writing the page of a siting memo that says how each region balances itself: what it generates from, how much it leans on its neighbours and in which months, and whether the two ends of a tie tell the same story. Real places, real years:

1. **Tennessee beside the Carolinas, 2025** (`https://erw-flame.vercel.app/supply?region=ten&b=car&year=2025#whole-country`): each region's net imports over the year and from which neighbours; the flow between the two as each side filed it, and how far the two filings stand apart.
2. **The Southwest beside the Northwest, 2024** (`https://erw-flame.vercel.app/supply?region=sw&b=nw&year=2024#whole-country`): what the Southwest sent to California in July and August 2024; the Northwest's exchange with Canada month by month, where only the United States' side files.
3. **Texas alone, 2023 and then 2025** (`https://erw-flame.vercel.app/supply?region=tex&b=none&year=2023#whole-country`, then `year=2025`): how little crosses Texas's ties with the Central region and with Mexico; the share of solar in August 2023 beside August 2025.
4. **The Mid-Atlantic beside the Midwest, 2025** (`https://erw-flame.vercel.app/supply?region=mida&b=midw&year=2025#whole-country`): the two regions where datacenter load grows fastest; each one's net imports by neighbour, the pair between them in "Who trades with whom", and the shares of gas, coal and nuclear by month.
5. **Florida beside the Southeast, December 2022** (`https://erw-flame.vercel.app/supply?region=fla&b=se&year=2022#whole-country`): Florida has one neighbour of the lower 48; what it took from the Southeast in the month of Winter Storm Elliott, and whether the year's row, the Southeast's own row and the pair's row give the same flow.

For each case the questions are the same: can the reader get the answer without leaving the page, without a figure that contradicts another page, and without a word they would not know?

## State on 19 November 2026

| Part | State |
|---|---|
| The five cases read on the page | done (session 8490) on the real files, the page drawn with the site's own code at each case's address (`site/scripts/supply-read-page.mjs`): every question of the five is answered on the page; see "The five cases on the real files" below. Rows 16 to 27 below are what the read found; six faults fixed at their cause with a test, the rest data requests, browser rows or rulings. (Session 8460: waited for the files.) |
| The method note | done: `docs/methods/supply_and_trade.md`, "The whole country" (session 8430), completed by session 8460 with the rules the replication needed (see "What the note lacked" below), and by session 8490 with "On the real files": the count, the four changes of the read, the do-file and the cross-check in short. |
| The replication | done on the real files (session 8490, after the merge of origin/main with the files, `af1962719`, and after every change of the read): **43,552 of 43,552** figures over 27 files (13 trade, 13 mix, 1 matrix). On the fixtures (session 8460): 33,132 of 33,132. |
| The same flow in two files | done (session 8490): 375 of 375 pairs' years agree with the trade files within 0.05 GWh; read to the MWh, 385 of 385 equal. |
| The Stata do-file for the five headline figures | written (session 8490): `replication/supply/replicate_regions.do`, the five figures with their expected values at its top, from the real files (+8,309.7 GWh; +91.1, +94.2 and 0.0 percent; 2,877.5 and +0.3 GWh; -7,769.7 GWh; 14.1 percent of 11 months). Not run: Stata is not installed on this machine. It needs Stata 16 with Python (the files are JSON). |
| The cross-check against a published figure | done (session 8490): "The cross-check" below, one table with its sources and the hosts' robots files and terms. Texas against ERCOT's own fact sheet and monthly overview agrees within 0.6 points or percent; against EIA's Short-Term Energy Outlook, solar is 14 percent higher here; trade with Canada and Mexico differs from EIA's Form EIA-111 by definition. The Hourly Electric Grid Monitor was not read: it is an application with no figure on a page to read, and it draws the same Form EIA-930 that the replication already checks. CAISO was not asked (the region of California is wider than CAISO and its 2024 holds 11 months). `www.ferc.gov` and `www.nerc.com` were not asked. |
| The decisions | on the page as hovers inside the section, each with its default and its source, checked on the real files (session 8490): the 10 percent of a large gap (on every percent's hover), the regions and the year drawn first (on the hover beside the region choice). The page's own decisions block is not changed (the pin holds it). All wait for Samuel's ruling in session 8430's report; rows 8 to 10 and 24 and 26 below add more. |

## Gaps found before any file (from the section as drawn on the fixtures)

| # | Where | The gap | What was done |
|---:|---|---|---|
| 1 | A neighbour's row for Canada or Mexico; a pair with either (cases 2 and 3) | The other side's report, the gap and the percent read "not held yet", and the hover said only that the file holds no report. The reader waits for a figure that will never come: no balancing authority of Canada or Mexico files Form EIA-930. | Fixed: each of those hovers now says so (`abroadWhy` in `site/components/supply/Country.tsx`), in the year's table, the month's hover and the pairs. Test: `site/scripts/test-supply-regions-8460.mjs`. |
| 2 | "Balancing authorities, pair by pair" and the partners (cases 2 and 4) | A code the index of the regions does not list (the index lists the authorities of the lower 48 only; the pairs also carry authorities across the border) read on hover "its name stands here once the index is on the site", also with the index on the site. | Fixed: with the index on the site such a code says the index does not list it, and its missing report says why. Its name still cannot be given: data request 324. Test: the same file. |
| 3 | "Generation mix by month" beside "Net imports by month" (every case) | A month of the mix is the region's own local month; a month of net imports is EIA's Eastern month. For the Northwest or California the two months do not hold the same hours, and nothing on the mix said which month it was. | Fixed: the hover of "Net generation, GWh" names the region's local month and the file's time zone, and the hover beside the heading says both. Test: the same file. |
| 4 | The mix table (cases 3 and 4) | A month's eight shares need not add up to 100, and no hover said why: the file holds an hour when its sources add up to its net generation within 5 percent. | Fixed: the hover beside the heading says it. Test: the same file. |
| 5 | The fold "Balancing authorities, pair by pair" | "Balancing authority" was defined nowhere in the section; a reader from outside the industry does not know it. | Fixed: the fold's first head says what one is. Test: the same file. |
| 6 | "Who trades with whom" in a year held in part (2018 from July; the running year) | The pairs' table says nowhere on its face that the year is not whole. The table of neighbours does ("10 of 12"). The contract's matrix holds no count of months; the hours the builder writes stand only on a report's hover. | Not a fault the page can close: data request 325 (the months a pair's year holds). When the file carries it: a column "Months held" in the pairs' table, one change in `Country.tsx` with a test. |
| 7 | "Who trades with whom", the year | The hover does not say which hours make a pair's year. The trade months are EIA's Eastern months; the contract's section 7 does not say what a year of the matrix is. | Data request 326 (one line in the contract). Then the head's hover names it. |
| 8 | Tennessee's row for the Carolinas, the Carolinas' row for Tennessee, and the pair's row (cases 1 and 5) | One flow stands in three places, from two files. On the fixtures they are made by unrelated rules; on real files they must agree, or the reader holds a contradiction inside one section. | The replication sets them side by side on request (`--same-flow`); it runs when the files land. Nothing to fix before. |
| 9 | Every table (cases 1 and 4) | No table can be sorted (the site's table has no sorting on any page). The pairs stand in EIA's order of codes by session 8430's choice, so that no table is a ranking; with every pair of balancing authorities in one fold, finding the widest gap means reading every row. | For Samuel's ruling. Default taken: EIA's order, no sorting. The other choice: a click on "Gap, percent" that orders the pairs by it (an order of pairs by how far two filings stand apart, not of regions by what they gave or took). |
| 10 | "not held yet" on the face where nothing is to come: the border's other side (row 1), and the percent of a pair whose two reports are both zero | The page's own words for a missing value (its browser check refuses "not held" without "yet"). The hover now says why at the border; the face still promises a figure. | For Samuel's ruling. Default taken: the page's words stay. The other choice: "not filed" at the border and a blank with "no percent of zero" on hover for the pair at zero. |
| 11 | The mark of a large gap | It is set on the percent before rounding, so a percent shown as 10.0 can stand without the mark. | Said in the method note. For Samuel's ruling with the 10 percent itself (session 8430's report). Default taken: before rounding. |
| 12 | The tables of a year (case 3) | Two regions stand side by side; two years do not. August 2023 beside August 2025 means choosing the year twice and remembering a figure. The charts carry every month, so the shape is there; the figures are not. | Left: a second year is a new choice of the address and a new column in every table, a view of its own for the page's next session. |
| 13 | The two charts of net imports side by side (cases 1 and 4) | A neighbour takes its colour from its place among that region's neighbours, so the Southeast can be one colour in Tennessee's chart and another in the Carolinas'. | Needs a browser to judge: browser read row 404. Not changed here. |
| 14 | The month table at 390 px (a region with five or more neighbours) | The table scrolls inside its frame, as the standard asks; scrolled right, the month's name leaves the screen (the site's table fixes no column). | Needs a browser: browser read row 405. The site's shared table, not this section's. |
| 15 | The charts' box under the pointer and their "Table" | Both are drawn in the browser from the same arrays as the month tables; the replication cannot read them. | Browser read row 406: three figures read off a chart against the month table. |

## Gaps found on the real files (session 8490)

| # | Where | The gap | What was done |
|---:|---|---|---|
| 16 | "Who trades with whom" (row 6) | The pairs' table did not say how many months a pair's year holds. The real files carry `months_held` and `months_in_year` (data request 325) and a pair's year is the sum of EIA's Eastern months (326). | Fixed (commit `e4ae80769`): a column "Months held" ("9 of 11"), its head's hover saying what a pair's year is. Test: `site/scripts/test-supply-regions-8490.mjs`. |
| 17 | Storage in the mix table (cases 3 and 4) | Storage is blank in Form EIA-930 before 1 July 2024 and reads exactly zero in regions with nothing filed after (the Mid-Atlantic in every month), which a reader takes for a region with no batteries. | Fixed (`e4ae80769`): the hover of Storage says when Form EIA-930 begins storage and that a zero is not a count of batteries. Same test. |
| 18 | Any table, a flow under 50 MWh (the Southwest and Central in December 2024; Tennessee's wind in 2025) | Read "-0.0" or "+0.0". | Fixed: a figure that rounds to zero reads "0.0" (the section's own formatters; the shared one is not changed, so no other page moves). Same test. |
| 19 | The mean of a pair (cases 1 and 5) | Tennessee and the Carolinas in 2025: reports of 94.2 and 91.1 GWh and a mean of 91.0, below both. The file's mean runs over the hours both reported, each report over its own side's hours; 53 of 160 pairs of regions and 240 of 1,323 pairs of authorities have a mean outside their two reports. The cell had no hover. | Fixed: the mean's hover says what it is and why it need not lie between the reports; where one side alone reported, that the mean is that report. Same test. |
| 20 | The percent of a gap (cases 1, 2 and 4) | The Northwest and California in 2024: 9,622.6 GWh beside 7,817.0, a gap of 4.7 GWh, 0.1 percent: California filed 8,000 of the year's 8,784 hours. A reader comparing the two reports sees a fifth apart; the page says a tenth of a percent. The hours stood only on each report's hover. | Fixed: when the two sides' hours differ, the percent's hover ends with each side's hours and that the reports can differ by more than the gap. Same test. |
| 21 | The mix table, a month the file leaves out (cases 3 and 4) | The builder writes a month only when 90 percent of its days are complete; the table drew only the months held, so Texas's December 2025 and the Mid-Atlantic's January and February 2025 were nowhere, and the year's "11 months" was the only trace. | Fixed: a month of the file's span that it does not hold stands in its place as a row, not held yet, with the rule on hover; the year's row names the months left out on hover; a year with no month held says the rule. Same test. |
| 22 | The mix files: months left out (cases 2, 3 and 4) | Months missing from the file between its first and last: the Mid-Atlantic 57 (September 2020 to February 2025 and two more), the Southwest 40 (all of 2023 and 2024), Florida 35 (most of 2018 to 2021), California 22 (eight of the ten months of 2026), the Northwest 11 (five of 2025), the Southeast 16, Tennessee 11, Central 6, the Midwest 3, the Carolinas 1, Texas 1 (December 2025, between two held months). The case 4 reader cannot read the Mid-Atlantic's mix before March 2025. | Data request (hand-back): for each region, which balancing authority's hours keep each month out, and whether one authority's gap is to keep a whole region's month out. Nothing filled. |
| 23 | The Carolinas and the Mid-Atlantic, 2025 (cases 1 and 4) | The Mid-Atlantic filed 7,098 of the year's hours of this flow, the Carolinas 8,735; the face reads "12 of 12" months, since a month counts when either side filed in it. | Data request (with row 22): is the gap in the Mid-Atlantic's filings in Form EIA-930 itself or in the builder. The hours are on the reports' and the percent's hovers. |
| 24 | "Months held" beside a report filed for part of the year (row 23) | "12 of 12" can stand beside a report of 81 percent of the hours. | For Samuel's ruling. Default taken: the months on the face, the hours on hover (the page standard: hover tips only). The other choice: the share of hours on the face beside the months. |
| 25 | The gap's sign in two tables (case 5) | One flow, Florida from the Southeast in 2022: the gap reads -11.2 in Florida's table and in the Southeast's (each region's own report less the other's, in its own sign of net imports) and +11.2 in the pairs (the sender's report less the receiver's). Each hover says which. | No fault: the same 11.2 GWh. Left as it stands. |
| 26 | The year's shares of a region with a month left out (case 3) | Texas's solar share of 2025 is 14.1 percent of 11 months; December, with less sun, is not in it. The year's row says "11 months" and now names the month on hover. | For Samuel's ruling. Default taken: the share over the months held, the count on the face. The other choice: no share for a year with a month left out. |
| 27 | The new rows of row 21 at 390 px and the mean's hover | Ten cells of "not held yet" in a row, and a hover on a figure that had none. | Browser read rows (hand-back). |

## The five cases on the real files (session 8490)

Each drawn at its address with the site's own code on the files of `af1962719` (no build, no server).

1. **Tennessee beside the Carolinas, 2025.** Tennessee's net imports from all neighbours: +8,309.7 GWh, all from the Midwest (+16,681.5), while it sends to the Mid-Atlantic (-5,399.9), the Southeast (-2,877.7) and the Carolinas (-94.2). The flow between the two: Tennessee reports -94.2 GWh, the Carolinas +91.1 (their own sign); over the 8,734 hours both filed, the gap is 0.0 and 0.0 percent. Answered on the page; rows 19 and 20 found here.
2. **The Southwest beside the Northwest, 2024.** The Southwest sent California 1,263.5 GWh in July and 1,531.7 in August (its own report). The Northwest's net imports from Canada month by month: -567.6 in January to -107.3 in July, -7,769.7 over the year, only the United States' side filed (the hover says so). The Southwest's mix holds no month of 2024 (row 22); the Northwest's lacks November (row 21).
3. **Texas, 2023 and 2025.** Net imports from Central: +1,236.3 GWh in 2023, +662.5 in 2025; from Mexico -382.2 and -364.5 (Texas's side only). Solar's share in August: 7.8 percent in 2023, 15.0 in 2025. December 2025 is not in the file (rows 21, 22, 26).
4. **The Mid-Atlantic beside the Midwest, 2025.** The Mid-Atlantic: -30,398.2 GWh from all neighbours, its largest sends to the Midwest (-21,410.5) and New York (-19,448.6); the Midwest +21,663.6. The pair: the Mid-Atlantic sent 21,410.5 GWh by its report, 23,939.5 by the Midwest's, a gap of 11.1 percent, marked large. The mix by month runs from March 2025 for both (January and February stand as rows not held yet, rows 21 and 22).
5. **Florida beside the Southeast, December 2022.** Florida took +59.0 GWh from the Southeast in December 2022 (the Southeast's report of the same month: -64.4). The year's flow is the same in Florida's row, the Southeast's row and the pair's (2,944.5 and 2,978.2 GWh); the gap's sign differs by table and each hover says why (row 25).

## The cross-check (session 8490)

Hosts read, each robots file and terms first, on 19 November 2026. No personal address was sent; no host of `warehouse/metadata/paused_sources.csv` was asked.

| Host | Robots (for the paths read) | Terms (on automated reading) | Read or not |
|---|---|---|---|
| `www.eia.gov` | `Allow: /`; nothing disallowed under `/electricity/` or `/todayinenergy/` | `/about/copyrights_reuse.php`: public domain, reuse with acknowledgement; nothing on automated reading | read: Electric Power Annual Table 2.14; Today in Energy 66464 and 67005 |
| `www.ercot.com` | disallows `/content/gridinfo`, `/misdownload` and others; `/files/docs/` not disallowed | `/help/terms`: public contents may be reused unmodified; prohibits use that harms the site's performance; nothing on robots or scraping | read: Monthly Operational Overview, September 2025; Fact Sheet, October 2026 |
| `www.ferc.gov`, `www.nerc.com` | refused on 19 November | | not asked |
| CAISO | | | not asked: the region of California is wider than CAISO's ground and its 2024 holds 11 months |

| Figure | Ours (the page's files) | Theirs | Difference | Why they differ |
|---|---|---|---|---|
| Texas, shares of 2025 by source | gas 41.2, wind 23.2, coal 13.0, solar 14.1, nuclear 8.5 percent of net generation, 11 months | ERCOT Fact Sheet (October 2026), "2025 Energy Use": gas 41.1, wind 23.6, coal 12.9, solar 13.9, nuclear 8.6 percent | within 0.4 points each | Ours lacks December 2025; ERCOT's "energy use" adds net DC-tie imports and a storage adjustment. The PDF's text also carries an overlaid 45.1 and 24.3 beside gas and wind and a footnote that puts solar in Other; the set that adds to 100 is the one used. |
| Texas, net generation, September 2024 | 41,224.3 GWh | ERCOT Monthly Operational Overview, September 2025: 41,003 GWh | +221.3 (0.5 percent) | Form EIA-930's sum of eight sources against ERCOT's settlement energy. |
| Texas, net generation, September 2025 | 43,934.0 GWh | the same report: 49,979 GWh, said to be 7.3 percent above 41,003 | -6,045 against the figure; against 7.3 percent above 41,003 (43,996), -62 (0.1 percent) | ERCOT's own text does not agree with itself; no figure is taken from it. |
| Texas, solar, January to September 2025 | 52,433.8 GWh | EIA, Today in Energy 66464 (24 October 2025, from the Short-Term Energy Outlook): 45 TWh | +7.4 TWh (ours 16 percent above) | EIA's figure is utility-scale solar in its outlook's own count; Form EIA-930 carries what ERCOT reports by fuel, which ERCOT's own share (above) matches. Not resolved here. |
| Texas, wind, January to September 2025 | 85,752.7 GWh | the same article: 87 TWh | -1.2 TWh (1.4 percent) | The same two counts. |
| Texas, wind and solar, January to September 2025 | 37.0 percent of net generation | the same article: 36 percent of demand | 1 point | Net generation against demand. |
| Texas, solar, 2025 | 63,460.5 GWh over 11 months | EIA, Today in Energy 67005 (16 January 2026, Short-Term Energy Outlook): 56 BkWh for the year | ours higher by 7.5 TWh with a month fewer | As above; the outlook's 2025 was in part an estimate when written. |
| The lower 48's net imports from Canada | 22,296.4 (2023), 11,580.9 (2024), 6,009.4 (2025) GWh, the United States' side | EIA, Electric Power Annual Table 2.14 (Form EIA-111): 14,840.8, 9,858.0, 8,458.9 GWh | +7,455.6, +1,722.9, -2,449.5 | Form EIA-111 counts power crossing the border; Form EIA-930 the interchange of balancing authorities, filed hour by hour. |
| The lower 48's net imports from Mexico | -1,028.4 (2023), -1,616.9 (2024), -1,335.6 (2025) GWh | the same table: 4,063.4, 3,959.5, 3,899.2 GWh | opposite signs | The same difference of form; the likeliest reason, not confirmed here, is plants in Mexico scheduled inside a United States balancing authority (imports in EIA-111, generation in EIA-930). |

No figure was adjusted to match. For the trade views' pairs and the other twelve regions' mixes no public figure on a readable page stands against them; the Hourly Electric Grid Monitor draws the same Form EIA-930 and is checked by the replication.

## What the note lacked (found by writing the replication from it)

The replication was written from the note and the contract. Nine rules were not settled by the note as session 8430 left it; each is now written there under "The rules above, made exact (session 8460)", as the page applies it:

1. A year's percent with a neighbour is taken on three sums over the months that hold all three arrays, and is not drawn when both summed reports are zero.
2. "Large" is judged on the percent before rounding, and in the month table the mark stands on the month's own report.
3. A pair's mean is turned to the direction with the two reports; the gap is the file's value unturned.
4. A pair with no direction stands in the file's order, the first side's report first, and reads "no net flow" at a mean of zero.
5. The two counts in the folds, and that they read zero in a year the matrix does not hold.
6. What the month's hover holds beyond the face (the neighbour's report, the gap, the percent on the month's own values).
7. Which sign a figure carries (a plus above zero for a region's reports, gaps and totals; none for a pair's reports and mean).
8. The year drawn first when the files do not hold the last ended year: the newest year held before it, then the newest held; and that "built" is the newest build among the files of the two regions drawn first and the matrix.
9. A mix month's days, the year's count of months, and that the year's net generation runs over the months that hold it.

## When the files land

1. `git fetch`, then `git ls-tree -r origin/main --name-only site/data/regions`; merge origin/main into `wip/8460-supply-regions-done`.
2. From `site/`: `node --import ./scripts/tsx-register.mjs scripts/supply-regions-figures.mjs <figures.json>`, then `python replication/supply/replicate_regions.py --figures <figures.json> --same-flow`. Write the count here and in the method note; a figure that fails is read against the note's rule first.
3. Draw the page on the real files (`scripts/supply-read-page.mjs`, as session 8430's hand-back says) and take the five cases start to finish; each gap is a new row above.
4. The Stata do-file `replication/supply/replicate_regions.do` with the five headline figures at its top; the cross-check table, each host's robots file and terms first.

## On the real files (session 8490, 19 November 2026)

The data machine's page files are on `origin/wip/c501-pages` (`af1962719`), not on main: `trade/<region>.json` (13), `trade_matrix.json`, `mix/<region>.json` (13) and `index.json`, built 19 November 2026 between 12:03 and 12:16 UTC. They were copied into the worktree untracked and are not committed here (they land through the data machine). origin/main was merged into the branch first (`5a0d29749`). Later the same day the files reached origin/main (`af1962719`); the 108 untracked copies were each identical to main's by `git hash-object`, were removed, and origin/main was merged (`196673600`).

| Check | Result on the real files |
|---|---|
| `site/scripts/test-supply-regions-8460.mjs` | 20 of 20 (and after every change of session 8490) |
| `site/scripts/test-supply-regions-8490.mjs` (session 8490's faults, rows 16 to 21) | 34 of 34 |
| The section's test (`site/scripts/test-supply-regions.mjs`) | 108 of 108 |
| The pin of the page | 208 of 208 (every address byte for byte outside what was added) |
| The replication, `replicate_regions.py --same-flow` | 40,248 of 40,248 at the first read; 43,552 of 43,552 over 27 files (13 trade, 13 mix, 1 matrix) after the merge of origin/main and every change of the read |
| The same flow in two files | 375 of 375 agree within 0.05 GWh; a separate read to the MWh: 385 of 385 equal |

The data requests made before the files, read against them:

| Row | Asked | On the real files |
|---:|---|---|
| 323 | keys the builders write that the contract does not list | the trade files carry `hours_in_month` and, by neighbour, `hours_own` and `hours_their`; the pairs carry `hours_a`, `hours_b`, `hours_both`; no pair lacks a key (0 of 1,652). The contract still has to list them. |
| 324 | the names of the authorities beyond the border | `index.json` lists 81 authorities, the nine of Canada and Mexico among them with their names; every code of the pairs and the partners is in it. |
| 325 | the months a pair's year holds | every pair carries `months_held` and `months_in_year` (2018: 6; 2026: 11; never above). |
| 326 | what a year of the matrix is | the matrix's year sums equal the trade files' Eastern months to the MWh (385 of 385), so a year of the matrix is the sum of EIA's Eastern months. |
