# Session 120 report: what Texas batteries did in real time, beside the day-ahead floor and the model

**Built, deployed as a review page, and honest about one thing it could not get.** The real-time side is on `/cost-of-power/battery/awards` as its last section, from 186 days of ERCOT's 60-Day SCED disclosure. Real-time energy is valued at the hub average's price, not at each battery's node: the node prices of the disclosed days are not public at any ceiling. No live page changed (snapshot below).

**Verdict: not ready to open.** The page is correct for what it says, and it says first what it leaves out. It is not yet "what Texas batteries earned": the node price is a stand-in, the real-time ancillary money is not valued, and contracts are in no public file. What is left is at the end, with three pulls that need your approval.

## Read these first

1. **The answer so far, February to July 2026, per kW of the fleet's MW.** Day-ahead awards: USD 4.17. Real-time deviations at the hub average's price: USD 3.00. The two together: USD 7.17. The battery page's model (one 2-hour battery on its day-ahead schedule) makes USD 18.81 over the same six months. So real time adds about three quarters again to the day-ahead floor, and the two together are 38 percent of the model's figure.
2. **Two thirds of what the fleet does is not sold day-ahead.** Over the 186 days it discharged 4,623,251 MWh in real time and had sold 1,483,064 MWh day-ahead: 32 percent. That is the reason the day-ahead floor is so far below the model.
3. **ERCOT's public list keeps seven days of node prices.** The storage disclosure is 60 days old when it is posted. So the node prices of a disclosed day left the list 53 days before the disclosure appeared. "Real-time settlement point prices at their nodes for the same days" cannot be pulled, at any ceiling. I pulled the week that is listed and used it for one thing only: to measure how far the nodes stand from the hub.
4. **The hub price understates, and the week shows by roughly how much.** From 28 September to 4 October 2026 the daily spread between the four dearest and four cheapest hours averaged USD 28.27 per MWh at the hub average. At the 291 storage settlement points the median was USD 44.29, and 227 of the 291 were wider than the hub. This is applied to no figure. Nothing is adjusted by it.
5. **The download ceiling cut the span.** From 6 December 2025 ERCOT lists 13.4 GB of daily zips (15.2 GB with supplements). The ceiling was 12 GB. I took the most recent months that fit: 1 February to 5 August 2026. The 57 days from 6 December to 31 January were not pulled, and the page says so.
6. **Real-time ancillary awards are in the file; their prices are not.** The quantities are in the table and on the page, with no dollar figure put on them.
7. **Real-time energy is telemetry, not the meter.** The disclosure's metered file does not hold the storage resources (none of the 339 on 5 August 2026).
8. **One thing of mine that would have changed a live page, caught before the load.** The node prices' report (NP6-905-CD) was already in the source registry, on `/terms`. My connector reworded its row and I had put it under a hold, which would have taken it off `/terms`. Both undone before anything was loaded; a test holds the row's words.

## The numbers, by month

USD per kW of the fleet's MW. Real time is at the hub average's price (`HB_HUBAVG`).

| Month | Days | MW | Day-ahead awards | Real-time deviations | Together | The model's | Together, share of the model's |
|---|---|---|---|---|---|---|---|
| February 2026 | 28 of 28 | 17,722 | 0.45 | +0.41 | 0.86 | 2.20 | 39% |
| March 2026 | 31 of 31 | 18,970 | 0.70 | +0.62 | 1.33 | 2.80 | 47% |
| April 2026 | 30 of 30 | 19,955 | 1.13 | +0.99 | 2.12 | 5.12 | 42% |
| May 2026 | 31 of 31 | 19,709 | 0.72 | +0.35 | 1.07 | 3.53 | 30% |
| June 2026 | 30 of 30 | 20,557 | 0.48 | +0.18 | 0.67 | 2.29 | 29% |
| July 2026 | 31 of 31 | 21,365 | 0.68 | +0.44 | 1.12 | 2.87 | 39% |
| August 2026 | 5 of 31 | 21,207 | 0.12 | +0.07 | 0.19 | not set beside a partial month | |
| **February to July** | 181 | | **4.17** | **+3.00** | **7.17** | **18.81** | **38%** |

