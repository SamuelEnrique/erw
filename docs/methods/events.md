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

## Session 64: two events of the hub history's second year

Both are on the Elliott template (each grid's local day; the same weekdays 364 and 728 days earlier; the peak-hour variables). They were chosen from the data, not from a news account: they are the days of the highest winter and summer hours of demand served, in EIA's hourly data, in the year the second year of hub prices covers (2024-09-01 to 2025-08-31). That year is why these two: they are the first events with prices at hubs other than ERCOT's.

- **Hub prices beyond ERCOT** (`hubs`): MISO Indiana Hub, NYISO N.Y.C., ISO-NE .H.INTERNAL_HUB and SPP SPPNORTH_HUB, from `iso_hub_prices_history`, each on its grid's local day: `rt_mean`, `rt_max` (the highest 15-minute mean; MISO's hourly real-time price), `da_mean`, `da_max`. A day is written only when every interval is there. The history starts 2024-09-01, so these hubs have no baseline days, and the event study gives them no estimate (it needs baseline days; `event_study.py` and the TypeScript twin both skip such a series).
- **No weather:** `noaa_isd_hourly` holds no event stations for these windows, so no estimate controls for temperature. Pulling it would be a new pull, not one approved in session 64.

### The January 2025 cold (`cold_2025`)

- **Window:** 2025-01-17 to 2025-01-26. **Grids:** PJM, MISO, SPP, NYISO, ISO-NE and ERCOT. **Prices:** ERCOT's hub (full), and the four hubs above.
- **Why these days:** PJM's highest winter hour of 2024-09 to 2025-08 was 144,420 MW on 2025-01-22, MISO's 104,434 MW on 2025-01-21, NYISO's 23,521 MW on 2025-01-22 and ISO-NE's 19,582 MW on 2025-01-21. SPP's and ERCOT's highest winter hours came on 2025-02-20, but 2025-01-21 and 22 were their second highest.
- **What the window shows:** PJM's peak hour stood 38.57 percent above the baseline on 2025-01-22, ERCOT's 47.97 percent the same day. The event study's pooled effect on daily demand served: PJM +412,096 MWh a day (95 percent interval 230,840 to 593,352), 17.51 percent of the counterfactual; ERCOT +21.63 percent; SPP +13.70; MISO +12.73; NYISO +9.68; ISO-NE +9.46.
- **Prices:** ERCOT's hub stayed calm (highest 15 minutes 192.08 USD/MWh on 2025-01-23; the pooled effect on its daily mean, +4.93 USD/MWh, has an interval that spans zero), while the eastern hubs rose: NYISO N.Y.C. 714.25 USD/MWh on 2025-01-21, SPP North 800.22 on 2025-01-23, ISO-NE 456.57 on 2025-01-17, MISO Indiana 393.10 (an hour) on 2025-01-21.
- **Left out:** NYISO's carbon intensity on 2025-01-17 (CO2 in 5 of 24 hours).

### The June 2025 heat (`east_heat_2025`)

- **Window:** 2025-06-20 to 2025-06-28. **Grids:** PJM, NYISO, ISO-NE and MISO. **Prices:** NYISO N.Y.C., ISO-NE and MISO Indiana (no ERCOT hub: ERCOT is not in it).
- **Why these days:** the highest hours of 2024-09 to 2025-08: PJM 160,560 MW on 2025-06-23, NYISO 31,857 MW and ISO-NE 25,898 MW on 2025-06-24.
- **What the window shows:** on 2025-06-24 ISO-NE's daily demand stood 39.93 percent above the baseline, NYISO's 35.23 and PJM's 35.05. Pooled effects on daily demand: PJM +15.35 percent (380,844 MWh a day, interval 195,313 to 566,376), NYISO +9.98, MISO +8.53, ISO-NE +6.75 (interval -15,756 to 61,785 MWh: it spans zero, and 2025-06-25 is missing an hour).
- **Prices:** every hub's highest came on 2025-06-24: NYISO N.Y.C. 2,960.11 USD/MWh (15 minutes), ISO-NE 1,240.24, MISO Indiana 1,202.05 (an hour).
- **Left out, the ISOs' own gaps:** ISO-NE's demand on 2025-06-25 (23 of 24 hours); NYISO's real-time price on 2025-06-27 and ISO-NE's on 2025-06-22 and 2025-06-26 (days the history does not hold complete).

