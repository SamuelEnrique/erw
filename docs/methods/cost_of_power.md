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
- **Which hours of generation count:** those in which the fuel's own value is not blank. The mix's test of a whole hour (do all the sources add up to the total) is not applied, because it asks about every source: in Texas from 6 to 14 December 2025 it fails because EIA's "other" repeats the batteries' output, while solar and wind stand as reported. With that test December 2025 would hold 87 percent of its hours and Texas would have no twelve months to September 2026. Hours used that fail it: ERCOT 49, NYISO 37, ISO-NE 20, SPP 197, CAISO 7,912 (7,904 of them the hydro gap of 2019 and 2020, before any California price is held). **Ruled on 7 October 2026 (the owner): the generator page keeps this hours rule as built** (`warehouse/derived/capture_price.py`); session 145 had chosen it and asked.
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

## Session 162: the hybrid co-optimized, the capture price by hub and year, your plant's profile

`/cost-of-power/seller` gains three blocks. Nothing session 145 showed is removed: its hybrid figures stand in a row of their own. The page face still carries no method, with one exception the owner asked for by name (9 October 2026): the added figure is labeled "upper bound" on the face.

- **The builder:** `warehouse/derived/seller_hybrid.py` writes `site/data/seller/hybrid.json` and `site/public/seller/prices/<grid>_<year>.json`. No warehouse table is written and no request is made. It reads the capture price's own public price tables and the seller's model's generation shapes, and nothing else.
- **The arithmetic:** `site/lib/sellerhybrid.ts` (no imports), used by the page on the server, by the profile box in the browser and by `site/scripts/test-hybrid.mjs`.

### (a) The plant and the battery, co-optimized

For ERCOT and CAISO (the grids the battery page's model is open for), a solar or a wind plant and a 2, 4 or 8 hour battery behind one interconnection.

- **Prices:** the main hub's hourly day-ahead price (ERCOT's hub average, CAISO's SP15), from the tables the capture price reads, the first table that holds an hour.
- **The plant's output:** the seller's model's shape, EIA-930's hourly generation of the fuel over the fuel's installed nameplate that month (EIA-860M), times the reader's MW. A fleet's shape. An hour below zero (a plant's own use at night) is zero, the capture price's rule.
- **The program, one local day at a time.** With the hour's price p, the plant's output g, the battery's power P, its energy E (P times its hours) and the interconnection limit L:
  - maximize the sum of p x (g + discharge - charge);
  - charge between 0 and min(P, L + g): the battery charges from the plant's own output or from the grid, and what the plant does not supply is bought, the purchase inside the limit;
  - discharge between 0 and min(P, L - g): the pair's export stays inside the limit;
  - the state of charge, the sum of eta x charge less discharge over eta with eta the square root of 0.86 (the battery page's round trip), stays between empty and full, each day from empty;
  - at most one full cycle a day (the battery page's rule);
  - no discharge in an hour priced below zero. In an hour priced at zero or more, charging and discharging together never pays, and a tie that left both is netted, so in every hour the battery charges or discharges, never both.
- **The limit L** is the plant's capacity, or its highest hour of the twelve months when that is higher (EIA-860M lags new plants, so the fleet's output per MW of nameplate passes 1 in some hours). The plant alone therefore never loses energy to the limit; the limit binds on the battery, which cannot discharge at full power while the plant is near its capacity.
- **The plant sells every hour at its price,** as the seller's model does, with no curtailment at a negative price. The pair's revenue is the plant's plus what the battery adds; an idle battery is always allowed, so the pair never earns less than the plant alone, and with a battery of zero size the pair is the plant.
- **Perfect knowledge of the day.** Each day's schedule is the best one against that day's day-ahead prices, all known when it is made. That is an upper bound for a schedule made the day before, when offers are written without knowing where the market clears.
- **Energy only.** No ancillary service, no capacity payment, no tax credit rule, no degradation, no outage.
- **Charging from the plant** is an account, not a choice: at one hub price a MWh from the plant and a MWh from the grid cost the same. The page reports the share of the charging energy that the plant's output covered in the same hour.
- **The days.** A local day (23, 24 or 25 hours) is solved only when every hour of its price and of the fuel's output is held. A month counts with at least 90 percent of its days solved (the battery page's rule); the twelve months are the newest counted month and the eleven before it. Days left out are counted and shown on hover, never filled.

