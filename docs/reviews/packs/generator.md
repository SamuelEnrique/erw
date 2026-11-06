# Review pack: What a generator earns

- Address: `/cost-of-power/seller`, the second of the three cost-of-power tabs; in review (`site/lib/release.ts`): a visitor sees the in-review page.
- Written by session 264 on 2026-10-14 from the branch `wip/264-generator-pack`, code commit `3f694726` (on `afacb21e`: sessions 257, 258, 260 and 262).
- Replaces the how-it-works note of sessions 249 and 260 (removed from `docs/howitworks/` by session 264), whose content is folded in below: its numbers, its sources table and its demo (the appendix).
- The default case unless a line says otherwise: ERCOT, solar, 100 MW, the hub average (`HB_HUBAVG`), real-time prices, October 2025 to September 2026, the model's snapshot built 2026-10-04 (`site/data/merchant_snapshot.json`), the capture file built 2026-10-13T17:38:04Z (`site/data/seller/capture.json`).
- Read in the internal view on a local build of this branch (port 3264), 14 October 2026.

## Against roadmap item 2 (session 381)

Roadmap item 2 (`docs/roadmap.md`, "Five tools sellable") is done for a tool when it has a method note signed by Samuel, a replication a reader can run, a cross-check table against published figures and a decisions block. Read on 21 October 2026 by session 381 from `wip/381-five-tools` (cut from `main` at `dc4d5ba6`); every exit code below is of a run that day, its output under `runs/chain_oct21/s381/` on the code machine. The checks that read the built site were not run: the local production build stopped twice on Supabase statement timeouts (the home page's required read), and each cell says so. No method note is signed: none of the five has a signature in any file. No page and no default figure was changed by this session. The parts below this section are the pack as written on 14 October and amended since; where a figure here differs, this section is the newer.

| Roadmap item 2 asks | What the tool has | Where | Today | What it lacks |
|---|---|---|---|---|
| A method note signed by Samuel | `generator_earns_algorithm.md` (session 183, "written for sign-off"), with the scenarios (186), CAISO at depth (253), the rulings of 18 October (298) and session 353's tax credits | `docs/methods/generator_earns_algorithm.md`, linked from the page's source line | not signed: no sign-off block, no signature in any file | Samuel's signature, and a block to sign in (the owner's words) |
| A replication a reader can run | The default case's hours (ERCOT solar at `HB_HUBAVG`, real time, per MW, 2018-07 to the model's last hour 2026-10-03), a do-file and its Python mirror, linked from the page | `site/public/seller/erw_2026_generator_hourly.csv` (session 183, 10 October), `erw_2026_generator_replication.do`, `.py` (`page.tsx`, `HOURLY_CSV`) | The mirror on the CSV: exit 0, USD 59.85 per kW over October 2025 to September 2026, a price received of USD 23.27 per MWh, coverage 0.67 times. Against today's page: not read (the local build stopped twice on Supabase statement timeouts, 21 October). The do-file: not run | Samuel's Stata run. The CSV is the model's snapshot of 4 October; the daily page files have not rewritten it since 10 October, so a later snapshot would need a new export |
| A cross-check table against published figures | 21 rows (Lazard, the ATB, EIA, CAISO's market monitor, Berkeley Lab, Potomac Economics), each with its gap and reason; the page's line counts them | `docs/methods/generator_earns_algorithm.md#cross-checks`; part 4 below | `check-cross-checks.mjs`: not run on 21 October (no local build: it stopped twice on Supabase statement timeouts) | Nothing held and missing. Berkeley Lab's terms are an open question of part 9 |
| A decisions block | Scenarios A and B in the shared block, the reader's plant and contract, Resets, the price years since session 352 | `site/app/cost-of-power/seller/SellerScenarios.tsx`, `site/components/decisions/ScenarioBlock.tsx` | `check-decisions-face.mjs`: not run on 21 October (no local build) | Nothing that needs no ruling |

**On a built site (session 422, 21 October 2026).** A build at 15:22 UTC of `wip/422-tool-checks`, which is main with chain 019's branches not yet landed (`wip/461-combined`), served on localhost; outputs in `runs/chain_021/s422/` (git ignores `runs/`). `check-cross-checks.mjs` exit 0, 18 of 18 for the three decision pages (this page's line: 34 published figures); `check-decisions-face.mjs` exit 0, 144 of 144; the mirror, `erw_2026_generator_replication.py`, exit 0, and its headline figures equal the page's default headline to the digit shown: USD 59.85 per kW, a price received of USD 23.27 per MWh, debt coverage 0.67 times.

## 1. What it is for, and for whom

- The question: what a solar plant, a wind plant, a battery or a gas peaker earned selling every MWh at a hub's price, year by year; the price it received against the hub's plain average (the capture price and the capture rate); whether that covers its debt; whether it is worth building, with or without a contract.
- For whom: a lender first ("built for a lender's reading: the bad months, the stress days, and debt service coverage", `docs/methods/cost_of_power.md`, "The seller's side"); since session 186 a developer or an investor too (two scenarios, NPV and IRR to equity); since session 235 the PPA price at which NPV is zero.
- Where: five grids, 39 hubs and zones (ERCOT 14, CAISO 3, NYISO 11, ISO-NE 9, SPP 2). MISO blank (paused while its terms are reviewed); PJM blank (licensed source needed). This pack checks ERCOT and CAISO.
- What it is not: merchant by default; no capacity payment, no ancillary service, no tax credit; a grid's whole fleet at a hub's price, not one site at its node. The method note: "It is not a forecast and not a valuation."
- The default answer in one line: 100 MW of ERCOT solar earned USD 59.85 per kW in the last twelve months, was paid USD 23.27 per MWh against a hub average of 32.17 (a capture rate of 72 percent), covered its debt 0.67 times, and has an NPV of USD -74.16 million at a hurdle rate of 12 percent; the breakeven PPA price is USD 58.36 per MWh over a PPA term of 35 years.
- California's default (SP15, solar): USD 28.45 per kW on 2,057 MWh per MW; 13.86 against 28.53 (a capture rate of 49 percent; 48.6 to one decimal); coverage 0.23; breakeven PPA price USD 73.19.

## 2. The model, step by step

Everything is per 1 MW of nameplate, multiplied by the reader's MW at the end; every result is linear in MW.