## Session 308: the late January 2026 cold (`cold_2026`)

The owner's default of 18 October 2026 to ruling 6 of `docs/state/morning_2026-10-14.md`: one new event window, the late-January 2026 cold outbreak, with the same baseline as the other eight (the same weekdays 364 and 728 days earlier). It is on the `cold_2025` template (the six grids, ERCOT's hub in full, the four hubs above, the peak-hour variables). No request was made: EIA's hourly data is the emissions connector's held extract, and the hub prices are `iso_hub_prices_history`.

- **Window:** 2026-01-23 to 2026-02-02. **Why these days, from the data:** the highest winter hour of demand served (EIA-930, November 2025 to March 2026) came on 2026-01-26 in ERCOT (75,599 MW) and SPP (45,624 MW), 2026-01-25 in ISO-NE (20,279 MW), 2026-01-27 in MISO (101,013 MW) and 2026-01-29 in PJM (139,410 MW); NYISO's came on 2026-02-07 (24,317 MW), outside the window. The window opens on 23 January, when MISO's and SPP's demand rose, and closes on 2 February, PJM's and ERCOT's last high day.
- **What the window shows:** daily demand above the baseline at most by 49.95 percent in ERCOT (2026-01-25), 40.46 in PJM and 37.47 in SPP (2026-01-31), 30.49 in MISO (2026-02-01), 29.68 in ISO-NE (2026-01-25) and 22.43 in NYISO (2026-01-31). The event study's pooled effect on daily demand served: PJM +677,815 MWh a day (95 percent interval 579,490 to 776,140), MISO +401,424, ERCOT +346,005, SPP +200,299, NYISO +74,910, ISO-NE +67,430.
- **Prices:** the highest real-time 15 minutes (MISO: an hour) were NYISO N.Y.C. 3,768.68 USD/MWh and MISO Indiana 2,001.11 on 2026-01-24, ERCOT 1,281.45 on 2026-01-28, ISO-NE 847.69 on 2026-01-25 and SPP North 790.62 on 2026-01-23. The pooled effect on the daily real-time mean: MISO +192.39 USD/MWh, NYISO +167.19, ISO-NE +130.29, SPP +95.19, ERCOT +78.12, every interval above zero.
- **No weather:** as for `cold_2025`, no estimate controls for temperature.
- **The rebuild moved the older events' figures by rounding only:** 15 of `event_window_daily`'s ERCOT hub means by 0.0001 USD/MWh, and 146 of `event_study_estimates`' figures by at most 0.0003 USD/MWh (relative 7 in 100,000), from inputs rebuilt since the table's last build on 2 October 2026.

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

## The pages as they stand (session 332, 20 October 2026)

- **Nine event pages and the index**: the eight events before it and `cold_2026` (session 319, from the window of
  session 308). Their charts are drawn in SVG (session 303); every figure under a chart, and every estimate of the
  event study block, carries its check key, and `check-values` reads each page.
- **Downloads** (session 332): at the foot of every event page (in the event study block every page ends with) and on
  the index, `event_window_daily` as the live set's CSV with a Python and a Stata reader of that CSV, and
  `event_study_estimates` named with its place on Redivis (not in the live set: the pages compute the same estimates,
  `event_study.md`).

## The tool as a reader meets it (session 7531, 16 November 2026)

Session 7531 (chain 304) took `/events` to the done line: this note completed, a replication, a cross-check, a
decisions block and a faults file. The sections above are the table's method, event by event; this one is the pages.
The estimates' method is the table's own note, [`event_study.md`](event_study.md); the other notes of the tool's
neighbourhood ([`doe_oe417_events.md`](doe_oe417_events.md), [`noaa_ncei_billion_disasters.md`](noaa_ncei_billion_disasters.md),
[`eia930_event_hourly_interchange.md`](eia930_event_hourly_interchange.md)) are tables no page of `/events` reads today.

### The ten pages and what each shows

