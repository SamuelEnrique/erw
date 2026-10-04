# Session 102 report: landing

**Sessions 91 to 101 are on the live site, every new page in review.** Two deploys, not one, each with the 25-page snapshot before and after. The second put back a number the first had moved on a live page.

## Read this first: a difference that was not meant

**`/terms`, a live page, said "The 133 data sources in the registry" where it had said 125, from about 18:36 to 18:45 UTC.** The page lists the source registry and counts it; the landing's eight new sources added eight lines and moved the count. The comparison of the first deploy found it. I held those sources off the page (a list, `sources_hold`, in `warehouse/supabase/live_set.yaml`, read by the site's build) and deployed again: `/terms` now reads as it did before the landing, 0 differences against the snapshot taken before anything was pushed. The registry itself, Redivis and Supabase hold the eight sources like any other; when one of their pages opens, its line comes off the list.

No other number on a live page changed that the chain did not name. The one change it named is on the battery page (below).

## Every difference, the 25 live pages

Snapshots in `runs/snapshots/`: `before-102` (18:04 UTC), `after-102` (first deploy, 18:36), `before-102b`, `after-102b` (second deploy, 18:45), `after-102-load` (after the Supabase load, 18:51). Net, `before-102` against `after-102b`: 57 differences.

| Page | Differences | What | Expected |
|---|---|---|---|
| `/` | 35 | The five latest real-time prices and their interval lines (the 15-minute feed moved between the snapshots), and three lines that say how many days of history the small chart holds ("7 days" to "6.4 days in the ERW table": the same window read later) | Yes: the live feed, not the deploy |
| `/network` | 6 | The hourly refresh's stamps (built 16:05 to 18:05 UTC; demand's newest hour 14:00 to 16:00 UTC) | Yes: the hourly job |
| `/cost-of-power/battery` and its six ERCOT views (2, 4, 8 hours, both strategies) | 2 each, 14 | The sentence under the chart, one line gone and one line new. No number differs | Yes: the wording you asked for |
| `/data/methods/battery_stack` | 2 | The method note's bullet that describes that sentence | Yes |
| `/terms` | 0 net (10 after the first deploy, 10 back after the second) | The count 125 to 133 and eight lines, then back | **No: reported above, corrected** |
| The six CAISO battery views, `/about`, `/storage`, `/cost-of-power/seller` and its two California views, three methods pages | 0 | | |

Across the Supabase load (`after-102b` against `after-102-load`): **0 differences in all** on the 25 pages. The home page still counts 97 public tables and 13,849,497 rows, read both from the page and from the database with a visitor's key.

## What a visitor now reads on the battery page

Under the ERCOT chart, in place of "so years before 2024 show more than real batteries earned":

> This is an upper bound: before 2024 it is mostly payment for holding reserves, to a battery longer than any Texas then had, and 2021 is one week of February. Recent years are the ones to read.

That is session 101's one-line wording, as written there. California's sentence is as it was. The method note says the same and says why: the warehouse holds no measure of what real batteries earned.

In the notes of the two closed grids (internal view only; SPP and New York stay closed, `ready: false`):

- **SPP:** 60 minutes for Regulation Up, Regulation Down, Spinning Reserve and Supplemental Reserve, cited to SPP's Integrated Marketplace Protocols, Revision 119, section 4.2.2. No longer labeled assumed.
- **New York, 10-Minute Spinning Reserve:** one hour, cited to NYISO's Market Administration and Control Area Services Tariff, section 4.4.2.1, effective 16 September 2026. No longer labeled assumed.
- **New York, Regulation Capacity:** still labeled assumed, with the reason in the tariff's own terms: Rate Schedule 3, section 15.3.2.1(e), states no time.

The review table was rebuilt with the cited rules (3,744 rows). The hours are the ones session 86 assumed, so no figure moved: the site's copy differs from the old one in its build stamp only, compared value by value.

## The table steps, in session order

All under the data lock, taken per write step and released each time; it is free. Every gate was run unpiped and its exit code read.

