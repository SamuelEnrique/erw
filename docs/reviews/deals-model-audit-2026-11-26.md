# The energy deal tracker: the model audited as a hostile expert would

Session 10215, 26 November 2026, chain 710 (part D), the old laptop. Read as an M&A analyst at an energy fund, who would quote its counts and medians in a memo and wants to find them wrong, and as a PPA buyer, who would read it for what power sells for and who is signing. In the form of `docs/reviews/queues-model-audit-2026-11-26.md`.

- Nothing changed on main but this file and its folder of evidence (`docs/reviews/deals-model-audit-2026-11-26/`). No table written, no lock taken, no default moved, no model called, no request to any service.
- Each finding's test is on its own branch, `wip/audit-deals-<n>`. Branches that change only words are for landing (the rows at the foot); a branch whose fix would move a figure carries the test only and is not for landing.
- Not repeated: the faults read of 11 November (`docs/reviews/deals-faults-2026-11-11.md`) and the six items of the method note's section 12 that wait for the owner (the hold, a floor of "Sure", hover tips, the grid a story names in the three views, the folded Vistra loan's 433 MW, whether a deal must be energy's); the audit of the stored records of 6 November (`docs/reviews/deals-audit-2026-11-06.md`); the tracker audit's finding on the news window of the datacenter extractor (`docs/reviews/tracker-model-audit-2026-11-26.md`, finding 2), whose deal-side twin is finding 1 here. Where a measure here sizes one of them, it is cited, not refiled.
- **The hold.** `energy_deals` is held whole ("license needed") since 21 October 2026, so a visitor today sees the hold's sentence and the row count (583) on every view, the decisions, and the companies tab. Every figure below is what the pages draw once the hold allows, computed with the pages' own functions on the warehouse's rows, as the replication does. No row of the held table is printed in this file or its folder: only sums and counts.

## In short

- **The arithmetic is right.** An independent restatement written from the method notes (`docs/methods/deal_tracker.md` sections 2 to 7, `docs/methods/energy_deals.md`) with the standard library alone gives every figure of every view from the warehouse's 583 rows: 1,108 of 1,108 keys equal to the pages' own functions run on the same rows, with no gap at all (`compare.out`). The default views: November 2026, 32 deals, 2,501.5 MW from 5 that state it, 16 percent tagged AI; the tracker 578 deals (5 folded pairs), 35 state a size, 40,297 MW, none a price, 296 a value in US dollars; 13 median sizes; 212 tagged AI power, USD 3.06 trillion stated by 122 of them.
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
| The month's cells (2026-11) | 32 deals; 2,501.5 MW from 5 (printed "2,502", the page's whole number); 16 percent AI | the same | 0 |
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
| 1 | Medium | The window: "since 2025-10-01" against rows from January 2025; "June to September 2025" against May to September; no story scored since 12 November 2026, unsaid | 42 rows outside the stated window; November's 32 deals are four dated days; the monthly chart is a chart of what was scored | words | `wip/audit-deals-1` (`76bcdc188`) |
| 2 | Medium | The companies tab lists the held deals' parties with their deal types, technologies, places and links, under a decision that says nothing of a row is drawn | 541 rows | words; the hold of those rows for ruling | `wip/audit-deals-2` (`cc0c32314`) |
| 3 | Low | The AI view sums dollars across kinds of deal by buyer, grid and quarter, against decision 4; doubtful pairs and rumored talks in the sums; "a valuation" among the tracker's values | 15 buyer cells (USD 1.13 trillion), 6 of 7 quarters; one deal is 40.9 percent of USD 3.06 trillion | words; the figure for ruling | `wip/audit-deals-3` (`f819cf539`); `wip/audit-deals-7` (`4af4a3a28`) |
| 4 | Low | The tracker's fold: AI power "tagged as power or infrastructure for AI or datacenters" | 160 of 212 tagged name no energy word; 75 capital, 29 compute | words | `wip/audit-deals-4` (`4a1f8e8be`) |
| 5 | Very low | The AI view's grid note reads a named grid first; the code reads the state | one tagged deal in "not stated", not PJM | words | `wip/audit-deals-5` (`0330c26ed`) |
| 6 | Low | The comparables' medians mix technologies and countries, and a median of three is one deal's figure | PPA 348 MW over 43.5 to 3,600 MW; M&A's 892 is one gas plant | words; a floor of five for ruling | `wip/audit-deals-6` (`f8724525e`) |

