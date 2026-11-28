# The grid network: method

Tables: `grid_network_nodes`

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
- a report above 20,000 MW, which no single tie carries, is set aside first (`SCREEN_MW`, in both builders), so the hour is read from the other BA's report, or is not held (since the ruling on the Grid tool audit of 26 November, finding 6; in the seven weeks the audit read, two such reports, SPP's of its MISO tie on 4 and 6 October, neither read by the pair rule).

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

## How far behind the newest hour is, and why (session 247)

Measured on 13 October 2026 at 07:57 UTC, with three reads of EIA (`runs/session247/probe_interchange.out` and `network_dry.out` on the data machine):

| What | Newest hour that is complete | Behind the clock |
|---|---|---|
| The page's file in Storage (built 07:05 UTC that day by the hourly job) | the hour beginning 2026-10-11 03:00 UTC | 53 hours |
| EIA's API route for interchange (`electricity/rto/interchange-data`) | the same hour: 340 reports an hour up to the period ending 2026-10-11T04, then 256, 181, 161, and 19 an hour after 07 | 53 hours |
| EIA's own bulk file (`EIA930_INTERCHANGE_2026_Jul_Dec.csv`, last modified 12 October 14:38 GMT) | the same hour: 297 pairs an hour up to the hour ending 04:00, then 220, 156, 135, and nothing after 07:00 | 53 hours |

