# Cost of power: method

> **MISO is paused (4 October 2026).** MISO's terms forbid automated access to its site, so every pull of MISO's own servers is paused pending a review; MISO's hub prices stop at the last day pulled, and so do the months built on them. What is held stays as it is. [`miso_pause.md`](miso_pause.md)

Built in session 37 for the cost-of-power model v0, platform tool 16 (`/cost-of-power`). Three derived tables (tier derived, public), written by `warehouse/derived/cost_of_power.py`, from tables and files the warehouse already held. No pull was made to build them.

**v0 is market-based.** It measures what electricity costs to buy on the wholesale market at an ISO's main hub. It does not measure what power costs to build: a levelized cost (LCOE) needs capital, fuel and financing inputs the warehouse does not hold yet.

## The hubs and the demand

| ISO | Hub (the price board's main hub) | Balancing authority whose demand weights it | Local clock |
|---|---|---|---|
| ERCOT | HB_HUBAVG | ERCO | America/Chicago |
| CAISO | TH_SP15_GEN-APND | CISO | America/Los_Angeles |
| ISO-NE | .H.INTERNAL_HUB | ISNE | America/New_York |
| MISO | INDIANA.HUB | MISO | EST (all year) |
| NYISO | N.Y.C. (zone J) | NYIS | America/New_York |
| SPP | SPPNORTH_HUB | SWPP | America/Chicago |
| CAISO (session 49, for `/learn/bill` only) | TH_NP15_GEN-APND | CISO | America/Los_Angeles |

- **PJM is not here.** Its prices are internal (license), so no PJM price enters a public table.
- **Prices:**
  - ERCOT: `ercot_all_hub_prices_history` (2015 on), joined to the rolling `iso_rtm_hub_prices` and `iso_dam_hub_prices` from where the history ends.
  - The other ISOs: their rolling tables only, `iso_*_hub_prices`, `nyiso_*_zone_prices` and `isone_*_zone_prices(_hourly)`. These hold about the last 33 days.
  - **Session 49:** `iso_hub_prices_history` (from 2025-09-01, `warehouse/connectors/hub_history.py`) comes first for the five other ISOs, the rolling tables after it, so every ISO has about a year. ISO-NE's history holds its 15-minute real-time prices; where its live table is hourly, they are averaged to the hour first (an hour only when all four are present).
  - **NP15 (session 49):** CAISO's NP15 hub is built beside SP15 with the same demand weights (CAISO's whole BA), for `/learn/bill`, where PG&E's wholesale reference is NP15 (PG&E serves Northern California). It is not in the ISO comparison on `/cost-of-power`, which keeps one main hub per ISO.
- **An hour's price** is the mean of its intervals: four 15-minute prices, or the one hourly price. It is used only when every interval of the hour is present.
- **Demand and CO2** come from EIA's per-BA workbooks (sheet Published Hourly Data), from the emissions connector's extracts under `warehouse/raw/eia930_emissions/`. Demand is held from 2018-07-01. `eia930_all_demand` keeps 30 days only, so it cannot weight earlier months.
- **One hub's price, the whole BA's demand.** Each hub's price is weighted by the demand of the whole balancing authority. A buyer elsewhere in the ISO pays its own node's price, which can differ, above all in NYISO, where N.Y.C. is one zone of eleven.

## Formulas

For one hub, one market (real-time or day-ahead) and one local month, over the hours where both the price and the BA's demand are held:

- `load_weighted` = sum(price_h x demand_h) / sum(demand_h). This is what the BA's load, as a whole, paid per MWh.
- `simple_mean` = mean(price_h). This is what a flat load, the same MW in every hour, pays per MWh.
- `shape_premium` = `load_weighted` - `simple_mean`, each rounded to four decimals first. It is the extra per MWh the grid's load shape pays above a flat load. It is positive when demand peaks in dear hours; negative when demand is high in cheap hours.
- `rt_hours`, `da_hours` = the hours used; `hours_in_month` = the local month's hours (743 or 745 in a month with a clock change).

