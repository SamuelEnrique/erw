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
- **The 2018 baseline is not held.** The 728-day offset puts the baseline at 2018-03-04 to 2018-06-03. EIA's per-BA workbooks, the only EIA-930 history the warehouse holds, start on 2018-07-01. That offset is left out whole, and so for this window the baseline is 2019 alone. It is named in the table's header and run log. Pulling EIA's six-month files for 2018 would restore it (not done: session 36C made no pulls). **Session 49 restored it** for the seven ISO BAs: see below.
- **One baseline year means that year's weather is in every comparison.** A cold or mild week of 2019 moves the 2020 comparison as much as a lockdown. The table holds no weather (`weather_obs_hourly` starts in 2026), so a drop against the baseline is not a measure of COVID-19 alone. (Session 49: two baseline years for the seven ISO BAs, and station temperatures in the table; see below.)
- **Weeks:** thirteen whole weeks from 2020-03-01, a Sunday, to 2020-05-30. A week's figure compares its seven days' demand with the seven baseline days' demand. It is written only when all fourteen days are complete. 2020-05-31 is a week's first day only, so it has no weekly row.
- **Prices, for context:** ERCOT's hub average, the daily mean real-time and day-ahead price, on the window's days and ERCO's baseline days.
- **The date the page cites:** California's Governor "issued a stay at home order to protect the health and well-being of all Californians" on 2020-03-19 (Executive Order N-33-20; the release at https://www.gov.ca.gov/2020/03/19/governor-gavin-newsom-issues-stay-at-home-order/, read as text in session 36C; the order's own PDF is a scan with no text). The warehouse holds no list of other states' orders or their dates.

## Session 49: the 2018 baseline and the weather rows

