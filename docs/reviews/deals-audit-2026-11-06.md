# The deal tracker and the datacenter tracker: the audit of 6 November 2026

Energy Research Warehouse (ERW), chain 156 (`queue/done/156-night-6-november-portable-deals-datacenters.md`), portable-laptop, the code role. Session 2230 wrote the ground; session 2231 the audit of the stored records; sessions 2232 to 2251 add their rows. Every count below was read from the files of main at `c750ce225` (6 November 2026, about 07:20 UTC), whose two tables were last written by the daily run `20261105T234321Z` and `20261105T234404Z`.

## Ground (session 2230)

### Where the code lives

The prompt names `warehouse/news/deals*.py` and `datacenters*.py`. The extraction is not there: it is in two folders of its own, and this chain reads the prompt's list as those folders.

| File | What it does |
|---|---|
| `warehouse/deals/extract.py` (575 lines, session 15) | Clusters of scored stories (sectors deal, ppa, capital, nuclear, generation, datacenter_power, lng, oil, gas; significance 5 or more) sent 12 a call to the Sonnet-class model with a JSON schema; every number kept only if its span is in the title or summary and parses to the same value; state, country and status only from their spans (session 16's ruling); `same_as` against the newest 250 deals; writes `energy_deals` (public by its own header) and `energy_deals_evidence` (internal) and `warehouse/deals/checked.csv` |
| `warehouse/deals/deal_parties.py` (session 531) | One deal across days in code: same type and two parties within 30 days, an asset sharing a word, sums within a quarter; two governments are not a deal; a party the story does not name is dropped |
| `warehouse/deals/duplicates.py`, `duplicates.csv` | The register of folded pairs, a person's choice |
| `warehouse/deals/public_rows.py` | The rows whose evidence rests on a publisher read as public (the shown subset) |
| `warehouse/deals/eval/` | `eval_sample.csv`, `sample.py`, `score.py`, `spot_check_s15.csv`: session 15's spot check |
| `warehouse/datacenters/extract.py` (session 16) | Scored stories of sector `datacenter_power`, any significance; facilities with operator, developer, site, state, county, city, MW, phase, status, planned year, power source, utility; each value kept only as stated; `same_as` accepted only on the same operator or developer, site, or county or city in the state (session 166); writes `datacenter_projects` and `datacenter_projects_evidence` |
| `warehouse/derived/datacenter_facilities.py` | Joins `datacenter_projects` with the nine operators' site lists and the queues: the table the page reads |
| `warehouse/companies/seed_from_deals.py` | Every party of a deal becomes a row of `energy_companies` (tool 10) |

The prompts are the `SYSTEM` strings of the two extractors (no separate prompt file); the schemas are their `SCHEMA` dictionaries. The daily sequence runs `model_step deals`, `run_other companies_from_deals`, `model_step datacenters`, `run_other datacenter_facilities` in that order (`warehouse/run_daily.sh`, lines 317 to 325).

### The two tables

| Table | Rows | Evidence rows | Last written | License (`license_status.csv`) |
|---|---|---|---|---|
| `energy_deals` | 529 | 585 | 2026-11-05 23:43 UTC | license needed since 21 October (outlet terms, session 205) |
| `datacenter_projects` | 163 | 183 | 2026-11-05 23:44 UTC | license needed since 21 October |

`energy_deals` has 33 columns (the events shape, then `deal_type`, `buyer`, `seller`, `other_parties`, `asset`, `technology`, `state`, `country`, `mwh`, `dollars`, `price_value`, `price_unit`, `term_years`, `announced_date`, `date_basis`, `ai_power`, `confidence`, `n_stories`, `story_ids`, `story_urls`, `model_id`, `extracted_at`). `datacenter_projects` has 36 (the entities shape, then the extractor's).

Rows by ISO week of `event_date` (deals) and `first_story_at` (facilities):

| Week | W36 | W37 | W38 | W39 | W40 | W41 | W42 | W43 | W44 | W45 |
|---|---|---|---|---|---|---|---|---|---|---|
| deals | 4 | 7 | 1 | 27 | 40 | 41 | 32 | 38 | **0** | 11 |
| facilities | 0 | 0 | 0 | 3 | 22 | 25 | 22 | 28 | **1** | 5 |

Stories sent, by day of `checked_at` (`warehouse/deals/checked.csv`, `warehouse/datacenters/checked.csv`): every day from 4 to 25 October (deals 33 to 114 a day, facilities 2 to 69), **then none from 26 October to 4 November**, then 64 and 44 on 5 November. The last day with new rows before the gap: deals 24 October (518 in the table after the run of 25 October, which checked 4 stories and added none); facilities 25 October (157).

How full the deal rows are (529): buyer 373, seller 425, technology 276, dollars 277, country 89, state 50, **mw 30**, term_years 18, mwh 3, **price in USD per MWh 0**, price_value 2 (both not prices of energy: "CAD/share" and "%"), announced_date 1. Status: signed 165, announced 133, empty 89, closed 78, rumored 55, cancelled 9. AI-power true 197, false 332. Confidence: median 0.60, quartiles 0.55 and 0.80, range 0.30 to 0.95. Types: m_and_a 135, other 81, equity_raise 81, fuel_supply 53, debt 50, ppa 33, joint_venture 29, offtake 27, project_finance 23, lease 10, behind_the_meter 3, smr 3, nuclear_restart 1. Model: claude-sonnet-5-5 338, claude-sonnet-5 191.

How full the facility rows are (163): operator 113, developer 74, city 64, state 52, mw 45, site_name 34, power_source 20, planned_year 9, county 8, utility 5. Status (the extractor's word): empty 79, announced 45, under_construction 13, applied 9, cancelled 7, permitted 5, operating 5.

### The daily step's last ten runs (`warehouse/metadata/run_status.csv`, the health summaries)

| Run | deals | datacenters | First error line |
|---|---|---|---|
| 20261021T15 | ok, 61 stories, 497 in table | ok, 33 stories, 145 | |
| 20261022T15 | ok, 53, 505 | ok, 30, 150 | |
| 20261023T15 | ok, 49, 514 | ok, 26, 154 | |
| 20261024T15 | ok, 33, 518 | ok, 17, 156 | |
| 20261025T14 | ok, 4, 518 | ok, 2, 157 | |
| 20261026T15 | **failed** | **failed** | `RuntimeError: all 1 calls failed` |
| 20261027T14 | failed | failed | same |
| 20261028T15 | failed | failed | same |
| 20261029T14 | failed | failed | same |
| 20261030T15 | failed | failed | same; the 3-run failure streak raised for both |
| (31 October to 4 November) | no run | no run | the daily workflow did not run on these days (no row of either step, nor of `eia_fuels` or `news_score`) |
| 20261105T23 | ok, 64 stories, 529 | ok, 44, 163 | |

The step's own line hides the cause. The cause is in the same run's other model steps: `news_brief` printed "You have reached your specified API usage limits. You will regain access on 2026-11-01 at 00:00 UTC", and `news_score` scored 0 of 400 with 16 calls failed. The extractor counts the failed call and raises `all 1 calls failed`, without the API's words; the health line says the same. The scorer still left **1,092 stories unscored** after the run of 30 October, and only scored stories are sent to the extractors, so the backfill of 27 October to 5 November depends on the scorer's backlog first (session 2237).

### The pages today (both `review` in `site/lib/release.ts`; a visitor sees the in-review page)

- `/deals` (tabs `?tab=deals|tracker|companies`, `lib/tabs.ts`): the deals in a sortable table with the month's count, MW and AI share (`DealsTable.tsx`); the tracker (`v2/view.tsx`) by type, technology, grid, counterparty and year, with the kinds of tool 6 read from fields (session 465); the comparables (`?view=comparables`, session 466: counts and medians of disclosed price and MW by type, technology, grid or year, nothing from fewer than three); the companies tab; the decisions block (`Decisions.tsx`); the downloads of `energy_deals` and `news_stories`. Under the hold every view draws the hold's words and the row count (`catalogue|energy_deals|n_rows`) and no row; the internal view (the cookie) draws the rows.
- `/datacenters` (`?view=facilities|grids`): the facilities of `datacenter_facilities` (the joined table, held whole) with the power side drawn whether or not the table can be read (session 467), the large-load panel, the view by grid with the queues and the grid's prices (session 468); downloads of `datacenter_facilities`, `datacenter_operator_sites`, `datacenter_projects`, `ercot_large_load_status`.
- Unlanded, on origin: `wip/833-deals` (chain 080 and chain 084, 18 commits: the shown public rows `site/data/deals_public.json` and `datacenters_public.json`, the EQR join `warehouse/deals/eqr_join.py`, the A and B compare, the method notes' "What is shown and what is held") and `wip/130-deals-v3` (session 130's `/deals/v3`, 1 commit, superseded by the tracker). Neither is an ancestor of main.

### What the Roundup reads (`warehouse/news/roundup.py`, the old laptop's chain 154 owns it)

- The week's deals: rows of `energy_deals` whose `event_date` falls in the week, under the floor (`confidence` 0.7 or more and one of `buyer`, `seller`, `asset`, `mw`; US first; session 2702); printed fields `event_date`, `deal_type` (through `DEAL_LABEL`), `buyer`, `seller`, `asset`, `mw`, `dollars`, `status`, `story_urls`; the deal of the week is the largest by `dollars` (by `mw` when none states dollars), keyed by `event_id`.
- The week's facilities: rows of `datacenter_projects` whose `first_story_at` falls in the week, under the floor (`confidence` 0.7 or more and one of `operator`, `site_name`, `mw`); printed fields `first_story_at`, `operator`, `site_name`, `city`, `county`, `state`, `capacity_mw` (else `mw`), `project_status`, `story_urls`; the largest new load keyed by `entity_id`.
- **These names keep their meaning in this chain**: a new field is added beside them, never in place of one (the prompt's rule).

### Chain 024's decisions on the deal tracker and comparables

- Session 531 (chain 024, the Roundup audit's fix 8): one deal across days, matched in code (`deal_parties.same_deal`), two governments not a deal, an unnamed party dropped; the rules change later extractions, not the stored rows; folding the stored rows is the register's.
- The comparables (session 466, chain 019, beside it): nothing computed from fewer than three disclosed deals; a median is of stated figures only; a deal stating none is left out, never zero; the chart shows the median price where a group has three prices, else the median size, and says so. On the 492 rows of 20 October no group stated three prices; on the 529 of 5 November no deal states a price in USD per MWh at all.
- The rulings of 23 October (`docs/reviews/deals-rulings-2026-10-23.md`): items 1 to 6 and 9 open, 7 ruled and done (a revised figure is a note), 8 answered in practice, 10 done.

## The audit of the stored records (session 2231)

**The sample.** `energy_deals` sorted newest first (`extracted_at`, then `event_date`), every fifth row of the newest 600: the table holds 529, so **106 deals** (D001 to D106). `datacenter_projects` sorted the same way, **60 facilities** spread evenly over its 163 rows (F001 to F060). Each row was read against its stories' stored title and summary (the only text the warehouse holds of a story: the median summary is 77 characters, so most rows rest on a headline), by three readers working from one rubric, the rows' own fields and the stories' words only; six of their calls were read again by the session (D010, D021, D046, D094, F006, F051), all confirmed. The sample with every row's grade and note: `docs/reviews/deals-audit-2026-11-06/` (`sample_deals.csv`, `sample_facilities.csv`, the rubric in its README).

**What the extraction cannot see.** Of 18,358 scored stories, 6 state a price per MWh, kWh or "per megawatt-hour" in their title or summary (3 gas, 1 storage, 1 grid conditions, 1 power prices). A disclosed price is therefore almost never in the stored text, whatever the extractor does: the comparables (session 2239) can only be as full as the stories are. Terms in years, MWh and points of delivery are as rare.

### The deals: fault classes (106 rows)

| # | Class | Rows | Share | Three examples (the story's words) |
|---|---|---|---|---|
| 1 | Place missed (a country or US state the story names, row empty) | 17 | 16% | D002 "supporting development of the Bahamas LNG hub"; D006 "planned UK BWRX-300 fleet"; D024 "Perry plants in Ohio" (only PA kept) |
| 2 | Status missed (the words state it, row empty) | 14 | 13% | D026 "Seals Acquisition"; D030 "Strike ... 1.7-GW Mobile Gas Power Deal"; D058 "to Buy" |
| 3 | Not a deal (a plan, a pledge, a seeking, a permission, government talks) | 12 | 11% | D022 "Black Hills plans $1.8 billion investment"; D035 "SoftBank pledges 75bn euros to build"; D048 "DayOne Seeks to Boost Loan to Record $7 Billion" |
| 4 | Kind wrong, or the vocabulary has no word for it (gas buildout, pipeline, compute capacity) | 11 | 10% | D021 stored ppa: "Big Step Toward Hyperscaler PPA", "1.2 GW Natural Gas Power Push" (a gas buildout, not yet a PPA); D005 stored other: "$580 million US gas pipeline order"; D059 stored offtake: "OpenAI, Amazon Sign $38 Billion Cloud Deal" (compute, not energy) |
| 5 | A party is a description, not a name | 7 | 7% | D040 "Investors push for higher yield"; D041 "lease with US hyperscaler"; D054 "Fusion Startup Raises $450 Million" |
| 6 | AI-power tag wrong | 6 | 6% | D010 false on "AEP signs 960-MW Indiana nuclear pact with Amazon, X-energy"; D042 false with AirTrunk (a datacenter operator) buying; D037 true on "as AI demand booms" with no AI party |
| 7 | A party wrong (not a party, or the roles swapped) | 4 | 4% | D046 Meta as seller: "Meta Agrees to Fund Local Energy Infrastructure"; D070 Nvidia as a party: "Nvidia-backed Firmus"; D103 a rival bidder: "outbidding Norway's DNO" |
| 8 | MW missed | 3 | 3% | D023 "adding 181MWdc of solar"; D047 "Half-GW, Gas-Fired Permian Power Plant"; D066 "1 gigawatt AI data centre" |
| 9 | Confidence too low on a clean deal | 3 | 3% | D004 0.5 on "STTGDC to host Neysa GPUs at data center"; D080 0.4 on "Brookfield, Nuclear Company to form joint venture"; D095 0.55 on "Deutsche Telekom, Nvidia to launch $1.2 billion AI cloud" |
| 10 | USD missed | 2 | 2% | D019 "Sold for About $1 Billion"; D031 "GBP3.6 billion (USD4.8 billion)" |
| 11 | USD wrong (another sum of the story) | 2 | 2% | D069 "$15 billion in AI infrastructure" kept as the nuclear purchase; D071 "valued at $2.4 billion" kept as the sum raised |
| 12 | Price wrong (not an energy price) | 1 | 1% | D094 "seeks 80% equity selldown" kept as price 80 "%" |
| 13 | Term missed | 1 | 1% | D032 "22-Year LNG Contract to Supply Petrobras" |
| 14 | Status unsupported | 1 | 1% | D077 "Putin Allows TotalEnergies to Sell 10% Stake" kept as announced |
| 15 | A party missed | 1 | 1% | D026 the seller of "Acquisition of EnCap Delaware Basin Assets" |
| 16 | Confidence too high on a faulty row | 1 | 1% | D054 0.75 with no party named |
| - | MW wrong, MWh, price missed, place wrong | 0 | 0% | no figure in the sample is invented or of the wrong value: every figure fault is a figure missed or a figure of another sum |

The readers' calls to note: debt deals put the lender as buyer in some rows and the borrower in others (D011, D024 against D027), a fault the rubric did not count; fund closes and IPOs with no investor named were counted as deals (D008, D009, D016, D036, D038); a sum stated only in euros was correct as empty (D036).

### The facilities: fault classes (60 rows)

| # | Class | Rows | Share | Three examples (the story's words) |
|---|---|---|---|---|
| 1 | MW stated without saying whether it is IT load or total | 14 | 23% | F003 "1GW data centre complex"; F005 "225MW off-grid data center in Zaragoza, Spain"; F006 "Nebius signs on for 50MW" (a tenant's share, not the facility) |
| 2 | Status missed | 9 | 15% | F010 "planned data center in the state"; F013 "launches first phase"; F041 "on track to go live in mid-2026" |
| 3 | Confidence too low on a clean row | 6 | 10% | F042 0.5 on "Amazon's Chile data center moves ahead"; F039 0.5 on "Pauses Wyoming Site"; F019 0.4 on "AI supercomputer in Sweden" |
| 4 | Not a facility (a company-wide plan, no site) | 5 | 8% | F017 "proposed 6MW data center acquisition" (no place); F040 "Plow $52 Billion Into French Data Centers"; F057 "$19 billion data center lease deal with Anthropic" |
| 5 | State missed | 5 | 8% | F010 "Indiana utility NiSource for planned data center in the state"; F032 "NJ data center"; F046 "rent Texas data center" |
| 6 | Operator missed | 3 | 5% | F002 "the Sky Data Centers site in Santa Rosa"; F015 "Brookfield, NextEra to Build $100 Billion AI Hub"; F036 "Balearic Islands launches new data center" |
| 7 | Status wrong | 3 | 5% | F035 under_construction on "First project planned"; F051 announced on "increased Tennessee gas turbines"; F053 cancelled from "OpenAI halts Stargate UK" applied to other sites |
| 8 | Two or more facilities folded into one row | 3 | 5% | F051 xAI's Memphis site and "Mississippi data center"; F053 several Stargate sites; F056 AWS Mexico with a UAE data center |
| 9 | Operator wrong | 2 | 3% | F028 "Duos still owns facility"; F050 "TikTok owner weighs" (the row says TikTok) |
| 10 | Power source missed | 2 | 3% | F010 "20-year power deal"; F032 "unpermitted generator fleet" |
| 11 | Timeline missed | 2 | 3% | F018 "due to be delivered next year"; F027 "Fit Energy on October 6 said" |
| 12 | Site missed | 1 | 2% | F027 "Newport Township, Luzerne County" |
| 13 | A year of another event kept as the facility's | 1 | 2% | F010 planned_year 2028 from "Will commence in 2028" (the power deal's start) |
| - | MW missed or wrong, utility, confidence too high | 0 | 0% | |

### Duplicates (the whole tables, in code: `deal_parties.same_deal` and two looser tests)

| # | Pair | Why one deal | State |
|---|---|---|---|
| 1 | `deal:29c1d07b7456f089` (2026-10-02, "US" lends Vistra USD 4.0 billion) and `deal:70bf30d372e1d674` (2026-10-05, "Department of Energy", USD 4.2 billion, 433 MW) | the Roundup audit's fix 8 pair: the code's rule matches it, the register does not fold it | open: not in `duplicates.csv` |
| 2 | `deal:6d416fb10be3a6f0` (2026-09-30, Amazon and Constellation, 190 MW) and `deal:3768a40d6f7e3242` (2026-10-06, "nuclear expansions") | the audit's second pair | open: not in the register |
| 3 | `deal:a56c03853279fd07` (Petrobras and Sempra, LNG, 2026-09-29) beside `deal:f2dc6da3fa975d52` (Petrobras and Cheniere, the same day and story) | one story, one LNG deal: Sempra is read from a story whose link is "cheniere-petrobras-seal-long-term-lng-spa" (the Roundup audit's W40 note) | open |

The looser tests found no other repeat: Google and SpaceX (a lease of 5 June and the orbital project of 12 May), Anthropic and Google (the cloud contract of 6 May and the equity of 24 April), Japex's two acquisitions of one story (Verdad and Fundare) and Google's two PPAs of one story (AES and Xcel) are each two deals. Facilities: no two rows share an operator and a place; one pair shares an operator and a state (Google in Texas, `datacenter:0ae5b4f73b7c8038` at Amarillo and `datacenter:f2eedf98a66d7f0a` with no place), not enough to fold. The register holds 3 folds and 3 doubtful pairs (session 113). None of the six rows of the three open pairs fell in the sample; 3 of the 60 sampled facilities fold several facilities into one (class 8), the opposite fault.

### Why the Roundup of W44 printed empty tables

The Roundup of 2026-W44 (26 October to 1 November) prints the rows of `energy_deals` whose `event_date`, and of `datacenter_projects` whose `first_story_at`, falls in the week. No story of the week was sent to either extractor: the step failed on 26, 27, 28, 29 and 30 October (`RuntimeError: all 1 calls failed`: the API's spending limit, "You will regain access on 2026-11-01 at 00:00 UTC", which only the digest's line printed), and the daily run did not run from 31 October to 4 November. The scorer had stopped too (0 of 400 scored on 30 October, 1,092 left unscored), and only scored stories are eligible. So W44 holds 0 deals and 1 facility (dated in W44 by a story that reached the table on 5 November), and the tables printed were empty, not wrong: the week's deals were never extracted. Session 2237 makes a failed day a plain health line with the API's words; the backfill (the desktop's) fills the days.

### Rows for the sessions that follow

| Row | Class (from the tables above) | Session | State |
|---|---|---|---|
| A1 | Deals: place missed (17) | 2232 | open |
| A2 | Deals: status missed (14), unsupported (1) | 2232 | open |
| A3 | Deals: not a deal (12) | 2232 | open |
| A4 | Deals: kind wrong or no word for it (11) | 2232 | open |
| A5 | Deals: a party a description (7), wrong (4), missed (1); the lender and borrower roles | 2234 | open |
| A6 | Deals: AI-power tag wrong (6) | 2232 | open |
| A7 | Deals: MW missed (3), USD missed (2), term missed (1) | 2235 | open |
| A8 | Deals: USD of another sum (2), a share kept as a price (1) | 2235 | open |
| A9 | Deals: confidence too low (3) or too high (1) | 2232 | open |
| A10 | Deals: the three open duplicate pairs | 2233 | open |
| A11 | Facilities: MW basis unstated (14) | 2236 | open |
| A12 | Facilities: status missed (9) or wrong (3) | 2236 | open |
| A13 | Facilities: not a facility (5); several folded into one (3) | 2236 | open |
| A14 | Facilities: state (5), operator (3 missed, 2 wrong), site (1), power source (2), timeline (2), a year of another event (1) | 2236 | open |
| A15 | Facilities: confidence too low (6) | 2236 | open |
| A16 | The step's failure line hides the API's words; a failed day is not a plain health line | 2237 | open |

## Session 2232: the schema and the prompt, on the fixture

The fixture: `tests/fixtures/deals/stories_2232.json`, 40 stored stories in 36 clusters (30 rows the audit found faulty, 6 clean), with answers written from the stories' own words (`answers_2232.json`, each with the words it rests on). The new prompt's answers recorded once (`recorded_2232.json`, claude-sonnet-5-5, 3 calls, USD 0.1227) and replayed through the extractor by `tests/test_session2232_deals.py`, offline. The same answers graded against the stored rows give the count before.

| Class on the fixture | Before (the stored rows) | After (the new prompt and code) |
|---|---|---|
| A deal kept where the story reports none (of 9) | 7 | **0** |
| A stated deal missed (of 25 deals, 2 either way) | 0 | 2 (Volta's raise at a valuation; the US government's stakes in Lithium Americas: the model returned no deal) |
| A figure invented or of another sum | 2 (a valuation, a company-wide investment) | **0** |
| A percentage kept as a price | 1 (graded on the audit's sample) | **0** |
| AI-power tag wrong | 3 (Amazon and AEP, STTGDC and Neysa, AirTrunk) | **0**: the rule in code, every tagged row with its basis |
| Country missed | 4 | 1 (the UK fleet of BWRX-300s) |
| A party a description or wrong (rows) | 3 (D040 "Investors", D041 "US hyperscaler", D046 Meta) | 1 (D046: Meta as the seller of what it pays for) |
| MW missed | 1 | 0 |
| Kind wrong or no word for it | not a field before | 0 (gas buildouts and compute capacity now have their kinds) |
| Stage wrong | not a field before | 0 |

"Half-GW" stays without MW: a figure with no digits is not converted (session 16's ruling); the audit's reader counted it missed.

**Correction to the duplicates (pair 3).** The Cheniere story's own summary says "Earlier Sempra announced a 20-year agreement to also supply about 0.8 MMtpa of LNG to the Brazilian state-owned company": Sempra's row is a second deal the story states, not a misread of Cheniere's. Pair 3 is not a duplicate; session 2233 marks it so.

| Row | State after session 2232 |
|---|---|
| A1 place missed | fixed on the fixture (4 to 1); the UK case open |
| A2 status missed or unsupported | `stage` added with its span; 0 wrong on the fixture; `status` unchanged for the Roundup |
| A3 not a deal | fixed on the fixture (7 to 0) |
| A4 kind | fixed: `kind` (tool 6's kinds, power kinds first, `compute_capacity` for the ruling) |
| A6 AI-power tag | fixed: the rule in code (`fields.ai_of`), its basis on the row |
| A8 a share kept as a price | fixed in code (`fields.energy_price`); the sum of another figure fixed by the prompt on the fixture |
| A9 confidence | the prompt gives the bands and asks for the words (`confidence_basis`, in the evidence table); graded again in session 2249 |