**What the section shows, side by side** (USD for the reader's sizes; per MW on hover):

| Row | Plant alone | Battery alone | Co-optimized pair | Added, not co-optimized: upper bound |
|---|---|---|---|---|
| Energy at day-ahead prices | the plant under the program's prices and days | the same battery with no plant and an interconnection of its own, same days, prices and rules | the program above | the first two added |
| Plant at real-time prices, battery with ancillary services (session 145's figures, kept) | the seller's model, real time | the figure of What a battery earns, energy and ancillary services, for the strategy chosen | not modeled | session 145's combined figure |

- **In the first row the added figure is a true upper bound of the pair:** the pair is the same two assets, on the same prices and days, under one more limit. The difference is what sharing the interconnection costs.
- **The second row is session 145's "Combined", kept and labeled an upper bound as the owner asked.** It is on other prices (the plant in real time) and holds ancillary revenue the co-optimized pair does not, so it is not a bound of the first row's pair by arithmetic. Where the first row's pair comes out above it, the page marks it on the face ("below the co-optimized pair") and says so in the hover. On the real numbers of 9 October 2026 it does not happen at the default sizes: for a 100 MW plant with a 100 MW battery, in ERCOT and CAISO, solar and wind, at 2, 4 and 8 hours and under both strategies (24 cases, read from the built page by `site/scripts/check-seller-deeper.mjs`), the co-optimized pair is below the kept figure in every one. The nearest is ERCOT wind with a 2-hour battery under the day-ahead schedule: the pair USD 12,088,452 against a kept figure of USD 13,463,570. Other sizes are not ruled out, which is why the page carries the mark.
- **The battery alone against the battery page's own program.** `warehouse/derived/battery_stack.py`, `solve_day`, with no ancillary product, on the same days and prices, gives this file's figure on every day of ERCOT's twelve months at 2, 4 and 8 hours and of CAISO's at 2 and 4 hours. At 8 hours in CAISO, 7 days differ, by USD 5.92 per MW in a year of USD 63,384 (0.009 percent): the battery page's program may discharge at a price below zero to make room, and this one does not.
- **One implementation, checked by a second.** The page's function is a simplex of its own in TypeScript; the builder solves the same program with scipy's HiGHS and writes its figures in the file; `site/scripts/test-hybrid.mjs` holds the two to one part in a million on every case written (they agree to one part in ten billion).

Per MW of plant, a 4-hour battery of the plant's size, October 2025 to September 2026 (built 9 October 2026):

| Grid, plant | Plant alone | Battery alone | Co-optimized pair | The two added | Charging from the plant |
|---|---|---|---|---|---|
| ERCOT solar (364 days, 1 left out) | 63,285 | 53,881 | 116,379 | 117,166 | 60.2 percent |
| ERCOT wind (364 days, 1 left out) | 90,830 | 53,881 | 137,601 | 144,711 | 34.7 percent |
| CAISO solar (363 days, 2 left out) | 29,833 | 39,046 | 68,726 | 68,879 | 60.5 percent |
| CAISO wind (363 days, 2 left out) | 66,621 | 39,046 | 101,905 | 105,667 | 25.5 percent |

Other grids read "not modeled for this grid". MISO is blank, paused while terms are reviewed; PJM reads "licensed source needed".

### (b) Capture price by hub and year

One table: every public hub and zone the capture file holds (39 of five grids) as rows, the calendar years 2019 to 2026 and the last twelve months as columns, solar or wind and day-ahead or real time by a switch (day-ahead first: every hub holds it). A click on a year sorts by it.

- **A cell** is the capture price of the year's counted months, from `site/data/seller/capture.json` by `lib/capture.ts` (`hubYears`, `yearCell`): the sum of price x generation over the sum of generation. Capture price times generation equals revenue; the tests hold it for every cell.
- **On hover:** the hub's simple average price over the same hours, the capture ratio (the capture price over that average, in percent), the hours held of the year (hours used over the year's 8,760 or 8,784), the months counted when the year is partial, and the source (the price tables and the EIA-930 workbook).
- **The generation shape for a hub is its grid's whole fleet of that fuel by hour,** as the rest of the page uses it (EIA-930; California from the join from CAISO's own supply). Two hubs of one grid differ by their prices only.
- **A partial year** (fewer than twelve counted months) is marked "partial" in the cell and holds its counted months only. **A year not held** reads "not held" with the reason on hover: the price is not held that year, no month holds 95 percent of its hours, or the grid's generation of that fuel is zero (New York's solar in EIA-930).
- **Shading** is the capture ratio: red below the hub's simple average, grey above it.
- **No MISO hub, no PJM hub and nothing internal:** the file is built from public tables only; MISO and PJM are rows of words.

