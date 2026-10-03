# Method: the battery revenue stack

Energy Research Warehouse (ERW), session 67. Tables: `battery_stack_monthly` and `battery_stack_stress_daily` (series, derived, public). Code: `warehouse/derived/battery_stack.py`; the page's arithmetic is `site/lib/batterystack.ts`. Page: `/cost-of-power/battery`, "What a battery earns". Tests: `tests/test_session67.py`.

**The question.** What does a grid battery of a given size and duration earn, from which streams, and does it cover its debt? The seller tab's battery (`merchant_revenue_monthly`, `docs/methods/cost_of_power.md`) is energy only. A real battery also earns from ancillary services and, in some markets, from capacity. This method adds the ancillary services, co-optimized with energy. It adds no capacity payment (see "Capacity").

## Scope

| Market | Hub (energy) | Ancillary prices | From |
|---|---|---|---|
| ERCOT | `HB_HUBAVG` | `ercot_as_prices`: Regulation Up, Regulation Down, Responsive Reserve, Non-Spin, and ECRS from 2023-06-10 | 2018-01-01 |
| CAISO | `TH_SP15_GEN-APND` (SP15) | `caiso_as_prices`, the expanded system region `caiso:AS_CAISO_EXP`: Regulation Up, Regulation Down, Spinning Reserve, Non-Spinning Reserve | 2024-09-01 |

Durations 2, 4 and 8 hours. Every result is per MW of rated power, per local month. The page scales by the reader's size: every result is linear in MW, which is itself an assumption (see "What the model cannot see").

## Co-optimization, not addition

