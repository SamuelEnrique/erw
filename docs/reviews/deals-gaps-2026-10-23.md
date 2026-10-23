# What a lab's power trader reads in a deal, and what the tracker holds: 23 October 2026

Energy Research Warehouse (ERW), session 824 (chain `queue/done/080-night-23-october-portable-landing-deals-.md`, portable-laptop). The fields a power trading lead or an infrastructure-finance lead reads in a deal, from the two research reports of 21 October (`docs/reviews/research/ask-the-grid-landscape-2026-10.md`, "AG", its TL;DR and section 4; `docs/reviews/research/deep-research-report.md`, "DR", its roles), set against the columns of `energy_deals` (505 rows, extracted 2026-10-22T15:02:19Z) and its evidence table, and for each field the tracker does not hold, the source that would. Read only; no request; no row changed.

## Read these first

- **The roles.** AG, section 4: OpenAI's Power Trading Lead ("Power & Land team, inside datacenter design"; "owns hedging across electricity and gas"; the posting covers "fixed-price supply, forwards, swaps and options", AG Key Findings row 3), its Clean Energy and New Technology Lead, and the Utility and Power Project, Infrastructure Finance and Energy Policy leads a secondary source lists. DR, roles: Anthropic's "Data Center Energy Lead" and "Energy Scheduling & Portfolio Lead"; OpenAI's "Clean Energy and New Technology Lead" ("clean power, storage, grid flexibility and low-carbon backup"); OpenAI's Camellia campus with "a 25-year contract to provide 1 GW of flexible demand response to Georgia Power". AG's inference: "what these roles reach for: forward power and gas curves, utility tariffs and large-load interconnection terms, PPA and deal comparables, cost-of-power at candidate sites, and policy and regulatory tracking", and "none of the four verified providers publishes an open, assumption-visible cost-of-power or deal dataset".
- **The tracker holds the counterparties, the size, the type, the status and a stated price or term where a story prints one.** It does not hold the price structure, the delivery point or node, the product's shape (firm, as-generated, shaped, hourly matched), the settlement index, the start date, the credit terms, the counterparty's regulated status or the regulator's docket. For the 16 shown rows, no evidence row is a public filing: every one is a World Nuclear News article, so no field beyond the article's words can be drawn, and none was.
- **Three sources would fill most of the gaps, in order of what they give for the effort**: FERC's Electric Quarterly Report (`ferc_eqr_contracts`, already in the warehouse, internal by the ERW's own record; session 825 joins it), the companies' own announcements (press releases and 8-K exhibits on EDGAR), and the ISOs' and utilities' filings (interconnection agreements, large-load tariffs). Each is listed below by field, for the desktop's data chain.

## The fields, one by one

The reader is the lead above; the second column is the ERW's column where one exists. "Stated" counts the 505 rows that carry the field (the extraction keeps a field only where a story's words state it).