Source: `ercot_storage_rt_monthly` (this session) and `battery_stack_monthly`, variable `dayahead_2h_revenue_total_usd_per_mw`. The page computes every figure from the tables when it is rendered; a test sets the method's figures against the table.

**Checks on these figures.**

- In each of the seven months, the day-ahead revenue, the MWh sold and the MW equal `ercot_storage_dam_awards_monthly`'s (session 115). The builder writes nothing if they differ.
- All 186 days are matched by the day-ahead disclosure. Every one of the 17,852 Settlement Intervals has a hub price: every resource-interval is valued.
- The hub price is on the right clock. ERCOT's own node files hold the hub average too: over the 577 intervals both hold, the warehouse's hub price and ERCOT's file agree to the cent in every one. Shifted by one interval they differ by USD 2.54 on average.
- One resource-hour is recomputed by hand in exact decimals in the tests, without the reducer's code.

**Energy, 186 days.**

| | MWh |
|---|---|
| Discharged in real time | 4,623,251 |
| Sold day-ahead | 1,483,064 (32% of discharged) |
| Charged in real time | 5,614,106 |
| Bought day-ahead | 1,058,095 |

1.26 MWh discharged per MW of the fleet per day. MWh out over MWh in: 0.82 (telemetry; not an efficiency, since what is stored at the start and the end differs).

**Day-ahead, node against hub** (USD per MWh, weighted by MWh): the fleet sold at its own nodes for 0.02 to 2.49 above the hub average by month (August's five days: 0.18 below) and bought for 1.89 to 4.90 below it. Small on the selling side; the buying side is where the nodes help.

**Real-time ancillary awards, 186 days, MW for an hour.** Not valued.

| Service | Real time | Day-ahead | Real time less day-ahead |
|---|---|---|---|
| Regulation Up | 2,170,700 | 2,171,357 | -658 |
| Regulation Down | 1,837,845 | 1,705,083 | +132,762 |
| Responsive Reserve | 6,564,769 | 5,460,586 | +1,104,184 |
| ECRS | 5,146,786 | 3,879,678 | +1,267,108 |
| Non-Spin | 6,935,800 | 5,464,805 | +1,470,995 |

In three of the five services the fleet holds a fifth to a third more reserve in real time than it was awarded day-ahead. ERCOT pays that difference at real-time prices the warehouse does not hold. It is the largest known piece of market revenue still missing.

## Measured first, then pulled

| | Measured | Ceiling | Taken |
|---|---|---|---|
| SCED disclosure from 6 December 2025 | 249 zips, 15.2 GB (243 daily zips: 13.4 GB) | 12 GB | 186 daily zips, 1 February to 5 August 2026: 10.42 GB |
| Node prices | 690 interval files listed, 7 days | the same 12 GB | 690 files, 5.6 MB |
| **Downloads in all** | | **12 GB** | **10.43 GB** |
| **Stored rows in all** | one day: 8,136 resource-hours | **9,000,000** | **1,675,014** |

- One day was measured first (5 August 2026): 98,310 rows for 339 resources in a file of about 100 MB of text.
- Each day was reduced to resource-hours as it was read, and written before the next zip was asked for. The zips are kept under `warehouse/raw/ercot_60d_sced/zips/` with a manifest (document id, bytes, SHA-256, when).
- 186 of 186 days reduced. None missing, none refused by a check. 119 requests in the last run; no zip asked for twice.
- USD 0. No model call.

| Table | Rows | What | Where |
|---|---|---|---|
| `ercot_sced_esr_hourly` | 1,458,735 | a storage resource and an hour: energy, its four 15-minute intervals, limits, state of charge, real-time awards | archive, Redivis draft; not loaded (`catalogue_hold`) |
| `ercot_rtm_node_prices` | 213,900 | a settlement point and a 15-minute interval, the week listed | archive, Redivis draft; not loaded (`catalogue_hold`) |
| `ercot_storage_rt_monthly` | 329 | the fleet by month | archive, Redivis draft, Supabase under `review_hold` |
| `ercot_storage_node_basis` | 2,050 | each storage node against the hub, the week | archive, Redivis draft, Supabase under `review_hold` |

All four pass the validator (exit 0). Nothing was released on Redivis.

## How ERCOT settles a storage resource since 5 December 2025

Read from the Nodal Protocols on 5 October 2026: Section 4 dated 1 August 2026, Section 6 dated 28 August 2026. The method page (`docs/methods/ercot_storage_realtime.md`) has the table; in short:

- **4.6.2.1, Day-Ahead Energy Payment**, and **4.6.2.2, Day-Ahead Energy Charge**: the award times the day-ahead Settlement Point Price.
- **4.6.4.1, Payments for Ancillary Services Procured in the DAM**: the award times the service's day-ahead clearing price.
- **6.6.3.1, Real-Time Energy Imbalance Payment or Charge at a Resource Node**: by 15-minute interval, the metered output at the node's price, and the day-ahead position (a quarter of the hour's award) settled back at the node's real-time price. What is settled in real time is the deviation from the day-ahead position.
- **6.6.3.1, charging**: `RTRMPRESR_b = Max[-$251, (sum of RNWFL * RTLMP at the bus) + RTRDP]`. An ESR's charging is settled at the price at its own bus.
- **6.7.2.1, Real-Time Ancillary Service Imbalance Payment or Charge** (6.7.2.2 to 6.7.2.6 by service): the real-time award less the day-ahead award, at the service's real-time price.
- **6.6.5.5 and 6.6.5.5.1, ESR Set Point Deviation Charges**: left out.

