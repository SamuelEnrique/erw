# The deal tracker, as a reader meets it (`/deals`)

Energy Research Warehouse (ERW), platform tool 6. Written by session 7405 (chain 303, 16 November 2026) as the one note for the tool: what a deal is, how two stories of one deal become one row, how each figure is read and when it is left empty, every view with its figures, and what the tracker cannot see. It points to the tables' own notes and does not repeat them:

- [`energy_deals`](energy_deals.md): the table, each field with its vocabulary and its evidence rule, the hold, and every check key of the pages.
- [`deal_counterparties`](deal_counterparties.md): one name a company, its parent, its utility number.
- `energy_deals_evidence` (internal): the sentence each deal rests on and the words behind each figure.
- `docs/methods/companies.md`: the capital view's kinds of company.

Where this note and `energy_deals.md` differ on a column, that note governs; on what the pages show and how a figure is computed from the rows, this note governs.

The figures quoted here are of the live set's rows as read on 16 November 2026 at 09:49 UTC (590 rows, the newest deal dated 13 November), the day's `replication/deals/page_figures.json`. They move with the table every day.

## 1. The views

| Address | What it draws | Its figures |
|---|---|---|
| `/deals` | Every row of the table, sortable, with its filters and the three cells of the month | section 7.1 |
| `/deals?tab=tracker` | The deals by type, kind, technology, grid, counterparty, year and status; the headline counts; the deals by month | 7.2 |
| `/deals?view=comparables` | The deals' disclosed figures side by side, one dimension at a time, and the disclosed prices | 7.3 |
| `/deals?view=ai` | The deals tagged AI power by buyer, kind of supply, grid and quarter; the ten with the most megawatts and the ten with the most US dollars | 7.4 |
| `/deals?view=charts` | Four charts: megawatts by quarter and kind of supply, the prices stated, the AI-power share, the counterparties with the most megawatts | 7.5 |
| `/deals/capital` | Capital flows (platform tool 11): under the hold, the table's row count alone | 7.6 |

**The hold.** `energy_deals` is held whole ("license needed") since 21 October 2026: every deal was extracted from news stories, and the outlets' own pages ask for permission. Every view draws the hold's sentence and the count of rows it covers, and nothing of a row. Every rule below is what the pages compute when the hold allows; the replication runs the pages' own functions on the rows to say what that is.

## 2. What a deal is, and is not

- **A deal** is a specific transaction between named parties that a scored news story reports: a power purchase agreement, an offtake, an acquisition or merger, project finance, tax equity, debt, an equity raise, a joint venture, a lease, a behind-the-meter supply, a nuclear restart, a small modular reactor deal, a fuel supply contract (the fourteen types of `deal_type`, with "other").
- **Not a deal**: market commentary, policy, earnings, a forecast, a price. Since the stricter prompt of 6 November 2026 also: a company's plan or pledge to invest, a company that seeks or weighs a deal with no counterparty named, a government's permission, an agreement between two governments, a raise whose company the story does not name, a project one party leads with no counterparty, and talks with only one party named. Talks between two named companies are a deal, with the status rumored.
- **A deal needs a party the story names.** "Investors", "a US hyperscaler" and "lenders" are descriptions, and the field is left empty.
- **Which rows the stricter list has reached.** 61 of the 590 rows were extracted under it. The other 529 were extracted by the first prompt and later given the new fields in code (`fields_version` `upgraded`); none of them has been read again by a model. By this session's reading of their stories' titles, about 22 of the 529 are a plan, a pledge, a seeking, one-sided talks or a permission, and about 19 more cannot be told from a title (section 10).
- **Is a deal energy's where its asset is energy?** That is the tracker's intent, and it is written in no prompt and no rubric today: the extraction is told to extract "energy transactions" and its list of what is not a deal has no line for an asset that is not energy. So the table holds funding rounds and purchases of AI and cloud companies, chip contracts, fund raises and sales of businesses that are not energy (about 51 of the 529 by the same reading). They are in the counts, and most are tagged AI power (section 5). Whether the rule is written into the prompt is the owner's (section 12).
- **The kind** (`kind`, since session 2232) is master plan tool 6's: the power kind first where the deal's words name it (nuclear restart or uprate, small modular reactor, behind the meter, gas buildout, transmission, storage, compute capacity), else the form (power purchase, offtake, project finance, acquisition, capital, fuel supply), else other. A cloud, GPU or datacenter capacity contract is compute capacity, never an offtake. A row extracted before the kinds took its kind from its own words in code, else from its type.
- **The panel's four types** (power purchase, offtake, project finance, acquisition) are the extraction's own types of those names; every other type is "Other" on the tracker tab (343 of the 585 deals). Tolling is a type no row has.

