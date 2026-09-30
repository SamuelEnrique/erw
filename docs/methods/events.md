# Event windows: method

Built in session 36B for the Historical Event Analyzer (`/events`). One derived table, `event_window_daily` (tier derived, public), written by `warehouse/derived/event_window.py` from tables and files the warehouse already held: no pull.

## The table

- **Rows:** one row per event, entity, variable and day.
- **Partition columns:**
  - `ba`, the EIA-930 balancing authority;
  - `event`, the event id (`uri_2021`), a reserved partition column since session 36B (decision 31 of `docs/datastandard.md`).
- **Later events append their rows.** The key stays (entity, variable, ts_utc), so an event whose days, or baseline days, overlap another event's fails the build.
- **Days are the operating days of the grid's own time zone** (America/Chicago for ERCOT). Each is labelled with its local date at 00:00:00Z (decision 11), freq `P1D`.
- **Complete days only.** A day's value is written only when every interval of that day is present: 96 real-time intervals, 24 day-ahead hours, or 24 EIA-930 hours. Nothing is filled. Days left out are named in the table's header and run log.

## The first event: Winter Storm Uri, ERCOT (`uri_2021`)

- **Window:** 2021-02-07 to 2021-02-24, eighteen days: the week before the storm, the storm, and the week after.
- **Baseline:** the same calendar days of 2019 and 2020. For the comparison variables, the baseline of a day is the mean of those two years' values for the same calendar day.
- **The date the page cites:** EIA writes that "ERCOT began implementing rotating outages at midnight on February 15" (https://www.eia.gov/todayinenergy/detail.php?id=46836).

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

**Where the hourly demand and net generation come from.** EIA's per-BA workbook for ERCO (sheet Published Hourly Data, source `eia:gridmonitor/knownissues/xls`), as the emissions connector extracted it in session 34 (`warehouse/raw/eia930_emissions/20260930T000657Z/erco_hours.csv`, the same columns `carbon_intensity_*` divide by).

- The warehouse's `eia930_all_demand` and `eia930_all_generation` keep only about 30 days, so they cannot reach 2019 to 2021.
- The extract's workbook, URL and Last-Modified date are in the table's header.
- Raw files are pruned after 14 days. The extract behind this table will leave the machine, but the rows stay in the table, the archive and Redivis.

## Demand during load shed is load served

EIA-930's demand is the load the grid served, not what customers wanted. During rotating outages, customers whose power was cut used nothing, and that shortfall is not in the numbers.

- So demand served during Uri is a floor on what Texans would have used. The fall on 2021-02-15 shows the outages as much as any change in need.
- Demand served still stayed above the 2019 and 2020 baseline on every day of the outages, because the cold raised the demand that could be served.

## What the page reads

`/events/uri-2021` draws four charts from this table, with the event year against 2019 and 2020 on the same calendar days: price, demand served, net generation and carbon intensity.

Under each chart is a one-line figure read from a row of the table, each with a check key that `site/scripts/check-values.mjs` recomputes:

- the peak real-time price;
- the lowest demand hour;
- the largest day-to-day fall in net generation, and the largest shortfall against the baseline.

## Not in the table

- Prices of other hubs and load zones.
- Outage (load shed) amounts: ERCOT reports them, and the warehouse does not hold them.
- Weather: `weather_obs_hourly` starts in 2026.