1. The address becomes the inputs: grid, hub, asset, size, a battery's MWh, a peaker's heat rate and variable O&M, each bounded (`inputsOf()` in `site/lib/merchant.ts`); the two scenarios' eleven assumptions, each bounded (`parseScenarios()` and `bound()` in `site/lib/seller/finance.ts`); session 264: a typed value outside its bounds is held at the bound and one line under "Your plant" says so (`clampedWords` in `modelOf()`, `site/app/cost-of-power/seller/model.ts`).
2. The price comes in: the hub's real-time price, an hour the mean of its four 15-minute prices and only when all four are held; a hub with no twelve months of real time is priced day-ahead and the page says so (`build_iso()` in `warehouse/derived/merchant_revenue.py`; methods note 3.1, 4.3).
3. The shape comes in (solar, wind): the grid's whole solar or wind generation by hour from EIA-930 over the fuel's installed nameplate that month from EIA-860M, MWh per MW installed: a fleet's shape (`fuel_hours()` and `capacity()` in `warehouse/derived/merchant_revenue.py`).
4. An hour becomes dollars: output per MW times the hour's price; a plant sells in every hour, also below zero; nothing is curtailed (`build_iso()` in `warehouse/derived/merchant_revenue.py`).
5. A battery's day: each local day whose every hour holds a price, the best schedule solved exactly with the day's prices known; round trip 86 percent, from empty, at most one full cycle; energy only, an upper bound (`battery_day()` in `warehouse/derived/merchant_revenue.py`).
6. A peaker's hour: runs where the price is strictly above Henry Hub times the heat rate plus variable O&M, and earns the difference; no start cost, no minimum run (`peakerOver()` in `site/lib/merchant.ts`).
7. Hours become a month: revenue, energy, capture price (sales over energy), flat price and rate; a month is held at 90 percent of its hours (a battery: days) (`months()` in `site/lib/merchant.ts`).
8. Months become the spans: the last twelve months (the newest held month and the eleven before it, all held), the last three full years, every full year held (`lastTwelve()`, `spanOf()` and `spans()` in `site/lib/seller2.ts`): 59.85, 102.24 and 130.80 USD per kW.
9. The price received: a second builder weighs each hour's price by the fleet's generation, `sum(price x generation) / sum(generation)`, against `sum(price) / hours` over the same hours; a month counts at 95 percent of its hours (`twelve()` in `site/lib/capture.ts` on `warehouse/derived/capture_price.py`): 23.27 against 32.17 over 8,736 hours and 80,832,584 MWh.
10. The capture rate (session 264 beside every capture price): the price received over the flat average, in whole percent, from the same rows (`stat()` in `site/lib/capture.ts`, key `cap|<grid>|<hub>|<market>|<fuel>|l12|rate`): 72.
11. Another hub: the model solved again with that hub's own price and the same fleet shape (`hubIso()` and `withHub()` in `site/lib/sellerhubs.ts`, on `warehouse/derived/merchant_hubs.py`).
12. The capture chart and table: every hub and zone of the grid, the last twelve months and each year (`capView` in `modelOf()`, `site/app/cost-of-power/seller/model.ts`).
13. Debt: `capex x share x r / (1 - (1 + r)^-n)` per kW, `n = min(term, life)` (`debtService()`, `crf()`, `debtYears()` in `site/lib/seller/finance.ts`): 1,375 x 0.60 x 0.0858033 = 70.79 per kW, USD 7,078,769 for 100 MW (`debtUsd()`).
14. Coverage: `(contract + (1 - cshare) x revenue - fom) / debt` (`coverage()` in `site/lib/seller/finance.ts`): (59.85 - 12.50) / 70.79 = 0.67 times.
15. The flows to equity: year 0 `-capex x (1 - share)`; year t the income less fixed O&M less the debt payment while the debt lasts; the income is the contract plus the uncontracted share of the market for the PPA term, then the whole plant in the market (`flows()`, `incomeInYear()`, `contractYears()` in `site/lib/seller/finance.ts`; session 264: the PPA term, where it was the debt's years).
16. NPV and IRR: discounted at the hurdle rate; IRR by bisection from -99 to 1,000 percent, "none" when NPV has one sign at both ends (`npv()`, `irr()` in `site/lib/seller/finance.ts`): USD -74.16 million; IRR none.
17. Two contract prices: coverage 1.25 at `(1.25 x debt + fom) / E` (`contractPrice()`): 39.14; NPV zero at `-NPV(price 0) / sum over the PPA term of E / (1 + h)^t` (`breakevenPpa()`): 58.36 (a battery and a peaker: a toll, `breakevenToll()`).
18. "Make B a PPA": B's share 100 and its price B's breakeven rounded up to the cent (`asPpa()` in `site/lib/seller/finance.ts`; the button in `SellerScenarios()`, `site/app/cost-of-power/seller/SellerScenarios.tsx`).
19. What matters most: each assumption moved down and up by its step, NPV again, sorted by the larger move; the contract's three rows only when a scenario holds a contract (`sensitivity()` in `site/lib/seller/finance.ts`).
20. The bad months and the stress days: the median, the 10th-percentile and the worst three months (real months); ERCOT's Uri, Elliott and 2023 heat against a normal week (`summary()`, `stress()` in `site/lib/merchant.ts`); in the CSV downloads since session 212, the worst month a row of the results.
21. A battery beside it (solar and wind, ERCOT and CAISO): plant and battery behind one interconnection, solved a day at a time against the main hub's day-ahead prices (`warehouse/derived/seller_hybrid.py`; `profileResult()` in `site/lib/sellerhybrid.ts` for the reader's own year).
22. The downloads: months and the other tables, the page's own arithmetic (`GET()` in `site/app/cost-of-power/seller/months.csv/route.ts` and `tables.csv/route.ts`); session 264: offered where the grid's prices may be redistributed (`licenseHeldGrid()` in `site/lib/license.ts`).

Not read by the model: `ercot_rtm_price_adders` (session 244). ERCOT's scarcity adders are inside the hub price the model reads, so scarcity revenue is counted but not shown apart.

## 3. Every assumption

"Your plant" is the panel at the left; the scenario assumptions are the panel under "Is it worth building?" (address `a` or `b`, then the letter). The 12 October rulings: `docs/reviews/erw-review-2026-10-12.md` and the session reports after it.