**Complete months.** A month is complete when `rt_hours` equals `hours_in_month`. A partial month is written too, with its hours, and the page labels it partial. Nothing is filled.

**`cost_of_power_hourly_profile`:**

- For the last 12 local months each hub holds with demand: the mean real-time price of each local hour of day (`rt_mean_h00` to `rt_mean_h23`).
- The number of hours averaged (`rt_days_h00` to `rt_days_h23`).
- Every complete price hour of those months counts, whether or not its demand is held.

**`cost_of_power_carbon`:** over the same real-time hours as the monthly table:

- `rt_load_weighted`;
- `intensity_demand` = EIA's CO2 emissions consumed x 1000 / demand (kgCO2/MWh). This is the CO2 charged to the BA's load, imports included.
- `intensity_generation` = CO2 generated x 1000 / net generation.
- These are the `carbon_intensity_*` formulas, over the ISO's local month. A month missing any hour of CO2 has no intensity row; the header and run log name it.

## Which months each ISO has (session 49, as built on 2026-10-01)

| ISO | Real-time | Day-ahead | Complete real-time months |
|---|---|---|---|
| ERCOT | 2018-07 to 2026-09 | 2018-07 to 2026-09 | 11 of 13 since 2025-09: all but 2025-12, 2026-09 |
| CAISO SP15 | 2025-09 to 2026-09 | 2025-09 to 2026-09 | 8 of 13 since 2025-09: all but 2025-11, 2026-01, 2026-02, 2026-03, 2026-09 |
| CAISO NP15 | 2025-09 to 2026-09 | 2025-09 to 2026-09 | 8 of 13 since 2025-09: all but 2025-11, 2026-01, 2026-02, 2026-03, 2026-09 |
| ISO-NE | 2025-09 to 2026-09 | 2025-09 to 2026-09 | 2 of 13 since 2025-09: 2026-01, 2026-03 |
| MISO | 2025-09 to 2026-09 | 2025-09 to 2026-09 | 10 of 13 since 2025-09: all but 2026-01, 2026-06, 2026-09 |
| NYISO | 2025-09 to 2026-09 | 2025-09 to 2026-09 | 4 of 13 since 2025-09: 2026-01, 2026-04, 2026-05, 2026-08 |
| SPP | 2025-09 to 2026-09 | 2025-09 to 2026-09 | 11 of 13 since 2025-09: all but 2026-01, 2026-09 |

A month counts as complete when every hour has a price and the BA's demand. 2026-09 is in progress.

## Which months each ISO has (as built on 2026-09-30)