- **The lag is EIA's, and both of its public routes have it.** The page's file was current to the publisher within the hour. There is no fresher public copy of EIA-930 interchange to read.
- **Why two days.** The hours after 04:00 UTC on 11 October are the first hours of that day in Eastern time, then Central, Mountain and Pacific. On the morning of 12 October EIA published each balancing authority's interchange through the end of its local day of 10 October, and not 11 October. So a local day's interchange is public on the second morning after it: between about 35 hours behind (just after EIA's morning update, about 14:30 UTC) and about 59 hours behind (just before the next).
- **What the builder adds to that: nothing but the partial hours.** It shows the newest hour in which at least 90 percent as many pairs reported as in the window's median hour. The three hours after it had 129, 97 and 88 of 157 pairs; showing them would draw a network with a third of its lines missing.
- **Demand is not behind.** EIA publishes demand one to two hours after the hour, and the page shows each grid's demand at its own newest hour.
- **What would close it:** another source of interchange (each operator's own real-time tie flows), which is seven connectors and, for four of the grids, a license or a ruling. Not built.

## Who supplies a grid (session 68)

Table `ba_supply_monthly` (derived, public; `warehouse/derived/ba_supply.py`), from `eia930_daily_interchange` (session 62: every pair, daily, from 2019) and `eia930_daily_total_interchange` (session 68: EIA-930's own total interchange of every balancing authority, type TI, daily, from 2019; 210,911 rows of a 300,000-row ceiling). A month's days are EIA's Eastern days, the day boundary of both tables. **Positive means the neighbour supplied the grid** (a net import): EIA's own sign is the opposite and is flipped once, in the builder.

**November and December 2025 in `eia930_daily_total_interchange` (session 3941, chain 267).** On 13 October 2026 EIA's API answered those two months short (334 and 735 rows against about 2,200 a month), and the connector kept the answer as the months' checkpoints and never asked again; on 14 November the API still answered 1,067 rows for the two. The connector now asks again for a past month whose checkpoint holds fewer than 90 percent of the other checkpoints' median rows a day (the last two years), and takes each balancing authority day the API still lacks from EIA's six-month file of the same form (`EIA930_BALANCE_2025_Jul_Dec.csv`, its "Total Interchange (MW) (Adjusted)" summed over the Eastern day), only when every hour of that day is in the file with a number. On July to October 2025 that sum equalled the API's daily value, rounded to the MWh, on 6,811 of 7,074 balancing authority days; the others differ by EIA's later revisions (PACW's most, then SOCO, AECI and LGEE by a few MWh). 2,779 days were filled (1,521 in November, 1,258 in December), each row's `source` the six-month file. The file holds no region (CAL, US48 and the other aggregates), so a region's day the API lacks stays absent.

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

## The map (session 180)

The page has two shapes, chosen at its top: **Network**, the free-floating network described above, which is how the page opens and which session 180 did not change, and **Map**, the same grids on the ground. The shape is kept in the address as `shape=map`, written after the view's own query; an address without it is the network, so every address shared before session 180 opens as it did.

**What the map draws, and from what.** Nothing of its own. The view, the hour or day the replay is on, the selected grid, the colors and the side panel are the network's (`site/app/network/Network.tsx`); the map (`NetworkMap.tsx`) draws them over each balancing authority's published boundary. A region has the color its sphere has: the carbon intensity of the grid's generation, on the same scale, with the same legend, grey where it is not held. A tie is a line between the two regions, as wide as the network draws it (0.4 plus 3 times the square root of its share of the period's largest flow), with an arrowhead at the importer and a dash that runs from the exporter to the importer, faster as the flow is larger. Hovering a region names the grid, as hovering a sphere does; clicking it opens the same panel. With a grid selected, it and its neighbours stay as they are and the rest is dimmed. The rings of the Batteries and Prices switches are drawn in the Network view only; on the map the panel holds their numbers. MISO's hub price reads "paused while terms are reviewed" and PJM's is not shown, in the same panel, on either shape.

**The boundary file is not yet held (10 October 2026).** The map reads one file, `site/public/network/ba_boundaries.json`. Until that file exists the map's frame says that the boundary file is not yet held and draws no region; nothing is sketched in its place, and no boundary is drawn from memory or by approximation. Session 180 was allowed five requests to find one public file of the boundaries and used all five without reaching one:

| # | Request (host `atlas.eia.gov`, EIA's U.S. Energy Atlas) | Answer |
|---|---|---|
| 1 | `/robots.txt` | 200, 190 bytes. `User-agent: *`, `Crawl-delay: 60`, and `Disallow:` for `/sites/`, `/admin/`, `/sessions/`, `/groups/`, `/people/`, `/workspace/`. The catalog and its files are not disallowed. |
| 2 | `/api/feed/dcat-us/1.1.json` (the catalog) | 200, 641,294 bytes. It lists 101 datasets, not the whole atlas, and none of them is the balancing authorities or control areas. |
| 3 | `/api/search/v1/collections/dataset/items?q=balancing&limit=50` | 404: `Collection with id "dataset" not found`. A wrong address; it cost one request. |
| 4 | `/api/search/v1/collections/all/items?q=balancing&limit=50` | 200, 397 bytes: `numberMatched` 0. |
| 5 | `/api/search/v1/collections/all/items?q=control&limit=50` | 200, 16,331 bytes: one match, "USA Current Wildfires" (Esri's), not a boundary layer. |

Five requests and 658,303 bytes against a ceiling of five and 200 MB. Request 2 was sent 50 seconds after request 1, ten seconds short of the 60 the robots file asks; the connector has refused a request sent too soon since then (`--min-gap`). The requests, their times and the sha256 of each answer are in the session's `requests.csv`.

**The second pull (session 180b, 10 October 2026): HIFLD's open catalog no longer exists at its address.** The owner then approved one layer, "Control Areas" of the Homeland Infrastructure Foundation-Level Data (HIFLD) open catalog on ArcGIS Hub, with at most ten requests and 300 MB. Six requests were sent and none reached the layer, its record or its license statement, so the file is still not held and the map's frame stands as it was:

| # | Request | Answer |
|---|---|---|
| 1 | `https://hifld-geoplatform.hub.arcgis.com/robots.txt` | 200, 147 bytes (its content type was not kept: the connector keeps an answer's headers from request 2 on). `User-agent: *`, `Crawl-delay: 60`, and `Disallow:` for `/sites/`, `/admin/`, `/sessions/`, `/groups/`, `/people/`, `/workspace/`: ArcGIS Hub's own file, the same lines as the atlas's. |
| 2 | `https://hifld-geoplatform.hub.arcgis.com/api/feed/dcat-us/1.1.json` (the catalog) | 500, 62 bytes, `application/json`: `{"error":"CONT_0001: Item does not exist or is inaccessible."}` |
| 3 | `https://hifld-geoplatform.hub.arcgis.com/api/search/v1/collections/all/items?q=Control%20Areas&limit=50` | 400, 81 bytes, `application/geo+json`: `{"message":"CONT_0001: Item does not exist or is inaccessible.","statusCode":400}` |
| 4 | `https://services1.arcgis.com/robots.txt` | 403, 11 bytes, no content type given: `Invalid URL` |
| 5 | `https://hifld-geoplatform.opendata.arcgis.com/robots.txt` (the catalog's other name) | 404, 31 bytes, `application/json`: `{"error":"Site does not exist"}` |
| 6 | `https://hifld-geoplatform.hub.arcgis.com/` (the front page) | 404, 30 bytes, `text/plain`, `Location: /404`: `Not Found. Redirecting to /404` |

Six requests and 382 bytes against a ceiling of ten and 300 MB; four requests were left unspent. The three requests after the first to `hifld-geoplatform.hub.arcgis.com` each waited the 60 seconds its robots file asks (the connector refused two that were sent early, before anything left the machine). What the answers say: the catalog's site is gone under both of its names, so its list of datasets, the layer's record and the layer's license statement cannot be read there. Request 4 went to the ArcGIS Online host that used to serve HIFLD's layers; that host's name came from the session's own recollection, not from an answer of the catalog, and only its robots file was asked for. The host answered 403, so there is no robots file to read: Python's standard reader, which is the connector's measure, treats a 403 on a robots file as "nothing may be asked", while RFC 9309 treats any 4xx as "no rule is stated". The stricter reading was kept: no layer, service list or item record was asked of that host, and no other host was tried. No license words are quoted for the layer because no statement of them was reached. Whether a layer of a retired catalog may be read from the host behind it, and under which words, is a ruling for the owner. The requests, their times, each answer's headers and the sha256 of each answer are in the session's `requests.csv` and beside it.

**The third pull (session 193, 11 October 2026): no published boundary answered, so the map is derived from counties and says so.** The owner allowed thirty requests and 300 MB, terms read first, and named three places to look in order. Twelve requests were sent, 9,917,072 bytes:

| # | Request | Answer |
|---|---|---|
| 1 | `https://www.eia.gov/robots.txt` | 200, 718 bytes. `Allow: /` for every agent, with a list of folders disallowed (among them `/global/`, `/scripts`, `/styles`, `/archive/`); none of the addresses below is in it. No delay is asked. |
| 2 | `https://www.eia.gov/about/copyrights_reuse.php` (the terms) | 200, 52,528 bytes: "U.S. government publications are in the public domain and are not subject to copyright protection. You may use and/or distribute any of our data, files, databases, reports, graphs, charts, and other information products that are on our website". It asks for an acknowledgment with the date. |
| 3 | `https://www.eia.gov/maps/layer_info-m.php` (EIA's list of map layers and their shapefiles) | 301, 0 bytes, `Location: https://atlas.eia.gov/search`. The list is gone; it points at the atlas, whose catalog and search session 180 read (no balancing-authority layer). The redirect was not followed. |
| 4 | `https://www.eia.gov/electricity/gridmonitor/dashboard/electric_overview/US48/US48` (the Hourly Electric Grid Monitor) | 200, 43,735 bytes: the page names its program, `main-62AHFAMH.js`. |
| 5 | `https://www.eia.gov/electricity/gridmonitor/main-62AHFAMH.js` | 200, 4,903,073 bytes. The map's shapes are inside the program: the states, and thirteen regions (`REG-CAL`, `REG-CAR`, `REG-CENT`, `REG-FLA`, `REG-MIDA`, `REG-MIDW`, `REG-NE`, `REG-NY`, `REG-NW`, `REG-SE`, `REG-SW`, `REG-TEX`, `REG-TEN`). A balancing authority is drawn as a bubble at one latitude and longitude. No boundary of a balancing authority is in it. |
| 6 | `https://api.github.com/repos/NREL/ReEDS-2.0/license` | 301, 206 bytes: the repository moved; the answer names `https://api.github.com/repositories/189060033/license`. |
| 7 | that address | 200, 3,120 bytes: BSD 3-Clause, "Copyright (c) 2023, Alliance for Sustainable Energy, LLC". Redistribution is allowed with the notice kept; it is not public domain. |
| 8 | `https://api.github.com/repositories/189060033/contents/inputs/shapefiles` | 200, 8,059 bytes: the folder `US_PCA` and five other files. |
| 9 | `https://api.github.com/repositories/189060033/contents/inputs/shapefiles/US_PCA` | 200, 4,638 bytes: `US_PCA.dbf` (67,124 bytes) and the shapes themselves as a 131-byte pointer to a large-file store. |
| 10 | `https://raw.githubusercontent.com/NatLabRockies/ReEDS-2.0/main/inputs/shapefiles/US_PCA/US_PCA.dbf` (the attribute table) | 200, 67,124 bytes: 134 regions, fields `rb` (`p1` to `p134`), `st`, `rto`, `interconne`, `country`, `custreg`. No field holds an EIA-930 code: 0 of the page's 70 grids match any value of any field. They are the model's own regions, not balancing authorities, so the shapes were not asked for. |
| 11 | `https://www.eia.gov/electricity/data/eia861/` | 200, 77,055 bytes: "Release date: October 7, 2026 (final data)"; the newest file is `zip/f8612025.zip`. |
| 12 | `https://www.eia.gov/electricity/data/eia861/zip/f8612025.zip` | 200, 4,756,816 bytes, sha256 `f59f6c732bf685fe0a1591b32227f5ce572dc0dfd26bb5caaeed128ac4e3a396`: Form EIA-861's detailed data files for 2025. |

No request went to an ArcGIS Online services host (session 180b's reading of a 403 on a robots file stands until the owner rules), to HIFLD, MISO, PJM or the Virginia SCC. Eighteen requests were left unspent.

**The derived map: counties (session 193).** The file the map now reads is the ERW's own derivation, not a boundary any balancing authority or agency published, and the map carries that sentence inside its frame whenever a region is drawn (`provenance.derived`, `provenance.label`; the page never draws a derived file without it). `warehouse/connectors/eia_ba_boundaries.py counties` makes it, with no request, from two things:

- **EIA-861, 2025** (request 12). `Service_Territory_2025.xlsx` lists the counties each utility serves in each state (11,803 lines, 3,096 utility-states). `Sales_Ult_Cust_2025.xlsx`, `Delivery_Companies_2025.xlsx` (Texas's delivery utilities report there) and `Short_Form_2025.xlsx` give each utility's balancing authority code and customers in a state. The codes are EIA's own, the ones EIA-930 uses.
- **County shapes** from the package the site already uses for its project map (`us-atlas` 3.0.1, `counties-10m.json`, sha256 `145aaf5d1433352a6a1d8e86b5f149c7c653f9171baf14aaf75ee66575def1b0`): the Census Bureau's cartographic boundary files, 2017 edition, as TopoJSON. Nothing was asked of the Census Bureau.

The rule, whole:

1. A utility's customers in a state under each of its codes are those of the wires: Parts A, C and D of `Sales_Ult_Cust` (bundled service and delivery), the delivery companies' file and the short form. Part B, energy sold by a marketer over another utility's wires, is left out: its customers are Part C's.
2. Those customers are split evenly over the counties `Service_Territory` lists for the utility in that state. EIA-861 does not say how many customers a utility has in each county, so the even split is an assumption, and the only one.
3. A county is given to the code with the most customers so allotted. Where no utility of a county reports a customer, to the code most of its utilities name. A tie is no assignment (there was none).
4. A county's name is matched to its shape exactly, after accents, case, punctuation and the words county, parish, borough, census area and municipality are dropped and Saint is written St. Where a state has a county and an independent city of one name, the plain name is the county and "<name> City" is the city.
5. A balancing authority's area is the counties given to it, joined, then simplified as a publisher's file would be (0.02 degrees). A code is drawn only when it is exactly the code of one of the page's grids.

What came out (the file's `provenance.counts`):

- 44 of the page's 70 grids have an area. 3,067 of the 3,107 counties of the lower 48 states and the District of Columbia are drawn.
- 2,008 counties are served only by utilities of one code. 1,126 are served by utilities of several and were given to the largest; the smallest winning share of a county is 33 percent (in the Tennessee Valley Authority's area). `site/public/network/ba_counties.csv` holds every county with its code, the share and how many codes were named.
- **40 counties of the lower 48 are blank.** 37 were given to `WACM`, a code of EIA-861's 2025 files that is not one of the page's grids (10 counties in Colorado, 9 in South Dakota, 8 in Wyoming, 6 in Nebraska, 3 in Utah, 1 in New Mexico). The page draws `SWPW`, Southwest Power Pool West, which EIA-861 does not name; nothing was moved from one code to the other. The other 3 are independent cities of Virginia that no utility's list names (Galax, Lynchburg and the city of Roanoke). A fourth, Falls Church, was given a code and has no shape in the county file, so it is not drawn either.
- 25 utility-states have a territory and no code in the files (Wolverine Power Supply Coop's 33 counties in Michigan are the largest); their counties were given by the other utilities that serve them.
- **26 grids have no area.** 17 are named by no utility in the files: seven operators of Canada and Mexico (`AESO`, `BCHA`, `CEN`, `HQT`, `IESO`, `MHEB`, `SPC`) and `AVRN`, `BHBA`, `CPLW`, `DEAA`, `GRID`, `GWA`, `SIKE`, `SWPW`, `WWA`, `YAD`. Nine are named and won no county against a larger neighbour in the same county: `GCPD`, `GVL`, `HST`, `IID`, `JEA`, `NBSO`, `SEPA`, `SPA`, `TIDC`. A grid with no area is not on the map and its ties are not drawn there; the Network view holds them.
- Four county names of EIA-861 are not in the shapes, all in Alaska, which the page does not draw.
- **A check that changed the rule.** The first build read `Sales_Ult_Cust` and the short form only, and left 8 counties blank. Looking them up showed why: Texas's delivery utilities (Oncor, CenterPoint and five more, 8.5 million customers) are in `Delivery_Companies`, so they had no weight, and 39 Texas counties had gone to a neighbour's code or to none (Harris County, which holds Houston, to `MISO`). The file was added to the rule before anything was drawn; a test holds Harris County to `ERCO`.

What this map is not:

- **Not a boundary.** A balancing authority's footprint follows transmission and generation, not county lines, and several overlap. Here a county has exactly one, so a small balancing authority inside a large one's counties disappears, and a county split between two is shown whole for the larger.
- **Not customers by county.** The even split gives a rural county and a city of the same utility the same weight.
- **Not the date of the replay.** It is EIA-861's year 2025, for every hour and year the page shows.
- **Not a measure.** Area is land. Nothing on the page is computed from these areas: the colors, flows and numbers are the Network view's own.

**Why the license has to be read per file.** The atlas is not one license. Of the 101 datasets its catalog listed, 41 say "This work is licensed under the Esri Master License Agreement", 40 carry only EIA's liability statement, 10 say "None (public use)", 7 say nothing, and one quotes EIA's own rule: "U.S. government publications are in the public domain and are not subject to copyright protection. You may use and/or distribute any of our data, files, databases, reports, graphs, charts, and other information products that are on our website". So a boundary layer on the atlas is used only after its own license statement has been read and says public domain or the equivalent, and the robots file of the host that serves the file (a feature service's host is not `atlas.eia.gov`) has been read as well.

**When the file is held: how it is made.** `warehouse/connectors/eia_ba_boundaries.py build` reads the publisher's GeoJSON as it came and writes the site's file. It is reference geometry, not a table: nothing of it goes through the validator, into `warehouse/output` or into the live set.

- **Matching is exact.** A shape is given to a grid only when the publisher's own code for it, in the property a person names after reading the file (`--code-field`), is the grid's EIA-930 code. No name is compared and nothing is guessed. The file records every grid with no shape (`nodes_without_shape`: Canada's and Mexico's operators at the least, which a file of US boundaries does not hold) and every shape with no grid (`shapes_without_node`). A grid with no shape is not on the map; its ties are not drawn there, and the Network view holds them.
- **The date.** The boundaries are the publisher's as of the vintage its file gives (`provenance.vintage`), one date for every hour and every year the page can show. A balancing authority that changed its footprint, or did not exist, on a day of the replay is still drawn with that one boundary.
- **Overlaps are real.** Some balancing authorities sit inside others. The file is ordered by area, largest first, and the page draws in that order, so a smaller one is on top of the larger one around it.
- **What is simplified.** A grid's parts are joined, then simplified with the Douglas-Peucker rule, topology kept (0.02 degrees by default, about 2 km), coordinates kept to three decimals (about 100 m), and parts smaller than the tolerance squared are dropped. Each shape is simplified on its own, so two neighbours' shared border may open or overlap by up to the tolerance. The file's `provenance` holds the source, the address, the retrieval time, the sha256 and size of the raw file, the publisher's license words and the tolerance; the builder refuses a raw file whose sha256 is not in the request log, and a result over 400,000 bytes.
- **The projection.** Albers for the lower 48 with Alaska and Hawaii inset (d3-geo's `geoAlbersUsa`, which the site's project map already uses).

**What the colors are not.** A region's color is one number for the whole balancing authority: the carbon intensity of what was generated inside it in the period shown. It is not the intensity of the power used at any place inside the boundary (imports are not in it), it does not vary within the region, and a large region is not a large number: area on the map is land, not load or generation. A boundary is a planning footprint as its publisher drew it, not a service-territory survey and not a line any wire follows.

## The map made whole (session 8601)

Session 8601 (chain 504, 19 November 2026) added to the map and took nothing from it. The Network shape is as it was: the map's code and its boundary file are still fetched only when "Map" is chosen (384 ms from the click to the regions drawn, on the build of that night), and nothing the map needs is computed while the network is the shape shown.

**Which boundary file.** The map asks first for the whole country's boundary file, `site/data/regions/ba_boundaries.json` (the contract `docs/state/page_files_regions.md`, section 1: a GeoJSON FeatureCollection, one feature a balancing authority, written by the data machine from a publisher's layer), through the address `/grid/boundaries`. That address is under `/grid`, so the release gate covers it as it covers the page. Until the server holds the file the address answers `{ "held": false }` and the map draws the file it has drawn since session 193, the ERW's own derivation from counties, with its label. A file that is the contract's draws with one line under the map that names its source and the day it was retrieved, and no derived label. A file that is not the contract's whole (no source, no retrieval time, a feature with no code or no polygon) is an error and draws nothing.

**The point inside a shape.** A tie begins and ends at one point inside each balancing authority. The county file gives that point; the contract's file gives none, so the reader finds one (`insidePoint` in `site/lib/networkMap.ts`): the centroid of the shape's largest ring when it lies inside the shape, else the middle of the longest stretch inside the shape on a level line across that ring at half, a quarter or three quarters of its height. It is a place to draw from, not a place on the ground: no substation, no load center.

**A grid with no boundary is listed, not dropped.** Under the map, inside its frame: "Not on the map: no boundary in the file", then each such balancing authority by name. A name has the same hover and the same click as a region. Its ties cannot be drawn on the map (a line needs two points); the Network shape draws them, and the map's key says how many of the hour's ties it could draw.

**A region's hover.** The name and, for the hour or day shown: the carbon intensity of generation (as the panel writes it), demand, net imports or exports over the ties that reported (`netOf`, the panel's own sum and the figure under the network), the batteries when the switch is on, the hour, and the tables. A figure that is not held says so.

**A tie's hover.** Both names in the direction of flow, the megawatts (a day's are its average), the hour or day, and which side reported it. The snapshot's rule is the pair rule above: the flow is the report of the balancing authority whose code sorts first, and in an hour it did not report, the other's with the sign turned. The snapshot does not record which of the two it was in a given hour, so the hover says the rule and ends "The file does not mark which". When a snapshot carries, for a pair, the list of frames read from the second side (`links[].other`), the hover names the side (data request 541 of `docs/state/data_requests_done_line.md`). The hover takes the tie whose line is nearest the pointer, within four screen pixels of its edge, and not at its two ends, where a grid's ties meet and the grid answers. A finger has no hover: a tap on a tie shows the same words.

**Width and motion.** A tie's width is the rule's own (0.4 plus 3 times the square root of its share of the period's largest flow), now in screen pixels at every zoom. On a frame narrower than 748 px (a phone, or the map beside an open panel) the widths, the dash and the ring shrink with the frame, to six tenths at most: at full size the arrowheads of the West ran into each other on a phone. The key under the map draws three of those widths with their megawatts: the period's largest flow, a quarter of it and a sixteenth. The dash still runs from the exporter to the importer, faster as the flow is larger, and stands still where the reader asks for less motion.

**Batteries.** With the Batteries switch on, the map draws the network's ring at the point inside each balancing authority whose batteries are reported for the hour: the same rule (half full at rest, full when discharging at the period's most, nearly empty when charging at its most), over a faint whole circle so an emptier ring can be read. The Prices ring stays in the Network shape; the panel holds its numbers on the map.

**Moving and zooming.** The wheel zooms about the pointer (a wheel that would zoom out of the whole map scrolls the page), two fingers zoom about the point between them, a drag moves a map that is zoomed, and three buttons zoom in, zoom out and show the whole map. From one to twelve times; the map cannot be pulled off its frame. At rest one finger scrolls the page.

**The color.** As before: the region has its sphere's color, one call on one range (`colorOf(view.intensity(id, hour), lo, hi)`). In the live week that is the latest hour of carbon intensity held, for the seven grids that hold one; in a story or the replay, each day's own. 37 of the 44 regions drawn from the county file are grey, "not held": the warehouse computes a carbon intensity for the seven ISO balancing authorities only (data request 540 of `docs/state/data_requests_done_line.md`).

**A fault found and fixed.** The brand's rule for a button that is not pressed gave a switch that is on (`role="switch"`, `aria-checked="true"`: Batteries, Prices) ink letters on its own ink ground, so "Batteries: on" could not be read, in the Network shape too. `site/app/tokens.css` now leaves such a switch its own white letters.

**After the reader's read (session 8604, `docs/reviews/grid-map-read-2026-11-19.md`).** Five cases a reader would bring were taken on the map in a browser, and these things changed:

- A tie's hover names the one table its megawatts come from (the interchange table of the view: `eia930_all_interchange` in the live week, `eia930_daily_interchange` in the replay, `eia930_event_hourly_interchange` in a story), and its two names stand once, in its head; who reported is said by code.
- The states' outlines are drawn as thin lines over the regions (the Census Bureau's cartographic boundaries as `us-atlas` holds them, the file the project map draws). They name nothing and answer no pointer; a region's hover says the state under the pointer. A balancing authority's footprint follows no state line, and without them nothing on the map said where a place is.
- Where published footprints lie on one another (Salt River Project, Arizona Public Service and the Western Area Power Administration's Desert Southwest region all hold Phoenix), the hover of the one on top names the others: "Also covers this point". The smaller footprint is drawn on top, as before. An overlap is the publisher's, not an error of the map: a footprint is a planning area, and two authorities can plan for the same ground.
- "California's evening" shows the newest whole Pacific day of the live week for which California's batteries are reported (`eveningDay` in `site/lib/networkV3.ts`: a day counts when all but one of its hours hold a report). A newer whole day with no report is passed over and named in the line under the controls. With no report in the week at all it is the newest whole day, as it was before this session. This holds in the Network shape too. The cause it answers: the live set's battery table can end a day or two before the week's interchange.
- With a grid chosen that is none of the seven, the fold "neighbours, last twelve months" says the twelve months are not held for it. It used to say "Click a grid, or choose one above". In the Network shape too.
- When the whole country's index is on the site, the panel says an authority's local time from the index's time zone; until then, as before, only the seven grids have one.
- **The 3D scene draws the hour the page opens on.** The scene is built on the week's newest hour; since session 124 the page opens on the newest hour that every reporting pair holds, which is usually earlier. Until this session the scene kept the newest hour's ties until the slider was first moved, under a line and a slider that named the other hour (on production on 19 November 2026: 139 ties drawn for 2026-11-17 04:00 UTC, whose own count is 148). The scene now takes the hour, view and selection shown as soon as it is ready. This is the one change to what the Network shape draws as it opens.

**Held by** `tests/test_session8604.py` (the evening's day on a typed week, the hover's words, the sources); and, for the map as a whole, `tests/test_session8601.py` (the reader, the sums, the words, the arithmetic, the sources) and `site/scripts/check-grid-map.mjs` on a built site (the network unopened, the time, the megawatts and the colors of the two shapes set against each other, the hovers, the ring, a story switched in its middle, the zoom, the list, a phone).

**The map's done line (session 8606): its replication, its cross-check and its decisions block.**

- *Replication.* `replication/grid/map_figures.mjs` reads from a built page what the map draws (the hour the week opens on, the regions and the authorities listed, every tie drawn with its megawatts and its direction, the width key, and the hover of each of the 60 regions) and keeps the snapshot the page drew (`map_snapshot.json`). `replication/grid/replicate_map.py` computes each of those again from the snapshot and the boundary file, with none of the page's code, and compares: 439 of 439 figures met on 19 November 2026 (`map_figures_met.csv`). The rules it applies are this note's: the hour is the newest every reporting pair holds; a tie is a pair whose flow is held and not zero, from its exporter to its importer; a region's net exchange is the sum of its pairs signed from its side, a zero flow counted as a tie; a tie is on the map when both its ends have a boundary. Not compared: a region's demand in the hover, which the page reads from the live set and not from the snapshot, and the two lines that are geometry at the pointer (the state, the other footprints).
- *Cross-check.* `replication/grid/crosscheck_map.py` reads EIA's own series for the same hour in two requests (the open data API, `electricity/rto/interchange-data` and `region-data` type TI) and writes `crosscheck_map.csv`. For 2026-11-17 04:00 UTC (EIA's period `T05`, the hour's end): each of the snapshot's 159 pairs is the report EIA publishes, to 1 MW, by the pair rule (the first authority by code; the second's with its sign turned where the first filed nothing).
- *What the cross-check shows a reader should know.* A region's net exchange on the map is the sum of its pairs, each read from one side. It is not the authority's own total interchange as it files it with EIA. For the same hour the two are the same to 1 MW for 39 of the 60 authorities EIA holds a total for and differ for 21: PJM's pairs sum to 811 MW exported and its own total is 82 MW exported; CAISO's pairs sum to 4,119 MW imported and its own total is 5,076 MW. The difference is the two sides of a tie not agreeing, which the pair rule settles one way. The map's decisions block says so. Whether the hover should carry the authority's own total beside the sum is for the owner's ruling; the default is the sum, as the Network view has had it.
- *Decisions block.* "Decisions on this map (9)", a fold inside the map's own frame (`site/app/network/MapDecisions.tsx`), closed to start: each line a choice that moves what is drawn, with its rule and its source. The Network shape's markup is not touched by it.

Held by `tests/test_session8606.py` (the rules on typed pairs, the kept runs, an altered figure caught, the block's lines) and one more check of `site/scripts/check-grid-map.mjs`.

**The accessibility read (session 8609).** The map, the Network view beside it and the region tabs were read with the axe-core engine on a built site, in the internal view, at 1280 and 390 px (`site/scripts/a11y-axe.mjs`: WCAG 2.0, 2.1 and 2.2, levels A and AA; not a gate). The region tabs broke no rule. The map broke two, both fixed at their cause:

- *Controls nested in an image.* The map's frame was an image (`role="img"`) and its regions are buttons; what is inside an image is hidden from assistive technology. The frame is now a labelled group, and each region is a button with its name that a keyboard reaches: focus shows its figures, Enter or Space opens its panel.
- *Target size.* The ten names under the map ("Not on the map") were buttons 16 px tall. Each is 24 px tall, the least WCAG 2.2 allows a pointer's target.

After the two, the read finds nothing on the map or on the Network view at either width. The read does not cover what an engine cannot judge: the order a keyboard takes through 60 regions (the file's, largest first), and whether a screen reader's words for a region are enough; those are a person's to try. Held by `tests/test_session8609.py` and two checks of `site/scripts/check-grid-map.mjs` (the names' height; a region reached and opened with the keyboard alone).

**After the second read (session 8612).** Five more cases (a day replayed, the June 2025 heat, a region's Network tab in the Map shape, the year played, ERCOT's batteries) found two faults, both fixed. A link of a region's list of authorities keeps the shape the reader is in: followed in the Map shape it opened the panel in the 3D network (`site/components/grid/BaLink.tsx`; the list is drawn on the server, the shape is in the address). And with the Batteries switch on, when the hour shown draws no ring the map says so and names the newest hour of the view that holds a report (`newestBatteryFrame` in `site/lib/networkV3.ts`); it reads the view's own battery series and computes no figure. Left as the network has it, for the owner's ruling: while a story or the year plays, the address does not name it; it does once paused. Held by `tests/test_session8612.py`.

**Against the brand (session 8611, `docs/brand.md`).** A region's tables take the brand from the site's stylesheet (the dark rule under the header, mono figures, the first column kept in place, the fade at the edge). Three things did not follow it and now do: the hour by hour chart names each source at the right end of its columns in its own color, where it had a row of swatches above the plot (section 6, direct labels); its hover card names each series in its color with its figure in the mono face; and on a phone the map's three zoom buttons and the names under the map are 44 px tall (section 3; they were 32 and 24). Held by `tests/test_session8611.py`.

## The thirteen regions in the Grid tool (session 8602)

Session 8602 (chain 504, 19 November 2026). Until then the tool's picker held the seven grids and the Lower 48. It now also holds EIA's thirteen regions of the lower 48 (California, Carolinas, Central, Florida, Mid-Atlantic, Midwest, New England, Northwest, New York, Southeast, Southwest, Tennessee, Texas), six of which no page of the site had drawn: the Southeast, Florida, the Carolinas, Tennessee, the Northwest and the Southwest, none of whose balancing authorities is one of the seven grids.

**What a region is.** One of the thirteen regions of EIA's hourly grid monitor (Form EIA-930), with the balancing authorities EIA's reference tables place in it. The page draws no region of its own making. The regions, their authorities and every figure come from the whole country's page files, `site/data/regions/`, which the data machine builds (`warehouse/derived/region_files.py`, `docs/methods/regions_pages.md`); their shapes are the contract `docs/state/page_files_regions.md`. The site's code only reads them (`site/lib/regionsdata.ts`) and does the small arithmetic of `site/lib/gridregions.ts`: the hour of a position in an hourly array, the newest hour that holds a net generation, a source's share of that hour, one month of a trade file.

**The address.** A region has its own word: `/grid?region=se&view=mix`. The grid's word (`grid=`) and the function that reads an address for a grid (`gridPick`) are untouched, so every address the tool had reads as it did. A region is in view only when the address names one the index holds; otherwise the page is the grid's page, as before.

**Until a file is on the site.** Under the grid picker a row "EIA region" lists the regions of `index.json`. Until that file is on the server the row reads "not built yet", its hover names the file, and no region can be chosen. A region whose own file is missing says "not built yet" on that tab, with the file's name on hover, and draws no figure.

**The Mix tab for a region** (`mix/<region>.json`, the form of the seven grids' `site/data/mix/*.json`):

- The latest hour held: the newest hour of the file's 35 days that holds a net generation; its demand, net generation and net imports, and each of the eight sources with its megawatts and its share of that hour's net generation (megawatts over net generation, to a hundredth of a percent).
- Generation by source hour by hour for those 35 days, with demand, in UTC. Since session 8605 each hour is its own column (`site/components/grid/RegionHours.tsx`): a source above zero is stacked up from zero and a source below zero (batteries charging, pumped storage pumping, a solar plant's own use at night) down from zero, by the rule of `stack` in `site/lib/mix2.ts`; an hour a source does not hold is a gap in that source; demand is a line. The mouse reads the hour, in UTC and in the region's time, and each source's megawatts; the table holds the same hours. No figure is computed: a column's height is the file's megawatts.
- The average day of any month or year the file holds, by local hour (the stacked areas and the demand line a grid has), and the shares of the period by source with their megawatt-hours and the days held. Since session 8605 the months the file does not hold are counted under the month chips and named on hover with the data machine's rule (a month is written when at least 90 percent of its days are complete, `docs/methods/regions_pages.md`), and so are the whole months since the newest held, up to the month the file was built in. Such a month is absent, never zero.
- The Storage row (session 8605): CAISO, NYISO and PJM file no battery series in Form EIA-930 (the Storage page, since session 34). For a region that holds one of them (California, New York, the Mid-Atlantic) the row says so on hover, and for California points to the Storage page. The figure shown is the file's and is not changed.
- One calendar month year after year: net load (demand less wind and solar) by hour, each year's midday low (09:00 to 16:00), evening high (from 16:00) and the ramp between them, by the functions the seven grids' tab uses (`site/lib/mix2.ts`).
- "The rest of the Mix tab": the seven parts a grid's tab has that a region's file does not hold (a hub price beside the mix, wind and solar forecasts, the records, how hard the system works, availability by source, carbon intensity and temperature beside the mix, the table by state and since 2001). Each is drawn, blank, as "not held for this region", with its reason on hover. None is hidden and none is filled.

A region's days and local hours are counted in the time zone its file names (the zone of most of its demand). Demand is the sum of the region's balancing authorities that file demand, for an hour every one of them holds; net imports are EIA's total interchange with its sign turned (positive: the region imports). Those are the data machine's rules, said on the page's hovers.

**The Gravity tab for a region** (`trade/<region>.json`): for a month, one row a neighbouring region (and Canada or Mexico): the region's net imports from it by the region's own report, the same flow as the neighbour reported it, the gap between the two over the hours both reported, and the hours each side held; then the total, which the file writes only when every neighbour's own report holds at least half the month's hours. A figure a side did not report is blank, never zero. A chart draws each neighbour's monthly net imports for the last 36 months. Months are EIA's Eastern months. Neither side's report is adjusted to the other. Since session 8605 a month the reports hold in part is said so, beside the table and under the chart for its last point: the most hours any neighbour's row holds of the region's own report, against the hours of the month, both from the file (`hours_own`, `hours_in_month`). The month's figures are not scaled up to a whole month.

**The Network tab for a region:** the network as for the Lower 48, under a list of the region's balancing authorities; a name opens that authority's panel. When the index is on the site, every panel and every hover on the map names the authority's EIA region, and the panel's line opens the region in the tool. **The Clean tab** draws its three parts blank: the warehouse computes no carbon intensity for a region.

**A region beside the grid that covers nearly its ground** (Texas and ERCOT, New York and NYISO, New England and ISO-NE, the Mid-Atlantic and PJM): the region's hover in the picker carries the first sentence of the data machine's own account of why the two differ (`alike.why` in `demand/<region>.json`). Both stand; the page does not choose between them.

**Ask is not changed.** With a region in view the panel is the Lower 48's, says so, and reads no region's page file.

**Held by** `tests/test_session8602.py` (the address, the readers on the tests' own fixture, the page's hand-over, the seven grids' blocks as they were) and `site/scripts/check-grid-regions.mjs` on a built site, which reads the same files the server reads and checks the page's figures against them.

**The regions against EIA's own regional series (session 8606, the cross-check of the done line).** The region files are summed by the data machine from the balancing authorities' rows of EIA's six-month files. EIA also publishes each region's own hourly series through its open data API (Form EIA-930: `electricity/rto/region-data` for demand, net generation and total interchange, `electricity/rto/fuel-type-data` for net generation by energy source, the region's code as respondent). `replication/grid/crosscheck_regions.py` sets the two side by side for three hours of each of the thirteen regions (the latest hour the file holds, the same hour seven days earlier, and the hour of the file's 35 days in which "other" is lowest), folding EIA's codes as the contract folds them, and writes every row to `replication/grid/crosscheck_regions.csv` with its address (the key is not part of it). Read on 19 November 2026 at 14:37 UTC:

- The file's hour is EIA's period at the hour's end: an hour the file starts at 04:00 UTC is EIA's period `T05`. Read the other way, no region's demand agrees.
- 383 of the 430 figures compared are EIA's to 1 MW. Demand: 32 of 38. Net imports: 32 of 36. The eight sources: 270 of 282. The sum of the sources: 32 of 37.
- Net generation agrees in 17 of 37: the file's is the sum of its eight sources, and EIA's is the total the authorities report, which is not always the sum of EIA's own codes (the Central region by 315 and 424 MW in two hours, the Mid-Atlantic by up to 495 MW).
- Four hours differ by more than 100 MW in a figure that should agree (the Carolinas at 2026-10-31 17:00 UTC, the Southwest at 2026-11-02 13:00 and 2026-11-16 15:00), the largest the Southeast at 2026-11-11 19:00 UTC (demand 23,757 MW in the file, 24,859 MW in EIA's series). Data request 551 holds them.
- Where EIA returns no code for a region's source (battery storage for New York and the Mid-Atlantic, wind for the Carolinas and Florida, coal for New England), the file writes 0. Data request 551 asks whether those should be blank.
- California's "other" is EIA's own: in the hour to 2026-11-08 19:00 UTC, EIA's code OTH for California is minus 10,253 MW and its battery code BAT minus 151 MW, and the file's "other" (petroleum, geothermal, other and unknown together) is minus 9,070 MW, the same as EIA's four codes summed. The page says nothing on what is inside EIA's "other".

*Read again on the rebuilt files (session 8613, 19 November 16:55 UTC).* The data machine rebuilt the mix files at 14:52 UTC under its answers to requests 544, 549 and 551, and they reached main at about 16:50. On them: **388 of the 439 figures compared are EIA's to 1 MW** (demand 33 of 39; net imports 34 of 37; the eight sources 270 of 285; the sum of the sources 34 of 39; net generation 17 of 39, for the reason above). The sources EIA publishes no series for are now blank in the files too, so they are not held on either side and are not compared: wind for the Carolinas and Florida, storage for New York and the Mid-Atlantic. Five hours differ by more than 100 MW in a figure that should agree; two of them are the latest hour itself (Florida and the Northwest at 17 November), which the data machine reads as two vintages: its files are EIA's six-month files as saved on 18 November, and EIA's series has been revised since (its answer to request 551). `crosscheck_regions.csv` on the branch is this second read.

A cross-check, not a replication: it reads EIA's published figure for the same hour, not the files the data machine summed. `tests/test_session8606.py` holds the folding to the contract's words and the output's form.

**The region tabs' replication (session 8606).** `replication/grid/regions_figures.mjs` reads from a built page the figures the Mix and trade tabs draw for each of the thirteen regions; `replication/grid/replicate_regions.py` computes each again from the region files with none of the page's code (the latest hour and its shares, the newest month's energy and shares, the days held, the months not held, the calendar month across the years with its midday low, evening high and ramp, the newest month of trade with its hours, the line on a part of a month) and compares: 1,349 of 1,349 figures met on 19 November 2026 (`regions_figures_met.csv`). It replicates the page from its files; the files from the warehouse's tables are the data machine's (`docs/methods/regions_pages.md`). When the region files are rebuilt, the page is to be read again before the comparison: the script says so and stops. The page's decisions block for a region ("Decisions on this page") carries five more lines since this session: the hour by hour chart's rule, the months' rule, the part of a month, storage, and what the cross-check found.

**After the second read of the regions (session 8613).** Two gaps, both fixed from the files' own fields. The trade tab has a row of years, every year the file holds (July 2018 on), and the months offered are those of the year shown; it offered the newest thirteen months and no way to an older one. And with a whole year as the Mix tab's period, the line under the shares gives the file's own count of the year's months held and due and names the months not held ("301 days held, in 10 of the year's 12 months (not held: January 2025, February 2025)"). No figure is computed for either. Held by `tests/test_session8613.py`.

**A finger on the hour by hour chart (session 8614).** On a phone a tap on the chart showed no card: the card came up on a pointer's move, and a tap is a press and a lift with no move between; the lift is also the touch pointer's leave. A finger's press now reads the hour as a move does, and a touch's leave is let pass, so the card of a tap stays until the next tap. A mouse is as it was; the chart's Table always held every hour. The map of balancing authorities was built for a finger from the start (a tap opens a region's panel, a finger on a tie shows its figures) and its check uses fingers. The regions' check now taps the chart with a finger at 390 px. Held by `tests/test_session8614.py`.

**Read on production (sessions 8617 and 8620, 19 November 2026, with what had landed by 18:28 UTC).** With a finger at 390 px: the 3D network's scene is fetched 270 ms after the reader scrolls to it and a tap on a sphere opens its panel; the site's shared charts on a region's Mix tab (the average day, year after year) put their card up on a tap and keep it, which is what the hour by hour chart now does too. How long the map takes to open there, three tries each (`runs/c504_map_open_time.mjs`): from a press of "Map" on the open Network tab, 905 ms the first time, when the map's code and the boundary file are fetched, and about 200 ms after (1280 px: 905, 205, 216; 390 px: 210, 256, 196); from a cold open of the map's own address, 0.7 to 1.1 seconds (1280 px: 1,089, 925, 768 ms; 390 px: 738, 1,031, 786 ms), with its 60 regions drawn.

**A source no authority has ever printed (session 8610, made ready before the files).** Data request 551 found the region files writing 0 where EIA publishes no series at all. The data machine's answer (the contract's line of 19 November): such a source is `null` all through the region's mix file (its averages, its energy, its share, its hourly array) and is named in a new key, `sources_not_printed`: wind in the Carolinas, Florida and the Southeast; storage in the Mid-Atlantic and Tennessee; coal, solar and storage in New York. The files in that form were not on main when this was written; the page was made ready on a copy of New York's real file with the three set to null (never shipped), and is held by `tests/test_session8610.py`:

- In the latest hour's table and in the table of shares such a source is a row, blank in every cell ("not held"), after the sources that are held. Its hover says no balancing authority of the region has reported it to EIA in any hour held since July 2018, and that it is blank, not zero. It was 0 MW, 0.0 percent and 0 MWh.
- The charts draw only what is held, so such a source has no layer and no name in the legend.
- **Net load.** Net load is demand less wind and solar (the seven grids' rule, `netLoad` in `site/lib/mix2.ts`, which is not changed). By that rule alone a region with no solar ever reported would have no net load at all. For a region, a never-printed wind or solar is not there to take from demand: net load is demand less the one that is reported, and the page says so under the table ("No balancing authority of New York has reported solar to EIA since July 2018, so net load here is demand less wind."). An hour of a source that is reported and not held still leaves that hour blank. The figures this gives are the ones the page drew while the file wrote such a source as zero (checked on New York: every year's midday low, evening high and ramp the same).
- The replication reads the same form by the same rule (`replicate_regions.py`), and counts two more checks a region: 1,375 of 1,375 on the first files, and 1,483 of 1,483 on the rebuilt ones, which hold more months and name their never-printed sources (19 November, 16:55 UTC). The page read keeps when each region's two files were built, and the comparison stops when a file has been rebuilt since.

## The gravity shape (session 266)

The owner named it on 14 October 2026: a third shape of the network, "Gravity", beside "Map" and "Network" at the top of
the Network view (`/grid?view=network&shape=gravity`). It draws the same hour, the same selection, the same colors, the
same hover card (the grid's name) and the same panel as the other two. Code: `site/lib/networkGravity.ts` (the rule,
no drawing) and `site/app/network/NetworkGravity.tsx` (the SVG).

- **What is drawn.** The Lower 48 (EIA-930's `US48`) is a circle at the center. Each of the seven ISO grids (CAISO,
  ERCOT, ISO-NE, MISO, NYISO, PJM, SPP) is a circle around it. The other balancing authorities of the network are not
  drawn here: their net generation is not in the live set (`eia930_all_generation` holds the seven and `US48` there),
  and the line under the frame says so.
- **Size.** A circle's area is proportional to its net generation in the hour shown (`eia930_all_generation`,
  `net_generation_mw`, read for the live week beside the demand, `site/app/network/data.ts`). The Lower 48's own
  generation sets the scale: its radius is 80 units of a 640-unit frame, and a grid's radius is 80 times the square
  root of its generation over the Lower 48's (never under 6 units, so a small grid can still be clicked).
- **Distance: the rule.** Net imports in the hour are the sum of the grid's reporting ties, signed so that power coming
  in is positive (the panel's own sum). Divided by the grid's net generation, they give a share. A grid with no net
  exchange sits on the middle ring (205 units from the center, drawn dashed). A net importer is pulled toward the
  center by 90 units times its share over 0.25, a net exporter pushed out by the same rule; a share of a quarter or
  more is the full pull. Since session 299 the pull is a square-root scale of that share (the section
  "One page, four tabs" below). So **a net importer sits nearer the center, a net exporter farther out**. A circle never
  overlaps the Lower 48 and never leaves the frame (4 units of gap).
- **Bearing.** Each grid keeps a fixed bearing that follows the map, in degrees clockwise from north: CAISO 262, SPP
  318, MISO 8, ISO-NE 40, NYISO 66, PJM 104, ERCOT 196. Only the distance carries data.
- **What is not drawn from a stand-in.** A grid whose generation is not held for the hour is a dashed outline on the
  middle ring; a grid with zero generation is a dashed outline too, at the full pull when it imports; a grid with no
  tie reported in the hour sits on the middle ring. Outside the live week (a story or a replayed day) generation by
  hour is not held, so the shape draws nothing and says so.
- **California.** CAISO's circle is EIA-930's net generation, the same source as the other grids. From December 2025
  EIA-930's California generation reads below CAISO's own (`docs/methods/eia930_caiso_break.md`), so CAISO's circle is
  smaller and its pull larger than CAISO's own figures would make them. Put to the owner (session 266 report).
- **Checked.** `site/public/grid/erw_2026_grid_replication.py` rebuilds every circle's generation, net imports, share,
  radius and distance from `erw_2026_grid_replication.csv`; `site/scripts/check-grid-replication.mjs` compares them
  with the page, value by value.

## The two-day lag, said under the chart (session 266)

One line under the network says the newest hour shown and how many hours before the snapshot's latest hourly refresh
it began, computed from the snapshot (the check key `net|lag|<hour>|<refresh>`, `netValue` in `site/lib/network.ts`),
and why: EIA-930 publishes a balancing authority's interchange for a local day on the second morning after it (the
section "How far behind the newest hour is, and why" above). The Now view's sentence gives the same lag for the hour
of its exchange, under the same key.

## One page, four tabs, and the Ask panel (session 299)

The owner's merge of 18 October 2026, and the Grid pack's rulings, made the Grid tool one page of four tabs: Network,
Mix, Clean and Gravity, the grid picked once above them, and Ask a panel on the right of every tab. The Now view's
blocks (the latest hour) open the Mix tab; the Exchange view's blocks sit under the gravity shape on the Gravity tab;
`/ask` and `/mix` redirect to the panel and the tab. An old address keeps resolving: `view=now` opens Mix,
`view=exchange` opens Gravity, `view=ask` opens the page with the panel, `shape=gravity` with `view=network` opens
Gravity (`site/lib/gridtool.ts`, `OLD_VIEWS`). Every block keeps its markup inside the wrapper and its check keys, so
no number moved. The rulings the page carries, said on the page in its decisions block:

- **4b, the opening grid.** With no grid in the address the page opens on the Lower 48 on every tab (ERCOT on the Now
  and Ask views until then).
- **1a, one source for the gravity shape.** EIA-930's net generation sizes every circle, CAISO's included, and the line
  under the frame says that CAISO's reads smaller and more pulled in since December 2025 (the California break,
  `docs/methods/eia930_caiso_break.md`). CAISO's own figure is not substituted: the shape would then mix two sources.
- **2c, a square-root pull.** The pull toward or away from the center is now `sign(share) * sqrt(|share| / 0.25)`,
  clamped to one (the linear `share / 0.25` until then), so a grid importing a sixteenth of its generation sits at half
  the full pull rather than a quarter of it: small shares, which are most hours, are told apart. The full pull, a
  quarter of generation or more, and the bearings are as they were. `site/lib/networkGravity.ts` and the replication
  script `site/public/grid/erw_2026_grid_replication.py` carry the same rule.
- **3c, the age of "now", said twice.** The line under the network gives the newest hour's age against the snapshot's
  latest hourly refresh (the check key `net|lag|<hour>|<refresh>`, which the value checker recomputes) and, beside it,
  against the clock when the page was drawn (`data-network-clock-lag`, not a key: the clock is not a table, and the
  page is served for an hour, so the clock figure can be up to an hour stale).
- **6a, the 63 other balancing authorities.** Not drawn on the gravity shape: their net generation is not in the live
  set. The line under the frame counts them.

## Not here

- The published boundaries of the balancing authorities: not held after three pulls. The Map draws the ERW's own derivation from counties, labeled as derived (see "The map", "The derived map: counties").
- The demand of the BAs outside the seven ISOs.
- Hourly interchange before 2026-09-13, except the two stories' windows (daily interchange is held from 2019).
- Flows by transmission line: EIA-930 reports BA-to-BA totals only.

## What stood on the page face until session 168

Session 168 (the owner's instruction of 8 October 2026): version 3 became the network page at `/network`, and
`/network/v3` redirects to it. The page that stood at `/network` is kept, unrouted, in
`site/app/_retired/network-original`. Method, limits and "what this is not" text no longer stands on the page face:
the eight blocks below were moved here whole, each under a heading that says where it stood. The page keeps the line
"Newest hour ... Demand of the seven ISOs" (carried over from the old page) and one source line at the bottom.

Where a block held a figure the page computed at the moment it was read, the figure below is the one the page showed
on 9 October 2026 at 06:37 UTC (the last build before the move; the live week refreshed 2026-10-09 06:05 UTC, the
twelve months 2025-10 to 2026-09). Those figures are a dated copy, not a live read. The live ones are in the panel of
the page (a grid's twelve months, the three measures' range), in the line under the network (the newest hours) and in
the tables named in the source line. The method of the replay, the prices, the trace and MISO's pause is written at
length in [`grid_network_v3.md`](grid_network_v3.md).

### From the old page (`/network` until session 168), fold "Who supplies each ISO grid: three measures"

A grid's net imports can be measured three ways from EIA-930: the sum of the ties it reports with each neighbour;
EIA's own total interchange for it; and its demand less its net generation. They should agree. Over the last twelve
months, as a share of demand, on each measure's own months:

| Grid | Sum of its ties | EIA's total interchange | Demand less net generation | Largest supplier | Days held / left out |
|---|---|---|---|---|---|
| CAISO | 16.84 percent | 16.83 percent | 28.11 percent | NEVP, 4.03 percent | 311 / 54 |
| ERCOT | 0.08 percent | 0.07 percent | 0.08 percent | SWPP, 0.11 percent | 311 / 54 |
| ISO-NE | 4.67 percent | 5.36 percent | 4.67 percent | NYIS, 4.47 percent | 317 / 48 |
| MISO | 2.66 percent | 2.52 percent | 0.31 percent | PJM, 3.37 percent | 311 / 54 |
| NYISO | 11.69 percent | 11.62 percent | 11.68 percent | PJM, 14.44 percent | 313 / 52 |
| PJM | -2.66 percent | -1.24 percent | -3.11 percent | TVA, 0.84 percent | 222 / 143 |
| SPP | -1.70 percent | -1.23 percent | -1.24 percent | SPC, 0.04 percent | 204 / 161 |

(The table as the page showed it on 9 October 2026, from `ba_supply_monthly`, 2025-10 to 2026-09. The page computed
it with `site/lib/basupply.ts`; the panel of the page still shows each grid's own row when the grid is picked.)

- **The headline is the sum of the ties** (the sum of its reported ties). It is complete on every day it counts, it
  equals EIA's total interchange on the same days for CAISO, ERCOT, ISO-NE, MISO and NYISO, and the neighbours'
  shares add up to it. Where the three measures differ by more than 1 point of demand, the panel shows the range.
- **CAISO.** Its ties and EIA's total interchange agree to the MWh on every day; demand less net generation reads
  about ten points higher. The gap opens in December 2025: through 2024 and most of 2025, CAISO's demand less net
  generation less its interchange was within about 2 percent of demand; from January 2026 it runs at 70 to 93 GWh a
  day, 10 to 15 percent of demand. The interchange did not change: CAISO's published net generation fell. Why EIA's
  figure fell is not in the data the warehouse holds. Until it is explained, the balance overstates California's
  imports.
- **PJM**: the three disagree by about two points. **SPP**: its ties read about half a point below the other two.
  Both leave out many days (a regular neighbour missing or a pair-day screened).
- **MISO**: demand less net generation reads one to three points below its interchange on the same days, in every
  year since 2019.

Held days: every regular neighbour reported and no pair-day screened out (further than 10 median absolute
deviations, at least 500 MWh, from the pair's own median: EIA's daily interchange holds days no tie can carry).
Demand and net generation are held for the seven ISO grids only. EIA's Eastern day. Method: this note, "Who supplies
a grid (session 68)" above.

### From the old page, fold "What this is, and what it is not"

- **Physical flows between balancing authorities**, as each reports them to EIA. Not contracts: who buys power from
  whom can differ from the path it takes.
- **EIA revises its data.** A day reported late or corrected changes these figures when the warehouse next pulls it.
- **A neighbour's power may itself be imported.** A grid's supplier is the tie it arrives over, not where it was
  generated.
- **Each pair is counted once** on the network: its flow is read from the BA whose code sorts first, as that BA
  reported it (positive = it exported to the other); in an hour it did not report, from the other BA's report with
  the sign flipped.
- A balancing authority keeps supply and demand matched in its own area and trades across the ties with its
  neighbours. EIA: the power system of the Lower 48 "is made up of three main interconnections, which operate
  largely independently from each other with limited transfers of power between them", and ERCOT is the one where
  "the balancing authority, interconnection, and the regional transmission organization are all the same entity and
  physical system" ([EIA, Today in Energy](https://www.eia.gov/todayinenergy/detail.php?id=27152)). That is why
  ERCOT hangs on 2 thin ties while the eastern grids form one dense mesh.
- Sphere size: demand for the 7 ISO balancing authorities the warehouse holds demand for, interchange volume over
  the week for the others. Color: carbon intensity of generation, green to cardinal, grey where not held. Positions
  are computed once, with a fixed seed, and never re-settle.

### From the old page, fold "How fresh each layer is"

- The flows of the live week: refreshed every hour; newest hour 2026-10-07 03:00 UTC (Oct 6, 23:00 Eastern) when the
  page was read on 9 October 2026. EIA's interchange between pairs has run more than a day behind its demand.
- Demand of the seven ISOs: newest hour 2026-10-09 04:00 UTC (Oct 9, 00:00 Eastern) when the page was read; EIA
  publishes it one to two hours after the hour.
- Carbon intensity, the sphere color: daily.
- Batteries of the live week: EIA-930 for ERCOT, ISO-NE, MISO and SPP; CAISO's own data for CAISO; refreshed daily.
  NYISO and PJM report no battery series.
- Who supplies a grid, the last twelve months: EIA-930's daily interchange, refreshed with the warehouse; 2025-10 to
  2026-09 when the page was read.
- The two stories: fixed windows, pulled once (Uri: 2021-02-07 to 2021-02-24; the June 2025 heat: 2025-06-20 to
  2025-06-28).

The two newest hours are still on the page, live, in the line "Newest hour ... Demand of the seven ISOs".

### From the old page, the California data-break note (above its source line)

California's carbon intensity of generation is EIA's CO2 over EIA's generation before 16 December 2025 and over
CAISO's own generation from that date, joined there and not blended: [the method note](eia930_caiso_break.md).

(The date is written in one place, `site/lib/caisoJoin.ts`; the note is the component
`site/components/CaisoBreakNote.tsx`, which other pages still show.)

### From the old page, its source line

The old page's source line also named `eia930_daily_total_interchange` (the table behind the second of the three
measures above) and read "Built 2026-10-09 06:05 UTC, onto the daily build of 2026-10-09 05:05 UTC. Public domain
(EIA) and CAISO." on the day it was read. The page's source line is version 3's; the hour of the hourly refresh is in
the line under the network ("refreshed ...").

### From version 3's page (`/network/v3` until session 168), fold "The replay: what a day is"

- **A day is EIA's Eastern day**, from its daily interchange of every pair of balancing authorities, 2019 to
  2026-10-06 (the replay's last day when the page was read). A flow is the day's MWh over the day's hours: its
  average MW, so a day draws on the scale an hour draws on.
- **Each pair is counted once**, by the network's own rule: read from the balancing authority whose code sorts
  first, as it reported it; on a day it did not report, from the other's report with the sign flipped. A day neither
  reported is left blank.
- **704 pair-days are left out as days no tie can carry**: further than 10 median absolute deviations, and at least
  500 MWh, from the pair's own median. It is the rule of the monthly supply table; one such day would set the scale
  of a whole year.
- **A share of demand, by day:** each supplier's flow over the grid's demand that day, both as the day's average MW.
  Demand is EIA's daily figure, its own sum of the hours it holds; a day whose demand is not above zero, or outside
  half to twice the median of the six days around it, is not used and shows no share.
- **A day the record confirms is kept.** The rule above would leave out 2,740 pair-days in all. 1,918 of them are
  kept because both balancing authorities reported the day and their figures agree within 5 percent: two operators,
  one flow. 0 more are kept where only one side reports and EIA's hourly record shows no hour above what the same
  tie carried on other days. Among them are the days of Winter Storm Uri on which MISO sent the most to SPP, and the
  three days on which Texas's ties with Mexico ran at their highest level hour after hour.
- **A day with few pairs or none says so.** Where EIA's file is blank for a day (47 days in all, most of them in
  late 2025), the page says how many pairs the day holds and draws nothing in their place.
- **Not held by day:** the batteries.
- **Not drawn:** AEC, CFE, EEI, GLHB, GRIF, HGMA, NSB, SPC, WACM, which reported in those years and have no place in
  today's network.

(The counts are those of `site/public/network/daily_index.json` as built 2026-10-08 15:11 UTC: `pair_days_screened`
summed over the years, `pair_days_rule`, `pair_days_confirmed_both_sides`, `pair_days_confirmed_by_hours`,
`thin_days` and `left_out_bas`. The file holds the current ones.)

### From version 3's page, fold "Prices, and what the ring does not say"

- **The outer ring's weight follows the real-time price at the grid's main hub.** It is drawn only where a public
  price is held for the moment shown: in the replay, for CISO, ERCO, ISNE, MISO, NYIS, SWPP, and for most of them
  only from September 2024; ERCOT from 2019.
- **PJM has no ring:** its prices are licensed and not shown.
- **NYISO and ISO-NE have no ring: their prices are held for a license** (session 11000, 26 November 2026). Their
  terms ask for written permission, which the ERW has not recorded (`warehouse/metadata/license_verdicts.csv`), and
  their prices are held since 21 October 2026. The live week reads the live set, which holds them back; the files of a
  past day and of the June 2025 story still carried them, and until this session the replay printed the day's price
  and drew its ring. Now no view draws a ring or prints a figure of either: the panel reads "license needed" where
  the price would stand, with the reason on hover (`HELD_PRICE` in `site/lib/networkV3.ts`). That the files themselves
  still carry the prices is data request 576.
- **MISO has no ring: it is paused.** MISO's own files are paused since 4 October 2026 while a person reviews its
  terms. Its flows, demand and carbon here are EIA's, which are not paused. So this page shows no figure of MISO's
  price, in the live week, the stories or the replay. (Since session 168 the panel reads "paused while terms are
  reviewed" where MISO's price would stand, and the first two sentences of this bullet are its hover.)
- **A hub is not a site:** the price at one hub is not what power cost at every point of the grid.
- **The weight is relative to the highest price of the period shown**, by its square root, so that one scarcity
  hour does not turn every other ring into a hair. The panel gives the number.

### From version 3's page, fold "Trace the power: what it is, and what it is not"

- **Two steps.** For the grid selected, over the period shown: the neighbours that supplied it on net, largest
  first, with each one's share of that inflow; and for each of those, the neighbours that supplied it over the same
  period.
- **Physical flows, not contracts.** Who buys power from whom can differ from the path it takes.
- **Not where the power was generated.** A supplier generates most of what it sends; its own inflows are listed
  beside it, and nothing says their power is the power passed on.
- **Net, over the period.** A tie that carried power both ways counts by its balance; a neighbour that took power on
  net is not a supplier.
- **The period.** In the live week and the stories, the whole view. In the replay: the day shown, its month (as it
  opens) or the year; the panel says which, and how many of its days hold a flow for the grid.
- **Each tie is read once, by the network's rule** (the balancing authority whose code sorts first, as it reported
  it). The two sides of a tie do not always agree, so a figure here can differ from the same tie as the grid itself
  reported it, which is what the panel's twelve months use.
- **Nothing is traced through Mexico.** Its operator is one name in EIA's file, but its tie to California and its
  ties to Texas belong to systems that do not connect inside Mexico.

### From version 3's page, the line under its folds

"The three measures of each grid's imports, what the network is and is not, and how fresh each layer is: on the
network page." It pointed at `/network`, the old page. Since the two pages are one, the line is off the page: the
three things it named are the first three blocks of this section.

<a id="replication"></a>

## Replication

This section is the page's own download of one hour (`site/public/grid/`). The Grid tool's replication package, which recomputes every figure of the page (`replication/grid/`), is the section "Replication (sessions 3703 to 3705)" below (session 1884).

Session 1743 (chain 195, 6 November 2026) wrote this section, which the note lacked. The three decision tools' notes each have one ("Run it"). The package was in the repository since session 266 but was named only in the review pack (`docs/reviews/packs/grid.md`). Roadmap item 2 asks for "a replication a reader can run".

- **What it rebuilds.** The Network view's figures and the gravity shape's circles for the hour shown, which is the newest hour every reporting pair holds:
  - the balancing authorities drawn and the pairs reporting;
  - the hour's lag behind the snapshot's refresh;
  - for each of the seven ISO grids: its ties reporting, its net imports (negative: a net export) and their share of its demand;
  - for each, its net generation and the gravity shape's share, radius and distance (`site/lib/networkGravity.ts`).
- **The files** are the page's public downloads in `site/public/grid/`, served under `/grid/`:
  - `erw_2026_grid_replication.csv`: every value as the page reads it, nothing computed. It holds one row per balancing authority, each tie's flow in the hour, the seven grids' demand, and the net generation of the seven and the Lower 48.
  - `erw_2026_grid_replication.do` (Stata): rebuilds the figures from the CSV alone.
  - `erw_2026_grid_replication.py` (Python, standard library): the do-file step for step, printing the same lines.
- **Run it.**
  - Stata: `cd site/public/grid`, then `do erw_2026_grid_replication.do`.
  - Python: `python site/public/grid/erw_2026_grid_replication.py site/public/grid/erw_2026_grid_replication.csv`.
  - The do-file's header lists the values the mirror printed on 19 October 2026 (session 304).
- **The page moves every hour, the committed file does not.** The committed CSV is of the hour 2026-10-12 03:00 UTC (the snapshot refreshed 2026-10-14 08:05 UTC). To set a file beside today's page, write one from the page's own reads, then compare it with a running site value by value:
  - `node site/scripts/write-grid-replication.mjs <out.csv>` (the public key);
  - `node site/scripts/check-grid-replication.mjs <base-url> <out.csv>`.
- **The record.**
  - 14 October 2026 (session 266): 60 values, 0 different.
  - 21 October (session 422): a file written that day, 60 values, 0 different.
  - 6 November 2026 (session 1743): the mirror on the committed CSV, exit 0, 55 lines; the 16 the do-file's header lists are equal.
  - The do-file has not been run: Stata is not on the code machine.
- **Tests.** `tests/test_session266.py` and `tests/test_session304.py` hold the files to each other and to the house rules; `tests/test_session1743.py` holds this section and the block below.
- **The other parts of roadmap item 2.** The cross-check table is the section below. The decisions block is the page's "Decisions on this page" (`site/app/grid/page.tsx`, `data-decisions="299"`); section "One page, four tabs, and the Ask panel" above gives its rulings.

## Sign-off

Session 1743 added this block, which the note lacked. The battery's (session 1527), the generator's and the datacenter's notes (session 463) have one, and the Grid pack's "Against roadmap item 2" (session 381) lists "Samuel's signature, and a block to sign in". Signing this note accepts, as the tool's rules:
- EIA-930's interchange as the network's one source, with the pair rule;
- the newest complete hour (90 percent of the median hour's pairs) and the two-day lag said under the chart;
- EIA-930's net generation as the gravity shape's one source, CAISO's break said and not substituted;
- the square-root pull;
- the rulings of 18 October 2026 the page's decisions block carries (1a, 2c, 3c, 4b, 6a).

It leaves open what the section "Cross-checks" lists as not compared, and the "Checked against" line the page does not carry.

- Signed off by:
- Date:
- Items left open ruled, and how:

## Sign-off: the map and the thirteen regions

Session 8606 (chain 504) added this block for the two parts of the tool built on 19 November 2026. A session never signs it. Signing it accepts, as their rules:
- the map draws the network's own megawatts on the balancing authorities' published footprints, the hour, the pair rule and the colors being the Network view's;
- a region's net exchange is the sum of its pairs, each read from one side, and is not the authority's own total interchange (section "The map's done line");
- an authority with no boundary in the file is listed, not placed by hand; state lines are drawn and names stay on hover;
- a region is one of EIA's thirteen, drawn from the data machine's files with nothing filled: a part not held is blank with its reason, a month not held is absent and counted, a part of a month is shown as held;
- hour by hour, a source below zero is drawn down from zero; the Storage row says who files no battery series and its figure is not changed.

It leaves open the rulings the signature pack lists (`docs/reviews/grid-map-regions-signature-pack-2026-11-19.md`), each with its default taken, and the data requests 540, 541, 544, 549 and 551.

- Signed off by:
- Date:
- Items left open ruled, and how:

<a id="cross-checks"></a>

## Cross-checks

Session 381, 21 October 2026 (roadmap item 2, "a cross-check table against published figures"), in the form of the three decision tools' notes (`battery_earns_algorithm.md`, `generator_earns_algorithm.md`, `datacenter_pays_algorithm.md`: our figure, the published figure, where it was read, the gap, the reason). Every published figure below is one the ERW already holds with its source; none was fetched for this table, and no figure of the page moved. The rows are those of the review pack's part 4 (`docs/reviews/packs/grid.md`) whose other side is a publisher's figure; the pack's rows that set the page against its own tables (the replication file, `check-values`) stay there. EIA-930 is EIA's own hourly report, so a row against it checks our sums and our reading of the hour, not EIA's figures. "Gap" is ours less theirs.

| Our figure | Published figure | Source and date | Gap | Reason |
|---|---|---|---|---|
| ERCOT (ERCO), net generation 2025, the sum of EIA-930's hours: 485.2 TWh | 541.8 TWh, Form EIA-923's plant rows summed by their balancing authority code (`eia_annual_generation_ba`) | [EIA, Form EIA-923, 2025 final file](https://www.eia.gov/electricity/data/eia923/xls/f923_2025.zip), Last-Modified 11 September 2026, read 19 October 2026 (session 323, `docs/methods/eia_annual_crosscheck.md`) | -10.45 percent | Likely, not EIA's statement: EIA-930 is what the balancing authority meters, EIA-923 each plant's own net generation, industrial self-generation used on site among it. 48 hours of 2025 are missing from EIA-930 for ERCO; at the year's mean hour they explain none of the gap |
| CAISO (CISO), the same: 185.4 TWh | 203.1 TWh | the same | -8.72 percent | The same reason; 2023 and 2024 read -9.18 and -8.35 |
| PJM, the same: 873.8 TWh | 878.1 TWh | the same | -0.48 percent | Within 1 percent in each of 2023 to 2025 |
| SPP (SWPP), the same: 302.1 TWh | 293.2 TWh | the same | +3.05 percent | EIA-930 higher: likely generation SPP meters from plants EIA-923 codes to another authority |
| The Lower 48 (US48), the same: 4,280.5 TWh | 4,494.7 TWh, every code but none, HECO and EIA's state-fuel increment | the same | -4.76 percent | The sum of the reasons above; 2023 and 2024 read -4.27 and -4.38 |
| Sum of each ISO grid's reported ties, 360 hours from 2026-09-13 to 2026-09-28 | EIA-930's net generation less demand for the same grid and hours (`eia930_all_generation`, `eia930_all_demand`) | [EIA, Hourly Electric Grid Monitor (Form EIA-930), API v2 `electricity/rto`](https://www.eia.gov/opendata/browser/electricity/rto), read by session 49 (this note, "The source") | Mean absolute gap: ERCOT 1.6 MW, NYISO 0.4, ISO-NE 0.7; CAISO 3,199.1, PJM 2,042.1, MISO 1,397.9, SPP 978.1 | For the last four, the interchange a grid reports does not close EIA's own balance of its generation and demand: a property of the data, recorded, not corrected |
| Net imports by ties in the hour shown on 14 October 2026 (2026-10-12 03:00 UTC): ERCOT 128, ISO-NE 156, NYISO 2,120 MW | EIA-930's demand less net generation in that hour: 128, 156, 2,111 MW | [EIA, Form EIA-930, API v2 `electricity/rto`](https://www.eia.gov/opendata/browser/electricity/rto), read through the live set on 14 October 2026 (session 266, `site/public/grid/erw_2026_grid_replication.csv`) | 0, 0, +9 MW | The three grids whose ties close EIA's balance |
| The same hour, the four others: CAISO 6,591, MISO 1,561, PJM -1,544, SPP -437 MW | 7,058, 103, -1,462, -964 MW | the same | -467, +1,458, -82, +527 MW | As over the 360 hours above; CAISO's gap also carries EIA-930's lower California generation (the next row) |
| California's generation, the mean of 888 hours from 2026-08-26 to 2026-10-02, EIA-930: 22,618 MW | CAISO's own supply figure: 24,358 MW (`caiso_fuel_supply`) | [CAISO, Today's Outlook, supply](https://www.caiso.com/todays-outlook/supply), as held; compared in `docs/methods/eia930_caiso_break.md` ("What was wrong with the denominator") | -1,740 MW | EIA's solar reads 944 MW lower and its wind 473 MW lower than CAISO's own; gas, geothermal, hydro, nuclear and coal agree within 1 MW |
| The newest complete hour on 13 October 2026 at 07:57 UTC: the hour beginning 2026-10-11 03:00 UTC | The same hour on EIA's API route and in EIA's bulk file `EIA930_INTERCHANGE_2026_Jul_Dec.csv` | [EIA, Form EIA-930 bulk files](https://www.eia.gov/electricity/gridmonitor/), read 13 October 2026 (session 247, this note, "How far behind the newest hour is") | 0 hours; both 53 hours behind | The lag is EIA's publication, not the ERW's refresh |
| One tie, MISO to SPP, 15 February 2021: MISO's report, 95,060 MWh | SPP's report of the same tie: 95,390 MWh | [EIA, Form EIA-930, API v2 `electricity/rto/interchange-data`](https://www.eia.gov/opendata/browser/electricity/rto/interchange-data), as held in `eia930_all_interchange` (`docs/methods/grid_network_v3.md`, the replay) | -330 MWh (0.3 percent) | Two operators' reports of one flow; the network reads the code that sorts first (the pair rule) |

- Not compared: an operator's own tie flows (ERCOT's DC ties, CAISO's interties). No connector holds them.
- Not compared: EIA's Electric Power Annual by balancing authority. It publishes no table by balancing authority (`docs/methods/eia_annual_crosscheck.md`, section 1); Form EIA-923 stands in for it above.
- Not in the table: ERCOT's 2023 peak demand, 85,432 MW in the highest hour of EIA-930 against ERCOT's record of 85,508 MW (`docs/methods/demand_growth.md`). The note quotes ERCOT's record without the address it was read from, so it is listed here and not set in the table.
- Not in the table: ISO-NE, MISO and NYISO against Form EIA-923 (2025: -4.91, -6.68 and -3.09 percent). `eia_annual_crosscheck.md` gives the gaps and not the two totals, and `eia_annual_crosscheck_ba` is not in the live set (a read on 21 October 2026 answered "Could not find the table"), so their TWh are not quoted.
- The page carries no "Checked against" line yet, unlike the three decision tools: adding one changes the page's words, and is listed in the session's report for Samuel's ruling.

- **Session 3705 (chain 208).** The table of the Grid tool's headline figures against figures others publish, one row a figure, is `docs/methods/crosschecks/grid.md` (sessions 3708 to 3710). The replication below holds the page to its own inputs; this section and that file hold the inputs to other publishers.

## The figures on the page and their keys

Each number `/grid` shows carries its key (`site/components/Num.tsx`), which `site/scripts/check-values.mjs` checks against the live set and `site/scripts/check-methods.mjs` against this note (session 409). The keys the sections above do not name:

- `bsup|<BA>|share:pairs`, `bsup|<BA>|mwh:pairs`, `bsup|<BA>|days_held`: on the Gravity tab, under the gravity shape, the Exchange view's block "Over the last twelve months" (`components/grid/ExchangeView.tsx`): the grid's net imports as a percent of its demand, by the sum of its reported ties (`pairs`), the same net imports in MWh, and the days held, computed from `ba_supply_monthly` by `site/lib/basupply.ts` as "Who supplies a grid" above describes.
- `bsup|<BA>|neighbour_mwh:<ID>`, `bsup|<BA>|neighbour:<ID>`: the table of the grid's neighbours over the same twelve months: each neighbour's net import into the grid in MWh, and its percent of the grid's demand.
- `net|maxflow|<BA>|<hour>`: the Exchange view's headline "Largest flow": the largest flow, either way, over the grid's reporting ties in the hour shown, in MW, read from the network's snapshot of `eia930_all_interchange`.
- `net|topexport|<hour>`: the Exchange view of the Lower 48, in its first paragraph: the largest net export of any balancing authority in the hour shown, in MW, its reporting ties summed and signed from its side (`netExports` and `topExporter` in `site/lib/network.ts`), from the same snapshot; two authorities with the same net export give it to the first by its id.

## Replication (sessions 3703 to 3705)

Roadmap item 2 asks for a replication a reader can run. `replication/grid/` is the Grid tool's, in the form of the three decision tools' packages (`replication/battery/`, `generator/`, `datacenter/`) and Research's (`replication/analysis/`). It reproduces the figures the page prints from EIA-930 and the warehouse's tables:

- the network snapshot the page draws: public Storage's `erw-public/network/grid_network.json`, or the committed `site/data/grid_network.json`;
- the warehouse's tables as CSV: `eia930_all_emissions`, `carbon_intensity_hourly` and `carbon_intensity_monthly`, `eia930_all_generation`, and the tables the Ask panel's stored answers read;
- this folder's `assumptions.json`: every assumption, its default, its source and how to change it (the section below).

Since session 5005 (13 November 2026) `figures_of_the_page.py` keeps the snapshot it read beside the figures (`replication/grid/snapshot.json`), and `replicate.py` reads that copy when no `--snapshot` is given. Until then a run with no argument stopped (exit 2) the day after the figures were written, because the daily run rewrites `site/data/grid_network.json`. `--snapshot site/data/grid_network.json` still sets today's snapshot beside the figures, once they are written again from it.

| File | What it does |
|---|---|
| `figures_of_the_page.py` | Writes `page_figures.json` and `.csv`: the figures the page prints, each with its check key, the value and the tolerance (half of the last digit the page shows, as `site/lib/format.ts` writes it). It also writes `snapshot_hour.csv` (the snapshot's hour shown, for Stata) and `replicate_ask.do`. The network's figures come from the page's own functions, which `network_figures.mjs` runs with node (`site/lib/gridKeys.ts`, `networkV3.ts`, `network.ts`, `networkGravity.ts`: pure, type imports only). The carbon months are the rows the Clean tab's monthly block names. The Ask figures are the stored answers the panel shows, with the license hold the panel applies on the day |
| `replicate.py` | Standard library and pandas only. It recomputes every figure without the page's code. The network: the hour shown, its age, each grid's ties signed from its side, net export and import, the number of ties, the largest flow, the largest net exporter, and the gravity shape's net import, generation and share where the tables hold the hour. The carbon months: each month's CO2 (`eia930_all_emissions`, `co2_emissions_generated`) over its MWh, each hour's MWh being its CO2 over its intensity, over months whose every UTC day holds 24 hours. The Ask answers: each stored query run again with the Ask tool's rules (`warehouse/chat/tools.py`: the filters, the grid's scope, latest, mean, sum, min, max or count, the groups). `mix_now()` applies the Mix tab's latest-hour rules (`components/grid/NowView.tsx`) to rows a reader reads |
| `replicate.do`, `replicate_ask.do` | The network's hour, the carbon months and the Ask panel's 24 plain queries in Stata, in the owner's rules; since session 5074 also each grid's carbon intensity in the hour shown (the hour's own row, as `replicate.py` reads it). Not yet run: no Stata on the machine that wrote them. `tests/test_session5074.py` holds them to `replicate.py`: every family of check keys the page prints is built by `replicate.do`, and every Ask figure is either stated by `replicate_ask.do` with the page's value and tolerance or named there as `replicate.py`'s or "license needed" |
| `assumptions.json` | The 25 assumptions (below) |

**What it found on 6 November 2026** (the snapshot built 2026-11-05T23:09:35Z, hour shown 2026-11-03T23:00 UTC; the tables of `warehouse/output` on the portable laptop, retrieved 26 September to 2 October 2026):

- 188 figures; 158 computed, **147 met**.
- **Network and Gravity: 85 of 85.** The page's own code and the replication agree on every figure; the test holds them to each other on whatever snapshot is committed.
- **Carbon: 14 of 14 months** of the Clean tab's monthly block, rebuilt from the hours to within 0.0001 kg CO2 per MWh.
- **Not held in the tables given: the network's 7 hourly carbon figures** (the hours of 30 October to 2 November are after the tables' copy).
- **Ask: 48 of 59 met; 11 a known difference.** Each of the 11 is an answer asked on 14 or 19 October of the live set, against a copy of its table made on 26 or 30 September or 2 October. The CAISO answers moved with the California join's rebuild; SPP's queue gained a project. One answer's table (`ercot_hub_prices_daily`) is not on the machine.
- **22 "license needed":** the stored answers of ISO-NE, MISO and NYISO whose tables are held for those grids.
- **Not replicated:**
  - the Mix tab's and the Clean tab's latest hours. These are live reads; the package's `mix_now()` applies the rules to rows a reader reads with the site's public key, and this chain read no row of the live set.
  - the hourly carbon intensity itself. Its denominators are EIA's per-BA workbooks, which no table holds.
  - the Mix tab's other views, built from EIA's workbooks on the data machine.
- **The test:** `tests/test_session3703.py`. It runs both computations of the network on the committed snapshot, so the daily run's new snapshot never turns it red. The carbon and Ask checks run where the tables are, and skip in a clean checkout. It also checks the Mix tab's rules on a fixture, the license hold against the site's, the query rules on a fixture, the imports, and both do-files' rules.

**What it found on 14 November 2026** (session 3962, chain 278, five-tools request 3; the snapshot built 2026-11-12T21:46:53Z, hour shown 2026-11-09T23:00 UTC; the tables of `warehouse/output` on the data machine, the EIA-930 tables retrieved 13 November):

- 203 figures; 181 computed, **178 met**; 22 license needed; **0 not held in the tables given**.
- **Network 70 of 70, Gravity 30 of 30.** With `eia930_all_generation` held, the gravity shape's generation for the seven grids and the Lower 48, and each grid's net import as a share of its generation, are computed by `replicate.py` and, since this session, by `replicate.do` (section 1b).
- **Carbon: 21 of 21** (the months and the network's hourly colours).
- **Ask: 57 of 60 met; 3 a known difference** (SPP's answers asked on 14 October, against copies of their tables made on 5 November and 26 October).
- **The tests held to it:** test 3703 runs the page's own code again with the committed file's generation figures, and test 5074 gives them to `replicate.py`: the generation is an input read from the table, as the snapshot is, and the share is computed from it by both. Until this session both tests compared against a run without generation, so a file written where the table is held could not be committed (session 3936).

The earlier files stay as they were: `site/public/grid/erw_2026_grid_replication.{csv,do,py}` (session 266), the Network view's hour of 12 October 2026, the page's download.

## Decisions: every assumption, its default, its source, how to change it (session 3705)

Roadmap item 2's decisions block for the Grid tool. The table is `replication/grid/assumptions.json`, word for word (`tests/test_session3705.py` holds the two to each other). The page's own block, "Decisions on this page" (`site/app/grid/page.tsx`, `data-decisions="299"`), carries the owner's five rulings of 18 October; they are rows here too. No page was changed.

| Assumption | Default | Source | How to change it |
|---|---|---|---|
| `network_window_hours` | 168 (hours) | warehouse/derived/grid_network.py: the snapshot holds the last week of EIA-930's hourly interchange (hours, links' mw arrays of 168) | the window of grid_network.py and network_hourly.py; the page draws whatever the snapshot holds |
| `network_snapshot` | the hourly copy in public Storage, else the committed one | site/lib/network.ts pickSnapshot: Storage's erw-public/network/grid_network.json when it is whole and its newest hour is not older than site/data/grid_network.json's | site/lib/network.ts |
| `network_pair_rule` | each pair once, read from the BA whose code sorts first | warehouse/derived/grid_network.py (the snapshot's rule): a pair's flow is the one the first BA in code order reported, positive when it exported | warehouse/derived/grid_network.py |
| `network_quiet_hours` | 48 (hours) | site/lib/networkV3.ts completeHour, quiet = 48: a pair that held no flow in the snapshot's last 48 hours is silent and does not hold back the hour shown | the default argument of completeHour in site/lib/networkV3.ts |
| `network_hour_shown` | the newest hour every reporting pair holds | site/lib/networkV3.ts completeHour and site/lib/gridKeys.ts shownHour; the newest hour of all when no hour is whole | site/lib/networkV3.ts |
| `network_sign` | positive: power left the grid | site/lib/gridKeys.ts tiesOf and site/lib/network.ts netValue: a tie's flow is signed from the grid's side; net export is the sum over its reporting ties, net import the same sum from the other side | site/lib/gridKeys.ts |
| `network_top_exporter_tie` | the first in code order | site/lib/network.ts topExporter: of equal net exports, the balancing authority whose code sorts first | site/lib/network.ts |
| `network_lag_rounding` | half up | site/lib/network.ts netValue, net|lag: the hours from the hour shown to the snapshot's refresh, by JavaScript's Math.round | site/lib/network.ts |
| `gravity_source` | EIA-930 net generation for every circle, CAISO's included | the owner's ruling 1a of 18 October 2026 (docs/methods/grid_network.md, "One page, four tabs, and the Ask panel"); the line under the frame names California's break of December 2025 | a ruling |
| `gravity_pull` | sign(share) x sqrt(|share| / 0.25), held to one | the owner's ruling 2c of 18 October 2026; site/lib/networkGravity.ts | site/lib/networkGravity.ts GRAVITY.S_FULL and the pull's formula |
| `gravity_full_pull_share` | 0.25 (share of the grid's net generation) | site/lib/networkGravity.ts GRAVITY.S_FULL | site/lib/networkGravity.ts |
| `gravity_others` | the 63 other balancing authorities are not drawn | the owner's ruling 6a of 18 October 2026: their net generation is not in the live set; the line under the frame counts them | a ruling |
| `grid_opening` | US48, the Lower 48 | the owner's ruling 4b of 18 October 2026; site/lib/gridtool.ts gridPick | site/lib/gridtool.ts |
| `carbon_intensity` | CO2 generated x 1,000 over net generation (kg CO2 per MWh) | warehouse/derived/carbon_intensity.py; docs/methods/emissions.md: EIA's CO2 Emissions Generated over the Net generation column of the same EIA-930 workbook row | warehouse/derived/carbon_intensity.py |
| `carbon_daily_monthly` | energy-weighted over whole UTC days and months | docs/methods/emissions.md: a day is its CO2 over its MWh over UTC days with all 24 hours; a month the same over months whose every day is complete | warehouse/derived/carbon_intensity.py |
| `carbon_left_out` | months computed on an impossible hour, and California's months without hydro, are not shown | site/data/carbon_left_out.json (warehouse/derived/carbon_left_out.py, docs/methods/impossible_hours.md); held until a person approves the rebuilt table | a person's approval of the rebuilt carbon tables |
| `mix_latest_hour` | the latest hour that holds the total net generation | components/grid/NowView.tsx: its sources largest first; demand's latest hour and the same hour a week earlier | components/grid/NowView.tsx |
| `mix_caiso` | EIA-930's generation for California is not drawn; CAISO's own supply from 2025-12-16 | components/grid/NowView.tsx (session 118) and docs/methods/eia930_caiso_break.md (the one join of the warehouse) | docs/methods/eia930_caiso_break.md |
| `mix_sources` | natural gas, coal, nuclear, wind, solar, hydro, storage, other | docs/methods/generation_mix_hourly.md, "The sources": EIA's codes grouped as the site groups them | warehouse/derived/mix_profile.py |
| `clean_sources` | nuclear, wind, solar, hydro | site/data/clean/<grid>.json clean (docs/methods/clean_energy.md, "Carbon-free") | warehouse/derived/mix_clean.py |
| `clean_levels` | 50, 75 and 90 (percent carbon-free in an hour) | site/data/clean/<grid>.json levels | warehouse/derived/mix_clean.py |
| `ask_examples_per_grid` | 5 (stored answers) | site/data/grid_ask_examples.json max_examples: answers a recorded evaluation graded right, each figure traced to its tool result | site/scripts/build-grid-ask-examples.mjs |
| `ask_scope` | a grid's own chat and the Grid panel's profile read only that grid's rows | warehouse/chat/tools.py scope_rows with docs/grids/grids.json and docs/grids/grid_tables.json; the general chat reads every row | docs/grids/grid_tables.json |
| `license_held_grids` | isone, miso, nyiso | site/data/license_status.json, read by site/lib/license.ts on 6 November 2026 (from 21 October 2026): a figure of a table held for a grid prints "license needed" | a publisher's permission recorded in site/data/license_status.json |
| `tolerance` | half of the last digit the page shows | site/lib/format.ts shown(): a whole number as a count, any other with two decimals; a stored answer's figure as its text has it | page_figures.json, written by figures_of_the_page.py |
