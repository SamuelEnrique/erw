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