| ISO | Real-time | Day-ahead | Complete months |
|---|---|---|---|
| ERCOT | 2018-07 to 2026-09 | 2018-07 to 2026-09 | every month but 2018-07 (720 of 744 hours; EIA's ERCO demand starts on 2018-07-02), 2018-11 (673 of 721), 2025-12 (696 of 744) and 2026-09 (to the 27th) |
| CAISO, ISO-NE, NYISO | 2026-08-26 to 2026-09-27 | 2026-08-26 to 2026-09-28 | none |
| MISO | 2026-08-27 to 2026-09-27 | 2026-08-26 to 2026-09-28 | none |
| SPP | 2026-09-24 to 2026-09-27 (96 hours) | 2026-08-26 to 2026-09-28 | none |

- **The rolling tables drop their oldest days.** The builder therefore keeps, from its previous file, any month the inputs no longer reach (`carry`), and never recomputes a month from fewer hours.
- **The builder is not in the daily run.** The ERCOT history and the extracts are not on the runner. Rerun it by hand after the daily runs to complete September 2026 and add later months.

## The ranked month (session 49)

- **The ranked bar** and the calculator's defaults use one month for every ISO, chosen in this order:
  1. the latest month complete (`rt_hours` equal to `hours_in_month`) for every ISO's main hub;
  2. failing that, the latest month in which every hub holds at least 90 percent of its real-time hours, labelled with the hours held;
  3. failing that, the latest month every ISO holds, labelled partial.
- **Why the second rule:** each ISO's real-time files miss a few days or intervals, and a day missing any interval is not written (session 13). From 2025-09 to 2026-08, ISO-NE's Internal Hub is complete only in January and March 2026, NYISO's N.Y.C. in four months, and MISO's Indiana Hub misses hours in January and June. So no month is complete at all six hubs, and the first rule alone would always fall back to the current, partial month.
- **Before session 49** the ranked month was the latest month every ISO held hours for, 2026-09, partial for five of the six, and the calculator priced each hub over the months it held (12 for ERCOT, one or two for the others).

## The calculator on `/cost-of-power`

**Inputs,** each labelled on the page as an assumption with its default:

- facility size in MW (default 100);
- load factor (default 0.9);
- period: a month (30 days), a year (365 days), or a training run of N days (default 90).

**Flat load:**

- Energy = MW x load factor x 24 x days.
- Price = the hub's real-time `simple_mean` over the last 12 months held, weighted by `rt_hours`. That is the mean price of every hour held.
- **Session 49:** the page passes one month, the ranked month (below), so every ISO is priced on the same complete month; the function still takes the last 12 months when given none.
- Cost = energy x price.

**Cheapest 80 percent of hours:**

- The facility draws MW x load factor only in the cheapest 80 percent of hours and nothing in the rest, so it uses 80 percent of the flat energy.
- The hours are chosen by the hourly profile (session 49: the ranked month's cells only). The (month, hour of day) cells of the last 12 months are ranked by `rt_mean_hNN`, and the cheapest are taken, weighted by `rt_days_hNN`, until they hold 80 percent of the hours. The last cell is taken in part.
- Price = the weighted mean of the chosen cells.
- This is a schedule set by hour of day and month, which a facility could plan in advance. It is not perfect foresight of each hour.

**The results are wholesale energy only.** The page computes the defaults on the server, and `site/scripts/check-values.mjs` recomputes them from Supabase (keys `cop|flat|...` and `cop|cheap80|...`).

## What wholesale leaves out, and why it understates what an end user pays

The hub price is the energy component alone. An end user's bill adds:

- **Transmission and distribution:** the wires, charged by the utility or the transmission owner per MWh or per MW of peak.
- **Capacity:**
  - PJM, ISO-NE, NYISO and MISO hold capacity auctions whose cost reaches load. `pjm_rpm_capacity_prices` holds PJM's (internal).
  - ERCOT has no capacity market; its scarcity pricing is in the energy price.
- **Ancillary services, uplift and losses.**
- **Retail margin and hedging,** for a customer that buys through a retailer.
- **Taxes and fees.**

A large load's delivered cost is therefore above the hub price. EIA's retail prices by state (`eia_retail_electricity_prices`) show what customers paid in all. They are not compared here, because they cover a different mix of customers and months.

## Not in the tables

- PJM prices (internal).
- Node and zone prices other than the main hub.
- Bilateral and hedged contract prices.
- Any build cost (LCOE).

## The seller's side (session 51): what a generator earns

`/cost-of-power/seller` ("What a generator earns", the second tab) answers the other half of the question: what a merchant power plant earns selling at an ISO's main hub, month by month, and whether that covers its debt. It is built for a lender's reading: the bad months, the stress days, and debt service coverage.

- **The builder:** `warehouse/derived/merchant_revenue.py`.
- **The table:** `merchant_revenue_monthly` (tier derived, public; in Redivis and coverage, not in Supabase).
- **The snapshot the page reads:** `site/data/merchant_snapshot.json`, which holds the same monthly figures, the hourly prices and Henry Hub, and the ERCOT stress days.
- **The page's arithmetic:** `site/lib/merchant.ts`, shared with `scripts/check-values.mjs` (keys `mr|<inputs>|<stat>`).

### Prices

**The price** is the real-time hourly price at each ISO's main hub, exactly as the buyer's side computes it (`cost_of_power.prices_of` and `hourly`): an hour is the mean of its intervals, written only when all are present.

**The window:**
- **ERCOT:** from 2018-07 (generation by fuel starts on 2018-07-01; its prices reach back to 2015).
- **The other five ISOs:** from 2025-09, `iso_hub_prices_history` joined to the rolling tables.
- **PJM:** excluded (internal prices).

### Assets (each per MW; every result is linear in MW, so the page scales by the reader's size)

**Solar and wind: the fleet's hourly output per MW installed.**
- **Output:** EIA-930's hourly generation by fuel, the BA workbooks' `Adjusted SUN Gen` and `Adjusted WND Gen`. These are the workbooks already saved under `warehouse/raw/eia930_emissions/` that the emissions extracts were read from. The extracts themselves hold no fuel columns. **California's hours from 1 November 2023 to 2 December 2025 are read one hour earlier than EIA stamps them (session 82):** EIA's values for California sit one hour late in that period, measured against CAISO's own data and against the sun (`docs/methods/eia930_caiso_break.md`, "The late hours"). The same holds for California's demand in the load weights above.
- **Capacity:** the fuel's installed nameplate in that BA in that month, from EIA-860M: operating generators by operating month, plus retired ones until their retirement month.
- **Revenue** is the sum over the month's hours of output per MW times the price.
- **Limits:**
  - It is a fleet average, not a site: a single plant's resource, curtailment, congestion and node price are not in it.
  - Curtailed energy is not in EIA-930's generation.
  - EIA-860M lists some new plants after they start generating, so output can exceed installed nameplate. In ERCOT, 1,428 solar hours did, and SPP had 121 solar hours, mostly in years of fast growth; this inflates the shape there. CAISO's solar is negative in 4,197 hours (station use at night, as EIA reports it).
  - The values are kept as EIA and EIA-860M give them, and counted in the run log and on the page.
  - EIA-930 reports no solar for NYISO (NYIS), so NYISO has wind only.

**Batteries (`battery_2h`, `battery_4h`): an upper bound.**
- **The model:** the perfect-foresight optimum of `lib/battery.ts`'s rules at asset scale, solved per local day from empty with an exact-state dynamic programme (`battery_day`):
  - hourly, at full power or nothing;
  - at most one full cycle a day (the energy taken out of the battery is at most its usable energy).
- **Round trip:** 86 percent, the low end of Lazard's 92 to 86 percent for utility-scale standalone storage (LCOS v10.0).
- **Durations:** 2 and 4 hours, the two Lazard prices. The page prices a battery at the nearer of the two from MWh / MW.
- **What makes it an upper bound:** nobody knows a day's prices in advance.

**Gas peaker.**
- **The rule:** it runs in each hour whose hub price exceeds Henry Hub times the heat rate plus the variable O&M, and earns the difference.
- **Henry Hub:** the day's spot price from `eia_fuel_spot_prices`, or the last trading day's before a day without one.
- **Defaults:** 10.725 MMBtu/MWh and 4.25 USD/MWh, the midpoints of Lazard LCOE v18.0's gas peaking (new build) ranges (10,275 to 11,175 Btu/kWh; 3.50 to 5.00 USD/MWh). The page recomputes the peaker from the hourly prices at the reader's own heat rate and variable O&M.
- **Not modeled:** start costs, minimum run, ramp limits, outages, and the gas basis. Delivered gas in New England and New York costs more than Henry Hub in winter, so the margin there is overstated.

### The table: `merchant_revenue_monthly`

| Part | What it is |
|---|---|
| Entity | the hub, e.g. `ercot:HB_HUBAVG` |
| Partition | `ba` |
| Timestamp | the local month's first day (`ts_utc` `YYYY-MM-01T00:00:00Z`, freq `P1M`) |
| Variables | `<asset>_<metric>`, for the assets `solar`, `wind`, `battery_2h`, `battery_4h` and `peaker` |
| Per month | `flat_price` (the mean of all priced hours) and `hours_in_month` |
| Rows, 2026-10-01 | 5,984: ERCOT 3,670 (100 months), each other ISO 481 (13 months), NYISO 390 (no solar) |

| Metric | Unit | What it is |
|---|---|---|
| `revenue_per_mw` | USD/MW | sales less purchases (batteries) or less fuel and variable O&M (peaker) |
| `sales_per_mw` | USD/MW | sales alone |
| `energy_per_mw` | MWh/MW | energy delivered |
| `capture_price` | USD/MWh | sales over energy |
| `flat_price` | USD/MWh | the mean price over the hours the asset used |
| `capture_rate` | pct | the capture price over the flat price |
| `hours` | count | priced hours used; for batteries, days |

`USD/MW` and `MWh/MW` joined the unit vocabulary with Decision 34.

### The page

**Inputs**, each with a labelled default:
- ISO hub;
- asset;
- size (MW; MWh for a battery);
- annual debt service;
- fixed O&M;
- for the peaker, the heat rate and the variable O&M.

**Defaults** come from Lazard, *Levelized Cost of Energy+*, June 2025, each the midpoint of Lazard's range:

| Asset | Capital, USD/kW | Fixed O&M, USD/kW-yr | Life, years |
|---|---|---|---|
| Solar (utility) | 1,375 | 12.5 | 35 |
| Wind (onshore) | 2,100 | 32.25 | 30 |
| Battery, 2 hours | 610 (total installed) | 11.2 (5.6 USD/kWh x 2) | 20 |
| Battery, 4 hours | 1,110 (total installed) | 22 (5.5 USD/kWh x 4) | 20 |
| Gas peaker | 1,300 | 13.5 | 30 |

**Debt service:**
- **Formula:** capital x 60 percent debt at 8 percent, levelized over the life: Lazard's own financing, "60% debt at an 8% interest rate", with "Economic life sets debt amortization schedule".
- **Check:** this reproduces Lazard's wind illustration. 300 MW at 1,900 USD/kW gives 342 million of debt and 30.4 million a year.

**What the page shows:**
- **Monthly revenue** over the window for the reader's size.
- **The months held:** a month counts when the asset's hours (a battery's days) are at least 90 percent of the month's. Months below that are shown grey and not counted, which understates them.
- **The summary:** the median and the 10th-percentile month (nearest rank), and the worst three months.
- **The stress days** (ERCOT only, since the other hubs' prices start after them): revenue per day in each event's window from `event_window_daily` (Uri, Elliott, the 2023 heat), against a normal week, seven times the mean of the same event's baseline days.
- **Debt service coverage:**
  - Cash flow available for debt service is revenue less fixed O&M.
  - Monthly coverage is that over one twelfth of the annual debt service.
  - Trailing-twelve-month coverage is twelve consecutive held months over the annual debt service.
  - Months and windows under 1.0x and 1.25x are counted and flagged.

**Merchant only, and labelled so:** no PPA, hedge, capacity payment or ancillary service. Real assets are rarely fully merchant, because lenders size debt on contracted cash flows. The list "How a lender should read the page" stood on the page until session 145 and stands in full in that session's section below; in short:
- the battery is an upper bound;
- the fleet is not a site;
- the hub is not the node;
- Henry Hub is not delivered gas;
- the other hubs have only thirteen months.

### Hand-computed checks (`tests/test_session51.py`)

Recomputed from the source files, not through the builder:

| Check | Result |
|---|---|
| ERCOT solar, 2025-07 | 744 hours; 26,000.2 MW installed; 277.9898 MWh/MW; 7,941.5254 USD/MW; capture 28.5677 USD/MWh. Equal to the table |
| ERCOT peaker, 2025-07 | 142 run hours; sales 9,901.2650; fuel and variable O&M 5,401.1143; margin 4,500.1507 USD/MW. Equal |
| One battery day, 2023-08-10, 2 hours | the DP equals brute force over every action sequence of the day's 12 evening hours (5,195.4751 USD/MW, equal to a ten-thousandth of a dollar: the DP keys each state to 1e-9 MWh). The full day's plan charges at 04:00, 08:00 and 09:00 and discharges at 15:00 and 16:00, Central time; replayed by hand it earns its value, 5,676.3210 USD/MW, within one cycle |

The snapshot equals the table for every asset, month and metric.

## Session 145: one page, the capture price, a contract and a hybrid

`/cost-of-power/seller` is one page in the battery page's layout. It holds everything the seller's tab (session 51) and its version 2 (session 107) showed; `/cost-of-power/seller/v2` redirects to it and carries its query. The two retired pages are kept, unrouted, under `site/app/_retired/`. The page face carries no method: every definition, assumption and limit is in this note, and a figure that is missing is a short placeholder with its reason on hover.

- **The builder of the new figures:** `warehouse/derived/capture_price.py`, which writes `site/data/seller/capture.json`. No warehouse table is written and no request is made.
- **The page's arithmetic for them:** `site/lib/capture.ts` (no imports), shared with `site/scripts/check-seller.mjs` and `site/scripts/test-capture.mjs`.
- **The model of sessions 51 and 107 is unchanged:** `site/lib/merchant.ts` and `site/lib/seller2.ts` on `site/data/merchant_snapshot.json`, with the same check keys (`mr|<inputs>|<stat>`).

### What left the page face and stands here

**Merchant only.** No power purchase agreement, hedge, capacity payment or ancillary service: the asset sells every MWh at the hub's real-time price. Real projects are rarely fully merchant, because lenders size debt on contracted cash flows; the page shows what is left when the contract is gone, or what an uncontracted tail earns.

**How a lender should read the page:**
- **Size on the bad months, not the average.** The 10th-percentile month and the worst three are what debt must survive; the trailing-twelve-month coverage shows whether a bad stretch outlasts a year.
- **The battery is an upper bound.** It knows each day's prices in advance; a real one captures a fraction of this. The peaker runs on perfect hourly information too, with no start costs.
- **Solar and wind are the fleet, not your site.** Hourly output per MW is the whole balancing authority's, so a single site's curtailment, congestion and node price are not here, and new capacity listed late in EIA-860M inflates the early hours of a new fleet.
- **The hub, not your node.** A plant is paid its own node's price; the gap to the hub (basis) can be large and negative exactly in the windy, sunny hours.
- **Gas is Henry Hub.** A peaker in New England or New York pays a delivered gas price that spikes in winter; Henry Hub understates it there, so the peaker's margin is overstated.
- **The few months outside ERCOT.** The other hubs' prices start in September 2024: about two years is a short sample of weather and gas, not a distribution.

**The stress days.** Revenue on the local days of each event (`event_window_daily`'s window) against the same event's baseline days, the same days or weekdays of earlier years. A normal week is seven times the mean of the baseline days. A merchant asset's best days are the grid's worst: what it earns in a storm depends on being available in it, which the model assumes (no outage, no frozen equipment, no fuel shortage).

**The spans (session 107).** The last twelve months are the newest twelve held in a row, so they overlap the newest full year where one is held. A long-run average is the sum over its full calendar years divided by their number; a year with a month missing is in none. A month is held when at least 90 percent of its hours are (a battery: its days). Figures are per kW of nameplate, before any cost but the peaker's fuel: no fixed cost, debt, tax or contract. With fewer than three full years held, one unusual season moves every figure. On the chart an incomplete year is pale: it holds fewer than twelve months and is in no long-run average. The battery joined the spans in session 145: energy alone, priced as the reader's battery, the model's 4-hour battery by default.

**What the model does not tell you.** What a plant with a contract earns (most solar and wind is sold under one, not at the hub); what your site earns (this is a fleet's output at a hub's price); whether it pays (no cost is taken off but the peaker's fuel, outside the debt coverage, which takes fixed O&M and the debt payments the reader gives); next year.

**The monthly chart.** A month in cardinal earned less than one month of debt payments (the dashed line, the annual debt payments over twelve). A grey month holds less than 90 percent of its hours (a battery: days) and is shown, not counted.

**MISO and PJM.** MISO is blank, "paused while terms are reviewed": its pulls are paused since 4 October 2026 and its terms forbid automated access and derivative works (`docs/methods/miso_pause.md`). The seller's tab showed MISO's Indiana Hub until session 145; the snapshot and the table still hold it, and the page shows none of it. An address that names MISO opens ERCOT. PJM reads "licensed source needed": no PJM hub or zone price is held in a public table.

### (a) The capture price

For a hub or zone, a fuel (solar, wind) and a market (real time, day-ahead), over a span of hours:

| Figure | Definition |
|---|---|
| Generation-weighted price | sum(price x generation) / sum(generation), USD per MWh |
| Flat average | sum(price) / hours, over the same hours |
| Premium or discount | the first less the second, in USD per MWh, and as a percent of the flat average |

- **The hours** are those in which both the price and the fuel's generation are held.
- **The price** is every public hub and zone price held, read by `price_compare.read_prices`: an hour of real time is the mean of its four 15-minute prices and is held only when all four are; where a real-time price is held two ways (ISO-NE), the one that holds more hours is used whole. Real time is shown first where a hub holds twelve months of it, with day-ahead beside it; where only day-ahead holds twelve months (New York City, the ISO-NE Internal hub, ERCOT's four non-competitive load zones), day-ahead is shown first, and each figure says which market it is.
- **The tables read:** `iso_hub_prices_history`, `ercot_all_hub_prices_history`, `iso_dam_hub_prices`, `iso_rtm_hub_prices`, the ISO-NE and NYISO zone tables, and the two histories of session 140 when they are on the machine (`ercot_zone_prices_history` was; `iso_zone_prices_history` was not on 7 October 2026, so the New York and New England zones, SPP South and ZP26 hold weeks and read "not held yet"). A table marked internal in `coverage.csv`, or absent from it and without "License: public" in its own header, is not read.
- **The generation** is the grid's whole fleet by hour: the hours of `mix_profile.hours_of`, which are EIA-930's hourly net generation by source from 2019, and for California from 16 December 2025 CAISO's own supply by fuel (the warehouse's one join, `docs/methods/eia930_caiso_break.md`). **It is the fleet's shape, not a site's:** a plant with trackers, a different wind regime, a curtailment order or a different node will differ. California's last twelve months and December 2025 hold both sources, EIA's hours before the join and CAISO's from it.
- **Which hours of generation count:** those in which the fuel's own value is not blank. The mix's test of a whole hour (do all the sources add up to the total) is not applied, because it asks about every source: in Texas from 6 to 14 December 2025 it fails because EIA's "other" repeats the batteries' output, while solar and wind stand as reported. With that test December 2025 would hold 87 percent of its hours and Texas would have no twelve months to September 2026. Hours used that fail it: ERCOT 49, NYISO 37, ISO-NE 20, SPP 197, CAISO 7,912 (7,904 of them the hydro gap of 2019 and 2020, before any California price is held).
- **Generation below zero** (a plant's own use at night; California's solar in 27,885 hours) weighs nothing, and the hour stays in the flat average.
- **A month counts** when the hours with both are at least 95 percent of the month's hours, in the grid's local time. **The last twelve months** are the newest counted month and the eleven before it, when all twelve count. **A year** is whole with twelve counted months; otherwise it is marked partial and holds its counted months only. A month under 95 percent is in no figure: nothing is filled or scaled up.
- **New York's solar:** EIA-930 itemizes no solar generation for New York (every hour is zero), so there is no generation to weigh a price by and no figure.

**Why this figure and the model's capture price differ.** The model's capture price (the spans table, the months table) is monthly, at the main hub, and weighs each hour by the fleet's output per MW of nameplate installed that month (EIA-860M); the new figure weighs by the generation itself, at every hub. A fleet that grows within the span weighs its later months more in the new figure. The model counts a month at 90 percent of its hours and reads California from EIA throughout; the new figure counts a month at 95 percent and reads California from CAISO after the join. At the main hubs the two are close: ERCOT solar over October 2025 to September 2026, 23.20 by the model and 23.27 by generation; CAISO SP15 solar, 13.83 and 13.86.

**The figures on 7 October 2026**, last twelve months (October 2025 to September 2026), USD per MWh received against the flat average:

| Main hub | Market | Solar | Wind |
|---|---|---|---|
| ERCOT, hub average | real time | 23.27 against 32.17: -8.90 (-27.7 percent) | 27.60: -4.57 (-14.2 percent) |
| CAISO, SP15 | real time | 13.86 against 28.53: -14.66 (-51.4 percent) | 25.88: -2.65 (-9.3 percent) |
| NYISO, New York City | day-ahead | no solar itemized | 77.93 against 73.10: +4.83 (+6.6 percent) |
| ISO-NE, Internal hub | day-ahead | 55.93 against 74.19: -18.26 (-24.6 percent) | 76.25: +2.06 (+2.8 percent) |
| SPP, North hub | real time | 41.21 against 30.79: +10.42 (+33.8 percent) | 25.05: -5.75 (-18.7 percent) |

63 of the 156 hub, market and fuel series hold twelve months. The widest solar discount in dollars is ERCOT's West load zone in real time (19.98 against 35.24: -15.26, -43.3 percent) and in percent CAISO's SP15; the widest solar premium is SPP's North hub. The widest wind discount is ERCOT's West hub in real time (23.86 against 30.63: -6.76, -22.1 percent); no hub pays wind a real-time premium, and New York City pays the widest day-ahead one.

### (b) Your contract

A contracted share of the energy (percent) and a price (USD per MWh), typed in the browser: the state of one component, in no form, with no field name, never in the address, a request, storage or a log. The arithmetic is the datacenter page's (`lib/datacenter.ts`, `contractResult`), which is the battery page's: the contracted share at the typed price, the rest at the market's figure for the same twelve months.

- **The energy** is the model's output per MW of nameplate over the capture price's last twelve months, times the reader's MW.
- **The market's figure** is the generation-weighted price at the hub chosen, in the market shown first.
- **Revenue without the contract** is therefore the energy times that price. At the main hub it differs slightly from the model's twelve-month revenue, by the difference in weights described above.
- **Solar and wind only.** A gas peaker runs only when the price is above its cost and a battery buys as well as sells, so a share of their energy at a fixed price is not this arithmetic; the battery page has a contract per kW-month.
- **Not in it:** the contract's settlement point and basis, shape or hourly settlement terms, curtailment and negative-price clauses, credit and collateral, and renewable energy certificates.

### (c) A solar plant with a battery beside it

For ERCOT and CAISO, the two grids the battery page's model is open for:

- **The battery alone** is the battery page's own figure for that size, duration (2, 4 or 8 hours) and strategy: its last twelve months from `battery_stack_monthly`, by `lib/batterystack.ts` (`stat`, `l12:total`), read with the battery page's own query. Energy and ancillary services, split hour by hour. Every limit of that model applies (`docs/methods/battery_stack.md`): with perfect foresight it is an upper bound.
- **The solar plant alone** is the model's revenue per MW over the same twelve months, at the main hub, where both models are priced.
- **Combined** is the two revenues added, and nothing else: two assets at one hub, each priced as if it stood alone. There is no shared interconnection limit, the battery does not charge from the plant's own output, no clipped or curtailed energy is recovered, and no tax credit rule is applied. The battery page's model does none of these either. A real hybrid behind one interconnection earns less than this sum when its limit binds and may earn more where it recovers energy the plant would have lost.
- **Per MW:** each asset per MW of itself; the combined figure per MW of the solar plant.
- **Other grids:** NYISO's and SPP's battery models are in review and ISO-NE's reserve prices need a license, so the section reads "not modeled for this grid".

### (d) Where free energy is

The page links to `/curtailment?grid=<grid>&place=<hub id>#free-energy` for the hub chosen (session 144's section).

### Tests and checks (session 145)

`tests/test_session145.py` and `site/scripts/test-capture.mjs`, on a saved real week (`tests/fixtures/session145/`: the price rows of ERCOT's West hub for the week from 1 June 2026 and the grid's solar and wind generation of the same hours): the generation-weighted price by hand; a plant that generates the same in every hour captures the flat average exactly; the premium in dollars and in percent agree; a month under 95 percent writes no figure; MISO has no number; the contract arithmetic equals the battery page's; the combined figure is the sum of its two parts. `site/scripts/check-seller.mjs` reads the built page as HTML and in a real browser.
