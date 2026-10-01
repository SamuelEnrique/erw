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

## Not here

- The demand of the BAs outside the seven ISOs.
- Interchange before 2026-09-13.
- Flows by transmission line: EIA-930 reports BA-to-BA totals only.