- **COVID-19's 728-day baseline, restored.** `eia930_all_history` (`warehouse/connectors/eia930_history.py`) holds EIA's six-month file for January to June 2018, demand and net generation of the seven ISO BAs (the file's Adjusted columns, 60,084 rows). `build_covid` reads it before the extracts, so the seven BAs now have 275 or 276 days (the window and both baselines, 2018-03-04 to 2018-06-03 and 2019) where they had 183 or 184. The Lower 48 (US48) is not a balancing authority in that file and keeps the 2019 baseline alone (184 days).
- **Weather rows.** For every event, per station and local day of the window and its baseline days: `temp_mean_f`, `temp_min_f`, `temp_max_f` (degF) and `hdd_65f`, `cdd_65f` (degF-day), entity `noaa:<station>` (DFW, IAH, SAC, LAX, PHL, ORD, MSP, JFK, BOS, OKC), `node` the ISD station id, `ba` the grid it stands for. From `noaa_isd_hourly` (NOAA NCEI ISD, `warehouse/connectors/noaa_isd.py`): `temp_mean_f` is the mean of the day's clock-hour means; the degree days use (max + min) / 2, the National Weather Service's daily mean; a station-day needs readings in at least 20 of its 24 local clock hours. 12,585 rows; the table holds 25,580 in all.
- **Not held:** IAH for ERCOT's 2023 heat and COVID-19, and LAX and ORD for COVID-19, left out to keep the NOAA pull under its 100,000-row ceiling (the noaa_isd_hourly header lists them); those grids use their first station alone on those days.
- **Use:** the event study's temperature-controlled specification (`docs/methods/event_study.md`).

## Session 39: three more events on the COVID-19 template

Built on `build_covid`'s code path, which each event configures. All three use the same key and the same weekday-aligned baseline: the same weekday 364 and 728 days earlier. Both baseline years are held for all three, because EIA's workbooks start 2018-07-01.

**Variables in each event:** the COVID-19 set, plus two for the peak hour (`max_vs`):

- the COVID-19 set, without its weekly rows: `demand_mwh`, `demand_min_mw`, `demand_max_mw`, `intensity_generation`, `demand_mwh_vs_baseline` and `demand_pct_vs_baseline`;
- `demand_max_mw_vs_baseline` (MW) and `demand_max_pct_vs_baseline` (pct): the day's highest hour of demand against the mean of the baseline days' highest hours.

Heat waves and cold snaps are stories about the peak hour.

### The September 2022 heat wave in CAISO (`caiso_heat_2022`, session 58)

2022-08-31 to 2022-09-09, CAISO's balancing authority (CISO), on this template. The baseline is the same weekdays 364 and 728 days earlier. The weather is at Sacramento and Los Angeles (`noaa_isd_hourly`, pulled for this window). CAISO's prices for 2022 are not held, so there is no price chart. The page lists CAISO's notices of those days, from `caiso_grid_emergencies`, and the event study's estimates with and without temperature. Method and numbers: `docs/methods/california_reliability.md`.

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

### Winter Storm Elliott, December 2022 (`elliott_2022`)

- **Window:** 2022-12-19 to 2022-12-29.
- **Grids:** PJM, MISO, SPP, NYISO, ISO-NE and ERCOT, each on its own local day, as for COVID-19.
- **Prices:** ERCOT's hub average, the daily mean and highest real-time and day-ahead price (`prices` "full"). PJM's prices are internal and not used.
- **Framing,** read as text:
  - FERC, NERC and the Regional Entities' inquiry report (https://www.ferc.gov/sites/default/files/2024-02/24_Winter-Storm_Elliot_0207_UPDATE.pdf): the storm blanketed "most of the eastern United States on December 23 and 24", with "90,500 MW of coincident unplanned generating unit outages, derates and failures to start" at the worst point.
  - PJM's Event Analysis and Recommendation Report (2023-07-17): "almost a quarter of the generation capacity", 47,000 MW, on forced outages; load on Dec. 23 "about 136,000 MW" against a forecast of about 127,000 MW; PJM "remained reliable, was able to serve its customers" on Dec. 23 and 24; TVA and Duke "were both in an EEA-3 and shedding load".
- **What the rows show:**
  - PJM's highest hour, 135,328 MW on 2022-12-23, agrees with the report.
  - The peak hour against the baseline was highest on 2022-12-23 in ERCOT (+65.01 percent), PJM (+41.76), MISO (+39.61) and SPP (+50.45), and on the 24th in NYISO (+17.18) and ISO-NE (+10.80, the least moved).
- **What contradicts the story:**
  - PJM's report says SPP "set a new winter peak" on Dec. 23. In EIA-930, SPP's highest hour of the window is 18:00 Central on 2022-12-22 (47,026 MW), which is 00:00 UTC on Dec. 23. The warehouse holds no SPP peak record to say which count the report used.
- **The baseline weeks hold Christmas too:** the same weekdays of 2021 and 2020.
- **Left out:**
  - MISO 2021-12-27 misses an hour, so MISO's comparison for 2022-12-26 is left out.
  - SWPP's CO2 is missing on several December days of 2020 and 2021.

### The summer 2023 heat in ERCOT (`ercot_heat_2023`)

- **Window:** 2023-08-01 to 2023-09-10, ERCOT operating days.
- **Prices:** ERCOT's hub average, the daily mean and highest real-time and day-ahead price.
- **Framing:** ERCOT's two news releases of 2023-09-06, read as text:
  - https://www.ercot.com/news/release/2023-09-06-ercot-has-initiated: the EEA 2;
  - https://www.ercot.com/news/release/2023-09-06-ercot-has-exited: "No power outages associated with the ERCOT power grid were necessary"; "Texas set a new September peak demand record today of 82,705 MW driven by extreme heat across the state"; and the chief executive's "High demand, lower wind generation, and the declining solar generation during sunset led to lower operating reserves on the grid".
- **What contradicts the story:**
  - The emergency did not come on the day of the highest demand. EIA's highest hour on 2023-09-06 was 82,692 MW, 13 MW under ERCOT's September record. The window's highest hour was 85,432 MW on 2023-08-10.
  - The price marks the emergency: the highest 15-minute real-time price of the window, 5,075.46 USD/MWh, came on 2023-09-06.
  - The day most above the baseline (daily demand, +32.81 percent) was 2023-09-08. The peak hour most above it (+30.31 percent) was 2023-08-13.
- **Left out:** ERCO's CO2 hours on two baseline days (2021-08-17 and 18), so the intensity of those two days is missing.

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
