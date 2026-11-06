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

## Session 2233: one record a deal

`warehouse/deals/dedupe.py` (new), called by the extractor for every deal the model does not mark `same_as`: session 531's rule, and four more, each from a case of the fixture (`tests/test_session2233_deals.py`, twelve stored stories about four deals, each its own cluster on its own run, the fake model never marking `same_as`):

| Rule | The case | Before | After |
|---|---|---|---|
| One party named on one side, a size both state agreeing, the assets sharing a word or the MW agreeing | the DOE's own release names no borrower ("Energy Department Announces $4.2 Billion Investment"); WNN names only "American Electric Power" | two records each | one |
| A name and its initials | "AEP" and "American Electric Power" | two | one |
| A later stage within a year | "Williams Closes $5.5B Momentum Deal", 32 days after the signing | two (the 30-day window) | one, stage closed |
| The size within tolerance (USD a quarter, MW a tenth) | Devon and Coterra at USD 21.5 and 21.4 billion; the combined company's USD 58 billion is not the purchase | one (the model left the 58 out) | one; a stated 58 would keep two apart |

Twelve stories make **four records**, each with its three sources; the earliest first-reported date; a later stage replaces the record's `stage` and `status`, and every change is in the new column `status_history` ("2026-10-19 rumored (first record); 2026-10-19 announced (news:...); 2026-10-19 signed (news:...)"); a figure the record lacks is filled, one it holds is never replaced.

