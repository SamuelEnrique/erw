# The energy deal tracker: the model audited as a hostile expert would

Session 10215, 26 November 2026, chain 710 (part D), the old laptop. Read as an M&A analyst at an energy fund, who would quote its counts and medians in a memo and wants to find them wrong, and as a PPA buyer, who would read it for what power sells for and who is signing. In the form of `docs/reviews/queues-model-audit-2026-11-26.md`.

- Nothing changed on main but this file and its folder of evidence (`docs/reviews/deals-model-audit-2026-11-26/`). No table written, no lock taken, no default moved, no model called, no request to any service.
- Each finding's test is on its own branch, `wip/audit-deals-<n>`. Branches that change only words are for landing (the rows at the foot); a branch whose fix would move a figure carries the test only and is not for landing.
- Not repeated: the faults read of 11 November (`docs/reviews/deals-faults-2026-11-11.md`) and the six items of the method note's section 12 that wait for the owner (the hold, a floor of "Sure", hover tips, the grid a story names in the three views, the folded Vistra loan's 433 MW, whether a deal must be energy's); the audit of the stored records of 6 November (`docs/reviews/deals-audit-2026-11-06.md`); the tracker audit's finding on the news window of the datacenter extractor (`docs/reviews/tracker-model-audit-2026-11-26.md`, finding 2), whose deal-side twin is finding 1 here. Where a measure here sizes one of them, it is cited, not refiled.
- **The hold.** `energy_deals` is held whole ("license needed") since 21 October 2026, so a visitor today sees the hold's sentence and the row count (583) on every view, the decisions, and the companies tab. Every figure below is what the pages draw once the hold allows, computed with the pages' own functions on the warehouse's rows, as the replication does. No row of the held table is printed in this file or its folder: only sums and counts.

## In short

- **The arithmetic is right.** An independent restatement written from the method notes (`docs/methods/deal_tracker.md` sections 2 to 7, `docs/methods/energy_deals.md`) with the standard library alone gives every figure of every view from the warehouse's 583 rows: 1,108 of 1,108 keys equal to the pages' own functions run on the same rows, with no gap at all (`compare.out`). The default views: November 2026, 32 deals, 2,501.5 MW from 5 that state it, 16 percent tagged AI; the tracker 578 deals (5 folded pairs), 35 state a size, 40,297 MW, none a price, 296 a value in US dollars; 14 median sizes; 212 tagged AI power, USD 3.06 trillion stated by 122 of them.
- **The window has holes the page misdates, and the as-of date is nowhere (finding 1).** The first tab says "since 2025-10-01"; 42 of the 583 rows are of January to April 2025. The chart note blames "June to September 2025"; May 2025 is empty too (13 of 370 stories scored). And the extraction stopped on 12 November 2026: no story has been scored since (2,107 stories held after the newest deal, none scored), so "Deals in 2026-11: 32" is four dated days, and "scored daily since 23 September 2026" no longer holds. Fixed in words.
- **The companies tab shows what the hold withholds (finding 2).** The decisions say every view draws "nothing of a row"; the companies tab, drawn under them, lists 541 parties of the held deals (`energy_companies`, not held) with each one's deal types, technologies, the place a deal states (195) and the stories' links. Fixed in words; whether those rows are held with the deals is for Samuel's ruling.
- **The AI view's dollar sums add unlike things (finding 3).** Decision 4 says no sum is drawn across kinds of deal and the sums are by the kind of supply; the default view sums by buyer, and by grid and quarter too, so 15 buyers' cells add a compute contract, a raise and an acquisition (USD 1.13 trillion), every quarter but one mixes kinds, and one acquisition of USD 1.25 trillion is 40.9 percent of the USD 3.06 trillion. The register's doubtful pairs add USD 55 billion twice; rumored talks are USD 235 billion. The tracker's note also counts "a valuation" among the values, which decision 4 excludes. Fixed in words; the figure is for Samuel's ruling.
- **Smaller, all words.** The tracker's fold says AI power is what "the model tagged as power or infrastructure for AI": 160 of the 212 tagged deals name no energy word, 75 are capital (finding 4). The AI view's grid note reads a named grid first; the code reads the state alone (finding 5). The comparables' medians by type set a 43.5 MW solar PPA beside a 3,600 MW nuclear one, and a median of three is one deal's figure (finding 6).
- **What an analyst's own number would hold:** a price per MWh (0 of 578 state one) and a price per MW (8 deals state USD and MW, no acquisition among them); a US-only count (38,147 of the 40,297 MW name no country); deals above a confidence floor (at the Roundup's 0.7: 281 deals, 21,705 MW, against 578 and 40,297); one sum per kind of deal.
- **Six branches fix words and move no figure (1 to 6); one shows a figure for ruling (7).** No data request: every measure was made from files on this machine. Needs the key: scoring and extracting the stories since 12 November 2026 and the unscored months.

