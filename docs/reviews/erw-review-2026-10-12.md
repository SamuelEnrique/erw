# The whole-ERW review of 12 October 2026 (session 229)

Read on 13 October 2026, 03:50 to 06:30 UTC, unattended, on the old laptop. Every page a visitor can reach from the menu on `main` (57 pages, read on a local production build of `37c3a74e` in the internal view, so pages in review are seen as they are), and the next versions of the three tools on their branches (`wip/203-brand-battery`, `wip/212-generator-layout`, `wip/213-datacenter-layout` with session 228). Facts gathered by `runs/session229/review.mjs` (a real browser: screenshot, words, headings, placeholders, dates, console exceptions, every same-origin link fetched, sideways scroll) and by `scripts/check-values.mjs` against production (6,928 of 6,959 values match; 31 latest prices superseded within 45 minutes); the judgments are this session's. Screenshots in `docs/reviews/erw-review-2026-10-12/` (1280 px; 390 px for the five sellable tools and the Grid tool's parts). Nothing on a page, a table or a setting was changed.

## A. The five sellable tools against roadmap item 2

Item 2's "done": each has a method note signed by Samuel, a replication a reader can run, a cross-check table against published figures, and a decisions block; Automated Analysis in its final form; the Grid tool one page.

| Tool | Page | Method note | Signed | Replication | Cross-check table | Decisions block | Three questions | State |
|---|---|---|---|---|---|---|---|---|
| Battery | /cost-of-power/battery | [x] battery_earns_algorithm.md | [ ] | [x] CSV, do-file, Python mirror | [x] 14 figures, five published ERCOT revenues (session 208) | [x] | [x] on wip/203-brand-battery (sessions 208, 211) | main: the old layout; the branch waits for Samuel's screenshots |
| Generator | /cost-of-power/seller | [x] generator_earns_algorithm.md | [ ] | [x] CSV, do-file, Python mirror | [x] 10 figures | [x] | [x] on wip/212-generator-layout (session 212) | main: twelve sections, 205 "not held" cells |
| Datacenter | /cost-of-power | [x] datacenter_pays_algorithm.md | [ ] | [x] CSV, do-file, Python mirror; session 228's carbon file | [x] 6 figures (EIA) | [x] | [x] on wip/213-datacenter-layout; the four questions answered (session 228) | main: three grid questions as tables of other tools' figures |
| Automated Analysis | /analysis | [ ] a method note (the page links one; no algorithm note of its own) | [ ] | [x] each card downloads its data, Python and do-file | [ ] none | [ ] none | n.a. | one 29,000 px scroll of nine cards, the scanner, the request form and the week's templates; not "its final form" |
| Grid | /network with /mix and /ask | [x] grid_network.md (the network only) | [ ] | [ ] none | [ ] none | [ ] none | n.a. | three pages, plus /grid, /emissions and the seven grid pages, all on EIA-930; not merged |

Missing on every one of the five: Samuel's signature on the method note.
Missing on two: the landing of the branches (battery first, then generator, then datacenter: each builds on the one before).
Missing on Automated Analysis: a form (one card a screen), a cross-check of its findings, a decisions block or its equivalent (what a reader does with a finding).
Missing on the Grid tool: the merge itself (roadmap item 2), a replication of the network's figures, a cross-check against EIA's own hourly report.

## B. Overlaps: pages to merge or cut

- EIA-930 three ways: /grid (yesterday by ISO), /mix (today and since 2001), /network (the exchange map), /emissions (the carbon of the same hours), the seven /grid/<iso> pages. Merge into the Grid tool: one page, one grid in view, four tabs (now, mix, exchange, clean), with /ask as its question box. Roadmap item 2 says so.
- Storage three ways: /storage, /storage/buildout, /storage/owners. Merge into /storage as tabs: the fleet, the build-out, the owners.
- Carbon three ways: /emissions, /mix/clean (not in the menu), the datacenter page's "How clean?". Keep the datacenter's answer for the load; fold the other two into the Grid tool's "clean" tab.
- The shoulder hours (/shoulder) repeat /mix/stress's evening ramp and /storage's cycle. Merge into the Grid tool's stress view or into /storage.
- /consumption is /demand by sector. Merge into /demand.
- /resources is /map's layers. Merge into /map.
- /storage/owners and /companies are deal-analyst lists; /companies is a filter of /deals. Merge /companies into /deals.
- /severance/lease is /severance's second tab. Merge.
- /battery/customer is empty until typed and sits beside the battery tool with a near-identical name. Merge into /play/battery or cut.
- /explorer/ercot-peak-premium is one measure of one hub; /board holds the spreads. Merge into /prices as an ERCOT tab.
- /tour names pages in review. Merge into /about or cut.
- /thesis and /contracts read internal tables. Cut from the visitor menu; keep behind the internal view.
- The price board (/board) and /prices: /prices answers, /board is the wall. Keep both only if /board gets a top block; else fold the wall into /prices.

## C. The menu: pages in the wrong place