## 1. The window has holes the page misdates, and no as-of date (Medium)

- **Where.** `site/app/deals/page.tsx`, the first tab's lead ("Energy deals reported in the news since 2025-10-01") and the month's note; `site/app/deals/v2/view.tsx`, the chart "Deals by month" ("the stories of June to September 2025 are held but not scored ... The ERW has scored the news daily since 23 September 2026"); `docs/methods/energy_deals.md` ("The page shows the deals reported since 1 October 2025"); the method note, section 8.
- **Why it is wrong.** The table's rows run from 5 January 2025: 42 of the 583 are dated January to April 2025, when every story was scored. By month of publication (`news_stories`, the extractor's own rule: scored, nine sectors, significance 5 or more; `warehouse/deals/checked.csv`): May 2025, 370 stories and 13 scored (2 eligible, no deal); June to September 2025, none scored; October to December 2025, 790 of 1,935; January to May 2026, every one; June to August 2026, 863 of 1,819; September to November 2026, the daily feed, 3,371 to 11,914 stories a month against 351 to 656 before, and 253 of the 578 deals. The scorer's last run was 12 November 2026 at 22:06 UTC and the extractor's at 22:08: the 2,107 stories held after the newest deal (12 November) are unscored. So the month's cells read "Deals in 2026-11: 32" for deals dated 4, 5, 11 and 12 November, and nothing says how far they reach.
- **The test.** `tests/test_audit_deals_1.py` on `wip/audit-deals-1`: through `lib/dealsview.ts`, the month counts what is dated in it, whatever the newest day (passes on main); the record of stories sent is in git (passes); the words tests fail on main.
- **The fix on the branch, words only.** The lead reads "since January 2025" and says the stories scored are uneven; the month's note names the newest deal held (drawn from the rows) and says no story was scored after 12 November 2026, as of 26 November 2026; the chart's note names May to September 2025 (13 of 1,885 scored), the months scored by less than half, the stop, and the newest deal; both method notes the same. No figure moves.
- **Needs the key.** Scoring the stories since 12 November 2026 and the unscored months, then the extractor (model runs).

## 2. The companies tab shows what the hold withholds (Medium)