### (c) Your plant's profile

A box for solar and wind: the reader pastes or uploads one calendar year of hourly output, and revenue, the capture price and the pair with a battery are computed in the browser.

- **Nothing is sent and nothing is stored.** The profile lives in the page's memory and nowhere else: it is in no request, no address, no cookie, no local or session storage and no log, and a file chosen is read on the device by the browser's own file reader. The fields have no name and stand in no form. The only request the box makes is a plain GET for the static file of the hub's prices for the year chosen, `/seller/prices/<grid>_<year>.json`, which is asked for when the page opens and when another year is chosen and carries nothing of the reader's. `site/scripts/check-seller-deeper.mjs` proves it in a real browser: after a paste no request leaves the page, the address is unchanged and storage and cookies hold nothing of it.
- **What is accepted, exactly.** 8,760 values for a common year or 8,784 for a leap year, one for each hour of the year chosen, in order. One number a line, or a CSV (comma, semicolon or tab) with exactly one column that is a number in every row; a first line that holds no number is read as a header; empty lines after the last value are ignored. A number is plain digits with an optional decimal point and exponent: no thousands separator, no unit. Each value is the plant's output in that hour in MW (the hour's average) or MWh in the hour, which are the same number.
- **The year and the time zone.** Hour 1 runs from 00:00 to 01:00 on 1 January of the year chosen in the grid's local standard time, with no daylight saving shift all year: UTC-6 for ERCOT and SPP, UTC-8 for CAISO, UTC-5 for NYISO and ISO-NE.
- **What is refused,** with a plain sentence that names the line: any other count of values, a value below zero, an empty line or empty value between values (a gap), a value that is not a number, rows of unequal width, and more than one column of numbers. Nothing is filled, cut to length or repaired.
- **The prices** are the main hub's hourly day-ahead prices of the year chosen (ERCOT's hub average, SP15, the New York City zone, ISO-NE's Internal hub, SPP's North hub), whatever hub is chosen on the page. A year is offered when at least 95 percent of its hours hold a price: ERCOT and NYISO 2019 to 2025; CAISO, ISO-NE and SPP 2025. An hour without a price (CAISO's 2025 holds 8,735 of 8,760) is in no figure: revenue, the capture price and the simple average are over the priced hours, and the box says how many.
- **The pair** is section (a)'s program with the form's battery, each day 24 hours of local standard time, on the days whose 24 hours all hold a price (the others left out and counted). The limit is the profile's highest hour. It is shown for ERCOT and CAISO; the other grids read "not modeled for this grid", as in section (a).

### Tests and checks (session 162)

`tests/test_session162.py` and `site/scripts/test-hybrid.mjs`, on the site's own files of real rows: capture price times generation equals revenue for every hub, fuel, market and year of the table (to a cent in a million dollars) and for the hybrid's plants hour by hour; the pair is never below the plant alone on any day; state of charge, power, the limit and the one cycle hold in every hour; with a battery of zero size the pair is the plant; the two added are never below the pair; the page's function and the builder's agree; the battery alone is the battery page's program with no ancillary product; a profile of the wrong length, with a value below zero, a gap or a value that is not a number is refused; a flat profile captures the simple average exactly. `site/scripts/check-seller-deeper.mjs` reads the built page as HTML and in a real browser (the figures of the hybrid for both grids, both fuels, the three durations and both strategies; every cell of the table; the switch, the sort and the hover; the pasted profile sends and stores nothing).