| Assumption | Default | Source | Ruling of 12 October |
|---|---|---|---|
| Grid | ERCOT | ERW's choice: the only grid held from July 2018; the other four from September 2024 | none |
| Hub or zone | the grid's main hub: hub average, SP15, New York City zone, Internal hub, North hub | The price board's main hubs, `docs/methods/cost_of_power.md` | none |
| Asset | solar | ERW's choice | none |
| Size, MW (`mw`) | 100; a battery 100 MW / 400 MWh; bounds 1 to 5,000 (session 264: a value outside is held at the bound, with a line) | `DEFAULT_SIZE`, `site/lib/merchant.ts`; Lazard's storage cases are 100 MW | none |
| Market | real time; day-ahead where a hub holds no twelve months of real time | ERW's rule, methods note 4.3 and section 5 | none |
| An hour's price | the mean of four 15-minute prices, only when all four are held | ERW's rule, methods note 3.1 | none |
| First month | July 2018 (ERCOT); September 2024 (the other four) | EIA-930's generation by fuel begins 2018-07-01 (`SHAPE_START`, `warehouse/derived/merchant_revenue.py`) | none |
| Solar and wind output | the grid's whole fleet by hour over installed nameplate that month | EIA-930 (`Adjusted SUN Gen`, `Adjusted WND Gen`) and EIA-860M | none |
| Output above nameplate or below zero | kept as EIA reports it (ERCOT: 1,428 solar hours above nameplate; CAISO: 4,197 solar hours below zero) | ERW's choice: nothing trimmed; counted in `tables.csv` | none |
| California's hours | read one hour earlier from 2023-11-01 to 2025-12-02 | `docs/methods/eia930_caiso_break.md` | none |
| Curtailment, negative prices | none: the plant sells every hour | By construction, methods note 3.2 | none |
| A month is held | 90 percent of its hours (a battery: of its days) | ERW's rule (`NEAR = 0.9`) | none |
| A month counts for the price received | 95 percent of its hours | ERW's rule (`NEAR = 0.95`, `warehouse/derived/capture_price.py`) | none |
| Battery round trip | 86 percent | Lazard LCOS v10.0, the low end of 92 to 86 percent | none |
| Battery cycles and start | at most one full cycle a day, from empty each day | The battery page's rule | the battery page approved (12 October night) |
| Battery foresight | the day's prices all known | By construction: an upper bound | none |
| Battery duration priced | 4 hours; 2 when MWh over MW is 3 or less | Lazard prices two durations (`durationOf`) | none |
| Peaker heat rate (`hr`) | 10.725 MMBtu per MWh; bounds 6 to 16 | Lazard, gas peaking new build, midpoint of 10,275 to 11,175 Btu per kWh | none |
| Peaker variable O&M (`vom`) | USD 4.25 per MWh; bounds 0 to 50 | Lazard, midpoint of 3.50 to 5.00 | none |
| Gas price | Henry Hub spot of the local day; no basis | EIA, `eia_fuel_spot_prices` | none |
| Peaker carbon cost | California's allowance on CAISO (the latest current auction's settlement price times 53.06 kg CO2 per MMBtu, USD per MMBtu added to the fuel); none elsewhere | The owner's ruling 1a of 18 October 2026 (session 298); CARB's auction results and EPA's factor | 1a |
| Battery beside the plant (`bmw`, `dur`, `strat`) | the plant's MW, 4 hours, perfect foresight | ERW's choice | none |
| The pair's limit and prices | the plant's MW or its highest hour; the main hub's day-ahead price | `docs/methods/cost_of_power.md`, "Session 162" | none |
| 1. Capital cost (`c`) | solar 1,375; wind 2,100; battery 610 (2 h), 1,110 (4 h); peaker 1,300 USD per kW; 0 to 10,000 | Lazard, Levelized Cost of Energy+, June 2025, midpoints | none |
| 2. Debt share (`s`) | 60 percent; 0 to 100 | Lazard: "60% debt at an 8% interest rate" | the battery page's 20 is its own (session 208); this page stays 60 |
| 3. Interest rate (`r`) | 8 percent; 0 to 30 | The same | none |
| 4. Term of the debt (`t`) | the asset's life: 35, 30, 20, 30 years; 1 to 40 | Lazard: "Economic life sets debt amortization schedule" | none |
| 5. Fixed O&M (`f`) | 12.5; 32.25; 11.2 and 22; 13.5 USD per kW a year; 0 to 500 | Lazard, midpoints | none |
| 6. Degradation (`d`) | 0 (solar, wind, peaker); 2.6 percent (battery); 0 to 20 | Battery: Lazard LCOS v10.0; the others: no cited rate | the ruling of 11 October named the battery only |
| 7. Project life (`l`) | 35; 30; 20; 30 years; 1 to 40 | Lazard's life of each asset | none |
| 8. Hurdle rate (`h`) | 12 percent; 0 to 40 | Lazard: "40% equity at a 12% cost" | "the owner's ruling of 12 October 2026" (session 208): 12, Lazard's cost of equity; it was 9.6 |
| 9. Contract share (`n`) | 0: fully merchant; 0 to 100 | No contract | the chain prompt of 12 October (session 212): the contract becomes scenario assumptions, 0 by default |
| 10. Contract price (`p`) | 0; 0 to 1,000 | The reader's own term: no published price is held | the same |
| 11. PPA term, years (`y`, session 264) | the asset's life: 35, 30, 20, 30; 1 to 40, whole; cut to the life | Lazard's economic life, the debt's own default term: no published PPA term is held; at the default every figure is what it was (the reversible choice) | none: the owner's list of 14 October |
| Coverage target | 1.25 times (`TARGET`) | ERW's choice: no source cited | none |
| Revenue in every future year | the last twelve months repeated, less degradation | ERW's choice: "An assumption, not a forecast" (methods note 11.3) | none |
| Breakeven PPA share | the scenario's own contract share, or 100 when it holds none (`ppaShare`) | Session 235 | "the results show the breakeven PPA price" (the owner's task of 12 October) |
| Sensitivity steps | capital cost 100; debt share 10 points; interest 1; term 5 years; fixed O&M 5; degradation 1; life 5; hurdle 1; contract share 10; price USD 1; PPA term 5 years | ERW's choice (`swing` in `SPECS`) | none |
| Tax, credit, inflation, repowering, residual value | none | By construction, methods note 11.3 and 11.6 | none |

