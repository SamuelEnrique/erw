# What a datacenter pays: the model audited as a hostile expert would

Session 10203, 26 November 2026, chain 710 (part B), the old laptop. Read as the energy procurement lead of an AI lab who is choosing a site with this page and wants to find it wrong. In the form of `docs/reviews/battery-model-audit-2026-11-20.md`.

- Nothing changed on main but this file and its folder of evidence (`docs/reviews/datacenter-model-audit-2026-11-26/`). No table written, no lock taken, no default moved, no model called.
- Each finding's test is on its own branch, `wip/audit-datacenter-<n>`. Branches that change only words are for landing (the rows at the foot); branches whose fix would move a figure carry the test only and are not for landing.
- Earlier reads of this page are cited, not repeated: the faults of 13 November (`docs/reviews/datacenter-cost-faults-2026-11-13.md`), the reader's read of 16 November (`docs/reviews/datacenter-cost-read-2026-11-16.md`) and the ruling files of 17 November (`docs/reviews/ruling-impact-cost-of-power-2026-11-17.md`, `ruling-alternatives-cost-of-power-2026-11-17.md`).

## In short

- **The arithmetic is right.** An independent restatement written from the method note, not from the page's code, gives every figure of the default case from the page's own files to the digit: USD 34.07 per MWh over November 2025 to October 2026, USD 29,846,522 for 100 MW, a bad month of USD 37.88 (August 2026, rank 4 of 36), USD 0.0691 per GPU-hour for 49,310 GPUs, day-ahead 35.70, the hub 1.28 below the zone. 131 numbers, the flexible ways and the scenarios included, agree with the page's library to 1e-6 (the largest gap USD 0.0000000005). The published replication passes 14 of 14 on the same window.
- **"If perfectly foreseen ... the most it could have saved" holds** on all 392 cases held (every grid, region, market and seven settings) and on all 3,528 year rows: the foreseen figure is never below the rule's.
- **"All-in power per GPU-hour" is energy alone at the defaults (finding 1).** It holds no delivery, ancillary service or loss charge unless the reader types one. In Oncor's area the page's own delivery table adds USD 8.81 per MWh, 25.9 percent of the energy: the "all-in" figure is about a fifth too low. Fixed in words on its branch.
- **The load is a price taker, and the page never says so (finding 3).** The size runs to 10,000 MW, 16.6 percent of ERCOT's mean demand in 2026, and every dollar scales linearly. A rough merit order from the page's own prices and ERCOT's load: +USD 0.42 per MWh at 1,000 MW (+1.2 percent), +4.21 at 10,000 MW (+12.3 percent). Fixed in words.
- **The contract is a block shaped like the load (finding 5).** A lab's contract is usually a solar or wind PPA settled at a hub. Over the generator page's twelve months ERCOT's solar captured USD 23.27 per MWh at the hub average against a flat load's 32.20: each contracted MWh of solar costs the load USD 8.93 more than the page's arithmetic; at a 50 percent share, +4.46 per MWh of the load (+13.1 percent). Fixed in words.
- **Two kinds of dollars, again (finding 4).** Each month's own dollars, never said; in the scenarios flat prices are discounted at Lazard's money rate of 9.6 percent. With prices rising 2 percent a year the present value of 20 years for 100 MW is USD 299.42 million, not 261.19 (+14.6 percent). A figure: for Samuel's ruling.
- **Smaller.** The All grids tab's "All-in" leaves out distribution, ancillary services and losses (finding 2, words); the carbon is a grid average, not what the load adds (finding 6, words); the GPU defaults round 1.275 kW up and take the industry's overhead ratio, not a lab's (finding 7, a figure); California is priced at generator trading hubs, where a load pays its utility's load aggregation point, which no table holds (finding 8, a data request).
- **Five branches fix words and move no figure (1, 2, 3, 5, 6); two show a figure for ruling (4, 7); one shows a data gap (8).**

## The ground: each file and what it does

