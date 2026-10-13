# Session 228 report: "What a datacenter pays" answers its four questions

13 October 2026, from 02:34 UTC, unattended, on the old laptop (`samueloldlaptop`, a code machine). Branch `wip/213-datacenter-layout`, merged with `main` first, pushed, **not landed** (the chain prompt: Samuel reviews from screenshots). Model spend USD 0. Pulls: none from a publisher; the live set in Supabase read with the public key. No warehouse data written. No em dash in anything written.

## Read these first

The four answers for the default load (ERCOT, the North load zone, a flat 100 MW load, real time), as the page states them:

- **What will it pay?** Unchanged: "A flat 100 MW load at LZ_NORTH in ERCOT, buying real time, paid USD 33.73 per MWh over the last twelve months, USD 29.55 million in all: USD 0.0684 per GPU-hour for power alone." Every number of the section, of the results table and of the chart is identical before and after (`docs/brand/review-228/numbers_before_after.txt`).
- **Will the power be there?** "Over the last twelve months, Oct 2025 to Sep 2026, the price at LZ_NORTH in ERCOT was at or above USD 1,000 per MWh in 4 hours: January 2026 (4), between 07:00 and 22:00 US Central standard time. A flat 100 MW load paid USD 446,175 in them. Scenario A runs flat, in every hour." With scenario B set flexible (off in the 100 most expensive hours), the page adds that B was off in 3 of the 4 and avoided USD 306,942.
- **How clean?** "At ERCOT's monthly average, the power this load used over the last twelve months carried 303.14 kg of CO2 per MWh, 265,548 tonnes a year for 100 MW. Over the 776 hours held hour by hour (2026-09-07 to 2026-10-09), its own hours carried 346.71 kg per MWh against the grid's 346.71 on average. By year, ERCOT's consumed electricity went from 414.04 kg per MWh in 2019 to 314.26 in 2025 (the years with at least ten months held)." The window's three ways: flat 346.71, flexible 346.71 (off in none of those hours), shifting 334.82.
- **How soon?** "By ERCOT's own report of 19 June 2026, 8,927 MW of large load was approved to energize and 3,900 MW was observed running at the non-simultaneous peak; the approved figure grew by 2,053 MW since the report of 28 May 2025. New submissions by 13 March 2026: 137 requests, 140,000 MW. No wait is estimated: ERCOT publishes none." Beside it: 8 proceedings and orders on large loads in motion for ERCOT in the public dockets held.
- **Every new number carries a check key** (`dc|<address>|<stat>`, 57 distinct on the default page) and `check-values` recomputes each from its own read of the same tables and the page's own files: 461 of 461 across the three cost-of-power pages. The figures are in the two downloads (`months.csv`: the scarce hours and the grid's intensity of each month; `tables.csv`: the tables `scarce_hours`, `carbon` and `large_load`) and the Stata do-file and Python mirror rebuild them (the mirror run: `runs/session228/mirror.out`).
- Screenshots before and after, 1280 and 390 px: `docs/brand/review-228/`.

## What each answer reads, and how it is computed

All three: `site/lib/datacenter/answers.ts` (pure arithmetic, no import, as `finance.ts`), the reads at its end (`readAnswers`: the caller hands over a reader of one Supabase table, so the page, `check-values` and the downloads read the live set each their own way and compute once). The page's `model.ts` computes the three ways of running with `monthsRuled` (flat; the load's own flexible way, else the form's default of 100 hours off; the load's own shift, else the form's 20 percent) and hands them over. `docs/methods/datacenter_pays_algorithm.md`, sections 4.15 to 4.17.

