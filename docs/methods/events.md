# Event windows: method

Built in session 36B for the Historical Event Analyzer (`/events`). One derived table, `event_window_daily` (tier derived, public), written by `warehouse/derived/event_window.py` from tables and files the warehouse already held: no pull.

## The table

- **Rows:** one row per event, entity, variable and day.
- **Partition columns:**
  - `ba`, the EIA-930 balancing authority;
  - `event`, the event id (`uri_2021`), a reserved partition column since session 36B (decision 31 of `docs/datastandard.md`).
- **Later events append their rows.** The key is (entity, variable, ts_utc, event) since session 36C (decision 32), so an event's days and baseline days may be another event's days.
- **Days are the operating days of the grid's own time zone** (America/Chicago for ERCOT; each balancing authority's own zone for COVID-19, below). Each is labelled with its local date at 00:00:00Z (decision 11), freq `P1D`.
- **Complete days only.** A day's value is written only when every interval of that day is present: 96 real-time intervals, 24 day-ahead hours, or 24 EIA-930 hours. On the spring change to daylight time a local day has 23 hours (92 real-time intervals), and that is complete (session 36C; Uri's days never cross a change). Nothing is filled. Days left out are named in the table's header and run log.

## The first event: Winter Storm Uri, ERCOT (`uri_2021`)

- **Window:** 2021-02-07 to 2021-02-24, eighteen days: the week before the storm, the storm, and the week after.
- **Baseline:** the same calendar days of 2019 and 2020. For the comparison variables, the baseline of a day is the mean of those two years' values for the same calendar day.
- **The date the page cites:** EIA writes that "ERCOT began implementing rotating outages at midnight on February 15" (https://www.eia.gov/todayinenergy/detail.php?id=46836).

## The second event: COVID-19, spring 2020 (`covid_2020`)

Added in session 36C.

- **Window:** 2020-03-01 to 2020-05-31, ninety-two days.
- **Grids:** the seven ISO balancing authorities of EIA-930 (CISO, ERCO, ISNE, MISO, NYIS, PJM, SWPP) and US48, the lower 48 states.
- **Days:** each balancing authority's local day.
  - ERCO: ERCOT operating days (America/Chicago).
  - SWPP: America/Chicago.
  - MISO: Eastern Standard Time all year (`EST`), its market day, as in `storage_daily_cycle`.
  - ISNE, NYIS, PJM and US48: America/New_York.
  - CISO: America/Los_Angeles.
- **Baseline: weekday-aligned.** The baseline of a day is the same weekday 364 days earlier (2019) and 728 days earlier (2018). A calendar-day baseline would compare a Sunday with a Monday, and demand differs by weekday more than the effects this page looks for. Holidays still move: Easter was 2019-04-21 and 2020-04-12. Memorial Day aligns exactly (2019-05-27 and 2020-05-25).
- **The 2018 baseline is not held.** The 728-day offset puts the baseline at 2018-03-04 to 2018-06-03. EIA's per-BA workbooks, the only EIA-930 history the warehouse holds, start on 2018-07-01. That offset is left out whole, and so for this window the baseline is 2019 alone. It is named in the table's header and run log. Pulling EIA's six-month files for 2018 would restore it (not done: session 36C made no pulls).
- **One baseline year means that year's weather is in every comparison.** A cold or mild week of 2019 moves the 2020 comparison as much as a lockdown. The table holds no weather (`weather_obs_hourly` starts in 2026), so a drop against the baseline is not a measure of COVID-19 alone.
- **Weeks:** thirteen whole weeks from 2020-03-01, a Sunday, to 2020-05-30. A week's figure compares its seven days' demand with the seven baseline days' demand. It is written only when all fourteen days are complete. 2020-05-31 is a week's first day only, so it has no weekly row.
- **Prices, for context:** ERCOT's hub average, the daily mean real-time and day-ahead price, on the window's days and ERCO's baseline days.
- **The date the page cites:** California's Governor "issued a stay at home order to protect the health and well-being of all Californians" on 2020-03-19 (Executive Order N-33-20; the release at https://www.gov.ca.gov/2020/03/19/governor-gavin-newsom-issues-stay-at-home-order/, read as text in session 36C; the order's own PDF is a scan with no text). The warehouse holds no list of other states' orders or their dates.

## Session 39: three more events on the COVID-19 template

Built on `build_covid`'s code path, which each event configures. All three use the same key and the same weekday-aligned baseline: the same weekday 364 and 728 days earlier. Both baseline years are held for all three, because EIA's workbooks start 2018-07-01.

**Variables in each event:** the COVID-19 set, plus two for the peak hour (`max_vs`):

- the COVID-19 set, without its weekly rows: `demand_mwh`, `demand_min_mw`, `demand_max_mw`, `intensity_generation`, `demand_mwh_vs_baseline` and `demand_pct_vs_baseline`;
- `demand_max_mw_vs_baseline` (MW) and `demand_max_pct_vs_baseline` (pct): the day's highest hour of demand against the mean of the baseline days' highest hours.

Heat waves and cold snaps are stories about the peak hour.

### The August 2020 heat wave in CAISO (`caiso_heat_2020`)