| Field a trader or a finance lead reads | `energy_deals` column | Stated, of 505 | Of the 16 shown | What the tracker says where it is blank | Source that would fill it |
|---|---|---|---|---|---|
| Counterparties (buyer, seller, others) | `buyer`, `seller`, `other_parties` | 505 (a party on every row; 2 governments both are not kept, session 531) | 16 | | held |
| Product: PPA, tolling, hedge, swap, capacity, offtake, fuel supply | `deal_type` (fourteen types; no tolling, hedge, swap or capacity type) | 505 | 16 | the type is one of the extraction's fourteen; a hedge or a swap is read as "other" or "ppa" | FERC EQR (`product_name`: energy, capacity, tolling, swaps are its own vocabulary); the company's announcement |
| Size, MW | `mw` | 27 | 3 | "MW not stated" | the company's announcement; the ISO's interconnection agreement for a plant; FERC EQR (contract quantity) |
| Energy, MWh | `mwh` | 2 | 0 | | FERC EQR (transaction quantity) |
| Term, years; start and end | `term_years` (no start, no end) | 17 | 1 | "not stated" | FERC EQR (`contract_execution_date`, `commencement_date`, `termination_date`); the announcement |
| Price, USD per MWh | `price` (USD per MWh only); `price_value`, `price_unit` otherwise | 0 state USD per MWh; 2 state a price in another unit (session 466: no group has three) | 0 | "not stated" | FERC EQR (`rate`, `rate_units`, the filed rate for a contract in force); rarely the announcement |
| Price structure: fixed, indexed, escalator, collar, hub plus basis | none | 0 | 0 | not said | FERC EQR (`rate_description`, where the filer writes it); the contract where filed with a regulator |
| Settlement index or hub | none | 0 | 0 | not said | FERC EQR (`point_of_delivery_balancing_authority`, `point_of_delivery_specific_location`) |
| Delivery point or node; grid | `state` and `country` only; the grid read from the state (session 113) | 45 name a state | 5 name a state | "the table holds no point of delivery" | FERC EQR (point of delivery); the ISO's interconnection queue for a plant's node |
| Shape: firm, as-generated, shaped, 24/7 matched; flexibility (demand response, curtailable) | none | 0 | 0 | not said | the announcement (Camellia's "flexible demand response" is such a term); the utility's large-load tariff and the interconnection agreement for the curtailment terms |
| Status (announced, signed, closed) and the date it closed | `status`, `event_date`, `date_basis` | 505 dated; 419 state a status | 16 | the status the story states | the announcement; an 8-K for a listed company |
| Value, USD; financing structure (debt, equity, tax equity, loan guarantee) | `dollars`; `deal_type` for financings | 269 state dollars | 4 | "not stated in US dollars" | the announcement; an 8-K; DOE's Loan Programs Office for a federal loan |
| Credit: the buyer's rating, security, parent guarantee | none | 0 | 0 | not said | the rating agencies (paid); the contract where filed |
| Regulated status: utility tariff, commission docket, approval needed | none (the policy monitor holds dockets separately) | 0 | 0 | not said | the state commission's docket (`policy_actions`, `large_load_rules`); FERC's eLibrary for a wholesale contract |
| AI or datacenter power | `ai_power` | 505 (a flag on every row; 194 true) | 16 (none true) | | held |
| The evidence | `energy_deals_evidence` (one sentence a story, internal) | 557 rows | 16 rows, all World Nuclear News | the sentence is outlet text, not shown | a filing's own text could be shown (a government's and a regulator's words are public) |

Counts of the "Stated" column are from `warehouse/output/energy_deals.csv` as it stood (27 rows with `mw`, 269 with `dollars`, 45 with `state`, 17 with `term_years`, 419 with `status`); the shown rows' from `docs/reviews/deals-public-rows-2026-10-23.md`.

## What a public filing in the evidence gives, for the shown rows

Nothing beyond the story. The 16 shown deals' public evidence rows are 16 World Nuclear News articles (an outlet whose terms the ERW reads as public; a news article, not a filing). The deals' `story_ids` name four more outlets for three of them, every one asking for permission, and the DOE newsroom for Vistra's loan (a government page; its story is not in the evidence table). No row of `energy_deals_evidence` is a regulator's or an ISO's filing or a company's own announcement, because the deals' feeds are news feeds. So no held field was drawn from a filing in this session, and the "drawn from a public filing" path of the tracker has no row to draw until the data machine adds a filing source.

## What the data machine would add, in order

1. **FERC EQR, joined to the deals** (session 825 reads it; the tables `ferc_eqr_contracts`, `ferc_eqr_contract_terms`, `ferc_eqr_buyer_names` are in the warehouse): the filed product, rate, rate units, quantity, delivery point and dates for every wholesale contract a seller files, each quarter. The join is by the parties' names and the quarter; its precision is session 825's measure. The tables are internal by the ERW's own record (`docs/licenses.md`, FERC's page not yet read for the EQR), so the panel shows "license needed" until the owner's ruling.
2. **The companies' own announcements**: a press-release feed for the parties the deals name most (the buyers and sellers of `energy_companies`), read from each company's own newsroom page, and the 8-K exhibits of the listed ones through EDGAR's public full-text search. A company's page is its own words; `docs/licenses.md` gives the nine datacenter operators' pages the verdict "needs written permission" today, so each newsroom's terms are read first.
3. **The ISOs' and utilities' filings**: an interconnection agreement names the plant, its node, its MW and its in-service date (the queue tables hold the node for a queued plant already: `*_interconnection_queue`, `datacenter_queue_positions`); a large-load tariff names the curtailment and the minimum-take terms (`large_load_rules`, `large_load_statements`).
4. **DOE's Loan Programs Office** for the federal loans the deals name (Vistra's USD 4.2 billion): the amount, the term and the conditions, on a public domain page.

## Decisions made without you (session 824)

- The fields are the reports' and the roles' words, not an industry template: AG's section 4 and Key Findings row 3, DR's roles section. A field neither names (the credit terms) is listed because the Power Trading Lead's posting names risk management.
- "Drawn from a public filing" was tested against the evidence table and found empty; nothing was invented to fill it.
- The sources are listed with the warehouse table that holds each where one exists, so the data chain starts from a table, not a pull.

## For Samuel's ruling

- Whether the EQR tables' flag moves from internal to public once FERC's page is read (the filed terms are the one source for the price structure, the settlement point and the dates).
- Whether a press-release feed for the deals' parties is a pull the data machine may make (each newsroom's terms read first).
