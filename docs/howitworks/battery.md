# How it works: What a battery earns

- **Address:** `/cost-of-power/battery` (production: `https://erw-flame.vercel.app/cost-of-power/battery`).
- **Status:** in review, like every page of the site (`site/lib/release.ts`). A visitor sees the in-review page; a demo needs the internal view (section 7).
- **Written from:** `main` at commit `9700198f`, which holds the page as merged in `80aa2362` (session 234, the brand restyle). Checked again by session 260 against `main` at `34b468fa`: since `9700198f` the page's code changed only in where its fonts and wrapper come from (`site/components/Brand.tsx`, session 235); no label, default or number moved.
- **California (session 257):** four passages below carry the mark "(session 257)". They describe the page as that session committed it on its branch (`9e0bbfe8`, 18:24 UTC on 2026-10-13): CAISO's line beside its market monitor, and CAISO's stress days. They hold from the moment that branch is on `main`.
- **Date:** 2026-10-13. A number marked **[c]** is printed in no method or report: it was computed for this document with the page's own library from the table built on 2026-10-13 at 08:10 UTC (`docs/howitworks/computed/`, the script and its output); every other number is quoted from the file named in the last section.

## 1. What it is for, and for whom

- **The question.** What did a grid battery of a given size and duration earn in ERCOT or CAISO, from energy and from ancillary services together, by year and by stream, did that cover its debt, and is it worth building at stated costs.
- **For whom.** A developer or investor sizing a merchant battery; a lender who wants a coverage figure and a bad month; an operator who wants a ceiling to set a real result against.
- **What it gives.** USD per kW of rated power and US dollars for the reader's size. The default case is ERCOT, 4 hours, perfect foresight, 100 MW: USD 81.40 per kW over October 2025 to September 2026, 33 percent of it from ancillary services, debt covered 2.63 times, NPV USD -69.78 million.
- **What it is.** An upper bound on what the posted prices offered one small battery at the hub. The page says so under its chart.
- **What it is not.** Not a forecast, not a valuation, not what any real battery was paid, and not advice. No sentence on the page says what to build.
- **Where it stops.** Two grids are shown: ERCOT from 2018-01-01 and CAISO from 2024-09-01. NYISO and SPP are built and in review. PJM, ISO-NE and MISO are words only: their prices are licensed.

## 2. The model, in numbered steps

