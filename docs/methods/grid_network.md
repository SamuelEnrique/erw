# The grid network: method

Energy Research Warehouse (ERW), session 49 (the plan of session 42). Three derived products from EIA-930's hourly interchange:

- `grid_network_nodes`: one entity per balancing authority (BA).
- `grid_network_links`: each BA pair once per hour.
- `site/data/grid_network.json`: the snapshot `/network` draws.

The source table is `eia930_all_interchange`.

## The source: `eia930_all_interchange`

- **Route:** EIA API v2 `electricity/rto/interchange-data`, hourly, every pair EIA reports (no facet).
- **Connector:** `warehouse/connectors/eia930_interchange.py`.
- **Entities and columns:** one entity per reporting BA and neighbor, `eia930:<FROM>-<TO>`; `ba` is the reporter, lowercase; `x_to_ba` is the neighbor.
- **Values:** `interchange_mw`, EIA's megawatthours per hour, which is the hour's mean MW.
- **Time:** EIA's period is the hour's end in UTC (as for every EIA-930 route, `eia930.py`), so `ts_utc` is the hour's start.
- **Completeness:** per pair and UTC day, a pair-day missing any hour is not written. One `run_status` row counts them and names the first 20.

**The sign, checked against the data.** For each of the seven ISO BAs we summed its reported interchange over its neighbors for each hour from 2026-09-13 to 2026-09-28 (360 hours). We compared the sum with its net generation minus its demand, from `eia930_all_demand` and `eia930_all_generation`.

| BA | Mean of \|interchange - (net generation - demand)\|, MW | Mean of \|interchange + (net generation - demand)\|, MW |
|---|---|---|
| ERCO | 1.6 | 511.9 |
| NYIS | 0.4 | 5,201.7 |
| ISNE | 0.7 | 1,569.4 |
| CISO | 3,199.1 | 14,419.1 |
| MISO | 1,397.9 | 4,611.0 |
| PJM | 2,042.1 | 6,098.4 |
| SWPP | 978.1 | 2,626.8 |

- **Convention:** positive interchange means the reporting BA exports to the neighbor. Net generation minus demand is a BA's net export, and the sum matches it, not its negative.
- **ERCOT, NYISO and ISO-NE** match to within 2 MW.
- **CAISO, MISO, PJM and SPP** match less closely. Their reported interchange does not exactly close EIA's balance of generation and demand. That is a property of the data, recorded here.

**The pull (session 49):**
- **Window:** the approved pull was the last 30 days. They hold 236,808 rows, over the 150,000 ceiling, so the latest 18 complete UTC days were pulled, 2026-09-13 to 2026-09-30: 131,008 rows reported by the API.
- **Written:** 127,560 rows, 341 directed pairs.
- **Not written:** 465 pair-days missing an hour.
- **Daily:** the run adds the last 3 days, merged into the history.

## The pair rule

Each pair is reported by both of its BAs. In the network each pair is counted once:
- its flow is read from the BA whose code sorts first, as that BA reported it (positive = it exported to the other);
- in an hour that BA did not report, the flow comes from the other BA's report with the sign flipped.

`grid_network_links` holds the result for the latest 168 hours: entity `eia930:<A>-<B>`, A the code that sorts first, variable `flow_mw`.

## Nodes