A battery cannot sell its full power as energy and be paid to hold the same power in reserve in the same hour. Adding an energy-only optimum to an ancillary-only optimum would count the battery twice. Instead, for each local day, one linear program (scipy's HiGHS) splits the battery hour by hour between charging, discharging and each ancillary product.

Variables, for each hour `t` of the day, per MW: charge `c_t`, discharge `d_t` (both measured at the grid), and an award `r_k,t` for each ancillary product `k`, each between 0 and 1.

Maximize

    sum over t of  p_t x (d_t - c_t)  +  sum over k, t of  a_k,t x r_k,t

where `p_t` is the energy price (USD/MWh) and `a_k,t` the product's capacity price (USD per MW held for the hour). Subject to:

- **Power.** `d_t + (upward awards in t) <= 1` and `c_t + (downward regulation in t) <= 1`.
- **Energy.** The state of charge `s_t = s_(t-1) + eta x c_t - d_t / eta` stays between 0 and the duration (in MWh per MW), with `s = 0` at the start of every local day and `eta = sqrt(0.86)`: a round trip of 86 percent, the seller tab's (Lazard LCOS v10.0, utility-scale, low end).
- **One cycle.** The energy taken out of the battery in a day, `sum of d_t / eta`, is at most the duration: at most one full cycle a day, the seller tab's rule.
- **Energy behind the reserves.** For every upward product awarded in hour `t`, the battery holds enough stored energy to deliver it for the product's required duration `h_k`: `sum over upward k of r_k,t x h_k / eta <= min(s_(t-1), s_t)`. The requirements add up across products, and hold at the start and at the end of the hour.
- **Room behind downward regulation.** `r_regdn,t x h x eta <= duration - max(s_(t-1), s_t)`: the battery could absorb the energy if called.

**Reserves are never deployed.** An award pays its capacity price and moves no energy. A real battery that is called sells energy at the real-time price and must recharge; in a stress event that matters a great deal (see "What the model cannot see").

**Charging and discharging in the same hour.** At a negative price the relaxed program would charge and discharge at once, to be paid for burning energy. On a day where its solution does that, the day is solved again as a mixed-integer program with one charge-or-discharge switch for each negative-price hour. This happened on a handful of days (the run log counts them). At a price of zero or more it never pays, and a tie is netted out.

**Each day stands alone.** The battery starts every local day empty, as on the seller tab. So energy bought to back a reserve late in the day is lost at midnight. This understates a real battery a little: it would carry the charge over.

## Two strategies

- **Perfect foresight (`foresight`), the upper bound.** Energy at the hourly mean of the real-time price, ancillary services at day-ahead prices, all known in advance. No operator knows the day's real-time prices in advance.
- **The day-ahead schedule (`dayahead`).** The battery is scheduled against day-ahead energy and ancillary prices and paid those prices, with no real-time trading. It assumes the battery's offers clear at the day-ahead price. Day-ahead prices are known before the day, so this is closer to what a schedule can capture, but it still assumes a perfect schedule against them.

## Required durations, and their sources

The stored energy an upward reserve must have behind it. Each market's published requirement is used where it could be checked against the market operator's own document in session 67. Where it could not, one hour is assumed, and the page and this document say so.

| Market | Product | Required duration | Source |
|---|---|---|---|
| ERCOT | ECRS | 2 hours from 2023-06-10 (when ERCOT began buying it); 1 hour from 2025-12-05 | NPRR 1096, "Require Sustained Two-Hour Capability for ECRS and Four-Hour Capability for Non-Spin", approved 2022-05-12, effective 2022-12-09; NPRR 1282, "Ancillary Service Duration under Real-Time Co-Optimization", approved 2025-07-31, effective 2025-12-05 |
| ERCOT | Non-Spin | 4 hours from 2022-12-09 | NPRR 1096 |
| ERCOT | Non-Spin | 1 hour before 2022-12-09 | **assumed**: not verified |
| ERCOT | Regulation Up, Regulation Down, Responsive Reserve | 30 minutes from 2025-12-05 | NPRR 1282: it "updates duration requirements for Regulation Service and Responsive Reserve (RRS) to thirty minutes; and updates duration requirement for ERCOT Contingency Reserve Service (ECRS) to one hour" |
| ERCOT | Regulation Up, Regulation Down, Responsive Reserve | 1 hour before 2025-12-05 | **assumed**: not verified |
| CAISO | Regulation Up, Regulation Down, Spinning Reserve, Non-Spinning Reserve | 1 hour | **assumed**: CAISO's tariff requirement was not checked against the tariff in session 67 |

ERCOT's pages: `https://www.ercot.com/mktrules/issues/NPRR1096`, `https://www.ercot.com/mktrules/issues/NPRR1282`. The requirement that applies to a local day is the one in force on that day.

## Never filled

A local day is solved only when every hour of its energy price (23, 24 or 25 hours) and of every ancillary product bought on that day is held. Any other day is left out of the stack and counted, in `days_left_out` (with `days_left_out_ancillary` and `days_left_out_energy` for the reason). A month's revenue is the sum over its held days only: it is never scaled up to a full month. A month with no day held has no revenue row at all, never a zero. On the page a month counts toward the averages when at least 90 percent of its days are held (the seller tab's rule).

Session 67's run: ERCOT, no day left out under either strategy (3,195 days with perfect foresight to 2026-09-30, 3,197 on the day-ahead schedule to 2026-10-02). CAISO, five days left out under each strategy: 2025-04-06, 04-07 and 04-08 (OASIS returns no ancillary prices for them, `docs/methods/capacity_and_ancillary.md`), and 2024-11-03 and 2025-11-02 (the 25-hour days of the autumn clock change, which the hub price history does not hold).

## The tables

**`battery_stack_monthly`**: entity `<market>:<hub>`, `freq` P1M, `ts_utc` the first day of the market's local month at 00:00:00Z, partition column `market`. `variable` is `<strategy>_<N>h_<metric>`, repeated in `x_strategy`, `x_duration_hours` and `x_metric`:

| Metric | Unit | Meaning |
|---|---|---|
| `revenue_energy_usd_per_mw` | USD/MW | discharge sales less charging purchases, the month's held days |
| `revenue_<product>_usd_per_mw` | USD/MW | each ancillary product: `regup`, `regdn`, and `rrs`, `ecrs`, `nspin` (ERCOT) or `spin`, `nonspin` (CAISO) |
| `revenue_ancillary_usd_per_mw` | USD/MW | the products' sum |
| `revenue_total_usd_per_mw` | USD/MW | energy plus ancillary |
| `discharged_mwh_per_mw` | MWh/MW | energy delivered to the grid |
| `days_held`, `days_left_out`, `days_left_out_ancillary`, `days_left_out_energy`, `days_in_month` | count | the days behind the month |