- **The index** (`/events`): nine cards, one an event, each with its window, its grids and one figure: the highest (or,
  for COVID-19, the lowest) row of one variable of one entity inside the window (the cards' list below). Under them the
  two tables as downloads, the link to the Flex Alert scorecard, and the decisions block.
- **Uri** (`/events/uri-2021`): four charts (ERCOT's hub average real-time price, demand served, net generation, carbon
  intensity), each with 2021 against 2019 and 2020 on the same calendar days; seven figures under them; the event study
  block (ERCOT's demand served and the hub price).
- **COVID-19** (`/events/covid-2020`): weekly demand against the baseline for eight grids on one axis; one small chart a
  grid (2020, and the same weekday of 2019 and, for the seven ISO grids, 2018); under each, the deepest weekly drop and,
  when it differs, the deepest from the week of 2020-03-22 on; ERCOT's hub prices for context; the event study block
  (the Lower 48 first, then the seven grids, and the hub price).
- **The seven pages on the shared template** (`EventWindow`: CAISO 2020, CAISO 2022, Elliott, ERCOT 2023, the January
  2025 cold, the June 2025 heat, the January 2026 cold): the peak hour against the baseline, all grids on one axis; the
  page's own sentence under it; for each grid a chart of its highest hour each day with the same weekdays 364 and 728
  days earlier, and one line (the peak against the baseline and its MW, the window's highest hour, the highest carbon
  intensity); carbon intensity, all grids; ERCOT's hub prices where the page has them; the other hubs where it has
  them; CAISO 2022 adds CAISO's notices day by day; then the event study block.
- **Every page ends** with the event study block ("What the estimates say") and the decisions block.

### The figures on the pages, each with its table and rule

Every figure is a row of `event_window_daily` picked by the rule its sentence states, or an estimate computed from the
table's daily rows at build time (`event_study.md`). "In the window" is the event's local days, both ends included; of
two equal values the earlier day is taken.

| Page | Figure | Entity, variable | Rule |
|---|---|---|---|
| Index | each card | Uri and ERCOT 2023: `ercot:HB_HUBAVG`, `rt_max`; COVID-19: `eia930:US48`, `demand_pct_vs_baseline_week`; CAISO 2020: `eia930:CISO`, `demand_max_pct_vs_baseline`; CAISO 2022: `eia930:CISO`, `demand_max_mw`; Elliott and the three events of 2025 and 2026: `eia930:PJM`, `demand_max_mw` | the highest in the window; COVID-19 the lowest from the week of 2020-03-22 on (session 7531) |
| Uri | highest 15-minute real-time price, and the highest of 2019 and 2020 | `ercot:HB_HUBAVG`, `rt_max` | the highest of 2021's days; the highest of the baseline days |
| Uri | lowest hour of demand served; the lowest on 2021-02-15 | `eia930:ERCO`, `demand_min_mw` | the lowest of 2021's days; the named day |
| Uri | largest day-to-day fall; largest shortfall against the baseline | `eia930:ERCO`, `net_generation_mwh_day_change`, `net_generation_mwh_vs_baseline` | the lowest of 2021's days |
| Uri | highest carbon intensity | `eia930:ERCO`, `intensity_generation` | the highest of 2021's days |
| COVID-19 | deepest weekly drop; deepest from the week of 2020-03-22 | each grid's `demand_pct_vs_baseline_week` | the lowest week; the lowest from 2020-03-22, shown only when its week differs |
| Template | the peak against the baseline and its MW | each grid's `demand_max_pct_vs_baseline`, then `demand_max_mw` of that day | the highest in the window |
| Template | the window's highest hour; the highest carbon intensity | each grid's `demand_max_mw`, `intensity_generation` | the highest in the window |
| Template | ERCOT's hub: highest 15 minutes, highest daily mean, highest day-ahead hour | `ercot:HB_HUBAVG`, `rt_max`, `rt_mean`, `da_max` | the highest in the window |
| Template | each other hub: the same three | `miso:INDIANA.HUB` (real-time hourly), `nyiso:N.Y.C.`, `isone:.H.INTERNAL_HUB`, `spp:SPPNORTH_HUB` | the highest in the window |
| CAISO 2020 | the peak against the baseline on 14 and 15 August, and the highest | `eia930:CISO`, `demand_max_pct_vs_baseline` | the named days; the highest in the window |
| CAISO 2022 | the highest hour; the peak against the baseline, highest and on 2022-09-06 | `eia930:CISO`, `demand_max_mw`, `demand_max_pct_vs_baseline` | the highest; the named day |
| CAISO 2022 | CAISO's notices by day | `caiso_grid_emergencies`, each local day of the window and its notice types | as the report lists them |
| Elliott | PJM's highest hour; ISO-NE's peak against the baseline; SPP's highest hour and its hour on 2022-12-23 | `demand_max_mw`, `demand_max_pct_vs_baseline` | the highest; the named day |
| ERCOT 2023 | the highest hour on 2023-09-06; the window's highest hour; the highest 15-minute price | `eia930:ERCO`, `demand_max_mw`; `ercot:HB_HUBAVG`, `rt_max` | the named day; the highest |
| Jan. 2025 and Jan. 2026 colds | PJM's highest hour, MISO's (2025) or ERCOT's (2026), PJM's peak against the baseline | `demand_max_mw`, `demand_max_pct_vs_baseline` | the highest |
| June 2025 heat | PJM's highest hour; NYISO's and ISO-NE's peak against the baseline | `demand_max_mw`, `demand_max_pct_vs_baseline` | the highest |
| Every event page | the event study block: the lead grid's pooled effect, its interval, its percent of the expected and the MWh a day expected; with temperature where a station is held, and the weather share under its condition; a row a grid (and the hub price where the page shows ERCOT's hub); each event day's effect | `demand_mwh` (`rt_mean` for the hub), daily rows | `event_study.md`, `dow_year_mean_v1` and `dow_year_temp_v1` |

### Assumptions, with their defaults and sources

The decisions block below lists them, each as the pages draw it. The ones that move figures most: the window's dates;
the baseline (the same weekday 364 and 728 days earlier; Uri the same calendar days of 2019 and 2020); demand served,
not wanted; complete days only; and, for the estimates, the absence of a trend (growth since the baseline years counts
as effect) and of weather in the first estimate.

### What the tool does not hold

- **Load shed** (MW or customers): ERCOT, CAISO and the southeast balancing authorities report it; the table holds
  demand served only, and the pages say so where it matters (Uri, CAISO 2020, Elliott).
- **Generator outages** (FERC's 90,500 MW for Elliott; ERCOT's 34,000 MW averaged over two days of Uri): quoted where a
  page quotes them, never computed.
- **CAISO's prices** for 2020 and 2022, and **PJM's prices** at any date: CAISO's are not held for those years, PJM's
  are internal.
- **Weather** for the January 2025 cold, the June 2025 heat and the January 2026 cold: no station is held, so no
  estimate there controls for temperature.
- **Other states' stay-at-home orders** in 2020, and the hourly profile of each effect (`event_study.md` holds it in the
  table; no page shows it).
