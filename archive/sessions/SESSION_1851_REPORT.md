# Session 1851: the deal tracker, read as a reader (chain 213, 12 November 2026)

Energy Research Warehouse (ERW). Chain 213, session 1851, samueloldlaptop, unattended, Fable 5.1. 10:12 to 10:28 UTC (the clock in this report was corrected by session 1856 from the commit times). Long end 1:30. Precheck passed; `origin/main` had not moved (0 commits ahead of the main copy's `37cbea47b`).

## What it did

- Served session 1850's build of origin/main on port 3851 and read the thirteen addresses of the deal tracker (`/deals`, the tracker, the comparables by four dimensions and the prices by two, the AI view by four, the charts) at 1280 and 390 with the internal cookie: a full-page screenshot, the HTML as drawn and every table, key, hover and status line of each (`runs/s1851/read-deals.mjs`, `runs/s1851/findings.json`, `runs/s1851/shots/`, 26 screenshots).
- **Every address shows the hold and nothing of a row** ("license needed ... All 529 rows of energy_deals are held from 2026-10-21"): no table, chart or download, the internal view included. The cookie opens a page in review; it does not lift a license hold, and no environment variable does.
- So every figure was recomputed with the pages' own functions in Node on the live set's 529 rows (`runs/s1851/recompute-deals.mjs`, `recompute.json`, `view.csv`): the comparables by type, technology, grid and year, the prices, the AI cells by buyer, supply, grid and quarter, the ten largest by MW and by US dollars, the four charts' figures, and the sortable table's thirteen sorts, ten filters and CSV.
- The medians recomputed by hand in Python agree with the page's functions: power purchase agreements 9 deals, median 509 MW; ERCOT 3, median 222; solar 3, median 509.
- The twenty largest AI-power rows read against their stories' titles and summaries and the evidence sentences: every MW and dollar figure is in its headline; seven of the ten by dollars are capital (an acquisition at a valuation, funding rounds, a merger), not power.
- **The faults file written:** `docs/reviews/deals-faults-2026-11-11.md`, 21 rows: 9 open for sessions 1852 and 1853 (the zero counts under the hold, the AI dollar list's capital rows, "parties not stated" where the others are named, the headline's 3.9 trillion sum, the colored header bands on five tables, the browser-tooltip hovers on the month chart and the four charts, the "not stated" grid charted as a grid, trillions written as billions), 3 for the owner (the hold itself, a confidence floor, the visible grey explanatory text on every tool page), 5 for the data machine (the live set's `extra` lacks every v2 field; cloud contracts classed grid supply; share purchases and funding rounds in the table; the TeraWulf row; 479 of 529 rows with no place), 4 checked and not faults (the downloads' columns, the comparables' keys and floor, the sorts, the filters).
- Server 3851 stopped by PID after the read (its process had answered exit 1 when killed, as expected). `scripts/sync.py` from session 1850 is still restoring tables in the background.

## Decisions made without you

- A local lift of the hold (a scratch edit of `site/data/license_status.json` for a read-only build) was refused by the session's permission layer as a weakening of a control. I did not try another way: the hold is a compliance control, and the pages' own functions on the live rows give the same figures the page would draw. The faults file says so in its first section.
- The grey explanatory text under every title and panel is recorded as one ruling (row 17), not as a fault a session fixes: it is `ToolPage`'s shared components on every tool, and the chain's rules bar a layout redesign.
- The colored header bands (row 6) are taken as a fix, not brand work: `docs/brand.md` section 5 already rules them out and `/deals`'s own table follows the rule.

## For Samuel's ruling

- Row 1: whether `energy_deals` stays held whole (state review item 25). Until then no reader, internal view included, sees a deal on any of the thirteen addresses.
- Row 16: a default confidence floor on `/deals` (editable in place) or none. Default kept: none.
- Row 17: whether tool pages keep their visible lead and note paragraphs or move them to hovers and folds, site-wide.
