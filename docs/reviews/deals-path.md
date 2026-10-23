# The investor's path, walked: the deal tracker on 23 October 2026

Energy Research Warehouse (ERW), session 831 (chain `queue/done/080-night-23-october-portable-landing-deals-.md`, portable-laptop). The questions an infrastructure investor asks of a deal list, from the two research reports of 21 October (cited), walked click by click on `/deals` in the internal view, on a local build of `wip/830-deals` (sessions 822 to 830 over main) served on port 3828: what the page showed, whether it answered, what broke. The screenshots are `docs/brand/review-831/step-*.png` (1280 px; the 390 px shots of the same pages are under `review-830/`).

## The questions, and where they come from

1. **Who is buying power for AI, from whom, and how much?** AG, Key Findings row 3: labs hire "for hedging, utility deals, infrastructure finance and energy policy"; section 4: the roles reach for "PPA and deal comparables". DR, roles: Anthropic's "Energy Scheduling & Portfolio Lead", OpenAI's Camellia campus "25-year contract to provide 1 GW of flexible demand response to Georgia Power".
2. **What does a comparable deal pay, and for what product?** AG, section 4 ("PPA and deal comparables"; "none of the four verified providers publishes an open, assumption-visible cost-of-power or deal dataset"); the Power Trading Lead's posting covers "fixed-price supply, forwards, swaps and options" (AG, Key Findings row 3).
3. **Is the figure sourced, and may I cite it?** AG, Key Findings row 2 and TL;DR: a "clean license posture can be a differentiator"; DR, "On the data warehouse's role": "the factual backbone ... unique content that others can cite".
4. **What was filed, not just announced?** AG, section 4 (the roles reach for "large-load interconnection terms"); DR, roles (OpenAI's filings and "property acquisitions and resource reports").
5. **How do two deals compare?** AG, section 4 ("deal comparables"); the battery page's A and B form is the ERW's own answer to "which is better" without a verdict (`docs/brand.md`, section 7's assumptions and Resets).

## The walk

| Step | Address, click | What the page showed | Answered? | What broke |
|---|---|---|---|---|
| 1 | `/deals` (the deals tab) | The line: 486 deals held (license needed), 3 unsettled, 16 shown, each on a public source named on the row. Then "Compare two deals, A and B" with two selects, then the table of 16 rows: date, type, parties, asset, technology, where, MW, USD, status, AI. `step-deals_1280.png` | Question 1 in part: the shown deals are nuclear (World Nuclear News is the one public outlet of the feeds); Amazon and Constellation, Amazon and AEP, Vistra's loan are the AI-power rows; 3 of 16 state MW, 4 state dollars. The 486 held rows are where most of the AI deals are, and the line says so. | Nothing. The compare form's selects ran to the page's edge in the first build (session 830 stopped them at the panel's measure). |
| 2 | click a row (Amazon / Constellation, 2026-09-30) | The row opens: buyer, seller, capacity 190 MW, value not stated, price not stated, term not stated, "Sources: World Nuclear News (2026-10-01); 2 other outlets, whose terms ask for permission or are not read, also report it; they are not linked", "Filed terms (FERC EQR): looked for a filed contract whose seller and buyer are two of this deal's parties: 2026 Q3's filings are not held yet; 0 rows match in the quarter held (2026 Q2). The filed product, rate, quantity, delivery point and dates: license needed", "Evidence: shown because a source whose terms the ERW reads as public reports it". (The opened row is not in a screenshot: the shot script takes a page, not a click; the words are the component's, `DealsTable.tsx`.) | Questions 3 and 4: the source is named and linked; the filed terms are looked for and said to be held. Question 2 is not answered: no shown deal states a price. | The compare page failed on the server in the first build (a client module's function called from a server component); fixed in session 829. |
| 3 | `/deals?a=deal:70bf30d372e1d674&b=deal:d6eda0ffd6db76cd` (choose A and B, Compare) | Vistra's loan beside Amazon and AEP's 960 MW on twelve rows: date, type, parties, asset, technology, grid, MW, term, USD, USD per MW, status, evidence; "What differs, B against A: Size, MW: 527 MW". `step-deals-compare_1280.png` | Question 5: yes, without a verdict; USD per MW only for the deal that states both. | Nothing after the fix. |
| 4 | `/deals?tab=tracker` | The same line; "The ERW holds 16 deals ... These are the 16 shown deals; 489 held or unsettled deals are not counted"; "Most stories give no size and no price" over the 16; the headline numbers (16 deals, 1,583 MW from 3, 0 state a price, 4 a value) with the tip "Computed over the 16 shown deals only; 489 held or unsettled deals are not counted (license needed)"; the deals-by-month chart with the held months hatched above the shown bars (January 2025 to October 2026). `step-deals-tracker_1280.png` | Question 1 in part, honestly: the chart's hatching shows where the held deals are by month (106 in October 2026). | Nothing. |
| 5 | `/deals?view=comparables` | "Of the 16 deals shown, 0 state a price ... every figure of this view is over the shown deals only"; by type: every group "fewer than three" for a price; the median size shown where three state it (none today). `step-deals-comparables_1280.png` | Question 2: no. The view says why: nothing is computed from fewer than three deals that state a figure, and no shown deal states a price. | Nothing. |
| 6 | `/contracts` | The power contracts page: FERC EQR's quarter in force, by product and balancing authority, the largest buyers and sellers, the terms read from the words; every figure internal (the page reads through the internal token). `step-contracts_1280.png` | Question 4: the filed terms exist in the warehouse; the deal rows cannot show them until the EQR tables' flag is ruled on (`deals-rulings-2026-10-23.md`, item 5). | Nothing. |

## What the path says

- **The tracker answers "who, with whom, how much" for the rows a public source stands behind, and says plainly how many rows it cannot show.** An investor sees 16 deals and a count of 489; the count is honest and keyed, but the AI-power deals they came for are mostly behind it. The one thing that would change this is a ruling on the publishers (the rulings file, items 1, 2 and 5) and a filing source (`deals-gaps-2026-10-23.md`).
- **"What does a comparable deal pay" has no answer from the news.** No shown deal states a price per MWh, and across all 505 none does (session 466). The filed terms are the answer, and they are joined and held: the panel on each row shows the join is done.
- **Two deals compare without a verdict**, on the same rows, with the pair in the address; the figures a story does not state stay "not stated".
- **What broke on the build**: the compare page's server error (fixed, session 829) and the selects' width (fixed, session 830). `check-links.mjs` on the build: session 829's report.

## Fixes made that needed no ruling

- `Compare.tsx`: its own `usd` (session 829); the form's selects stop at the panel's measure (session 830).

## Decisions made without you (session 831)

- The walk is on the local build of the chain's branch, not production: nothing of the chain is on production yet (the landing's gate is blocked by another machine's branch in flight and by a past issue's revised figure; the rulings file, item 7).
- The opened row (step 2) is described from the component's words; the shot script takes pages, not clicks.