**`battery_stack_stress_daily`**: the same per local day (`freq` P1D), revenue by stream only, for the days inside the windows of ERCOT's three stress events (`event_window.py`): Winter Storm Uri (2021-02-07 to 2021-02-24), Winter Storm Elliott (2022-12-19 to 2022-12-29), the summer 2023 heat (2023-08-01 to 2023-09-10). The `event` column names the event and is part of the key (Decision 32).

The split between energy and ancillary revenue on a day is one optimum of the program. Where two schedules earn the same total, the split between streams is not unique; the total is.

## How it differs from the seller tab's energy-only battery

ERCOT, 4 hours, perfect foresight, USD per kW of rated power, by year:

| Year | Seller tab, energy only | Energy only, this program | This model: energy | This model: ancillary | This model: total |
|---|---|---|---|---|---|
| 2018 | 39.4 (from July) | 68.2 | 45.2 | 198.5 | 243.7 |
| 2019 | 140.7 | 141.7 | 110.7 | 291.4 | 402.2 |
| 2020 | 49.4 | 50.1 | 34.1 | 153.4 | 187.5 |
| 2021 | 134.9 | 137.9 | 23.0 | 3,407.5 | 3,430.6 |
| 2022 | 150.6 | 153.9 | 126.1 | 267.0 | 393.1 |
| 2023 | 201.0 | 205.3 | 152.0 | 378.1 | 530.1 |
| 2024 | 73.4 | 75.1 | 62.7 | 85.0 | 147.7 |
| 2025 | 62.0 | 63.2 | 57.4 | 30.1 | 87.4 |
| 2026 (to September) | 43.6 | 44.7 | 40.8 | 19.4 | 60.2 |

Three things differ, in this order of size:

1. **Ancillary services are in.** The total is higher in every year, and the energy stream alone is lower than the energy-only figure, because the battery gives up some energy sales to hold reserves that pay more. That is co-optimization working: the streams are not added.
2. **Partial power.** The seller tab's battery moves at full power or not at all in an hour. This program may charge or discharge at part power, which earns 1 to 2 percent more on energy alone (the second column against the first).
3. **Days.** The seller tab's table starts in July 2018 (where its solar and wind shapes start) and leaves out the two clock-change days of each year; this table starts in January 2018 and holds them.

Both are hourly. The session's prompt expected the seller tab's figure to rest on finer real-time intervals; it does not (`merchant_revenue.py` uses the hourly mean of the 15-minute real-time prices), so resolution is not a cause of the difference. With ancillary prices at zero this program reproduces the energy-only optimum at the same resolution (tested).

## Capacity

No capacity payment is in the model, and no value from `iso_all_capacity_prices` (internal) is read by the builder, the tables or the page.

- **ERCOT** is an energy-only market: there is no capacity payment to add.
- **CAISO**: resource adequacy is bought bilaterally. California's resource adequacy prices are contract statistics published by the CPUC; they are not in the warehouse, so the stream is "not held", never an estimate. For a California battery this is an omission the reader should weigh: its resource adequacy contract is revenue this page does not show.
- The page's optional contract (computed in the browser, never sent) lets a reader put their own contracted revenue beside the market's.

## What the model cannot see

- **One battery does not move prices.** The battery is a price taker. Ancillary markets are small next to the energy market, so a large battery or a fleet pushes those prices down. Large sizes are overstated, ancillary income most of all.
- **Reserves are never called**, so no energy is sold or bought on deployment and no state of charge is lost to it.
- **The hub, not the node.** A battery is paid its own node's price.
- **No degradation, outages or station power** beyond the round-trip efficiency and the one-cycle limit.
- **Foresight.** Perfect foresight is an upper bound. The day-ahead schedule assumes every offer clears at the day-ahead price.
- **Hourly.** A battery trading 5- and 15-minute real-time prices can earn more from energy than an hourly model shows.
- **ERCOT after 2025-12-05.** Real-time co-optimization began; real-time ancillary prices are not held, so ancillary revenue is day-ahead in both strategies.