1. **Prices come in.** Connectors write ERCOT's hub energy prices at `HB_HUBAVG` (real time every 15 minutes, day-ahead hourly) and its hourly day-ahead ancillary clearing prices (`ercot_as_prices`). For CAISO: the SP15 hub and `caiso_as_prices`.
2. **A price becomes an hourly price.** The hour's energy price is the mean of its intervals, and only when all are present (four of four for ERCOT real time). An hour with a missing interval has no price.
3. **A day is admitted or left out.** A local day (23, 24 or 25 hours) is solved only when every hour has an energy price and a price for every product bought that day. Any other day is left out and counted. Nothing is filled or scaled.
4. **One optimization a day.** For each grid, strategy, duration and local day, one linear program (scipy's HiGHS) splits 1 MW hour by hour between charging, discharging and an award of each ancillary product, each between 0 and 1 MW.
5. **What it maximizes.** Energy price times (discharge less charge), plus each product's capacity price times its award, summed over the day's hours.
6. **Power limit.** In an hour, discharge plus upward awards is at most 1 MW; charge plus Regulation Down is at most 1 MW. So a megawatt is sold once.
7. **Energy limit.** The battery starts every local day empty. State of charge rises by 0.9274 of what is charged and falls by the discharge over 0.9274 (the square root of 0.86), and stays between 0 and the duration.
8. **Energy behind reserves.** Each upward award must have stored energy to deliver it for the product's required duration, at the hour's start and at its end. Regulation Down must have room to absorb.
9. **One cycle.** The energy taken out in a day is at most one full charge.
10. **Reserves are not called.** An award is paid its price and moves no energy.
11. **Negative prices.** If the solution charges and discharges in the same negative-price hour, the day is solved again with one charge-or-discharge switch for each such hour. In the 36 months exported this was needed on one day, 2025-01-04.
12. **Every limit is checked again** on the solution, hour by hour. One violation stops the whole build.
13. **Days become months.** A day's energy revenue, each product's revenue and the total are summed by local month into `battery_stack_monthly`, per MW, rounded to four decimals. A month with no solved day has no revenue row, never a zero.
14. **The live set.** The loader copies the table to Supabase. The page reads the rows of one hub, one strategy and one duration on each request.
15. **A month counts** when at least 90 percent of its days are solved. Only such months enter any figure.
16. **The last twelve months** are the newest month that is complete in the table and the eleven before it, all counted. The headline is their total per MW over 1,000 (USD per kW), and that total times the reader's MW (US dollars).
17. **A bad month** is the 10th percentile, by nearest rank, of the counted months among the 36 calendar months ending with the same month.
18. **Debt coverage** is the twelve months' revenue for the size, less a year of fixed O&M, over a year of debt payments. Default: `(8,140,219 - 2,200,000) / 2,261,119 = 2.63`.
19. **Is it worth building.** In the browser, scenario A repeats the last twelve months' revenue every year of the project life, cut by the degradation rate each year after the first, and computes cash flow to equity, NPV at the hurdle rate, IRR, a breakeven toll and the merchant tail. Nothing is sent.
20. **What matters most.** Each assumption is moved down and up by one stated step, the others held, and the NPV recomputed.
21. **The check.** `site/scripts/check-values.mjs` reads the table itself and recomputes every keyed number on the page (254 of 254 in sessions 208 and 211).

## 3. Every assumption, its default and its source

"Fixed" means the reader cannot change it on the page. Labels in quotation marks are the page's own.

| Assumption | Default | Where the user changes it | Source |
|---|---|---|---|
| Grid | ERCOT | "Grid" | ERW's choice of default |
| Where energy is priced | `HB_HUBAVG` (ERCOT), SP15, `TH_SP15_GEN-APND` (CAISO) | fixed for each grid | ERW's assumption; a battery is paid its own node's price |
| History | ERCOT from 2018-01-01; CAISO from 2024-09-01 | fixed | what the price tables hold |
| Duration | 4 hours | "Duration": 2, 4 or 8 hours | ERW's choice; the fleet's mean was 1.50 hours in 2025 |
| Size | 100 MW | "Size, MW", 1 to 5,000 | ERW's choice; every result is linear in MW, itself an assumption |
| Strategy | Perfect foresight: energy at the hourly real-time price, ancillary at day-ahead prices, all known in advance | "Strategy": "Day-ahead schedule" | ERW's definition of an upper bound |
| Day-ahead schedule | paid day-ahead energy and ancillary prices; every offer clears; no real-time trading | "Strategy" | ERW's definition |
| Price taker | awards of 0 to 1 MW per MW at the posted price, whatever the market's size | fixed | ERW's assumption; tested in session 74 |
| Reserves called | never | fixed | ERW's assumption; tested in session 79 |
| Round-trip efficiency | 86 percent, split evenly between charge and discharge | "Round-trip efficiency": 86, 89 or 92 | Lazard LCOS v10.0: 86 to 92 percent; the model runs at the low end |
| Cycles | at most one full cycle a day | "Cycles a day, at most": 0.5, 1, 1.5 or 2 | ERW's choice (the seller tab's rule); the other steps are the reader's |
| Start of day | empty; nothing carried over midnight | fixed | ERW's choice (the seller tab's rule) |
| Resolution | hourly | fixed | ancillary prices are hourly |
| ERCOT products | Regulation Up, Regulation Down, Responsive Reserve, Non-Spin, and ECRS from 2023-06-10 | fixed | `ercot_as_prices`, day-ahead clearing prices |
| CAISO products | Regulation Up, Regulation Down, Spinning Reserve, Non-Spinning Reserve, region `AS_CAISO_EXP` | fixed | `caiso_as_prices` |
| Energy behind ERCOT Regulation and Responsive Reserve | 1 hour to 2025-12-04; 30 minutes from 2025-12-05 | fixed | before: assumed, not verified; from: ERCOT NPRR 1282 |
| Energy behind ECRS | 2 hours from 2023-06-10; 1 hour from 2025-12-05 | fixed | ERCOT NPRR 1096; NPRR 1282 |
| Energy behind Non-Spin | 1 hour to 2022-12-08; 4 hours from 2022-12-09 | fixed | before: assumed; from: NPRR 1096 |
| Energy behind CAISO regulation | 1 hour (day-ahead awards) | fixed | CAISO tariff, section 8.4.1.1(g) |
| Energy behind CAISO reserves | 30 minutes | fixed | CAISO tariff, section 8.4.3 |
| A day with a missing hour | left out whole, counted | fixed | ERW's rule: never filled |
| Capacity payment | none | "Contract share" and "Contract price" | ERCOT has none; California's resource adequacy prices are not held |
| A month counts | 90 percent of its days solved | fixed | the seller tab's rule |
| The last twelve months end | with the last complete month | fixed | the owner's ruling of 2026-10-11 (session 195) |
| A bad month | 10th percentile, nearest rank, of 36 calendar months | fixed | ERW's choice (session 71) |
| The one month set aside | a month above 25 percent of everything held gets a column without it | fixed | ERW's choice (session 71) |
| Chart scale | broken when the tallest year is above 2.5 times the second | fixed | ERW's choice, so the other years stay readable |
| Capital cost | 610, 1,110, 2,110 USD per kW (2, 4, 8 hours) | "Capital cost" | Lazard LCOE+ June 2025, LCOS v10.0, midpoints of 340 to 880 and 620 to 1,600; 8 hours is a straight line through the two, an extrapolation |
| Fixed O&M | 11.2, 22, 43.6 USD per kW a year | "Fixed O&M" | the same Lazard cases |
| Debt share | 20 percent of capital cost | "Debt share" | Lazard's storage cases: "20% debt at an 8% interest rate and 80% equity at a 12% cost" (60 percent until session 208) |
| Interest rate | 8 percent a year | "Interest rate" | the same |
| Term of the debt | 20 years, level payments, cut to the life if longer | "Term of the debt" | Lazard: 20 years for storage |
| Degradation | 2.6 percent a year, as a cut to revenue | "Degradation" | Lazard LCOS v10.0, 2 and 4 hours; 8 hours takes the same |
| Project life | 20 years | "Project life" | Lazard |
| Hurdle rate | 12 percent a year | "Hurdle rate" | Lazard's cost of equity; the NPV is to equity (the owner's ruling of 2026-10-12) |
| Contract | share 0, price 0: fully merchant | "Contract share", "Contract price" | none: the reader's own term; no published price is held |
| How a contract runs | for the debt's years, at a flat price; the contracted share earns nothing from the market | fixed | ERW's choice (session 208) |
| Future revenue | the last twelve months, every year of the life | fixed | ERW's assumption, not a forecast |
| Tax, tax credit, augmentation, residual value, inflation | none | fixed | ERW's choice: none is modeled |
| Breakeven toll | the price at which coverage is 1.25 | fixed | ERW's choice; the code cites no source for 1.25 |
| IRR search | between -99 and 1,000 percent a year | fixed | ERW's choice; outside it the page says "none" |
| Steps of efficiency and cycles | the model's own runs, nothing interpolated; the file is rebuilt by the data machine's daily run (on `main`: built 2026-10-13T17:42:40Z) and is withdrawn when a month of the table differs from it by more than half a cent per MW | fixed | `site/data/battery_scenario_steps.json` |
| The awards line | the months both tables hold whole (January to July 2026); the fleet's kW is the sum of each resource's highest limit (HSL) in the month | fixed | `site/data/battery_awards_beside.json`, built 2026-10-10 |
| California's line beside its market monitor (session 257) | 2025, a 4-hour battery on the day-ahead schedule: the model's energy and regulation income are computed from the table; the real fleet's 35 and 9 are typed from the report | fixed | `FLEET_BESIDE` in `site/lib/batterystack.ts`; CAISO Department of Market Monitoring, 2025 Annual Report on Market Issues and Performance, June 2026, section 1.3.3, Tables 1.7 and 1.8 |
| Rounding | the table to four decimals; US dollars to a whole dollar for the size; USD per kW to two decimals | fixed | the code |
| Sensitivity steps | capital cost USD 100 per kW; debt share 10 points; interest 1 point; term 5 years; fixed O&M USD 5; efficiency 3 points; cycles 0.5; degradation 1 point; life 5 years; hurdle rate 1 point; contract share 10 points; contract price USD 1 | fixed | ERW's choice |