- **Window:** 2020-08-10 to 2020-08-24, Pacific time.
- **No prices:** CAISO's prices for 2020 are not held, and the page says so.
- **Framing:** CAISO, the CPUC and the CEC's Final Root Cause Analysis (January 13, 2021), read as text: "the two rotating outages in the CAISO footprint on August 14 and 15, 2020" (https://www.caiso.com/Documents/Final-Root-Cause-Analysis-Mid-August-2020-Extreme-Heat-Wave.pdf).
- **What contradicts the story:**
  - The highest peak hour against the baseline was on 2020-08-18 (+23.50 percent, 46,643 MW), not on the outage days (+10.74 and +21.58 percent).
  - The same report says "August 17 through 19 were projected to have much higher supply shortfalls", and credits a statewide mitigation effort and consumer conservation for avoiding further outages.
  - Demand served on 14 and 15 August also leaves out the load that was shed.
- **Left out:** three CISO days, each missing one hour in EIA's data:
  - 2020-08-10, an event day;
  - 2019-08-13 and 2019-08-25, baseline days, so their comparisons for 2020-08-11 and 2020-08-23 are missing.

## Sources and variables

| Variable | Entity | From | Unit |
|---|---|---|---|
| `rt_mean`, `rt_max` | `ercot:HB_HUBAVG` | `ercot_all_hub_prices_history`, market `ercot_rtm`: the day's mean and highest 15-minute real-time settlement point price (ERCOT NP6-785-ER) | USD/MWh |
| `da_mean`, `da_max` | `ercot:HB_HUBAVG` | the same table, market `ercot_dam`: the day's mean and highest hourly day-ahead price (ERCOT NP4-180-ER) | USD/MWh |
| `demand_mwh` | `eia930:ERCO` | EIA's hourly demand, summed over the day's 24 hours | MWh |
| `demand_min_mw`, `demand_max_mw` | `eia930:ERCO` | the day's lowest and highest hour of demand | MW |
| `net_generation_mwh` | `eia930:ERCO` | EIA's hourly net generation, summed | MWh |
| `intensity_generation` | `eia930:ERCO` | the day's CO2 generated (`eia930_all_emissions`) x 1000 over its net generation: `carbon_intensity_daily`'s formula, over the local day | kgCO2/MWh |
| `demand_mwh_vs_baseline`, `net_generation_mwh_vs_baseline` | `eia930:ERCO` | event days only: the day minus the baseline mean of its calendar day | MWh |
| `demand_mwh_day_change`, `net_generation_mwh_day_change` | `eia930:ERCO` | event days only: the day minus the previous day of the window | MWh |

For `covid_2020`, by entity `eia930:<BA>` for each of the eight, and `ercot:HB_HUBAVG` for prices:

| Variable | Rows | From | Unit |
|---|---|---|---|
| `demand_mwh`, `demand_min_mw`, `demand_max_mw`, `intensity_generation` | the window and the held baseline days | as for Uri, from each BA's extract and `eia930_all_emissions` | MWh, MW, kgCO2/MWh |
| `demand_mwh_vs_baseline` | event days | the day minus the mean of its held baseline days | MWh |
| `demand_pct_vs_baseline` | event days | (the day over the mean of its held baseline days, minus 1) x 100 | pct |
| `demand_mwh_vs_baseline_week`, `demand_pct_vs_baseline_week` | the week's first day, `freq` `P1W` | as above, over the week's seven days | MWh, pct |
| `rt_mean`, `da_mean` | `ercot:HB_HUBAVG`, the window and the baseline days | as for Uri | USD/MWh |

**Where the hourly demand and net generation come from.** EIA's per-BA workbook for ERCO (sheet Published Hourly Data, source `eia:gridmonitor/knownissues/xls`), as the emissions connector extracted it in session 34 (`warehouse/raw/eia930_emissions/20260930T000657Z/erco_hours.csv`, the same columns `carbon_intensity_*` divide by).

- The warehouse's `eia930_all_demand` and `eia930_all_generation` keep only about 30 days, so they cannot reach 2019 to 2021.
- The extract's workbook, URL and Last-Modified date are in the table's header.
- Raw files are pruned after 14 days. The extract behind this table will leave the machine, but the rows stay in the table, the archive and Redivis.

## Demand during load shed is load served

EIA-930's demand is the load the grid served, not what customers wanted. During rotating outages, customers whose power was cut used nothing, and that shortfall is not in the numbers.

- So demand served during Uri is a floor on what Texans would have used. The fall on 2021-02-15 shows the outages as much as any change in need.
- Demand served still stayed above the 2019 and 2020 baseline on every day from 2021-02-09 to 2021-02-20, the outages included (the rows `demand_mwh_vs_baseline`). The table holds no weather to say why.

## What the page reads

`/events/covid-2020` draws one chart of weekly demand against the baseline, in percent, for all eight grids on one axis, and a small multiple per grid (daily demand served in 2020 and on the baseline days). Under each grid is one line read from its weekly rows: the deepest weekly drop against the baseline and its week, and the deepest from the week of 2020-03-22 on, the first whole week after California's order. The two differ because the literal deepest week is, in several grids, the week of 2020-03-01, before any order. The table holds no weather to say why.

`/events/uri-2021` draws four charts from this table, with the event year against 2019 and 2020 on the same calendar days: price, demand served, net generation and carbon intensity.

Under each chart is a one-line figure read from a row of the table, each with a check key that `site/scripts/check-values.mjs` recomputes:

- the peak real-time price;
- the lowest demand hour;
- the largest day-to-day fall in net generation, and the largest shortfall against the baseline.

## Not in the table

- Prices of other hubs and load zones.
- Outage (load shed) amounts: ERCOT reports them, and the warehouse does not hold them.
- Weather: `weather_obs_hourly` starts in 2026.