| Session | Table | Rows | Validator | Coverage | Archive | Redivis draft |
|---|---|---|---|---|---|---|
| 92 | `api_cost_ledger` (internal) | 1,110 | exit 0 | yes | 558 rows new | internal dataset |
| 94 | `generation_mix_hourly_profile` | 162,911 | exit 0 | yes | yes | public |
| 94 | `generation_mix_records` | 306 | exit 0 | yes | yes | public |
| 95 | `interconnection_queue_summary` | 17,246 | exit 0 | yes | yes | public |
| 96 | `hub_price_comparison` | 575 | exit 0 | yes | yes | public |
| 97 | `eia930_demand_growth` | 24,108 | exit 0 | yes | yes | public |
| 98 | `caiso_curtailment_intervals` | 484,819 | exit 0 | yes | yes | public |
| 98 | `caiso_curtailment_profile` | 6,124 | exit 0 | yes | yes | public |
| 99 | `ferc_eqr_buyer_names` (internal) | 17,955 | exit 0 | yes | yes | internal dataset |
| 99 | `ferc_eqr_buyer_doubtful` (internal) | 1,281 | exit 0 | yes | yes | internal dataset |
| 99 | `ferc_eqr_party_totals` (internal) | 12,290 | exit 0 | yes | yes | internal dataset |
| 100 | `spp_as_quantities` | 159,768 | exit 0 | yes | yes | public |
| 100 | `battery_stack_review_monthly` (rebuilt) | 3,744 | exit 0 | yes | unchanged | public |

The derived tables of sessions 94 to 97 and 99 were built again by their own builders before validation; each gave the row count its session reported. `upload.py --check-license` before the upload and after it: 20 internal tables, 0 in the public dataset, exit 0 both times. Every upload's row count equals Redivis's count. **Nothing was released.** The archive wrote 887,941 rows to the bucket `erw-archive`, 0 failed.

Four things the table steps needed that the reports did not foresee:

1. **Coverage would not build.** Eight of the new tables had no sector rule; two sources (`spp:DA-MC`, `erw:caiso_curtailment_profile`) were not in the registry; and two builders wrote a "Derived from:" line with a note inside it, which the coverage builder reads as table names. Rules added; the sources registered from the connectors' own definitions, with no request to any publisher; the two header lines now name tables only. Then exit 0.
2. **This machine's daily tables were a day behind the daily run's.** 27 tables. Committing a coverage built from them would have stepped main's coverage back a day. They were refreshed from Redivis (`sync.py --refresh`, 27 restored, 0 failed).
3. **The cost ledger had diverged.** This machine held session 92's 558 evaluation rows; Redivis held 37 rows of today's daily run that this machine did not. Merged by event id through the ledger's own writer: 1,110 rows, nothing dropped.
4. **The committed coverage is the daily run's rows plus this machine's rows for the 13 tables above** (129 tables). Even after the refresh, about 30 tables here carry an older retrieval stamp than the daily run's (same rows), and one, `storage_buildout_monthly`, was restored without its header and would have been described wrongly. The builder ran here and exited 0; the merge is the same carry-over it does for a table a machine lacks.

## Supabase