## The ground: each file and what it does

| File | What it does |
|---|---|
| `site/app/deals/page.tsx` | The page `/deals`: three tabs (deals, tracker, companies) and three views under the tracker (`?view=comparables`, `ai`, `charts`); the first tab's lead, the hold, the month's three cells, the table, the citation; the decisions and downloads under every tab |
| `site/app/deals/DealsTable.tsx`, `site/lib/dealsview.ts` | The first tab's table: every row of `energy_deals` (folded pairs not folded), its filters, sort, row details, the CSV, Python and Stata downloads; `rowOf`, `monthBlock` (the month's count, MW and AI share) |
| `site/app/deals/v2/view.tsx`, `site/lib/deals2.ts` | The tracker tab: the register's pairs folded (`fold`), the panel and its bracket counts, the summary sentence, the "most stories give no size" block, three headline numbers, deals by month, every deal, the folds "How a deal gets here", "Rows that were one deal", "What this does not tell you" |
| `site/app/deals/comparables/view.tsx`, `PlaceDeal.tsx`, `deals2.ts` (`comparables`, `medianOf`, `priceCells`, `place`) | Comparables: by type (the default), technology, grid or year, the deals, those stating a price and a size, and each median from three; the disclosed prices of PPAs and offtakes; a reader's deal placed against them |
| `site/app/deals/ai/view.tsx`, `site/lib/dealsai.ts` (`supplyOf`, `aiCells`, `largest`) | The AI-power view: the tagged deals by buyer (the default), kind of supply, grid or quarter, with MW and USD summed where stated; the ten with the most MW and the ten with the most USD, capital deals left out |
| `site/app/deals/charts/view.tsx`, `dealsai.ts` (`mwByQuarter`, `pricePoints`, `aiShare`, `topParties`) | Four charts: MW by quarter and kind of supply, the prices stated, the AI share of MW by quarter, the ten counterparties with the most MW |
| `site/app/deals/capital/page.tsx`, `site/data/capital.json`, `warehouse/derived/capital_page.py` | Capital flows (tool 11): under the hold, the row count alone (583, built 16 November) |
| `site/app/deals/Held.tsx`, `Decisions.tsx`, `site/lib/decisions.ts` (`DEAL_TRACKER_DECISIONS`) | The hold's sentence (the catalogue's row count); the 13 decisions with default and source, and session 465's 17 choices |
| `site/app/companies/view.tsx` | The companies tab: `energy_companies` (public), 21 researched rows and 541 seeded from the deals' parties |
| `site/data/deal_duplicates.json`, `warehouse/deals/duplicates.csv` | The register: 8 pairs, 5 folded and 3 doubtful (the two files agree) |
| `warehouse/deals/extract.py`, `fields.py`, `dedupe.py`, `deal_parties.py`, `crosscheck.py`, `counterparties.py`, `public_rows.py` | The extraction (scored stories of nine sectors, significance 5 or more, by cluster), the v2 fields, the join of a later story, the cross-check flags, one name a company |
| `docs/methods/deal_tracker.md` ("the method note"), `energy_deals.md`, `deal_counterparties.md` | The tool's note (views, rules, keys, decisions, what waits) and the tables' notes |
| `replication/deals/` | `fetch_rows.py` (reads the live set: not run here), `replicate.py`, `replicate.do`, `page_figures.json` of 16 November (1,123 of 1,124) |
| Read from the main copy, never written | `energy_deals.csv` (583 rows, extracted 12 November 2026 22:08 UTC; the coverage file's row), `energy_deals_evidence.csv` (counts of words only), `news_stories.csv` (26 November), `energy_companies.csv` (25 November) |

## How every number here was computed

- **The default views:** `/deals` drawn on 26 November 2026 (the month 2026-11), `?tab=tracker` with no choice, `?view=comparables` by type, `?view=ai` by buyer, `?view=charts`, `/deals/capital`, each as drawn once the hold allows.
- **The page's own code on the rows:** `to_rows.py` writes the CSV's rows as the live set would serve them (the loader's rule for events: the event columns, every other column in `extra`, an empty value left out); `site/scripts/deal-tracker-figures.mjs` (the replication's runner of the pages' own functions) computes every key from them (`node --import ./scripts/tsx-register.mjs`).
- **The restatement:** `restate.py`, standard library only, from the notes' rules; where a note leaves a word list open, its choice is written beside it. `compare.py` sets the two side by side.
- **One rule at a time and the claims:** `measures.py` (window, stages, sizes, the tag, the grid, repeats, the evidence's words counted, the companies), `measures2.py` (the AI view's dollars, the comparables' floor, a floor of "Sure"), `measures3.py` (the AI view's dollar sums cell by cell).
- **The live set is newer than the CSV**: the method note read 590 rows on 16 November; the warehouse's CSV and its coverage row hold 583, the newest dated 12 November. The rules are restated to the digit; the live page's figures are of its own rows.
- Copies of the scripts and their printouts, with every key that names a party or a deal taken out (`sanitize.py`): `docs/reviews/deals-model-audit-2026-11-26/` (written to run from `runs/c10215/` of a worktree). The rows are not copied.

## The arithmetic re-done

| Figure | The pages' functions | Restated | Gap |
|---|---|---|---|
| The table: rows; state MW; state USD; flagged; "Sure" from and to | 583; 36; 298; 14; 0.3 to 0.95 | the same | 0 |
| The month's cells (2026-11) | 32 deals; 2,501.5 MW from 5; 16 percent AI | the same | 0 |
| The table's filters: AI yes and no; price disclosed; MW from 500; 14 kinds; 9 stages | 213 and 370; 0; 17; capital 158, M&A 154, other 76, fuel supply 58, PPA 32, compute capacity 31, project finance 20, offtake 16, gas buildout 12, storage 10, SMR 7, behind the meter 5, nuclear restart 4, transmission 0; signed 190, announced 139, none 98, closed 82, rumored 60, cancelled 10, financed 4 | the same | 0 |
| The tracker: deals; folded; state MW, MW; price; another unit; USD | 578; 5; 35, 40,297; 0; 2; 296 | the same | 0 |
| The tracker's brackets: types; tool 6's kinds; grids; years; statuses; storage; AI; with a state, a grid | PPA 37, offtake 26, project finance 25, acquisition 150, tolling 0, other 340; gas 12, behind the meter 5, SMR 5, restart 1; ERCOT 11, PJM 10, MISO 9, SPP 2, CAISO 1, ISO-NE 1; 2025 92, 2026 486; signed 189, announced 138, closed 85, rumored 59, cancelled 10; 10; 212; 52, 34 | the same, and every technology and every party named twice | 0 |
| Deals by month, 23 bars | 2025-01 11 ... 2025-04 9; May to September 2025 0; 2025-10 17 ... 2026-09 59, 2026-10 162, 2026-11 32 | the same | 0 |
| The summary sentence | "The ERW holds 578 deals from the news it reads, dated January 2025 to November 2026. 35 of them state a size, 40,297 MW in all, and none states a price." | its counts the same | 0 |
| Comparables, four dimensions | by type: M&A 150, equity raise 84, other 91, fuel supply 59, debt 55, PPA 37, joint venture 31, offtake 26, project finance 25, lease 12, behind the meter 4, SMR 3, restart 1; median MW PPA 348 (of 12), other 810 (6), M&A 892 (3), behind the meter 450 (3), offtake 50 (3); 13 medians in all; no median price | the same | 0 |
| Disclosed prices | 0 priced PPAs or offtakes | 0 | 0 |
| The AI view | 212 tagged; by supply capital 103, compute 29, grid 25, other 24, gas 13, nuclear 10, renewables and storage 8; MW gas 6,070, grid 6,312; USD capital 2.19 trillion, compute 405 billion, other 278 billion; by quarter 2026-Q1 1.66 trillion ...; the two lists of ten | the same, every buyer's cell too | 0 |
| The charts | MW by quarter and group, the deals without MW; AI share 2025-Q1 100, 2026-Q1 47.4, 2026-Q2 48.3, 2026-Q3 0, 2026-Q4 23.2; ten counterparties | the same | 0 |
| Capital | 583 rows (held) | the file's 583 | 0 |

- **1,108 of 1,108 keys equal, the largest gap 0** (`compare.out`). The restatement read US dollars as `usd` else `dollars` and a price as `usd_per_mwh` else `price`, as the note says; the tracker's code reads `dollars` and `price` alone. On these rows the columns agree, so no figure differs; a later row with `usd` and no `dollars` would be missed by the tracker's views and not by the table (not a branch: no row does it).
- **The published replication** reads the live set (`fetch_rows.py`), which this machine does not call: not run. Its runner of the pages' functions is the one used above.
- **What a visitor sees today**: on every view the hold's sentence ("All 583 rows of `energy_deals` are held from 2026-10-21") and on the companies tab the 562 companies. No em dash in any drawing.

## One rule changed at a time

Each line changes one choice and keeps every other. The base is the default views of the 583 rows of 12 November.

| Choice the pages make | The other choice | Worth | Said on the page? |
|---|---|---|---|
| Every row, at any "Sure" (owner's item 2) | a floor of 0.7 (the Roundup's) / 0.6 | tracker 578 to 281 / 435 deals; MW 40,297 to 21,705 / 35,197; AI-tagged 212 to 99 / 163; the month 32 to 23 / 30 deals, AI share 16 to 17 / 13 percent | yes (decision 10) |
| A median from three deals that state the figure | from five / ten | 13 medians to 8 / 3; by type, M&A's, offtake's and behind the meter's go at five | yes (decision 6); that a median of three is one deal's own figure, no (finding 6) |
| USD summed by buyer, grid and quarter on the AI view | only by the kind of supply | 15 of 82 buyer cells, 3 of 4 grid cells and 6 of 7 quarter cells that state USD add two kinds or more (USD 1.13, 3.04 and 3.06 trillion) | decision 4 says the sums are by the kind of supply (finding 3) |
| Rumored and cancelled deals in the sums | left out | AI USD 3.06 to 2.82 trillion (rumored 235 billion, 10 deals); MW unchanged (no rumored or cancelled deal states MW) | "rumored" is a stage shown per row; not beside a sum |
| The register's doubtful pairs as two | folded | AI USD 55 billion lower (a programme of USD 200 billion and a part of it of 15; one round of talks at 40 and 50) | yes, the fold lists them |
| The folded pair keeps the earlier row (owner's item 5) | carries the later row's figure | the Vistra loan: +433 MW (40,297 to 40,730), MW stated by 36 | yes (decision 3) |
| The first tab lists every row | the folded deals, as the tracker | 583 to 578; no November row is a folded duplicate (they are of January, May, August and October 2026) | yes (decision 3); the lead says "a deal reported by several stories is one row" |
| The grid from the state alone in three views (owner's item 4) | a grid a story names first | one AI-tagged deal moves from "not stated" to PJM | the AI view's note says a named grid first (finding 5) |
| Every scored story of nine sectors at significance 5 or more | (not a choice: what was scored) | May to September 2025: 1,885 stories, 13 scored, 2 eligible, 0 deals; October to December 2025: 790 of 1,935 scored; June to August 2026: 863 of 1,819; November 2026: 1,022 of 3,371, none after 12 November; September to November 2026: 3,371 to 11,914 stories a month against 351 to 656 before, and 253 of the 578 deals | partly, and misdated (finding 1) |

## Each claim against the code

| Claim, or question | Where | What the code does | Verdict |
|---|---|---|---|
| Announced against closed | the stage column, the panel's status, "Whether a deal closed" | Each row's stage or status as a story states it; sums add every stage | **Right as stated** for MW: the 35 deals that state MW are signed (24), announced (3), closed (3) or of no status (5), none rumored or cancelled. The dollar sums of the AI view add rumored deals (USD 235 billion): see finding 3 |
| "MW announced in 2026-11" | the month's cell | the MW of the deals dated in the month, any stage (announced 900, signed 709.5, none 892) | Loose: "announced" is the date's name, not the stage. Not a branch |
| A deal's value when undisclosed | every sum, decisions 2 and 4 | never estimated, never zero; a sum is over the deals that state it, the count beside it | **Right** |
| One deal reported by several stories | the first tab's lead; the tracker; decision 3 | the extraction's `same_as`, the code's join (same type, same two parties, 30 days), the register (5 folded, 3 doubtful); the first tab lists every row | **Right as stated** in the decisions. No pair of rows left unfolded shares a type and two parties within 30 days, or a MW and a party within 60 (`measures.py`). The doubtful pairs' dollars are summed twice on the AI view (finding 3). The first tab's lead ("one row") holds for the extraction, not for the 5 pairs the register folds, which the first tab lists as two (said in decision 3) |
| A PPA's MW against MWh against dollars | the size column, the flags | `mw`, `mwh` and `usd` kept apart, each with its span; 3 rows state MWh, 1 both; the cross-check flags a headline's figure the row lacks or contradicts (14 rows) | **Right**. No MWh is added to a MW sum |
| Price per MW comparables and their mix of assets | the comparables | No price per MW is drawn. A median is of every technology and country of the group | 8 deals state both USD and MW, 0.57 to 35 million USD per MW, none an acquisition: no such comparable could be drawn. The medians' mix is finding 6 |
| Currency and the dollars' year | decision 4; the column tips | Another currency is never converted; US dollars as stated, of the year of the deal (nominal) | **Right as stated**. 10 deals whose evidence names another currency state no USD and are in no dollar sum; 2 keep a USD figure their story gives beside it (session 2285). The dollars' year is not said; the deals span 23 months, so nominal against real is under 4 percent: not a branch |
| Dates: announced against signed, against the first story | the month's note, decision 11 | the announced date where a story states it (4 rows), else the first story's day (579, 99.3 percent) | **Right as stated** ("The first story's day for almost every deal") |
| The news window and its gaps | the first tab's lead, the month's cells, the tracker's chart note, the method note section 8 | the scored stories of nine sectors at significance 5 or more | **Finding 1** |
| How a deal is called "AI power" | the tracker's fold; the AI view's lead; decision 8; the table's column tip | `ai_power` as extracted, with `fields.ai_of` since session 2232 (a named AI party or a datacenter load) | The AI view, the tip and decision 8 are **right**; the tracker's fold is not (**finding 4**) |
| The grid | the panel ("by the state the story names"), decision 7, the AI view's note | `STATE_GRID[state]` in the tracker, comparables, AI view and charts; a named grid first in the table only | The AI view's note says a named grid first (**finding 5**) |
| Internal or licensed rows reaching a public figure | the hold; decision 13; the companies tab | Every deal view draws the hold and the row count; the downloads say "held"; capital's file holds the count alone; the companies tab draws `energy_companies` (public), 541 of whose 562 rows are the held deals' parties | **Finding 2** |
| The as-of date | the month's cells, the tracker's headline ("January 2025 to November 2026") | the newest deal is dated 12 November 2026; no story scored since | Not said (**finding 1**) |
| "Most stories give no size and no price" | the tracker | 35 of 578 state MW, 0 a price per MWh, 2 a figure in another unit, 296 USD | **Right** |
| "a purchase price, a financing or a valuation" | the tracker's third headline note | decision 4 and the table's tip: a valuation is not the deal's | Contradicts the decision (**finding 3**) |
| The ten with the most USD: "Power and infrastructure deals" | the AI view | the tagged deals whose kind of supply is not capital; a capital deal whose technology names nuclear, gas or a renewable is under that supply (decision 9) and listed | **Right as stated** by decision 9; two of the ten state no buyer and no seller, one a joint venture of the kind capital |
| "A deal counts for each of its two parties" | the counterparty chart | buyer and seller, one name a company | **Right**; the bars add to more than the MW stated, as said |
| The AI share by quarter | the charts | the tagged deals' MW over the quarter's MW stated | **Right**; 2025-Q1's 100 percent is one deal of 5,000 MW, 2026-Q3's 0 is of 7,520 MW from untagged deals: the hover gives the counts |
| "This page is in review", the hold's sentence | every view | as drawn | **Right** |

## What an M&A analyst's or a PPA buyer's own number would hold that this does not

| Item | Size | From |
|---|---|---|
| A price per MWh | 0 of 578 deals state one; the stories held are a title and a short summary | the tracker's counts |
| A price per MW for acquisitions and projects | 8 deals state USD and MW (debt 2, joint venture 1, offtake 1, other 1, PPA 3), 0.57 to 35 million USD per MW; no acquisition states both | `measures.json`, `usd_per_mw` |
| The US alone | country stated for 108 of 578 deals; of the 40,297 MW, 2,150 name a country (US 2,100); state stated for 52 | `measures.json` |
| A floor on doubtful rows | 143 deals below 0.6 ("doubtful that there is a transaction"), 297 below 0.7, holding 18,592 of the 40,297 MW | `measures.json`, the owner's item 2 |
| One sum per kind of deal | the AI view's default sums dollars by buyer across kinds (finding 3) | `measures3.json` |
| Deals beyond the news | none from filings, press releases or FERC's contract filings; `/contracts` holds the latter and the tracker links it | the method note, section 8 |
| An even window | the unscored months and the days since 12 November need the key | `measures.json`, `window` |
| Energy deals only | 160 of the 212 tagged deals name no energy word in technology or asset; about 51 of the older rows are not energy's (the method note, section 10) | finding 4; the owner's item 6 |

## Findings, largest effect first

| # | Severity | Finding | Effect | Fix | Branch |
|---|---|---|---|---|---|
| 1 | Medium | The window: "since 2025-10-01" against rows from January 2025; "June to September 2025" against May to September; no story scored since 12 November 2026, unsaid | 42 rows outside the stated window; November's 32 deals are four dated days; the monthly chart is a chart of what was scored | words | `wip/audit-deals-1` |
| 2 | Medium | The companies tab lists the held deals' parties with their deal types, technologies, places and links, under a decision that says nothing of a row is drawn | 541 rows | words; the hold of those rows for ruling | `wip/audit-deals-2` |
| 3 | Low | The AI view sums dollars across kinds of deal by buyer, grid and quarter, against decision 4; doubtful pairs and rumored talks in the sums; "a valuation" among the tracker's values | 15 buyer cells (USD 1.13 trillion), 6 of 7 quarters; one deal is 40.9 percent of USD 3.06 trillion | words; the figure for ruling | `wip/audit-deals-3`; `wip/audit-deals-7` |
| 4 | Low | The tracker's fold: AI power "tagged as power or infrastructure for AI or datacenters" | 160 of 212 tagged name no energy word; 75 capital, 29 compute | words | `wip/audit-deals-4` |
| 5 | Low | The AI view's grid note reads a named grid first; the code reads the state | one tagged deal in "not stated", not PJM | words | `wip/audit-deals-5` |
| 6 | Low | The comparables' medians mix technologies and countries, and a median of three is one deal's figure | PPA 348 MW over 43.5 to 3,600 MW; M&A's 892 is one gas plant | words; a floor of five for ruling | `wip/audit-deals-6` |
