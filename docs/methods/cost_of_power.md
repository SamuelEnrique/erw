# Cost of power: method

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

- **PJM is not here.** Its prices are internal (license), so no PJM price enters a public table.
- **Prices:**
  - ERCOT: `ercot_all_hub_prices_history` (2015 on), joined to the rolling `iso_rtm_hub_prices` and `iso_dam_hub_prices` from where the history ends.
  - The other ISOs: their rolling tables only, `iso_*_hub_prices`, `nyiso_*_zone_prices` and `isone_*_zone_prices(_hourly)`. These hold about the last 33 days.
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

## Which months each ISO has (as built on 2026-09-30)

| ISO | Real-time | Day-ahead | Complete months |
|---|---|---|---|
| ERCOT | 2018-07 to 2026-09 | 2018-07 to 2026-09 | every month but 2018-07 (720 of 744 hours; EIA's ERCO demand starts on 2018-07-02), 2018-11 (673 of 721), 2025-12 (696 of 744) and 2026-09 (to the 27th) |
| CAISO, ISO-NE, NYISO | 2026-08-26 to 2026-09-27 | 2026-08-26 to 2026-09-28 | none |
| MISO | 2026-08-27 to 2026-09-27 | 2026-08-26 to 2026-09-28 | none |
| SPP | 2026-09-24 to 2026-09-27 (96 hours) | 2026-08-26 to 2026-09-28 | none |

- **The rolling tables drop their oldest days.** The builder therefore keeps, from its previous file, any month the inputs no longer reach (`carry`), and never recomputes a month from fewer hours.
- **The builder is not in the daily run.** The ERCOT history and the extracts are not on the runner. Rerun it by hand after the daily runs to complete September 2026 and add later months.

## The calculator on `/cost-of-power`

**Inputs,** each labelled on the page as an assumption with its default:

- facility size in MW (default 100);
- load factor (default 0.9);
- period: a month (30 days), a year (365 days), or a training run of N days (default 90).

**Flat load:**

- Energy = MW x load factor x 24 x days.
- Price = the hub's real-time `simple_mean` over the last 12 months held, weighted by `rt_hours`. That is the mean price of every hour held.
- Cost = energy x price.

**Cheapest 80 percent of hours:**

- The facility draws MW x load factor only in the cheapest 80 percent of hours and nothing in the rest, so it uses 80 percent of the flat energy.
- The hours are chosen by the hourly profile. The (month, hour of day) cells of the last 12 months are ranked by `rt_mean_hNN`, and the cheapest are taken, weighted by `rt_days_hNN`, until they hold 80 percent of the hours. The last cell is taken in part.
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