## Results that look implausible, and why they are what the prices say

- **ERCOT 2021: USD 3,431 per kW.** Almost all of it is February (Winter Storm Uri): Responsive Reserve and regulation cleared in the thousands and tens of thousands of dollars per MW for days. A price-taking battery paid for holding reserves it is never asked to deliver collects all of it. In such a storm a real battery holding reserves is called on and runs down. The figure is what the published prices offered, not what a battery could have kept; the page breaks the chart's scale for that year and writes its value, says under the chart that the figures are an upper bound, and gives the average of every year held both with and without February 2021 (see "How the page reads the tables").
- **ERCOT 2018 to 2023: most of the revenue is ancillary** (Responsive Reserve before 2022, ECRS in 2023). From 2024 the ancillary stream falls sharply in the same prices.
- **CAISO: Regulation Down is the largest ancillary stream**, because the battery sits near empty for most of the day with room to absorb energy, and is paid for that room in nearly every hour. This is where the price-taker assumption carries the most weight.

## How the page reads the tables (session 71)

The page leads with the last twelve months, because the earlier years rest on an assumption that matters most in them (see "Results that look implausible"). Session 71 changed the page's wording, order and layout only: no table and no number changed, and every figure is still computed by `site/lib/batterystack.ts` from `battery_stack_monthly` and carries a check key.

- **The summary sentence:** over the last twelve months, the battery's total revenue per kW, the ancillary services' share of it, and its debt coverage. The last twelve months are the newest held month and the eleven before it, all held.
- **The three headline numbers:** the last twelve months (USD per kW, with the US dollars for the reader's size beneath); a bad month, the 10th percentile by total revenue (nearest rank) of the held months among the 36 calendar months ending with the last twelve months' last month (CAISO holds 25 of them, and the page says so); and debt coverage over the last twelve months.
- **The income table's columns**, each by stream and labeled with its span: the last twelve months; the average of the last three full calendar years (the newest year with all twelve months held and the two before it, each also complete: their months' sum over three; where three such years are not held the column says "not held" with the reason, as for CAISO, which holds one, 2025); the average of every year held (the mean of each calendar month's held months, summed over the twelve calendar months); and, where one held month is more than a quarter of everything the held months earned, the same average without that month. In ERCOT that month is February 2021 (Winter Storm Uri): 57 percent of everything a 4-hour battery earned with perfect foresight, which makes the every-year average USD 614.58 per kW with it and USD 269.68 without it (the last twelve months to September 2026: USD 81.40). The month is left out of that one column only: it stays in the data, on the chart (whose scale breaks for 2021, with the value written) and in the average of every year held. A last row gives each column's total per kW.
- **One sentence directly under the chart, not folded:** the figures are an upper bound, because the battery is assumed to sell as much of its power as reserves as it likes at the posted price and is never called, so years before 2024 show more than real batteries earned; recent years are the ones to read. For CAISO, held from September 2024, the sentence says every year shown is a recent one.
- **The contract:** "market income on the uncontracted share" and "from the market after the contract ends" use the last twelve months; the average of every year held is shown beside each, labeled. Debt coverage uses the last twelve months, as before.

Session 67's page led with the average of every year held and named February 2021 in a box under the summary sentence; session 71 removed the box, because the table and the sentence under the chart now say the same thing.

## The fleet-limited estimate (session 74, for review)

Not on the page, and no live strategy changed. `warehouse/analysis/battery_fleet_limited.py` solves the same program with one more limit: in each hour, one battery's award of a product, per MW of its power, is at most the MW ERCOT procures that hour divided by the operating battery MW in ERCOT that month, and never above 1 (`solve_day(..., caps=...)`; no cap, or a cap of 1, is the page's program exactly, and a test checks it). That assumes batteries share each product in proportion to their power and between them take all of it: still generous, before batteries were the main providers.

