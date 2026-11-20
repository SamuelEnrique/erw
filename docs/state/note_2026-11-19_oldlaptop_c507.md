# Note: chain 507 on the old laptop, 19 November 2026 (the audit finished, the findings review page, problem sets, the tour)

Chain file: https://github.com/SamuelEnrique/erw/blob/main/queue/done/507-day-19-november-oldlaptop-findings-review-page-problem-sets.md. Sessions 8900 to 8904. Progress: https://github.com/SamuelEnrique/erw/blob/main/docs/state/progress_c507.md. Model spend USD 0.00.

## The audit's final counts (549 drafts)

- Passed 361, passed after a fix 78, not checked 95, held (internal table) 13, withdrawn 2.
- **Withdrawn today:** `state-crude-share-crude-ak`: it counted Alaska twice (the North Slope inside the Alaska total); Alaska once is 3.09 percent of US crude in 2025, the draft said 6.13. The hunt's code is mended so a rerun cannot repeat it.
- **Mended today:** the two power-plant-against-citygate gas drafts now say they are a mean of monthly gaps, not EIA's annual gap (Nebraska 2024: 1.82 against EIA's 0.34). No figure changed.
- **Already known?** 411 drafts answered: 71 new as far as found, 205 known in part, 135 known (about 50 of them only repeat a publisher's own headline). 29 passed drafts still wait: the session's web-search allowance ran out twice (it refills at about 100 searches an hour).
- **Of the forty on the sheet:** 4 new as far as found, 20 known in part, 16 known; six (numbers 23, 24, 27, 31, 32, 34) only repeat a publisher's own figure and now say so on their entries.
- Waiting for the data machine: 48 drafts on hourly tables and 47 on FERC 714 (requests 557, 558); West Virginia's gas price table (560).

## What `/internal/findings` now shows (branch `wip/8900-findings-audit`, landing row 54)

- Each draft's audit beside it: verdict, the four checks with their reasons on hover, already known with who printed it, second route, tables and license, the Stata and Python files.
- The sheet of forty opens first in its order: sentence, chart, figure, what would make it wrong, a publisher's own figure where it is one, the do-file to read or save.
- Filters (family, verdict, reader, already known, ruling, a search) and the count of each verdict held at the top.
- Approve is stopped, with the reason, on a not-checked, held or withdrawn draft, in the button and in the server.
- The database list stopped at 500 of 616 drafts: migration 039 (request 559) lets the page read them all; until then the sheet's five missing drafts are drawn from the audit.
- Waiting for a browser: reads 423 to 428.

## The four new problem sets (branch `wip/8901-problem-sets`, landing row 56)

- https://erw-flame.vercel.app/learn/problems/who-trades-with-whom
- https://erw-flame.vercel.app/learn/problems/storm-across-the-country
- https://erw-flame.vercel.app/learn/problems/under-the-ground-and-in-the-wind
- https://erw-flame.vercel.app/learn/problems/where-energy-goes
- Every figure read from the file the page draws, checked by the site's value check; the replication matches all 113 figures. The fifth set (your own balancing authority) waits for its files. A teacher's dated copy waits for request 561. Browser reads 431 to 436.

## The tour's new stops (branch `wip/8902-tour`, landing row 55)

- After the ruled seven: every region of the grid with the balancing authority map, a storm across the country (Elliott), demand in every region, who trades with whom, the resource map. Energy by industry and energy per AI query are written and held back until their pages land. Browser reads 429 and 430.

## What waits for Samuel (default taken in each)

- Your Stata run of the forty do-files: nothing is approved until you run and click.
- Whether a reproduction that reruns the draft's own script should still count as "passed" (the Alaska case shows it checks the arithmetic, not the method). Default: the word kept, with the publisher reads as the second reader.
- Whether the six sheet findings that repeat a publisher's headline keep their places. Default: kept, each marked.
- Large figures in the new sets show two decimals by the site's one display rule. Default: kept.
- Whether tour stop 8 should open Tennessee directly. Default: it opens `/grid` and says which region to pick.
- Whether the energy-by-industry set stays listed before `/industry` lands. Default: listed, linking its method page.