## 3. One deal, one row: how two stories are folded

Three steps, in order:

1. **The extraction.** Each call carries the deals already held; a deal the model marks as one of them adds its story to that deal.
2. **The code** (`warehouse/deals/dedupe.py`, session 531's rule and chain 156's): a deal the model did not mark is joined to a held one when the two have the same type and the same two parties (in either order; a name and the same name with words added are one party; the US government is one party whatever it is called), are dated within 30 days, name assets that share a word where both name one, and state sums within a quarter of each other (megawatts within a tenth) where both state one. A join keeps the earliest date, moves the stage forward with its history, fills a figure the held row lacks and never replaces a figure held.
3. **The register** (`warehouse/deals/duplicates.csv`): pairs a person or a session judged one deal after the fact, each with its reason. Eight pairs on 16 November: five folded, three left as doubtful.

**What a view does with a folded pair.** The tracker tab, the comparables, the AI view and the charts count the pair once, as the row the register keeps, with the story links of both (585 deals). The first tab lists every row of the table (590). The row kept stands as extracted: a figure only the folded row states is not carried over. Today that is 433 MW and USD 0.2 billion of one loan, whose earlier row is the one kept (section 12).

## 4. How megawatts, US dollars and a price are read, and when they are empty

- **Every number has its words.** For each number the model returns the exact words of the title or summary it read it from. The number is kept only if those words are in the story and parse to the same value (GW and MW, billion and million applied). Otherwise it is empty, and the page says "not stated". Nothing is estimated, converted or filled.
- **Megawatts** (`mw`): the size the story states. 39 of the 585 deals state one (43,119 MW in all). Where the words give a ceiling ("up to 2.8 GW") the ceiling is the number kept; no range is held.
- **US dollars** (`usd`, the older `dollars`): the deal's own sum as stated, a purchase price, a financing or a contract's value. Not kept: a sum in another currency (never converted; a figure the story also gives in US dollars is kept, session 2285), a valuation, a company-wide investment, a market value, and, for a power purchase, an offtake, a lease or a fuel supply, a sum that funds something else or is an asset's cost (session 2271). 298 of the 585 state one. No sum is drawn across every kind of deal.
- **A price** (`usd_per_mwh`, the older `price`): US dollars per MWh only. A figure in another unit stays as extracted beside its unit and is never converted (2 deals). No deal held states a price in US dollars per MWh on 16 November: the warehouse holds a story's title and a short summary, not its text.
- **A term** in years only; a term stated in months is left empty and flagged.
- **The flags** (`flags`, 14 rows): after a row is built its headlines are read again in code, and a headline's figure the row lacks or contradicts, megawatts and megawatt hours confused, or a figure above a bound is flagged. A flag never changes or drops a figure.
- **A state, a country and a status** are kept only where the story's words name them. 52 of the 585 deals name a US state.

## 5. How a deal is tagged AI power

- **The rule** (`ai_power`, with `ai_power_basis` on the rows extracted since session 2232): a named AI lab, hyperscaler, datacenter operator or AI-load buyer is a party, or the load the deal serves is a datacenter. AI named only as a motive ("as AI demand booms", "tied to data centre buildout") does not tag a deal.
- **What the tag does not say.** It says who is in the deal or what it serves, not that the deal's asset is power. 217 of the 585 deals are tagged; 104 of them are capital deals by their kind of supply (a funding round, an acquisition, a financing) and 30 are compute capacity. The megawatts of the tagged deals are 16,107.5 MW from the 20 that state them.
- **Case.** "True" and "true" in the table are one flag.

## 6. The grid of a deal

The tracker tab, the comparables and the AI view read a deal's grid from the state a story names, for the states one grid operator mostly serves (the list of `datacenter_tracker.md`, section 6); 34 of the 585 deals have one. The table's own Grid column reads a grid a story names first (`grid`, 1 row), then the state. No deal's point of delivery or node is held.

## 7. Every figure, view by view

Each keyed figure is read on the built page by `site/scripts/check-values.mjs` and recomputed from the rows by `replication/deals/replicate.py`. A figure the pages print without a key is in the replication under a name of its own (`table|...`, `tracker|...`).

### 7.1 The table (`site/lib/dealsview.ts`)