- **Baseline days for the hubs beyond ERCOT's**: their history starts on 2024-09-01.

### The license hold as it stands

Since 21 October 2026 `event_window_daily` and `event_study_estimates` are "license needed", held by grid for ISO-NE,
MISO and NYISO (`site/data/license_status.json`). The site's checked-number component draws a figure as "license
needed" when its key names a held grid, and also when its key names no grid the license module knows. EIA-930's
entities (`eia930:CISO`, `eia930:PJM`, `eia930:US48` and the others) are of the second kind, so on the built pages
every EIA-930 figure and every estimate is drawn "license needed" (1,117 of the 1,127 numbers the ten pages compute),
and only ERCOT's and SPP's hub figures are drawn as numbers. The license module's own words say a row of no grid is
kept. That is fault 1 of [`docs/reviews/events-faults-2026-11-16.md`](../reviews/events-faults-2026-11-16.md), a
ruling: no hold is lifted here.

### Corrections of 16 November 2026 (session 7531)

- **COVID-19's baseline in the page's words.** The section "Session 49" above restored 2018 for the seven ISO grids,
  but the page went on saying its weekly figures were against 2019 alone. Recomputed from the table, NYISO's week of
  2020-05-17 is -15.23 percent against 2018 and 2019 (the table's row) and would be -11.77 against 2019 alone; PJM's
  -17.10 and -14.83. The page now says 2018 and 2019 (the Lower 48 2019 alone) and draws 2018's days (fault 2).
- **The index's COVID-19 card** read the lowest week of the whole window, the week of 2020-03-01, before any order
  (-11.82 percent); it now reads from the week of 2020-03-22, as the event page does: -10.62 percent, the week of
  2020-05-17 (fault 3).
- **ERCOT's September 2023 record.** "The summer 2023 heat in ERCOT" above quotes ERCOT's 82,705 MW of 6 September as
  its September record. ERCOT's release of 14 September 2023 lists 83,911 MW on 7 September and 84,182 MW on
  8 September, both inside the window (EIA: 83,913 and 84,185 MW), and an all-time record of 85,464 MW on 10 August
  (EIA: 85,432). The page now says so (fault 4).

## The decisions on the pages

Drawn at the foot of every page (`site/app/events/Decisions.tsx`), each with its default, its source and its session
in a hover tip; the index draws the first thirteen, the COVID-19 page all fifteen. No choice is editable: the pages
have no input, and every figure is fixed when the table is built or the page is drawn.

| # | Key | The choice | Default | Source |
|---|---|---|---|---|
| 1 | `window` | each event a fixed window of local days, both ends included | each event's dates (sections above) | each event's section |
| 2 | `baseline` | the same weekday 364 and 728 days earlier | Uri the same calendar days of 2019 and 2020; COVID-19 2019 and 2018 (the Lower 48 2019) | "Baseline: weekday-aligned", "Session 49" |
| 3 | `local-day` | the grid's own local day (MISO Eastern Standard Time all year) | each grid's zone | "The second event: COVID-19" |
| 4 | `complete` | a day only when every interval is held; nothing filled | complete days only | "Complete days only" |
| 5 | `served` | demand served, not wanted | EIA-930 demand | "Demand during load shed is load served" |
| 6 | `peak-hour` | the day's highest hour over the mean of the baseline days' highest hours | `demand_max_pct_vs_baseline` | "Session 39" |
| 7 | `pick` | each figure the row its sentence's rule picks; the earlier day of equal values | the first in day order | "The figures on the pages, each with its table and rule" |
| 8 | `intensity` | CO2 from generation over net generation | kg CO2 per MWh generated | "Sources and variables" |
| 9 | `price` | ERCOT's hub average; four other hubs from 2024-09-01 | HB_HUBAVG; MISO hourly | "Session 64" |
| 10 | `spec` | weekday and year effects, the event year the average baseline year | `dow_year_mean_v1` | `event_study.md` |
| 11 | `inference` | 95 percent normal intervals, HC1 | z = 1.96 | `event_study.md`, "Inference" |
| 12 | `temperature` | degree days at 65 F and their squares at the grid's airports | the stations listed in `event_study.md` | `event_study.md` |
| 13 | `weather-share` | the share printed only when the two estimates share a sign and the second is no larger | under that condition | `event_study.md`, "What the pages say" |
| 14 | `after-order` | COVID-19: the deepest week from the week of 2020-03-22 | 2020-03-22 | Executive Order N-33-20 |
| 15 | `weeks` | COVID-19: Sunday to Saturday weeks, all fourteen days complete | thirteen weeks | "Weeks" |

## The replication and the cross-check (session 7531)

- **`replication/events/replicate.py`**, written from this note and `event_study.md` and the public table alone,
  standard library only. On the table retrieved 19 October 2026: every figure the ten pages print that is not held,
  1,149 of 1,149 (1,100 numbers and the event study tables' day counts) inside half the page's last shown digit, each
  pick the same row; the table's comparison rows recomputed from its level rows, 2,890 of 2,890; the 62 pooled
  estimates not held and their intervals against the builder's `event_study_estimates`, 186 of 186; fifteen sentences
  of the pages that state a fact of the rows, all true. The pages' figures come from the pages drawn with the site's
  own components (`site/scripts/events-pages.mjs`, with the hold set aside for the drawing only). `replicate.do` gives
  five headline figures in Stata. Run: `python replication/events/replicate.py` (on the rows copied beside it) or
  `--tables <the warehouse's output folder>`.
- **Held rows are not in the replication (session 7531's held-row fix, 16 November 2026).** The counts were 1,176 of
  1,176 and 195 of 195; they moved because the rows and figures of ISO-NE's, MISO's and NYISO's hubs are held (both
  tables "license needed", held by grid: `site/lib/license.ts` `licenseHeldRow`) and the replication sits in a public
  repository. It drops a held row as it reads it, counts the 27 page figures and 3 pooled estimates (9 numbers) of
  those hubs as "held, not recomputed here", and copies none of the 484 held rows of `event_window_daily` or the 3 of
  `event_study_estimates` beside it (each file's first line gives the count). A row of no grid (`eia930:NYIS`,
  `noaa:...`) is kept, as the rule keeps it.
- **The cross-check**: [`docs/reviews/events-crosscheck-2026-11-16.md`](../reviews/events-crosscheck-2026-11-16.md),
  sixteen rows against FERC's, CAISO's, ERCOT's, PJM's and EIA's own accounts. Every peak stands within 2.0 percent of
  the operator's; the differences are of definition (an instant against an hourly mean, losses allocated, settlement).

## The whole country (session 8410, 19 November 2026)

Each of the nine event pages has a section "The whole country", under the event study and above the decisions block,
and each event's card on `/events` has a line of regions. Nothing else on the ten pages changed: outside what was
added, each page is byte for byte what it was (`site/scripts/test-events-pin.mjs`, as a visitor's build draws it and
with the hold stood aside).

- **What it reads.** One file an event, `site/data/regions/events/<event>.json`, written by the data machine from
  EIA's Form EIA-930 in the form of the contract [`docs/state/page_files_regions.md`](../state/page_files_regions.md)
  (its section 6): for each of EIA's thirteen regions of the lower 48 (California, Carolinas, Central, Florida,
  Mid-Atlantic, Midwest, New England, Northwest, New York, Southeast, Southwest, Tennessee, Texas) the hourly demand,
  net generation, net imports and generation by eight sources over the event's window, the baseline of each, and the
  hourly flow between each pair of regions with its baseline. The window and the baseline days are the ones this note
  gives for the event. Six of the regions were on no page before: the Southeast, Florida, the Carolinas, Tennessee,
  the Northwest and the Southwest (none of the seven grids is in them).
- **Until a file is on the site** the section reads "not built yet" and draws no figure, and the card's line reads the
  same. A file that cannot be read as JSON is treated the same way. No value is filled in.
- **What it computes** (`site/lib/countryfiles.ts`), each a sum or a mean of what the file holds, over the hours the
  event and the baseline both hold: a region's demand over the window in GWh and its percent on the baseline; its
  highest hour, when it was (UTC) and the baseline at that same hour; the mean of its net imports and of the
  baseline's (above zero the region imported); each source's generation less the baseline's, in GWh. For a pair of
  regions: which sent and which took over the window (the sign of the window's sum; the file's flow is from the first
  code to the second), the mean in MW and the energy in GWh, and the same for the baseline. A null hour is left out of
  both sums. The baseline at an hour is the file's: the mean of that hour at each baseline offset that holds it. The
  older sections take each baseline day's own highest hour, so the two comparisons are not the same, and the head's
  hover says so.
- **A region is not a grid.** A region's figure is EIA's sum of its balancing authorities, so the Mid-Atlantic is not
  PJM and Texas is not ERCOT even where they cover nearly the same ground. The lead's hover says so.
- **The choice of region.** Two lists (Region A, Region B) in a form that needs no script; the address carries the
  choice (`?region=ten&b=car#whole-country`). The regions drawn first are the page's own: Texas for the two ERCOT
  events, California for the two CAISO events and COVID-19, the Mid-Atlantic for the three events whose first grid is
  PJM, and Tennessee and the Carolinas for Winter Storm Elliott (FERC and NERC, quoted on the page: the balancing
  authorities that shed firm load were in the southeast, among them TVA and Duke). A window of 21 days or less is
  drawn by hour; a longer one (COVID-19) by UTC day, the mean of the day's held hours.
- **"Reached N of 13 regions" on `/events`.** A region is counted when its demand over the window stood 5 percent or
  more from the baseline, above or below. The 5 percent is this page's own default (session 8410); no publisher's
  threshold stands behind it, and the hover says so and gives every region's percent.
- **What it does not do.** No estimate of a share of a shock covered by imports, no ledger of regions that gave and
  took: the pair table gives each pair's own flow and nothing is summed across pairs. No carbon intensity and no
  price by region (the file holds neither).
- **License.** EIA's Form EIA-930 is public domain and the contract gives every file as `public`. The section still
  reads the file's own license line and the status file (`site/data/license_status.json`) for each table the file
  names: a file that is not public is drawn with every cell blank and "license needed" on hover. The older sections'
  hold on `event_window_daily` stands as it was.
- **Tests.** `site/scripts/test-events-regions.mjs` (the section drawn from a fixture in the contract's form, whose
  values are made by a rule and are not data; the whole pages with and without a file) and
  `tests/test_session8410_events_regions.py`.