- **Where.** `site/lib/decisions.ts`, decision 13 ("every view draws the hold's sentence and the count of rows it covers, and nothing of a row"), drawn under every tab of `/deals`, the companies tab included; the method note, section 1 and section 11; `site/app/companies/view.tsx`.
- **Why it is wrong.** The companies tab reads `energy_companies`, which `license_status.csv` does not hold (its source line is "ERW"). 541 of its 562 rows (25 November 2026) are seeded from the held deals (`warehouse/companies/seed_from_deals.py`): every buyer, seller and other party a company, with its deals' types and technologies as tags (`deal:ppa;tech:solar thermal`), the place a deal states (195 rows) and every story's link. A reader on the companies tab sees who did what kind of deal in which technology and where, with the story, under a sentence that says nothing of a row is shown. Whether that is a leak is a license question (the outlets' pages ask for permission; the rows hold no outlet text, only names, tags and links); that the sentence is false is not.
- **The test.** `tests/test_audit_deals_2.py` on `wip/audit-deals-2`: the site's license file holds `energy_deals` and not `energy_companies`, and the tab reads `energy_companies` (passes on main); the words test fails on main.
- **The fix on the branch, words only.** Decision 13 (and its line in the method note, word for word) says every view of the deals draws nothing of a row and that the companies tab, not held, shows each party with its deals' types and technologies, the place a deal states and the stories' links; its default says the same; the method note's hold paragraph counts the rows. No figure moves.
- **For Samuel's ruling.** Default "left as it is". The other choice: the deal-seeded rows of `energy_companies` held with `energy_deals` until a permission is recorded: the companies tab would show 21 companies, not 562. No branch: it is a license file's line and the seed's, not a page's code.

## 3. The AI view's dollar sums add unlike things (Low)

- **Where.** `site/app/deals/ai/view.tsx` (the lead, the table's "US dollars stated"); `site/lib/dealsai.ts`, `aiCells`; decision 4 ("no sum is drawn across every kind of deal"; default "sums are by the kind of supply on the AI view"); `site/app/deals/v2/view.tsx`, the third headline's note ("a purchase price, a financing or a valuation").
- **Why it is wrong.** `aiCells` sums the US dollars of every tagged deal of a group whatever its kind and stage, for each of the four groupings; only the grouping by kind of supply keeps one kind a sum, and the view opens by buyer. On the rows of 12 November: 15 of the 82 buyers' sums add two kinds of supply or more (USD 1.13 trillion; the largest adds capital, compute and other, USD 425 billion); 3 of the 4 grids' (the group "not stated", USD 3.02 trillion of the 3.06); 6 of the 7 quarters' (2026-Q1, USD 1.66 trillion, adds six kinds). One acquisition of USD 1.25 trillion, of no stated stage, is 40.9 percent of the tagged USD; the five largest are 60.8 percent. Rumored talks are USD 235 billion (10 deals). The register's doubtful pairs are summed twice: a financing programme of USD 200 billion beside the USD 15 billion part of it, and one round of talks at USD 40 and 50 billion (USD 55 billion counted twice). And the tracker's note says the values in US dollars include "a valuation", which decision 4 and the table's column tip say is not kept (no USD span names a valuation; 6 evidence sentences of USD-stating deals use the word, so a valuation kept as a deal's sum cannot be ruled out from the words held).
- **The test.** `tests/test_audit_deals_3.py` on `wip/audit-deals-3`: through `lib/dealsai.ts`, a buyer's sum adds a raise and a compute contract, rumored and signed, and the kind of supply parts them (passes on main); the words test fails on main.
- **The fix on the branch, words only.** Decision 4's default (and the method note, word for word) says the AI view sums each group it shows, one kind a sum only by the kind of supply, and that by buyer, grid or quarter a sum adds raises, acquisitions, financings and contracts, rumored deals among them; the AI view's lead and the method note's section 7.4 say the same; the tracker's note reads "a contract's value ... (a valuation is not kept)", and `tests/test_session1852.py`'s pinned sentence follows. No figure moves.
- **For Samuel's ruling.** Default "left as it is". The other choice (`wip/audit-deals-7`, a test only): US dollars shown only by the kind of supply, and rumored talks left out of every sum: 15 buyers' sums, 3 grids' and 6 quarters' would be replaced by their parts or dropped; the tagged USD 3.06 trillion would be 2.82 without rumored deals. Folding the doubtful pairs is the register's (a person's), not a rule.

## 4. The tracker's fold describes another AI tag (Low)

- **Where.** `site/app/deals/v2/view.tsx`, "How a deal gets here": "AI power shows the deals the model tagged as power or infrastructure for AI or datacenters."
- **Why it is wrong.** The tag is the AI-power rule (decision 8, the AI view's lead, the table's tip): a named AI lab, hyperscaler, datacenter operator or AI-load buyer is a party, or the load is a datacenter; since session 2232 it is set in code (`fields.ai_of`), for the 529 older rows it is the first prompt's. It says who is in the deal, not that the deal is power or infrastructure: of the 212 tagged deals, 160 name no energy word in their technology or asset (63 capital, 29 compute capacity, 21 other), 75 are of the kind capital, 24 acquisitions. The method note's section 10 found about 35 tagged rows not energy's at all.
- **The test.** `tests/test_audit_deals_4.py` on `wip/audit-deals-4`: through `lib/deals2.ts`, the "AI power" click keeps a tagged equity raise beside a tagged PPA ("True" and "true" one flag) (passes on main); the words test fails on main.
- **The fix on the branch, words only.** The fold says what the rule tags, that the tag is not of the asset, that a funding round, a financing or an acquisition of an AI company is tagged too, and that most tagged deals name no power asset (decision 8). No figure moves.

## 5. The AI view's grid note reads a grid the code does not (Very low)

- **Where.** `site/app/deals/ai/view.tsx`, the note grouped by grid: "A grid named in a story, else the grid that serves most of the state the story names"; `site/lib/deals2.ts`, `toDeal` (`grid: STATE_GRID[state]`); decision 7.
- **Why it is wrong.** The tracker, the comparables and the AI view read the state alone (decision 7, the owner's item 4); only the table's own column reads a named grid first. The one deal that names a grid and no state (PJM, tagged AI) sits in "not stated" on the AI view, where the note puts it under PJM.
- **The test.** `tests/test_audit_deals_5.py` on `wip/audit-deals-5`: through `lib/deals2.ts` and `lib/dealsai.ts`, a named grid with no state is "not stated", a state's grid is read (passes on main); the words test fails on main.
- **The fix on the branch, words only.** The note says the grid is the state's, a grid a story names without a state not read here, as in the tracker and the comparables (decision 7). Whether the three views read a named grid stays the owner's item 4.

## 6. The comparables' medians mix assets, and three is one deal (Low)

- **Where.** `site/app/deals/comparables/view.tsx`, the chart and the table (by type, the default); `site/lib/deals2.ts`, `comparables`, `medianOf`; decision 6 ("fewer than three would show one deal's terms as a market's").
- **Why it matters.** A group is every deal of a type, technology, grid or year, of every technology, country and stage. The power purchases' median, 348 MW of 12, runs from a 43.5 MW solar PPA to a 3,600 MW nuclear one, through fuel cells of 702 and 2,800 MW; the acquisitions' 892 MW of 3 sits between a 65 MW datacenter and a 5,400 MW portfolio and is the gas plant's own figure; "other" (810 of 6) holds a datacenter, four gas rows and a 6,000 MW nuclear row. 38,147 of the 40,297 MW name no country. A median of three is the middle deal's figure, which is what decision 6's floor means to avoid. An M&A analyst's comparable would be a price per MW within one asset class: no acquisition states both USD and MW.
- **The test.** `tests/test_audit_deals_6.py` on `wip/audit-deals-6`: through `lib/deals2.ts`, the median of three is the middle figure, of any mix (passes on main); the words test fails on main.
- **The fix on the branch, words only.** The chart's note says a group holds every technology, country and stage of its kind, sets a solar plant of tens of MW beside a nuclear plant of thousands, and that a median of three is the middle deal's own figure, not a market's.
- **For Samuel's ruling.** Default "left as it is". The other choice: a floor of five deals (13 medians to 8: M&A's, offtake's, behind the meter's, solar's and ERCOT's go) or ten (3 remain). No branch: the measure is in `measures2.json`.

## The words branches drawn and read

Each branch's pages were drawn to HTML with the site's own code (`draw_deals.mjs`, run from `site/` with `register.mjs`: the site's loaders, a stand-in for `components/Brand.tsx`, one for the first tab's client table, and the license file without the deals' row when `ERW_DRAW_UNHELD=1`): `app/deals/page.tsx` whole for the first tab, the tracker, the comparables, the AI view (by buyer and by grid), the charts and the companies tab, as a visitor meets them under the hold and as they draw once it allows, the live set's read answered from the rows on disk. Each new sentence was read in the drawn text. No em dash in any drawing.

| Branch | Where the words are drawn | Read |
|---|---|---|
| `wip/audit-deals-1` | the first tab's lead (under the hold too); the month's note; the tracker's chart note | pass: "Energy deals reported in the news since January 2025, from the stories the ERW scores, each with its sources."; "The newest deal held is dated 2026-11-12: the cells count the deals dated in the month up to that day, and not every story of a month was scored (none after 12 November 2026, as of 26 November 2026)."; "... of the stories of May to September 2025 held, almost none was scored (13 of 1,885) ... the newest deal held is dated 2026-11-12. The bars show what was scored as much as what was struck." |
| `wip/audit-deals-2` | decision 13, under every tab, the companies tab and the held views included | pass: "The companies tab reads energy_companies, which is not held: each party of a deal is a company row there, with the deals' types and technologies as tags, the place a deal states and the stories' links." and its default |
| `wip/audit-deals-3` | the AI view's lead; the tracker's third headline; decision 4's default | pass: "A group's sum adds every kind of deal in it and every stage: ..."; "296 state a value in US dollars: a purchase price, a financing or a contract's value, each as stated (a valuation is not kept) and not summed here ..."; "... by buyer (its default), grid or quarter, a group's sum adds raises, acquisitions, financings and contracts together, rumored deals among them." |
| `wip/audit-deals-4` | the tracker's fold | pass: "AI power shows the deals the AI-power rule tags: ..." and "The tag says who is in the deal or what it serves, not that its asset is power: ..." |
| `wip/audit-deals-5` | the AI view by grid | pass: "The grid that serves most of the state the story names (a grid a story names without a state is not read here, as in the tracker and the comparables: decision 7); ..." |
| `wip/audit-deals-6` | the comparables' chart note | pass: "A group holds every technology, country and stage of its kind: ..." |
| the six merged (a local trial, not pushed) | every view | pass: all nine new sentences drawn; the pages' functions on the merged code give the same 1,108 keys (no figure moved) |

- The six words branches merge together onto origin/main of 26 November (a local trial branch, removed) with no conflict. Their tests with every test file that reads the changed files (`test_session49`, `113`, `114`, `239`, `241c`, `282`, `329`, `411`, `421`, `462`, `463`, `465`, `466`, `500`, `1852`, `1853`, `2239_deals` to `2241_deals`, `2247_deals`, `5001`, `5003`, `7018_*_done` (eight), `7402_trackers`, `7404_trackers`, `7405_trackers`, `7407_trackers`) pass on the merge: 279 passed, 12 skipped. On origin/main each words test fails (8 failed) and each behaviour test passes (9 passed, those of `wip/audit-deals-7` among them).

## The decisions block, line by line

1. What a deal is, the stricter list since 6 November: **right as stated** (54 rows under it, 529 upgraded).
2. Figures only as stated, never zero: **right**.
3. One deal one row, the register, the folded pair as kept: **right as stated**; no unfolded repeat found by type and parties within 30 days.
4. US dollars as stated, no sum across every kind: the AI view sums across kinds by buyer, grid and quarter (**finding 3**).
5. A price in US dollars per MWh, nothing converted: **right** (0 priced; 2 in another unit).
6. A median from three: **right as computed**; a median of three is one deal's figure (finding 6).
7. The grid from the state in three views: **right**; the AI view's note says otherwise (finding 5).
8. The AI-power tag of the parties and the load: **right**; the tracker's fold says otherwise (finding 4).
9. The kind of supply, a technology's word first: **right**.
10. "Sure", no floor: **right as stated**; at 0.7, 281 deals and 21,705 MW remain of 578 and 40,297 (the owner's item 2).
11. The date: **right as stated** (4 stated, 579 the first story's day).
12. What the scored news reported: **right in kind**; the window it covers is misstated (finding 1).
13. Held whole, nothing of a row: true of the deal views, not of the companies tab (**finding 2**).

## Not covered, or left open

- **The live set's rows.** The CSV of 12 November (583 rows) was read, not the live set (590 on 16 November by the method note): no request to any service. The rules are restated to the digit.
- **The held tables in git.** `warehouse/output/energy_deals.csv` and the internal `energy_deals_evidence.csv` (outlet sentences) are tracked by git (`.gitignore` lets the evidence file in). Whether the repository is public was not checked (no request to any service); if it is, the site's hold does not hold these files. For Samuel, not a finding of the page.
- **The tracker's code reads `dollars` and `price` only**, the table's `usd` and `usd_per_mwh` first: equal on every row today; latent, not a branch.
- **The capital view's rules** (`warehouse/derived/capital_page.py`) draw nothing under the hold; not restated beyond its row count.
- **Each row's own figures** (MW, USD) are the table's: not restated, as the replication does not.
- **The pages in a browser**: drawn to HTML with the site's own code; no layout, no width of 390 px.

## Landing, rulings and data (returned to the chain's main session)

- **For landing (words only):** `wip/audit-deals-1` (`76bcdc188`), `-2` (`cc0c32314`), `-3` (`f819cf539`), `-4` (`4a1f8e8be`), `-5` (`0330c26ed`), `-6` (`f8724525e`). They merge together cleanly onto origin/main of 26 November; each was drawn and read (pass). No figure moves.
- **For Samuel's ruling, default "left as it is":**
  - Finding 3, `wip/audit-deals-7` (`4af4a3a28`), not for landing: the AI view's US dollars only by the kind of supply, rumored talks out: 15 of 82 buyers' sums and 6 of 7 quarters' would go; the tagged USD 3.06 trillion to 2.82.
  - Finding 2, no branch: the deal-seeded rows of `energy_companies` held with the deals: the companies tab 562 rows to 21.
  - Finding 6, no branch: a floor of five deals for a median: 13 medians to 8.
- **Data requests:** none. Every measure was made from the files on this machine.
- **Needs the key:** scoring the stories after 12 November 2026 and the unscored months (May to September 2025, the rest of October to December 2025 and June to August 2026), then `warehouse/deals/extract.py`; reading the 529 older rows again under the stricter prompt (the method note, section 10).
