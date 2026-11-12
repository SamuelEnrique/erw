# Session 1875: the policy monitor, read as a reader (chain 214, 12 November 2026)

Energy Research Warehouse (ERW). Chain 214, session 1875 (chain 213's step 1857), samueloldlaptop, unattended, Opus 5.5. 20:24 to 20:40 UTC, while session 1874's gate ran. Long end 1:30. Precheck passed for 1874 (on duty until 2026-11-13 12:19 UTC); no freeze.

## What it did

- Read `/policy` and `/policy?view=monitor` from session 1857's capture of the built site (`runs/s1857/`: the HTML at 1280 and 390 with the internal cookie, the full-page screenshots, `findings.json` with every table, hover and `data-check` key). `site/app/policy/` and the libraries it reads have not changed between that build (`37cbea47b`) and origin/main, so the capture is the page as it would build now. The clicks (filters, sorts, the expanding row, the CSV) were run through the page's own functions in Node; no browser was run in this session.
- Twenty actions' reads checked against their source text across EPA, NRC, DOE, FERC, BOEM, BLM, PUCT, CPUC and IRS (5 impact sentences, 15 plain reads): fifteen right; one states more than its text (BOEM's "held in 2023"); four right against their own document but drawn under another document's title. The texts from www.federalregister.gov only (robots.txt read first, 11 requests, the ERW user agent), kept under `runs/s1875/texts/`. One read-only query of the live set's `events` (anon key) to match each read to its document.
- **The faults file written:** `docs/reviews/policy-faults-2026-11-11.md`, 31 rows: 16 `open`, 7 `data machine`, 1 `ruling`, 7 `not a fault`.
- The worst three in plain words: the month-ahead calendar says "No dated step in these thirty days" while it holds 5, hidden by the significance floor (row 6), and the date extraction misses most deadlines (row 7, the desktop's: 61 of 1,495 records hold a step); 37 of 48 "next steps" drawn are already past (row 16); at 390 px the page is 938 px wide (row 1).
- The `open` rows, for sessions 1876 onward: 1 (390 px overflow), 2 (filter counts of all records, not the rows left), 3 (sector keys in lower case), 4 (the past week's window past the file's last document), 6 (the calendar under the floor), 9 (dates broken across lines), 14 (the "; it bears on table" clause in every impact sentence), 16 (past steps drawn as next), 17 (the next step's hover without document or key), 19 (sorting by figure across units), 21 (a row opens on mouse click only), 22 (raw keys in the open row), 23 (293 rows above the charts), 26 (a partial November drawn as a month), 28 (monthly sums of unlike figures), 29 (the CSV leaves out the plain read).
- For the desktop's chain: rows 5 (the file not rebuilt since 6 November), 7 (the date rule misses "on or before 5:00 p.m. Eastern Time on <date>" and the schedule notices), 12 (40 of 290 plain reads describe an older document than the row's title), 13 (EPA's proposed rescission and its final partial repeal merged in one record), 15, 18, 25.

## Decisions made without you

- The read was made from session 1857's capture rather than a new build, since the gate held the build lock and the page's code had not changed; the clicks were run through the page's functions rather than a browser (chrome-devtools did not connect in this window). Session 1876 builds the fixes and reads them on the built page.
- The Texas Governor's releases were left out of the twenty: their pages are not in the Federal Register and no further host was requested.

## For Samuel's ruling

- Row 31 is deals row 17 again (the grey note under the table), not restated.