- Economics holds /severance, /severance/lease and /learn/bill, which are a tax tool and a lesson. Move the two severance pages to a Tools group (or Games, renamed Learn), the bill to Learn.
- Economics holds /contracts (internal). Out of the menu.
- Grid holds /network, /grid, /mix, /demand, /curtailment, /emissions, /consumption and "Your grid" (seven pages): fourteen entries for one tool. After the merge: the Grid tool, Demand (with consumption), Curtailment.
- Infrastructure holds three storage pages and two map pages: after the merges, Project map, Datacenter tracker, Storage, Deals.
- Analysis holds /thesis (internal) and /events (an index of event pages). Thesis out; Events under Learn or under the Grid tool's stress view.
- Games is Learn: the bill, the problem sets, the game, the tour. Rename the group Learn.
- News is an aside (digest, roundup, email): right.
- Not in the menu but reachable and linked: /mix/clean, /mix/stress, /demand/weather, /prices/compare, /queues, /board/v3, /board/v4, /deals/v2, /map/v2, /datacenters/v2, /network/v3, /curtailment/v2, /seller/v2, /data/methods/*, /grid/<iso>/alerts, /reports/draft/*, /events/<event>, /learn/problems/storage-and-taxes. The versioned addresses (v2, v3, v4) should redirect to the one page or be retired before 20 October.
- /data/methods answers 404 on the local build and 200 on production: find out which is right before a visitor finds the other.

## D. The 20 highest-value improvements for 20 October

Ranked by value to the launch and to the authority goal. Effort S (a session or less), M (two or three), L (a week). Machine: code unless said. Ruling: whether Samuel must rule first.

| # | Page | Change, in one line | Effort | Machine | Ruling |
|---|---|---|---|---|---|
| 1 | /cost-of-power/battery | Land wip/203-brand-battery: three questions, the contract as assumptions, the brand | S | code | yes: the screenshots of review-211 |
| 2 | /cost-of-power/seller | Land wip/212-generator-layout after it | S | code | yes: review-212 |
| 3 | /cost-of-power | Land wip/213-datacenter-layout with session 228's four answers | S | code | yes: review-228, and section F |
| 4 | the five tools | Samuel signs the five method notes (a line with his name and the date at the top of each) | S | Samuel | yes |
| 5 | /analysis | One card a screen with a card index; the request form and the templates as tabs | M | code | no |
| 6 | /network, /grid, /mix, /emissions, /grid/<iso>, /ask | The Grid tool: one page, one grid in view, four tabs and the question box | L | code | yes: the layout |
| 7 | every page | The brand (docs/brand.md) applied to the generator and datacenter pages, then the rest, after the battery is approved | L | code | yes |
| 8 | /data, Terms | The 20 October license table: which tables are public, which "license needed" (ISO-NE, MISO, NYISO, the news outlets), which internal; the pages that go dark with them (board, datacenters, deals, digest, roundup, events) | M | data, Samuel | yes: the letters |
| 9 | /datacenters | A top block (facilities, megawatts, this week) and the list folded by operator | M | code | no |
| 10 | / | Drop the "In review" list for visitors; units on every "Open now" number; no empty sparkline | S | code | no |
| 11 | /board | A top block of the twelve numbers a trader checks first; the wall folded by group | M | code | no |
| 12 | /supply | Hide tables whose rows are all "not held"; load its weekly tables into the live set so its numbers carry check keys | M | data | no |
| 13 | /data | Downloads that time out (the two largest tables) say so and point to Redivis | S | code | no |
| 14 | /data/methods | A methods index that answers on the local build as on production | S | code | no |
| 15 | /storage, /storage/buildout, /storage/owners | One page, three tabs | S | code | no |
| 16 | /cost-of-power (branch) | ERCOT's own scarcity signal (the reserve adders) as a table, so "Will the power be there?" can count by each grid's own rule | M | data | yes: section F |
| 17 | /cost-of-power (branch) | A year of hourly carbon intensity for the page's grids (from Redivis or the data machine), so "How clean?" is hour by hour for the whole year | M | data | no |
| 18 | /network | Lead with one sentence of what the grid is doing now; close the two-day lag of the newest hour | S | code, data | no |
| 19 | /policy, /contracts | Future dates printed as they stand (2026-12-08, 2026-12-31): say "as filed" or hold them | S | code | no |
| 20 | the versioned addresses | /board/v3, /board/v4, /deals/v2, /map/v2, /datacenters/v2, /network/v3, /curtailment/v2, /seller/v2 redirect to the one page | S | code | no |

## E. Pages not ready for 20 October, and the one thing each needs

- /cost-of-power/seller (main): the landing of wip/212-generator-layout, after the battery.
- /cost-of-power (main): the landing of wip/213-datacenter-layout with session 228.
- /cost-of-power/battery (main): the landing of wip/203-brand-battery, with Samuel's approval of the screenshots.
- /analysis: one card a screen.
- /network, /grid, /mix, /ask: the Grid merge, or at least one sentence at the top of /network saying what the grid is doing now.
- /board: a top block; as it stands it does not answer in ten seconds.
- /datacenters: a top block; and its tables are "license needed" on 20 October.
- /deals, /digest, /roundup, /events, /map: a license verdict on the news outlets' tables (energy_deals, news_index, datacenter_projects, event_window_daily); without it they cannot be public on the 20th.
- /supply: its empty tables hidden, or filled by a pull.
- /contracts and /thesis: out of the visitor menu (internal tables).
- /resources, /tour, /battery/customer, /companies: merged or cut (section B).
- /data/methods: the local 404 explained.
- The home page: the "In review" block gone for visitors.
- MISO's price pages (/prices, /grid/miso): paused since 4 October; a line that says so where the price stands.


## F. Session 228's open ruling: one scarcity level for every grid, or each grid's own signal

The question: "Will the power be there?" counts the hours of the last twelve months whose price is at or above a level. Session 228 set one level, USD 1,000 per MWh, for every grid.

The case for one level (USD 1,000 per MWh, what the page does now):
- The count means the same thing on every grid, so a reader can set ERCOT beside CAISO and NYISO.
- USD 1,000 is the FERC offer cap (Order 831) in the six FERC markets; above it a price is scarcity pricing, not an offer.
- In ERCOT the same holds: only the operating reserve demand curve adders push a price above offers.
- One line of method on the page; one number in the download and the replication files.
- Default case: 4 hours in the year at LZ_NORTH, all in January 2026. A reader sees "4 hours" and the January morning and evening.

The case for each grid's own signal:
- ERCOT's own scarcity is its adders: an hour with a reserve adder above zero is short by ERCOT's own rule, at any price. The ERW holds no table of the adders.
- CAISO's own signal is its notices (EEA, flex alerts, restricted maintenance): caiso_grid_emergencies holds them, to 30 April 2025, and flex_alert_effects the alert hours to July 2024. The page counts them beside the price where held.
- NYISO, ISO-NE and SPP: reserve shortage pricing, each with its own demand curve; no table of those hours is held.
- At USD 1,000 a grid with a low cap (CAISO's soft cap USD 1,000 and hard cap USD 2,000) and a grid with a high one (ERCOT's USD 5,000) sit on one scale, so ERCOT's count is of a stronger event than CAISO's.
- A grid's own signal would need one more table a grid (the adders, the shortage intervals, the notices), each a pull with its own terms.

What the page can do without a ruling: keep the one level and say it on the page (it does), and count the operator's notices beside it where a table holds them (it does for CAISO).

What a ruling would change: the level (one for all, or one each), and whether a second level ("close to short", say USD 500, or the grid's tight hours of demand, which the download holds) stands beside it.

Recommendation: keep USD 1,000 for every grid for 20 October, and add each grid's own signal as a second count when its table is held (ERCOT's adders first).


## The pages, one block each

Scores 1 to 5: usefulness (to the launch's reader), accuracy (the numbers against their tables), clarity (the question answered in ten seconds), finish (layout, placeholders, dead ends).

### /: Energy Research Warehouse

- For: The front door: what the ERW is and the four tools open now, with live prices, gas and oil, the digest's top five. For anyone arriving.
- In 10 seconds: partly: the four numbers answer, but the generator's USD 550,484.85 carries no unit or size on the card, the network card's hour is two days old, MISO's sparkline reads no data, and the 'In review' list of twenty links is the page's largest block.
- Screenshot: `docs/reviews/erw-review-2026-10-12/home.png`
- Checked: `bs | grid=ercot&dur=4&strat=foresight&mw=100&fom=22&ds=6783357 | l12_kw:total | page shows "81.40" | page read 81.4021896 | Supabase 81.4021896`
- Fresh: newest date on the page 2026-10-13; tables: no table behind it (a page of words or of the reader's own numbers). On 20 October: public.
- Broken: console exceptions 0; dead links 0; placeholders ('not held' and the like) 0; sideways scroll no; 703 words, 2261 px tall
- Scores: usefulness 4, accuracy 4, clarity 3, finish 3
- Verdict: improve: drop the 'In review' list for visitors; give each 'Open now' number its unit; hide a sparkline with no data.

### /board: Price board

- For: Every price the warehouse holds, as a wall of tables (power by hub, peak and off-peak, spreads, gas, oil, products, retail). For a trader who knows the names.
- In 10 seconds: no: 5,002 words and an 11,700 px page; the first screen is a sea of equal rows with no question answered at the top.
- Screenshot: `docs/reviews/erw-review-2026-10-12/board.png`
- Checked: no check key on the page; a table behind it probed by hand in `runs/session229/probes.json` (session 229)
- Fresh: newest date on the page none printed; tables: eia_fuel_spot_prices to 2026-10-06 (P1D): stale, 7 days; eia_product_spot_prices to 2026-10-06 (P1D): stale, 7 days. On 20 October: public.
- Broken: console exceptions 0; dead links 0; placeholders ('not held' and the like) 57; sideways scroll no; 5002 words, 11253 px tall
- Scores: usefulness 4, accuracy 4, clarity 2, finish 3
- Verdict: improve: a top block of the twelve numbers a trader checks first, the wall folded by group; or merge the wall into /prices as its 'every hub' tab.

### /prices: Power prices

- For: Real-time and day-ahead prices by grid with sparklines and the latest interval. For a trader or an analyst checking a grid now.
- In 10 seconds: yes: six grids, the latest price and when, in one screen.
- Screenshot: `docs/reviews/erw-review-2026-10-12/prices.png`
- Checked: `series | iso_dam_hub_prices | ercot:HB_BUSAVG | spp_dam | 2026-10-13T03:00:00+00:00 | page shows "38.92" | page read 38.92 | Supabase 38.92`
- Fresh: newest date on the page 2026-10-13; tables: eia_fuel_spot_prices to 2026-10-06 (P1D): stale, 7 days. On 20 October: public.
- Broken: console exceptions 0; dead links 0; placeholders ('not held' and the like) 0; sideways scroll no; 578 words, 2359 px tall. MISO's real-time series stops on 2026-10-04 (the pause), and the card says so only in small print.
- Scores: usefulness 5, accuracy 5, clarity 4, finish 4
- Verdict: keep

### /supply: Supply and trade

- For: Gas storage, crude and product stocks, production, refining and trade against the five-year range. For an analyst of fuels.
- In 10 seconds: partly: the first block answers 'tighter or looser' in one glance; below it 57 placeholders read 'not held' (the trade and production rows), so half the page is empty cells.
- Screenshot: `docs/reviews/erw-review-2026-10-12/supply.png`
- Checked: no check key on the page; a table behind it probed by hand in `runs/session229/probes.json` (session 229)
- Fresh: newest date on the page none printed; tables: eia_gas_storage_weekly to 2026-10-02 (P1W): fresh; eia_petroleum_supply_weekly to 2026-10-02 (P1W): fresh; eia_gas_trade_monthly to 2026-07-01 (P1M): fresh; eia_basin_production_monthly to 2026-07-01 (P1M): fresh; cftc_cot_positions to 2026-10-06 (P1W): fresh. On 20 October: public.
- Broken: console exceptions 0; dead links 0; placeholders ('not held' and the like) 57; sideways scroll no; 2009 words, 6116 px tall
- Scores: usefulness 3, accuracy 4, clarity 3, finish 2
- Verdict: improve: hide a table whose rows are all 'not held' until its pull lands; the page's own tables (eia_gas_storage_weekly) are not in the live set, so nothing on it carries a check key.

### /explorer/ercot-peak-premium: ERCOT peak premium

- For: ERCOT's on-peak premium over off-peak by year and month, the one derived series the site opened first. For a trader.
- In 10 seconds: yes: one hub, one year, the premium in a sentence.
- Screenshot: `docs/reviews/erw-review-2026-10-12/explorer-ercot-peak-premium.png`
- Checked: `series | ercot_peak_premium_annual | ercot:HB_HUBAVG | all_median | 2025-01-01T00:00:00Z | page shows "25.68" | page read 25.68 | Supabase 25.68`
- Fresh: newest date on the page none printed; tables: ercot_peak_premium_annual to 2026-01-01 (P1Y): fresh; ercot_peak_premium_monthly to 2026-09-01 (P1M): fresh. On 20 October: public.
- Broken: console exceptions 0; dead links 0; placeholders ('not held' and the like) 0; sideways scroll no; 363 words, 2138 px tall
- Scores: usefulness 3, accuracy 5, clarity 4, finish 4
- Verdict: merge into /prices (an ERCOT tab) or into the price board's spreads: it is one measure of one hub.

### /contracts: Where power contracts are being struck

- For: FERC EQR power contracts, who sold to whom at what price, by quarter. For a deal analyst.
- In 10 seconds: partly: 6,053 words and a 29,000 px page; the top block chooses, the answer is a long table.
- Screenshot: `docs/reviews/erw-review-2026-10-12/contracts.png`
- Checked: no check key on the page; a table behind it probed by hand in `runs/session229/probes.json` (session 229)
- Fresh: newest date on the page 2099-12-31; tables: ferc_eqr_contracts to 2223-01-01 (event): fresh. On 20 October: internal.
- Broken: console exceptions 0; dead links 0; placeholders ('not held' and the like) 0; sideways scroll no; 6053 words, 29373 px tall. the newest contract date on the page reads 2026-12-31, an execution date in the future that the page prints as it stands.
- Scores: usefulness 4, accuracy 3, clarity 2, finish 2
- Verdict: cut from the visitor menu until its table has a license (ferc_eqr_contracts is internal); keep behind the internal view.

### /severance: Severance tax calculator: Texas, Louisiana, New Mexico

- For: A severance tax calculator for Texas, Louisiana and New Mexico with every rule sourced. For a producer or a tax analyst.
- In 10 seconds: yes: type a volume, read the tax; the rules under it with their sources.
- Screenshot: `docs/reviews/erw-review-2026-10-12/severance.png`
- Checked: no check key on the page (a page of words, of files, or of the reader's own numbers)
- Fresh: newest date on the page 2027-06-30; tables: eia_fuel_spot_prices to 2026-10-06 (P1D): stale, 7 days. On 20 October: public.
- Broken: console exceptions 0; dead links 0; placeholders ('not held' and the like) 0; sideways scroll no; 1914 words, 2754 px tall
- Scores: usefulness 3, accuracy 4, clarity 4, finish 4
- Verdict: keep; move under a Tools or Learn group, it is not an Economics page.

### /severance/lease: Severance tax for a lease: every well, every month

- For: The same tax for a lease, every well and month. For a mineral owner.
- In 10 seconds: yes, once a lease is typed; empty until then.
- Screenshot: `docs/reviews/erw-review-2026-10-12/severance-lease.png`
- Checked: no check key on the page (a page of words, of files, or of the reader's own numbers)
- Fresh: newest date on the page 2026-09-30; tables: eia_fuel_spot_prices to 2026-10-06 (P1D): stale, 7 days. On 20 October: public.
- Broken: console exceptions 0; dead links 0; placeholders ('not held' and the like) 0; sideways scroll no; 556 words, 1263 px tall
- Scores: usefulness 2, accuracy 4, clarity 4, finish 3
- Verdict: merge into /severance as a second tab.

### /learn/bill: What is on an electricity bill

- For: What is on an electricity bill, three default bills built from the rules, ten terms. For a reader new to the industry.
- In 10 seconds: yes: three bills with their parts in one screen.
- Screenshot: `docs/reviews/erw-review-2026-10-12/learn-bill.png`
- Checked: `bill | CA | total | page shows "262.33" | page read 262.3299 | Supabase 262.32990000000007`
- Fresh: newest date on the page 2026-10-01; tables: cost_of_power_monthly to 2026-10-01 (P1M): fresh. On 20 October: license needed (cost_of_power_monthly).
- Broken: console exceptions 0; dead links 0; placeholders ('not held' and the like) 0; sideways scroll no; 1133 words, 2290 px tall
- Scores: usefulness 3, accuracy 4, clarity 5, finish 4
- Verdict: keep; it belongs in Learn (Games group), not Economics.

### /cost-of-power/battery: What a battery earns

- For: What a 100 MW battery earned in ERCOT or CAISO from energy and reserves, by stream and span, and whether it covers its debt. One of the five sellable tools. For a developer, lender or analyst.
- In 10 seconds: yes on main too, but the main version still has the contract panel, three folds and the 'Other grids' table; the branch version answers in three questions.
- Screenshot: `docs/reviews/erw-review-2026-10-12/cost-of-power-battery.png`
- Checked: `bs | grid=ercot&dur=4&strat=foresight&mw=100&fom=22&ds=6783357 | l12_share:ancillary | page shows "33" | page read 33 | Supabase 33`
- Fresh: newest date on the page none printed; tables: battery_stack_monthly to 2026-10-01 (P1M): fresh; battery_stack_stress_daily to 2023-09-10 (P1D): stale, 1129 days. On 20 October: public.
- Broken: console exceptions 0; dead links 0; placeholders ('not held' and the like) 6; sideways scroll no; 1779 words, 4761 px tall
- Scores: usefulness 5, accuracy 5, clarity 4, finish 4
- Verdict: improve: land wip/203-brand-battery (sessions 203, 208, 211): three questions, the contract as assumptions, the brand.

### /cost-of-power/seller: What a generator earns

- For: What a solar, wind, battery or peaker plant earned at the hub price, the capture price at every hub, debt coverage, a battery beside it. Sellable tool two.
- In 10 seconds: partly on main: 3,086 words, twelve sections, 205 'not held' cells in the capture tables before the answer to 'is it worth building' appears; the branch version answers in three questions.
- Screenshot: `docs/reviews/erw-review-2026-10-12/cost-of-power-seller.png`
- Checked: `mr | iso=ercot&asset=solar&mw=100&mwh=0&ds=7078769&hr=10.725&vom=4.25&fom=12.5 | ttm_last | page shows "0.67" | page read 0.668933604133713 | Supabase 0.668933604133713`
- Fresh: newest date on the page 2026-10-12; tables: merchant_revenue_monthly to 2026-10-01 (P1M): fresh. On 20 October: license needed (merchant_revenue_monthly).
- Broken: console exceptions 0; dead links 0; placeholders ('not held' and the like) 205; sideways scroll no; 3086 words, 9159 px tall
- Scores: usefulness 5, accuracy 5, clarity 3, finish 3
- Verdict: improve: land wip/212-generator-layout (session 212) after the battery.

### /cost-of-power: What a datacenter pays

- For: What a large load pays for power at a hub or zone, flat or flexible, whether the power is there, how clean, how soon. Sellable tool three.
- In 10 seconds: partly on main: the first question is answered in one sentence; the other three are tables of the other tools' figures with links out; the branch version (session 228) computes all four for the load.
- Screenshot: `docs/reviews/erw-review-2026-10-12/cost-of-power.png`
- Checked: `series | cost_of_power_monthly | nyiso:N.Y.C. | rt_load_weighted | 2026-08-01T00:00:00+00:00 | page shows "58.53" | page read 58.525 | Supabase 58.525`
- Fresh: newest date on the page none printed; tables: cost_of_power_monthly to 2026-10-01 (P1M): fresh; cost_of_power_hourly_profile to 2026-10-01 (P1M): fresh; cost_of_power_carbon to 2026-10-01 (P1M): fresh. On 20 October: license needed (cost_of_power_carbon), license needed (cost_of_power_monthly), license needed (cost_of_power_hourly_profile).
- Broken: console exceptions 0; dead links 0; placeholders ('not held' and the like) 2; sideways scroll no; 3106 words, 9232 px tall
- Scores: usefulness 5, accuracy 4, clarity 3, finish 3
- Verdict: improve: land wip/213-datacenter-layout (sessions 213 and 228) after the generator.

### /battery/customer: What a battery saves a customer

- For: What a home or business battery saves a customer on their own numbers. For a retail customer.
- In 10 seconds: no: empty until the reader types; no default case shown.
- Screenshot: `docs/reviews/erw-review-2026-10-12/battery-customer.png`
- Checked: no check key on the page (a page of words, of files, or of the reader's own numbers)
- Fresh: newest date on the page none printed; tables: no table behind it (a page of words or of the reader's own numbers). On 20 October: public.
- Broken: console exceptions 0; dead links 0; placeholders ('not held' and the like) 0; sideways scroll no; 347 words, 1632 px tall
- Scores: usefulness 2, accuracy 3, clarity 3, finish 3
- Verdict: merge into /play/battery or /learn/bill as the 'your battery' step, or cut.

### /shoulder: The shoulder hours

- For: The shoulder hours: how the evening ramp and batteries' discharge sit by month and year, ERCOT and CAISO. For a storage analyst.
- In 10 seconds: partly: the average day chart answers, but the question the page asks is not stated at the top.
- Screenshot: `docs/reviews/erw-review-2026-10-12/shoulder.png`
- Checked: `series | shoulder_hours_monthly | iso:ercot | shoulder_hours | 2026-08-01T00:00:00Z | page shows "5" | page read 5 | Supabase 5`
- Fresh: newest date on the page none printed; tables: shoulder_hours_monthly to 2026-10-03 (P1D;P1M;P1Y): stale, 10 days. On 20 October: public.
- Broken: console exceptions 0; dead links 0; placeholders ('not held' and the like) 7; sideways scroll no; 1085 words, 3753 px tall
- Scores: usefulness 3, accuracy 5, clarity 3, finish 4
- Verdict: merge into the Grid tool (/mix/stress holds the same evening ramp) or into /storage.

### /network: The grid network

- For: The 70 balancing authorities and the power they exchange, live and replayed, in 3D. The Grid tool's map (sellable tool five with /mix and /ask).
- In 10 seconds: partly: a striking map, but the first screen is controls (watch, play, batteries, prices) and the newest hour is two days old (2026-10-11 03:00 UTC).
- Screenshot: `docs/reviews/erw-review-2026-10-12/network.png`, `docs/reviews/erw-review-2026-10-12/network-390.png` (390)
- Checked: no check key on the page; a table behind it probed by hand in `runs/session229/probes.json` (session 229)
- Fresh: newest date on the page 2026-10-13; tables: eia930_all_interchange to 2026-10-10 (PT1H): fresh; grid_network_nodes to 2026-10-10 (PT168H;PT1H): fresh; grid_network_links to 2026-10-10 (PT1H): fresh. On 20 October: public.
- Broken: console exceptions 0; dead links 0; placeholders ('not held' and the like) 1; sideways scroll no; 657 words, 1559 px tall. the newest hour that every pair holds lags two days behind EIA-930's demand table (2026-10-12).
- Scores: usefulness 4, accuracy 4, clarity 3, finish 4
- Verdict: improve: lead with one sentence of what the grid is doing now; the Grid merge of roadmap item 2 (network, mix, ask on one page).

### /grid: Grid conditions

- For: Yesterday's demand, forecast miss and generation mix for seven ISOs and the Lower 48. For anyone asking how the grids did yesterday.
- In 10 seconds: yes: one block a grid, peak and mix.
- Screenshot: `docs/reviews/erw-review-2026-10-12/grid.png`
- Checked: `series_max | eia930_all_demand | demand_mw | 2026-10-11T00:00:00Z | 2026-10-12T00:00:00Z | eia930:US48 | page shows "525,264" | page read 525264 | Supabase 525264`
- Fresh: newest date on the page 2026-10-12; tables: eia930_all_demand to 2026-10-11 (PT1H): fresh; eia930_all_generation to 2026-10-11 (PT1H): fresh. On 20 October: public.
- Broken: console exceptions 0; dead links 0; placeholders ('not held' and the like) 0; sideways scroll no; 1985 words, 5119 px tall
- Scores: usefulness 4, accuracy 5, clarity 4, finish 4
- Verdict: merge into the Grid tool with /network and /mix: three pages show EIA-930's generation three ways.

### /mix: Energy mix

- For: The energy mix today, the last seven days by hour and monthly since 2001, any grid or state. Part of the Grid tool.
- In 10 seconds: yes: the US today so far in one chart; 296 words.
- Screenshot: `docs/reviews/erw-review-2026-10-12/mix.png`, `docs/reviews/erw-review-2026-10-12/mix-390.png` (390)
- Checked: `series_esum | eia930_generation_latest | eia930:US48 | net_generation_mw | 2026-10-12T00:00:00Z | 2026-10-13T00:00:00Z | page shows "1,468,475" | page read 1468475 | Supabase 1468475`
- Fresh: newest date on the page 2026-10-12; tables: eia930_all_generation to 2026-10-11 (PT1H): fresh; eia930_generation_latest to 2026-10-12 (PT1H): fresh; state_generation_mix_monthly to 2026-07-01 (P1M): fresh; generation_mix_hourly_profile to 2026-09-01 (P1M): fresh; clean_energy_summary to 2026-09-01 (P1M;P1Y): fresh; grid_stress_yearly to 2026-01-01 (P1Y): fresh. On 20 October: license needed (clean_energy_summary), public.
- Broken: console exceptions 0; dead links 0; placeholders ('not held' and the like) 0; sideways scroll no; 296 words, 1750 px tall
- Scores: usefulness 4, accuracy 5, clarity 4, finish 4
- Verdict: merge into the Grid tool (roadmap item 2).

### /demand: Demand growth

- For: Demand growth by balancing authority since 2019, the ranking and where the growth is, with the weather taken out on its second view. For a planner or an analyst of AI load.
- In 10 seconds: yes: the ranking answers the question in one table.
- Screenshot: `docs/reviews/erw-review-2026-10-12/demand.png`
- Checked: no check key on the page; a table behind it probed by hand in `runs/session229/probes.json` (session 229)
- Fresh: newest date on the page 2026-10-05; tables: eia930_demand_growth to 2026-01-01 (P1Y): fresh; eia930_demand_weather to 2026-01-01 (P1Y): fresh. On 20 October: public.
- Broken: console exceptions 0; dead links 0; placeholders ('not held' and the like) 1; sideways scroll no; 628 words, 3189 px tall
- Scores: usefulness 5, accuracy 5, clarity 4, finish 4
- Verdict: keep; it is the strongest 'where is load growing' page the site has.

### /curtailment: Curtailment

- For: Wind and solar curtailment by day, month, hour and reason, every grid, and where free energy is. For a developer or a storage analyst.
- In 10 seconds: partly: the choose block comes first; the answer (how much, when) is the second screen.
- Screenshot: `docs/reviews/erw-review-2026-10-12/curtailment.png`
- Checked: `series_esum | caiso_curtailment_daily | caiso:ISO | curtailed_solar_mwh | 2026-07-13T00:00:00Z | 2026-10-11T00:00:00Z | page shows "489,137.54" | page read 489137.5380000002 | Supabase 489137.5380000002`
- Fresh: newest date on the page 2026-10-12; tables: caiso_curtailment_daily to 2026-10-10 (P1D): fresh; spp_curtailment_daily to 2026-10-11 (P1D): fresh; ercot_wind_solar_hsl_daily to 2026-10-11 (P1D): fresh; iso_curtailment_monthly to 2026-09-01 (P1M): fresh; caiso_curtailment_profile to 2026-09-01 (P1M): fresh; ercot_wind_solar_hsl_hourly to 2026-10-12 (PT1H): fresh. On 20 October: public.
- Broken: console exceptions 0; dead links 0; placeholders ('not held' and the like) 8; sideways scroll no; 1630 words, 8399 px tall
- Scores: usefulness 4, accuracy 5, clarity 3, finish 4
- Verdict: keep; lead with the month's figure.

### /emissions: Emissions

- For: Carbon intensity now, ranked, the last 24 hours and monthly since 2018, by grid. For anyone asking how clean the power is now.
- In 10 seconds: yes: the ranking is the first block.
- Screenshot: `docs/reviews/erw-review-2026-10-12/emissions.png`
- Checked: `series | carbon_intensity_hourly | eia930:CISO | intensity_generation | 2026-10-09T23:00:00+00:00 | page shows "121.65" | page read 121.646 | Supabase 121.646`
- Fresh: newest date on the page 2026-10-09; tables: carbon_intensity_hourly to 2026-10-09 (PT1H): fresh; eia930_all_emissions to 2026-10-09 (PT1H): fresh. On 20 October: public.
- Broken: console exceptions 0; dead links 0; placeholders ('not held' and the like) 0; sideways scroll no; 440 words, 1649 px tall
- Scores: usefulness 4, accuracy 5, clarity 4, finish 4
- Verdict: merge into the Grid tool's 'how clean' or into /mix/clean: three pages carry the carbon story.

### /consumption: Consumption by sector

- For: Retail sales and energy by sector and state, where industrial and commercial load grows. For a planner.
- In 10 seconds: partly: the US block answers; the state tables are long.
- Screenshot: `docs/reviews/erw-review-2026-10-12/consumption.png`
- Checked: `series_esum | eia_retail_sales_monthly | eia:retail_sales:US:ALL | retail_sales | 2025-08-01T00:00:00Z | 2026-08-01T00:00:00Z | page shows "4,089,342,191.31" | page read 4089342191.3100004 | Supabase 4089342191.3100004`
- Fresh: newest date on the page none printed; tables: eia_retail_sales_monthly to 2026-07-01 (P1M): fresh; eia_sector_energy_consumption_monthly to 2026-06-01 (P1M): stale, 134 days. On 20 October: public.
- Broken: console exceptions 0; dead links 0; placeholders ('not held' and the like) 0; sideways scroll no; 1012 words, 2906 px tall
- Scores: usefulness 3, accuracy 5, clarity 3, finish 4
- Verdict: merge into /demand as its 'by sector' view.

### /map: The project map

- For: The project map: operating and planned units, datacenters and deals on one map. For anyone asking where things are being built.
- In 10 seconds: partly: the map answers if the reader knows what to click; the choose block is above the map.
- Screenshot: `docs/reviews/erw-review-2026-10-12/map.png`
- Checked: no check key on the page; a table behind it probed by hand in `runs/session229/probes.json` (session 229)
- Fresh: newest date on the page 2026-10-09; tables: energy_projects to 2026-10-12 (snapshot): fresh; datacenter_facilities to 2026-10-12 (snapshot): fresh. On 20 October: license needed (datacenter_facilities), license needed (energy_projects).
- Broken: console exceptions 0; dead links 0; placeholders ('not held' and the like) 0; sideways scroll no; 578 words, 2753 px tall
- Scores: usefulness 4, accuracy 4, clarity 3, finish 3
- Verdict: keep; merge /resources into it as a layer switch.

### /resources: Where the resources are

- For: Where the natural resources are (wind, solar, geothermal, hydropower, the queue) as map layers. For a developer siting a plant.
- In 10 seconds: no: 153 words, a list of layers and a method heading named 'Session 159'; the map itself is the content and it opens in a second step.
- Screenshot: `docs/reviews/erw-review-2026-10-12/resources.png`
- Checked: no check key on the page (a page of words, of files, or of the reader's own numbers)
- Fresh: newest date on the page none printed; tables: eia860m_operating_generators to 2026-10-12 (snapshot): fresh; eia860m_planned_generators to 2026-10-12 (snapshot): fresh; energy_projects to 2026-10-12 (snapshot): fresh; datacenter_facilities to 2026-10-12 (snapshot): fresh. On 20 October: license needed (energy_projects), license needed (datacenter_facilities), public.
- Broken: console exceptions 0; dead links 0; placeholders ('not held' and the like) 1; sideways scroll no; 153 words, 1505 px tall
- Scores: usefulness 3, accuracy 4, clarity 2, finish 2
- Verdict: merge into /map as layers; take the session heading off the face.

### /datacenters: Datacenter power tracker

- For: The datacenter power tracker: facilities from the news, the operators' site lists and the queues, with megawatts. The platform's sharpest lens.
- In 10 seconds: partly: 9,562 words and a 23,000 px page; the summary numbers are there but the page is the whole list.
- Screenshot: `docs/reviews/erw-review-2026-10-12/datacenters.png`
- Checked: `datacenters | count | page shows "380" | page read 380 | Supabase 380`
- Fresh: newest date on the page 2026-10-09; tables: datacenter_facilities to 2026-10-12 (snapshot): fresh. On 20 October: license needed (datacenter_facilities).
- Broken: console exceptions 0; dead links 0; placeholders ('not held' and the like) 0; sideways scroll no; 9562 words, 23474 px tall
- Scores: usefulness 5, accuracy 3, clarity 2, finish 3
- Verdict: improve: a top block (facilities, megawatts, this week's additions) and the list folded by operator; the tables behind it are 'license needed' on 20 October (datacenter_facilities, the news outlets).

### /storage: Battery storage

- For: Battery storage in the US: the fleet, by ISO and state, planned additions, the daily cycle. One of the pages that was live.
- In 10 seconds: yes: the fleet's size and the cycle in one screen.
- Screenshot: `docs/reviews/erw-review-2026-10-12/storage.png`
- Checked: `storage | n | operating | page shows "1,137" | page read 1137 | Supabase 1137`
- Fresh: newest date on the page 2026-10-11; tables: storage_capacity to 2026-10-12 (snapshot): fresh; storage_daily_cycle to 2026-10-11 (P1D): fresh; eia930_all_storage to 2026-10-11 (PT1H): fresh. On 20 October: public.
- Broken: console exceptions 0; dead links 0; placeholders ('not held' and the like) 0; sideways scroll no; 638 words, 2843 px tall
- Scores: usefulness 4, accuracy 5, clarity 4, finish 4
- Verdict: keep

### /storage/buildout: How much storage has been built

- For: How much storage has been built, by year, duration and grid, against solar. For a storage analyst.
- In 10 seconds: yes: one chart answers.
- Screenshot: `docs/reviews/erw-review-2026-10-12/storage-buildout.png`
- Checked: `series | storage_buildout_monthly | us:total | battery_operating_mw | 2026-08-01T00:00:00Z | page shows "54,489" | page read 54488.9 | Supabase 54488.9`
- Fresh: newest date on the page none printed; tables: storage_buildout_monthly to 2026-08-01 (P1M): fresh. On 20 October: public.
- Broken: console exceptions 0; dead links 0; placeholders ('not held' and the like) 1; sideways scroll no; 569 words, 2306 px tall
- Scores: usefulness 4, accuracy 5, clarity 4, finish 4
- Verdict: merge into /storage as its 'build-out' tab.

### /storage/owners: Who owns the batteries

- For: Who owns the batteries, operating and planned, the largest owners. For a deal analyst.
- In 10 seconds: yes: a ranked table.
- Screenshot: `docs/reviews/erw-review-2026-10-12/storage-owners.png`
- Checked: no check key on the page; a table behind it probed by hand in `runs/session229/probes.json` (session 229)
- Fresh: newest date on the page 2026-10-13; tables: storage_owners_monthly to 2026-08-01 (P1M): fresh. On 20 October: public.
- Broken: console exceptions 0; dead links 0; placeholders ('not held' and the like) 0; sideways scroll no; 777 words, 3288 px tall
- Scores: usefulness 3, accuracy 5, clarity 4, finish 4
- Verdict: merge into /storage as its 'owners' tab.

### /companies: Companies

- For: Energy companies the warehouse knows, with their projects and deals. For a deal analyst.
- In 10 seconds: no: 5,034 words, a list with no question at the top; no check key on the page.
- Screenshot: `docs/reviews/erw-review-2026-10-12/companies.png`
- Checked: no check key on the page; a table behind it probed by hand in `runs/session229/probes.json` (session 229)
- Fresh: newest date on the page none printed; tables: energy_companies to 2026-10-12 (snapshot): fresh. On 20 October: public.
- Broken: console exceptions 0; dead links 0; placeholders ('not held' and the like) 0; sideways scroll no; 5034 words, 13981 px tall
- Scores: usefulness 3, accuracy 3, clarity 2, finish 2
- Verdict: merge into /deals (the company is a filter of deals) or cut from the menu.

### /deals: Energy deals

- For: Energy deals from the news: who, what, how much, by week. For a deal analyst.
- In 10 seconds: partly: the week's deals are at the top, but 5,464 words follow with 454 links.
- Screenshot: `docs/reviews/erw-review-2026-10-12/deals.png`
- Checked: `deals | month_count | 2026-10 | page shows "61" | page read 61 | Supabase 61`
- Fresh: newest date on the page 2026-10-09; tables: energy_deals to 2026-10-09 (event): fresh. On 20 October: license needed (energy_deals).
- Broken: console exceptions 0; dead links 0; placeholders ('not held' and the like) 0; sideways scroll no; 5464 words, 17483 px tall
- Scores: usefulness 4, accuracy 4, clarity 3, finish 3
- Verdict: improve: lead with this week and fold the rest; its tables are 'license needed' on 20 October (energy_deals, the news outlets).

### /analysis: Automated Analysis

- For: Automated Analysis: findings on demand, each a question, a chart, the numbers before and after, the why and a method footnote, with downloads; the weekly chart templates. Sellable tool four.
- In 10 seconds: partly: the first card answers in one screen, but 8,072 words and a 29,000 px page carry nine cards, the scanner's list, the request form and the week's templates on one scroll; at 390 px it is a 3.7 MB screenshot.
- Screenshot: `docs/reviews/erw-review-2026-10-12/analysis.png`, `docs/reviews/erw-review-2026-10-12/analysis-390.png` (390)
- Checked: no check key on the page (a page of words, of files, or of the reader's own numbers)
- Fresh: newest date on the page 2026-10-12; tables: no table behind it (a page of words or of the reader's own numbers). On 20 October: public.
- Broken: console exceptions 0; dead links 0; placeholders ('not held' and the like) 7; sideways scroll no; 8072 words, 16081 px tall
- Scores: usefulness 5, accuracy 4, clarity 3, finish 3
- Verdict: improve: one card a screen with a card index; the request form and the templates as their own tabs; this is the tool roadmap item 2 wants 'in its final form'.

### /ask: Ask the warehouse

- For: A question box over the live set, answered only from queries, the table named. Part of the Grid tool.
- In 10 seconds: yes as a box; nothing is answered until asked, and the page says the limits (35 days of prices, 10 questions an hour).
- Screenshot: `docs/reviews/erw-review-2026-10-12/ask.png`, `docs/reviews/erw-review-2026-10-12/ask-390.png` (390)
- Checked: no check key on the page (a page of words, of files, or of the reader's own numbers)
- Fresh: newest date on the page none printed; tables: no table behind it (a page of words or of the reader's own numbers). On 20 October: public.
- Broken: console exceptions 0; dead links 0; placeholders ('not held' and the like) 0; sideways scroll no; 88 words, 900 px tall
- Scores: usefulness 4, accuracy 4, clarity 4, finish 3
- Verdict: merge into the Grid tool's page as its question box (roadmap item 2); add three example questions with their answers.

### /events: Events

- For: The events the warehouse studies (Uri, Elliott, the heat waves) and the Flex Alert scorecard. For an analyst of stress.
- In 10 seconds: partly: a list of events; the scorecard's finding is below.
- Screenshot: `docs/reviews/erw-review-2026-10-12/events.png`
- Checked: `series | event_window_daily | eia930:CISO | demand_max_pct_vs_baseline | 2020-08-18T00:00:00+00:00 | caiso_heat_2020 | page shows "23.50" | page read 23.4955 | Supabase 23.4955`
- Fresh: newest date on the page 2025-06-28; tables: event_window_daily to 2025-06-28 (P1D;P1W): stale, 472 days. On 20 October: license needed (event_window_daily).
- Broken: console exceptions 0; dead links 0; placeholders ('not held' and the like) 0; sideways scroll no; 276 words, 998 px tall
- Scores: usefulness 3, accuracy 5, clarity 3, finish 4
- Verdict: keep as the index of the event pages; its table is 'license needed' on 20 October (event_window_daily).

### /policy: Policy

- For: Policy actions this week and every action, with one-line reads. For a policy analyst.
- In 10 seconds: partly: 'this week' answers; 9,433 words and 18,000 px follow.
- Screenshot: `docs/reviews/erw-review-2026-10-12/policy.png`
- Checked: no check key on the page; a table behind it probed by hand in `runs/session229/probes.json` (session 229)
- Fresh: newest date on the page 2027-03-10; tables: policy_actions to 2026-10-13 (event): fresh; policy_reads to 2026-10-13 (event): fresh. On 20 October: public.
- Broken: console exceptions 0; dead links 0; placeholders ('not held' and the like) 0; sideways scroll no; 9433 words, 18187 px tall
- Scores: usefulness 4, accuracy 4, clarity 3, finish 3
- Verdict: improve: fold 'every action' by month; the newest date printed is 2026-12-08, a future date the page prints as filed.

### /thesis: Thesis Builder

- For: Thesis Builder: a niche typed, a run queued, a report in tabs. For an investor.
- In 10 seconds: no: a form and a list of runs; nothing to read until a run is made; its table is internal.
- Screenshot: `docs/reviews/erw-review-2026-10-12/thesis.png`
- Checked: no check key on the page (a page of words, of files, or of the reader's own numbers)
- Fresh: newest date on the page none printed; tables: no table behind it (a page of words or of the reader's own numbers). On 20 October: public.
- Broken: console exceptions 0; dead links 0; placeholders ('not held' and the like) 0; sideways scroll no; 409 words, 900 px tall
- Scores: usefulness 2, accuracy 3, clarity 3, finish 2
- Verdict: cut from the visitor menu until a run is public; keep internal.

### /play/battery: The home battery game

- For: The home battery game on real prices. For a reader new to the industry.
- In 10 seconds: yes: one screen, one choice.
- Screenshot: `docs/reviews/erw-review-2026-10-12/play-battery.png`
- Checked: `series | iso_rtm_hub_prices | ercot:HB_HUBAVG | spp_rtm | 2026-10-11T15:15:00+00:00 | page shows "-2.40" | page read -2.4 | Supabase -2.4`
- Fresh: newest date on the page 2026-10-11; tables: iso_rtm_hub_prices to 2026-10-12 (PT15M;PT1H): fresh; ercot_all_hub_prices_history to 2026-08-26 (PT15M;PT1H): stale, 48 days. On 20 October: license needed (iso_rtm_hub_prices), public.
- Broken: console exceptions 0; dead links 0; placeholders ('not held' and the like) 0; sideways scroll no; 133 words, 900 px tall
- Scores: usefulness 2, accuracy 4, clarity 4, finish 4
- Verdict: keep in Games.

### /tour: The tour

- For: The tour of the site. For a first visitor.
- In 10 seconds: partly: 340 words of links; it names pages that are in review.
- Screenshot: `docs/reviews/erw-review-2026-10-12/tour.png`
- Checked: no check key on the page (a page of words, of files, or of the reader's own numbers)
- Fresh: newest date on the page none printed; tables: no table behind it (a page of words or of the reader's own numbers). On 20 October: public.
- Broken: console exceptions 0; dead links 0; placeholders ('not held' and the like) 0; sideways scroll no; 340 words, 1007 px tall
- Scores: usefulness 2, accuracy 3, clarity 3, finish 3
- Verdict: merge into /about or cut.

### /learn/problems/know-your-grid: Know your grid: ERCOT and CAISO side by side

- For: Problem set: five questions on ERCOT and CAISO with answers from the tables. For a student.
- In 10 seconds: yes: question one is on the first screen.
- Screenshot: `docs/reviews/erw-review-2026-10-12/learn-problems-know-your-grid.png`
- Checked: `calc | ratio | series_max~eia930_all_demand~demand_mw~2026-10-11T00:00:00Z~2026-10-12T00:00:00Z~eia930:ERCO | series_max~eia930_all_demand~demand_mw~2026-10-11T00:00:00Z~2026-10-12T00:00:00Z~eia930:CISO | page shows "2.57" | page read 2.572708743323025 | Supabase 2.572708743323025`
- Fresh: newest date on the page 2026-10-10; tables: eia930_all_demand to 2026-10-11 (PT1H): fresh; eia930_all_generation to 2026-10-11 (PT1H): fresh; storage_daily_cycle to 2026-10-11 (P1D): fresh; carbon_intensity_daily to 2026-10-09 (P1D): fresh. On 20 October: public.
- Broken: console exceptions 0; dead links 0; placeholders ('not held' and the like) 0; sideways scroll no; 234 words, 1307 px tall
- Scores: usefulness 3, accuracy 5, clarity 4, finish 4
- Verdict: keep in Games (Learn).

### /learn/problems/prices-and-your-bill: Prices and your bill

- For: Problem set: prices and a bill. For a student.
- In 10 seconds: yes
- Screenshot: `docs/reviews/erw-review-2026-10-12/learn-problems-prices-and-your-bill.png`
- Checked: `series | cost_of_power_monthly | ercot:HB_HUBAVG | rt_simple_mean | 2026-09-01T00:00:00+00:00 | page shows "38.39" | page read 38.3874 | Supabase 38.3874`
- Fresh: newest date on the page none printed; tables: cost_of_power_monthly to 2026-10-01 (P1M): fresh; cost_of_power_hourly_profile to 2026-10-01 (P1M): fresh. On 20 October: license needed (cost_of_power_monthly), license needed (cost_of_power_hourly_profile).
- Broken: console exceptions 0; dead links 0; placeholders ('not held' and the like) 0; sideways scroll no; 240 words, 1355 px tall
- Scores: usefulness 3, accuracy 5, clarity 4, finish 4
- Verdict: keep

### /learn/problems/when-the-grid-broke: When the grid broke: four events

- For: Problem set: four events. For a student.
- In 10 seconds: yes
- Screenshot: `docs/reviews/erw-review-2026-10-12/learn-problems-when-the-grid-broke.png`
- Checked: `calc | ratio | series~event_window_daily~ercot:HB_HUBAVG~rt_max~2021-02-17T00:00:00+00:00~uri_2021 | series~event_window_daily~ercot:HB_HUBAVG~rt_max~2020-02-10T00:00:00+00:00~uri_2021 | page shows "5.35" | page read 5.350785928364949 | Supabase 5.350785928364949`
- Fresh: newest date on the page 2020-08-14; tables: event_window_daily to 2025-06-28 (P1D;P1W): stale, 472 days. On 20 October: license needed (event_window_daily).
- Broken: console exceptions 0; dead links 0; placeholders ('not held' and the like) 0; sideways scroll no; 274 words, 1423 px tall
- Scores: usefulness 3, accuracy 5, clarity 4, finish 4
- Verdict: keep; its table is 'license needed' on 20 October (event_window_daily).

### /learn/problems/networks-and-money: Networks and money

- For: Problem set: networks and money. For a student.
- In 10 seconds: yes
- Screenshot: `docs/reviews/erw-review-2026-10-12/learn-problems-networks-and-money.png`
- Checked: `net | ties | ERCO | 2026-10-11T03:00:00Z | page shows "2" | page read 2 | Supabase 2`
- Fresh: newest date on the page 2026-10-11; tables: eia930_all_interchange to 2026-10-10 (PT1H): fresh; merchant_revenue_monthly to 2026-10-01 (P1M): fresh. On 20 October: license needed (merchant_revenue_monthly), public.
- Broken: console exceptions 0; dead links 0; placeholders ('not held' and the like) 0; sideways scroll no; 334 words, 1491 px tall
- Scores: usefulness 3, accuracy 5, clarity 4, finish 4
- Verdict: keep

### /data: Data

- For: Data and methods: the catalogue of public tables, coverage, access, the dictionary, the methods. For a researcher or a licensing reader.
- In 10 seconds: partly: the coverage count answers; 4,632 words follow; two of its download links answer 502 on production (eia930_all_generation and eia930_all_emissions, the two largest tables).
- Screenshot: `docs/reviews/erw-review-2026-10-12/data.png`
- Checked: `catalogue | ai_power_regions | n_rows | page shows "187" | page read 187 | Supabase 187`
- Fresh: newest date on the page 2026-10-19; tables: no table behind it (a page of words or of the reader's own numbers). On 20 October: public.
- Broken: console exceptions 0; dead links 4 (/api/download?table=caiso_reliability_daily (502), /api/download?table=eia_fuel_spot_prices (502), /api/download?table=eia930_all_emissions (502), /api/download?table=eia930_all_generation (502)); placeholders ('not held' and the like) 1; sideways scroll no; 4632 words, 14315 px tall. the local build answered 502 for four downloads and production for two (the largest tables): the route's timeout, not a missing table.
- Scores: usefulness 5, accuracy 4, clarity 3, finish 3
- Verdict: improve: a download that times out should say the table is too large for the route and point to Redivis; the table of pages should show the status a visitor sees.

### /about: About

- For: What the ERW is, how the digest and the Roundup are made, the platform, the site, a glossary.
- In 10 seconds: partly: 2,157 words; the first paragraph answers, the glossary is the bulk.
- Screenshot: `docs/reviews/erw-review-2026-10-12/about.png`
- Checked: no check key on the page (a page of words, of files, or of the reader's own numbers)
- Fresh: newest date on the page none printed; tables: no table behind it (a page of words or of the reader's own numbers). On 20 October: public.
- Broken: console exceptions 0; dead links 0; placeholders ('not held' and the like) 0; sideways scroll no; 2157 words, 3905 px tall
- Scores: usefulness 3, accuracy 4, clarity 3, finish 4
- Verdict: keep; the glossary could be its own page or a fold.

### /terms: Terms

- For: Terms: data licensing per source, subscribers, Ask, usage counts.
- In 10 seconds: yes for its reader (a lawyer or a licensing reader).
- Screenshot: `docs/reviews/erw-review-2026-10-12/terms.png`
- Checked: no check key on the page (a page of words, of files, or of the reader's own numbers)
- Fresh: newest date on the page 2026-10-04; tables: no table behind it (a page of words or of the reader's own numbers). On 20 October: public.
- Broken: console exceptions 0; dead links 0; placeholders ('not held' and the like) 0; sideways scroll no; 2835 words, 9953 px tall
- Scores: usefulness 4, accuracy 5, clarity 4, finish 4
- Verdict: keep; the per-source licensing table is the document the 20 October launch needs.

### /digest: ERW's Energy Digest, 2026-10-12

- For: The weekday Energy Digest: top of the industry, by sector, AI and power, the numbers today, the archive.
- In 10 seconds: yes: the top five in one screen.
- Screenshot: `docs/reviews/erw-review-2026-10-12/digest.png`
- Checked: no check key on the page; a table behind it probed by hand in `runs/session229/probes.json` (session 229)
- Fresh: newest date on the page 2026-10-12; tables: news_index to 2026-10-12 (event): fresh. On 20 October: license needed (news_index).
- Broken: console exceptions 0; dead links 0; placeholders ('not held' and the like) 0; sideways scroll no; 1175 words, 4076 px tall
- Scores: usefulness 4, accuracy 4, clarity 4, finish 4
- Verdict: keep; its index table is 'license needed' on 20 October (news_index: the outlets).

### /roundup: ERW's Roundup, 2026-W41

- For: The Sunday Roundup: five stories, deals, datacenter announcements, policy of the week.
- In 10 seconds: yes: the five stories first.
- Screenshot: `docs/reviews/erw-review-2026-10-12/roundup.png`
- Checked: no check key on the page (a page of words, of files, or of the reader's own numbers)
- Fresh: newest date on the page 2026-10-11; tables: news_index to 2026-10-12 (event): fresh; energy_deals to 2026-10-09 (event): fresh; datacenter_projects to 2026-10-09 (snapshot): fresh. On 20 October: license needed (energy_deals), license needed (datacenter_projects), license needed (news_index).
- Broken: console exceptions 0; dead links 0; placeholders ('not held' and the like) 0; sideways scroll no; 2054 words, 9493 px tall
- Scores: usefulness 4, accuracy 4, clarity 4, finish 4
- Verdict: keep; the same license question as the digest.

### /subscribe: Email

- For: The email sign-up.
- In 10 seconds: yes
- Screenshot: `docs/reviews/erw-review-2026-10-12/subscribe.png`
- Checked: no check key on the page (a page of words, of files, or of the reader's own numbers)
- Fresh: newest date on the page none printed; tables: no table behind it (a page of words or of the reader's own numbers). On 20 October: public.
- Broken: console exceptions 0; dead links 0; placeholders ('not held' and the like) 0; sideways scroll no; 336 words, 1062 px tall
- Scores: usefulness 2, accuracy 5, clarity 4, finish 4
- Verdict: keep as an aside, not a menu page.

### /privacy: Privacy

- For: What the site records and what it does not.
- In 10 seconds: yes
- Screenshot: `docs/reviews/erw-review-2026-10-12/privacy.png`
- Checked: no check key on the page (a page of words, of files, or of the reader's own numbers)
- Fresh: newest date on the page none printed; tables: no table behind it (a page of words or of the reader's own numbers). On 20 October: public.
- Broken: console exceptions 0; dead links 0; placeholders ('not held' and the like) 0; sideways scroll no; 726 words, 1579 px tall
- Scores: usefulness 3, accuracy 5, clarity 4, finish 4
- Verdict: keep

### /grid/ercot: ERCOT: Electric Reliability Council of Texas

- For: ERCOT's page: who runs it, demand now, where the power comes from, batteries, how clean, with the grid's own alerts. For anyone asking about one grid.
- In 10 seconds: yes: demand now and the mix on the first screen.
- Screenshot: `docs/reviews/erw-review-2026-10-12/grid-ercot.png`
- Checked: `series | eia930_all_demand | eia930:ERCO | demand_mw | 2026-10-11T23:00:00+00:00 | page shows "70,555" | page read 70555 | Supabase 70555`
- Fresh: newest date on the page 2026-10-12; tables: no table behind it (a page of words or of the reader's own numbers). On 20 October: public.
- Broken: console exceptions 0; dead links 0; placeholders ('not held' and the like) 0; sideways scroll no; 1621 words, 5551 px tall
- Scores: usefulness 4, accuracy 5, clarity 4, finish 4
- Verdict: merge into the Grid tool as the grid's view (one page, seven grids), with /grid, /mix and /network.

### /grid/caiso: CAISO: California Independent System Operator

- For: CAISO's page: who runs it, demand now, where the power comes from, batteries, how clean, with the grid's own alerts. For anyone asking about one grid.
- In 10 seconds: yes: demand now and the mix on the first screen.
- Screenshot: `docs/reviews/erw-review-2026-10-12/grid-caiso.png`
- Checked: `series | eia930_all_demand | eia930:CISO | demand_mw | 2026-10-11T23:00:00+00:00 | page shows "25,638" | page read 25638 | Supabase 25638`
- Fresh: newest date on the page 2026-10-12; tables: no table behind it (a page of words or of the reader's own numbers). On 20 October: public.
- Broken: console exceptions 0; dead links 0; placeholders ('not held' and the like) 10; sideways scroll no; 2788 words, 7567 px tall
- Scores: usefulness 4, accuracy 5, clarity 4, finish 4
- Verdict: merge into the Grid tool as the grid's view (one page, seven grids), with /grid, /mix and /network.

### /grid/pjm: PJM: PJM Interconnection

- For: PJM's page: who runs it, demand now, where the power comes from, batteries, how clean, with the grid's own alerts. For anyone asking about one grid.
- In 10 seconds: yes: demand now and the mix on the first screen.
- Screenshot: `docs/reviews/erw-review-2026-10-12/grid-pjm.png`
- Checked: `series | eia930_all_demand | eia930:PJM | demand_mw | 2026-10-11T23:00:00+00:00 | page shows "91,870" | page read 91870 | Supabase 91870`
- Fresh: newest date on the page 2026-10-11; tables: no table behind it (a page of words or of the reader's own numbers). On 20 October: public.
- Broken: console exceptions 0; dead links 0; placeholders ('not held' and the like) 0; sideways scroll no; 1462 words, 5123 px tall
- Scores: usefulness 4, accuracy 5, clarity 4, finish 4
- Verdict: merge into the Grid tool as the grid's view (one page, seven grids), with /grid, /mix and /network.

### /grid/nyiso: NYISO: New York Independent System Operator

- For: NYISO's page: who runs it, demand now, where the power comes from, batteries, how clean, with the grid's own alerts. For anyone asking about one grid.
- In 10 seconds: yes: demand now and the mix on the first screen.
- Screenshot: `docs/reviews/erw-review-2026-10-12/grid-nyiso.png`
- Checked: `series | eia930_all_demand | eia930:NYIS | demand_mw | 2026-10-11T23:00:00+00:00 | page shows "16,480" | page read 16480 | Supabase 16480`
- Fresh: newest date on the page 2026-10-13; tables: no table behind it (a page of words or of the reader's own numbers). On 20 October: public.
- Broken: console exceptions 0; dead links 0; placeholders ('not held' and the like) 0; sideways scroll no; 1443 words, 5069 px tall
- Scores: usefulness 4, accuracy 5, clarity 4, finish 4
- Verdict: merge into the Grid tool as the grid's view (one page, seven grids), with /grid, /mix and /network.

### /grid/isone: ISO-NE: ISO New England

- For: ISO-NE's page: who runs it, demand now, where the power comes from, batteries, how clean, with the grid's own alerts. For anyone asking about one grid.
- In 10 seconds: yes: demand now and the mix on the first screen.
- Screenshot: `docs/reviews/erw-review-2026-10-12/grid-isone.png`
- Checked: `series | eia930_all_demand | eia930:ISNE | demand_mw | 2026-10-11T23:00:00+00:00 | page shows "13,399" | page read 13399 | Supabase 13399`
- Fresh: newest date on the page 2026-10-12; tables: no table behind it (a page of words or of the reader's own numbers). On 20 October: public.
- Broken: console exceptions 0; dead links 0; placeholders ('not held' and the like) 0; sideways scroll no; 1539 words, 5484 px tall
- Scores: usefulness 4, accuracy 5, clarity 4, finish 4
- Verdict: merge into the Grid tool as the grid's view (one page, seven grids), with /grid, /mix and /network.

### /grid/miso: MISO: Midcontinent Independent System Operator

- For: MISO's page: who runs it, demand now, where the power comes from, batteries, how clean, with the grid's own alerts. For anyone asking about one grid.
- In 10 seconds: partly: MISO's prices are paused since 4 October, so its price blocks are older than the rest.
- Screenshot: `docs/reviews/erw-review-2026-10-12/grid-miso.png`
- Checked: `series | eia930_all_demand | eia930:MISO | demand_mw | 2026-10-11T23:00:00+00:00 | page shows "83,241" | page read 83241 | Supabase 83241`
- Fresh: newest date on the page 2026-10-11; tables: no table behind it (a page of words or of the reader's own numbers). On 20 October: public.
- Broken: console exceptions 0; dead links 0; placeholders ('not held' and the like) 0; sideways scroll no; 1420 words, 5135 px tall
- Scores: usefulness 3, accuracy 4, clarity 4, finish 3
- Verdict: merge into the Grid tool as the grid's view (one page, seven grids), with /grid, /mix and /network.

### /grid/spp: SPP: Southwest Power Pool

- For: SPP's page: who runs it, demand now, where the power comes from, batteries, how clean, with the grid's own alerts. For anyone asking about one grid.
- In 10 seconds: yes: demand now and the mix on the first screen.
- Screenshot: `docs/reviews/erw-review-2026-10-12/grid-spp.png`
- Checked: `series | eia930_all_demand | eia930:SWPP | demand_mw | 2026-10-11T23:00:00+00:00 | page shows "41,055" | page read 41055 | Supabase 41055`
- Fresh: newest date on the page 2026-10-12; tables: no table behind it (a page of words or of the reader's own numbers). On 20 October: public.
- Broken: console exceptions 0; dead links 0; placeholders ('not held' and the like) 0; sideways scroll no; 1558 words, 5476 px tall
- Scores: usefulness 4, accuracy 5, clarity 4, finish 4
- Verdict: merge into the Grid tool as the grid's view (one page, seven grids), with /grid, /mix and /network.

### /data/methods: 404

- For: The methods index.
- In 10 seconds: no: the local build answers 404 ('This page could not be found'); production answers 200 (23 KB). The release map lists it; the route exists only through a rewrite or a static file not in the local build.
- Screenshot: `docs/reviews/erw-review-2026-10-12/data-methods.png`
- Checked: no check key on the page (a page of words, of files, or of the reader's own numbers)
- Fresh: newest date on the page none printed; tables: no table behind it (a page of words or of the reader's own numbers). On 20 October: public.
- Broken: console exceptions 0; dead links 0; placeholders ('not held' and the like) 0; sideways scroll no; 7 words, 1048 px tall. 404 on the local build; 200 on production.
- Scores: usefulness 3, accuracy 2, clarity 2, finish 1
- Verdict: improve: find why the local route 404s; a methods index the methods pages link back to.

### /data/standard: ERW Data Standard v0

- For: The data standard, version 0, in full.
- In 10 seconds: yes for a data engineer; 7,532 words.
- Screenshot: `docs/reviews/erw-review-2026-10-12/data-standard.png`
- Checked: no check key on the page (a page of words, of files, or of the reader's own numbers)
- Fresh: newest date on the page 2026-09-29; tables: no table behind it (a page of words or of the reader's own numbers). On 20 October: public.
- Broken: console exceptions 0; dead links 0; placeholders ('not held' and the like) 0; sideways scroll no; 7532 words, 18652 px tall
- Scores: usefulness 3, accuracy 5, clarity 3, finish 4
- Verdict: keep under Data.

### /data/faults: Known data faults

- For: Known faults in source data, with their status.
- In 10 seconds: yes for a data engineer; 7,459 words.
- Screenshot: `docs/reviews/erw-review-2026-10-12/data-faults.png`
- Checked: no check key on the page (a page of words, of files, or of the reader's own numbers)
- Fresh: newest date on the page 2026-10-05; tables: no table behind it (a page of words or of the reader's own numbers). On 20 October: public.
- Broken: console exceptions 0; dead links 0; placeholders ('not held' and the like) 0; sideways scroll no; 7459 words, 16293 px tall
- Scores: usefulness 4, accuracy 5, clarity 3, finish 4
- Verdict: keep under Data.

### /cost-of-power/battery (branch): What a battery earns

- For: The battery tool as the branch wip/203-brand-battery holds it (sessions 203, 208, 211): three questions, the contract as two scenario assumptions, the sensitivity chart in its own section, the brand's type and tables.
- In 10 seconds: yes: 'What did it earn?' answers in the first sentence, the three numbers under it; 1,767 words.
- Screenshot: `docs/reviews/erw-review-2026-10-12/branch-cost-of-power-battery.png`, `docs/reviews/erw-review-2026-10-12/branch-cost-of-power-battery-390.png` (390)
- Checked: the branch pages: check-values 461 of 461 on the three cost-of-power pages (session 228, `runs/session228/check_values6.out`)
- Fresh: newest date on the page none printed; tables: battery_stack_monthly to 2026-10-01 (P1M): fresh; battery_stack_stress_daily to 2023-09-10 (P1D): stale, 1129 days. On 20 October: public.
- Broken: console exceptions 0; dead links 0; placeholders ('not held' and the like) 5; sideways scroll no; 1767 words, 4682 px tall
- Scores: usefulness 5, accuracy 5, clarity 5, finish 4
- Verdict: land it (after Samuel's approval of the screenshots in docs/brand/review-211).

### /cost-of-power/seller (branch): What a generator earns

- For: The generator tool as wip/212-generator-layout holds it (session 212): the battery's three questions, two CSV downloads for the tables that left the page.
- In 10 seconds: yes: the first sentence and three numbers; 1,661 words against 3,086 on main; one placeholder against 205.
- Screenshot: `docs/reviews/erw-review-2026-10-12/branch-cost-of-power-seller.png`, `docs/reviews/erw-review-2026-10-12/branch-cost-of-power-seller-390.png` (390)
- Checked: the branch pages: check-values 461 of 461 on the three cost-of-power pages (session 228, `runs/session228/check_values6.out`)
- Fresh: newest date on the page 2026-10-12; tables: merchant_revenue_monthly to 2026-10-01 (P1M): fresh. On 20 October: license needed (merchant_revenue_monthly).
- Broken: console exceptions 0; dead links 0; placeholders ('not held' and the like) 1; sideways scroll no; 1661 words, 4129 px tall
- Scores: usefulness 5, accuracy 5, clarity 4, finish 4
- Verdict: land it after the battery.

### /cost-of-power (branch): What a datacenter pays

- For: The datacenter tool as wip/213-datacenter-layout holds it with session 228: four questions answered for the load, then the two decision questions.
- In 10 seconds: yes: each of the four in one sentence with its number; 2,818 words, 71 check keys, every one recomputed by check-values (461 of 461 on the three pages).
- Screenshot: `docs/reviews/erw-review-2026-10-12/branch-cost-of-power.png`, `docs/reviews/erw-review-2026-10-12/branch-cost-of-power-390.png` (390)
- Checked: the branch pages: check-values 461 of 461 on the three cost-of-power pages (session 228, `runs/session228/check_values6.out`)
- Fresh: newest date on the page 2026-10-09; tables: cost_of_power_monthly to 2026-10-01 (P1M): fresh; cost_of_power_hourly_profile to 2026-10-01 (P1M): fresh; cost_of_power_carbon to 2026-10-01 (P1M): fresh. On 20 October: license needed (cost_of_power_carbon), license needed (cost_of_power_monthly), license needed (cost_of_power_hourly_profile).
- Broken: console exceptions 0; dead links 0; placeholders ('not held' and the like) 2; sideways scroll no; 2818 words, 7536 px tall
- Scores: usefulness 5, accuracy 5, clarity 4, finish 4
- Verdict: land it after the generator; one ruling open (section F).