## 4. The cross-checks

"Gap" is ours less theirs, USD per kW unless said. A gap is not an error to be closed: most rows set one modeled battery beside a fleet.

| What is compared | Ours | Theirs | Gap | Reason for the gap | Where it is written |
|---|---|---|---|---|---|
| ERCOT, day-ahead ancillary income, January to July 2026, a month | 2.25 | 0.40, ERCOT's storage resources' own awards | +1.85; ours is 5.66 times | The model holds 142 percent of its power in awards in the mean hour; the fleet held 21.6 percent. Regulation alone: 122 against 4.4 | `battery_earns_algorithm.md`, section 9 |
| ERCOT, 4 hours, 2024 | 148 foresight, 127 day-ahead | 55, Modo Energy's fleet average | +93, +72 | One price-taking battery at the hub against a fleet at its nodes, mostly 1 and 2 hours | the same note, "Cross-checks" |
| ERCOT, 4 hours, 2025 | 87, 78 | 26.0 through November; 29.4 for the year, Modo's nowcast | +58, +49 | The same. Ours over theirs is 2.7 and 3.0 in the two years | the same |
| ERCOT, 2024 and 2023 | 148 and 530 foresight; 127 and 459 day-ahead | about 127 and up to about 475, E3's modeled 2-hour battery at ERCOT North | 2024: +21, 0; 2023: +55, -16 | The closest method to ours; 2 hours at the North hub against 4 at the hub average | the same |
| ERCOT, first half of 2025, a month | 7.3 | 2.13, Tyba's median asset; 6.19 the best | +5.2; +1.1 | Ours sits above the best asset | the same |
| ERCOT, market revenue, February to July 2026 | 18.81, the 2-hour day-ahead schedule | 7.17: the fleet's day-ahead awards 4.17 and real-time deviations at the hub price 3.00 | +11.64 (subtraction made here) | The fleet figure leaves out contracts, node prices and real-time ancillary money | `ercot_storage_realtime.md`, "As built" |
| ERCOT, day-ahead only, January to July 2026 | 30.14, the 2-hour day-ahead schedule | 6.53, the fleet's day-ahead awards | +23.61 | Never offered 9.70 (an allocation); price -0.62; offered and not awarded 14.53 | `ercot_storage_dam_offers.md`, "The gap in three parts" |
| ERCOT's market monitor, 2024 report | none | no storage net revenue published | none to compute | Its net revenue analysis covers gas, wind and solar | `battery_earns_algorithm.md`, "Cross-checks" |
| CAISO, 2025, 4 hours, day-ahead, run the market monitor's way | 84.72 | 77.3, the market monitor's own model, "CAISO System" | +7.4 (10 percent) | One hub against more than 280 nodes; their regulation moves energy; their month-long horizon has no cycle limit. Not separated | `battery_stack.md`, "CAISO beside its market monitor" |
| The same by quarter | 29.23; 24.30; 17.45; 13.75 | 28.8; 22.8; 14.2; 11.5 | +0.4; +1.5; +3.3; +2.3 | Same shape. The third quarter's gap is not explained | the same |
| CAISO, 2025, the page's model, day-ahead | 85.34 | 77.3 | +8.0 | The two reserves add 0.77; round trip 0.86 against 0.85 | the same |
| CAISO, 2025, the page's model, perfect foresight | 91.74 | 77.3 | +14.4 | An upper bound against a day-ahead schedule | the same |
| CAISO, 2025, the real fleet: energy; regulation | 42.31; 42.25 | nearly 35; 9 | +7.3; +33.3 | The whole gap is regulation: the model sells as if the market had no size | the same |
| CAISO, 2025, the southern local areas | 84.72 | 62.6; 64.2; 66.3 | +22.1; +20.5; +18.4 | Not explained: how their nodes map to SP15 was not checked | the same |
| CAISO, 2022 to 2024, the fleet | no whole year held | 103, 78, 53 | none to compute | CAISO's prices are held from 2024-09-01 | both notes |
| Revenue against the cost of storage | 81.40, last twelve months | 144.90 to 320.04 per kW-year, Lazard's levelized cost of a 4-hour battery | -63.50 to -238.64 | Lazard's cost also pays charging energy, augmentation, taxes and a 12 percent return on equity | `battery_earns_algorithm.md`, "Cross-checks" |
| Round-trip efficiency | 86 percent | 92 to 86 (Lazard); 85 (Annual Technology Baseline) | 0 to -6; +1 | The low end of Lazard's range | the same |
| Fixed O&M, 4 hours | 22 | 44.40, the ATB's 4 percent of capital cost | -22.40 | The ATB pays for augmentation inside fixed O&M; Lazard does not | the same |
| Project life | 20 years | 15 years (ATB) | +5 | Lazard's storage cases run 20 | the same |
| SP15 day-ahead peak block, January to September 2026, USD per MWh | 24.04 | 23.97, ICE's index in EIA's file | +0.07 | A traded expectation against the cleared price | the same |
| The optimizer, all 1,096 exported days | the model's day | an independent solve and a ceiling that needs no solver | largest relative gap 3.2e-10; the ceiling reached on 1,095 days | The one other day is the switch day, 2025-01-04, USD 0.038 below the linear ceiling, as it should be | `battery_earns_algorithm.md`, section 8 |
| Reserves called, ERCOT, 2018-01-01 to 2024-07-31 | 393.1 and 530.1 (2022, 2023), never called | 401.8 and 562.3, called on ERCOT's own event lists | within 0.1 percent in 2018 to 2020; 0.9 percent below in 2021; above from 2022 | Energy delivered on call is paid a scarcity price | `battery_stack.md`, "Reserves that are called" |
| A cap by the market's size, ERCOT, 2026-09-03 to 2026-10-02 | 5.92, price taker | 4.52, fleet-limited | the capped battery earns 69 to 82 percent | Caps average 2.6 percent of power for regulation, 9 for ECRS, 13 for Responsive Reserve and Non-Spin | `battery_stack.md`, "The fleet-limited estimate" |