1. **Will the power be there?** From the page's own price files (the same hours as "What will it pay?"), over the last twelve months: the hours whose price is at or above USD 1,000 per MWh, the sum of their prices times MW (what a flat load paid), the hours by month and by clock hour in the grid's standard time, and for each way the scarce hours its weight was 0 in and what it avoided against a flat MW (the flat sum less its own sum of price x weight). The level: the cap on an incremental energy offer in every FERC market (Order 831); in ERCOT a price above it comes from its scarcity pricing. One level for every grid (decision 2). The operator's own notices where a table holds them: CAISO's `caiso_grid_emergencies`, counted in the twelve months and the table's last date said (it runs to 30 April 2025); no other grid's notices are held as a table, and the page says so.
2. **How clean?** From `carbon_intensity_monthly` and `carbon_intensity_hourly` (variable `intensity_demand`, kg CO2 per MWh of consumed electricity, the ERW's from EIA-930's CO2 estimates), for the grid's balancing authority. The last twelve months at the monthly average: each month's energy per MW of the way times the month's intensity, over the months with an intensity (11 of the 12 for ERCOT: the monthly table lacks one month of 2025), and the tonnes a year at that rate on the year's whole energy. Hour by hour: the live set holds the hourly table's last 35 days; over the hours in which the price and the intensity are both held (776), each way's own-hours intensity is the sum of weight x intensity over the sum of weights, the grid's mean beside it. By year: the mean of the months held, with the count. `eia930` tables were not needed: the intensity tables are derived from them.
3. **How soon?** From `ercot_large_load_status` (every row: approved to energize, observed non-simultaneous and simultaneous peaks, new submissions), one report a day; the latest with an approved figure, the change from the newest report a year or more before it (else the earliest held), and the table of every report. The rules a large load must meet: the count of proceedings and orders in motion for the grid in the public dockets held (`large_load_rules` through the site's `rules.json`, as the block "Rules in motion" counted them), the newest named; the rows are in the download.

**Which grids have no public figure for question 4:** CAISO, NYISO, ISO-NE and SPP (and MISO and PJM, which the page does not open). Each gets the one line "<grid> publishes no figure of large load waiting or energized that the warehouse holds as a public table, so none is stated here, and no wait is estimated", with the rules line under it. `datacenter_queue_positions` is not in the live set and `license_status.csv` flags it "license needed" for three of its operators, so it is not read; `large_load_statements` and `large_load_waits` are internal and are not read.

## Checks, with exit codes

None piped; outputs under `runs/session228/`.

| Command | Exit | Result |
|---|---|---|
| `scripts/precheck.py --what "session 228"` | 0 | 6 of 6; on duty until 13 October 18:34 UTC |
| `git merge --no-edit origin/main` | 0 | `66b55db6` |
| `runs/session228/probe.py` (the live set's tables) | 0 | hourly intensity 33 days, monthly whole, daily 97 days; `ercot_large_load_status` loaded; `datacenter_queue_positions` and `large_load_rules` not loaded; CAISO's notices to 30 April 2025 |
| `npx tsc --noEmit`, eight times | 2, 2, 0, 2, 2, 0, 0, 0 | the failures: two duplicate names, a null, a missing field, each fixed |
| `node scripts/try-datacenter-answers.mjs` (the answers outside the page) | 0 | the figures above, 0.7 s |
| `python site/scripts/write-datacenter-carbon.py` | 0 | `erw_2026_datacenter_carbon.csv`: 87 months, 776 hours |
| `python site/public/datacenter/erw_2026_datacenter_replication.py` | 0 | the same figures as the page: 4 hours, USD 446,175, 303.14, 265,548, 346.71, the years |
| `npm run build`, three times | 0, 0, 0 | no "statement timeout" line |
| `python -m unittest` on the ten modules that read the datacenter page, twice | 0, 0 | 214 tests OK |
| `runs/session208/capture.mjs` before and after, 1280 and 390 | 0 ×6 | the results table's 25 lines identical in every raw value; "What will it pay?" identical but one word (the downloads' line names session 213) |
| `CHECK_VALUES_PAGES=/cost-of-power node scripts/check-values.mjs` (`MSYS_NO_PATHCONV=1`), five runs | 0, 1, 1, 1, 0 | the first before the page was in its list (345 of 345, none of the new keys read); then 28 failures of text against raw (the figures were rounded for display: fixed, the text is now lib/format's `shown` or USD short, decision 5); then 2 of `ll:approved_change`, the page's cached read an hour behind the live set, which gained three reports during the session (decision 6); the last 461 of 461 |
| `node scripts/check-datacenter-scenarios.mjs`, three runs | 1, 0, 0 | the first: my own list of the download's tables; then 96 of 96 twice (the final build) |
| `curl` of `months.csv` as a visitor | | 404 "in review" |
| `scripts/freeze.py status` | not run | nothing deployed |
| Whole suite in a clean copy | not run | not landed; run it before the landing |

## Decisions made without you

1. **The three answers stand between "What will it pay?" and "Which option is better?"**, in the prompt's order, so that the page's four questions come first and the two of the decisions after. The scenario block still sets the headline of the first; the new answers read A's way of running and show B's beside it where B runs the other way.
2. **One scarcity level for every grid, USD 1,000 per MWh**, the FERC offer cap (Order 831), with ERCOT's scarcity adders the only thing above it there. The alternative, each grid's own cap (ERCOT's USD 5,000, CAISO's hard cap USD 2,000), would make the count mean different things. "Close to short" is not a second level: the operator's notices stand beside the count where a table holds them (CAISO's, which ends in April 2025, so none fall in the twelve months), and the count's level is said on the page.
3. **The flexible load that "steps off in those hours" is the page's own rule**, decided before each hour from day-ahead prices (section 5.1), not a load told the scarce hours: the default flexible way was off in 3 of the 4, which is what it would have avoided. A load off in every scarce hour would avoid the flat figure; the table says what a flat load paid, so that reading is there too.
4. **The carbon basis is consumed electricity** (`intensity_demand`: generation plus imports less exports), what a load in the grid uses, not the grid's generation. The last-twelve-months figure is at the monthly average because the live set holds hourly intensity for 35 days only (`live_set.yaml`, the recent window); the own-hours difference between the ways is shown over that window, which the prompt's "flat against flexible against shifting" needs hour by hour. For a whole year hour by hour the hourly table would have to come from Redivis or the data machine's files; for the ruling.
5. **The figures' text is `shown` (a whole number, else two decimals) or USD short**, as `check-values` reads them against the raw value; USD and tonnes for the size are rounded to the unit in the stat itself, so that the page's raw value, its text and the recomputation are one definition. The page writes every figure through one component that reads `statOf` by the stat's name.
6. **The page's read of the live set is cached an hour** (`lib/supabase.ts`, `rest` with `HOURLY`), as the battery page's is. `ercot_large_load_status` gained three reports (24 April, 21 May and 19 June 2026) while this session ran (the data machine loaded them: the probe at 02:40 UTC saw rows to 26 March), so the page showed the March report while `check-values` read June. The build's fetch cache (825 MB, `site/.next/cache/fetch-cache`) was removed and the server restarted; the page then showed June and every value matched. The headline above is June's. The committed site file `data/large_load_status.json` and `coverage.csv` still say March: the page no longer reads that file for this answer.
7. **No brand restyle**, as instructed; the new sections use the page's own components (`HeadlineRow`, `HeadlineNumber`, `ToolTable`).
8. **`check-values` now reads `/cost-of-power` and `/cost-of-power?run=hours`** (the page's own view, flat and flexible), where until now it read only the "Grid by grid" view; the two addresses carry 98 of the 461 values.
9. **The carbon CSV is a site file written from the live set** (`site/scripts/write-datacenter-carbon.py`, provenance in its header), beside the data machine's hourly export, so that the do-file and the mirror can rebuild "How clean" from files a reader downloads. The do-file has not been run (Stata is not on this machine); the mirror follows it step for step and prints the page's figures.

## For Samuel's ruling

1. The three answers, from the screenshots: their words, their three numbers each, their tables.
2. The scarcity level (decision 2): USD 1,000 for every grid, or each grid's own cap, or a second "close to short" level (the page's tight hours of demand stand in the download).
3. The hourly carbon window: 35 days from the live set, or a year's hourly intensity for the page from Redivis or the data machine (a year file beside the price files).
4. "How soon?" for the four grids with no public figure: the one line and the rules count, or the datacenter tracker's own figures beside it.
5. The trend's two ends in the "How clean?" sentence (the first and last years with at least ten months held) against the table's every year.
6. `data/large_load_status.json`, the page's older site file of ERCOT's reports, now three reports behind the live set: rebuild it on the data machine, or retire it (the page reads Supabase for this answer).

## To finish

- The landing, after the battery's and the generator's: `git switch -c task/228-datacenter-answers wip/213-datacenter-layout`, `git merge origin/main`, the whole suite in a clean worktree, `npm run build`, the before snapshot as its own command, `git push`, the after snapshot and the comparison (the page is in review: 0 differences expected on the 25 pages).

## The prompt

Session 228 of 12 October, evening: "What a datacenter pays answers its four questions. Where: branch wip/213-datacenter-layout, merged with main first. Do NOT land. No brand restyle. Goal: the page answers the four questions an AI company asks of a site, each with a computed answer for the load the reader describes: 1. What will it pay? (exists; unchanged, every number identical) 2. Will the power be there? ... 3. How clean? ... 4. How soon? Only from public-licensed tables ... Each new answer follows the existing pattern ... Every new number appears in check-values and traces to a table and a query. Add the new figures to the page's CSV download and to the Stata do-file and Python mirror. Done: check-values passes with the new numbers; every existing number unchanged; screenshots at 1280 and 390 to docs/brand/review-228/ (before and after); report; push the branch. Then say SESSION DONE and stop (do not run the queue)."