- Two files disagreed (the old note): the methods note's table in 11.1 gave the hurdle rate as 9.6; the code says 12 (session 208). The PPA term (session 264) is now in the code and this pack; the methods note's 11.1 and 11.3 gain a line (session 264).
- The PPA term's choice: the asset's life, because no published term is held in the repository, and because the life is what every contract of this page ran for until today (the debt's default term), so no default number moves. Berkeley Lab's PPA samples report contract terms; none is held here (part 9, question 6).

## 4. The cross-checks

"Gap" is ours less theirs. None is a real plant's revenue. Ours is the page's own figure; theirs as the methods note quotes it ("Cross-checks", read 11 October 2026; section 12.5, read 13 October 2026). 21 rows below are published figures; the page counts 20.

| What is compared | Ours | Theirs | Gap | Reason |
|---|---|---|---|---|
| ERCOT solar, contract price for coverage of 1.25 | USD 39.14 per MWh | Lazard LCOE, utility solar, unsubsidized: USD 38 to 78 | inside, at the low end | Ours covers debt 1.25 times and fixed O&M only; Lazard's returns 12 percent on equity and pays taxes |
| ERCOT wind, the same | USD 56.85 per MWh | Lazard LCOE, onshore wind: USD 37 to 86 | inside | The same, over 3,028 MWh a year per MW |
| Gas peaker, toll for coverage of 1.25 | USD 8.34 per kW-month | Lazard LCOE, gas peaking: USD 149 to 251 per MWh | not stated | A fixed charge against a cost per MWh |
| Capital cost, solar | USD 1,375 per kW | ATB 2025: 1,490 per kW AC (2024) | -115, 7.7 percent | Lazard's midpoint against one modeled tracking plant |
| Capital cost, wind | USD 2,100 per kW | ATB 2025: 1,968 (2023 market average) | +132, 6.7 percent | A 2025 midpoint against a 2023 average |
| Fixed O&M, solar | USD 12.50 per kW a year | ATB 2025: 24.66 | -12.16 | The ATB adds land, property and administration |
| Fixed O&M, wind | USD 32.25 per kW a year | ATB 2025: 43 | -10.75 | The ATB counts every operating cost as fixed |
| Degradation, solar | none | ATB 2025: 0.7 percent a year | -0.7 | No cited default for solar; part 9 |
| SP15 day-ahead peak block, Jan to Sep 2026 (EIA) | USD 24.04 (NP15 34.35) | ICE index in EIA's file: 23.97 (NP15 34.58) | +0.07 (NP15 -0.23) | A traded expectation against the cleared price |
| New England hub day-ahead peak block, same months (EIA) | USD 77.72 | ICE index: 78.55 | -0.83 | The same; January -7.41 |
| CAISO peaker at NP15, 2025, margin over fuel, USD per kW (market monitor) | 41.47, 42.0 percent of hours | 3.52 net, 3.43 percent | +37.95 | No carbon cost in the page's rule: with the allowance 10.11 |
| The same, run their way as far as the model can | 16.32 | 3.52 | +12.80 | Start costs, minimum run and half load, a 10 percent bid adder |
| CAISO peaker at SP15, 2025 (market monitor) | 30.05, 34.0 percent | 0.78 net, 1.32 percent | +29.27 | The same; with the allowance 6.95 |
| The same, run their way | 11.27 | 0.78 | +10.49 | The same |
| Henry Hub, 2025 average (market monitor) | 3.54 USD per MMBtu | 3.54 | -0.001 | One series by two routes |
| CAISO wind, 2025, flat average (LBNL wind 2026) | 34.23, mean of SP15 and NP15 | 34.21 | +0.02 | Two hubs against every plant's node |
| CAISO wind, 2025, price the fleet's shape received (LBNL wind) | 32.91, mean of SP15 30.29 and NP15 35.53 | 32.97 at all plants; 30.82 after curtailment | -0.06 | The profile at a hub; not the plants' nodes or curtailment (a further 2.15) |
| CAISO wind, 2025, capture rate (LBNL wind) | 97.1 at SP15, 95.3 at NP15 | 96.4 for the profile alone | -0.1 points | Their value factor 0.9551 adds capacity value |
| CAISO solar, breakeven PPA price (LBNL utility-scale solar 2025) | USD 72.58 on 2,075 MWh per MW (2025) | LevelTen CAISO solar index 2024: 47.06; LBNL's West sample of 2024: 27.45 | +25.52 | No tax credit, 12 percent to equity, a whole fleet's output |
| CAISO wind, breakeven PPA price (LBNL wind) | USD 79.50 on 3,125 MWh per MW (2025) | LevelTen CAISO wind index 2025: 78.2 | +1.30 | The same |
| CAISO solar, capture rate (LBNL solar) | 45.8 at SP15, 71.7 at NP15 (2025) | 25.1 percent (2024, energy only) | not computed: no year held by both | ERW's CAISO prices begin September 2024 |
| Not held | ERCOT's market monitor (Potomac Economics) on a solar or wind plant's revenue | not held in the repository | no number | Part 9, question 6 |
| Not compared | any ERCOT hub price | EIA's 2026 file holds no ERCOT hub | no number | No public index for the default hub |

Internal checks (not published figures): the default case rebuilt from one hourly CSV, every headline to the cent (part 8; session 264 adds the capture rate, NPV, the two contract prices); 99 ERCOT months by a second builder (methods note 5.1); the flat price of 3,708 hub-months, model against capture file, within USD 0.0001; the finance library against the battery page's, 400 seeded cases, 0 gap (`site/scripts/test-seller-finance.mjs`); one solar month by hand, ERCOT 2025-07 (`tests/test_session51.py`); the pair's solver against scipy's HiGHS, one part in ten billion (`site/scripts/test-hybrid.mjs`); session 264, `check-values` on the four seller views, 234 of 234 (179 before: the spans, the headline and the summary sentence now carry keys).

## 5. The edge cases tested

Tested tonight (14 October 2026) on a local build of this branch at port 3264, in the internal view (`runs/session264/edge.mjs`, its output `runs/session264/edge.out`); the capacity factors through the reader's own year with the browser's own functions on the page's price file (`runs/session264/profile_edges.mjs`).

| Case | What was typed (the address) | What the page does |
|---|---|---|
| A plant type with no data in a grid | `/cost-of-power/seller?iso=nyiso&asset=solar` | One line: "No month of solar is held for NYISO, so no number is shown: EIA-930 itemizes no solar generation for New York." Every figure "not held yet" with its reason on hover; the results table "not held"; no chart; no number invented |
| A plant type with data in CAISO | `/cost-of-power/seller?iso=caiso&asset=wind` | SP15: USD 64.04 per kW; 25.88 against 28.53, "a capture rate of 91 percent" in the sentence and the headline; coverage 0.28 |
| Size 0 MW | `/cost-of-power/seller?mw=0` | Held at 1 MW. The new line under the panel: "Size, MW: 0 is below the bound of 1, so the page uses 1." Per-kW figures unchanged; dollars for 1 MW (worst month USD 1,393) |
| Size tiny | `/cost-of-power/seller?mw=0.001` | "Size, MW: 0.001 is below the bound of 1, so the page uses 1." |
| Size above the bound | `/cost-of-power/seller?mw=9999` | "Size, MW: 9,999 is above the bound of 5,000, so the page uses 5,000." Debt payments USD 353.94 million a year; coverage 0.67 (linear in MW) |
| Size not a number | `/cost-of-power/seller?mw=abc` | "Size, MW: "abc" is not a number, so the page uses 100." |
| Peaker inputs outside | `/cost-of-power/seller?asset=peaker&hr=3&vom=80` | Two clauses in the line: heat rate held at 6, variable O&M at 50; margin over fuel USD 25.57 per kW |
| Battery energy outside | `/cost-of-power/seller?asset=battery&mw=100&mwh=10000` | "Energy, MWh: 10,000 is above the bound of 800, so the page uses 800." |
| Scenario values outside | `/cost-of-power/seller?ac=99999&ay=99` | "Scenario A, capital cost: 99,999 is above the bound of 10,000 ... Scenario A, PPA term: 99 is above the bound of 40, so the scenario uses 40." Column A reads "capex 10,000 USD/kW, PPA 40 years"; coverage 0.09 |
| PPA term below | `/cost-of-power/seller?by=0&v=b` | "Scenario B, PPA term: 0 is below the bound of 1, so the scenario uses 1." Column B "PPA 1 year" |
| Capacity factor 0 | the reader's own year, 8,760 zeros, ERCOT 2025 | Read; energy 0; revenue USD 0; capture price and rate "none" (no division by zero) |
| Capacity factor tiny | 8,760 values of 0.001 MW | Read; 9 MWh; revenue USD 293; capture 33.50 against flat 33.50, rate 100.0 |
| Capacity factor 100 percent | 8,760 values of 100 MW | Read; 876,000 MWh; USD 29,343,506; rate 100.0 |
| Capacity factor above nameplate | 8,760 values of 150 MW for a 100 MW plant | Read as typed: the box takes no nameplate, so 150 is not "above" anything it knows; 1,314,000 MWh; the pair's limit is the profile's highest hour. Not clamped (decision 4 of the report) |
| A value below zero, a short year | one hour -1; 8,759 values | Refused, with the line and the reason: "Line 6 is below zero (-1)"; "8,759 values were read and 2025 has 8,760 hours" |
| PPA price above the capture price | `/cost-of-power/seller?bn=100&bp=50&v=b` | B (all the energy at USD 50, above the capture price of 23.27, below the breakeven of 58.36): coverage 1.65 times; NPV USD -17.63 million (-176.31 per kW); IRR 7.7 percent; the breakeven row still reads 58.36, "the scenario's own price is USD 50". A unchanged: 0.67, USD -74.16 million |
| PPA price below the capture price | `/cost-of-power/seller?bn=100&bp=15&v=b` | B (USD 15, below the capture price): coverage 0.37 times, lower than merchant (0.67); NPV USD -91.45 million (-914.54 per kW); IRR none; the breakeven row 58.36, "the scenario's own price is USD 15". The page states the numbers and no verdict |
| PPA at the breakeven, shorter term | `/cost-of-power/seller?bn=100&bp=58.36&by=20&v=b` | B (the 35-year breakeven, 58.36, over a 20-year PPA term): coverage 1.95 times; NPV USD -6.4 million (-64.03 per kW): after 20 years the plant is merchant again; B's breakeven row reads USD 61.68 "for a PPA term of 20 years". Column B's head "PPA 20 years" |
| CAISO PPA above the capture price | `/cost-of-power/seller?iso=caiso&bn=100&bp=50&v=b` | SP15 (capture 13.86): A NPV USD -99.83 million, coverage 0.23; B at USD 50: coverage 1.28, NPV USD -39 million (-389.97 per kW), IRR 1.3 percent; breakeven 73.19 in both columns |
| The downloads | `/cost-of-power/seller/months.csv`, `tables.csv`, `months.csv?iso=caiso` | HTTP 200 (107, 4,027 and 33 lines); ERCOT and CAISO prices "may be public" (`docs/licenses.md`, rows 2 and 3); an ISO-NE or NYISO grid answers "license needed" from 21 October (`tests/test_session264.py` holds the day) |

## 6. What the model cannot see, ranked

Ranked by the held number where there is one; "no number held" where the repository holds none.

1. Future prices: the finance repeats one window of price years for the plant's life. Since session 352 (20 October 2026) the reader chooses it beside "Your plant" ("Price years", read from `price_years_by_window`, at the main hub): the last twelve months (the default, 59.85 per kW for ERCOT solar), any calendar year held (59.46 in 2024 to 217.53 in 2021), the three-year average (102.24), the seven-year (130.80), or every full year held. Scenario A and B, the results and the sensitivity follow it, so NPV at another year's revenue is now a number; a line under the results gives the highest and lowest whole year. The windows with a stress event taken out are held in the table but not offered (they hold no energy, which the contract rows read). No forecast is held.
2. PPA and hedge terms: merchant by default; received 23.27, needs 39.14 for coverage of 1.25 and 58.36 for NPV zero. A contract is a share at a flat price for the PPA term (session 264; the debt's years until then): no negative-price clause. Since session 353 (20 October 2026) the contract has a shape, as generated (the default) or a flat block settled at the hub's average (the default solar case contracted whole at 58.36: NPV about zero as generated, USD -21.27 million as a block; the block's breakeven 68.45). What PPAs sign at in ERCOT: no number held (CAISO: LevelTen 47.06 solar, 78.2 wind).
3. Tax credits and taxes: since session 353 (20 October 2026) two inputs in Financing, the investment credit (a percent of capital, year 1) and the production credit (USD per MWh, ten years), 0 by default and not counted in coverage; whether a project qualifies, and at what rate, is the reader's: no number held. At 30 percent ITC the default solar NPV is about USD -39.83 million against -76.66. Lazard's range in part 4 is unsubsidized.
4. Scarcity and availability: Uri's 18 days earned USD 12,382,220 for 100 MW against 5,985,226 for the whole last twelve months; the model assumes the plant ran through the storm. ERCOT's reserve adder averaged USD 7.05 per MWh in 2021 and 0.07 in 2025 to 4 December.
5. Basis between hub and node. Session 358 (`node_basis_daily`, `node_basis_summary`): ERCOT's day-ahead price at every generator's settlement point over 1 October 2025 to 30 September 2026 (335 days), against `HB_HUBAVG`, the point's mean basis in USD per MWh: solar (125 points) median 0.09, 10th percentile -5.22, 90th 5.40; wind (165) median -3.79, -7.88 to 4.06; gas (195) median 1.36. Real time, 20 days (28 September to 18 October 2026): solar median -0.83, wind -2.01. Since session 353 (20 October 2026) the scenarios can be priced at a node (the 10th, median or 90th percentile of the class's day-ahead basis, month by month, on the plant's energy): solar 100 MW, USD -15.83 per kW at the 10th, 0.17 at the median, 14.69 at the 90th (NPV -88.94, -76.53, -65.27 million); the figures above the scenarios stay at the hub. Hub to hub: ERCOT solar 47.51 at the West hub, 72.48 in the Houston zone against 59.85; coverage 0.49 to 0.85.
6. Capital cost and fixed O&M off the midpoint: USD 100 per kW moves NPV by USD 8.21 million; USD 5 of fixed O&M by 4.09 million; the ATB's solar fixed O&M is 12.16 higher.
7. Ancillary services and capacity: none counted. A battery: 58.53 per kW energy alone against 81.40 on What a battery earns. NYISO and ISO-NE capacity: no number held.
8. Degradation: solar none; ATB 0.7 percent; one point a year moves NPV by USD 3.51 million.
9. A fleet, not a site: site against fleet, no number held; EIA-860M lists some plants late (1,428 ERCOT solar hours above 1.0).
10. CAISO's peaker carbon allowance: SP15 2025 30.05 per kW by the page's rule, 6.95 with the allowance, 0.78 by the market monitor; every CAISO peaker figure is too high by that; adding the allowance waits for a ruling (part 9, question 1). Given on 18 October 2026 as 1a and built in session 298: the allowance is in the run rule now (the last twelve months' margin at SP15 from USD 43.19 to 19.66 per kW).
11. California's wind since May 2026: 3,650 MW of New Mexico wind (SunZia) in the denominator; the last twelve months hold 2,477 MWh per MW against 3,125 in 2025.
12. Curtailment and negative prices: the fleet's curtailment is out of EIA's generation; a site's is not; no number held.
13. Real time against day-ahead: USD 6,328,531 day-ahead (364 days) against 5,985,226 real time for 100 MW.
14. Perfect foresight (battery) and perfect hourly information (peaker): upper bounds; the battery page's day-ahead schedule gives 73.00 against 81.40.
15. The peaker's start costs and delivered gas: no number held for ERCOT; CAISO's market monitor's unit costs USD 65.7 to 71.0 per MWh run against ours 50.6 to 50.8.
16. Age of the files: the snapshot built by hand 2026-10-04, newest month September 2026; no schedule rebuilds it.

## 7. The ten hardest questions

### 1. Your NPV is USD -74.16 million: is solar in Texas not worth building?
No. It says 100 MW selling every MWh at the hub average, no contract, no tax credit, the last twelve months repeated for 35 years, does not return 12 percent to equity. Revenue less fixed O&M 59.85 - 12.50 per kW against debt payments of 70.79: coverage 0.67. IRR "none". The method note: the block "does not say which to choose".

### 2. Is this my plant at my node?
No. ERCOT's whole solar fleet by the hour, scaled to 100 MW, paid the hub's price. Basis at a node: the warehouse holds no node price for a plant. "Your plant's own year" takes the reader's hourly output, still priced at the main hub, day-ahead.

### 3. Why the last twelve months? It is your worst case.
It is the newest year, not a chosen one: 59.85 per kW. The page shows 102.24 (2023 to 2025) and 130.80 (2019 to 2025) beside it. 2024 was 59.46, 2025 63.54; 2021 to 2023 were 217.53, 197.43 and 183.72. The finance reads only the last twelve months; NPV on an average: no number held.

### 4. Where is the tax credit?
Nowhere: "no tax, no tax credit, no repowering, no residual value, no inflation". Its size: not known here; it would need the credit's value and eligibility as assumptions.

### 5. What PPA price does it need, for how long, and what are PPAs signing at?
USD 58.36 per MWh for NPV zero on the whole plant over the PPA term of 35 years (session 264: the term is now the reader's, the eleventh assumption). 39.14 keeps coverage at 1.25. The market paid 23.27 (a capture rate of 72 percent). A 20-year PPA at 58.36 leaves NPV at USD -6.4 million; the 20-year breakeven is 61.68 (part 5). ERCOT PPA prices: none held; CAISO: LevelTen 47.06 (solar 2024), 78.2 (wind 2025).

### 6. How much of the good years was Uri and scarcity, and will it come back?
2021 earned 217.53 per kW; Uri's 18 days alone USD 12,382,220 for 100 MW, best day USD 4,060,021 (2021-02-17). The capture rate that year: 55 percent. Hours with a reserve adder of at least USD 100: 70 (2021), 103, 18, 4, 1 (2025). The model cannot split a year into scarcity and the rest; no forecast.

### 7. What about curtailment and negative prices?
The fleet's curtailed energy is already missing from EIA's generation. A site's own curtailment is not modeled; the plant sells below zero. Size for a site: not known. The page links to the curtailment page's free-energy section for the hub.

### 8. Where are capacity and ancillary revenue?
Not counted. ERCOT has no capacity payment. NYISO and ISO-NE do, left out: no number held. A battery: 58.53 per kW energy alone here against 81.40 on What a battery earns.

### 9. A battery with perfect foresight: is that honest?
Labeled an upper bound. The battery page sets its foresight figure of USD 148 per kW in 2024 beside a published fleet average of 55 (Modo Energy). Here the battery is energy only at 60 percent debt; its toll for coverage of 1.25 is USD 8.90 per kW-month.

### 10. Who has checked this, and how old is it?
21 published figures in part 4 (the page counts 20); the default case rebuilt from one hourly CSV to the cent, now with NPV and the breakeven PPA price (part 8); 234 values recomputed by `check-values` tonight. No ERCOT hub price and no real plant's settlement is compared. The Stata do-file has never been run (no Stata on the machine). The snapshot is from 2026-10-04, built by hand.

## 8. What Samuel's Stata run must reproduce

The do-file and its Python mirror are at the page's defaults (session 264 checked and added the capture rate, the energy, the contract price, NPV and the breakeven PPA price, mirroring `site/lib/seller/finance.ts`). The Python mirror, run tonight (exit 0), prints every value below; the page shows the same.

| Name | Value the page shows | The do-file's display line |
|---|---|---|
| Revenue, last twelve months, USD per kW | 59.85 | `revenue, last twelve months, USD per kW:` |
| Long-run average, 2023 to 2025 | 102.24 | `long-run average of the last three full years, USD per kW a year:` |
| Long-run average, 2019 to 2025 | 130.80 | `long-run average of every full year held, USD per kW a year:` |
| Hours of the capture price | 8,736 | `hours used for the capture price:` |
| Price received, USD per MWh | 23.27 | `price received, weighted by generation, USD per MWh:` |
| Flat average, USD per MWh | 32.17 | `flat average over the same hours, USD per MWh:` |
| Difference | -8.90 and -27.7 percent | `difference, USD per MWh:` and `difference, percent of the flat average:` |
| Capture rate, percent | 72 | `capture rate, percent of the flat average:` |
| Annual debt payments, USD | 7,078,769 (7.08 million) | `annual debt payments, USD:` |
| Debt coverage, times | 0.67 | `debt coverage, last twelve months, times:` |
| Energy sold, MWh per MW | 2,580 | `energy sold, last twelve months, MWh per MW:` |
| Contract price for coverage of 1.25 | 39.14 | `contract price at which coverage reaches 1.25 times, USD per MWh:` |
| NPV at 12 percent, USD million | -74.16 | `NPV at the hurdle rate, USD million for 100 MW:` |
| Breakeven PPA price, 35 years | 58.36 | `breakeven PPA price, the whole of the energy for the PPA term, USD per MWh:` |
| Months held | 99, 2018-07 to 2026-09 | `months held:` |
| The worst month | 2024-02, USD 139,298.97 (the page: 139,299) | `worst month 1:` |

The rest of the do-file's lines (the trailing-twelve-month windows, the median and 10th-percentile months, the worst three) are in the download and are reproduced by the same run: 0.67 at 2026-09; 88 windows; lowest 0.65; 33 under 1.0; 36 under 1.25; 62 and 71 months under 1.0 and 1.25; median 2018-09 USD 550,484.85; 10th percentile 2020-12 USD 240,213.49.

```
cd "<the folder holding the three files, downloaded from the page's source line>"
do erw_2026_generator_replication.do

* the same lines without Stata:
python erw_2026_generator_replication.py erw_2026_generator_hourly.csv
```

## 9. Questions only Samuel can answer

1. The CAISO peaker's carbon cost (session 253 question 1; session 257 question 1). (a) Add California's allowance to the run rule for CAISO: SP15 2025 goes from USD 30.05 to 6.95 per kW, every CAISO peaker figure falls; it needs `carb_auction_allowance_prices`, license internal. (b) Leave the rule and say on the page that no carbon cost is counted. (c) Leave it as it is, in the methods note only (today).
2. The SunZia sentence beside CAISO's wind (253 question 2; 257 question 2). (a) A sentence on the page that 3,650 MW of New Mexico wind entered the denominator in May 2026. (b) Hold SunZia out of the denominator: the last twelve months' 2,477 MWh per MW moves toward 2025's 3,125. (c) First check that EIA-930's CAISO wind counts its output; nothing changes until then.
3. Berkeley Lab's terms (253 question 5; 257 question 6). (a) Quoting with the source is enough: no change. (b) Read and record the terms page in `docs/licenses.md` as for the other publishers before the figures stay counted. (c) Drop LBNL's six rows from the count (20 becomes 14).
4. The stale check scripts (257 question 8): session 264 moved `check-seller.mjs` and `check-seller-face.mjs` to `site/scripts/_retired/` with a README, and the page's numbers are covered by `check-values` (234 keys). (a) Keep it so. (b) Rewrite a face check at 1280 and 390 px for the three-question layout. (c) Delete the retired files after a month. A third, `check-seller-deeper.mjs`, also describes the page before session 212 (session 235's report, item 3): tonight it exits 1, its battery-beside rows NaN (that section is in the CSV now) and a crash at its line 120 before the profile box. (d) Retire it the same way; (e) rewrite it for the profile box alone.
5. The PPA term's default (session 264). (a) The asset's life, the debt's own default (today: no number moves). (b) a published contract length once one is read and held (Berkeley Lab's PPA samples are a candidate; none is held): a shorter term raises the breakeven price (part 5). (c) Tie it to the debt's term (as before session 264): a shared address must then carry both.
6. A published ERCOT figure: the market monitor (Potomac Economics, State of the Market) or Berkeley Lab's ERCOT PPA index is not held. (a) Read one and add a row to the cross-checks. (b) Leave ERCOT compared with Lazard and the ATB only (today).
7. Solar degradation (the old note's open row): (a) take the ATB's 0.7 percent a year as the default (one point a year moves NPV by USD 3.51 million; 0.7 was not computed); (b) keep none (today); (c) a line in the field's source only.
8. The capture figures of a "license needed" grid: from 21 October the model's numbers (`mr|` keys) and the downloads of ISO-NE and NYISO show "license needed", but the capture table's figures (`cap|` keys) are not held by `components/Num.tsx`, which knows no `cap` table. (a) Hold them too (a licensing change: not made unattended). (b) Leave them, as derived figures. (c) Hide the two grids from the page's grid list from that day.
9. CAISO's stress days and history (253 questions 3 and 4; 257 question 3): (a) the data machine writes session 246's notice days into the snapshot and pulls CAISO before September 2024; (b) leave ERCOT's only.

## Appendix: the five-minute demo

Written from the page's code and checked against the local build of session 264. Open the internal view first: `https://erw-flame.vercel.app/internal/open`, paste the token, press "Open the internal view". Then `/cost-of-power/seller`.

Say first: this is what Texas's solar fleet was paid, hour by hour, at the hub's real price; then what that does to a lender's coverage and an owner's return.

- Minute 0 to 1, what did it earn? Your plant: ERCOT, Hub average, Solar, 100. The sentence: "... USD 59.85 per kW ... USD 102.24 ... USD 130.80. At the hub average the price it received ... USD 23.27 per MWh, USD 8.90 (27.7 percent) below the flat average of USD 32.17: a capture rate of 72 percent." The three headline numbers: 59.85 USD/kW; 23.27 USD/MWh with "a capture rate of 72 percent"; 0.67 times on USD 7.08 million.
- Minute 1 to 2, the years and the price received: the chart Revenue by year (131.46, 62.44, 217.53, 197.43, 183.72, 59.46, 63.54 for 2019 to 2025; 2018 and 2026 hatched). The table: revenue 59.85, 102.24, 130.80; energy 2,580, 2,600, 2,422; capture rate 72, 110, 98. The capture chart: 177, 130, 55, 131, 146, 85, 76 for 2019 to 2025, 73 for 2026, 72 for the last twelve months. The hub table: West hub 18.47 against 30.63, 60 percent; Houston hub 27.26 against 32.88, 83 percent.
- Minute 2 to 3, another hub: click West hub; revenue 47.51, coverage 0.49, price received 18.47. Click Hub average to go back.
- Minute 3 to 4, is it worth building? Scenario A, eleven fields (session 264: the PPA term last). The results: worst month USD 139,299 (February 2024; coverage 0.06); NPV USD -74.16 million; IRR none; 39.14; 58.36 "on 100 percent of the energy for a PPA term of 35 years". Press "Make B a PPA": B's share 100, price 58.36, NPV zero or just above. Type 20 in B's PPA term: B's NPV falls to USD -6.4 million and its breakeven rises to 61.68.
- Minute 4 to 5, what matters most: the chart for scenario A, eight rows: capital cost 8.21, interest 5.96, debt share 4.10, fixed O&M 4.09, degradation 3.51, life 1.73, hurdle 1.59, term 1.16 (USD million). Close on the source line: "Checked against: 34 published figures (Lazard, the Annual Technology Baseline, EIA, CAISO's market monitor, Berkeley Lab, Potomac Economics)." (session 298: 20 until then, before Potomac's 2024 net revenue; the same session set solar's degradation default to the ATB's 0.7 percent, so the solar case's rows and NPV above are the ones of before it.)
- California, if asked: `/cost-of-power/seller?iso=caiso`: 28.45 per kW; 13.86 against 28.53, a capture rate of 49 percent; coverage 0.23; breakeven PPA 73.19.

## Where every number comes from

"Methods note" is `docs/methods/generator_earns_algorithm.md`.

| Number | File | Section |
|---|---|---|
| 59.85; 102.24; 130.80; 23.27; 32.17; -8.90; -27.7; 0.67; 8,736 hours; 80,832,584 MWh | Methods note; `runs/session264/repl.out` (the mirror tonight) | Opening; 4.2; 4.3 |
| The capture rate 72 (and 91, 49 for CAISO) | the page tonight, key `cap|ercot|HB_HUBAVG|rt|solar|l12|rate`; `runs/session264/cv1.out` | session 264 |
| 82,500,000; 0.0858033; 7,078,769; 70.79 | Methods note; `site/scripts/test-seller-finance.mjs` | Section 2; 11.3 |
| 39.14; 58.36; -74.16; 2,580; USD 550 of equity | Methods note; the mirror tonight | 11.3 |
| Revenue by year; the income table; capture rate by year and by hub | Methods note; `docs/brand/review-235/numbers_before_after.txt` | 4.8; 4.9; part 3 |
| The eight bars (8.21 to 1.16); -65.95 and -82.37 million | `docs/brand/review-212/numbers_before_after.txt` | the `npv` cells and bar lines |
| Worst month 139,299; 11.64 and 6.33 million | Methods note; review-212 numbers | 11.4 |
| Other hubs (47.51, 0.49; 72.48, 0.85); battery 58.53; peaker 48.15 | Methods note; `archive/sessions/SESSION_183_REPORT.md` | 5.1 |
| Wind 56.85; peaker toll 8.34; battery toll 8.90 | Methods note; `archive/sessions/SESSION_186_REPORT.md` | Cross-checks |
| Stress days (12,382,220; 18 days; 4,060,021) | Methods note | 4.16 |
| The published comparisons of part 4 | Methods note | Cross-checks; 12.5 |
| 1,428 and 4,197 hours; 107.495 MW; 6,328,531; 364 days | Methods note | 3.2; 4.11 |
| Battery page: 81.40, 73.00, 148 and 55 | `docs/methods/battery_earns_algorithm.md` | The default case; Cross-checks |
| Reserve adders: 7.05, 0.07; hours of at least USD 100 | `docs/methods/ercot_rt_price_adders.md` | Hours a year with an adder above zero |
| California: 28.45, 2,057, 13.86, 28.53, 48.6, 0.23, 73.19; 2,477, 3,125; 3,650 MW; 30.05, 6.95, 0.78 | Methods note; `docs/howitworks/computed/generator_caiso_check_2026-10-13.json` | 12.2 to 12.5 |
| Every default, bound and step, the PPA term | `site/lib/seller/finance.ts`, `site/lib/merchant.ts` | `SPECS`, `defaultsOf`, `DEFAULTS`, `DEBT`, `HURDLE`, `TARGET` |
| The edge cases of part 5 | `runs/session264/edge.out`, `runs/session264/profile_edges.out` | session 264 |
| The license verdicts (ERCOT, CAISO may be public; ISO-NE, NYISO need permission) | `docs/licenses.md`; `site/data/license_status.json` | rows 2 to 5; `merchant_revenue_monthly` |
| Check counts: 234 of 234 tonight (179 before) | `runs/session264/cv1.out`, `cv2.out`; `archive/sessions/SESSION_235_REPORT.md` | the summary line |