- **The month's three cells** (`monthBlock`): `deals|month_count|<month>`, the rows dated in the month; `deals|month_mw|<month>`, the megawatts they state, with how many state them; `deals|month_ai_pct|<month>`, the share tagged AI power to a whole percent. At the start of a month with no deal yet the cells show the month before, and say so. November 2026 so far: 39 deals, 5,301.5 MW from the 8 that state it, 26 percent.
- **Each row's own figures**: `event|energy_deals|<deal>|mw` and `|dollars`.
- **The filters** (kind, grid, state, counterparty, megawatts from and to, year, AI power, stage, price disclosed) change what is listed and downloaded, never a keyed figure. The stage is the row's stage where extracted, else its status.
- **"Sure"** is the extraction's own confidence that the row is a real, specific transaction with its fields right, from 0 to 1: 0.8 or more for a deal between named parties that the words state as done or agreed, 0.6 to 0.8 for a stated deal with a field unclear, under 0.6 where it is doubtful that there is a transaction. It runs from 0.3 to 0.95 on the rows held. The table shows every row whatever its figure; the Roundup's tables take a floor of 0.7.

### 7.2 The tracker tab (`site/lib/deals2.ts`)

The folded deals (585) and their counts: those that state megawatts and the sum (39; 43,119 MW), a price per MWh (0), a figure in another unit (2), a value in US dollars (298); the panel's brackets (each type, each of tool 6's four kinds read from the type or the words, each technology as stated, each grid, year and status, storage only, AI power); the parties named in two deals or more; the deals of every month from the first to the last, a month with none drawn as zero. The one sentence under the title is made from these counts alone.

### 7.3 The comparables and the disclosed prices

- **By type, technology, grid or year**, for each group: the deals `deals|comp_deals|<dimension>|<value>`, those that state a price `comp_with_price` and a size `comp_with_mw`, and the median of each, `comp_median_price` and `comp_median_mw`, **only where three or more deals of the group state the figure**. A median is of the figures stated; a deal that states none is left out, never counted as zero. A group with fewer than three says so. The group that does not state the dimension is keyed `-`.
- **On how many deals the medians rest today**: no group has three deals that state a price, so no median price is shown anywhere. Fourteen groups have a median size: power purchases 452.5 MW (of the 14 that state one), acquisitions 892, offtakes 50; nuclear 1,080, gas 896, solar 322; ERCOT 222; the year 2026 479.5 MW (of 38).
- **The disclosed prices**: the power purchases and offtakes that state a price in US dollars per MWh, by technology, grid or year: `deals|price_count`, and from three `price_median`, `price_low` and `price_high`. None today. A reader's own deal is placed against them in one line, nothing stored or sent.

### 7.4 The AI-power view (`site/lib/dealsai.ts`)

- **By buyer, kind of supply, grid and quarter**: `deals|ai_deals|<dimension>|<value>`, the megawatts `ai_mw` and US dollars `ai_usd` summed where stated, and how many state each (`ai_with_mw`, `ai_with_usd`). A sum has no key where no deal of the group states the figure.
- **The buyer** is the buyer as one name a company, else the party named first.
- **The kind of supply** is the first of these that the deal's kind or its technology's words say: nuclear; gas; renewables and storage; then compute capacity; grid supply (a power purchase, an offtake or a behind-the-meter deal with no technology stated); capital (a raise, an acquisition, a financing); other. A technology's word wins over the form, so a capital deal whose story names nuclear is under nuclear.
- **The two lists of ten** (the most megawatts, the most US dollars) are of the tagged deals that are not capital by that reading.

### 7.5 The charts

`deals|chart_mw|<quarter>|<group>`: megawatts stated by quarter and five groups of supply (compute, capital and other together), with the quarter's deals that state none (`|without`); `deals|chart_price|<deal>|price`: each priced power purchase or offtake; `deals|chart_ai|<quarter>|share`: the tagged deals' share of the megawatts stated, to a tenth of a percent, with both sums; `deals|chart_party|<name>|mw`: the ten counterparties with the most megawatts, a deal counted once for its buyer and once for its seller.

### 7.6 Capital flows (`/deals/capital`)

Project finance, acquisitions, debt and equity raises with the kind of company that brings the money, from a file the data machine builds (`site/data/capital.json`). While the table is held the file holds the hold and the table's row count alone, `capital|n_rows`.

## 8. What the tracker cannot see

- A deal no scored story reports, and a deal only a filing or a press release describes.
- A figure the title and summary do not state: most deals' size, almost every price, the tenor, the point of delivery.
- The market: the counts by month follow the ERW's news coverage. No deal is dated May to September 2025; the stories of June to September 2025 are held and were not scored.
- Whether a deal closed, where no later story says so.

## 9. The replication and the cross-checks

