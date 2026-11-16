# The data machine's eight tools: a signature pack for Samuel (16 November 2026)

Energy Research Warehouse (ERW). Written by session 7018 of chain 301 (`queue/done/301-day-16-november-desktop-open-faults.md`), the data machine (lab-desktop), for the eight tools `docs/state/done_line_claims.md` gives it (17 to 24), in the form of `docs/reviews/five-tools-signature-pack-2026-11-14.md`.

- **What a signature is.** You fill the three lines of the note's "Sign-off" block and commit them, or say them in a prompt and a session writes your words there. A session never signs.
- **What you sign accepts** the rules the decisions block lists, at their defaults. It does not freeze the figures: they move with the data.
- **The expected values** are those each tool's do-file states at its top, from the Python mirror's run of 16 November 2026. Each do-file is run from its own folder with the table it reads beside it (the tables are on Redivis and in the live set's downloads). None of the do-files has been run: Stata is not on the data machine.

---

## 17. The price board (`/board`)

**You sign:** `docs/methods/price_board.md`, section "Sign-off". It accepts the 11 decisions of its section "The decisions on the page".

**The five choices that move the figures most:**

| Choice | Default | Source |
|---|---|---|
| A power row's day is the mean of a complete local operating day: every hour of it held (24; 23 or 25 on the clock-change days), or every 15-minute interval; a day short of one is not drawn, never filled. | Complete local operating days only, in each grid's own time zone. | docs/methods/price_board.md, "Common rules"; the operators' day-ahead and real-time settlement point prices. |
| On-peak is the hours ending 7 to 22 local, Monday to Friday (CAISO Monday to Saturday), with NERC's holidays off-peak; every other hour is off-peak. | Hours ending 7 to 22 local on peak days; NERC holidays off-peak. | NERC's off-peak holidays and the industry's 5x16 block; docs/methods/price_board.md, the section on peak and off-peak hours. |
| A row is marked stale beside its date past 3 days for a power market's daily row, 10 for another daily row, 17 for a weekly one and 132 for a monthly one, and a stale row prints no move. | 3, 10, 17, 132 and 135 days by the row's step. | The owner's ruling of 18 October 2026 (EIA posts spot prices weekly and late); docs/methods/price_board.md, "The held rows and the stale closes". |
| Every spark spread is the day-ahead daily mean less 7.0 MMBtu/MWh times Henry Hub, an assumed combined-cycle heat rate and one gas price for every grid; it is labelled indicative. | 7.0 MMBtu/MWh and Henry Hub, with EIA's fleet heat rate beside it where held. | EIA, Electric Power Annual, Table 8.1 (the gas fleet's average heat rate, shown beside); EIA's Henry Hub spot price. |
| No futures price is drawn: NYMEX contracts 1 to 4 need CME Group's license, and EIA's copy of them ended on 5 April 2024, so each futures cell reads "licensed source needed". | Futures cells read "licensed source needed"; no figure. | CME Group's terms; EIA's NYMEX futures series, discontinued 5 April 2024. |