The tables follow the first four with one substitution: the hub average's real-time price where the protocols have the node's.

## What it still leaves out

Stated first on the page, in this order: contracts; the price at each battery's own node; real-time ancillary service money; charges and credits of the settlement statement; the meter. And the 57 days before 1 February.

## The live pages

One deploy: `task/120-storage-realtime`, run 37295486421, merged to main as `a6e6d5d`. One load into Supabase: the two small tables, both under `review_hold`. No freeze was in force (`scripts/freeze.py status`: exit 0).

Snapshots `before-120` (09:45 UTC, before the load and the deploy) and `after-120` (10:23 UTC, with production serving the new section): 25 pages, 4,098 checked numbers each, 0 failed reads.

**36 differences, all of them the clock. None is this session's.**

| Page | Differences | What | Expected |
|---|---|---|---|
| `/` | 30 | the price board's newest real-time interval of five hubs (for example ERCOT 08:45 UTC at 37.02 became 09:45 UTC at 35.88), with their lines of text and two "days in the ERW table" ages (5.8 to 5.7; 3.8 to 3.7) | yes: the 15-minute price job |
| `/network` | 6 | "refreshed 09:05 UTC" became "10:05 UTC"; the ISOs' newest demand hour 07:00 became 08:00 UTC; the build stamp in the source line | yes: the hourly network refresh |
| `/about`, `/storage`, `/cost-of-power/seller` (three views), `/cost-of-power/battery` (thirteen views), `/terms`, the four methods pages | 0 | | |

The home page's counts of rows and public tables did not move, and `/terms` did not move: the four tables and the two new sources are under their holds, and the node prices' report kept its row.

The full comparison is `runs/snapshots/` (`before-120`, `after-120`) and `runs/session120/snap_compare.out` on this machine.

## For your approval: three pulls, none scheduled