- The page's source line says "Checked against: 14 published figures".
- **Not done.** The Stata do-file has not been run: Stata is not on the machine that wrote it. Its Python mirror equals the page's library.
- **Stale by design.** The replication files still carry 60 percent debt and coverage 0.88 (the defaults before session 208) until the next export.

## 5. What it cannot see, ranked by how much it moves the answer

Items 1 to 7 are ranked by the number the repository holds, as far as numbers in different units can be set side by side. The last group holds no number and cannot be ranked.

1. **The years ahead.** The NPV repeats the last twelve months for 20 years. Size: the same battery's revenue is USD 81.40 per kW over the last twelve months, 255.08 a year over 2023 to 2025, and 614.58 a year over every year held (269.68 without February 2021). NPV reaches zero at the defaults at about USD 190 per kW a year. The tool holds no forecast.
2. **The size of the ancillary markets.** The battery sells reserves as if the market had no limit. Size in ERCOT: USD 2.25 per kW a month against the fleet's 0.40, January to July 2026; with awards capped by the market's size the battery earns 69 to 82 percent of the price taker's figure (30 days of 2026). Size in CAISO: regulation of USD 42.25 per kW in 2025 against the real fleet's 9. Direction: the page is too high.
3. **Operation.** Perfect foresight against the day-ahead schedule: USD 81.40 against 73.00 over the last twelve months; 10.0 percent of the page's figure in 2025. The day-ahead schedule is still a perfect schedule. Among real assets the spread is wide: a median of USD 2.13 per kW a month and a best of 6.19 in the first half of 2025 (Tyba). For one real operator: no number held.
4. **The node.** Energy is priced at the hub. In the one week of ERCOT node prices held (2026-09-28 to 2026-10-04, 291 storage settlement points) the daily spread between the four dearest and four cheapest hours was USD 28.27 per MWh at the hub and 44.29 at the median point; 227 points were wider than the hub. In California the market monitor's own model runs from 62.6 (LA Basin) to 111.7 (Greater Fresno) around a system figure of 77.3. Direction: either. Applied to no figure on the page.
5. **Degradation.** The model has no capacity fade. The scenario cuts revenue 2.6 percent a year. One point more or less moves the default NPV by USD 3.02 million [c]. Augmentation cost: none modeled; the ATB's convention would about double fixed O&M (44.40 against 22).
6. **Reserves that are called.** Within 0.1 percent of the page in 2018 to 2020, 0.9 percent below in 2021, and above it in 2022 and 2023 (401.8 against 393.1; 562.3 against 530.1). Regulation is never called in that test: no number held.
7. **Each day from empty.** The first hour of each day can hold no upward reserve. Size: at most USD 1.29 per kW over the last twelve months, 1.6 percent of 81.40. Direction: the page is slightly too low. Energy left at midnight averages 0.023 MWh per MW.

