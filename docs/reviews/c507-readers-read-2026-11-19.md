# The reader's read of chain 507's work (19 November 2026)

Energy Research Warehouse (ERW). Chain 507, part E, on samueloldlaptop: each page read as its reader would, on the pages drawn to HTML with the site's own code (this machine cannot build the site); what only a browser can settle is a browser read in `docs/state/browser_reads_wanted.md`. Every gap is a numbered row; a fault is fixed at its cause with a test, or said to wait and for whom.

## Part B: Samuel approving ten findings in a sitting (`/internal/findings`)

Five cases, read on `wip/8900-findings-audit`: (1) open the page and take the sheet's first ten in order; (2) run the first one's Stata; (3) a sheet draft whose sentence the audit mended; (4) one of the five sheet drafts beyond the database's 500-row list; (5) a withdrawn draft found by search.

| # | Case | What the reader meets | State |
|---:|---|---|---|
| 1 | 3 | The sentence on the page is the mended one, but the chart picture's line under its title still carries the old words (7 of the forty, 74 drafts in all): the two disagree and nothing said why | fixed at `88b1464dd`: a line under the picture says so, the audit's change on hover; the render test checks every sheet draft (a line exactly where the change names the picture). Drawing the pictures again is the data machine's (the hunt's builder) and is for Samuel's ruling (chain 506's) |
| 2 | 2 | The do-file reads whole tables; the panel names them, but not where a whole copy is, and the site's download holds only the live set's window of some tables | fixed at `88b1464dd`: the do-file line's hover says what it reads, where the whole tables are, and that the draft's own files hold a shorter do-file on its yearly CSV. No link to the download was added: it would hand a partial table for the hourly ones |
| 3 | 4 | The five sheet drafts the list does not return are drawn from the audit with their state taken as a draft; a click on Approve may answer "no such draft" | waits: migration 039 (data request 559); the page says so on hover beside each |
| 4 | 1 | Ten approvals in a row: each block's state changes in place; on the next visit the approved ones move to "Ruled", still carrying their sheet number | no gap |
| 5 | 5 | The withdrawn Alaska draft: Approve drawn disabled, the reason beside it, the withdrawal's one line at the draft's top | no gap |

## Part D: a first-time visitor on the tour (`/tour`)

Five cases, read on `wip/8902-tour`: (1) the first page; (2) stop 8, the grid's regions; (3) stop 9, Elliott across the country; (4) stops 10 and 11, demand and trade; (5) stop 12, the resource map.

| # | Case | What the reader meets | State |
|---:|---|---|---|
| 6 | 1 | Twelve stops, about eight minutes; the ruled seven first; the menu line says the same | no gap |
| 7 | 2 | Stop 8 opens `/grid`, the same address as stop 4: the visitor lands on ERCOT and must pick a region from the list as the stop says | for Samuel's ruling, default kept: the stop opens `/grid` because `/grid?region=ten` is not an address the route check reads; adding it to `site/scripts/check-routes.mjs` and pointing the stop there is a one-line change after a build confirms it |
| 8 | 3 | Elliott's page: "The whole country" and its three blocks, as the stop quotes | no gap on main; check-tour on a build is browser read 429 |
| 9 | 4 | `/demand` and `/supply` are the data machine's pages today (chain 505): a heading the stop quotes may be renamed | the test and check-tour fail when a quoted heading goes (browser read 429) |
| 10 | 5 | The resource map is at `/map`, titled "The project map": the stop's title says "What is under the ground and in the wind" and its line says the page's own name | no gap |

## Part C: a teacher setting a problem set for Monday

Five cases, read on `wip/8901-problem-sets` from its own report and its node test's drawn pages: (1) choose a set on the index on Friday; (2) print the teacher's copy; (3) read the resource set's answers aloud; (4) the trade set's question on 2019, where the two sides disagree on the direction; (5) the energy-by-industry set, whose page is not on main.

| # | Case | What the reader meets | State |
|---:|---|---|---|
| 11 | 1 | The four new sets have no dated edition: a figure may move between Friday and Monday when the data machine rebuilds a page file | waits: data request 561 (a dated edition with the nine sets) |
| 12 | 2 | No teacher's copy of the four yet (it is drawn from an edition); the live page shows the worked answers behind each question's click | waits: data request 561 |
| 13 | 3 | Figures shown to two decimals however large: 15,244,926.85 MWh a year, 315,802,780.06 dry metric tons a year | for Samuel's ruling, default kept: `lib/format.ts` `shown()` is the site's one display rule and `check-values.mjs` reads it; a rule by size would move every set's figures |
| 14 | 4 | Mid-Atlantic says 2,437,201 MWh went to Tennessee in 2019; Tennessee says it sent 6,612,970 MWh the other way: the question asks which way each said the power ran, and the answer says both | no gap: the disagreement is the lesson the set names |
| 15 | 5 | `/industry` is not on main, so the set links its method page; the figures carry their page file on hover and come in the set's CSV | for Samuel's ruling, default kept: the set stays listed; its page link is added when `/industry` lands (as the tour's held stop) |