| | |
|---|---|
| Database before | 437.3 MB |
| Database after | 753.0 MB (789,531,795 bytes), after the load's vacuum |
| Rows written | 603,438 in ten tables, each matched against its file |
| Limit | 7,500 MB (the loader's); your line for this load was 2 GB |

**Loaded for Ask ERCOT, four of the five session 92 listed:** `ercot_as_prices` (336,092 rows), `lbnl_interconnection_queue` (38,201), `merchant_revenue_monthly` (8,335), `storage_owners_monthly` (9,540).

**Not loaded: `ercot_all_hub_prices_history`, 3,063,570 rows.** The load of the others measured 549 bytes a row. At that rate the history adds about 1,600 MB and brings the database to about 2,356 MB, past 2 GB. Skipped, as you said, and its rule is out of the live set. Session 92's lighter way, a daily summary of about 51,000 rows, would fit; it is a derived table to build.

**Loaded for the review pages, held out of the public catalogue:** `generation_mix_hourly_profile`, `generation_mix_records`, `interconnection_queue_summary`, `hub_price_comparison`, `eia930_demand_growth`, `caiso_curtailment_profile`, and `storage_owners_monthly`. The mechanism is new and small: `review_hold` in `live_set.yaml`. The loader writes such a table's catalogue row with `in_live_set` "review"; the site's catalogue reader leaves those rows out of every count and list a visitor sees; Ask reads them. To open one, take its name off the list. The site's change went out in the first deploy, before any row was loaded.

**Not loaded, by decision:** `caiso_curtailment_intervals` (484,819 rows) and `spp_as_quantities` (159,768). No page reads either from Supabase: the curtailment page reads the profile built from the intervals, and the battery page's SPP is closed. Both are under `catalogue_hold`. The three EQR buyer tables are internal and not loaded, as session 99 said; the loader stored the summary of the contract table with the largest buyers and sellers, and `/contracts?view=largest` now shows them.

**Migration 022 applied** after the workflow reached main, as session 91 said. `scheduler.py --test chain-watch.yml`: GitHub answered HTTP 204. `--status`: `erw-chain-watch`, every 15 minutes, active. This chain is marked (since 17:10 UTC).

## The deploys

| Push | Run | Result |
|---|---|---|
| `task/102-landing`, first | 37223161364 | **Failed its tests, merged nothing.** Four tests of sessions 91 and 92 that had never run on GitHub's Linux runner: one read a Windows path with `os.path.basename`; three import the site's modules, whose packages the workflow installs only after the tests |
| `task/102-landing`, second | 37224140953 | **755 tests passed; the route check failed on one page in review, merged nothing.** `/learn/problems/networks-and-money`: the newest hour of the hourly network snapshot held no flow on ERCOT's ties, and the page read the first tie of an empty list. The same fault was on production before this session |
| `task/102-landing`, third | 37224610175 | Passed, merged (`5ee03c6`), deployed |
| `task/102-terms` | 37225235215 | Passed, merged (`190c3f4`), deployed: the `/terms` correction |

Vercel accepted both deployments; no storage refusal. The fixes: `scripts/alert.py` names a folder from a path written on any machine; the three Node tests skip where the site's packages are absent; the problem set takes the newest hour in which ERCOT's ties are reported and says which hour that is.

## The new pages on production, in the internal view

`site/scripts/check-review-pages.mjs` (new): each page asked with the internal cookie and without it. **14 of 14 render with data and are closed to a visitor.** Each page's own check, run against production: `/queues` 55 of 55, `/prices/compare` 54 of 54, `/demand` 83 of 83, `/curtailment/v2` 60 of 60, `/mix/v2` 56 of 56, `/network/v3` 26 of 26 in a browser, Ask ERCOT's link and context 23 of 23 in a browser. The contracts check runs only against a stand-in for the database, so on production I read the page: the largest view holds 294 figures and does not say "not loaded here yet".

### Ask ERCOT: three questions, USD 0.2253 of the USD 0.50 cap

Asked through the site's own route with the internal cookie. Model `claude-sonnet-5-5`. Whole answers in `runs/session102/ask_ercot.json`.

1. **"What was the average day-ahead price of Responsive Reserve (RRS) in ERCOT in 2023, in USD per MW?"** USD 0.0796. Not answered: *"Not in the warehouse. The RRS day-ahead price table (ercot_as_prices) can't be queried on this site. Only its last 35 days of prices are served here, and 2023 is outside that. The nearest thing is battery_stack_monthly, which holds modeled battery revenue from RRS, not the RRS price. I'm stating no number for 2023."* **This is wrong about the site as it now is, and I could not ask again** (three questions were allowed). The table had been loaded about seven minutes earlier: a visitor's key reads 39,955 of its rows for 2023 and its catalogue row says "yes". The site keeps the catalogue for an hour, so the likely cause is that Ask still held the catalogue from before the load. Likely, not proven. The sentence "only its last 35 days" is the tool's general note and no longer fits this table.
2. **"Which company reports the most battery storage in ERCOT, and how many MW?"** USD 0.0937. *"Engie North America reports the most operating battery storage in ERCOT: 1953.5 MW across 27 units (storage_capacity, derived by the ERW from EIA's monthly generator inventory, August 2026 vintage). The 'company' is the operator name reported to EIA, often a project company, so parent companies are not combined. The next largest I saw were Key Capture Energy at 579.7 MW and RWE Clean Energy at 573.4 MW (storage_capacity)."* With a chart of the rows it fetched. It answered from `storage_capacity`, not from the owners table.
3. **"How many MW of standalone battery storage are active in ERCOT's interconnection queue?"** USD 0.0520. *"ERCOT's own queue report lists 122304.92 MW of battery energy storage with status active, across 652 projects (ercot_interconnection_queue). The report tags these projects as "Other - Battery Energy Storage", a fuel category separate from solar. I read that as standalone batteries, but the table has no separate hybrid flag, so that is an inference. The snapshot is the vintage of 2026-09-30."* With a chart.

## Branches

Deleted, 12, each with 0 commits not on main, checked twice: `wip/090-fixes`, `wip/091-alerts`, `wip/092-ask-ercot`, `wip/093-network-v3`, `wip/094-mix-v2`, `wip/095-queues`, `wip/096-prices-compare`, `wip/097-demand`, `wip/098-curtailment`, `wip/099-buyers`, `wip/100-reserves`, `wip/101-early-years`. The workflow deleted both task branches when it merged them. Kept: `wip/076-land` (one commit not on main: session 76's report, identical to main's copy) and `wip/102-landing` (this report and the load's commit, which reach main with session 103's push).

## Tests and checks

- `tests/test_session102.py`, 11 tests: the review hold, the rules of the tables loaded and not loaded, the site's catalogue reader, the sources held off `/terms`, the sector rules, the battery sentence, the cited durations, SPP and New York closed.
- Every session's tests on this machine: 712 ran; **one fails and is not this session's:** `test_session49.Interchange.test_interchange_ceiling`. `eia930_all_interchange` holds 159,144 rows, as the daily run made it, against the 150,000 the test allows. It held 151,632 before I refreshed it, so it was already over. It does not run on GitHub (the table is not on the runner). Yours to rule: raise the ceiling or trim the window.
- Four older tests stated rules this landing changes, and now state the new ones with the reason: `merchant_revenue_monthly` and `ercot_as_prices` are in the live set; `storage_owners_monthly` is under `review_hold`; the durations are cited; session 101's check that its branch changed no page is no longer made.
- The site: `tsc` exit 0, the build exit 0, the battery page's browser test (all assertions), the route check on this machine's build (16 live pages, 95 in review, 0 failed), the no-request proof.

## Errors and decisions

1. **Two deploys where you asked for one.** The second exists only to put `/terms` back. I judged "no number on a live page may change" to outrank "one push".
2. **Three pushes to reach the first deploy.** The two that failed merged nothing and deployed nothing.
3. **The coverage merge** (table steps, point 4) is a decision of mine.
4. **`catalogue_hold` kept its meaning** (not in Supabase at all); `review_hold` is the new state (in Supabase, not in a visitor's counts). `storage_owners_monthly` moved from the first to the second.
5. **`upload.py --restore --out-dir` restored 34 tables, not the one I named,** into `runs/session102/` (1.6 GB). I deleted the 33 I had not asked for; nothing in `warehouse/output` was touched.
6. **The "iso" column of four new coverage rows is a word, not a grid** ("generation", "hub", "interconnection", "DEMAND"): the builder reads it from the entity's prefix. Cosmetic today; it would matter if a page filtered the catalogue by grid.
7. **No pull, no request to any publisher. MISO stays paused.** Model spend USD 0.2253, the three questions. No force push.

## For Samuel

1. **Ask ERCOT's first answer** (above). Ask it the same question when you open the page; if it still says the reserve prices cannot be queried, the cause is not the cache and the fault is real.
2. **The hub price history is not on the site.** Ask ERCOT will say "not in the site's live set" for any hub price older than 35 days. A daily summary would fix most of it; raising the 2 GB line would fix all of it.
3. **`test_interchange_ceiling`** fails on this machine, from the daily run's table.
4. **Three daily-run lines the reports asked for are not added** (the mix profile, the price comparison, the demand growth; the curtailment connector): they change the daily run, which this chain did not name.

Energy Research Warehouse (ERW), session 102, on the old laptop (`samueloldlaptop`, data role), 2026-10-04 from 17:05 to about 19:05 UTC, unattended, after one question at the start (your confirmation that the chain overrides the freeze today).

## MY REVIEW LIST

Open the internal view first: `https://erw-flame.vercel.app/internal/unlock?token=<INTERNAL_COSTS_TOKEN>`.

| Page | Look at first | Known weakness |
|---|---|---|
| https://erw-flame.vercel.app/ask/ercot | Ask "What was the average day-ahead price of Responsive Reserve in ERCOT in 2023?", the question it refused today | The site's database lacks the hub price history (2015 to August 2026), so older hub prices are "not in the live set". It does not compute across two tables or rank groups |
| https://erw-flame.vercel.app/network/v3 | The date picker: replay 15 February 2021, then "Play the year" | A replayed day has no demand (so no share of demand; session 109 adds it), no batteries, and prices only where held: ERCOT from 2019, five grids from September 2024, PJM never. 1,072 pair-days are left out as impossible |
| https://erw-flame.vercel.app/mix/v2 | California, one calendar month across the years: the duck curve growing | California has no months from September 2019 to August 2020 (EIA's file holds no hydro) and no December 2025. PJM is held to a looser test (15 percent). Texas's December 2025 is not written |
| https://erw-flame.vercel.app/queues | ERCOT, storage alone: active MW by year entered, and the share that reached operation | "Reached operation" is what the queues record, not every plant built: the file has 45 operating standalone batteries in ERCOT. ISO-NE has no median wait |
| https://erw-flame.vercel.app/prices/compare | The twelve-month table, cheapest hub first | Only eleven hubs hold twelve months and no zone does. MISO is held and not shown. PJM is not held |
| https://erw-flame.vercel.app/demand | PJM's peak by year, then the year to date | Seven ISOs and the Lower 48 only, no other balancing authority. The Lower 48 has an average and no peak. Faulty hours are screened by a rule of the page's own |
| https://erw-flame.vercel.app/curtailment/v2 | Curtailment by hour of day against battery charging | By fuel at five minutes ends 31 December 2025 (hourly by fuel after). The pull stops at 500,000 rows; it holds 484,819 |
| https://erw-flame.vercel.app/contracts | The table by the quarter signed | One quarter of filings (2026 Q2). Internal: FERC's license statement could not be read |
| https://erw-flame.vercel.app/contracts?view=largest | The largest buyers of energy | Ranked by contracts, not MW (8,060 of 66,192 rows file MW); the market operators lead it. One rule joined 564 names filed without a legal form |
| https://erw-flame.vercel.app/storage/owners | ERCOT's largest: Engie North America | An owner is the company that reports to EIA, often a project company. No parent is merged |
| https://erw-flame.vercel.app/battery/customer | Type a demand charge and a battery; the saving appears and nothing is sent | It knows no battery cost, so it cannot say whether the battery pays back. One demand charge, every month alike |
| https://erw-flame.vercel.app/storage/buildout | MW against MWh for ERCOT | Planned units carry no MWh: EIA-860M's planned sheet has no energy capacity |
| https://erw-flame.vercel.app/shoulder | California, a summer month: hours needed against hours the fleet holds | The shoulder runs to midnight in every California month, so "hours needed" is a floor. Texas's worst days are not measured |
| https://erw-flame.vercel.app/play/battery | Play Easy once to the end screen | Session 111 checks it whole for tomorrow. The penalty is 6 times the cap, set by Uri alone |