1. **Keep the node prices from now on** (NP6-905-CD). ERCOT's list drops a day after seven. The daily price job already reads this report for the hub prices of the latest intervals and keeps only the hubs (`warehouse/connectors/ercot_prices.py`). I did not check whether it reads all 96 files of a day; if it does, keeping the storage nodes' rows adds no request to ERCOT, and if not, it adds about 96 small files a day. From the day it starts, a day's node prices meet its storage disclosure 60 days later, and real-time energy can be valued at the node, as the protocols settle it. Each day that passes without it is a day that cannot be had later. About 30,000 rows a day.
2. **Real-time ancillary service prices** (the real-time clearing prices for capacity since 5 December 2025), to value the imbalance quantities above. A new report; USD 0; I did not look for its size, since it was not among the approved pulls.
3. **The 57 days from 6 December 2025 to 31 January 2026** of the SCED disclosure: about 3 GB, about 440,000 rows. ERCOT's list still holds them.

## Decisions made without you

- **The hub average as the stand-in**, named `_hub` in every variable and "at the hub average's price" wherever a figure stands. The alternative was no real-time dollar figure at all.
- **Charging at the same price as discharging.** The protocols settle charging at the bus price, which is not public either.
- **1 February as the start**: whole months, the most recent that fit under 12 GB.
- **A run's value holds until the next SCED run of the day, never across a run the resource is not in.** My first rule held a value to the resource's own next row and refused three days (below).
- **A Load Zone's `LZ` row is kept, its `LZEW` row is not.** ERCOT prints both under one name and the prices can differ (4 of 12 pairs in the first file).
- **One page of ERCOT's site read once**, to confirm the SCED report's product id (NP3-965-ER) in place of a guess. Not a data pull.
- **A day with a repeated hour (the autumn clock change) is left out with its reason.** None is in the months pulled; a rule never run on one is not trusted with one.

## Errors, and what caught them

| What | Caught by | Now |
|---|---|---|
| The reducer read ERCOT's Central stamps as they stood: 8 March was "a gap of 65 minutes" and refused | the pull's own check | stamps go to UTC first; the day is 23 hours; a test on real rows of that day |
| A value held to the resource's own next row: one resource that left the file at 00:30 on 5 February would have had 23 hours of its last five minutes; the day was refused | the gap check | the day's SCED clock; a test on real rows of that day |
| No rows written after that fix: a time zone lost in an assignment | the first re-run (0 resource-hours) | fixed before any table was written |
| A file's name stamp read as the interval's start; it is the end | my own test, on ERCOT's files | the interval is read from the file's columns |
| A settlement point "twice in one interval": every file refused | the same test | `LZ` and `LZEW` are two rows of one zone |
| The node table's values written as text: the shared writer failed after writing the file | exit 1 | numbers; rewritten |
| The registry row of NP6-905-CD reworded, and the source under a hold: `/terms` would have changed | reading the diff before the load | the row's words as they were; not held; a test |
| A reader with `comment="#"` | session 103's rule, in the full test run | `skiprows` |

The pull was restarted twice to reduce again with the corrected rule. No zip was downloaded twice.

## Tests

`tests/test_session120.py` (33) and `tests/test_session120_page.py` (17), on saved real samples: rows of ERCOT's own storage file for three days (5 August, 8 March, 5 February 2026), three of ERCOT's node-price zips whole, and real rows of two ERW tables. They hold, among others: one hour recomputed by hand; the clock-change day; the resource that leaves; what stops a day (seven cases); nothing filled for an hour with no run; a zip that would pass 12 GB is not requested; neither pull is on a schedule; an interval with no price is not valued and is counted; whole months only beside the model; the method's figures are the table's.

Full suite: 1,151 tests, exit 0. Site build exit 0. Route check exit 0 (16 live, 99 review).

## Verdict

**Not ready to open.**

What is left, exactly:

1. **Node prices.** Approve pull 1 above. Sixty days after it starts, the first month can be valued at the node. Until then the hub stand-in stays, labeled.
2. **Real-time ancillary money.** Approve pull 2; then value the imbalance by 6.7.2.1.
3. **December and January.** Approve pull 3.
4. **The page's title** still says "awarded day-ahead". When the real-time side is at node prices, the title and the lead should be rewritten around the three figures: the floor, the market total, the model.
5. **Not obtainable from public files, and to be said on the page for good:** contracts, the settlement meter, the statement's charges and credits.