- **Quantities:** `ercot_as_quantities`, ERCOT's DAM Ancillary Service Plan (NP4-33-CD), the plan published the day before each delivery day. ERCOT's public reports site keeps about a month of it. No keyless public source of 2018 to 2026 was found: the archive API needs a subscription key, and the yearly methodology documents give rules and adjustment tables, not the quantities. So the estimate covers 2026-09-03 to 2026-10-02 only.
- **The fleet:** `storage_buildout_monthly`, `iso:ercot`, `battery_operating_mw` of the day's month; September and October 2026 are not yet published by EIA, so August's 18,204.5 MW is used and named in the output.
- **Result, those 30 days:** with caps averaging 2.6 percent of a battery's power for regulation, 9 percent for ECRS and 13 percent for Responsive Reserve and Non-Spin, the fleet-limited battery earns 69 to 82 percent of the price-taker, the ancillary stream falling about four fifths and part of the freed power going to energy (4 hours, perfect foresight: USD 4.52 per kW against 5.92).
- **What it cannot do:** lower the years before 2024 much. ERCOT's operating battery fleet was 87 MW at the end of 2018, 107 in 2019, 218 in 2020, 821 in 2021 and 2,130 in 2022. ERCOT's 2024 methodology states that at least 2,300 MW of Responsive Reserve is procured in every hour (the 2024 quantities; earlier years' are not held). With quantities of that order, the cap is 1 for Responsive Reserve, the stream that carried 2018 to 2021, until the fleet passed them in 2023. The implausible early years come from assuming a battery is paid for reserves it is never asked to deliver, not from the fleet being too large for the market.

## California's rules, verified (session 74)

CAISO's tariff, Section 8 as of 1 May 2026 (https://www.caiso.com/documents/section-8-ancillary-services-as-of-may-1-2026.pdf):

- **Regulation Up and Down, section 8.4.1.1(g):** "Regulation capacity offered must be dispatchable on a continuous basis for at least sixty (60) minutes in the Day-Ahead Market and at least thirty (30) minutes in the Real-Time Market". The model's awards are day-ahead, so the one hour it assumed is the tariff's. Section 8.4.1.2 (Regulation Energy Management) lets a storage resource bid up to four times the energy it can deliver in fifteen minutes; the model does not use it.
- **Spinning and Non-Spinning Reserve, section 8.4.3:** "must be capable of maintaining that output or scheduled Interchange for at least thirty (30) minutes": half an hour, not the hour assumed.

Run both ways on the same days (`warehouse/analysis/battery_caiso_rules.py`), the verified rules move CAISO's yearly totals by at most USD 0.2 per kW (4 hours, perfect foresight, 2025: 91.6 assumed, 91.7 verified). The page and `battery_stack.py` still carry the assumed hour for Spinning and Non-Spinning Reserve; changing them changes the live table, so it is left for Samuel (`archive/sessions/SESSION_74_REPORT.md`, "To finish").

## The daily run

`warehouse/run_daily.sh` refreshes `ercot_as_prices` and `caiso_as_prices` (CAISO: the last days, merged into the table restored from the Redivis draft) and then runs the builder, each under `warehouse/health.py`. `iso_capacity_prices.py` runs on the first day of each month. On the GitHub runner the ERCOT price history is not present, so the builder recomputes the months the rolling price tables reach and keeps every earlier month from its own table, restored from the draft: a month is never replaced by one resting on fewer days. A row whose value did not change keeps its `retrieved_at`.

## Checks

`tests/test_session67.py`: the program equals an exhaustive search on toy days; a day worked by hand; one hour's power is never sold twice; with ancillary prices at zero it reproduces the energy-only optimum at the same resolution, and without losses it equals the seller tab's battery; every power, energy and reserve constraint holds in every solved hour; charging and discharging never share an hour; a day with a missing ancillary price or energy hour is left out and counted, and a month with no held day gets no revenue row; the 8-hour battery never earns less than the 4-hour, nor the 4-hour less than the 2-hour. The builder also checks every constraint on every day it solves and fails on a violation. `site/scripts/check-values.mjs` recomputes every number on the page from its own read of the tables.