- `replication/deals/` (session 7404): `fetch_rows.py` reads the rows from the live set into `rows/`, which git ignores; `replicate.py` computes every figure of every view from the rows by the rules of this note, in its own Python, beside what the pages' own functions give on the same rows (`site/scripts/deal-tracker-figures.mjs`). On 16 November 2026: **1,123 of 1,124 inside the tolerance; the one difference is named**: the capital view's file says 529 rows, the count of the day it was built, and the table holds 590. `replicate.do` reproduces the headline figures in Stata, with the expected values at its top.
- `docs/methods/crosschecks/deal_tracker.md`: the tracker's counts and megawatts by year and kind beside published tallies of power purchase agreements, and the twenty largest AI-power rows each against its own story's headline.

## 10. What a second reading of the older rows would change (not run)

The 529 rows extracted before 6 November 2026 have not been read by the stricter prompt. Reading them again is a model run, which this note's session did not make. By a word reading of each row's story titles, checked by eye (no model; the lists are in the session's report):

| By the titles | Rows of the 529 | Of them tagged AI power |
|---|---:|---:|
| A plan or a pledge to invest, a seeking, one-sided talks or a permission: the stricter prompt's own list would not return it | about 22 | about 10 |
| Not energy's: an AI or cloud company's funding, stake or purchase, a chip contract, a fund's raise, a business that is not energy. Dropped only if the rule is written into the prompt (section 2) | about 51 | about 35 |
| A compute or infrastructure contract typed as an offtake or as other, which the prompt's kinds would call compute capacity | about 4 | 4 |
| Cannot be told from a title (a sale weighed or explored, a datacenter's financing) | about 19 | about 8 |
| Stands | about 433 | about 140 |

A second reading would also fill what the first prompt did not ask for: the stage and its words, the country by the newer rules, a party a later story names.

## 11. The decisions on the page

The page lists, at the foot of every tab, the choices that move its figures, each with its default and its source on hover (`site/lib/decisions.ts`, `DEAL_TRACKER_DECISIONS`, drawn by `site/components/tool/DecisionsBlock.tsx`); the older list of every choice with its session (`site/app/deals/Decisions.tsx`, session 465) stays under it. The list below is the same list, word for word; `tests/test_session7405_trackers.py` holds the two equal.

1. A deal is a named transaction between named parties that a scored news story reports. A plan or a pledge to invest, a seeking with no counterparty, a government's permission and an agreement between two governments are not deals. **Default:** The stricter list is applied to what is extracted since 6 November 2026; the rows extracted before it stand as the first prompt left them until they are read again. **Source:** The extraction's prompt (warehouse/deals/extract.py) and the audit of 6 November 2026 (docs/reviews/deals-audit-2026-11-06.md). (sessions 15 and 2232)
2. A size in MW, a sum in US dollars, a price and a term are kept only where the story's own words state them and parse to the same number; a figure no story states is "not stated", never zero and never an estimate. **Default:** Blank. A sum is over the deals that state the figure, with their count beside it. **Source:** Session 16's ruling: nothing inferred beyond the stated words (warehouse/deals/extract.py, verified). (sessions 15 and 16)
3. Two stories of one deal are one row: the extraction joins a later story to the deal it already holds, the code joins the same type and parties within 30 days, and the register folds what is left. A folded pair is counted once in the tracker, the comparables, the AI view and the charts, as the row kept; the first tab lists every row. **Default:** The row kept stands as extracted, with the story links of both; a figure only the folded row states is not carried over. **Source:** warehouse/deals/dedupe.py and the register warehouse/deals/duplicates.csv, each pair with its reason. (sessions 113, 531 and 2233)
4. US dollars are a deal's own sum as stated: a purchase price, a financing or a contract's value. Another currency is never converted, a valuation or a company-wide investment is not the deal's, and no sum is drawn across every kind of deal. **Default:** No total over all deals; sums are by the kind of supply on the AI view. **Source:** The extraction's prompt and session 2271's rule for a contract's sum; deals faults row 5. (sessions 15 and 1852)
5. A price is a price in US dollars per MWh; a figure in another unit is shown as extracted and never converted. **Default:** Nothing converted; almost no story states a price. **Source:** warehouse/deals/fields.py, energy_price; the warehouse holds a story's title and a short summary, not its text. (session 113)
6. The comparables show a median only where three or more deals of a group state the figure; a deal that states none is left out of the median, never counted as zero. **Default:** Three deals. **Source:** site/lib/deals2.ts, medianOf; fewer than three would show one deal's terms as a market's. (session 466)
7. The tracker, the comparables and the AI view read a deal's grid from the state a story names, for the states one grid operator mostly serves; the table's own Grid column reads a grid a story names first. No deal's point of delivery is held. **Default:** The state alone in the three views; most deals name no state and have no grid. **Source:** site/lib/deals2.ts, STATE_GRID; warehouse/deals/fields.py, grid_of. (sessions 113 and 2238)
8. A deal is tagged AI power where a named AI lab, hyperscaler or datacenter operator is a party, or the load it serves is a datacenter; AI named only as a motive does not tag it. The tag does not say the deal's asset is power: a funding round of an AI company is tagged too. **Default:** The tag as extracted; "True" and "true" are one flag. **Source:** warehouse/deals/fields.py, ai_of; the extraction's prompt. (sessions 114, 2232 and 2270)
9. The kind of supply is the first of nuclear, gas, renewables and storage that the deal's kind or its technology's words say, then compute capacity, grid supply (a power purchase or an offtake with no technology stated), capital, and other. The two lists of ten leave out the capital deals. **Default:** A technology's word wins over the form of the deal. **Source:** site/lib/dealsai.ts, supplyOf; deals faults row 3. (sessions 2240 and 1852)
10. "Sure" is the extraction's own confidence, from 0 to 1, that the row is a real, specific transaction with its fields right: 0.8 or more for a stated deal between named parties, under 0.6 where it is doubtful that there is a transaction. Every row is shown whatever its figure. **Default:** No floor: the table opens with every row. **Source:** The extraction's prompt, its confidence bands; whether the table should open at a floor is the owner's (deals faults row 16). (sessions 15 and 2251)
11. A deal's date is the announced date where a story states it, else the day its first story was published (UTC); at the start of a month with no deal yet, the month's cells show the month before, labelled. **Default:** The first story's day for almost every deal. **Source:** warehouse/deals/extract.py, date_basis. (sessions 15 and 49)
12. The tracker holds what the news the ERW scores reported, from the title and a short summary of each story: its counts by month follow that coverage, not the market, and a deal only a filing or a press release describes is not here. **Default:** No source beyond the scored news. **Source:** docs/methods/energy_deals.md, "What the extraction cannot see". (sessions 15 and 2247)
13. From 21 October 2026 the deals are held whole for a license: every view draws the hold's sentence and the count of rows it covers, and nothing of a row. **Default:** Held whole; no row is shown. **Source:** warehouse/metadata/license_status.csv: the outlets' own pages ask for permission. (sessions 215 and 465; the owner's ruling of 12 October 2026)

## 12. What waits for the owner

Three rows of the faults read of 11 November (`docs/reviews/deals-faults-2026-11-11.md`) are the owner's. In plain words, each with the default the pages stand on:

1. **Whether the deals stay held whole** (row 1). No reader, the internal view included, sees a deal, a comparable or a download. The other choice: show the rows whose every source is public, each with its license. Default: held whole.
2. **Whether the table opens at a floor of "Sure"** (row 16). A row at 0.3 stands beside a row at 0.95. Default: no floor; every row is shown and the column sorts.
3. **Whether the grey explanatory text becomes hover tips** (row 17). It is drawn under every title and panel of every tool, so the change reaches the whole site. Default: unchanged.

Three more were found by the work of 16 November (rows 22, 23 and 28 of the same file):

4. **Whether the three views read a grid a story names**, as the table's own column does. One row differs today. Default: the state alone.
5. **Whether a folded pair carries over a figure only the folded row states.** The register keeps the earlier row of the Department of Energy's loan to Vistra, so the tracker shows that loan without the 433 MW its later stories state. Default: the row kept stands as extracted.
6. **Whether "a deal is energy's where its asset is energy" is written into the extraction's prompt.** Default: not written; the note says what the table holds.

## Sign-off

Signing this note accepts, as the tool's rules:

- what a deal is and is not, with the stricter list reaching only the rows extracted since 6 November 2026 until the older rows are read again (section 2);
- one deal, one row: the extraction, the code's rule and the register, a folded pair counted once as the row kept (section 3);
- megawatts, US dollars and a price only as the story's words state them, empty otherwise, nothing converted and no sum across every kind of deal (section 4);
- the AI-power tag as a tag of the parties and the load, not of the asset (section 5);
- a median only from three deals that state the figure (section 7.3);
- "Sure" as the extraction's own confidence, with no floor on the table (section 7.1);
- the decisions of section 11, the list the page shows at its foot.

It leaves open the six items of section 12 and the second reading of section 10.

- Signed off by:
- Date:
- Items of section 12 ruled, and how:
