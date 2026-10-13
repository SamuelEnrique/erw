# What a generator earns: every number, step by step

**Session 208 (the owner's ruling of 12 October 2026): the hurdle rate's default is 12 percent**, Lazard's cost of equity ("40% equity at a 12% cost"): the NPV is to equity, after the debt payments, so equity's cost discounts it. From session 196 to 207 it was the weighted cost, 9.6 percent, which this note's worked figures below still carry as the record of those sessions; the datacenter page keeps 9.6. The debt share of this page's assets stays 60 percent, Lazard's generation structure (`lib/merchant.ts`); the battery page's is 20 since the same ruling (`battery_earns_algorithm.md`).

Energy Research Warehouse (ERW), session 183, 10 October 2026. Written for sign-off. Page: `/cost-of-power/seller`. This note is written from the code, not from the older notes: `warehouse/derived/merchant_revenue.py` (the model), `warehouse/derived/capture_price.py` (the capture price), `warehouse/derived/seller_hybrid.py` (the plant with a battery), `warehouse/derived/merchant_hubs.py` (the model at another hub, new in this session), and on the site `lib/merchant.ts`, `lib/seller2.ts`, `lib/capture.ts`, `lib/sellerhybrid.ts`, `lib/sellerhubs.ts` and `app/cost-of-power/seller/`. Where an older note and the code differ, section 9 says so. The older note, `docs/methods/cost_of_power.md` ("The seller's side", "Session 145", "Session 162"), stays as the record of why each piece was built.

Downloads, the default case hour by hour: [erw_2026_generator_hourly.csv](/seller/erw_2026_generator_hourly.csv), [the Stata do-file](/seller/erw_2026_generator_replication.do) and [its Python mirror](/seller/erw_2026_generator_replication.py). Section 8.

**The default case**, used for every example below: ERCOT, solar, 100 MW, priced at the hub average (`HB_HUBAVG`), fixed O&M USD 12.50 per kW a year, debt payments USD 7,078,769 a year. With the model's snapshot built on 4 October 2026 and the capture file built on 7 October 2026 the page shows: USD 59.85 per kW over the last twelve months (October 2025 to September 2026); a long-run average of USD 102.24 a year for 2023 to 2025 and USD 130.80 for the seven full years 2019 to 2025; a price received of USD 23.27 per MWh, USD 8.90 (27.7 percent) below the flat average of USD 32.17; debt covered 0.67 times.

## 1. The order of computation

Four builders write four sets of files. None of them runs on a schedule today: each was run by hand on the data machine, on the date its file carries (section 10, item 3).

1. **The model** (`merchant_revenue.py`, built 4 October 2026). For each grid's main hub and each asset, per 1 MW: every local month's revenue, sales, energy, capture price, flat price and hours. It writes the table `merchant_revenue_monthly` and the page's snapshot `site/data/merchant_snapshot.json`, which also holds the hub's hourly prices and Henry Hub by hour (for the peaker at the reader's heat rate) and ERCOT's stress days.
2. **The capture price** (`capture_price.py`, built 7 October 2026). For every public hub and zone, both markets and both fuels: each local month's hours, sum of prices, sum of generation and sum of price times generation. It writes `site/data/seller/capture.json`.
3. **The plant with a battery** (`seller_hybrid.py`, built 9 October 2026). For ERCOT and CAISO: twelve months of the main hub's hourly day-ahead price and of the fleet's output per MW. It writes `site/data/seller/hybrid.json` and the yearly price files of "Your plant's profile" (`site/public/seller/prices/`).
4. **The model at another hub** (`merchant_hubs.py`, new, built 10 October 2026). Step 1 again with each other hub's own price. It writes `site/data/seller/hubs/`. Section 5.

**The page, on each request**, reads those files (and, for the battery beside the plant, the battery page's table through Supabase) and computes every number it shows with the libraries named above, scaling by the reader's MW. The contract and the pasted profile compute in the browser.

**The check.** `site/scripts/check-values.mjs` recomputes every number of the model with the same library from the snapshot and compares it with what the page printed (key `mr|<inputs>|<stat>`). `check-seller.mjs` and `check-seller-deeper.mjs` do the same for the capture price, the contract, the hybrid and the profile, in a real browser.

## 2. The reader's inputs

All are in the address, each bounded and defaulted (`inputsOf` in `lib/merchant.ts`, and the page):

| Input | Default | Bounds | What it changes |
|---|---|---|---|
| `iso` | `ercot` | `ercot`, `caiso`, `nyiso`, `isone`, `spp`. MISO and PJM cannot be chosen; an address that names one opens ERCOT | the grid |
| `hub` | the grid's main hub | the grid's hubs and zones in the capture file; any other value opens the main hub | since this session, everything the model shows (section 5); before it, only the capture price and the contract |
| `asset` | `solar` | `solar`, `wind`, `battery`, `peaker` | which rows of the model; the cost defaults |
| `mw` | 100 | 1 to 5,000 | every US dollar figure is the per-MW figure times `mw`; per-kW and per-MWh figures do not move |
| `mwh` (battery) | 4 times `mw` | `mw` to 8 times `mw` | the battery is priced as the nearer of a 2-hour and a 4-hour battery (section 6, item 12) |
| `ds` | the default annual debt payment for the asset and size, rounded to a dollar | 0 to 1e10 | debt coverage only |
| `fom` | 12.5 (solar), 32.25 (wind), 11.2 or 22 (battery, 2 or 4 hours), 13.5 (peaker), USD per kW a year | 0 to 200 | debt coverage only |
| `hr`, `vom` (peaker) | 10.725 MMBtu per MWh, 4.25 USD per MWh | 6 to 16; 0 to 50 | the peaker's hours and margin, computed again from the hourly prices |
| `bmw`, `dur`, `strat` (solar and wind) | `mw`; 4 hours; perfect foresight | 1 to 5,000; 2, 4 or 8; `foresight` or `dayahead` | the battery beside the plant only |

**Session 195: `ds` and `fom` are scenario A's.** "Your plant" no longer holds annual debt payments and a fixed O&M. Scenario A of "Scenarios A and B" (section 11) holds the fixed O&M, and its annual debt payment is computed from its capital cost, debt share, interest rate and term; every coverage figure of the page reads the two from scenario A. In an address written before the session the two names are still read, once, as old names of scenario A's own assumptions (`battery_earns_algorithm.md`, section 11.1, "The block the three pages share"). Everything this note says of `ds` and `fom` below holds with "scenario A's annual debt payment for the size, rounded to a dollar" and "scenario A's fixed O&M" in their place.

Anything outside its bounds is clipped; anything unreadable takes the default. The contract's two terms (a share and a price) are not in the address: they live in the page's memory and are never sent.

**The debt default.** Annual debt payment = capital cost x 1,000 x MW x 60 percent x r / (1 - (1 + r)^-n), with r = 8 percent and n the asset's life. This is Lazard's own financing ("60% debt at an 8% interest rate", debt amortized over the economic life), on the midpoint of Lazard's capital cost range. For the default case: 1,375 x 1,000 x 100 x 0.60 = USD 82,500,000 of debt; the factor at 8 percent over 35 years is 0.0858033; the payment is USD 7,078,769 a year. Section 7 has every asset's figures.

## 3. The model, one hour at a time

Everything is per 1 MW of nameplate. Every result is linear in MW, so the page multiplies.

### 3.1 The price

The real-time price of the grid's main hub, by hour (`cost_of_power.prices_of` and `hourly`). An hour is the mean of its 15-minute prices and is written only when all four are present; an hour with a missing interval has no price and is in no figure. Tables: ERCOT `ercot_all_hub_prices_history` (the yearly history) then `iso_rtm_hub_prices` after its last hour; the other grids `iso_hub_prices_history` then `iso_rtm_hub_prices` (NYISO and ISO-NE: their zone tables). Main hubs: ERCOT hub average, CAISO SP15, NYISO New York City zone, ISO-NE Internal hub, SPP North hub.

The model's window begins at the later of the hub's first price and 1 July 2018 (EIA-930's generation by fuel begins then): ERCOT from July 2018, the other four from September 2024.

### 3.2 Solar and wind: the fleet's shape

- **Output in an hour, per MW** = the grid's whole solar (or wind) generation in that hour, from EIA-930's balancing authority workbook (columns `Adjusted SUN Gen` and `Adjusted WND Gen`; EIA's time is the hour's end, so the hour's start is one hour earlier), divided by the fuel's installed nameplate in that balancing authority in that month.
- **Installed nameplate of a month** (EIA-860M, `eia860m_operating_generators` and `eia860m_retired_generators`): the sum of nameplate MW of generators of that energy source whose operating month is on or before the month's first day and that are not retired, or retire after it. One figure a month, used for every hour of the month.
- **It is a fleet's shape, not a site's.** Every plant in the balancing authority, old and new, fixed and tracking, east and west, averaged. Curtailed energy is not in EIA-930's generation. A single plant's resource, curtailment, congestion and node price are not in it.
- **California:** EIA's hours from 1 November 2023 to 2 December 2025 sit one hour late and are read one hour earlier (`caiso_join.true_hours`, `docs/methods/eia930_caiso_break.md`).
- **Nothing is trimmed.** An hour in which the fleet produced more than the installed nameplate (EIA-860M lists some new plants after they start: 1,428 solar hours in ERCOT) is kept as it is, so the shape passes 1.0 there. An hour EIA reports below zero (a plant's own use at night: none in ERCOT, 4,197 solar hours in CAISO) is kept as it is, so it takes a little off energy and revenue. Both counts are on the page ("The fleet's hours as EIA reports them").
- **A month** of solar or wind uses the hours that hold both a price and a value of the fuel that is not blank:
  - energy per MW = the sum of output per MW;
  - revenue per MW = sales per MW = the sum of output per MW times the price;
  - capture price = sales over energy;
  - flat price = the mean price over the same hours;
  - capture rate = capture price over flat price, percent;
  - hours = the count of those hours.
- A month whose energy sums to zero or less writes no row (NYISO's solar: EIA-930 itemizes none).

### 3.3 The battery (energy only)

One optimization for each local day whose every hour holds a price (`battery_day`), for a 2-hour and a 4-hour battery:

- hourly steps; in each hour the battery charges at full power, discharges at full power, or rests (a last step that only tops up or empties is allowed);
- round trip 86 percent, split evenly: charging 1 MWh from the grid stores 0.927 MWh, and taking 1 MWh out delivers 0.927 MWh;
- each day starts empty; at most one full cycle a day (the energy taken out of the battery is at most its usable energy);
- the day's prices are all known in advance: **an upper bound**;
- solved exactly by dynamic programming over (state of charge, energy cycled).

A month's battery figures are the sums of its solved days; its `hours` field is the count of days solved. Energy alone: ancillary services are on What a battery earns, which is the page to use for a battery.

### 3.4 The gas peaker

- It runs in each hour whose price is above its cost: Henry Hub (USD per MMBtu) x heat rate + variable O&M. Strictly above.
- Henry Hub is the day's spot price (`eia_fuel_spot_prices`, `eia:henry_hub`), or the last trading day's before a day without one. The day is the grid's local day.
- Margin = the sum over run hours of price less cost. Energy = the run hours (1 MWh per MW each). "Price while running" = sales over run hours.
- At the default heat rate and variable O&M the page reads the month's row. At any other, it computes the same rule again from the snapshot's hourly prices (rounded to the cent) and Henry Hub (rounded to a tenth of a cent).
- Not modeled: start cost, minimum run, ramp limits, outages, and the gas basis (a New York or New England plant pays more than Henry Hub in winter, so its margin is overstated).

### 3.5 Months, and which count

- A month is the grid's local calendar month (America/Chicago for ERCOT and SPP, America/Los_Angeles for CAISO, America/New_York for NYISO and ISO-NE). Its hours follow the clock changes: 743 or 745 in March and November.
- **A month is held** when the hours the asset used are at least 90 percent of the month's hours (a battery: the days solved of the month's days). A month under 90 percent is shown in grey and is in no figure.
- Each figure is rounded to four decimals in the snapshot.

## 4. Every number on the page, in the order the page shows it

**Session 212 (the owner's chain prompt of 12 October 2026): the page asks the battery page's three questions**, and this section's order is the page's order until then. What the page draws now: (1) "What did it earn?": the summary sentence (4.2), the three headline numbers (4.3), the revenue chart by year (4.8), the income table (4.9, under the heading "The last twelve months beside the long-run averages"), one sentence of what the model cannot see (below, "What the model cannot see"), the two CSV downloads, and the reader's own year (4.12). (2) "Is it worth building?": scenarios A and B (section 11), with the contract's share and price as two of their assumptions (11.1; 4.10 is how the contract was computed until this session). (3) "What matters most": the sensitivity chart (11.5) with one line on how to read it. Into the CSV downloads, computed as this section says: `/cost-of-power/seller/months.csv` holds every month (4.13, 4.15: revenue, energy, the capture price and rate, and each month's coverage at scenario A's costs); `/cost-of-power/seller/tables.csv` holds, in long form (table, row, column, value, note), the capture price at every hub (4.5), by year at the hub (4.6, both markets), every public hub by year (4.7), the plant with a battery beside it (4.11, both rows), the stress days (4.16) and the fleet's hours as EIA reports them (4.17). Gone outright: the premium chart (4.4; its figures are in the download and in the headline) and "Debt coverage" (4.14; the headline's coverage and the results table's row stay, and each month's coverage is in the download). The input panel's note (4.1) and the source line (4.18) are as they were. What the page computes is `site/app/cost-of-power/seller/model.ts`, shared with the two downloads, so a download is the page's own read and arithmetic. Each download takes the page's status: in review, a visitor is answered 404.

<a id="cannot-see"></a>

**What the model cannot see** (the one sentence under the income table says the first of these; the page's hover reasons and `cost_of_power.md` say the rest):

- The plant is the grid's whole fleet by the hour, scaled to the reader's size, not one site (3.2); it is paid the hub's price, not its own node's, and no basis is modeled.
- Nothing is curtailed, no clipped energy is recovered, and no negative-price clause applies: in an hour priced below zero the fleet still sells (3.1, 3.2).
- No capacity payment, no ancillary service, no renewable energy certificate, no tax credit: energy at the hub price alone (a battery's ancillary revenue is on What a battery earns).
- The peaker has no start cost, no minimum run and no outage; it runs in every hour the price is above fuel plus variable O&M (3.4).
- A contract (11.1) is a share of the energy at a fixed price (or a toll on a share of the capacity): no shape, no settlement point, no credit.
- The scenarios repeat one year of revenue over the project's life (11.6): not a forecast and not a valuation.

"The months" below are the model's months for the asset at the hub the page is priced at (the main hub by default; section 5), `m.revenue` and so on being per MW, and `MW` the reader's size.

### 4.1 The input panel's note

Lazard's capital cost, fixed O&M and life for the asset, the debt terms, and the default annual debt payment for the reader's size (section 2). For the default case: "capital 1,375 USD/kW (1,150 to 1,600), fixed O&M 12.5 USD/kW a year (11.00 to 14.00), life 35 years. Debt: 60 percent of the capital at 8 percent over the life, USD 7.08 million a year for 100 MW."

### 4.2 The summary sentence

"Over the last twelve months, Oct 2025 to Sep 2026, a merchant solar plant in ERCOT priced at the hub average earned USD 59.85 per kW. The long-run average of 2023 to 2025 was USD 102.24 a year, and of the 7 full years held (2019 to 2025) USD 130.80. At the hub average the price it received, weighted by generation, was USD 23.27 per MWh, USD 8.90 (27.7 percent) below the flat average of USD 32.17."

- **The last twelve months** (`lastTwelve` in `lib/seller2.ts`): the newest held month whose eleven months before it are all held. Revenue per kW = the sum of the twelve months' revenue per MW, over 1,000. Default: USD 59,852.26 per MW, so 59.85.
- **The long-run average of three years:** the newest full calendar year and the two before it, when all three are full (a year is full when its twelve months are held). The sum of their 36 months' revenue over 3, over 1,000. Default: 2023, 2024 and 2025 (183.72, 59.46 and 63.54), so 102.24.
- **The average of every full year held:** the same over every full calendar year. It is said only when more than three are held. Default: 2019 to 2025 (131.46, 62.44, 217.53, 197.43, 183.72, 59.46, 63.54), so 130.80. 2021 holds Winter Storm Uri.
- **The price received** and the flat average are the capture file's, at the hub chosen (4.3). They are not the model's capture price, which is in the spans table (4.9): section 9, item 1.

### 4.3 The three headline numbers

1. **Revenue, last twelve months, USD per kW** (the peaker: "Margin over fuel"). As 4.2. The note under it names the twelve months and the hub and market the figure is priced at.
2. **Price received at the hub, USD per MWh** (solar and wind). From the capture file, for the hub chosen, in the market shown first (below), over its last twelve months:
   - price received = sum(price x generation) / sum(generation);
   - flat average = sum(price) / hours, over the same hours;
   - the difference in USD per MWh, and as a percent of the flat average.
   Default: 23.27 against 32.17: -8.90, -27.7 percent; real time, October 2025 to September 2026, 8,736 hours and 80,832,584 MWh of fleet generation.
   For a battery or a peaker this place shows the model's own "price while selling" (or "while running") against the price of every hour, from 4.9.
3. **Debt coverage, last twelve months, times.** The newest held month whose eleven before it are held: (the twelve months' revenue for the reader's size, less twelve months of fixed O&M) over the annual debt payments. Fixed O&M for a year = `fom` x 1,000 x MW. Default: (5,985,226 - 1,250,000) / 7,078,769 = 0.67. Since session 195 `fom` and the debt payments are scenario A's, and the figure is computed in the browser as A is changed (`CoverHeadline` in `SellerScenarios.tsx`); at the defaults it is the same 0.67 on the same 7,078,769.

**The capture price, exactly** (`capture_price.py`, `lib/capture.ts`):

- **The price** of a hub and market by hour: every public hub and zone price table held, read by `price_compare.read_prices`; an hour of real time is the mean of its four 15-minute prices and is held only when all four are; where a market is held two ways (15-minute and hourly) the one that holds more hours is used whole.
- **The generation** is the grid's whole fleet of the fuel by hour (`mix_profile.hours_of`): EIA-930's hourly net generation by source from 2019, and for California, from the join of 16 December 2025, CAISO's own supply by fuel. An hour counts when the fuel's own value is not blank (the mix's stricter test of the whole hour is not applied; the owner ruled this on 7 October 2026). Generation below zero weighs nothing and the hour stays in the flat average.
- **A month counts** when the hours with both a price and generation are at least 95 percent of the month's hours. The last twelve months are the newest counted month and the eleven before it, when all twelve count. A month under 95 percent is in no figure.
- **The market shown first** for a hub: real time when the hub holds twelve counted months of it (for either fuel), else day-ahead when it holds twelve, else whichever it holds. Each figure says which. On the files of 7 October 2026 every main hub but ISO-NE's shows real time.
- **Why it is a fleet figure:** two hubs of one grid differ by their prices only; the weights are the same fleet.

### 4.4 The chart: premium or discount to the flat average, by year

For the hub chosen and the market shown first, one pair of bars a calendar year (solar, wind) and one for the last twelve months: the capture file's price received less its flat average over the year's counted months, USD per MWh. A year with fewer than twelve counted months is hatched and holds its counted months only. Hover gives the price, the flat average, the difference and the months. The line under the chart links to the curtailment page's free-energy section for the same hub.

### 4.5 Capture price at every hub, last twelve months

One row for each hub and zone of the grid: the price received and its difference from the flat average, solar and wind, as 4.3, in the market shown first on the page, with the other market under it in small type. A cell with no twelve counted months is a placeholder whose hover gives the reason (how many months count, and since when the price is held). A click on a hub's name opens the page at that hub.

### 4.6 By year at the hub

The numbers of chart 4.4 as a table: for each year and the last twelve months, the price received, the flat average, the difference and the percent, solar and wind. The other market is in a fold.

### 4.7 Capture price by hub and year

Every public hub and zone of the five grids (39) by calendar year 2019 to 2026 and the last twelve months, with a switch for the fuel and the market. A cell is the capture price of the year's counted months; hover gives the simple average over the same hours, the capture ratio, the hours used of the year's hours, the months counted and the source tables. MISO and PJM are rows of words.

### 4.8 The chart: revenue by year, USD per kW

For each calendar year, the sum of the held months' revenue per MW, over 1,000. A year with fewer than twelve held months is hatched and holds those months only (default: 2018 with six months, 2026 with nine). Default: 45.27 (2018, six months), 131.46, 62.44, 217.53, 197.43, 183.72, 59.46, 63.54, and 47.04 (2026, nine months).

### 4.9 The last twelve months beside the long-run averages

Three spans (the last twelve months, the last three full years, every full year held) by five rows. For a span of months, with Y the number of years it covers (1, 3, or the count of full years):

| Row | Formula | Default: twelve months, three years, every year |
|---|---|---|
| Revenue, USD per kW | sum of revenue per MW / Y / 1,000 | 59.85, 102.24, 130.80 |
| Energy sold, MWh per MW | sum of energy per MW / Y | 2,580, 2,600, 2,422 |
| Capture price, USD per MWh | sum of sales / sum of energy | 23.20, 39.32, 54.00 |
| Price of every hour, USD per MWh | the mean of the months' flat prices, each month weighing the same | 32.10, 35.78, 54.90 |
| Capture rate, percent | capture price over that, x 100 | 72, 110, 98 |

The capture price here is the model's: the fleet's output per MW of nameplate, at the hub the page is priced at. It differs a little from the headline's price received (23.20 against 23.27): section 9, item 1.

### 4.10 With your contract (computed in the browser, never sent)

**Session 212: this panel and section are gone.** The contract is two assumptions of a scenario (11.1, the battery page's form since session 208): a share and a price, both 0 by default, in the address with the other assumptions, read by the scenario's coverage, NPV, IRR and sensitivity chart and by the headline's coverage. `SellerContract.tsx` stays on disk, undrawn. What follows is how the panel computed until then.

For solar and wind. The reader types a share of the energy (percent) and a price (USD per MWh).

- **Energy** = the model's energy per MW over the capture price's twelve months (every one of them must be held in the model), times MW.
- **The market's price** = the price received at the hub chosen (4.3).
- Contracted energy = share x energy x contract price. Market revenue on the rest = (1 - share) x energy x market price. Revenue with the contract = the two added. Revenue without it = energy x market price. The difference = with less without. Each total is also shown per MWh.
- The share is held between 0 and 100. Nothing is computed until both terms are valid numbers.
- A peaker and a battery have no contract here (a peaker runs only above its cost; a battery buys as well as sells). The battery page has its own.
- Not in it: settlement point and basis, shape, curtailment and negative-price clauses, credit, renewable energy certificates.

### 4.11 With a battery beside it (ERCOT and CAISO; solar and wind)

Always priced at the grid's main hub, whatever hub is chosen; the page says so when another hub is chosen. Two rows of four figures, USD for the reader's sizes.

**Row 1, energy at day-ahead prices** (`lib/sellerhybrid.ts`, on `hybrid.json`). Twelve months of local days; a day is solved only when every hour of its day-ahead price and of the fleet's output is held; a month counts with 90 percent of its days; the twelve are the newest counted month and the eleven before it. Default: 364 days, 1 left out.

- **Plant alone:** the sum over the days' hours of price x output. The output is the model's shape (3.2) times MW, with an hour below zero set to zero. Default: USD 6,328,531.
- **Battery alone:** the program below with no plant and a limit of its own. Default (100 MW, 4 hours): USD 5,388,107.
- **Co-optimized pair:** for each day, with price p, plant output g, battery power P, energy E = P x hours, and limit L:
  - maximize the sum of p x (g + discharge - charge);
  - charge between 0 and min(P, L + g); discharge between 0 and min(P, L - g), and none in an hour priced below zero;
  - state of charge = the running sum of 0.927 x charge less discharge / 0.927, between 0 and E, from empty each day;
  - at most one full cycle a day (the sum of discharge / 0.927 is at most E).
  L is the plant's capacity, or its highest hour of the twelve months when that is higher (default: 107.495 MW for a 100 MW plant, because the fleet's shape passes 1.0). The plant sells every hour, so the pair is the plant plus what the battery adds, and never less than the plant. Default: USD 11,637,889.
- **Added, not co-optimized: upper bound.** Plant alone plus battery alone. The pair is the same two assets under one more limit, so it is never above this figure. Default: USD 11,716,638; the difference, USD 78,749, is what sharing the interconnection costs.
- **The day's prices are known when the schedule is made:** an upper bound for a schedule made the day before. Energy only: no ancillary service, no capacity payment, no tax credit rule, no degradation, no outage.
- Under the table: the share of the battery's charging energy that the plant's own output covered in the same hour (default 60 percent: 94,554 of 157,005 MWh). At one hub price a MWh from the plant and a MWh from the grid cost the same, so this is an account, not a decision.

**Row 2, plant at real-time prices, battery with ancillary services** (session 145's figures, kept):

- **Plant alone:** the model's revenue (main hub, real time) over the battery page's last twelve months, times MW.
- **Battery alone:** the battery page's own last-twelve-months figure for that size, duration and strategy, read from `battery_stack_monthly` with the battery page's own query. Energy and ancillary services.
- **Co-optimized pair:** not modeled.
- **Added: upper bound.** The two added. It is on other prices than row 1 and holds ancillary revenue row 1 does not, so it is not a bound of row 1's pair by arithmetic; where row 1's pair comes out above it, the page marks it.

Other grids read "not modeled for this grid".

### 4.12 Your plant's profile (computed in the browser, never sent)

The reader pastes 8,760 hourly values (8,784 in a leap year) of a plant's output. Revenue = the sum of value x the main hub's day-ahead price of that hour of the year chosen, over the hours that hold a price; capture price = revenue over the energy of those hours; simple average = the mean price of those hours. With a battery (ERCOT and CAISO): 4.11's program on the days of 24 hours, local standard time, whose every hour holds a price, with the profile's highest hour as the limit. A wrong count, a gap, a value below zero or a value that is not a number is refused; nothing is repaired. Always the main hub.

### 4.13 Month by month

For the reader's size, over the held months (default: 99 months, July 2018 to September 2026):

- **The median month** and **the 10th-percentile month**: the held months sorted by revenue (ties by month); the month at position ceiling(0.5 x n) and ceiling(0.1 x n), counted from 1. Default: USD 550,485 (September 2018) and USD 240,213 (December 2020).
- **The year's average:** twelve times the mean held month. Default: USD 12,216,826.
- **The worst three months:** the three lowest. Default: February 2024 (USD 139,299), February 2026 (148,707), February 2023 (175,324).
- **The chart:** one bar a month; the dashed line is one twelfth of the annual debt payments; a month below it is in the accent color; a month under 90 percent held is grey.

### 4.14 Debt coverage

- **Monthly coverage** = (the month's revenue less one twelfth of a year's fixed O&M) over one twelfth of the annual debt payments. Counts of held months under 1.0 and under 1.25. Default: 62 and 71 of 99.
- **Trailing twelve months:** at each held month whose eleven before it are held, (the twelve months' revenue less a year's fixed O&M) over the annual debt payments. The newest, the lowest, and the counts of windows under 1.0 and 1.25. Default: 0.67 at September 2026; lowest 0.65; 33 and 36 of 88 windows.
- The chart is that series, with lines at 1.0 and 1.25.
- With debt payments of zero, no coverage is computed.

### 4.15 Every month (folded)

For each month: revenue, energy, capture price, flat price, capture rate, monthly coverage, and the share of the month held. A month not held is muted.

### 4.16 Stress days (folded, ERCOT only)

For Winter Storm Uri (7 to 24 February 2021), Winter Storm Elliott (19 to 29 December 2022) and the summer 2023 heat (1 August to 10 September 2023): the days are those of `event_window_daily` for the hub average, each marked as inside the event's window or as a baseline day (the same days or weekdays of earlier years).

- A day's revenue: solar and wind, the sum over the day's hours of output x price; battery, the day's optimum; peaker, the rule of 3.4 over the day's hours.
- Per day = the mean over the window's days; the window = their sum; a normal week = seven times the mean of the baseline days; the best day = the highest day of the window.
- Default: Uri USD 12,382,220 over 18 days (USD 687,901 a day; a normal week USD 61,313; best day 17 February 2021, USD 4,060,021); Elliott USD 135,772 over 11 days; the 2023 heat USD 10,557,599 over 41 days.
- The other grids' prices begin after these events, so they read "ERCOT only".

### 4.17 The fleet's hours as EIA reports them (folded)

The counts of 3.2: hours above installed nameplate and hours below zero, solar and wind, for the grid.

### 4.18 The source line

The tables read, the EIA-930 workbook, the dates the snapshot, the capture file and (at another hub) the hub's model were built, the cost source, and the three downloads of section 8.

## 5. Another hub or zone (new in session 183)

**What was wrong.** Until this session, choosing another hub changed the capture price (4.3 to 4.6) and the contract (4.10) and nothing else: revenue, the months, debt coverage and the stress days stayed at the main hub. One page stood on two footings.

**What is true now.** The hub chosen prices everything the model shows: 4.2, 4.3, 4.8, 4.9, 4.10 (its energy), 4.13, 4.14, 4.15 and 4.16. The page writes the hub and the market beside the headline, in the sentence, under the year chart and in the months' title.

- **How.** `merchant_hubs.py` runs the model's own function (`merchant_revenue.build_iso`) with one thing changed: the hub's hourly price in place of the main hub's. The fleet's shape, the nameplate, the battery optimization, the peaker rule, Henry Hub, the 90 percent rule and the rounding are the same code. The page turns a hub's file into the record the model's library reads (`lib/sellerhubs.ts`), so every figure is computed by the same functions.
- **Which price.** The hub's prices are read as the capture price reads them (4.3), from 1 July 2018 where held.
- **Which market.** One market for each hub: the market the page shows the hub's capture price in (4.3). So the revenue and the capture price beside it are on one market, and the page says which ("real-time prices" or "day-ahead prices"). Day-ahead is used for ERCOT's four load zones that hold no real-time price (AEN, CPS, LCRA, RAYBN) and for SPP's South hub.
- **The main hub is unchanged.** It keeps the page's snapshot, so no number of a default page moved. As a check, the new builder is also run at each main hub at real-time prices and set beside the snapshot month by month; the result is in `site/data/seller/hubs/index.json` (`check`) and section 5.1.
- **What stays at the main hub, and says so:** the battery beside the plant (4.11: the battery page's model and the day-ahead pair are built for the main hub) and the pasted profile (4.12).
- **A hub with few months.** ISO-NE's zones hold public prices from 26 August 2026 only, so they show one held month and no twelve months. Nothing is filled.
- **A hub whose model is missing** (the capture file rebuilt and the hub files not): the page says "The model holds no month at this hub" and shows the main hub's figures under the main hub's name. A figure never stands under a hub it was not priced at.
- **The check keys** of a page priced at another hub carry the hub and its market (`mr|...&hub=HB_WEST&market=rt|...`), so no check can read them as the main hub's.

### 5.1 The figures

Built on 10 October 2026 from the tables of that day: 34 hubs and zones of five grids (ERCOT 13, CAISO 2, NYISO 10, ISO-NE 8, SPP 1) in 34 files of 12.6 MB together. 26 of them hold twelve months in a row.

**The check at the main hubs** (the new builder at real-time prices against the snapshot of 4 October; a month is compared when both hold the same hours of it):

| Grid | Months compared | Solar, wind, both batteries | Peaker |
|---|---|---|---|
| ERCOT | 99 | equal to the last decimal the snapshot holds | September 2026 differs by 0.19 percent; every other month equal |
| CAISO | 25 | equal | September 2026 differs by 0.41 percent |
| ISO-NE | 20 (batteries 18) | equal | equal |
| SPP | 25 | equal | September 2026 differs by 0.33 percent |
| NYISO | 6 compared, 17 not | within 0.01 percent | within 0.5 percent |

- **The peaker's September 2026:** Henry Hub's prices of 30 September to 6 October arrived after the snapshot was built, which had carried 29 September's price forward. A newer fact, not another rule. ISO-NE's September is not held, so it is not compared.
- **New York City:** the snapshot reads its real-time price from the hub history (15-minute prices, from September 2024); the capture price and this builder read the zone history (NYISO's own hourly figure, from 2019), which holds more hours. The two tables hold the same hours in 6 months and those agree; in 17 they hold different hours and are not compared. The page keeps the snapshot at New York City, so this difference is on no page; it is why section 10, item 16 recommends rebuilding the snapshot from the histories.
- **One price.** A month's flat price does not depend on the weights. In 3,708 hub-months where the model and the capture file use the same hours, the model's flat price equals the capture file's for that hub and market to USD 0.0001 per MWh (`site/scripts/test-seller-hubs.mjs`).
- **The two capture prices at a hub** (the model's and the capture file's, edge case 7) differ by under 1 percent in 40 of the 42 cases (hub and fuel) that hold the same twelve months in both; the other two are wind at NP15 (1.2 percent) and solar at SPP's South hub (4.7 percent; at SPP's main hub, the North hub, it is 5.5 percent), where the solar fleet grew fastest within the year.

**ERCOT, the default sizes, October 2025 to September 2026** (revenue in USD per kW; coverage of the default debt, times):

| Hub or zone | Market | Solar revenue | Solar coverage | Wind revenue | Wind coverage |
|---|---|---|---|---|---|
| Hub average (the main hub) | real time | 59.85 | 0.67 | 83.57 | 0.46 |
| Bus average | real time | 60.08 | 0.67 | 84.79 | 0.47 |
| Houston hub | real time | 69.99 | 0.81 | 89.97 | 0.52 |
| North hub | real time | 59.28 | 0.66 | 85.66 | 0.48 |
| South hub | real time | 62.62 | 0.71 | 86.41 | 0.48 |
| West hub | real time | 47.51 | 0.49 | 72.23 | 0.36 |
| Houston load zone | real time | 72.48 | 0.85 | 91.86 | 0.53 |
| North load zone | real time | 64.13 | 0.73 | 88.62 | 0.50 |
| South load zone | real time | 70.97 | 0.83 | 88.48 | 0.50 |
| West load zone | real time | 51.44 | 0.55 | 86.99 | 0.49 |
| AEN load zone | day-ahead | 80.13 | 0.96 | 103.23 | 0.63 |
| CPS load zone | day-ahead | 74.02 | 0.87 | 103.17 | 0.63 |
| LCRA load zone | day-ahead | 81.53 | 0.98 | 102.56 | 0.63 |
| RAYBN load zone | day-ahead | 66.57 | 0.76 | 96.28 | 0.57 |

Before this session every row of that table showed the first row's revenue and coverage. A day-ahead row is not comparable with a real-time row: the page says which market each is.

Elsewhere: CAISO solar earns USD 28.45 per kW at SP15 and 49.43 at NP15; SPP solar 101.62 at the North hub (real time) and 101.18 at the South hub (day-ahead); a 100 MW, 4-hour battery selling energy alone in ERCOT earns USD 58.53 per kW at the hub average and 70.75 at the West hub; a gas peaker 48.15 and 59.58.

**A gap found on the way.** The zone history holds 288 of the 744 hours of July 2026 of New York's real-time price, at every zone. So at every New York zone the last twelve months in real time are July 2025 to June 2026, in the capture price (as before this session) and in the model. New York City's default page runs to September 2026 because its snapshot reads another table. Section 10, item 19.

## 6. Edge cases, as the code handles them

1. **An hour with a missing 15-minute price** has no hourly price and is in no figure. It lowers the month's hours; under 90 percent the month is not held.
2. **A month enters the last twelve months before it ends.** A month is held at 90 percent of its hours, so a 31-day month counts from its 28th day, with its last days missing and its revenue low by them. Today the snapshot is built by hand and its newest held month (September 2026) is whole. If the builder is ever scheduled, a headline would move on the 28th. The same holds for the capture price at 95 percent (the 30th day of 31). Section 10, item 5.
3. **The first month.** ERCOT's model begins at 1 July 2018 00:00 UTC, which is 30 June in Texas: June 2018 holds five hours, is not held, and is in no figure.
4. **Clock changes.** Days of 23 and 25 hours are solved as they are (the battery, the pair). The pasted profile is in local standard time all year and its days are 24 hours.
5. **Output above nameplate and below zero** are kept in the model (3.2). In the capture price and in the pair of 4.11, an hour below zero is set to zero. So in California the model's solar energy is slightly lower than the capture file's weights.
6. **The 90 percent and the 95 percent.** The model holds a month at 90 percent of its hours; the capture price counts it at 95 percent. A month with 92 percent is in the revenue and not in the price received. On the files of today no month of the default case falls between the two.
7. **Two fleets of weights.** The model weighs an hour by output per MW of that month's nameplate; the capture price weighs by generation itself. A fleet that grows within the span weighs its later months more in the capture price. Default: 23.20 against 23.27.
8. **"Price of every hour" in the spans table** is the mean of the months' flat prices, each month weighing the same, not each hour (32.10 against the capture file's 32.17 for the same twelve months). Section 10, item 6.
9. **The peaker at the default and at another heat rate** are computed from different precision: the month's row (full precision) and the hourly arrays (prices to the cent). An hour priced within half a cent of the cost can fall on the other side. The difference is a few dollars a month per MW.
10. **Henry Hub on a weekend or holiday** is the last trading day's price. An hour with no Henry Hub at all (before the series begins) is not in the peaker.
11. **The peaker runs strictly above its cost.** At a price equal to cost it does not run.
12. **A battery longer than four hours** on this page is priced as a 4-hour battery: the model holds two durations, and `mwh / mw` at or under 3 takes the 2-hour figures, above 3 the 4-hour figures. The field accepts up to 8 hours, so a 100 MW, 800 MWh battery shows the 4-hour battery's revenue with the 4-hour battery's cost defaults. The panel's note says "Priced as a 4-hour battery". Section 10, item 7.
13. **The battery's month** is held by days: 90 percent of the month's days solved.
14. **New York's solar** has no figure anywhere: EIA-930 itemizes none.
15. **MISO** is in the snapshot (built before the pause was applied to this page) and is shown nowhere; an address that names it opens ERCOT.
16. **The median and the 10th percentile** are real months (nearest rank), not interpolated values.
17. **The contract's energy** needs all twelve of the capture price's months held in the model; otherwise the section reads "not held yet" with the reason.
18. **The battery beside the plant, row 2,** needs the plant's months held over the battery page's twelve months, which can differ from the plant's own last twelve months when one of the two tables is newer.
19. **Files built on different days.** The snapshot (4 October), the capture file (7 October), the hybrid file (9 October) and the hub files (10 October) were built from the tables of their day. Their whole months agree; their newest partial month differs and is in no headline.
20. **A price below zero.** Solar and wind sell every hour, also at a negative price: nothing is curtailed in the model. The pair's battery does not discharge at a negative price.

## 7. Assumptions, their defaults and sources

| Assumption | Default | Source |
|---|---|---|
| Capital cost, USD per kW | solar 1,375; wind 2,100; battery 610 (2 hours) and 1,110 (4 hours); peaker 1,300 | Lazard, Levelized Cost of Energy+, June 2025: the midpoint of each range (1,150 to 1,600; 1,900 to 2,300; 340 to 880; 620 to 1,600; 1,150 to 1,450) |
| Fixed O&M, USD per kW a year | 12.5; 32.25; 11.2 and 22; 13.5 | the same, midpoints (11.00 to 14.00; 24.50 to 40.00; 3.0 to 8.2 and 3.0 to 8.0 per kWh times the hours; 10.00 to 17.00) |
| Life, years | 35; 30; 20; 30 | the same |
| Debt | 60 percent of capital at 8 percent, level payments over the life | Lazard's own financing |
| Annual debt payment, 100 MW | solar USD 7,078,769; wind 11,192,257; battery 3,727,791 (2 hours) and 6,783,357 (4 hours); peaker 6,928,540 | computed (section 2) |
| Battery round trip | 86 percent | Lazard LCOS v10.0, the low end of 92 to 86 percent |
| Battery cycles | at most one full cycle a day, each day from empty | the battery page's rule |
| Peaker heat rate and variable O&M | 10.725 MMBtu per MWh; 4.25 USD per MWh | Lazard, gas peaking new build, midpoints (10,275 to 11,175 Btu per kWh; 3.50 to 5.00) |
| Gas price | Henry Hub spot, no basis | EIA |
| A month held | 90 percent of its hours (model); 95 percent (capture price); 90 percent of its days (battery, pair) | the ERW's rules |
| Merchant only | no contract, hedge, capacity payment or ancillary service; no tax, no degradation, no outage, no curtailment | by construction; the contract of 4.10 is the one exception |

The reader can set the size, the debt payments, fixed O&M, the peaker's heat rate and variable O&M, the battery's size and duration, and the contract. In the "Your plant" panel the capital cost, debt share, rate and life are not inputs: they only set the default debt payment, which is an input. They are inputs of the two scenarios (section 11), which compute their own debt payment. Since session 195 the debt payments and fixed O&M are not inputs of "Your plant" either: scenario A holds them, and sets the headline.

## 8. The replication

**The files** (`site/public/seller/`, linked from the page's source line):

- `erw_2026_generator_hourly.csv`: the default case hour by hour. 72,384 hours from 1 July 2018 to the snapshot's last hour (3 October 2026), 100 local months, 4.4 MB, 16 provenance lines. Columns: `hour_utc`, `local_day`, `local_month`, `price_usd_mwh` (the hub average's real-time price of the hour), `solar_mwh` (the fleet's generation, EIA-930), `nameplate_mw` (the month's installed nameplate, EIA-860M), `in_last_twelve`. `-99999` in `solar_mwh` marks the 72 hours EIA left blank.
- `erw_2026_generator_replication.do`: the Stata do-file, to your rules (no line continuation; one empty line between commands outside loops and none inside; every variable destrung with force; the sentinel recoded variable by variable; real numbers as doubles). **It has never been run: Stata is not on the data machine.**
- `erw_2026_generator_replication.py`: its Python mirror, standard library only, step for step, printing the same 29 lines.

**One price column and one generation column are enough.** For ERCOT's hub average the capture price's hourly price and generation equal the model's on every one of the 67,943 hours it uses, and both last twelve months are October 2025 to September 2026. So the two capture prices of section 9, item 1 differ by the weights alone, and one CSV rebuilds both the model's numbers and the price received. The exporter (`warehouse/derived/generator_hourly_export.py`) reads the hours with the two builders' own functions and refuses to write unless the rows, as written, give the snapshot's months (100 of 100, to half a unit of its fourth decimal) and the capture file's months (94 of 94, to its rounding).

**What the do-file rebuilds, and what the page shows:**

| Number | Page | From the CSV |
|---|---|---|
| Revenue, last twelve months, USD per kW | 59.85 | 59.85 |
| Long-run average, 2023 to 2025; every full year, 2019 to 2025 | 102.24; 130.80 | 102.24; 130.80 |
| Price received; flat average; difference; percent | 23.27; 32.17; -8.90; -27.7 | the same (8,736 hours) |
| Annual debt payments; coverage, last twelve months | 7,078,769; 0.67 | the same |
| Months held; median month; 10th-percentile month | 99; 550,484.85 (September 2018); 240,213.49 (December 2020) | the same, to the cent |
| The year's average; the worst three months | 12,216,826.39; 139,298.97, 148,707.24, 175,323.73 | the same, to the cent |
| Months under 1.0 and 1.25; windows; lowest; windows under 1.0 and 1.25 | 62 and 71; 88; 0.65; 33 and 36 | the same |

The largest difference before rounding is 0.0000006 USD per MWh in the flat average: the page adds twelve month sums each rounded to the cent, the CSV adds the 8,736 hours.

**Not in the do-file:** the other rows of the spans table, the capture price by year and at other hubs, the contract, the battery beside the plant and the stress days. The CSV holds what the first two need.

**When the files go stale.** The CSV is written once. When the snapshot or the capture file is rebuilt, `tests/test_session183_replication.py` fails on the data machine, which is the alarm: run `python warehouse/derived/generator_hourly_export.py` and commit the CSV.

## 9. Where the notes and the code differ

1. **Two capture prices on one page.** The headline's "price received" (4.3) is the capture file's; the spans table's "capture price" (4.9) is the model's. `cost_of_power.md` says so; the page face does not. They differ by the weights (edge case 7): 23.27 and 23.20 at the default.
2. `cost_of_power.md` ("The seller's side") says the other grids are held "from 2025-09". The snapshot holds them from September 2024 (26 months); the note's own later section says September 2024.
3. `cost_of_power.md` says day-ahead is shown first for New York City. Since session 149's zone history, New York City holds real time from 2019 and is shown in real time. ISO-NE's Internal hub is still day-ahead first.
4. `cost_of_power.md` ("Session 145", decision 5) says the hybrid is at the main hub whatever hub is chosen. True, and now said on the page when another hub is chosen.
5. `merchant_revenue.py`'s header says the battery is "full power or nothing". The code allows a partial last step (charge up to full, discharge down to empty or to the cycle limit).
6. No note said a battery longer than four hours is priced as a 4-hour battery (edge case 12).
7. No note said the spans table's "price of every hour" weighs months, not hours (edge case 8).
8. No note said negative output is kept in the model and set to zero in the capture price and the pair (edge case 5).
9. The page's words and the code agree.

## 10. What is left, for your ruling

From this tool's reports (145, 149, 162) and from this session. Each with a recommendation.

| # | Item | From | State and recommendation |
|---|---|---|---|
| 1 | The hours rule for the capture price | 145 | Closed: you ruled on 7 October 2026 that the page keeps it |
| 2 | SPP South and New York's zones had no year | 145 | Closed by session 149 (day-ahead and real time from 2019) |
| 3 | No builder of this page is scheduled: the snapshot (4 October), the capture file, the hybrid file and now the hub files age | 145, 149, 162 | Open. `warehouse/run_data_machine.sh` (session 149) holds the capture step and is registered nowhere. Recommend: add the snapshot, the hybrid and the hub files to that run, monthly (the hub files are 11 MB and should not be rewritten daily), once you register it |
| 4 | ISO-NE's zones hold weeks, not years | 145, 149 | Closed as ruled: ISO-NE's zone history is internal. The page shows what the public tables hold |
| 5 | A month enters the last twelve months at 90 percent (95 for the capture price) | new | Open. Recommend whole months only for the headline, as recommended for the battery page in session 178. Moves nothing today |
| 6 | "Price of every hour" weighs months, not hours | new | Open. Recommend weighing hours (32.10 becomes about 32.17 at the default). Moves one row of one table |
| 7 | A battery longer than four hours is priced as four | new | Open. Recommend limiting the field to 4 hours and pointing to What a battery earns, which holds 8 hours |
| 8 | Two capture prices on one page (9.1) | 145 | Open. Recommend one: build the capture file's weights into the model's months, or label the spans row "model". A wording change at least |
| 9 | The two rows of the hybrid table, and the label "upper bound" on row 2 | 162 | Open, your word. Recommend keeping both rows; row 2's label is true of its own two parts only, and the hover says so |
| 10 | The 17 yearly price files are public addresses while the page is in review | 162 | Open, your word. Recommend leaving them: public day-ahead prices of five main hubs, from public tables |
| 11 | The hybrid is a table, with no chart | 162 | Open. Recommend one chart of a day (prices, plant, charge, discharge) with a day picker; a session of its own |
| 12 | The pair is built for ERCOT and CAISO only | 162 | Open. Row 1 is energy only and needs no reserve prices, so it can be built for NYISO, ISO-NE and SPP. Recommend doing it; row 2 stays ERCOT and CAISO |
| 13 | The pair and the pasted profile are priced at the main hub | 145, 162 | Open. Recommend building both for the hub chosen when item 12 is done; it needs each hub's day-ahead hours in a file |
| 14 | The page on a phone | 162 | Closed this session: looked at 390 px (`check-seller-face.mjs`) |
| 15 | `docs/platform-tools.md` and older status documents | 145, 162 | Closed this session where they named the old address |
| 16 | The model at the main hub for New York begins in September 2024, while its zones' models begin in 2019 | new | Open. The zone history of session 149 holds New York City from 2019. Recommend rebuilding the snapshot's four short grids from the histories; it adds years to their default pages, so their long-run averages appear |
| 17 | ISO-NE's Internal hub: revenue in real time, price received in day-ahead | new | Open. Its real-time months do not all count at 95 percent. Recommend showing both in one market when item 16 is done |
| 18 | The do-file has never been run | new | Open. Stata is not on the data machine. Please run it once |
| 19 | New York's real-time zone history holds 288 of the 744 hours of July 2026 | new | Open. New York's price received, at every zone and at New York City, therefore ends in June 2026, while New York City's revenue (the snapshot, another table) ends in September 2026; each figure says its months. Filling the 19 days is a pull from NYISO: your approval, after your ruling on NYISO's terms (session 149) |
| 20 | `check-seller.mjs` read the battery page as a visitor, and expected the main hub's revenue at another hub | 166, 145 | Closed this session: it reads the battery page in the internal view (in review since session 166) and expects the hub's own model |

## 11. Scenarios A and B (session 186)

The section "Scenarios A and B" of the page, after "With your contract": eight assumptions, two scenarios on the same eight rows, and a sensitivity chart, as session 179 built them for the battery (`battery_earns_algorithm.md`, section 11.1). It is computed in the browser by `site/lib/seller/finance.ts` (pure arithmetic, no request) from figures the page already shows. Nothing above or below the section changed: an address with none of the parameters below shows the page as it was, with this block at its defaults.

**Session 195: the block is the one the three decision pages share**, described once in `battery_earns_algorithm.md`, section 11.1, "The block the three pages share": the panel, the two columns, the row in words, the chart, where the scenarios are held, the old names, and that nothing is sent. What it means on this page:

- **Scenario A sets the headline.** The third headline number, debt coverage over the last twelve months, is computed in the browser from scenario A's fixed O&M and A's annual debt payment for the size (`round(capex x 1000 x share x crf(rate, n) x MW)`, the page's own multiplication, so the default is 7,078,769 to the dollar). The first two headline numbers, revenue and the price received, do not depend on any of the eight assumptions, so they are scenario A's rows as they stand.
- **The sections that used the two fields follow A as well**: the line of one month of debt payments in "Month by month" (4.13), the whole of "Debt coverage" (4.14) and the coverage column of "Every month" (4.15), each with the check key it always had, written with A's `ds` and `fom`.
- **The sentence under the table states scenario A**, whichever scenario is in view.
- **Default case, before and after:** revenue 59.85 USD per kW, price received 23.27 USD per MWh, coverage 0.67 times on debt payments of USD 7,078,769. No number moved.
- **Checks.** `site/scripts/check-decisions-face.mjs`; `site/scripts/check-seller-scenarios.mjs`, part 8b; `tests/test_session195.py`.

### 11.1 The eight assumptions and their defaults

**Session 212: ten.** The contract's share and price are the ninth and tenth, both 0 by default, so the default is fully merchant and every figure at a share of 0 is what it was. For solar and wind the contract is a share of the energy at a price per MWh; for a battery and a gas peaker, whose energy depends on the price, a toll on a share of the capacity in USD per kW-month (the battery page's form). The contract runs for the debt's years and pays its price flat: income in year t is `contract + (1 - cshare) x R_t` while `t <= n`, and `R_t` after, where `contract = cshare x E x cprice` for an energy contract and `cshare x cprice x 12` for a toll (`E` the last twelve months' energy, MWh per kW, 11.2). Coverage is `(contract + (1 - cshare) x R - fom) / debt`. The breakeven contract price row (11.3) does not read the contract: it is the price for the whole of the energy. The sensitivity chart draws the two contract rows only when the scenario holds a contract (as session 211 on the battery). `site/lib/seller/finance.ts` (`Contract`, `contractYear`, `merchantShare`, `incomeInYear`); `site/scripts/test-seller-finance.mjs`, the session 212 block.

| Assumption | Default | Source of the default | Bounds | Address (A, B) |
|---|---|---|---|---|
| Contract share, percent of the energy (a battery, a peaker: of the capacity) | 0 | no contract: fully merchant | 0 to 100 | `an`, `bn` |
| Contract price, USD per MWh (a battery, a peaker: USD per kW-month) | 0 | the reader's own term; no published price is held | 0 to 1,000 | `ap`, `bp` |

| Assumption | Default | Source of the default | Bounds | Address (A, B) |
|---|---|---|---|---|
| Capital cost, USD per kW | solar 1,375; wind 2,100; battery 610 (2 hours) and 1,110 (4 hours); peaker 1,300 | Lazard, Levelized Cost of Energy+, June 2025, the midpoint of each range (section 7) | 0 to 10,000 | `ac`, `bc` |
| Debt share, percent | 60 | Lazard: "60% debt at an 8% interest rate" (`cost_of_power.md`) | 0 to 100 | `as`, `bs` |
| Interest rate, percent a year | 8 | the same | 0 to 30 | `ar`, `br` |
| Term of the debt, years | the asset's life: 35; 30; 20; 30 | Lazard: "Economic life sets debt amortization schedule" | 1 to 40, whole | `at`, `bt` |
| Fixed O&M, USD per kW a year | 12.5; 32.25; 11.2 and 22; 13.5 | Lazard, the midpoint of each range (section 7) | 0 to 500 | `af`, `bf` |
| Degradation, percent a year | 0; a battery 2.6 | solar, wind and a gas peaker: none held, the model has no loss of output with age and the repository cites no rate. A battery: Lazard, Levelized Cost of Energy+, June 2025, LCOS v10.0, battery degradation of 2.6% per annum (session 196) | 0 to 20 | `ad`, `bd` |
| Project life, years | 35; 30; 20; 30 | Lazard's life of each asset (section 7) | 1 to 40, whole | `al`, `bl` |
| Hurdle rate, percent a year | 9.6 | Lazard, the same report: "60% debt at an 8% interest rate and 40% equity at a 12% cost"; the default is that weighted cost, 0.6 x 8 + 0.4 x 12 (session 196; until then 8, none held) | 0 to 40 | `ah`, `bh` |

- **The hurdle rate and a battery's degradation have a cited default since session 196** (the owner's ruling of 11 October 2026), as on the battery page (`battery_earns_algorithm.md`, section 11.1). Until then both had none and were to be confirmed by Samuel (sessions 179 and 186). The hurdle rate's default is Lazard's weighted cost, 9.6 percent, from "60% debt at an 8% interest rate and 40% equity at a 12% cost". A battery's degradation default is Lazard's 2.6 percent a year. **Solar, wind and a gas peaker still have no cited degradation rate, and the page says so**: their default stays none. What moved at the defaults: NPV only (solar USD -82.31 million to -78.43 million; wind -152.23 to -143.09; a 4-hour battery -75.13 to -79.57; a gas peaker -91.00 to -85.78). No headline number moved.
- **The address.** Each scenario's assumptions are two-letter parameters, the scenario's letter then the assumption's (`c` capital cost, `s` debt share, `r` interest rate, `t` term, `f` fixed O&M, `d` degradation, `l` life, `h` hurdle rate); `v=b` puts B in view. A parameter is written only when its value differs from the default, so no parameter means the defaults. The page's own parameters (section 2) work as before, but for `ds` and `fom`, which since session 195 are old names of scenario A's. A value outside its bounds is clipped; one that cannot be read takes the default. The address is rewritten in place (`history.replaceState`): a change sends no request. Show, the grid, the asset and "Reset the costs" carry the scenarios; a change of asset, or of a battery's duration, drops a typed capital cost, fixed O&M, term and life, whose defaults are the asset's. The links of the capture table open a hub afresh, as before, without the scenarios.
- **Scenario A sets the headline (session 195).** Until session 195 the scenarios did not read the "Your plant" panel's fixed O&M and annual debt payments, which set the headline coverage and the months' coverage: one idea in two places. Those two fields are gone. A scenario's fixed O&M is its own, and its debt payment is computed from its capital cost, debt share, interest rate and term; the page's coverage figures are scenario A's (0.67 times in the default case, before and after).
- **The scenarios do not read the contract typed in "Your contract".** Its terms stay on the reader's device and are never in the address, so a shared link could not carry them. (Until session 212; the contract is two of the scenarios' own assumptions since, in the address with the rest.)

### 11.2 What a scenario reads from the page

None of the eight assumptions is inside the model, so what a scenario reads is the page's own and is the same in A and B (the four rows of revenue, the capture price, the worst month and the battery beside it, and the energy the contract price is computed on):

- `R`: revenue of the last twelve months, USD per kW, at the hub and in the market the page is priced at (section 4.3, section 5). A gas peaker's is its margin over fuel, at the reader's heat rate and variable O&M.
- `E`: the energy of the same twelve months, MWh per kW (section 4.9's "Energy sold, MWh per MW", divided by 1,000).
- The capture price and its ratio. Solar and wind: the headline's price received at the hub chosen (section 4.3, from the capture file) over the flat average of the same hours, in percent. A battery and a peaker: the headline's price while selling or running, over the price of every hour (section 4.9's capture rate).
- The worst month: the lowest month of every month held, for the reader's size (section 4.13's first of "the worst three months").
- With and without the battery: the co-optimized pair and the plant alone, energy at day-ahead prices, for the reader's sizes (section 4.11's first row). Solar and wind in ERCOT and CAISO; elsewhere the row says "not modeled", with the reason on hover. It is priced at the grid's main hub whatever hub is chosen, as section 4.11 is.

### 11.3 The formulas

Per kW of nameplate; the page multiplies by `1,000 x MW` for the reader's size. `share`, `rate`, `deg` and `hurdle` are fractions here (the reader types percent). They are the battery page's formulas, and `site/scripts/test-seller-finance.mjs` holds the two libraries equal on 400 seeded cases.

- **Capital recovery factor.** `crf(i, n) = i / (1 - (1 + i)^-n)`; at `i = 0`, `1 / n`.
- **The debt's years.** `n = min(term, life)`: a term longer than the project life is cut to the life.
- **Annual debt payment.** `debt = capex x share x crf(rate, n)`. Default case (ERCOT solar): `1,375 x 0.6 x 0.085803 = 70.79` per kW, USD 7,078,769 for 100 MW, the page's own default.
- **Revenue in year t.** `R_t = R x (1 - deg)^(t - 1)`: the last twelve months repeated every year of the life, falling by the degradation rate each year after the first. An assumption, not a forecast.
- **Cash flows to equity.** `F_0 = -capex x (1 - share)`. For `t = 1 to life`: `F_t = R_t - fom - debt` while `t <= n`, and `F_t = R_t - fom` after. No tax, no tax credit, no repowering, no residual value, no inflation.
- **NPV at the hurdle rate.** `NPV = sum over t = 0 to life of F_t / (1 + hurdle)^t`, to equity, after debt payments.
- **IRR.** The rate at which that sum is zero, by bisection between -99 percent and 1,000 percent a year. When the sum has the same sign at both ends there is no such rate and the page says "none".
- **Debt coverage.** `(R - fom) / debt`. With no debt (`share = 0` or `capex = 0`) the page says "no debt".
- **The worst month's coverage.** `(M - fom / 12) / (debt / 12)`, with `M` the month's revenue per kW: the page's own monthly coverage (section 4.14) under the scenario's fixed O&M and debt.
- **The contract price at which coverage reaches 1.25.**
  - Solar and wind, USD per MWh, a contract for the whole of the energy: solving `(price x E - fom) / debt = 1.25` gives `price = (1.25 x debt + fom) / E`. It does not depend on the market price. Default case: `(1.25 x 70.79 + 12.5) / 2.580 = 39.14`.
  - A battery and a gas peaker, USD per kW-month, a toll on the whole of the capacity: `toll = (1.25 x debt + fom) / 12`, the battery page's breakeven toll. Their energy depends on the price, so a price per MWh for a fixed energy is not defined for them (section 4.10 says the same of the contract).

### 11.4 The rows, and what differs

Eight rows, the same for A and B: revenue last twelve months (USD per kW); the capture price and its ratio; the worst month (USD for the reader's size, with its month and its coverage under the scenario); debt coverage (with the annual debt payment); NPV at the hurdle rate (USD for the size, and per kW); IRR; the contract price at which coverage reaches 1.25; revenue with and without the battery beside it. Each column's header lists only the assumptions whose values differ between A and B, and nothing when none does. The last row says it in words: "B: capex USD 1,375 per kW against 1,500; hurdle rate 10 percent against 8." "Copy A to B" sets B to A. The sentence under the table states the NPV of the scenario in view at its hurdle rate.

The default case as the page stood on 11 October 2026 (ERCOT, 100 MW of solar, the hub average, October 2025 to September 2026): revenue USD 59.85 per kW; capture price USD 23.27 per MWh, 72.3 percent of 32.17; the worst month USD 139,299 (February 2024, of 99 months), coverage that month 0.06 times; debt coverage 0.67 times; NPV USD -78.43 million at 9.6 percent (USD -82.31 million at 8 percent, the default until session 196); IRR none; contract price USD 39.14 per MWh on 2,580 MWh a year per MW; USD 11.64 million with a 100 MW, 4-hour battery and USD 6.33 million without.

### 11.5 The sensitivity chart

For the scenario in view: each assumption is moved down and up by one stated step, the other seven held, and the NPV recomputed. The steps: capital cost USD 100 per kW; debt share 10 points; interest rate 1 point; term 5 years; fixed O&M USD 5 per kW a year; degradation 1 point; life 5 years; hurdle rate 1 point. A move that leaves the assumption's bounds is not drawn (degradation at 0 has no lower step). A term raised past the life is cut to the life, so that side does not move NPV at the defaults. The rows are sorted by the larger of the two moves. The two bars start at the scenario's own NPV (the vertical line). The colours are the site's first two categorical colours and carry no verdict; the same figures are in the table under the chart.

### 11.6 What this block is not

It is not a forecast and not a valuation. It repeats one year of merchant revenue over the project's life: no tax, no tax credit, no repowering, no residual value, no capacity payment. The pair with a battery is revenue only: a scenario holds the plant's costs, not the battery's. It states numbers for two sets of assumptions; it does not say which to choose.

### 11.7 Checks

`site/scripts/test-seller-finance.mjs` (hand cases, and the battery page's library on 400 seeded cases); `tests/test_session186.py` (a Python mirror of every formula above against the library to 1e-6, and the page's source); `site/scripts/check-seller-scenarios.mjs` (the page in a browser: the eight inputs and their Resets, the eight rows against the page's own figures, the address round trip, no request on a change, the chart's bars and hover, the four assets, 390 px).

## Checks

- Session 186: section 11.7.
- `tests/test_session183.py`, `tests/test_session183_replication.py`, `site/scripts/test-seller-hubs.mjs`, `site/scripts/check-seller-face.mjs`; the earlier `tests/test_session51.py`, `test_session107.py`, `test_session145.py`, `test_session162.py`, `site/scripts/check-seller.mjs`, `check-seller-deeper.mjs`, `test-capture.mjs`, `test-hybrid.mjs` and `check-values.mjs`.
<a id="cross-checks"></a>

## Cross-checks

Session 196, 11 October 2026. The page's numbers are reproducible from its tables; here they stand beside what others publish, so that a reader sees each gap and its reason. Every published figure was read on 11 October 2026 from the address given, after the host's robots file and terms; no file of theirs is copied, the figure is quoted and the source linked. "Gap" is ours less theirs. A gap is not an error to be closed: most rows compare one modeled plant with a fleet, or a cost with a market's revenue, and the reason says which.

| Our figure | Published figure | Source and date | Gap | Reason |
|---|---|---|---|---|
| Solar in ERCOT, the contract price at which coverage reaches 1.25 times: USD 39.14 per MWh | Levelized cost of energy, utility-scale solar, unsubsidized: USD 38 to 78 per MWh | [Lazard, *Levelized Cost of Energy+*, June 2025](https://www.lazard.com/media/uounhon4/lazards-lcoeplus-june-2025.pdf), LCOE v18.0, page 8 | +1.14 to -38.86: inside the range, at its low end | Ours covers the debt payments 1.25 times and the fixed O&M, on 60 percent debt, over the ERCOT fleet's 2,580 MWh a year per MW, and nothing else. Lazard's cost also returns 12 percent on the equity and pays taxes, over a range of sites and costs |
| Wind in ERCOT, the same contract price: USD 56.85 per MWh | Levelized cost of energy, onshore wind: USD 37 to 86 per MWh | the same | +19.85 to -29.15: inside the range | As above, over the fleet's 3,028 MWh a year per MW |
| A gas peaker, the toll at which coverage reaches 1.25 times: USD 8.34 per kW-month | Levelized cost of energy, gas peaking: USD 149 to 251 per MWh | the same | not stated | Not one unit: ours is a fixed charge for capacity, Lazard's a cost per MWh at its own hours of running and fuel price (USD 3.45 per MMBtu). No hours are assumed here to turn one into the other |
| Capital cost, solar: USD 1,375 per kW | USD 1,490 per kW of AC capacity in 2024 (1,620 in 2023) | [Annual Technology Baseline 2025, utility-scale PV](https://atb.nlr.gov/electricity/2025/utility-scale_pv) | -115, 7.7 percent | Ours is the midpoint of Lazard's 1,150 to 1,600. The ATB's is the modeled price of one 100 MW (DC) tracking plant, stated per kW of AC at 1.32 kW of modules to a kW of inverter |
| Capital cost, wind: USD 2,100 per kW | USD 1,968 per kW, the 2023 market average turbine | [Annual Technology Baseline 2025, land-based wind](https://atb.nlr.gov/electricity/2025/land-based_wind) | +132, 6.7 percent | Ours is the midpoint of Lazard's 1,900 to 2,300, a 2025 report; the ATB's is the market average of 2023 |
| Fixed O&M, solar: USD 12.50 per kW a year | USD 24.66 per kW of AC a year in 2024: 10.88 for the system, 11.41 for property, 2.38 for administration | [Annual Technology Baseline 2025, utility-scale PV](https://atb.nlr.gov/electricity/2025/utility-scale_pv) | -12.16 | Lazard's 11 to 14 is near the ATB's system part alone; the ATB adds land and property costs and administration |
| Fixed O&M, wind: USD 32.25 per kW a year | USD 43 per kW a year, all operating costs | [Annual Technology Baseline 2025, land-based wind](https://atb.nlr.gov/electricity/2025/land-based_wind) | -10.75 | The ATB counts every operating cost as fixed; Lazard's range is 24.50 to 40.00 |
| Degradation, solar: none | 0.7 percent a year | [Annual Technology Baseline 2025, utility-scale PV](https://atb.nlr.gov/electricity/2025/utility-scale_pv) | -0.7 | The model has no loss of output with age and the page's default for solar has no cited rate. The ruling of 11 October 2026 named the battery only. For Samuel's ruling: whether solar takes the ATB's rate |
| SP15, day-ahead, the peak block, January to September 2026: USD 24.04 per MWh over 166 delivery periods (a day, or two or three days sold as one) (NP15: 34.35 over 73 periods) | USD 23.97, ICE's "SP15 EZ Gen DA LMP Peak" (NP15: 34.58) | [EIA, Wholesale Electricity and Natural Gas Market Data, the 2026 file of ICE hub prices](https://www.eia.gov/electricity/wholesale/) | +0.07 (NP15: -0.23); by month -0.77 to +0.83 (NP15: -2.10 to +1.40) | ICE's index is the volume-weighted price of trades made the day before for the peak block; ours is the mean of the cleared hourly day-ahead price over the same block (hours ending 7 to 22 Pacific, Monday to Saturday, NERC holidays out) on the same delivery days. A traded expectation against the cleared price: SP15's months agree within USD 1, single days differ by about USD 3 |
| New England's internal hub, day-ahead, the peak block, January to September 2026: USD 77.72 per MWh over 157 delivery days | USD 78.55, ICE's "Nepool MH DA LMP Peak" | [EIA, Wholesale Electricity and Natural Gas Market Data, the 2026 file of ICE hub prices](https://www.eia.gov/electricity/wholesale/) | -0.83; by month -7.41 (January) to +1.31 | The same, with hours ending 8 to 23 Eastern, Monday to Friday. January's cold days were traded above where the day-ahead market cleared |

- A battery among this page's assets: its cross-checks are the battery page's (`battery_earns_algorithm.md`, "Cross-checks").
- Not compared: ERCOT's hubs. EIA's 2026 file holds no ERCOT hub; it holds SP15, NP15, the New England hub, and hubs of two operators this project sends no request to and reads no row of.