**No number held:**

- **California's resource adequacy contract.** Not in the warehouse. For a California battery it is revenue the page does not show.
- **Taxes and tax credits.** None in the NPV.
- **Real-time ancillary prices in ERCOT since 2025-12-05.** Not held, so ancillary income is day-ahead under both strategies.
- **Trading inside the hour.** The model is hourly; 5- and 15-minute trading can earn more from energy.
- **Outages and station power.**
- **Scarcity adders.** `ercot_rtm_price_adders` was added on 2026-10-13 (session 244). Neither the model nor the page reads it; what it would add was not examined.

## 6. The ten hardest questions

### 1. Your battery knows tomorrow's real-time prices. What does it earn without that?

On the day-ahead schedule the default case earns USD 73.00 per kW over the last twelve months against 81.40 with foresight. That schedule is still perfect against day-ahead prices and assumes every offer clears. What a real operator captures the tool does not know: it would need each resource's dispatch at its own node price. The only measure held is the fleet's spread: a median asset at USD 2.13 per kW a month, the best at 6.19, the model at 7.3 (first half of 2025).

### 2. Ancillary markets are small. What is left when 20,000 MW chase them?

Less than the page shows, and the page says so in one line under the income table. From January to July 2026 the model took USD 2.25 per kW a month of day-ahead ancillary income; ERCOT's storage resources, 17,180 to 21,365 MW of them, were awarded 0.40. With each award capped by ERCOT's own quantities divided by the fleet, the battery earned USD 4.52 per kW against 5.92 over 30 days of 2026, the ancillary stream falling about four fifths. That estimate is for review and is not on the page; ERCOT's hourly quantities are held for those 30 days only.

### 3. How far is the model from what real batteries were paid?

In ERCOT, about three times with foresight: USD 148 per kW against the fleet's 55 in 2024, and 87 against about 29 in 2025 (Modo Energy). Part of that is the battery, not the method: the fleet averaged 1.50 hours in 2025. Taken down the ladder of `battery_early_years.md`, 2025 reads 87.4 (the page), 78.7 (day-ahead prices), 46.2 (the fleet's duration), 36.7 (no regulation), 28.5 (energy only). In the warehouse's own data, February to July 2026: the fleet's day-ahead awards plus real-time deviations at the hub price were USD 7.17 per kW; the 2-hour day-ahead model made 18.81.

### 4. Where is degradation?

Not in the model. The battery holds its rated duration every day of every year. The finance block cuts revenue by 2.6 percent a year (Lazard's rate); that is a haircut, not fade, because fade shortens duration and revenue is not proportional to duration. One point either way moves the default NPV by USD 3.02 million [c]. Augmentation cost, outages and station power: no number held.

### 5. Does the battery have the energy behind the reserves it sells, and what if it is called?

It has the energy: each upward award must be backed for its required duration at the start and the end of the hour, and the build stops if one is not. Non-Spin needs 4 hours, so a 2-hour battery can hold at most 0.464 MW of it per MW. It is never called. Tested on ERCOT's own event lists for 2018-01-01 to 2024-07-31, being called changed the year by under 1 percent before 2022 and raised it after. Regulation's energy is not in that test, and CAISO's market monitor does model it. The battery starts each day empty and ran 0.983 cycles a day over the last twelve months; a limit of 1.5 cycles would lift the twelve months from 81.40 to 83.57.

### 6. ERCOT changed its market on 2025-12-05 (real-time co-optimization, RTC+B). Is the model still right?

Partly. The model applies the new required durations from that day (30 minutes for regulation and Responsive Reserve, 1 hour for ECRS; NPRR 1282). It still pays ancillary services at day-ahead prices under both strategies: the real-time ancillary prices are not held. The ORDC adders ended on 2025-12-04; the table of them was added on 2026-10-13 and the model does not read it. The last twelve months are October 2025 to September 2026: all but the first two months and four days fall after the change, so the headline is mostly a figure of the new design. What the new design paid a battery for real-time ancillary service the tool does not know; it would need ERCOT's real-time clearing prices for capacity.

### 7. Can the CAISO result be trusted?

For energy, within about a fifth; for regulation, no. Run the market monitor's way, the model gives USD 84.72 per kW for 2025 against the monitor's own 77.3, and tracks it by quarter. But real batteries were paid about 35 for energy and 9 for regulation; the model takes 42.31 and 42.25. The page prints that comparison in one line under CAISO's income table, as it prints the awards line for ERCOT (session 257). CAISO is held for 25 months and one full year. Every CAISO notice in those months is a Restricted Maintenance Operations notice: no Flex Alert and no emergency stage. No resource adequacy payment is in the figure.

### 8. The chart shows USD 3,431 per kW in 2021. Did anyone earn that?

The warehouse does not hold what anyone earned in 2021. The figure is what the posted prices offered: USD 2,841.6 of the year's 3,430.6 is seven days, 13 to 19 February (Winter Storm Uri). February 2021 alone is 57 percent of everything the default battery earned in every month held, which is why the table gives the every-year average both with it (614.58) and without it (269.68). The fleet was 821 MW at the end of 2021 and its mean duration that year was 1.23 hours; the page's shortest battery holds 2.

### 9. The NPV is USD -69.78 million. Is the tool saying do not build?

It says a number. The last twelve months paid USD 81.40 per kW; less fixed O&M of 22 that is 59.40 a year, worth USD 444 per kW over 20 years at 12 percent, against 888 of equity. Revenue would have to be about USD 190 per kW a year; ERCOT paid that to this battery only in 2021, 2022 and 2023. A capital cost of USD 620 per kW gives about USD -23 million and an IRR of 2 percent; half the battery under contract at USD 10 per kW-month gives about USD -51 million. The block has no tax credit, no tax, no augmentation and no residual value. Coverage of 2.63 times is not in tension with it: the year's revenue pays the year's debt at 20 percent debt; it does not pay equity 12 percent.

### 10. My battery is at a node and has a toll. Does the tool see either?

The node, no: energy is priced at the hub, and the one week of node prices held is applied to nothing. The toll, as two numbers the reader types: "Contract share" and "Contract price". No published contract price is held, so the default is fully merchant. The breakeven toll at the defaults is USD 4.19 per kW-month: the price on the whole battery at which coverage is 1.25.

## 7. A five-minute demo, click by click

The page is in review. On the machine you will show it from, open the internal view first: `https://erw-flame.vercel.app/internal/unlock?token=<your internal token>` (or paste the token into the form at `/internal/open`), then `https://erw-flame.vercel.app/cost-of-power/battery`.

This path was written from the page's code and its check scripts on 2026-10-13. It was not clicked through in a browser.

**Say this first:** this is what the posted prices offered one small battery at the hub, split hour by hour so nothing is counted twice. It is a ceiling, and the page shows how far the real fleet sits below it.

### Minute 0 to 1: the headline

1. Open the bare address. The tab "What a battery earns" is the third of three. The panel "Your battery" reads ERCOT, "4 hours", "Perfect foresight", 100.
2. Read the sentence under "What did it earn?": "Over the last twelve months a 100 MW, 4-hour battery in ERCOT earned USD 81.40 per kW, 33 percent of it from ancillary services, and covered its debt 2.63 times."
3. Name the three numbers:
   - "Last twelve months, all streams": USD 81.40 per kW; beneath it USD 8.14 million (8,140,219) for 100 MW, October 2025 to September 2026.
   - "A bad month: the 10th percentile, last 36 months": USD 475,477, December 2024.
   - "Debt coverage, last twelve months": 2.63 times, over debt payments of USD 2.26 million (2,261,119) a year.

### Minute 1 to 2: the chart and the table

1. "Revenue by year, USD per kW". The labels above the bars, rounded to a dollar: 244, 402, 187, then 2021 broken at the top (3,431), 393, 530, 148, 87, and 2026 hatched with "9 months" at 60.
2. Read the line under the chart aloud: "This is an upper bound: before 2024 it is mostly payment for holding reserves, to a battery longer than any Texas then had, and 2021 is one week of February. Recent years are the ones to read."
3. "Income by stream", last row "Total, USD per kW": 81.40 ("Last twelve months, USD"), 255.08 ("2023 to 2025, a year, USD"), 614.58 ("Every year held, a year, USD"), 269.68 ("Without Feb 2021, a year, USD").
4. The line under the table is the one to stop on: "this model takes USD 2.25 per kW a month; ERCOT's storage resources were awarded USD 0.40 per kW of their power a month; the model is 5.66 times the awards."

### Minute 2 to 3: the other strategy, the other grid

1. Under "Strategy" choose "Day-ahead schedule" and press "Show". The address becomes `?grid=ercot&dur=4&strat=dayahead&mw=100`. The sentence reads USD 73.00 per kW; 35 percent from ancillary services [c]; debt covered 2.26 times [c].
2. Under "Grid" choose "CAISO" and press "Show" (`?grid=caiso&dur=4&strat=dayahead&mw=100`). USD 64.96 per kW; 51 percent from ancillary services [c]; 1.90 times [c]. With "Perfect foresight" the same battery reads 79.05.
3. Point at three things. The bad month's note ends ": CAISO is held from September 2024". The second column reads "not held: CAISO holds one full year (2025)". The row "Capacity" reads "Not held: California's resource adequacy prices are contract statistics, not yet in the warehouse".
4. Read the line under the income table (session 257): "In 2025, for a 4-hour battery on the day-ahead schedule, this model takes USD 42.31 per kW from energy and USD 42.25 from regulation; CAISO's market monitor reports that real batteries in its area with a full year of operation earned about USD 35 per kW from energy and USD 9 from regulation". Say: energy is close, and the whole gap is regulation, a market the model treats as if it had no size. The two model figures are computed from the table and can move; 35 and 9 are the report's. The sentence with the downloads names California's stress days by their days ("the days of CAISO's system-wide notices"), where ERCOT's reads "Uri, Elliott, the 2023 heat".

### Minute 3 to 4: is it worth building

1. Open the bare address again (or choose "ERCOT" and "Perfect foresight" and press "Show"). Follow "Scenarios A and B" in the panel, or scroll to "Is it worth building?".
2. Read scenario A's column: "Revenue, last twelve months" USD 81.40; "Debt coverage" 2.63 times; "NPV at the hurdle rate" USD -69.78 million (USD -697.80 per kW at 12 percent); "IRR" -8.8 percent; "Breakeven toll" USD 4.19; "Merchant tail after the contract" USD 0 (0 years).
3. Type 50 into "Contract share" and 10 into "Contract price". Nothing is sent; the address gains `?an=50&ap=10`. The headline sentence now reads "with 50 percent of its power contracted at USD 10 per kW-month," and coverage 3.48 times [c]. NPV is about USD -51 million (-51.13 [c]).
4. Press "Reset all of A". Then type 620 into "Capital cost" (`?ac=620`): NPV about USD -23 million (-23.12 [c]), IRR 2.1 percent [c] (the methods note says 2 percent). Press "Reset" beside the field.

### Minute 4 to 5: what matters most

1. Scroll to "What matters most". The chart "How far each assumption moves NPV, scenario A" has ten rows at the defaults (twelve when scenario A holds a contract). The line above it says "holds the other eleven": there are twelve assumptions, and two are not drawn without a contract.
2. By the library's sort the first two rows are "Cycles a day, at most" and "Capital cost" [c]. Capital cost moves NPV by USD 9.52 million either way for USD 100 per kW. Cycles: USD 11.14 million [c], and it is the move down to 0.5 cycles; the move up to 1.5 cycles is USD 1.40 million [c]. The methods note lists capital cost first and calls the 11.14 a move up; the library sorts cycles first.
3. Point at a row: the line under the chart states the two NPVs. "The chart as a table" opens the same figures.
4. Close on the source line: "Checked against: 14 published figures", with the link "Each comparison, with its gap and the reason".

**With a sixth minute:** choose "Scenario B", set "Round-trip efficiency" to 92 and "Cycles a day, at most" to 2. B's revenue is USD 88.24 per kW [c] against A's 81.40, and "What differs" says so in words. "Copy A to B" undoes it.

### If something goes wrong

- **"This tool is in review and will open when it is approved."** The internal view is not open in this browser. Open the unlock address again.
- **"The table could not be read, so no number is shown".** The live set did not answer. Reload.
- **"Duration" acts at once.** "2 hours", "4 hours" and "8 hours" are links, not part of "Show", and a change of duration drops a typed capital cost and fixed O&M.
- **The numbers above hold until October 2026 is complete in the table**, about the first days of November. The twelve months then become November 2025 to October 2026 and every headline number moves.
- **Only 86 and 1 are offered under efficiency and cycles.** The file of steps is withdrawn when the table's months move past it, until the data machine's daily run rebuilds it. The line under the assumptions says which happened.

## Where the numbers in this document come from

| Number | File | Section |
|---|---|---|
| 81.40; 33 percent; 8,140,219; 475,477 (December 2024, 36 months) | `docs/methods/battery_earns_algorithm.md` | "The default case"; 4.2; 4.3 |
| 2,261,119; 2.63; NPV -69.78 million (-697.80 per kW); IRR -8.8; toll 4.19 | the same | "Session 208"; 11.1 |
| 255.08; 614.58; 269.68; 57 percent | the same | 4.5 |
| 2.25; 0.40; 5.66; 142, 21.6, 122 and 4.4 percent; 17,180 to 21,365 MW | the same, and `site/data/battery_awards_beside.json` | 9 |
| 0.464; 1.29 and 1.6 percent; 0.023; 0.983; 2025-01-04; 1,096 days; 3.2e-10; 0.038 | the same | 3.3; 5; 11; 3.4; 8 |
| 73.00; 79.05; 64.96; Modo 55, 26.0, 29.4; E3 127, 475; Tyba 2.13, 6.19, 7.3; Lazard 144.90 to 320.04; ATB 44.40, 15 years; ICE 23.97; 444, 888, 190; 620, -23 million, 2 percent; -51 million; 9.52; 11.14 | the same | "Cross-checks"; 11.1 |
| The chart's years (243.7, 402.2, 187.5, 3,430.6, 393.1, 530.1, 147.7, 87.4, 60.2, rounded to a dollar here); 4.52 and 5.92; 69 to 82; 2.6, 9, 13 percent; 401.8, 562.3 | `docs/methods/battery_stack.md` | "How it differs"; "The fleet-limited estimate"; "Reserves that are called" |
| 84.72; 77.3; the quarters; 85.34; 0.77; 91.74; 42.31; 42.25; 35; 9; 62.6, 64.2, 66.3, 111.7; 53, 78, 103 | the same, and `archive/sessions/SESSION_246_REPORT.md` | "CAISO beside its market monitor" |
| The 2025 ladder 87.4, 78.7, 46.2, 36.7, 28.5; 1.50 and 1.23 hours; 821 MW; 2,841.6; 10.0 percent | `docs/methods/battery_early_years.md` | "The ladder"; "What each step takes"; "February 2021" |
| 7.17, 4.17, 3.00, 18.81; 28.27, 44.29, 227 of 291 | `docs/methods/ercot_storage_realtime.md` | "As built on 5 October 2026" |
| 30.14; 6.53; 23.61; 9.70; -0.62; 14.53 | `docs/methods/ercot_storage_dam_offers.md` | "The gap in three parts" |
| California's line: its words, 35 and 9, the report's section and tables; the stress days named by their days (session 257) | `docs/methods/battery_earns_algorithm.md`, `docs/methods/battery_stack.md`; `site/lib/batterystack.ts` | "For CAISO, since session 257"; "CAISO beside its market monitor"; `FLEET_BESIDE`, `STRESS_BY` (each as on session 257's branch at `9e0bbfe8`) |
| ORDC adders end 2025-12-04; the table's date | `docs/methods/ercot_rt_price_adders.md` | "What it is" |
| 83.57 (1.5 cycles) | `site/scripts/test-battery-finance.mjs` | line 97 |
| 254 of 254 | `archive/sessions/SESSION_208_REPORT.md`, `SESSION_211_REPORT.md` | "Checks" |
| Labels, addresses, defaults, bounds, steps, 1.25, the IRR bracket | `site/app/cost-of-power/battery/` (`page.tsx`, `BatteryForm.tsx`, `Scenarios.tsx`), `site/lib/batterystack.ts`, `site/lib/battery/finance.ts`, `site/components/decisions/ScenarioBlock.tsx` | the code |
| Every number marked [c]: 35 and 51 percent; 2.26; 1.90; 3.48; -51.13; -23.12; 2.1; 3.02; the chart's first two rows; 11.14 as the move down; 1.40; 88.24 | `docs/howitworks/computed/battery_headline.txt`, written by `battery_headline.mjs` beside it (`node docs/howitworks/computed/battery_headline.mjs`, on a machine that holds the table) | from `warehouse/output/battery_stack_monthly.csv`, retrieved 2026-10-13T08:10:28Z, and `site/data/battery_scenario_steps.json`, built 2026-10-10 |

- The same run reproduced, from the table of 2026-10-13, every headline figure the methods note gives for the table of 2026-10-05: 81.40, 33, 8,140,219, 475,477, 2,261,119, 2.63, 255.08, 614.58, 269.68, 57, -69.78 million, -8.8 and 4.19.
- No report of session 234 is in `archive/sessions/`; the commit `80aa2362` is the record of what landed.