**Cross-checks** (the note's section "The cross-checks"):

- Henry Hub, June to September 2026: EIA's closes averaged by month against the World Bank's monthly averages, within 0.017 USD/MMBtu every month
- WTI and Brent, the same months: within 0.6 USD in four of eight months, up to 2.91 USD in the months of the widest moves (the World Bank compiles its own averages)
- Power hubs: no second public publisher held (ICE's indices are internal)

**Run it in Stata:**

```stata
cd "C:\path\to\erw\replication\board"
log using "board_stata_2026-11-16.log", text replace
do replicate.do
log close
```

**Expected** (the do-file's own header):

- 1. ERCOT hub average, day-ahead, 15 November 2026, USD per MWh:          37.2504
- 2. ERCOT hub average, day-ahead, mean of 9 to 15 November:               39.1464
- 3. CAISO SP15, day-ahead, 15 November:                                   31.3727
- 4. SPP North hub, day-ahead, 15 November:                                37.9086
- 5. ERCOT North less Houston, day-ahead, 15 November:                      2.3117  (37.5371 - 35.2254)

---

## 18. Power prices (`/prices`)

**You sign:** `docs/methods/power_prices.md`, section "Sign-off". It accepts the 8 decisions of its section "The decisions on the page".

**The five choices that move the figures most:**

| Choice | Default | Source |
|---|---|---|
| The real-time column is the newest interval each operator has published for the node, read every 15 minutes, so a price can be up to about half an hour old when the page is read. | The newest published interval, refreshed every 15 minutes. | The operators' real-time market data, read by the 15-minute loop (warehouse/connectors/latest_prices.py). |
| The day-ahead column is the hour that contains the time the page was drawn; where the table holds no such row, the cell says what it holds instead, its newest hour for the node or that it holds none of the last day. | The day-ahead hour containing the moment the page is drawn. | The operators' day-ahead market results; the owner's ruling of 20 October 2026 kept the column with these words. |
| PJM's prices are not shown: PJM licenses its market data for internal use only, so its grid is named and left without a figure. | PJM named, no figure. | PJM's terms for its market data, licensed for internal use only; docs/methods/power_prices.md, "The rules". |
| A grid whose price tables need a license from 20 October 2026 shows no price; the license line under the title names it, and its rows wait for the publisher's permission. | NYISO's and ISO-NE's prices held; the license line says why. | warehouse/metadata/license_status.csv and the publishers' own terms of use, read for each table. |
| MISO is paused since 4 October 2026: its terms forbid automated access, so no request goes to MISO and its rows are those held before the pause, or none. | No request to MISO; what is held stays. | MISO's terms of use; docs/methods/miso_pause.md. |

**Cross-checks** (the note's section "The cross-checks"):

- Every live price against the warehouse's own table of the same interval: 74,258 of 74,258 equal
- No second public publisher of the hub and zone prices is held; the operators' monthly market reports are not yet read

**Run it in Stata:**

```stata
cd "C:\path\to\erw\replication\prices"
log using "prices_stata_2026-11-16.log", text replace
do replicate.do
log close
```

**Expected** (the do-file's own header):

- 1. ERCOT hub average, day-ahead, the hour starting 2026-11-15 18:00 UTC:          32.29
- 2. CAISO SP15, day-ahead, the same hour:                                          13.34319
- 3. SPP North hub, day-ahead, the same hour:                                       34.2017
- 4. ERCOT hub average, real time, the interval starting 2026-11-14 18:00 UTC:      12.96
- 5. ERCOT West hub, real time, the same interval:                                  11.63

---

## 19. Where power is cheap (`/prices/compare`)

**You sign:** `docs/methods/hub_price_comparison.md`, section "Sign-off". It accepts the 9 decisions of its section "The decisions on the page".

**The five choices that move the figures most:**

| Choice | Default | Source |
|---|---|---|
| Two windows, each in the grid's own local time: the twelve months and the last whole month, both ending with the last calendar month that every hub of the history holds to its end, so no hub is compared over a month another lacks. | Twelve months and the last whole month, ending with the last month every hub holds. | docs/methods/hub_price_comparison.md, "The two windows". |
| A market of a hub is written when at least 95 percent of the window's hours are held, and a grid's carbon intensity when 90 percent of its days are; below that the cell names what is held, and nothing is filled. | 95 percent of the hours; 90 percent of the days for carbon. | docs/methods/hub_price_comparison.md, "When a figure is not written". |
| The share of hours below zero counts an hour whose mean, rounded to nine places, is below zero, so an hour of four prices that sum to exactly zero is not negative. | Below zero after rounding the hour's mean to nine places. | docs/reviews/price-compare-faults-2026-11-16.md, row 1; warehouse/derived/price_compare.py, hourly(). |
| The share of hours priced above USD 200 per MWh is the page's measure of scarce hours: one round threshold for every grid, not each operator's own scarcity signal. | USD 200 per MWh on every grid. | The page's own choice; docs/methods/hub_price_comparison.md, "The measures". |
| The carbon intensity beside a hub is its grid's average generation by day, the same figure for every hub of a grid, not the marginal plant's and not the hub's own. | The grid's average carbon intensity of generation. | EIA-930's hourly emissions by balancing authority, California by the warehouse's join. |

**Cross-checks** (the note's section "The cross-checks"):

- Every figure recomputed: 578 of 578 after one fault fixed (an hour of zero counted below zero)
- No second public publisher of the same hub averages is held; the operators' annual reports are not yet read

**Run it in Stata:**

```stata
cd "C:\path\to\erw\replication\compare"
log using "compare_stata_2026-11-16.log", text replace
do replicate.do
log close
```

**Expected** (the do-file's own header):

- 1. ERCOT hub average, mean price, USD per MWh:          34.30
- 2. ERCOT hub average, hours held:                       8,760
- 3. ERCOT West, share of hours below zero, percent:       7.42
- 4. ERCOT West, share of hours above USD 200, percent:    0.78
- 5. ERCOT Houston, mean price, USD per MWh:              35.22

---

## 20. Supply and trade (`/supply`)

**You sign:** `docs/methods/supply_and_trade.md`, section "Sign-off". It accepts the 11 decisions of its section "The decisions on the page".

**The five choices that move the figures most:**

| Choice | Default | Source |
|---|---|---|
| Every series is set against three values, each actually held: the period before, the same time last year and the five-year average; nothing is filled or estimated, and a comparison not held reads "not held". | The week or month before, last year, and the five-year average. | docs/methods/supply_and_trade.md, "The three comparisons". |
| The five-year average is the mean of the values 52, 104, 156, 208 and 260 weeks back (the same month of the five years before), given only when all five are held, with their lowest and highest beside it. | All five years held, or no average. | docs/methods/supply_and_trade.md, "The three comparisons". |
| The surprise is the period's change less the mean of the same change in the five years before, marked outside when beyond their lowest or highest; the page never says "against expectations", since no analysts' consensus is held. | Against the five-year average change, never a consensus. | docs/methods/supply_and_trade.md, "The surprise": the analysts' polls are licensed. |
| Fuel burned for power is derived, not reported: each grid's hourly gas, coal and oil generation, summed over whole local days, times a stated fleet heat rate (natural gas 7.6 MMBtu per MWh), so a grid's real fleet differs. | Stated fleet heat rates; whole local days only. | EIA-930's hourly generation by fuel; EIA's Electric Power Annual, Table 8.1, for the heat rates. |
| Weekly natural gas production is not shown: EIA publishes none of its own, and the weekly supply figures in its Natural Gas Weekly Update are S&P Global's, so the row reads "licensed source needed". | The row greyed, licensed source needed. | EIA's Natural Gas Weekly Update credits S&P Global for its weekly supply figures. |

**Cross-checks** (the note's section "The cross-checks"):

- EIA's weekly crude production, averaged by month, against its Petroleum Supply Monthly, February to July 2026: within 0.0 to 2.8 percent, the weekly below the survey from March

**Run it in Stata:**

```stata
cd "C:\path\to\erw\replication\supply"
log using "supply_stata_2026-11-16.log", text replace
do replicate.do
log close
```

**Expected** (the do-file's own header):

- 1. Working gas in storage, Lower 48, week of 2026-11-06, Bcf:                 3,862    (week before +61)
- 2. Its five-year average (the values 52, 104, 156, 208 and 260 weeks back):    3,808.6
- 3. Commercial crude oil stocks, million barrels:                               414.417  (week before +4.657)
- 4. Crude oil production, United States, thousand barrels a day:               14,013   (five-year average 12,792.4)
- 5. Refinery utilization, percent:                                              95.2

---

## 21. Battery storage (`/storage`)

**You sign:** `docs/methods/storage.md`, section "Sign-off". It accepts the 9 decisions of its section "The decisions on the page".

**The five choices that move the figures most:**

| Choice | Default | Source |
|---|---|---|
| Battery output is net generation as published: positive while the batteries discharge to the grid, negative while they charge, so a day's charging is the part below zero taken as a positive amount. | Positive discharging, negative charging. | EIA-930's battery series (fuel type BAT) and CAISO's Today's Outlook, both signed this way. |
| A day is the balancing authority's local day and counts only when every hour of it is held (23 or 25 on the clock-change days; for CAISO every 5-minute interval); a day short of one is left out, never filled. | Whole local days only. | docs/methods/storage.md, "Days" and "Completeness". |
| The day's energy out over energy in is not a measured efficiency: charge held across midnight moves it, and so do batteries reported under other fuels (solar or wind with integrated storage). | Shown as out over in, labelled not an efficiency. | docs/methods/storage.md, the daily cycle's notes. |
| California is drawn from CAISO's own 5-minute battery data, not EIA-930's, which CAISO does not report as BAT; it includes the batteries of hybrid plants, which CAISO publishes inside its total. | CAISO's own data for California, labelled as CAISO's. | CAISO, Today's Outlook, battery storage history ("Total batteries"). |
| The fleet is every generator with EIA's prime mover "Batteries" in EIA-860M, at its nameplate MW and, where EIA gives it, its nameplate energy; the page's sums by status, grid, state and planned year are sums of those rows and nothing else. | EIA-860M battery units at nameplate; sums of the rows only. | EIA-860M, Monthly Update to the Annual Electric Generator Report. |

**Cross-checks** (the note's section "The cross-checks"):

- Each grid's EIA-860M nameplate against the highest output its own reporting shows: CAISO 13,441 of 17,265.5 MW (78 percent), ERCOT 11,928 of 19,194.6 (62), MISO 931 of 1,175.9 (79), ISO-NE 516 of 1,021.7 (51), SPP 447 of 490.5 (91)

**Run it in Stata:**

```stata
cd "C:\path\to\erw\replication\storage"
log using "storage_stata_2026-11-16.log", text replace
do replicate.do
log close
```

**Expected** (the do-file's own header):

- 1. operating batteries:                       1,156
- 2. operating MW, every grid:                 56,120.7
- 3. operating MWh, every grid:               154,272.4
- 4. operating MW in ERCOT, and in CAISO:      19,194.6 and 17,265.5
- 5. planned MW with a planned year of 2027:   26,847.5

---

## 22. Demand growth (`/demand`)

**You sign:** `docs/methods/demand_growth.md`, section "Sign-off". It accepts the 9 decisions of its section "The decisions on the page".

**The five choices that move the figures most:**

| Choice | Default | Source |
|---|---|---|
| Weather is not removed: a year's demand is what was metered that year, heat waves and cold snaps included, so growth between two years is the difference of what was metered, not of a normal year. | As metered; the weather view removes it. | EIA Form EIA-930, hourly demand by balancing authority; docs/methods/demand_weather.md for the second view. |
| An hour is used when its demand is held, above zero and within 25 percent of the median of the four hours around it, since EIA's file holds faulty hours and a faulty high hour would be a year's peak; nothing is filled. | Within 25 percent of the median of the four nearest held hours. | docs/methods/demand_growth.md, "Which hours are used": the steepest real ramps move about a tenth in an hour. |
| Growth is measured against 2019, the last whole year before the pandemic in the file, and the newest partial year is set against the same months of every earlier year. | 2019 as the base; the year to date against the same months. | docs/methods/demand_growth.md, "The rows". |
| The Lower 48 has averages and no peak: its demand is EIA's sum over every balancing authority, faulty hours included, and such an hour passes the screen while it would set the peak. | No peak for the Lower 48. | docs/methods/demand_growth.md, "The Lower 48 has no peak". |
| California's hours of November 2023 to 2 December 2025 are read one hour earlier, since EIA dated them one hour late; a row that would land on an hour already held is dropped and the emptied hour is not filled. | Set back one hour, 31 October 2023 23:00 to 2 December 2025 23:00 UTC. | docs/methods/eia930_caiso_break.md, "The late hours": against CAISO's own data and against the sun. |

**Cross-checks** (the note's section "The cross-checks"):

- ERCOT's own hourly load against EIA-930's ERCOT: yearly means within 0.5 percent (2019, 2023, 2024, 2025), every year's peak in the same hour
- CAISO's own load against EIA-930's California: 99.50 to 99.61 percent from 2021 to 2025, 100.02 in 2026

**Run it in Stata:**

```stata
cd "C:\path\to\erw\replication\demand"
log using "demand_stata_2026-11-16.log", text replace
do replicate.do
log close
```

**Expected** (the do-file's own header):

- 1. ERCOT 2019 average demand, MW:          43,797.6
- 2. ERCOT 2025 average demand, MW:          55,717.2
- 3. ERCOT 2025 hours used:                   8,736   (EIA's file is blank for 24 hours of December 2025)
- 4. ERCOT 2025 peak hour, MW:               83,597   (the hour from 2025-08-18 22:00 UTC)
- 5. growth of the average since 2019, %:     27.22

---

## 23. Curtailment (`/curtailment`)

**You sign:** `docs/methods/curtailment.md`, section "Sign-off". It accepts the 11 decisions of its section "The decisions on the page".

**The five choices that move the figures most:**

| Choice | Default | Source |
|---|---|---|
| Each grid's number is what that grid publishes: CAISO's and SPP's own curtailment, ERCOT's output below the High Sustained Limit as the ERW's estimate, and no figure for a grid that publishes none or needs a license; the three are not comparable and are never summed. | Each operator's own figure, labelled; never a sum across grids. | CAISO's production and curtailment data and Daily Renewable Report; SPP's curtailment reports; ERCOT's hourly wind and solar reports. |
| ERCOT publishes no curtailment figure: output below the limit is max(0, limit less output) each hour, wind and solar each on its own, and includes ramping, telemetry and averaging, so the page calls it "output below HSL", never curtailment. | Called output below HSL; the ERW's estimate. | ERCOT, Hourly Averaged Actual and Forecasted Values (wind NP4-742-CD, solar by region); docs/methods/curtailment.md, "ERCOT". |
| A share is curtailed MWh over curtailed plus wind and solar output, over the days of the month both are held, written when those days hold at least 95 percent of the month's hours; one output source a month, nothing scaled up to a whole month. | Over the days both are held; 95 percent of the month's hours. | docs/methods/curtailment.md, "The share of available output". |
| California by the hour, by month and by reason counts a month when at least 90 percent of its days are held, its figure the sum over the days held, never scaled up; hours and months are Pacific. | 90 percent of the days; Pacific time. | CAISO's five-minute curtailment record and its daily report by hour from 2026; docs/methods/caiso_curtailment_intervals.md. |
| What curtailment is worth values each hour's curtailed MWh at the hub's price of that hour, a month written when the curtailment covers 90 percent of its days and the price 95 percent of its hours; an hour with no price is left out of both sides. | Each hour at the hub's price; 90 and 95 percent coverage. | docs/methods/curtailment.md, "What it is worth". |

**Cross-checks** (the note's section "The cross-checks"):

- EIA, Today in Energy, 28 May 2025: CAISO curtailed 3.4 million MWh in 2024, up 29 percent, solar 93 percent; the page's file 3,423,377 MWh, 28.7 and 93.3
- ERCOT's two reports: at most 0.12 MWh apart on the days both are held

**Run it in Stata:**

```stata
cd "C:\path\to\erw\replication\curtailment"
log using "curtailment_stata_2026-11-16.log", text replace
do replicate.do
log close
```

**Expected** (the do-file's own header):

- 1. solar curtailed, 2025, MWh:          3,482,322.8
- 2. wind curtailed, 2025, MWh:             283,305.3
- 3. solar curtailed, October 2026, MWh:    154,267.6
- 4. wind curtailed, October 2026, MWh:      28,197.5
- 5. days held in October 2026:                  31

---

## 24. The interconnection queue (`/queues`)

**You sign:** `docs/methods/interconnection_queue_summary.md`, section "Sign-off". It accepts the 9 decisions of its section "The decisions on the page".

**The five choices that move the figures most:**

| Choice | Default | Source |
|---|---|---|
| Every figure is from Berkeley Lab's yearly Queued Up data file, one row a request through the end of 2025; a newer request is not in it, and the next edition replaces every figure. | The 2026 edition, through 2025. | Lawrence Berkeley National Laboratory and GridTracker, Queued Up: 2026 Edition data file (CC BY 4.0). |
| Technologies follow Berkeley Lab's cleaned type: solar, solar with storage, storage alone, onshore wind, offshore wind and gas each on its own, and every other type and hybrid in one "other"; storage alone and solar with storage are kept apart from solar. | Seven groups from the cleaned type, hybrids apart. | The data file's cleaned type field (type_clean). |
| Completion and withdrawal shares are taken over requests that entered from 2000 to five years before the edition's last year, with a known status, so recent years, still mostly open, do not read as a low completion rate. | Entered 2000 to 2020 for the 2026 edition. | docs/methods/interconnection_queue_summary.md, "Past requests". |
| A share is written only from at least 20 past requests and a median only from at least 5 dated ones; below that the cell reads "not held", since one project would move a smaller share by five points or more. | 20 requests for a share; 5 for a median. | docs/methods/interconnection_queue_summary.md, "When a figure is not written". |
| Years to operation are the days from the request to the operation date over 365.25, for requests that reached operation with both dates in order; a request dated the other way round is left out, and ISO-NE, whose operating requests carry no date, has no median. | Dated requests only, both dates in order. | The data file's request and operation dates. |

**Cross-checks** (the note's section "The cross-checks"):

- Berkeley Lab's own summary of the 2026 edition: solar 773 GW (the file 772.6), gas 253 (252.8), wind 220 (219.7); storage approximately 749 GW against 552.7 in the file's parts, not reconciled

**Run it in Stata:**

```stata
cd "C:\path\to\erw\replication\queues"
log using "queues_stata_2026-11-16.log", text replace
do replicate.do
log close
```

**Expected** (the do-file's own header):

- 1. requests in the file:                                           38,201
- 2. MW requested (positive capacities only):                      7,098,748.5
- 3. active requests, and their MW:                                  8,513 and 1,864,963.3
- 4. of the 22,344 requests entered 2000 to 2020 with a known
- 5. median years from request to operation (3,098 requests):         3.58

---

## The rulings waiting (each with its default; the default stands until you rule)

- Curtailment: ERCOT's wind limit at the autumn hour of 1 November 2026 (`docs/reviews/curtailment-faults-2026-11-16.md`, row 3); default: the hourly row as published, the day not whole.
- The queue: the storage difference against Berkeley Lab's summary; default: the file's parts as filed.
- The board and the price pages: whether ICE's indices, as EIA republishes them, may be printed; default: held internal.
- Every grid held for a license or paused (PJM, NYISO, ISO-NE, MISO); default: named with the reason, no figure.