`grid_network_nodes` holds one entity per BA in the window, with `x_name` (EIA's name) and `x_iso` (the ISO, where the BA is one):

- **`demand_mw` and `intensity_generation`:** the latest hour the warehouse holds, for the seven ISO BAs only (`eia930_all_demand`, `carbon_intensity_hourly`). The other BAs' demand is not pulled.
- **`interchange_volume_mwh`:** over the 168 hours, the sum of the absolute hourly flow on every link of the BA.

## The snapshot and the page

- **The file:** `warehouse/derived/grid_network.py` writes `site/data/grid_network.json`, holding the nodes and, per pair, 168 hourly flows. The daily run rebuilds it after the connector and commits it.
- **No Supabase database:** the page reads no table. Since session 54 it reads the hourly snapshot in Supabase Storage first, and this file is the fallback (next section).
- **Positions:** a 3D force layout (Fruchterman-Reingold, 600 steps, seed 42), links weighted by the square root of their mean flow. It is computed once per build and fixed on the page, so the picture does not re-settle while the hours play.
- **On the page:**
  - sphere size is demand (the ISO BAs) or interchange volume (the others);
  - color is carbon intensity from green to cardinal, grey where not held;
  - link width and particle speed follow the hour's MW, with particles running in the direction of flow.

## What refreshes hourly, and what daily (session 54)

| What | How often | By | Where |
|---|---|---|---|
| Links: interchange between each pair of BAs, the last 168 hours | every hour (not 14:00 UTC, when the daily run starts) | `warehouse/derived/network_hourly.py`, `.github/workflows/hourly-network.yml` | the public Supabase Storage bucket `erw-public`, object `network/grid_network.json` |
| Demand of the seven ISO BAs (sphere size) | every hour | the same | the same |
| Carbon intensity (sphere color) | daily | `warehouse/derived/grid_network.py`, in the daily run | `site/data/grid_network.json`, committed; the hourly run carries it over unchanged |
| Nodes, names and positions | daily | the same | the same; the hourly run never moves a node |

- **The hourly run** pulls the last 48 hours of EIA-930 interchange (every pair) and demand (the seven ISO BAs). It merges them onto the newer-built of the Storage object and the committed file: each pair-hour it pulled replaces the old one, the older hours of the 168 are kept, and the window ends at the newest complete hour. It uploads one JSON object holding the build time (`built`), the newest hour (`newest_hour`), the daily build it was merged onto (`base_built`) and the EIA URLs it read (`pull.urls`, key removed). It never writes to the database or to git.
- **Leaner runs (session 55):** each run first reads the interchange route's `endPeriod` from the route's metadata, which returns no data rows. When it equals the `endPeriod` the Storage object was built from (`pull.interchange_end_period`), the run skips the interchange pull: the links are carried over unchanged, only demand is pulled (about 330 rows instead of about 15,900), and the object records `interchange: "unchanged"` and, in `pull.interchange_pulled`, when the links were last pulled. A newer daily snapshot, or a moved `endPeriod`, brings back the full pull.
- **The newest complete hour:** the latest hour in which at least 90 percent as many pairs reported as in the median hour of the window. EIA's balancing authorities report at different speeds, so the last hours of a pull are partial (at 2026-10-01 17:00 UTC: 155 pairs at 03:00, then 121, 87 and 75). Those hours wait for a later run instead of being shown half filled.
- **The page** reads the Storage object with a one-hour revalidation. It draws that object when the object is whole and not older than the committed file. Otherwise, including when Storage is unreachable, it draws the committed file and says so. It shows the newest hour in UTC and Eastern, the refresh time, and the newest demand hour.
- **Check keys:** demand from the hourly run carries the key `netsnap|<BA>|demand_mw|<hour>`. check-values reads it from the Storage object's `demand_recent`, which keeps each ISO BA's last 48 hours, because the hourly run writes nothing to the database.

### Why the newest hour is not the current hour

EIA publishes each hour's EIA-930 data after the hour ends, and the period it states is the hour's end (`ts_utc` here is the hour's start).

- **Demand** is published one to two hours after the hour: at 17:00 UTC on 2026-10-01 the newest demand hour was 15:00 to 16:00 UTC.
- **Interchange between pairs of BAs** reaches the API's `interchange-data` route much later. At the same moment the route's `endPeriod` was 2026-09-30T07, about 34 hours behind the clock, while the BAs' total interchange (`region-data`, type `TI`) and demand were current.

So the network's links run more than a day behind the clock even when refreshed every hour. The hourly run still moves them forward as soon as EIA publishes: the daily build keeps complete UTC days only, so its newest hour was 2026-09-28 23:00, and the first hourly run moved it to 2026-09-30 03:00.

For this reason the hourly run pulls interchange for the 48 hours ending at the route's own `endPeriod`, not at the clock: 48 clock hours would have held only about 14 hours of interchange and left a hole between the daily build and the pull. That is about 16,000 rows a run, more than the few thousand first estimated, because most pairs are reported by both BAs, some 337 reports an hour.

**Context** (EIA, "U.S. electric system is made up of interconnections and balancing authorities", Today in Energy, https://www.eia.gov/todayinenergy/detail.php?id=27152):
- the Lower 48's power system "is made up of three main interconnections, which operate largely independently from each other with limited transfers of power between them";
- in ERCOT "the balancing authority, interconnection, and the regional transmission organization are all the same entity and physical system".

## Who supplies a grid (session 68)

Table `ba_supply_monthly` (derived, public; `warehouse/derived/ba_supply.py`), from `eia930_daily_interchange` (session 62: every pair, daily, from 2019) and `eia930_daily_total_interchange` (session 68: EIA-930's own total interchange of every balancing authority, type TI, daily, from 2019; 210,911 rows of a 300,000-row ceiling). A month's days are EIA's Eastern days, the day boundary of both tables. **Positive means the neighbour supplied the grid** (a net import): EIA's own sign is the opposite and is flipped once, in the builder.

**Three measures of a grid's net imports, side by side**, per balancing authority and month:

1. **The sum of its reported ties** (`net_import_pairs_mwh`): the grid's own report of each tie, summed.
2. **EIA's total interchange** (`net_import_total_interchange_mwh`): the figure EIA publishes for the grid as a whole.
3. **Demand less net generation** (`net_import_balance_mwh`): the balance, from EIA's hourly workbooks; held for the seven ISO grids only.

**Held days** follow session 62's rules: a day counts when every regular neighbour reported it (a regular neighbour reports on at least half of the month's days that have any report) and none of its pair-days was screened out. A pair-day is screened out when it is further than 10 median absolute deviations, at least 500 MWh, from the pair's own median over its history: 2,732 of 945,130 pair-days, among them SWPP-MISO on 2026-07-21 (2,159,056 MWh, more than SPP's whole daily demand). A month EIA reported nothing for is counted as left out, not skipped. `thin_month` is 1 when fewer than two thirds of the month's days are held. Every share is taken over the *share days*: held days whose demand is held too, so a numerator and its denominator cover the same days.

**What the three showed, September 2025 to August 2026, on the same days** (percent of demand):

| Grid | Sum of ties | EIA's total interchange | Demand less net generation |
|---|---|---|---|
| CAISO | 16.49 | 16.49 | 26.87 |
| ERCOT | 0.07 | 0.07 | 0.07 |
| ISO-NE | 4.96 | 4.96 | 4.96 |
| MISO | 2.54 | 2.54 | 0.17 |
| NYISO | 11.82 | 11.81 | 11.81 |
| PJM | -2.72 | -1.25 | -3.18 |
| SPP | -1.44 | -1.00 | -1.01 |

**CAISO's gap, found.** EIA's total interchange for CAISO equals the sum of its eleven ties to the MWh on every day both exist; none of CAISO's pair-days was missing or screened in the year; every neighbour that reports a tie with CAISO is one CAISO reports too (CEN, Mexico's operator, does not report back). So the interchange is consistent, and the gap is in the balance. CAISO's demand less net generation less its interchange was within about 2 percent of demand through 2024 and most of 2025, then rose in December 2025 to 70 to 93 GWh a day (10 to 15 percent of demand) from January 2026. Demand and interchange did not move: CAISO's published net generation fell (January 2026: 348 GWh a day against 457 GWh in January 2025). The residual correlates only weakly with CAISO's battery discharge (0.51) and is about 1.7 times as large, so batteries alone do not explain it. Why EIA's net generation fell is not in the data the warehouse holds. Until it is explained, the balance overstates California's imports: session 62's 27.02 percent is that measure.

Two of CAISO's ties also disagree between their two sides: the Arizona ties (AZPS, SRP) and TIDC and BANC report different flows from CAISO's on the same days (column `neighbor_report_mwh` holds the neighbour's own report). The headline uses CAISO's.

**The headline rule.** The sum of the ties is the headline: it is complete on every held day, it equals EIA's total interchange on the same days for CAISO, ERCOT, ISO-NE, MISO and NYISO, and the neighbours' shares add up to it. Where the three measures spread more than one point of demand over the twelve months (CAISO, MISO and PJM in session 68's data), the panel shows the range and says so.

**Who supplied CAISO**, over the panel's twelve months (October 2025 to September 2026), is in the panel and its folded table; the largest supplier is Nevada Power (NEVP).

## The stories (session 68)

`eia930_event_hourly_interchange` (266,833 rows of a 400,000-row ceiling; `warehouse/connectors/eia930_event_hourly.py`): EIA-930's hourly interchange of every pair and hourly demand of every balancing authority, for two windows only: Winter Storm Uri, 2021-02-07 to 2021-02-24 (Central days, 432 hours) and the June 2025 heat, 2025-06-20 to 2025-06-28 (Eastern days, 216 hours). The warehouse's own hourly interchange (`eia930_all_interchange`) starts in September 2026.

`warehouse/derived/network_stories.py` writes one compact snapshot per story (`site/public/network/story_<event>.json`, and the same object in the public Storage bucket `erw-public`), in the shape the network draws: the same nodes and positions as today's network, each pair counted once by the pair rule above, demand, each day's carbon intensity where held (the seven ISO grids; grey elsewhere), batteries where EIA-930 reports them and the warehouse holds them, and the real-time price of each ISO's main hub where a public price is held. Never filled: an hour neither side reported is blank, and each story states what is missing. Balancing authorities of the window that are not in today's network (in 2021: AEC, GLHB, GRIF, HGMA, SPC, WACM) are not drawn and are named.

"California's evening" needs no pull: it is the newest complete Pacific day of the live week.

## Batteries (session 68)

The Batteries switch draws one thin ring around a grid whose batteries are reported for the hour shown: fuller as they discharge, emptier as they charge, against that grid's largest hour in the range shown. Which grids: EIA-930's battery series as the warehouse holds it (`eia930_all_storage`: ERCOT, ISO-NE, MISO and SPP, from November 2024), and CAISO's own data for CAISO (`caiso_battery_storage`, from August 2025), because CAISO reports no battery series to EIA-930. NYISO and PJM report none. The warehouse does not hold EIA-930's battery series for the balancing authorities outside the seven ISOs, so no ring is drawn for them; that is a limit of the warehouse, not a finding that they have no batteries. In the Uri window no grid's batteries are held; in the June 2025 window, ERCOT's, ISO-NE's and MISO's.

## Not here

- The demand of the BAs outside the seven ISOs.
- Hourly interchange before 2026-09-13, except the two stories' windows (daily interchange is held from 2019).
- Flows by transmission line: EIA-930 reports BA-to-BA totals only.

## The replay's share of demand (session 109)

A replayed day of `/network/v3` now gives, for the grid chosen, its net imports as a share of its demand that day, and
each supplier's flow as a share of the same demand.

- **Demand** is `eia930_daily_demand` (`warehouse/connectors/eia930_daily_demand.py`, an approved pull of session 109):
  EIA's daily demand of every balancing authority, API route `electricity/rto/daily-region-data`, type D, EIA's Eastern
  day, from 2019-01-01. 190,512 rows for 71 respondents (balancing authorities and EIA's regions) to 2026-10-03, of a
  ceiling of 300,000. Public domain. EIA's terms (`https://www.eia.gov/about/copyrights_reuse.php`, read 4 October
  2026): "U.S. government publications are in the public domain and are not subject to copyright protection. You may
  use and/or distribute any of our data, files, databases, reports, graphs, charts, and other information products that
  are on our website".
- **In the replay's files** a day's demand is its MWh over the hours of that Eastern day (24; 23 or 25 on the two days
  the clocks change): the day's average MW, the scale the flows are on. So a tie's average MW over the grid's average
  MW is that supplier's share of the day's demand. 54 of the network's balancing authorities have a demand.
- **A day's demand is used** when it is above zero and between half and twice the median of the six days around it
  (three before, three after, those held). 109 days of the history fail that and carry no demand and no share. EIA's
  daily demand is its own sum of the hours it holds: a day with hours missing at the source can be far off, and that is
  what the band catches. A day inside the band can still hold one impossible hour (`docs/methods/impossible_hours.md`):
  PJM's 224,345 MW of 13 July 2020 adds about 4 percent to that day.
- **What a share is not:** a share of the grid's supply (its own generation is not in the replay), nor a contract. The
  flows are physical, between neighbours.
- The live week's shares are as they were: hourly demand of the seven ISOs. The live page `/network` does not draw the
  replay and is unchanged.