**The stored table** (529 rows, read only): the new rules find the same two pairs as the audit, and no other. Both are now folds in the register (`warehouse/deals/duplicates.csv`, 5 folded, 3 doubtful: 524 deals once the folds are one), and `site/data/deal_duplicates.json` is rebuilt from it. Pair 3 (Sempra and Cheniere) is two deals (session 2232's correction).

| Row | State after session 2233 |
|---|---|
| A10 the open duplicate pairs | done: pairs 1 and 2 folded in the register; pair 3 not a duplicate; the extraction folds such pairs itself from now on |

## Session 2234: the counterparties

`warehouse/deals/counterparties.py` (new) gives every deal `buyer_name`, `seller_name` (canonical), `buyer_parent`, `seller_parent` (a second field) and `buyer_eia861`, `seller_eia861`, and builds the directory `deal_counterparties` (the seed of the company database, tool 10; method note `docs/methods/deal_counterparties.md`; held as `energy_deals` is). Run read only over the stored 529 deals (to the scratchpad, not `warehouse/output`):

- **481 counterparties** from 505 spellings: 416 companies, 44 AI buyers, 21 governments; 109 with two or more deals. Joined: Constellation and Constellation Energy (5 deals, 3,790 MW stated by 2), NextEra and NextEra Energy, AES and AES Corp, Viper, Kairos, Glenfarne, MidOcean, Crescent, Ithaca, Singtel; AEP and American Electric Power (6 deals, by `aliases.yaml` and its story); the US government (16 deals, 8 spellings).
- **Descriptions left out** (the audit's class 5): "investors" (10 fields), "banks" (3), "lenders", "owners", "a startup".
- **Fields of several parties split** ("Nvidia, Dell", "Apollo and Blackstone", "BP, Woodside and Chevron"): each party counted.
- **Parents** only where the words show them: 11 (ADNOC's XRG, BlackRock's GIP, Blackstone's QTS, EIG's MidOcean, MAIRE's Tecnimont, the units of Amazon, Constellation Energy, OGE Energy, Aditya Birla, Geely Holding, General Motors' venture arm), plus Amazon Web Services by alias. A first word shared (Related Digital and Related Companies, Golar LNG) gives none.
- **EIA-861 numbers: 0 matched.** The deals name holding companies (Duke Energy, Entergy, Dominion Energy, AES, Black Hills, NiSource), each the first words of several operating utilities in EIA-861, and the stories do not say which. Session 2250 reads the names with two or more deals for aliases a story shows.

| Row | State after session 2234 |
|---|---|
| A5 a party a description, wrong or missed | the descriptions are out of the directory and the prompt (session 2232) no longer returns them; the lender and borrower roles follow the extractor's rule (the lender is the buyer); a party wrong stays a fault of the extraction (session 2249 reads it again) |

## Session 2235: the figures cross-checked

`warehouse/deals/crosscheck.py` (new) reads every record's headlines again after it is built and writes what it finds to the record's `flags` (never changing or dropping a figure): a headline's MW, MWh or US dollars against the record's (a valuation, a combined company's value, a company-wide investment not compared); MW against MWh and USD against USD per MWh; a term the words state in months (left empty, flagged); the sanity bounds (MWh raised to 50 TWh: TotalEnergies and Airbus's 3.3 TWh contract is a real figure). The extractor flags every record on every run, so a record's flags follow its stories.

Over the stored 529 deals (read only, the stories' headlines of `news_stories`): **14 records flagged**.

| Flag | Records | Examples |
|---|---|---|
| A headline's MW the record lacks | 6 | "Liberty Inks 1.2-GW 'Critical Milestone' Deal"; "Google is purchasing a gigawatt of distributed capacity in PJM"; "Constellation-Google deal will bring $4.3B investment, 890 MW new nuclear to PJM" |
| A headline's USD the record lacks | 4 | "Oryx Energies Sold for About $1 Billion"; "Meta and AMD Agree to AI Chips Deal Worth More Than $100 Billion" |
| A headline's USD the record contradicts | 2 | Volta: the record holds the USD 2.4 billion valuation, the second headline "$10 billion AI partnership"; NIO and Geely: "more than $2 billion" against USD 2.4 billion |
| A headline's MW the record contradicts | 1 | "TotalEnergies, KKR Add 700 MW to US Solar JV": the record holds 2,100 MW |
| Above a bound | 1 | "SpaceX buys xAI in $1.25tn deal": USD 1.25 trillion |

| Row | State after session 2235 |
|---|---|
| A7 MW, USD and term missed | every such record now carries a flag naming the headline's figure; the figure itself is filled only by a later extraction whose span checks (the prompt of session 2232) |
| A8 a sum of another figure, a share as a price | the prompt (2232) and `fields.energy_price` stop them at extraction; the cross-check flags a stored record that holds one (Volta) |

## Session 2236: the datacenter facilities

New columns of `datacenter_projects` (`warehouse/datacenters/facility_fields.py`, the method note's "The columns of session 2236"): `mw_basis`, `power_kind`, `grid` with `grid_basis`, `utility_eia861` with its number and `utilities_in_county`, `energized_year`, `country`, `fields_version`. Three rules: a facility needs a stated place; two places are two facilities; a description is not an operator. The rollups by grid, state and operator: `datacenter_tracker_rollups` (`warehouse/derived/datacenter_tracker_rollups.py`, validator: pass).

The fixture (`tests/fixtures/datacenters/`): 35 stored stories in 28 clusters from the audit's sample, answers from their words, the new prompt's answers recorded once (claude-sonnet-5-5, 3 calls, USD 0.0933), replayed by `tests/test_session2236_deals.py`.

| Class on the fixture | Before (the stored rows) | After |
|---|---|---|
| A facility kept where none is (no place) | 2 (F017, F057) | **0** |
| Two places in one row (pairs, each way) | 6 (xAI TN and MS; AWS Mexico and UAE) | **0** |
| A facility missed | 0 | 1 (DataOne's NJ facility: the model gave no state, so no place) |
| State wrong or missed | 3 | 1 (Columbus, Georgia) |
| Status wrong or missed | 3 | 1 (JERA at Chiba: "building data centre" and "First project planned", two clusters joined) |
| A year of another event kept | 1 (F010's 2028, the power deal's start) | **0** |
| Operator a description or wrong | 1 ("TikTok") | **0** |
| MW basis | not a field before | 0 wrong (Nebius's 50 MW is a tenant's share; Fermi's 222 MW a phase) |
| Energized year | not a field before | 0 wrong (Microsoft India 2026) |

The stored 163 facilities rolled up (read only, to the scratchpad): 45 state MW (26,636 MW summed, every basis); 132 have no grid; ERCOT 11 facilities (4 with MW, 457 MW); PJM 10 (1, 18 MW); MISO 4 (none with MW); the operators with the most: Microsoft 11 (none with MW), Meta 9, Google 8 (1, 702 MW), Nebius 5.

| Row | State after session 2236 |
|---|---|
| A11 MW basis unstated | `mw_basis` asked with its words; the stored rows read `unstated` until a re-extraction |
| A12 status missed or wrong | the prompt's status words widened (launches, goes live, halts); 3 to 1 on the fixture |
| A13 not a facility, several folded into one | fixed on the fixture (2 to 0; 6 to 0) |
| A14 state, operator, site, power source, timeline, a year of another event | `energized_year` and `country` added; a year of another event out; operator descriptions out; state 3 to 1 |
| A15 confidence too low | the prompt's bands; read again in session 2249 |

## Session 2237: the daily step, end to end, offline

**The failure mode of 26 to 30 October, fixed** (`warehouse/deals/calls.py`, used by both extractors). The spending limit stops the run at its first call with the API's words in the health line ("the API's spending limit: You have reached your specified API usage limits. You will regain access on 2026-11-01 at 00:00 UTC"), not "all 1 calls failed"; a refusal or an answer that is not the schema's JSON is tried once more; a busy API twice more, 10 and 30 seconds apart. When no call answers, **no table is rewritten** (no header claims a day's retrieval it did not make) and every story stays to be sent again. Tested in `tests/test_session2237_deals.py`.

**One stored day, end to end** (`warehouse/deals/eval/one_day.py`): the 42 deal stories and 32 datacenter stories of 5 November, sent again with the new code against copies of every table held (the old columns upgraded in place on the way), in a temporary folder, the real model (claude-sonnet-5-5).

- **Sent again as they stand**: 4 deal calls (USD 0.1822) and 3 datacenter calls (USD 0.0854): **no new row**: every story joined the deal or facility it had made on 5 November (the reference list and the deduplication), so a day sent twice makes no duplicate.
- **As a first run** (that day's 8 deals and 4 facilities taken out of the copies first; USD 0.1716 and 0.0780): 8 deals and 4 facilities again. Against the stored eight: Google is now the party of "Google to serve as credit backstop for TeraWulf data center in Kentucky" (stored with no buyer); Entergy's "Arkansas data center deal" is tagged AI by its load (stored false); Eneva's "LNG-to-power move" is a gas buildout; Return's "835 million" financing in euros no longer carries USD 938 million, a sum its headline does not state, and it is a storage deal, financed, in Germany; the Belgian state and Engie are in Belgium. One false flag found and fixed: "targets 1GW annually" is a rollout's pace, not the deal's MW (`crosscheck.py` now skips a figure a year or a target).

**The backfill** (`scripts/deals_backfill.py --from 2026-10-27 --to 2026-11-05 --dry-run`, read 09:02 UTC on 6 November):

| Day | Stories | Unscored | Deal stories expected | Datacenter stories expected |
|---|---|---|---|---|
| 2026-10-27 | 502 | 502 | 53.1 | 28.9 |
| 2026-10-28 | 505 | 505 | 53.4 | 29.0 |
| 2026-10-29 | 523 | 523 | 55.3 | 30.1 |
| 2026-10-30 | 277 | 277 | 29.3 | 15.9 |
| 2026-10-31 to 2026-11-03 | 0 | 0 | 0 | 0 |
| 2026-11-04 | 102 | 23 | 2.4 | 1.3 |
| 2026-11-05 | 529 | 208 | 22.0 | 12.0 |

| Step | Stories | Calls | USD (estimate) |
|---|---|---|---|
| score (`warehouse/news/score.py`) | 2,038 | 82 | 1.93 |
| deals | 215.5 | 17 | 0.74 |
| datacenters | 117.2 | 11 | 0.26 |
| **total** | | | **2.93** |

The shares are those of the 14 days before (0.106 of scored stories reach the deal extractor, 0.058 the datacenter one; 1.07 stories a cluster); a call's cost is the median of each step's last ten successful runs. Every eligible story already scored has been checked: the gap is the scoring. **The four days 31 October to 3 November hold no story at all**: the daily run did not ingest the feeds, and no backfill from this repository brings those stories back. The estimate is above the daily cap of the scheduled model steps (USD 1.50): the live run is the desktop's, after the owner approves it (`--run`, under the data lock).

| Row | State after session 2237 |
|---|---|
| A16 the failure line and a failed day | done: the API's words, a stop at the limit, retries, no table rewritten |

## Session 2249: the second read

The audit's 106 deals and 60 facilities read again: their stories (172 and 82, stored text only) extracted afresh with the code of sessions 2232 to 2237 in a temporary folder (claude-sonnet-5-5: 10 calls, USD 0.4258; 7 calls, USD 0.2254; recorded as `tests/fixtures/deals/recorded_2249.json` and `tests/fixtures/datacenters/recorded_2249.json`), and the new rows graded on the first read's rubric by three readers of this session. Each record's grade and note: `docs/reviews/deals-audit-2026-11-06/second_read_deals.csv` and `second_read_facilities.csv`; the counts by `second_read_tally.py`. The two reads had different readers; where one reader's call differs from the other's (a fund close with no investor named: a deal in the first read, not one in the second), the count moves without the extraction moving, and the notes say so.

### Deals (106)

| Class | Before | After |
|---|---|---|
| Not a deal, and a row kept | 12 | **1** (D055, G42's Vietnam project with no counterparty) |
| A stated deal with no row | 0 | **6** (D022 Black Hills and Google; D031 Sellafield's unnamed partners; D061 ONEOK and MPLX; D071 Volta's raise; D084 Shell and Monomoy; D092 Crescent's sale) |
| Place missed | 17 | 12 |
| Status missed | 14 | 7 |
| Status unsupported | 1 | 1 (D062 "Divests" kept as closed) |
| Kind wrong or no word for it | 11 | 8 (capacity leases kept as other: D007, D050, D053; "Illinois Nuclear Upgrades" not an uprate: D012) |
| A party a description | 7 | **0** |
| A party wrong | 4 | 1 (D001: Google, the credit backstop, as seller) |
| A party missed or incomplete | 1 | 3 (D045 Engine No. 1; D104 and D105, the company acquired left out of seller) |
| AI-power tag wrong | 6 | 2 (D005 a motive; D104 Eaton, a supplier to datacenters) |
| MW missed | 3 | **0** |
| A figure wrong or invented | 3 | 2 (D045 a plant's cost as the deal's; D053 the bonds funding a building as the lease's) |
| USD missed | 2 | 1 |
| Term missed | 1 | 0 |
| Confidence too low | 3 | 0 |
| Confidence too high | 1 | 0 |

Two distinct deals the stories state got no row of their own: Sempra's 20-year agreement with Petrobras (D032) and NiSource's expanded Amazon agreement (D043).

### Facilities (60)

| Class | Before | After |
|---|---|---|
| Not a facility, and a row kept | 5 | 1 (F052, a state only) |
| A stated facility with no row | 0 | 2 (F017 Gorilla's acquisition, F028 the Columbus cluster) |
| Two places in one row | 3 (counted as class 8 in the first read) | **0** (xAI's Tennessee and Mississippi, Maine and Alaska, each split) |
| MW basis unstated or wrong | 14 unstated | 1 wrong (F049 "total" on "2.5 GW data centre park") |
| Status missed | 9 | 2 |
| Status wrong | 3 | 1 (F039 "Pauses" as cancelled) |
| State missed | 5 | 2 (F015 "Western Kentucky", F034 "Hutto, Texas") |
| Operator missed or wrong | 5 | 3 |
| Site missed | 1 | 0 |
| Power source missed | 2 | 2 (F032 "generator fleet", F060 "Gas-Powered Data Center") |
| Timeline missed or wrong | 2 | 0 |
| Confidence too low | 6 | 0 |

### Into the next file (`queue/next/159-night-7-november-portable-deals-continued.md`)

The classes still above zero, in order of count: deals' place missed (12), kind (8, capacity leases and the uprate words), status missed (7), stated deals with no row (6) and a second deal of one story with no row (2), parties incomplete (3); facilities' operator (3), state (2), power source (2), stated facilities with no row (2).

## Session 2250: the counterparties read for missed aliases

Every name of the directory with two or more deals (109 of 481) was read against every other for a missed alias: the same words, a name and its initials, one name inside another, a shared first word (`warehouse/deals/dedupe.same_party` and a first word of four letters or more). Sixteen pairs came up:

| Pair | Read | Done |
|---|---|---|
| Delfin; Delfin Midstream | one company: news:45e9aea1ffe912fa says "Delfin LNG" in its title and "Delfin Midstream's first 4.4 mtpa floating liquefied natural gas (FLNG) unit" in its summary | an alias in `aliases.yaml`, with the story (3 deals) |
| Lynas; Lynas Rare Earths | likely one company; no stored story names both | left two names (an alias needs its story) |
| Chevron; Chevron Australia. ExxonMobil; ExxonMobil Asia Pacific | a party followed by a place: its subsidiary there | a rule: the parent is the shorter name, where the deals name it themselves |
| Meta-backed data centre; Google-Linked Data Centers; CoreWeave-tied data center; Anthropic data centre backed by Google | descriptions of a facility by its backer, not names | a rule: no directory row |
| Amazon data center unit; Blackstone data center vehicle; Blackstone's QTS; Constellation Energy unit | the parent's words already show it (session 2234) | unchanged |
| Energy Transfer; Energy Vault; Energy Capital Partners. American Electric Power; American Real Estate Partners. Radiant; Radiant Energy Solutions | two companies each (I Squared's Radiant Energy Solutions is not the microreactor maker) | left apart |

After: **475 names** (481 before), 109 with two or more deals, 13 with a parent (11 before), 0 EIA-861 numbers.

| Row | State after session 2250 |
|---|---|
| A5 a party a description | closed in the directory (the descriptions are out) and on the second read (0 of 106) |

## Session 2251: the pages read as a reader at a fund reads them

Read from the pages' code (no build: the machine's memory held the landing's build), cell by cell, for what a decision needs: what (the kind and the form), who (the parties as one name a company), how much (MW, MWh, US dollars), at what price (per MWh), when (the date and its basis, the stage and its history), where (the state, the country, the grid and its basis), how sure (the model's confidence, the flags).

| Page | Found | Fixed |
|---|---|---|
| `/deals` table | an empty MW, US dollars, price, place, grid or stage cell was blank; "how sure" only in the opened row; an AI tag of false was blank | each empty cell says "not stated"; a column "Sure" (the confidence, sortable, its meaning as the header's tip); the AI cell says "no" |
| `/deals?view=comparables` | every count shown, a median "fewer than three"; the priced section says when no deal states a price | none needed |
| `/deals?view=ai`, `?view=charts` | "none stated" beside each sum with the count that state it; the empty chart says so | none needed |
| `/datacenters` list | every empty cell already "not stated"; the confidence under the sources | none needed |
| `/datacenters?view=grids` | held cells "license needed" with a footnote, a reserve margin not held "not held" with a footnote | none needed |

| Row | State after session 2251 |
|---|---|
| A9 and A15 confidence | the model's bands (2232, 2236), on the second read 0 too low and 0 too high; shown in its own column |

## Every row's state (session 2252)

| Row | Class | State | Where |
|---|---|---|---|
| A1 | Deals: place missed (17) | improved, open: 12 on the second read | next file |
| A2 | Deals: status missed (14), unsupported (1) | improved, open: 7 and 1 | next file |
| A3 | Deals: not a deal (12) | done: 1 on the second read | 2232 |
| A4 | Deals: kind (11) | improved, open: 8 (capacity leases kept as other, an uprate's words) | next file |
| A5 | Deals: a party a description, wrong or missed | done for descriptions (0) and wrong (1); open for incomplete (3: the company acquired left out) | 2232, 2234, 2250; next file |
| A6 | Deals: AI-power tag (6) | improved: 2 (a motive, a supplier to datacenters) | 2232; next file |
| A7 | Deals: MW, USD, term missed | done: 0, 1, 0; every stored record flagged where its headline states a figure it lacks | 2232, 2235 |
| A8 | Deals: a sum of another figure, a share as a price | improved: 2 (a plant's cost, a building's bonds) | 2232, 2235; next file |
| A9 | Deals: confidence | done: 0 too low, 0 too high; shown as its own column | 2232, 2251 |
| A10 | Deals: the open duplicate pairs | done: two folded, one two deals | 2233 |
| A11 | Facilities: MW basis | done: 1 wrong on the second read | 2236 |
| A12 | Facilities: status (9 missed, 3 wrong) | improved: 2 and 1 | 2236; next file |
| A13 | Facilities: not a facility (5), several in one row (3) | done: 1 and 0 | 2236 |
| A14 | Facilities: state, operator, site, power, timeline | improved: state 2, operator 3, site 0, power 2, timeline 0 | 2236; next file |
| A15 | Facilities: confidence too low (6) | done: 0 | 2236 |
| A16 | The step's failure line, a failed day | done | 2237 |
| New | Stated deals with no row (6), a story's second deal (2); stated facilities with no row (2) | open, from the stricter prompt | next file; ruling asked |

## Session 2256 (chain 159): the six stated deals with no row

The recorded answers of session 2249 (`tests/fixtures/deals/recorded_2249.json`) show that all six clusters were sent and the model returned no deal for each: the stricter prompt's reading, not the story selection and not the code's party check (which keeps a deal with one named party). Four reasons, not one:

| Row | Headline | Why no row | With `ERW_DEALS_ONE_PARTY=on` |
|---|---|---|---|
| D022 | Black Hills plans $1.8 billion investment to power Google's data center | a plan: the prompt names this headline as not a deal (the first read, session 2231, graded it not a deal; the second read counted it a miss) | no row |
| D031 | Sellafield selects partners for asset care framework | one party named | a row, Sellafield the buyer |
| D061 | ONEOK, MPLX's "Wellhead-to-Water" Deal Dominates Permian NGL Race | a commentary headline that names a deal | no row |
| D071 | Nvidia, Dell Back AI Cloud Startup Volta at $2.4 Billion Value | a valuation of an AI cloud, not a sum raised, and not an energy company | no row |
| D084 | Shell to offload Jiffy Lube to Monomoy Capital for $1.3 billion | two parties named; an asset that is not an energy asset | a row, USD 1.3 billion |
| D092 | Crescent Sells Non-Op D-J Assets Ahead of Closing Vital Deal | one party named | a row, Crescent the seller, no buyer |

So the ruling asked (chain 156's ruling 2) is about D031 and D092 only; D084 asks another (whether a sale of an asset that is not an energy asset by an energy company is a deal); D022 is a plan by the prompt's own rule; D061 and D071 stay out under either answer. The switch is the one change: its default is the answer. The row "New" above: the six read again, open for the ruling.

## Session 2257 (chain 159): deals' place missed (12)

The twelve, read in the 2249 recording and its log: two (D017, D029) were answered "Indonesia" by the model and refused by the code's span check, the span being the adjective ("Indonesian"); ten were left empty by the model though the headline names the country before the asset. The fix is code, no model call: the span check takes a country's adjective (`fields.country_names`), and an empty country is read from the words (`fields.country_of`; the rule in `docs/methods/energy_deals.md`, "A deal's country from the words"). Replayed on the same answers:

| | Before | After |
|---|---|---|
| Place missed (of 106) | 12 | **3** |

The three left: D024 ("Ohio, Pennsylvania") and D058 ("Texas, Louisiana") name two states for the one `state` field, so the state stays empty (the country is now the United States for both); D087 names Japan as the buyer's home ("Japan's Jera"), not the asset's country, which the rule leaves empty. Two rows outside the twelve gained a country by the same words (D010 "US utility American Electric Power", for a project in Indiana; D033 "US LNG terminal developer"); each read and right. A first form of the rule took any country's adjective and gave D028 "Italy" from "the Italian oil and gas group" (Eni, the party): narrowed before commit.

## Session 2258 (chain 159): deals' kind (8)

| Row | Before | After | Why |
|---|---|---|---|
| D007 | other | compute_capacity | a lease of a data center |
| D053 | other | compute_capacity | a lease of a data center (the junk bonds fund the building) |
| D050 | other | compute_capacity | a data center expansion between OpenAI and Oracle |
| D001 | other | project_finance | a credit backstop for a named data center |
| D013 | other | project_finance | credit support for a named campus |
| D020 | other | m_and_a | a stake exited |
| D012 | other | nuclear_restart_uprate | "Illinois Nuclear Upgrades" |
| D080 | capital | nuclear_restart_uprate | another story of the cluster: "May Restart Abandoned US Nuclear Project" |

Kind wrong: **8 to 0** on the replayed answers; no other row of the 82 (or of the 2232 fixture's 29, beyond D007 and D020 there) changed kind. A first form of the data-center rule also turned D034 ("optical fiber for data centers"), D046 ("local energy infrastructure for Louisiana data center") and D055 (a one-party project) into compute capacity; narrowed before the commit (`DC_SUPPLY`, two named parties), and the test holds the three as "other".

## Session 2259 (chain 159): deals' status missed (7) and unsupported (1)

| Row | Before (stage / status) | After | The words |
|---|---|---|---|
| D001 | - / - | announced / announced | "to serve as credit backstop" |
| D020 | - / - | announced / announced | "will become independent" |
| D047 | - / - | signed / signed | "Joins Mercuria to Develop" |
| D051 | - / - | announced / announced | "Partner to Develop" |
| D063 | - / - | signed / signed | "partners with" |
| D074 | - / - | signed / signed | "lease deal with" |
| D081 | - / - | rumored / rumored | "source says" |

Status missed: **7 to 0**. Two more rows of the 82 had a stage and no status (D012, and D062 below) and now carry the stage as status; on the 2232 fixture, D043, D047 and D059 the same way. No stage or status the model gave changed.

**Unsupported (D062), left open**: "Woodside Divests ... to Perenco", read as closed by the model. A check that a closed stage's words say so was tried and taken out: it also turned D100 ("takes 5% stakes") and D026 ("Seals Acquisition") from closed, both read as right by the second read, and the raises the prompt itself calls closed ("money raised or received"). No word rule tells these present-tense headlines apart; the row stays with its status now closed too (it had none).

## Session 2260 (chain 159): deals' parties incomplete (3)

- **D045, done**: the model named Engine No. 1 in the cluster of "Microsoft, Chevron and Engine No. 1 sign exclusive deal"; the fold into the earlier "Chevron, Microsoft Eye ..." record filled an empty buyer or seller only, never another party. `dedupe.merge` now adds the later party and rebuilds `parties`. Replayed: D045 has Engine No. 1; it is the only party added across both fixtures.
- **D104, D105, left for the owner's ruling**: "Eaton signs agreement to acquire COL Group", "ESR to acquire Aquila Clean Energy APAC": no seller named; the second read wanted the company acquired as seller. The same read graded D068 (Calpine), D089 (Coterra) and D037 (Dominion), with the same empty seller, as right, and `seller` is a field the Roundup prints as the party selling. Unchanged.

Parties incomplete: **3 to 2**, the two by the ruling.

## Session 2261 (chain 159): facilities' operator (3)

- **F014, done**: the model gave the developer as "Colt DCS, RMZ"; the check refused the joined string, not in the story as one piece. A company field now passes when each of its names is in the story. Replayed: F014's developer is "Colt DCS, RMZ"; no operator or developer refusal is left on either facility fixture.
- **F050, by the rule**: "TikTok owner weighs data center project in Brazil" names the company only by a description, which the rule refuses (session 2236).
- **F036, left**: "Balearic Islands launches new data center for critical government systems": the operator is a regional government named by its place; the model left it empty, and no word rule makes a place an operator.

Operator missed: **3 to 2**, both by the rule's reading.

The second read's facilities also show a country missed three times (F035 "Japan's AI infrastructure", F044 "Stargate Norway", F053 "Stargate UK"), which the 2249 tally counted under no class; it is the next class by count.

## Session 2262 (chain 159): facilities' country (3)

| Row | Words | After |
|---|---|---|
| F044 | site "Stargate Norway" | Norway |
| F053 | site "Stargate UK" | United Kingdom |
| F035 | the Chiba row: "AI infrastructure in Japan" | Japan |

Country missed: **3 to 0**; the three fills are the only ones across both facility fixtures (the 2236 fixture's one fill is the same Stargate UK cluster). F053's other row ("OpenAI's First Stargate Site") names no place at all and stays as it is.

## Session 2263 (chain 159): facilities' status (2 missed, 1 wrong)

| Row | Words | Before | After |
|---|---|---|---|
| F018 | "due to be delivered next year" | - | under_construction |
| F041 | "on track to go live in mid-2026" | - | under_construction |
| F039 | "Pauses Wyoming Site" | cancelled | - (paused is not cancelled) |

Status faults: **3 to 0**; no other facility of either fixture changed status.

### The audit's open classes after chain 159's sessions 2256 to 2263

Deals (106): not a deal kept 1; stated deals with no row 6 (two by ruling 2, one by a scope ruling, three by the prompt's rules: session 2256); place missed 3 (two states in one field, a buyer's country); status unsupported 1 (D062); kind 0; parties incomplete 2 (by a ruling); a party wrong 1 (D001, Google the credit backstop as seller); AI-power tag 2; a figure of another thing 2 (D045 the plant's cost, D053 the building's bonds); USD missed 1. Facilities (60): not a facility 1; stated facilities with no row 2; MW basis 1 (F049); operator 2 (by the rule); state 2 (F015 "Western Kentucky", F034 "Hutto, Texas"); power source 2 (F032, F060); country 0; status 0.

## Every row's state (session 2266, chain 159)

| Row | Class | State | Where |
|---|---|---|---|
| A1 | Deals: place missed | improved: 12 to 3 (two states in one field; a buyer's country) | 2257 |
| A2 | Deals: status missed, unsupported | done for missed (7 to 0); 1 unsupported left open (D062, no word rule tells it apart) | 2259 |
| A3 | Deals: not a deal | done: 1 | 2232 |
| A4 | Deals: kind | done: 8 to 0 | 2258 |
| A5 | Deals: parties | improved: incomplete 3 to 2 (both by a ruling); wrong 1 (D001) open | 2260 |
| A6 | Deals: AI-power tag | open: 2 (a motive, a supplier to datacenters) | next file |
| A7 | Deals: MW, USD, term missed | done | 2232, 2235 |
| A8 | Deals: a sum of another figure | open: 2 (a plant's cost, a building's bonds) | next file |
| A9 | Deals: confidence | done | 2232, 2251 |
| A10 | Deals: duplicate pairs | done | 2233 |
| A11 | Facilities: MW basis | open: 1 (F049 "2.5 GW data centre park" read as total) | next file |
| A12 | Facilities: status | done: 3 to 0 | 2263 |
| A13 | Facilities: not a facility, two places | done: 1 and 0 | 2236 |
| A14 | Facilities: state, operator, site, power, timeline, country | operator 3 to 2 (both by the rule), country 3 to 0; open: state 2, power source 2 | 2261, 2262; next file |
| A15 | Facilities: confidence | done | 2236 |
| A16 | The step's failure line | done | 2237 |
| New | Stated deals with no row (6), stated facilities with no row (2) | traced (2256): 2 by ruling 2, 1 by a scope ruling, 3 by the prompt's own rules; the switch `ERW_DEALS_ONE_PARTY` holds the answer | 2256; ruling |

## Session 2269 (chain 174): deals' place, the three left (a decision, no code)

- **D024 ("Ohio and Pennsylvania"), D058 ("Texas, Louisiana")**: the `state` field holds one two-letter code, and the Roundup reads it as one (`warehouse/news/roundup.py`: `state in US_STATES`). Two states named for one deal stay out of `state`; both deals carry the country (United States, session 2257). A field of several states would be a new column beside `state` (the data standard's `geo` form, a comma list of ISO 3166-2 codes); not added without a need on a page.
- **D087 ("Japan's Jera")**: Japan is the buyer's home, not where the LNG is produced; the rule leaves it empty (session 2257).

Place missed: 3, each by a written decision; the class is closed for code.

## Session 2270 (chain 174): deals' AI-power tag (2)

D005 ("gas pipeline order tied to data centre buildout") and D104 ("manufacturing capacity ... for data center and utility markets") were tagged AI power by a datacenter word naming a motive or a market. `fields.DATACENTER_GENERIC` takes such phrases out before the load check. **2 to 0**; no other row of the 82 changed (35 tagged now, 37 before). The 2232 fixture's written answer for D005 said AI power; the 2249 read, quoting the prompt's rule on motives, says not: the 2232 answer now accepts either, with the reason in its `why`.