| File | What it does |
|---|---|
| `site/app/cost-of-power/page.tsx` | The page: the view switch (Your load, All grids, Grid by grid), the summary sentence, the cost chart and table "What will it cost", the delivery table, the node band, the one sentence of what the model cannot see, the three answers, scenarios A and B, the sensitivity chart, the decisions block and the source line |
| `site/app/cost-of-power/model.ts` | Everything "Your load" computes on the server for one address (`loadModel`): the months of the load under the rule and foreseen, the last twelve, the bad month, the hub beside the zone, the two ways the scenarios compare, scenario B at its own site, the price-years window, the four summer peaks, the node band, the tight hours, the clean share, the answers' reads |
| `site/lib/datacenter.ts` | All the cost arithmetic: inputs and bounds, an hour's price from the files, months, spans, the last twelve months, the bad month, years, the foreseen load (`weights`), the forecast rule (`ruleThresholds`, `ruleWeights`, `monthsRuled`), the clean share, GPU-hours |
| `site/lib/datacenter/finance.ts` | Scenarios A and B: the ten assumptions with defaults and sources, price, year's cost, GPU-hour, hours off and the breakeven GPU-hour, present value, the fixed price with the same present value, the "all-in" GPU-hour, B against A, the sensitivity chart |
| `site/lib/datacenter/answers.ts` | The three answers: hours at or above USD 1,000, ERCOT's reserve adder, CAISO's notices, carbon at the monthly average and hour by hour, ERCOT's large-load reports |
| `site/lib/datacenter/delivery.ts` | Texas's delivery charges: each tariff line to USD per MWh for a flat load, components and totals |
| `site/app/cost-of-power/LoadHeadline.tsx`, `LoadScenarios.tsx`, `LoadAnswers.tsx`, `LoadForm.tsx`, `LoadSiteB.tsx`, `LoadCharts.tsx` | The page's pieces: the three headline numbers (scenario A's rows), the scenario rows and their notes, the answers' sentences and hovers, the form |
| `site/app/cost-of-power/AllGridsView.tsx`, `site/lib/siting.ts` | The All grids tab: every grid, hub, zone and ERCOT node, energy, "Transmission and 4CP", capacity, the "All-in" sum, headroom, carbon, the siting card |
| `site/app/cost-of-power/GridsView.tsx` | Grid by grid: the `cost_of_power_*` tables (method `docs/methods/cost_of_power.md`); shares no number with "Your load" |
| `site/lib/decisions.ts`, `DATACENTER_DECISIONS` | The 21 decisions at the page's foot, word for word the note's section 12 |
| `site/data/datacenter/*.json` | The page's files: one a grid and year (hourly prices by region and market in standard time, the tight hours, the carbon-free share), `index.json`, `texas_delivery.json`, `rules.json`, `how_soon.json`. Built 12 November 2026; ERCOT's `LZ_NORTH` held to 8 November 2026 |
| `warehouse/derived/datacenter_page.py`, `price_compare.py` | The builder of the page's files from the public price tables, and the reader of the tables and the rule for an hour |
| `warehouse/derived/datacenter_hourly_export.py`, `site/public/datacenter/` | The default case hour by hour (CSV), the carbon file, the do-file and the Python mirror |
| `replication/datacenter/` | `replicate.py` (14 of 14 on the files of 12 November, run here), `replicate.do` (never run), `page_figures.json` (2025-11 to 2026-10, the page's window) |
| `docs/methods/datacenter_pays_algorithm.md` | "Every number, step by step" ("the note"): sections 1 to 12, the cross-checks, the sign-off block (unsigned) |
| `docs/methods/datacenter_cost.md` | The older note: why each piece was built, every source's terms, the blocks borrowed from other tools |
| `docs/methods/cost_of_power.md` | The method of "Grid by grid" and of the generator and battery pages' shared files |

## How every number here was computed

- **The default case:** ERCOT, `LZ_NORTH`, a flat 100 MW load bought in real time, 1.3 kW per GPU, an overhead ratio of 1.56; the page's files of 12 November 2026; the last twelve months November 2025 to October 2026, all 8,760 hours held.
- **The independent restatement:** `restate.py` (standard library), written from the note's sections 3 to 5 and 4.14: months, the 95 percent rule, the last twelve, the bad month by nearest rank, the hub beside the zone, day-ahead, by year, the hours at or above USD 1,000, the forecast rule (30 prior days of day-ahead prices, the yearly budget), the foreseen load, the shifting load, and the scenarios' finance. It reads only `site/data/datacenter/`.
- **The page's own code on the same files:** `lib_figures.mjs` (`lib/datacenter.ts` and `lib/datacenter/finance.ts` run by Node as `model.ts` calls them). `compare.py` sets the two side by side.
- **One rule at a time:** `measures.py` (reuses the restatement) and `side.mjs` (the page's delivery and four-peak code). Tables of the main checkout read, never written: `ercot_as_prices`, `ercot_as_quantities`, `ercot_zone_load_hourly`, `ercot_4cp_intervals`. The generator page's public hourly file for the solar shape.
- **Is the foreseen figure ever below the rule's:** `foreseen_check.mjs`.
- Copies of every script and its printout: `docs/reviews/datacenter-model-audit-2026-11-26/` (written to run from `runs/c10203/` of a worktree).

## The arithmetic re-done

| Figure the default page prints | The page | Restated | Gap |
|---|---|---|---|
| Market energy, last twelve months, USD per MWh | 34.07 | 34.071372 | 0 (to 1e-12) |
| In all, 100 MW | USD 29.85 million (29,846,522 in the replication) | 298,465.22 per MW, 29,846,522 | 0 |
| Energy | 876,000 MWh | 8,760 MWh per MW | 0 |
| Power per GPU-hour | 0.0691 | 0.069097 | 0 |
| GPUs for 100 MW | 49,310 | 49,309.66 | 0 |
| A bad month | 37.88, August 2026, of 36 | 37.882715, 2026-08, rank 4 of 36 | 0 |
| The hub beside it, `HB_NORTH` | the zone 1.28 above | 32.790126, 1.281246 | 0 |
| Bought day-ahead (`buy=da`) | 35.70 | 35.697873 | 0 |
| Hours at or above USD 1,000; a flat 100 MW paid in them | 4; USD 446,175 | 4; 446,175 | 0 |
| By year, 2015 to 2026 | 24.04, 21.68, 23.88, 30.82, 36.35, 21.82, 150.61, 62.93, 48.69, 26.41, 32.66, 34.15 (ten months) | the same | 0 |
| Scenario A: present value, 20 years at 9.6 percent, 100 MW | USD 261.19 million | 261,194,973 | 0 (USD 0.0000000005 per MW) |
| Fixed price with the same present value; "all-in" per GPU-hour | 34.07; 0.0691 | 34.071372; 0.069097 | 0 |
| The flexible way the scenarios compare (off in 100 hours, the rule) | 31.80, 100 hours off; breakeven GPU-hour 0.4672 | 31.804736; 100; USD 230.36 per MWh not bought, 0.467174 | 0 |
| Flexible: foreseen; "the rule kept" | 29.70; 52 percent | 29.704320 (125 hours off); 51.9 | 0 |
| Off in 5 percent; shifting 20 percent | 29.69 (456 hours); 25.18 | 29.686118; 25.180913 | 0 |

- **131 numbers** compared, every one equal to 1e-6 relative or better.
- **The rule written a second time** gives the page's hours off in every case: the same 100 hours in the last twelve months, the budget of 2026 spent by July.
- **Nothing is filled:** every hour of the default window is held (8,760 of 8,760), so the 95 percent rule does not act today.

## One rule changed at a time, the default case

Each line changes one choice and keeps every other. "Worth" is the measured change of the default figure.

| Choice the page makes | The other choice | Worth, USD per MWh (34.07) or as stated | Said on the page? |
|---|---|---|---|
| The load zone `LZ_NORTH` | the hub `HB_NORTH` | -1.28 (-3.8 percent) | yes, a row of the table |
| Real time | day-ahead | +1.63 (+4.8 percent) | yes, `buy=da` |
| Months in standard time | months on the clock (Central prevailing) | -0.003 | yes (decision 5) |
| A month counts at 95 percent | whole months only | 0 today (every hour held) | yes (note, section 10, item 6) |
| A bad month by nearest rank | the interpolated 90th percentile of 36 | 37.88 against 37.11 | yes (decision 4) |
| 1.3 kW per GPU | the datasheet's 10.2 / 8 = 1.275 | GPU-hour 0.0691 to 0.0678 (-1.9 percent); GPUs 49,310 to 50,277 | the hover gives 10.2 and 8 (finding 7) |
| Overhead ratio 1.56 (industry) | 1.09 (the hover's Google fleet) | GPU-hour to 0.0483 (-30.1 percent); GPUs to 70,572 | the hover names both (finding 7) |
| Prices flat in the scenarios, discounted at 9.6 | prices rising 2 or 2.5 percent a year | present value, 100 MW: 261.19 million to 299.42 (+14.6 percent) or 310.24 (+18.8); fixed price 34.07 to 39.06 or 40.47 | no (finding 4) |
| Market energy alone | plus Oncor's delivery, from the page's own table | +8.81 (+25.9 percent); AEP Texas +8.39; CenterPoint 7.67 and TNMP 7.09, both conditional | yes for the headline; no for "all-in" (finding 1) |
| No ancillary charge | ERCOT's day-ahead plan of reserves at their clearing prices, over ERCOT's load | +0.27 over the 40 days the plan is held (3 September to 13 October 2026, 672 hours); about +0.33 over the twelve months (the 40 days' median quantity by product and hour) | the sentence names "ancillary"; "all-in" does not (findings 1, 2) |
| A price taker | a rough merit order (the median zone price by ERCOT load in 1 GW bins, the twelve months) | +0.03 at 100 MW; +0.42 at 1,000 (+1.2 percent); +2.10 at 5,000; +4.21 at 10,000 (+12.3 percent) | no (finding 3) |
| A contract in the load's own shape | a solar PPA settled at the hub average | +8.93 per contracted MWh; +4.46 per MWh of a flat load at a 50 percent share | the note says "no shape"; the page does not (finding 5) |
| Losses | the loss factors ERCOT applies to a load's metered energy | not sized: no loss table is held (data request below) | no (finding 2) |

- The own-effect line is rough: one curve for the year, blind to wind, sun and imports, which move the curve hour by hour. It sizes the order of the effect, no more.
- The ancillary line counts the day-ahead plan only. Since 5 December 2025 ERCOT also buys reserves in real time; that cost is not in any table here.

## Each claim against the code (part B, item 3)

| Claim, or question | Where | What the code does | Verdict |
|---|---|---|---|
| What "all-in" holds | the scenarios' row "All-in power per GPU-hour, over the years counted"; the chart ("where the all-in power per GPU-hour lands"); All grids' "All-in" | Scenarios: present value of market energy, the typed other charges and the upfront cost, over the present value of GPU-hours. All grids: energy, ERCOT's four-peak transmission at the Commission's wholesale rate, capacity (zero in ERCOT) | **Findings 1 and 2.** Energy, capacity and transmission are as stated; delivery beyond transmission, ancillary services, losses, ERCOT's fees, taxes and demand charges are in neither "all-in" |
| What the headline holds | the summary sentence, the income note, decision 1 | Market energy alone, every hour at the hour's price | **Right as stated**: "no delivery, transmission, capacity or ancillary charge is added". Losses and taxes are not named (finding 2) |
| The load's shape | "Your load", decision 6 | Flat, off in a budget of hours by a rule decided from day-ahead prices, off in a share, or shifting within the day; whole and at once, no minimum | **Right as stated** |
| Its flexibility's worth | "What the flexibility saves", the breakeven GPU-hour | The bill's fall, split on hover into a lower price and energy not bought; the breakeven is what a flat load paid in the hours off | **Right**; the split is the read of 16 November, row 3 |
| Day-ahead against real time | the form's market | The load pays the market chosen in every hour; the rule decides from day-ahead prices either way | **Right as stated** |
| A hub's price against where the load sits | decision 2, the node band | ERCOT: load zones, where a load settles. CAISO: three generator trading hubs (`TH_SP15_GEN-APND`, `TH_ZP26`, `TH_NP15`). NYISO: zones. ISO-NE: the hub and zones. SPP: two hubs | **Stated** (decision 2); California's load pays its utility's load aggregation point, not held (finding 8) |
| A contract | the scenarios' share and price | A share of the energy at a fixed price in every hour and every year, the rest at the market | **Finding 5**: the shape is the load's own, which no solar or wind contract has |
| An own plant | nowhere on this page | Not modelled | Not claimed |
| "Will it be there" | the answer "Will the power be there?" | Counts: hours at or above USD 1,000, ERCOT's reserve adder to 4 December 2025, CAISO's notices to 30 April 2025, the grid's tight hours, demand growth and capacity from other tools | **Measured, and each count says what it is.** It answers whether power was dear or the grid was tight, not whether a new connection can be served |
| "How soon" | the answer "How soon?" | ERCOT's large-load reports as published; the rules in motion counted; elsewhere a line that none is held | **Measured; no wait estimated, as the page says** |
| Carbon, average or marginal | "How clean?" | The ERW's intensity of consumed electricity (EIA-930), monthly, weighted by the load's monthly energy; and hour by hour over the hourly window | **Finding 6**: an average, location-based; never said on the face that it is not what the load adds |
| Carbon, the hour against the year | the same | Both shown, each with its window | **Right as stated** |
| A held grid | MISO, PJM, ISO-NE's zone history, NYISO's load queue | Not read or not shown; an address naming MISO or PJM shows ERCOT with a line that says so | **Right**: no held table reaches a figure (licenses checked in `coverage.csv`) |
| The load's own effect on price | nowhere | A price taker at any size up to 10,000 MW, dollars scaled linearly | **Finding 3** |
| The dollars' year | nowhere | Each month's own dollars, summed; 2015 beside 2026 in the chart; the scenarios' flat prices at a money rate | **Finding 4** |
| The window | the table's notes, the headline's note | The newest twelve counted months in a row, each region on its own; named beside the figure | **Right as stated** |
| "If perfectly foreseen ... the most it could have saved" | `FORESEEN_WHY` | The rule's budget of hours chosen knowing the year's prices | **Right on every case held** (392 cases, 3,528 year rows) |
| "The rule kept p percent" | the table | 100 x the rule's saving / the foreseen saving | **Right**; never above 100 on any case |
| Four summer peaks | the box and the scenarios | The flexible way's share of load in the four intervals, at the Commission's newest approved rate; not counted by default | **Right as stated**. The default flexible way avoided none of summer 2025's or 2024's four (its budget is spent by July): the read of 16 November, case 2, and the ruling file of 17 November, line 1 |

## What a procurement lead's own number would hold that this does not

Sized where files on this machine allow; per MWh of the default flat load (34.07).

| Item | Size | From |
|---|---|---|
| Delivery and transmission (Oncor, transmission voltage) | +8.81 (+25.9 percent) | the page's own table, `texas_delivery.json` |
| A solar PPA's shape, at a 50 percent share | +4.46 (+13.1 percent) | the generator page's hourly file |
| The load's own effect on price | +0.03 at 100 MW; +0.42 at 1,000; +4.21 at 10,000 | the page's prices against `ercot_zone_load_hourly` |
| ERCOT's day-ahead reserves, a load's share | +0.27 to +0.33 | `ercot_as_prices`, `ercot_as_quantities`, `ercot_zone_load_hourly` |
| Prices rising 2 percent a year over 20 years | present value +14.6 percent | the scenarios' own formulas |
| A node rather than the zone, behind a generator's meter | the page's own band: USD -7.97 to +7.39 between the 10th and 90th percentile (note, session 354) | `node_basis_summary`, shown and added to nothing |
| Losses on the load's metered energy | not sized | no loss factor table held: data request |
| ERCOT's administration fee, real-time reserves since 5 December 2025, uplift, securitization charges, taxes, retail margin | not sized | no table held |
| California's load aggregation point against the trading hub | not sized | no load aggregation point price held: data request |

## Findings, largest effect first

| # | Severity | Finding | Effect, default case | Fix | Branch |
|---|---|---|---|---|---|
| 1 | High | "All-in power per GPU-hour" holds market energy and what is typed, nothing else | the figure 0.0691; Oncor's delivery alone +25.9 percent | words | `wip/audit-datacenter-1` |
| 3 | Medium | The load is a price taker at any size to 10,000 MW; the page never says so | +0.42 per MWh at 1,000 MW, +4.21 at 10,000 (rough) | words | `wip/audit-datacenter-3` |
| 4 | Medium | Each month's dollars, never said; flat prices at a money rate in the scenarios | present value +14.6 percent at 2 percent inflation | figure: ruling | `wip/audit-datacenter-4` |
| 5 | Medium | The contract is a block in the load's own hours; a solar PPA costs more | +8.93 per contracted MWh; +4.46 per MWh at 50 percent | words | `wip/audit-datacenter-5` |
| 2 | Medium | All grids' "All-in" leaves out distribution, ancillary services and losses | +0.23 (Oncor's distribution and riders) +0.27 to 0.33 (reserves), losses not sized | words | `wip/audit-datacenter-2` |
| 7 | Low | 1.3 kW rounds the datasheet's 1.275 up; 1.56 is the industry's ratio, not a lab's | GPU-hour +1.9 percent; at 1.09, -30.1 percent | figure: ruling | `wip/audit-datacenter-7` |
| 6 | Low | Carbon is the grid's average; the face never says it is not what the load adds | not sized (no marginal rate held) | words | `wip/audit-datacenter-6` |
| 8 | Low | California is priced at generator trading hubs; a load pays its utility's load aggregation point | not sized (no table) | data request | `wip/audit-datacenter-8` |

The sections of each finding follow as the branches are written.
