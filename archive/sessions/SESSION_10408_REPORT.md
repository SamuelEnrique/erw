# Session 10408 report: chain 720 resumed; `/equities` on the SEC's company figures

Energy Research Warehouse (ERW). 27 November 2026, 08:39 to 09:30 UTC, the portable laptop's first window (code role), unattended. The only window on this laptop tonight.

## The resume

- **Main** was 349 commits behind origin/main with nothing of its own: fast-forwarded, nothing discarded.
- **The resume file** `721` was taken by name and the same text put back as `722`, alone, and pushed.
- **Precheck:** 6 of 6. My first run failed one check (the day's spend) because I ran it from the documents folder, which has no `.env`. That run recorded the laptop as idle; the second, from the main folder, put it on duty two minutes later, so no "ready" email follows.
- **No freeze.** Free memory at the start: 1,141 MB of 15,974 MB.
- **Rows 59, 60 and 61 have landed** (checked against origin/main).
- **Session number** 10408 was free on origin/main and on every branch.

## Equities: seen on the real files

- **The files** (built 27 November 03:23 UTC): 307 companies from SEC EDGAR, 18,555 filed periods. 243 companies have filed figures; 64 say "source needed" (foreign filers and some partnerships). Every share price, index and segment line is held: "license needed".
- **Production, as landed** (one browser run, 1280 and 390 px, six addresses a width): no sideways scroll, no "undefined". Every share price is a blank that says "license needed". The board's group has 30 rows, none with a figure, each with its reason on hover.
- **What the read found:** with a company chosen the page drew **no chart at all**. The energy price was drawn only where nothing was chosen, or laid over a share price's line, and every company's line is now a blank. The page had been built while no company existed.

## Equities: what a reader now gets (row 62, `wip/c720-equities-sec`)

- **A filed figure over time.** Revenue, net income, capital spending, debt or shares, by 3-month or 12-month periods, as a line over every period the company filed. Two new choices in the panel at the left.
- **As filed, nothing worked out.** A point is a figure for the period its filing reports. A fourth quarter that was only filed inside the year's 12 months has no point. A period filed twice (an amended form) shows the later filing's figure.
- **The newest period, on like terms.** One column for each length of period filed to that day (a 10-Q's 3 months beside its year to date), so two companies are compared on the same kind of period.
- **The energy price is back** as a chart of its own while no share price can carry it.
- **A filter** "Filed figures shown" on the table of every company.
- **A segment no SEC code holds alone** (LNG, solar, wind, storage and three more) shows its nought with the file's reason, and no longer opens an empty table.
- **Share prices stay blank,** "license needed", with the file's reason on hover. No held value is drawn.

## Checks

- **New test:** 76 checks on a fixture in the real files' shapes. The older equities tests pass unchanged (104 and 24).
- **Every drawn figure against main's files:** 2,329 pages, 1,179,547 figures, none differing. Each company's ten lines (3,070 lines, 48,019 points) computed twice from the file's rows, none differing.
- **Type check and lint:** clean. The type check found one error of mine in the new table, mended before the row.
- **The 216 test files that walk the site or name equities:** 2,891 passed, 82 skipped, 6 failed. None of the six names equities or runs a script that reads it (the chat's tests and three other pages'; three of them are known to fail on main on this laptop).
- **Built and seen:** exit 0 with 2,141 MB free. `/equities` and the board's group at 1280 and 390 px, the chart under a mouse and a finger, 381 keyboard stops each with a ring, the back button after a choice. The value check: 153 of 153.

## Three rows for the data machine (requests 578 to 580)

- **578:** the list should carry each company's newest filed period, so the table of all 307 can show and sort by revenue, income and debt. Today it can only say "shown".
- **579:** eighteen large utilities (AEP, Duke, NextEra, Southern and others) have nothing after the quarter to 31 March 2026, while 206 other companies reach 30 September. Exxon holds four periods, all of 2026: its SEC number is the new holding company's. One company's last filing is from 2016 and reads as current. EDGAR was not read from here: the pattern alone says so.
- **580:** the price board's own check of its file fails one of eight rules on main, on two held rows that carry a public heat-rate reference. No held value is in either row.

## Decisions made without you

- **The resume file's text is the chain's own block,** without the paragraph "where it stopped" that the last session added: the progress file says where it stands.
- **An amended filing's figure stands in place of the first filing's,** where the amendment holds one. The first filing's stays in the table of every period.
- **Debt and shares by "12 months"** are the figures at the period ends of the annual reports.
- **A line of one period is not drawn:** the page says "one period filed" and the figure is in the table.
- **The filed chart shows every period filed,** whatever the window chosen: the window is the price's.
- **A build was made** once memory reached 2 GB, after the tests, through the build lock.

## For Samuel's ruling

- **Which company the page opens on.** Today the list's first, ProFrac Holding (ACDC, first by ticker). A large, familiar company would say more at a glance. The page is left as it is.
- **Whether a missing fourth quarter may be worked out** as the year less its nine months. Today it is not: the page shows only what was filed.

## Needs the key

- Nothing. No model was called.

## Next

- Session 10409: `/forecast` gets a view for each output the forecast gained on 27 November.
