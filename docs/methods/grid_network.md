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

**The outlines, the lines and a click (session 1156, 23 October 2026).** What the map already did, and what was added:

- **The projection and the outlines are the project map's.** The map has always used the project map's projection (`geoAlbersUsa().scale(1300).translate([W / 2, H / 2])` on a 975 by 610 plane, the same numbers as `site/app/map/ProjectMap.tsx`). Since session 1156 it also draws the project map's state outlines, from the same file (`us-atlas`'s `states-albers-10m.json`, the Census Bureau's cartographic boundaries, already on that plane): the land under the regions, so a county no grid is given reads as land, and the borders between states over them. The derived areas, their label and their colors are unchanged.
- **The lines.** Each tie with a figure in the frame shown is a line between the two areas' points, from the exporter to the importer, with its arrowhead at the importer (as since session 180); a tie with no figure in the frame, or a zero, is not drawn (`edgesAt` in `site/lib/networkMap.ts`, the network's own rule moved there unchanged). The middle of each line answers a hover with its direction ("From SPP to ERCOT"), its window ("In the hour from ..., snapshot refreshed ...", the gravity shape's words; a day of the replay, "On ..., EIA's Eastern day") and its source. The ends of a line take no pointer, so a click near a region's point is the region's.
- **A line's MW is written only where the panel under the map holds it.** The map is drawn in the browser; the checked figures are the server panel's under it (`grid_network_<grid>`, session 1151, `components/grid/NetworkFigures.tsx`): the grid in view's ties in the hour the component opens on. So a line's hover gives its MW only for a tie of the grid in view, in that hour of the live week, and that MW is the panel's own figure (`edgeHeld`; `scripts/test-network-map.mjs` proves it for each of the seven grids on the committed snapshot). Any other line, another hour, a day of the replay, a story and the Lower 48 (whose panel holds no tie) say where the checked figure is, and its width follows the flow as before. No other number is written on the map.
- **Every line is public.** The lines are EIA-930's interchange, which is public domain, for every grid, PJM, MISO, ISO-NE and NYISO included (their own tables are held or paused here). No price is drawn on the map: the Prices switch's ring is drawn in the Network shape only, and the panel's hub price follows its own rules (PJM not shown, MISO paused). The note under the map says both.
- **A grid clicked.** One of the seven ISO grids of the picker (`site/lib/gridtool.ts` `GRID_CHOICES`) other than the grid in view is a link to its row on the Grid tool: `gridHref(slug, "network", { shape: "map" })`, the map again, with the moment shown carried (the replay's day or story as `net`, and its `t`). That address opens the grid's own panel (its node is the grid's own) and the panel under the map with that grid's checked ties, so the reader stays on the map and the clicked grid's lines gain their MW. The Mix tab was the other choice; it is one click away in the tabs. The grid in view, and every other balancing authority, opens its panel, as before.

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
- **Edges and their hover (session 1153).** The lines from the Lower 48 to the grids are the shape's edges. Each carries
  the grid's net exchange in the hour shown (the sum of its reporting ties, as above), and a grid with no tie reported
  in the hour has no edge: no line is drawn without a figure. Hovering an edge gives its net import or export in whole
  MW, its share of the grid's net generation and its window, the hour shown and the snapshot's refresh ("In the hour
  from 2026-10-21 23:00 UTC, snapshot refreshed 2026-10-23 14:36 UTC"); hovering a circle adds the grid's net
  generation. The words are `gravityTip` in `site/lib/networkGravity.ts`, tested by `site/scripts/test-gravity.mjs`.
- **One public source, for every grid (session 1153).** Every place and size is drawn from EIA-930's interchange and
  net generation, which are public domain, for every grid, PJM, MISO, ISO-NE and NYISO included, whose own tables are
  held or paused (`site/lib/license.ts`): no grid operator's own table places or sizes a circle, and the note under the
  frame says so. The color is not EIA-930's alone: it is `carbon_intensity_hourly`, EIA-930's emissions over net
  generation, and for California since 16 December 2025 over CAISO's own generation (the join,
  `docs/methods/eia930_caiso_break.md`).
- **A replayed day (session 1153).** The replay's files (`site/public/network/daily_<year>.json`, from
  `eia930_daily_interchange` and `eia930_daily_demand`) hold each day's interchange and demand but no generation, so the
  shape draws nothing for a replayed day and says so; the day stays in the address (`net=day&t=<day>`), and on the
  Gravity tab the grid picker carries it (`site/lib/carry.ts`), so picking another grid keeps the day. The panel under
  the shape (`grid_gravity_<grid>`) draws the live week's hour only, and says that no figure in it is the day's.
- **The nodes.** The shape's grids are the seven ISOs of `GRAVITY_GRIDS`; their names come from the snapshot's `nodes`
  (`site/data/grid_network.json`, or the hourly snapshot in Storage), which `warehouse/derived/grid_network.py` writes
  beside the warehouse table `grid_network_nodes`. That table is not in the live set: the page reads no
  `grid_network_nodes` rows.

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
no number moved. Since session 1172 `site/scripts/test-grid-addresses.mjs` holds this to every address: it follows each
redirect to `/grid` in `site/next.config.ts` as Next applies it (the rules in order, their query conditions, the old
address's query carried under the destination's words) and `/ask`'s own redirect, then reads the result as the page
does, so `/network`, `/network/v3`, `/mix` with each of its views, `/mix/v2`, `/mix/clean`, `/mix/stress`, `/emissions`,
the seven `/grid/<iso>` and the old words (`view=now`, `exchange`, `ask`; `mix=clean`; `shape=gravity`; a grid as
`grid=ERCO`, `ba=erco` or `grids=pjm,miso`; `node=BPAT`) each open the tab that holds their blocks with the grid they
named, `net`, `t`, `node`, `mix`, `mixp`, `shape` and `q` kept; and an address written by `gridHref`, the picker's
carried day, the map's region link or the network's own writes reads back to the same grid and tab. The route check
lists one address of each. The rulings the page carries, said on the page in its decisions block:

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

## The Grid tool's panels, every figure keyed (chain 077, 23 October 2026)

Chain 077 (sessions 1150 to 1161, `queue/done/077-day-23-october-code-grid-tool.md`) set out to make every figure of
`/grid` traceable. Session 1150's review (`docs/reviews/grid-tool-2026-10-23.md`) found that the Network tab carried
one check key and the Gravity shape five: the network component draws its figures in the browser, where none can be
checked. The rule the chain set: **every figure the tool draws in the browser has a twin drawn on the server**, in a
panel wrapped in `data-grid-panel="grid_<panel>_<grid>"`, each figure drawn through `site/components/Num.tsx` with a
key `site/scripts/check-values.mjs` recomputes and a one-line hover tip (its table, filter, hour or window, and the
snapshot's refresh). The panels, by tab:

- **`grid_network_<grid>`, the Network tab (session 1151, `site/components/grid/NetworkFigures.tsx`, the figures in
  `site/lib/gridKeys.ts`).** The grid in view in the hour the network component opens on, the newest hour that every
  reporting pair holds, so the panel and the drawing show the same hour: each reporting tie's MW and direction
  (`net|tie|<BA>|<other>|<hour>`), the net export or import (`net|export|<BA>|<hour>`, `net|import|<BA>|<hour>`), the
  number of ties (`net|ties|<BA>|<hour>`) and the grid's demand in that hour, read as the component reads it (the
  week's `eia930_all_demand` first, else the hourly snapshot's), keyed `netsnap|<BA>|demand_mw|<hour>` when the hourly
  snapshot holds that figure and `series|eia930_all_demand|eia930:<BA>|demand_mw|<hour>` otherwise (`demandAt`). For
  the Lower 48, the seven grids' net export and ties.
- **`grid_gravity_<grid>`, the Gravity tab (sessions 1151 and 1153).** What the gravity shape draws: each of the seven
  grids' net generation (`series|eia930_all_generation|eia930:<BA>|net_generation_mw|<hour>`), net import
  (`net|import|...`) and the import as a percent of generation (`calc|pct|<the import key>|<the generation key>`),
  the grid in view highlighted, the Lower 48's generation (the shape's scale) in the note. The section "The gravity
  shape" above gives its edges, its one public source and the replayed day.
- **`grid_clean24_<grid>`, the Clean tab (session 1151, `site/components/grid/Emissions.tsx`).** Under "The last 24
  hours": each of the seven ISOs' latest hour, and the lowest and highest of the 24 hours drawn, each
  `series|carbon_intensity_hourly|<entity>|intensity_generation|<hour>`, the grid in view highlighted. The table is
  `emissions.md`'s.
- **`grid_mix_<grid>`, the Mix tab (session 1152).** The energy mix's 24 hours and the monthly view:
  `generation_mix_hourly.md`, "The Mix tab's energy mix, keyed, hourly and by month".
- **`grid_scarcity_<grid>`, the Mix tab (session 1154).** `scarcity_hours_by_grid.md`, "On the Grid tool".
- **`grid_caisoalert_caiso`, CAISO's Mix tab (session 1155).** `california_reliability.md`, "On the Grid tool: the
  alert state".
- **`grid_ask_<grid>`, the Ask panel (session 1157).** Stored answers, no key: below.

**The keys.** Every key of these panels is of a kind check-values knew, with three changes. Session 1152 let `series_sum`'s
variable part name several variables, comma separated (a fuel group), recomputed with `in.(...)`; no earlier key holds
a comma, so none changes what it computes. Session 1154 added `series_n|<table>|<variable>|<start>|<end>|<entity>`,
the distinct hours the rows hold. Session 1155 added two forms of session 58's `awe` family, `awe|last|<group>|<day>`
and `awe|ndays|<group>|<from>|<to>`. `site/scripts/check-methods.mjs` names each (session 1162: a comma list is a
figure of each of its variables).

**The map and the gravity shape, after the chain (sessions 1156, 1158).** A line of the map gives its MW only where the
panel under it holds the figure (the section "The map", session 1156's paragraph). On a phone a tap on a line, the
Lower 48 or a circle opens its card, which stays until the next tap, and a card is never wider than the frame
(`cardWidth` in `site/lib/networkMap.ts`, at most 20rem); the mouse's hover is as before. Neither drawing takes an ARIA
role: the svg's own, with its name, since an image role hides the regions and links a keyboard reaches and a group role
is not allowed on an svg. A line answers a pointer, not the keyboard; its figure is in the keyed panel, which does.

**The day in the picker.** On the Network and Gravity tabs the grid picker carries the replay's day: `grid_network_v3.md`,
"The day carried from grid to grid".

**California's join date, in one place.** The gravity shape's note writes the day California's generation joined
CAISO's own (`carbon_intensity_hourly`'s color) through `caisoJoinDay()` (`site/lib/caisoJoin.ts`), not as a date
(the orchestrator's fix after session 1159, commit `169e537a`): `tests/test_session78.py` allows the date in that one
file.

**The stored answers of the Ask panel (session 1157, `site/components/grid/AskExamples.tsx`, `site/lib/gridask.ts`).**
Under the live Ask box, for the grid on screen, up to five answers of past evaluations, each a closed `<details>` with
the question as its summary, holding the answer as stored, each figure's table and filter and the day it was asked,
and the run it came from (file, question id). No model is called, and the live box is not changed (chain 075's). The
selection, made by `site/scripts/build-grid-ask-examples.mjs` into `site/data/grid_ask_examples.json`:

- **Only runs that kept every tool call's result:** `warehouse/chat/eval/eval_s302_fixtures.json` (19 October 2026)
  and `eval_s267_fixtures.json` (14 October). `eval_s320_first_run.json` kept the count of calls only, so none of its
  figures can be traced, and it is left out whole; the data file says so. Since session 1187 (chain 091) four later
  runs of 23 October 2026 too, each with its grades file: "The stored answers, refreshed" below.
- **Kept:** graded right by its run (verdict right, grade ok); about one grid (a comparison of two grids is shown for
  neither); every figure of the answer found in a non-error tool result of its own run at the rounding it is written
  to (the number check of `lib/chat/ask.ts`, ported). Dates, clock times, years, list markers and the question's own
  numbers are not figures. Refusals graded right ("not in the warehouse") are kept, after the answers with figures.
- **Order:** the route the panel itself sends first (ERCOT its profile, the Lower 48 the general chat, the others the
  grid's own chat), then the newest run, then answers with figures before refusals. At most five; fewer is said in
  words ("Four stored answers for NYISO so far").
- **Held tables, on the day the page is drawn:** an answer any figure of which comes from a table held for its grid
  (`site/lib/license.ts`, `licenseHeldRow`; the figure's entity, or the answer's grid when the call named none) is not
  shown; in its place, the words the live Ask's tools receive for that read (`licenseReason(table)`) and the table's
  name.
- **No check key:** these are stored texts of a past evaluation, not figures read from the database; the panel carries
  `data-ask-stored="1"` and says the figures are as of the day asked.

**Not keyed yet (session 1151's list).** Each draws a number from the database that would need a new key kind or a
change to how it is written: on the Mix tab, "Yesterday"'s forecast error at the peak, its mean absolute error and the
degree days (`components/grid/Conditions.tsx`); each fuel's share in "Generation mix, as a table" (one decimal, a
share over several variables); "Hours held" in the grid's 30-day mix table (`components/grid/YourGrid.tsx`); "The
table holds N notices" (`components/grid/Reliability.tsx`); and the network component's own side panel (the hub
price, the batteries, the replay's days), drawn in the browser.

**The reads (session 1160).** Every read of `/grid`, `/grid/caiso/alerts` and `/network` was timed three times
(`site/scripts/time-grid-reads.mjs`, which calls the pages as Next renders them): the slowest median 117 ms, none over
a second, each served by an index the live set has, so no index was added. Three reads were made smaller with the same
rows drawn (`generation_mix_hourly.md` and `california_reliability.md` say which). Left as they are: the network
snapshot is read twice on the Gravity tab on purpose, by the network (cached an hour) and by the Exchange blocks
(fresh).

Decisions (chain 077):

- **A server twin, not a key inside the browser drawing**: the drawings are drawn after the page is served, so
  check-values cannot read them; the twin is what the reader can trace and the checker can recompute. The drawings'
  hover cards stay unkeyed, as the shared charts' cards are.
- **The Gravity tab's panel shows what the shape draws**, not a second copy of the grid's ties: the Exchange blocks under
  it already key the ties, the net and their count in the same hour.
- **The Clean tab's panel shows all seven ISOs**, as its chart draws seven lines, the grid in view highlighted.
- **The hub price stays in the browser**: a price key needs the price board's interval rules or the market table's
  hourly mean; left for a later session.
- **A line of the map gives its MW only for the grid in view's ties in the panel's hour**; whether every tie's MW may be
  written is put to the owner (`docs/reviews/grid-rulings-2026-10-23.md`).
- **No keyboard stop on each line** of the map (about a hundred) or the gravity shape: it would bury the regions; the
  same figures are in the panel, which a keyboard reaches. Put to the owner as a design choice.
- **Stored answers only from runs that kept their tool results**, so that each figure shown can be traced to the call
  that returned it; a held table's answer is replaced by its license words, never drawn.
- **No index added**: the slow days of 21 and 22 October were the whole database (a primary-key read was slow too),
  not a missing index.

## The balance, said where the figures are (chain 078, 24 October 2026)

Chain 078 in this note (sessions 1164 to 1177): 1165 (this section), 1167, 1171 and 1172 (below), 1175 (the next
section); 1170's keys in the list at the end, its method in `grid_network_v3.md`; 1164, 1166, 1168, 1169, 1173 and
1174 set no rule here.

Session 1165 (`queue/done/078-day-24-october-code-grid-tool-2.md`), the Grid pack's blind spot 3
(`docs/reviews/packs/grid.md`, section 6): for CAISO, PJM, MISO and SPP the ties do not sum to net generation minus
demand. The Network tab's panel `grid_network_<grid>` now says so for the grid in view, under its ties, in a block
`data-grid-balance="<BA>"` ("Does <grid>'s balance close?"), for each of the seven ISO grids, the ones that close
included. In the hour the panel shows: the grid's net generation (`eia930_all_generation`, `net_generation_mw`, keyed
`series|eia930_all_generation|eia930:<BA>|net_generation_mw|<hour>` as the Gravity tab keys it), its demand (the
panel's own demand figure, `eia930_all_demand` `demand_mw` or the hourly snapshot's, `demandAt`), the net export over
its reporting ties (`net|export|<BA>|<hour>`, negative a net import) and **the gap**, net generation less demand less
net export, keyed `calc|bal|<G>|<D>|<X>` (the three keys with "~" for "|"): a new op of session 44's calc,
recomputed by check-values from its three operands (the arithmetic in `site/scripts/check-calc.mjs`). Over the
snapshot's week: **the mean size of the gap**, the mean of its absolute value (session 360's measure in
`eia930_balance.md`), `netbal|absmean|<BA>|<from>|<to>`, and **the count of hours** it is taken over,
`netbal|hours|<BA>|<from>|<to>`, a new key kind: `from` and `to` are the snapshot's first and last hour, and an hour
counts when every tie of the grid that holds a flow in some hour of the window holds one in it, and both the net
generation and the demand (`eia930_all_demand`) are held. check-values recomputes it with the page's rule
(`netbalValue` in `site/lib/gridKeys.ts`) on the snapshots it reads for the `net|` keys (the hourly one in Storage,
then the committed one, each hour from the first that holds it) and the grid's rows of the two tables in the window;
no value where neither snapshot holds the window's first or last hour. The block's note says, in words and no figure,
where session 360 found the grid's gap (`BALANCE_WHERE`); the hover tip of the gap and of the week's figures names the
split in one line (`BALANCE_SPLIT`): CAISO's and MISO's ties sum to their own total interchange and the gap is that
total against net generation minus demand; SPP's total closes and its ties do not sum to it; PJM has both; ERCOT,
NYISO and ISO-NE close.

On the fixture of the test (`site/scripts/fixtures/grid_balance.json`: the committed snapshot built 2026-10-23 14:36
UTC, the week of 15 to 21 October, and the seven grids' rows of the two tables read from Supabase with the anon key at
2026-10-23 22:37 UTC), in the hour the panel shows (21 October, 23:00 UTC) and over the 144 hours that hold all three:

| Grid | Net generation | Demand | Net export | The gap, the hour | Mean size, the week | Of mean demand |
|---|---|---|---|---|---|---|
| CAISO | 24,241 | 29,340 | -2,081 | -3,018 | 2,705.76 | 10.0 percent |
| MISO | 68,240 | 76,710 | -9,723 | 1,253 | 1,598.32 | 2.3 percent |
| PJM | 94,215 | 93,776 | 672 | -233 | 544.07 | 0.6 percent |
| SPP | 35,354 | 34,680 | 821 | -147 | 192.49 | 0.6 percent |
| NYISO | 15,074 | 17,501 | -2,428 | 1 | 2.38 | 0.0 percent |
| ERCOT | 61,094 | 61,145 | -49 | -2 | 1.40 | 0.0 percent |
| ISO-NE | 14,662 | 14,120 | 542 | 0 | 0.00 | 0.0 percent |

MW. The order and the sizes are session 360's (its 840 hours: CAISO 9.6 percent, MISO 1.9; SPP's 978.1 MW then
carried two impossible hours). A page shows the week its snapshot holds, so its figures move with the hourly refresh;
these are the fixture's.

**California.** CAISO's net generation in the block is EIA-930's total, the figure the gravity shape already draws for
CAISO (ruling 1a above: one source for every grid). The session 118 ruling withholds California's hourly mix by fuel
(`generation_mix_hourly.md`), not this total, so the block draws it, and its note says that since December 2025 it
reads below CAISO's own (`eia930_caiso_break.md`): most of CAISO's gap is that shortfall.

Decisions (chain 078):

- **The gap is net generation less demand less net export**, signed: negative where generation reads short of demand
  and exports (CAISO), positive where it reads over (MISO). Session 360's tests are written the other way (ties less
  net generation minus demand); the mean size is the same either way.
- **The week's figure is the mean absolute gap**, as session 360 measured it, not the signed mean: a gap that changes
  sign through the day would read near zero signed.
- **An hour of the week needs every tie of the grid**, not only the ties reporting in it: a partial sum of ties would
  read as a gap. The hour shown keeps the panel's own net export over its reporting ties (the hour the network opens
  on is complete for every pair still reporting), so no figure that stands moves.
- **The demand of the hour is the panel's demand figure**, keyed as it already was; the week's demand is
  `eia930_all_demand` alone (no fallback to the hourly snapshot's), so check-values reads one table.
- **A new op `bal` of calc, three operands**, rather than a nested calc (a nested key cannot be told apart once its
  "|" are "~"). The arithmetic moved to `site/scripts/check-calc.mjs` with its test; ratio, diff and pct compute as
  before. check-methods reads a calc key as the figures of all its operands (two, as before, or three).
- **No figure in the block's words**: where each gap sits is said in words; the figures are the keyed ones.
- **The test's fixture is self-contained** (`site/scripts/fixtures/grid_balance.json`: the snapshot's hours, the seven
  grids' links and the two tables' rows), since `site/data/grid_network.json` is rewritten each day.

### The Exchange blocks under the gravity shape (session 1167)

Session 1167: in "Each neighbour, that hour" (`components/grid/ExchangeView.tsx`, on the Gravity tab under the shape)
each neighbour's flow in the hour shown keeps its key (`net|tie|<BA>|<other>|<hour>`) and now answers a hover with its
tie, its hour and the snapshot's refresh, and the same tie over the snapshot's week in words; beside it, four keyed
columns of that week: the mean flow (whole MW), the lowest, the highest and the hours that hold a flow, signed from the
grid's side, keyed `nettie|<mean|min|max|hours>|<BA>|<other>|<from>|<to>` (`from` and `to` the snapshot's first and
last hour), a new key kind: check-values recomputes it with the page's rule (`nettieValue` in `site/lib/gridKeys.ts`,
the window by `windowOf`) on the snapshots it reads for the `net|` keys, the hourly one in Storage first, then the
committed one, each hour from the first that holds it. The direction is said in words, "<grid> sends to <code>" above
zero and "<grid> takes from <code>" below (it was "out" and "in"); the twelve months' table gains the same words (its
positive number is a net import, so "takes from", "net"). The hour's age against the snapshot's refresh is said once
in each branch of the block, the Lower 48's and a grid's, keyed `net|lag|<hour>|<refresh>` as under the network, and
not in any row. On the committed snapshot (refreshed 2026-10-23 14:36 UTC, the hour shown 21 October 23:00 UTC, 40
hours before it): ERCOT takes 51 MW from SPP in the hour, a mean of -96 MW over 144 hours, from -804 to 722 MW.

The same session, the standing rule (`site/lib/license.ts`: no held grid's rows are drawn): the replay's and the
stories' files (`public/network/daily_<year>.json`, `story_<event>.json`) hold ISO-NE's, MISO's and NYISO's hub
prices from `iso_hub_prices_history`, held by grid since 21 October 2026, and the Prices switch drew them. Each view's
price now leaves a held grid out (`shownPrice` in `app/network/Network.tsx`, the rule in `site/lib/gridHeld.ts`): no
ring, and the panel reads "license needed" with the publishers on hover (MISO keeps "paused while terms are reviewed"
in version 3). The live week's prices were already refused by the read. `iso_hub_prices_history` joins the Network and
Gravity tabs' list of tables read (`site/lib/gridtables.ts`), so their license line names it.

Decisions (session 1167):

- **The week's figures are written in the table, each with its key, and in words in the hour's hover line**: a figure
  only in a hover could not be keyed, and "keys for every figure" asks that each one shown be checked.
- **A new kind, `nettie|`, not a `netbal|` window**: the balance's window is the grid's, the tie's is one pair; its
  recomputation and its test (`site/scripts/test-grid-exchange.mjs`) came with it.
- **The mean is rounded to whole MW in the rule itself**, so the key's value, the page's raw value and the text agree;
  the lowest and highest are the flows as the snapshot holds them.
- **The week is every hour of the snapshot that holds a flow on the tie**, not only hours with every tie: a tie's own
  figures need only its own hours.
- **The age is said once in the Exchange block** even though the network above it on the Gravity tab says it for its
  own read: each block reads the snapshot on its own (the Exchange block on every request), so each says the hour it
  shows. Whether the tab should say it once only is put to the owner.
- **The replay's price is filtered on its way, `priceOf` left as it is**: `tests/test_session124.py` pins `priceOf`, so
  each view's own price goes through `shownPrice` before the ring and the panel.
- **`check-network-v3.mjs` counts the rings without the held grids**: its floor of five rings on a 2025 day becomes five
  less the held grids not already paused (three today, read from `site/data/license_status.json`), and a new check
  says no held grid has a ring.

### Revisions, said and checked (session 1171)

Session 1171, the Grid pack's blind spot 9 (`docs/reviews/packs/grid.md`, section 6): EIA calls EIA-930's hourly data
preliminary and revises an hour after it first publishes it; on 13 October 2026 one revised hour moved two of MISO's
figures between a page's read and the value checker's, and the run failed on them as if they were wrong.

**Said.** Each tab's data line (the grey source line at its foot) carries one sentence, the same words on the four tabs,
held in one constant (`EIA930_PRELIMINARY`, `site/lib/gridPreliminary.ts`, drawn by `components/grid/Preliminary.tsx`):
"EIA-930's hourly figures are preliminary and EIA revises them: a figure here is the value the warehouse held when this
page was drawn, so a later read of the same hour can differ." The Network and Gravity tabs, which already say under the
network how many hours before "this page was drawn" the newest hour began, write the same clock after "drawn"
("(2026-10-24 09:15 UTC)"); the Mix tab (the Now blocks' source line) and the Clean tab do not write a clock, so their
sentence has none. The Clean tab had no source line; it now has one, naming the tables the tab reads (the list of
`site/lib/gridtables.ts`, which its license line already shows). Every tab carries the drawing time on the sentence's
element as `data-eia930-drawn` (an ISO timestamp), for the checker. On the Gravity tab the sentence is in the network's
source line only, not again in the Exchange blocks' line under it.

**Checked.** The live set's `series` rows carry `loaded_at`, the load run that last wrote the row
(`warehouse/supabase/load.py` writes only the rows that are new or changed, session 11), and the anon key reads it. So
check-values (`site/scripts/check-values.mjs`, the rule in `site/scripts/check-revised.mjs`) tells a revision from an
error: for a key `series|eia930_<table>|<entity>|<variable>|<hour>` whose value on the page differs from Supabase's, it
reads the row's `loaded_at` and `freq`. When the page's text is its own value as the page writes it, the row is hourly
(`PT1H`) and it was written after the page's drawing time (the latest `data-eia930-drawn` on the page), the line is
`revised`, on its own line and in the summary ("N EIA-930 hours revised after the page was drawn"), and it passes only
for a table named on the line below. A row written at or before the drawing time is the row the page read, so its
difference fails as before, and the line adds "the row was last written ..., before the page was drawn ...: not a
revision". Every other difference fails as before: a page without `data-eia930-drawn`, a key of any other kind (a sum,
a maximum, a `calc|`, a snapshot's `net|` or `netbal|`), a table not named below, a text that is not the page's own
value.

Revised hours tolerated by check-values: `eia930_all_demand`, `eia930_all_generation`.

(check-values reads that line, word for word; a table taken off it makes its revised hours fail again, and a line
removed makes every one fail. `site/scripts/test-check-revised.mjs` reads it from this file.)

Decisions (session 1171):

- **The load time, not the retrieval time.** `retrieved_at` is when the data machine pulled EIA's file; a pull that
  brings the same value does not rewrite the row, but a revised value does, stamped with that load's `loaded_at`. A row
  is rewritten too when another of its columns changes (its `retrieved_at`), so a later `loaded_at` says the row may have
  moved, not that it did; the rule is asked only of a figure whose value already differs.
- **The drawing time is the page's clock, not its build's.** A Grid page is drawn on a request and cached up to an hour;
  its reads are made in the same drawing, or come from the site's fetch cache, which is older. A row loaded between a
  cached read and the drawing fails (the rule leans to a failure, never to a pass). The latest of the page's
  `data-eia930-drawn` is taken.
- **Two tables, the ones the Grid tabs key by the hour**: `eia930_all_demand` and `eia930_all_generation` (the Now
  blocks, the Network and Gravity panels, the hourly mix). Another EIA-930 table's revised hour fails, its line saying
  the note does not tolerate it, until its name is added here.
- **One row's key only.** A figure over many hours (`series_sum|`, `series_max|`, `netbal|`) moves when one of its hours
  is revised too, but telling which hour moved needs every row's load time; left failing, as before.
- **Counted apart**: a revised line counts among the values read, not among those that match, as the latest prices'
  "superseded" lines do; check-methods (`keysFromValues`) reads a revised line's key as it reads ok and FAIL lines.

### Every old address, tested (session 1172)

The rule and its test are in "One page, four tabs, and the Ask panel" above (`site/scripts/test-grid-addresses.mjs`, 8
tests over 61 addresses). Every case passed as the code stood, so `site/lib/gridtool.ts` and `site/next.config.ts` did
not change; the route check (`site/scripts/check-routes.mjs`, the block "session 1172") lists 15 more old addresses.

Decisions (session 1172):

- **The redirects are modelled, not served**: the test applies `next.config.ts`'s own list with Next 16's merge rule,
  read from Next's source; four requests to production, not followed, gave the same destinations. A rule to `/grid`
  with a pattern in its source (`:path*`) would fail the test's first case; there is none today.
- **`/ask`'s redirect is modelled from its two lines**, pinned by the test as `tests/test_session299.py` pins them; the
  page is chain 075's and was not changed.
- **The route check lists 46 of the 61 cases**, one for each rule and word: each is a full render in both passes, and a
  second address of the same rule asks nothing new of the server.
- **`node=BPAT` with no grid opens the Lower 48 with `named` false** (`grid=BPAT` gives true); no page or component
  reads `named`, so the test does not pin it.

## The 3D scene's code, loaded when it is drawn (sessions 428 and 1175)

The Network shape's 3D scene is drawn by 3d-force-graph on three.js, the largest code the Grid page can load (about
841 KB as session 428 measured its chunk). It is fetched by two `import()` calls in the network component's own effect
(`site/app/network/Network.tsx`), which returns before them unless the shape shown is the network (session 180), the
browser draws WebGL, and the frame is on screen or within 200 px of it (session 428). So the Mix tab, where `/grid`
opens, never fetches it; the Gravity tab and the Map shape never fetch it; the Network tab fetches it on a phone only as
the reader scrolls to the frame. No other module of the page imports either library or a package built on them:
`site/scripts/test-network-split.mjs` walks the page's import graph with the site's own TypeScript parser and fails on
any static import of them.

Session 1175 (24 October 2026): while the chunk is on its way, the frame (the same box, `min(72vh, 620px)` high and at
least 420 px) says "Loading the 3D network." over its middle. The line is the box's sibling, not its child, because the
library empties the box when it draws; it goes once the scene is built, and comes back if the reader leaves the shape
and returns. What the scene draws, its fixed positions, its hint line and the "This browser cannot draw 3D" fallback
are as they were.

Decisions (session 1175):

- **The libraries were already split; the scene's own code stays in the component.** Moving the scene into a module of
  its own would take a few kilobytes off the component, against the older tests that pin the scene's code where it is
  (sessions 93, 237, 241c, 428); the libraries, the weight, were split in session 428.
- **A line, not a drawing, while it loads**: no fake sphere or grey shape stands in for the network.
- **The proof is a source scan with the TypeScript parser**, not regular expressions: a comment or a string holding
  "three" is not read as an import, and a type-only import, which the compiler erases, is left out.
- **The scan covers every module the page and the root layout reach**, whichever tab draws them, so the claim holds as
  tabs change.
- **The line is drawn on the server too** (the scene never is), so the served HTML of each Network tab carries it: an
  expected difference at the landing.
- **A chunk that fails to download still shows "This browser cannot draw 3D"** (the fallback, kept as it was); a
  sentence for that case is put to the owner.

## The storage units and the snapshot, read once (chain 091, 24 October 2026)

Chain 091 in this note (sessions 1178 to 1189): session 1180. The note's other chain 091 sections: 1181 ("When a read fails"), 1182 ("Each panel's table, to download"), 1183 ("Every panel in the address"), 1184 ("The method from each panel"), 1186 ("The Grid pages under check-values, lighter") and 1187 ("The stored answers, refreshed", written by session 1188 from its report). Elsewhere: 1179's one read of a grid's generation in `generation_mix_hourly.md`; 1185's Lower 48 by month in `generation_mix.md`; each panel's failed read, file, anchor and method link in its own note's chain 091 section (`generation_mix_hourly.md`, `grid_network_v3.md`, `grid_stress.md`, `scarcity_hours_by_grid.md`, `california_reliability.md`, `ercot_grid_notices.md`, `eia930_balance.md`, added by session 1188). Session 1178 wrote the next queue file only; session 1188 wrote these index lines and the rulings list.

Session 1180. Two reads session 1160 left as they were. **The battery units**: the Mix and Clean tabs of each ISO grid read `storage_capacity` whole (`site/lib/data.ts` `storageUnits`: 1,627 units, two requests, seven columns) and kept the units whose ISO is the grid's (`site/lib/grid.ts` `load`), for the Batteries block of the Mix tab (`components/grid/YourGrid.tsx`: MW by status and the operating MWh, keyed `storage|iso_mw|<ISO>|<status>` and `storage|iso_mwh|<ISO>|operating`). Now `load` asks for the grid's units only and for the three columns drawn (`site/lib/gridReads.ts` `gridStorageUnits(iso)`: `extra->>iso=eq.<ISO>`, `capacity_mw`, `status`, the MWh), in the whole read's order (`entity_id`), so each sum adds the same numbers in the same order. `storageUnits` is unchanged for the pages that draw the whole fleet (`/storage`, the home page, the battery game). **The network snapshot on the Gravity tab**: the network component (`components/grid/NetworkView.tsx`, with its panel `grid_gravity_<grid>`) read the hourly snapshot with a one-hour revalidation and the Exchange blocks under it (`components/grid/ExchangeView.tsx`) read it again, fresh. Now the render reads it once, fresh (`freshSnapshot`, React's `cache` over `fetchHourly(0)`), and both draw that one object. The Network tab keeps its one hourly read; the Now view its own fresh one.

On the live set, 24 October 2026, 02:19 and 02:21 UTC (`site/scripts/time-grid-reads.mjs`, one request at a time, 22 addresses: the Mix and Clean tabs of the seven ISO grids and the Gravity tab of all eight): each Mix and Clean tab one request fewer for the units (2 to 1) and 1,221 to 1,597 fewer rows (1,627 to the grid's own: ERCOT 406, CAISO 405, ISO-NE 181, NYISO 90, PJM 71, MISO 66, SPP 30); each Gravity tab asks for the snapshot once, not twice (one distinct request either way, since both asked for the same object). Across the 22: 674 requests to 660, 419,636 rows to 399,356, 796 asks to 774, and the sum of the medians 44,612 ms to 42,159 ms. The figures: the 22 addresses, the Network tab of ERCOT and of the Lower 48 and `/grid`, drawn by the code before and after on the same answers (`site/scripts/same-figures.mjs`: a proxy on this machine keeps every answer in memory, each distinct request sent once; the seven narrowed reads are the tree after's own): 2,569 figures, every key, value and text the same, the 28 battery figures among them.

Decisions (chain 091):

- **Session 1160's reason for the two reads holds for the fresh one, not for the second read.** The Exchange blocks read the snapshot fresh since session 237 so that a number shown is the object's own (check-values reads it fresh; an hourly refresh between the page's cached read and the check revised four of PJM's ties). That read is kept. It needs no older read beside it: on the Gravity tab the network component and its panel now draw the same fresh object, so the tab's figures can no longer come from two versions of the snapshot. The Network tab's hourly read is unchanged (one read, its own).
- **The share is a `cache` of the fresh read, not a choice inside `fetchHourly`**: `lib/network.ts` keeps no imports beyond types (a test loads it in Node), and its other callers (the Now view, problem set E, the retired page) read as before. The network component takes the shared read when its shape is the Gravity tab's (`shape="gravity"`, which only that tab passes); the pinned call `pickSnapshot(await fetchHourly(HOURLY), committed)` stands for every other tab.
- **The units are filtered by PostgREST, not by an index**: `extra->>iso` has none, but the filter runs over the 1,627 rows of `table_name=eq.storage_capacity`, which the primary key finds; session 1160 left the read for want of an index, and none is needed for a table this size.
- **The Clean tab still reads the grid's units**, which it does not draw (the Batteries block is the Mix tab's): `load` is shared by the two tabs and knows no tab; one small request, left.
- **The proof's tool is kept** (`site/scripts/same-figures.mjs`, session 1179's one-off made a script): two trees, one set of answers, every figure compared; its walk and comparison are tested in `site/scripts/test-grid-units.mjs` with the narrowed read on a committed fixture of real rows (`site/scripts/fixtures/grid_units.json`) and the snapshot read once a render.

## When a read fails (chain 091, 24 October 2026)

Chain 091 in this note: session 1181.

Session 1181. Every panel chains 077 and 078 added to the Grid tool (`grid_network_`, the balance, `grid_gravity_`, `grid_clean24_`, `grid_mix_`, `grid_scarcity_`, `grid_caisoalert_`, `grid_ercotnotice_`, `grid_ask_`, the replayed day, the sentence on preliminary figures, the held lines, the stress and committed-file views) was drawn with one read failing at a time, on the live answers held in memory (a one-off walk of the page through `site/scripts/tsx-loader.mjs`, as `time-grid-reads.mjs` walks it: the 36 addresses with each table they read answered by an HTTP 500, 346 renders; 20 addresses with each table answered by a statement timeout past the retries and by an empty answer, 408 renders; no component threw in any). Six places drew a wrong statement where a read had failed, and two dropped a panel or drew a count from nothing; each now says the read could not be read, in the tool's one look (`Missing`, the words "could not be read", the table and the reason on hover), and draws no figure of it:

- the balance (`data-grid-balance`): net generation "not held", the gap "a part is not held" and "No hour of the week holds all three" when `eia930_all_generation` or `eia930_all_demand` could not be read; now "could not be read", "a part could not be read", "The week's gap is not computed: its hours could not be read". The hour's demand stays the snapshot's own (the hourly refresh read it), as before;
- the gravity panel: each grid's net generation "not held" and the Lower 48's "not held for the hour"; now "could not be read", the share "not computed";
- the energy mix panel (`grid_mix_`): "Demand is not held for these hours" when the demand could not be read, and an empty panel when the generation could not be read; now "Peak demand: could not be read" and "The hourly mix: working on it" (the view's own words for a failed read), in the panel;
- the scarcity strip: "No 15-minute price of these days is in the live set" and, on every cell's hover, "No price of this hour is in the live set" when `iso_rtm_hub_prices` could not be read, and nothing at all for ERCOT's daily price; now each says it could not be read (`lib/scarcityStrip.ts` takes the failed reads, its words for an empty answer unchanged);
- the last 24 hours' keyed table (`grid_clean24_`): on a failed or empty read the panel was not drawn and its name was gone from the page; the section's "no data" now stands under the panel's name;
- the two whole-table notice reads (`caiso_grid_emergencies`, `ercot_grid_notices`, every row of each): an empty answer drew "holds no notice", "0 days" of restricted maintenance or of notices that are not calls, and "no month of the chart is marked" as facts; a table that holds every notice since 1998 (2011 for ERCOT) answering none is a failed read, so every reader of the render says it could not be read (`site/lib/gridReads.ts` `wholeRead` over CAISO's read, which `lib/reliability.ts` keeps as session 1160 left it for the scorecard and the heat event page; `wholeTable` inside `lib/gridErcotNotices.ts`), and the page is marked for a short revalidation as any failed read is (session 537); CAISO's Reliability section said "The table holds 0 notices, the latest on no day" on a failed read and now says the notices could not be read;
- the replayed day on the Gravity tab: the demand "not held" when the year's committed file could not be read on the server; now "could not be read" (the Network tab's block already said so);
- ERCOT's interconnection queue ("What is being built", where the held lines of session 1167 stand): "Not in the warehouse yet: ... in the live set" when `energy_projects` could not be read; now "could not be read".

The panels that read no database (the stored examples under Ask, the stress view and the views of committed files, the held queue line) draw the same with every read failing; the snapshot's Storage object failing draws the committed snapshot, which the source line names ("the daily snapshot: the hourly copy was not reachable"), as since session 55. `site/scripts/test-grid-failed-reads.mjs` holds a case a panel and a failure kind (55 cases) on committed real rows (`site/scripts/fixtures/grid_failed_reads.json`, read once with the anon key, with the fixtures of sessions 1154, 1155, 1165 and 1174); on the code before this session 27 of them fail.

Decisions (chain 091, session 1181):

- **No read of the Grid page is `required()`.** `/grid` is drawn on demand (ƒ in the last landing's build, `runs/land_check/d3b4c998b5f0930331627bb23c4471577e29b4b6/build.out` on the old laptop): no page of it is cached, and Next keeps a read's answer in its data cache only when it is a 200, so a timeout or an HTTP error is asked again by the next visitor and cannot be baked into the page. A required read would throw the visitor an error page, and a page drawn on demand has no last good page to keep; no method note says a panel must not be drawn without its read. `required()` stays the rule for the prerendered pages (the home page, session 90); the one Grid page that is prerendered, `/grid/caiso/alerts` (an hour), keeps `attempt()` with session 537's mark of a minute.
- **What an hourly cache could keep is an empty answer**, a 200, kept for its revalidation. The reads where an empty answer would have drawn a wrong statement are the two whole-table notice reads ("no alert", "0 days"): made failed reads, said "could not be read", not `required()` (the page is drawn on demand). Every other read of the panels is of a window, where an empty answer is what the table holds for it and its words say so ("not held", "has no row in the last 7 days", "holds no hour of ERCOT", "No 15-minute price of these days is in the live set"): left as they are.
- **The words**: "could not be read" in `Missing`, the tool's one look for what is not there (session 1159), with the table and the reason on hover; never "not held", which says the warehouse holds no such figure. The words a panel already had for a failed read stay (`NoData`'s "no data for", "could not be read just now", the mix view's "working on it").
- **CAISO's whole read is guarded at its Grid readers** (`site/lib/gridReads.ts` `wholeRead` over `attempt(() => gridNotices())`, with `CAISO_HOLDS`), not inside `lib/reliability.ts`: the bounded reads of the Flex Alert scorecard and the heat event page must still say "no notice in the window" for an empty window, and sessions 1155, 1160 and 1174 pin those lines word for word. ERCOT's guard is inside `ercotNotices()` (`wholeTable`), its only readers being the Grid tool's. (Written by session 1188 from session 1181's report.)
- **The blocks older than chain 077 that say "not held" or nothing on a failed read** (the grid's own blocks of `components/grid/YourGrid.tsx`: carbon, storage cycles, the Batteries block, the price board, the weather; the table citations' catalogue; CAISO's daily reliability series) are listed in the session's report, not changed: they are not this chain's panels, and their failed reads are named at the foot of the grid's blocks ("Reads that failed").

## Each panel's table, to download (chain 091, 24 October 2026)

Chain 091 in this note: session 1182.

Session 1182. Each panel chains 077 and 078 added to the Grid tool offers its table as a file, as the older blocks offer
theirs: under the table, "Download this table (CSV)". The file is made on the server from the cells the panel draws
(`site/components/grid/PanelFile.tsx`), as the hub table's and the node list's downloads are made from the page's own
figures (`app/cost-of-power/AllGridsDownload.tsx`, session 793): no new route and no read, so the file holds what the
page draws when it is drawn. It is written into the link itself, a `data:text/csv` address with the `download`
attribute, so it needs no script and a checker reads it from the page's HTML. The files, by panel (`erw_<id>.csv`):

| Panel | File id | Rows | In the header beside the table |
|---|---|---|---|
| The network ties (Network tab) | `grid_network_<grid>` | each reporting tie: the neighbour, its flow, its direction; the Lower 48: the seven grids' net export and ties | the net export or import, the ties, the demand in the hour |
| The balance | `grid_network_<grid>_balance` | net generation, demand, net export, the gap | the week's hours and the gap's mean size |
| The replayed day (Network tab) | `grid_replay_<BA>` | the day's demand, net exchange, ties | |
| The gravity table | `grid_gravity_<grid>` | each of the seven grids: net generation, net import, the import's share | the Lower 48's generation; the replayed day's demand when the address names a day |
| The Exchange blocks | `grid_exchange_<grid>_ties`, `grid_exchange_<grid>_twelve_months`; the Lower 48: `grid_exchange_us48` | each tie in the hour and over the week; each neighbour over twelve months | the net, the ties, the largest flow, the hour's age; the twelve months' share, MWh and days held |
| The last 24 hours (Clean tab) | `grid_clean24_<grid>` | each ISO's latest, lowest and highest intensity, each with its hour | |
| The energy mix panel | `grid_mix_<grid>_hourly`, `grid_mix_<grid>_monthly` | each fuel's MWh and share | the 24 hours' total, the peak demand, the newest hour; the month's days, the alert or notice days |
| The scarcity counts | `grid_scarcity_<grid>` | each count of the strip, its hours held, its table | |
| CAISO's and ERCOT's notice lines | `grid_caisoalert_caiso`, `grid_ercotnotice_ercot` | each day and count of the lines, with its notices | |
| The stress tables | `grid_stress_<grid>_ramp`, `_tight_<year>`, `_calm`, `grid_stress_all_<year>` | each year, or each fuel, as the table | |

Each file opens with its provenance (CLAUDE.md, non-negotiable 5), one `#` line each: the panel and the page's
address, the tables (each with its source, and for the snapshot its build time), the filter, the hour or the window,
and the time the page was drawn; then the figures that stand beside the table in the panel's sentences, one line each
with its value and its check key; then the columns and the rows. A cell that holds a figure is the figure's value as
read (its `data-raw`), before the page rounds it; a figure of a held grid is written "license needed", never its value
(`components/Num.tsx` `heldBy`, the rule `lib/gridHeld.ts` and `lib/license.ts` keep); a cell the page writes in words
("not held", "could not be read", "no tie reported") is written in those words.

`site/scripts/test-grid-files.mjs` draws the pages on committed real rows (session 1181's stand-in, with
`site/scripts/fixtures/grid_files.json`: ERCOT's `ba_supply_monthly` and CAISO's monthly mix, read once with the anon
key) and holds, block by block, the figures of its files (key and value) to the figures the block draws, no more and no
fewer: 53 cases. `site/scripts/check-table-downloads.mjs` (by default on `site/scripts/grid-files.mjs`
`GRID_FILE_PAGES`; `CHECK_GRID_FILES`) checks that each page offers every panel's file and that each opens with its
provenance; `site/scripts/check-download.mjs --grid` reads each file whole: its rows as its link states, each with its
columns, and every number past the first column a figure of the page. `site/scripts/same-figures.mjs` on 20 addresses:
2,878 figures, every one the same before and after.

Decisions (session 1182):

- **The file is made from the cells the panel draws, not from a second read.** A route would read again, minutes or an
  hourly refresh later, and its figures could differ from the page's; the cells are read without drawing them
  (`cellOf`: a figure is a `Num`, a held figure its words, the rest its text), so the table and the file cannot say two
  things. Where a panel built its rows inline, the rows are now one constant handed to the table and to the file; the
  pinned lines of sessions 1165 and 1181 stand word for word.
- **A data: link, not a button that builds a file in the browser** (session 793's way): it works without script, and
  the two check scripts and the node test read it from the HTML. The cost is the page's size: the largest file is a
  few kilobytes.
- **The sentence's figures go in the header, one line each with its key**, so the file holds every figure of the panel
  and the table keeps the panel's columns; a figure drawn twice on the page (the Exchange net, in the sentence and the
  headline) is written once.
- **The replayed day's file is `grid_replay_<BA>`**, not named for a grid: its block is drawn on the Network tab of
  whichever grid the address names (session 1170's call is pinned word for word, so the block is not told the grid).
- **No figure moved, and no panel's words**: the link is a line under each table; the figures, their keys and the
  panels' names are the same before and after on the same live answers.
- **The check scripts' default pages carry the files each must offer**, so a panel that loses its file fails the check;
  a page whose read fails at the landing shows as a missing file, said, not hidden.
- **`check-download.mjs --grid` reads no database and makes no download**: it reads the files from the served pages'
  HTML, so it stays outside `/api/download`'s sixty requests an hour. (Written by session 1188 from session 1182's
  report.)
- **The link's words**, "Download this table (CSV), its source, filter and hour in the file's first lines.", are the
  same under every table; another wording is put to the owner (`docs/reviews/grid-rulings-2026-10-23.md`).

## Every panel in the address (chain 091, 24 October 2026)

Chain 091 in this note: session 1183.

Session 1183. Each panel chains 077, 078 and 091 added to the Grid tool has an anchor, an `id` on the page, so a reader's view can be shared as an address: the tab, the grid and the panel's own state in the query, the panel after the `#`. The anchors are one list, `site/lib/gridAnchors.ts` (`GRID_ANCHOR`, `PANEL_ANCHORS`), read by the components that draw the panels, by the two node tests and by the route check. An anchor is the same on every grid where the panel is the same (the grid is in the query, not in the anchor); where one page draws the same panel for several grids, the first takes the anchor and each next one the anchor and its grid (`anchorOf`: `mix-panel`, `mix-panel-miso`), as the Mix view's older sections do (`today`, `today-<ba>`).

| Panel | Anchor | An address that opens it, with its state | The state it carries |
|---|---|---|---|
| The network's figures, the hour shown (`grid_network_<grid>`) | `#network-figures` | `/grid?grid=ercot&view=network&net=day&t=2021-02-15&node=BPAT` | `net`, `t`, `node` (the network component's own words, through `netToPage`) |
| The replayed day (`grid_replay_<BA>`, inside the network's panel) | `#replayed-day` | `/grid?grid=ercot&view=network&net=day&t=2021-02-15&node=ERCO` | `net=day`, `t`, `node` |
| The balance (`data-grid-balance`) | `#balance` | `/grid?grid=ercot&view=network` | the grid |
| The gravity table (`grid_gravity_<grid>`) | `#gravity-figures` | `/grid?grid=ercot&view=gravity&shape=gravity&net=day&t=2021-02-15` | `shape`, `net`, `t` |
| The Exchange blocks: the seven grids (Lower 48) | `#exchange-grids` | `/grid?grid=us48&view=gravity&shape=gravity` | `shape` |
| The Exchange blocks: the ties and the week | `#exchange-ties` | `/grid?grid=ercot&view=gravity&shape=gravity` | `shape` |
| The Exchange blocks: twelve months | `#exchange-months` | `/grid?grid=ercot&view=gravity&shape=gravity` | `shape` |
| The last 24 hours (`grid_clean24_<grid>`) | `#last-24-hours` | `/grid?grid=ercot&view=clean` | the grid |
| The energy mix panel (`grid_mix_<grid>`) | `#mix-panel` | `/grid?grid=ercot&mixp=month` | `mixp` (and `grids`, `ba`) |
| The scarcity strip (`grid_scarcity_<grid>`) | `#scarcity` | `/grid?grid=ercot` | the grid: the strip is the grid's in the address |
| CAISO's alerts (`grid_caisoalert_caiso`) | `#caiso-alerts` | `/grid?grid=caiso` | the grid |
| ERCOT's notices (`grid_ercotnotice_ercot`) | `#ercot-notices` | `/grid?grid=ercot` | the grid |
| The stored answers under Ask (`grid_ask_<grid>`) | `#stored-answers` | `/grid?grid=ercot&ask=1&q=What+was+the+peak%3F` | `ask`, `q` (the question in the box, not sent) |
| The stress tables: ramp, tightest hours, calm stretches (`grid_stress_<grid>`) | `#stress-ramp`, `#stress-tight`, `#stress-calm` | `/grid?grid=ercot&mix=stress&year=2024` | `mix=stress`, `year`, `grids` |
| The stress tables: the seven grids (`grid_stress_all`) | `#stress-grids` | `/grid?grid=ercot&mix=stress&year=2024` | `mix=stress`, `year` |

Every panel's state was already in the address: each panel is drawn on the server from the page's query, and the network component writes its own words back through `netToPage` (session 1172's round trips). None keeps a state of its own in the browser. The energy mix panel's two views (its chips) now carry the panel's anchor (`#mix-panel`, or `#mix-panel-<grid>` for a grid after the first), where both carried `#hourly`, the first grid's section, on every grid. Three panels kept the anchor their section already had (`#scarcity`, `#caiso-alerts`, `#ercot-notices`), which links on the page point to.

`site/scripts/test-grid-addresses.mjs` (four tests more) holds, for each panel, that its address is the one the tool writes (`gridHref`), that it opens the panel's tab and grid without a redirect, and that each word of its state is read back as the panel reads it (the day and node by `gridPick`, `net` by the network component through `netFromPage`, `mixp` and `year` by the mix page's `choiceOf`, `ask` by the Ask panel); that no two panels share an anchor and no anchor is an id the page already draws; that the route check lists each address with its anchor; and that this note names each anchor. `site/scripts/test-grid-files.mjs` draws the pages on committed real rows and holds that each panel drawn carries its anchor (on the panel, on an element inside it, or on the element that holds it alone) and that no id is drawn twice on a page, a grid's second mix panel and stress tables included. `site/scripts/check-routes.mjs` asks each address of `GRID_ANCHORS` with the internal cookie at a landing and fails when the page does not draw the anchor's id.

**The files of session 1182, measured.** Each panel's CSV is written into its link as a `data:` address. Drawn outside Next on the same live answers (`site/scripts/same-figures.mjs --sizes`: each page's HTML and its flight payload, the two copies Next sends of what the server draws; a client component's own markup is not counted, the same before and after), on 40 addresses (`/grid`, each grid on each tab, the two monthly views, two stress views, three replayed days), the pages grew by 1.3 to 6.7 percent: the largest growth 33,510 bytes (`/grid?grid=ercot&mix=stress`, six files, 832,353 to 865,863 bytes, the largest page of the 40). The stress view with the seven grids, the heaviest address the tool writes, grew by 84,032 bytes, 6.5 percent (1,299,291 to 1,383,323 bytes, fifteen files). No page grew by more than 15 percent or 100 KB, so the files stay in the links. The site's Content-Security-Policy (`site/next.config.ts`, enforced since session 301) governs no download: its directives are fetch directives (scripts, styles, images, fonts, requests, workers, frames), with the four that cannot break a page; a link followed or downloaded is a navigation, which no directive of the policy covers (`default-src` stands in for fetch directives only, and `navigate-to` was never shipped by a browser). So a `data:` link with `download` is allowed, and no route is needed.

**The copy line.** `components/CopyLine.tsx` (session 1015) is drawn on `/data` only, under "Use the ERW in your tools"; no block of `/grid` has one, older or new, so none was added.

Decisions (session 1183):

- **The anchor is the panel's, not the grid's**: `#mix-panel` on every grid, so an address differs from another grid's only in its `grid`, and a link written for one grid works for the next. The grid goes into the anchor only where a page draws the same panel twice.
- **Where a session's test pins the panel's element word for word** (the energy mix panel, sessions 1152 and 1159; the last 24 hours, sessions 1159 and 1181), the anchor is on an element that holds the panel alone, not on the panel itself; the pinned lines stand. Elsewhere the `id` is on the panel's own element.
- **The three anchors that were there are kept** (`scarcity`, `caiso-alerts`, `ercot-notices`, on the panel's one section): the page links to them, and tests of sessions 1155, 1159 and 1174 pin them.
- **The mix panel's chips point at the panel**, not at the section `#hourly` above it: on a page of two grids the second grid's chips opened the first grid's section. The chips are links with `scroll={false}`: a click keeps the reader's place, and the anchor serves the address a reader copies or opens anew.
- **The files stay in the links** (measured above, under the brief's bound of 15 percent or 100 KB). `same-figures.mjs --sizes` is kept for the next panel that adds to a page.
- **No copy line**: the older blocks of `/grid` have none to follow, and the address with its anchor is what a reader shares from the browser's own bar; a "copy this view" control is a question for a ruling, not a placement to copy.

## The method from each panel (chain 091, 24 October 2026)

Chain 091 in this note: session 1184.

Session 1184. The older blocks of `/grid` end their source line with a link to their note ("Method", `/data/methods/grid_network`). Each panel chains 077, 078 and 091 added now links the section of its note that defines it: the chain 077 or 078 section, or the older section the panel follows. The links are kept beside the anchors in `site/lib/gridAnchors.ts`, one constant a panel (`METHOD_NETWORK`, `METHOD_BALANCE` and the rest), gathered by panel in `GRID_METHOD`, each `/data/methods/<note>#<id>` with the id the site's renderer writes for the heading (`site/lib/markdown.ts`, `headingSlugs`: the heading's text in lower case, without punctuation but the hyphen and the underscore, each space a hyphen).

| Panel | Its method |
|---|---|
| The network's figures, the gravity table, the last 24 hours, the stored answers | this note, "The Grid tool's panels, every figure keyed (chain 077, 23 October 2026)" |
| The balance | this note, "The balance, said where the figures are (chain 078, 24 October 2026)" |
| The Exchange blocks: the seven grids, the ties and the week | this note, "The Exchange blocks under the gravity shape (session 1167)" |
| The Exchange blocks: twelve months | this note, "Who supplies a grid (session 68)" |
| The replayed day | `grid_network_v3.md`, "The outside grids' demand in the replay (chain 078, 24 October 2026)" |
| The energy mix panel | `generation_mix_hourly.md`, "The Mix tab's energy mix, keyed, hourly and by month (chain 077, 23 October 2026)" |
| The scarcity strip | `scarcity_hours_by_grid.md`, "On the Grid tool (session 1154, 23 October 2026)" |
| CAISO's alerts | `california_reliability.md`, "On the Grid tool: the alert state (session 1155, 23 October 2026)" |
| ERCOT's notices | `ercot_grid_notices.md`, "6. On the Grid tool: the notice state (session 1174, 24 October 2026)" |
| The stress tables: the evening ramp, the seven grids | `grid_stress.md`, "The views' figures, keyed from the committed files (chain 078, 24 October 2026)" |
| The stress tables: the tightest hours, the calm stretches | `grid_stress.md`, "The large tables, keyed whole (session 1168)" |

Where the link stands: the scarcity strip and CAISO's alerts already ended their source line with a link to their note, and that link now opens the section (its words unchanged). ERCOT's notices keep the link to the whole note that session 1174 wrote and pinned, followed by one to the section. Every other panel gains one line at its foot, under its table and its download line, `"Method: <the section's words>."` (`site/components/grid/PanelMethod.tsx`, `data-grid-method="<panel>"`), inside the panel, so the line goes with the panel's anchor; the scarcity panel of the Lower 48 and of a grid without a strip draws that line too. Where a read fails, the replayed day (its year's file not read) and CAISO's and ERCOT's state lines say what could not be read as before, without a link; every other panel keeps its line. Each link is a `SiteLink`, so a visitor sees it as the other method links of the page while `/data/methods` is in review.

**The checks.** `site/scripts/check-methods.mjs` reads a page's notes from the links its code writes; a constant that holds a note's address counts (session 409's rule), so each `href={METHOD_<PANEL>}` is a note of `/grid` with no change to the script: `/grid`'s notes gain `grid_network_v3` and `grid_stress`, and its 553 figures stay named. `site/scripts/check-links.mjs` already held each fragment against the ids of the served page it names, the method pages among the pages it reads in the internal view (session 581), so it needed no change. `site/scripts/test-grid-methods.mjs` (new) renders each committed note with `lib/markdown.ts`'s own `render` and holds, for each panel, that its fragment is an id of the note under the heading named in the table above, judged by check-links' own `internalTarget`, `anchorOk` and `judge` (an id one letter off is a finding); that the section says what the panel draws; that the link is written in its component as a `Link` to its `METHOD_<PANEL>` whose words say "Method", and check-methods reads every one of these notes for `/grid`; and that every other `/data/methods/<note>#<id>` the Grid tool's code writes (`STRESS_METHOD`) resolves too. `site/scripts/test-grid-files.mjs` draws the pages on committed real rows and holds that each panel drawn carries its link.

Decisions (session 1184):

- **The section that defines the panel, not the note's top**: a reader who asks how a figure is made lands on the rule for that panel. Where a panel has no section of its own (the network's figures, the gravity table, the last 24 hours and the stored answers are bullets and a paragraph of the chain 077 section), the link opens that section.
- **The Exchange blocks' twelve months open "Who supplies a grid"**, the section that defines `ba_supply_monthly`'s measures and its held days, not session 1167's, which changed only the table's words.
- **One constant a panel in the components, not the list**: `scripts/page_tables.py` reads the constants a component imports, and the list names two notes named like tables (`ercot_grid_notices`, `scarcity_hours_by_grid`); imported whole by the network's panels, it read as reads of those tables on the Network tab (`tests/test_session502.py`). A panel imports only its own.
- **A heading's id is computed by the renderer in the test, never written by hand**: the ids in `site/lib/gridAnchors.ts` were printed by `render` and are held to it; a heading renamed in a note fails the test by name, and the link is changed with it.
- **A pinned link is kept and a second one added** (ERCOT's notices): session 1174's test holds the words and the address of the link to the whole note; this session extends, it does not move it.
- **No link in a failed read's words** (the replayed day's, CAISO's and ERCOT's): those lines say only what could not be read, as session 1181 set them.

## The Grid pages under check-values, lighter (chain 091, 24 October 2026)

Chain 091 in this note: session 1186.

Session 1186. `site/scripts/check-values.mjs` reads 48 addresses of the Grid tool (`/grid` and its tabs, and the old addresses that redirect into it: `/emissions`, `/mix`, `/network`, the seven `/grid/<iso>`, with `/grid/caiso/alerts`). Without a server it cannot read them, so `site/scripts/check-values-cost.mjs` measures it another way: each address is drawn outside Next as `site/scripts/same-figures.mjs` draws it (41 distinct pages, every keyed span of the server's HTML), a local site serves that HTML at check-values' own addresses, and a proxy on this machine stands where `SUPABASE_URL` points, sends each distinct request to Supabase once and keeps the answers in memory. check-values is then run as it is against the two, every address in one run (as a landing reads them), each address in a run of its own (`CHECK_VALUES_PAGES`), a run a key kind, and a run with every page value moved; every request is counted against the page check-values was reading. The old script and the new one ran on the same answers.

Where a key's recomputation read more than the page did for the same figure:

| Kind | What check-values read | Now |
|---|---|---|
| `net\|`, `nettie\|`, `netbal\|`, `netsnap\|` | the network snapshot in Storage (about 2 MB) once a key: CAISO's Exchange tab 88 requests, 14.1 MB, where the page reads it once | once a page (the next page reads it afresh); the committed snapshot parsed once a run |
| `calc\|`, `fmt\|` | a key's operands or inner key again for each key that names them: on the Mix tab each fuel's share read the day's whole net generation again | each key's value kept for the run, as the keys a page carries already were |
| `fcerr\|`, `degday\|`, `netbal\|` | the same two series for each of a pair of keys (`mape` and `hours`, `cdd` and `hdd`, `absmean` and `hours`) | read once a run |
| `gridq\|` | the grid's whole queue in `energy_projects` for each key: 27 keys on ERCOT's Mix tab, 2,000 rows each time | the queue once a run |
| `awe\|days` | `caiso_grid_emergencies` once a key | the table's rows the `awe\|last` and `awe\|ndays` keys already read once a run, the type and the year kept as the query kept them |
| `series\|`, `series_sum\|`, `series_max\|` | one request a key, where the page read the hour or the window once: the Flex Alert scorecard's 395 single-row reads | a page's keys of one table, entity and hour (`series\|`), or of one table, window and entity (the sums and maxima, a `calc\|` key's operands among them), read together, one request a group |

A key's value is taken from its group's answer only where that answer holds what the key's own query would have: a `series|` key's variable in no row or in one row (a variable held twice at the hour sends its own query, which takes the first row as before), a group's answer under PostgREST's page of 1,000 rows, and the sums of a window read through every page of the group. When the group's read fails, each key sends its own query, as before. A failed read is never kept: the next key that names it reads again.

On the live answers of 24 October 2026 (05:02 to 05:08 UTC, the pages drawn at 05:02; 1,729 distinct requests sent to Supabase through the one proxy kept open for the session, each once):

- **Every address in one run**: 1,865 requests to 467, 203,367 rows to 108,608, 66.7 MB to 9.5 MB, about 153 s of Supabase's answers to 34 s (each request counted at the time its first answer took). 2,275 key lines, every one the same, value for value, 0 FAIL in both.
- **Each address alone** (48 runs): 7,389 requests to 1,659, 730,329 rows to 361,041, about 547 s to 125 s. Every page's lines the same.
- **Every page value moved**: every key FAILs in both scripts, the same 2,033 lines; the other 242 lines are the committed files against their live-set rows, which no page value reaches, the same in both.
- **A run a kind** (18 kinds): the same lines in each. `bsup|`, `ercotn|`, `file|`, `series_esum|`, `series_max|`, `series_n|`, `states_sum|`, `storage|` read as before.

The slowest ten addresses by that estimate, alone, before and after (requests, rows, seconds of answers; the page's own draw beside them): CAISO's monthly mix 425 to 91, 26,199 to 12,741, 28.1 to 6.6 (the page: 70 requests, 47,400 rows); `/grid/caiso` and `/grid?grid=caiso` 399 to 82, 26,093 to 12,635, 26.2 to 5.9 (69, 46,925); the Flex Alert scorecard 395 to 46, 395 rows both, 25.0 to 3.0 (6, 3,774); ERCOT's monthly mix 278 to 66, 70,044 to 23,011, 20.9 to 5.0 (61, 36,922); `/grid/ercot`, `/grid?grid=ercot`, its Mix tab and `/mix?ba=erco&state=TX` 277 to 58, 70,515 to 22,906, 20.2 to 4.5 (60, 36,447); `/grid/spp` 277 to 51, 50,181 to 18,594, 18.9 to 3.8 (52, 32,221).

Decisions (chain 091, session 1186):

- **Never a weaker check: a key that failed before fails.** Proved three ways: the two scripts' lines on the drawn pages, the run with every page value moved, and `site/scripts/test-check-values-light.mjs` (8 tests: check-values run as it is on two pages of real rows, every right key ok and every wrong key FAIL, a revised hour's row still read for its `loaded_at`; on the old script its three verdict tests pass and its five request tests fail).
- **The snapshot once a page, not once a run**: the Storage object is refreshed every hour, and a page is drawn from one object; a run is up to 15 minutes. An answer that is not ok is not kept (the next key asks again, as before).
- **Groups only where a key's own query would answer the same rows**, so no rule of PostgREST's order or paging changes a figure; the sums of a window keep the order of the rows they read (the window's rows by entity, hour and variable), so a sum over one variable adds the same numbers in the same order.
- **Bytes can grow where rows fall**: a group's answer carries each row's variable, so the sums' runs read 0.8 MB to 2.6 MB for the same 47,616 rows in 124 requests to 57; across every address the bytes fall from 66.7 MB to 9.5 MB.
- **Left as they read**: the Clean tabs' single hours of `carbon_intensity_hourly` (one variable, several hours a grid: 38 requests of one row each, against the page's 17 to 22 requests of about 10,000 rows) and `series_n|` (one window a key, no two keys of one window). Neither reads more than the page.
- **The measure is kept** (`site/scripts/check-values-cost.mjs`): its estimate of time is the sum of each request's first answer, not a live run's; the live timing waits for a build (under "To finish" of session 1186's report). Its proxy can be kept open (`--serve-proxy`) so several runs share one set of answers.

## The stored answers, refreshed (chain 091, 24 October 2026)

Chain 091 in this note: session 1187 (written by session 1188 from its report; session 1187 changed no note).

Session 1187. The Ask panel's stored answers (`grid_ask_<grid>`, session 1157 above) came from the two evaluation runs that kept every tool call with its result. Chains 075 and 076 recorded four later runs that keep them (session 1111's `trace`), asked through `/api/ask` on 23 October 2026: `warehouse/chat/eval/eval_s1113_run.json` (session 320's thirty), `eval_s1114_run.json` (session 1114's thirty), `eval_s1133_s320_run.json` and `eval_s1133_s1114_run.json` (session 1133's two askings again). Their grades are in files of their own (`eval_s1113_grades.json`, `eval_s1114_grades.json`, `eval_s1133_s320_grades.json`, `eval_s1133_s1114_grades.json`), not in the run. All four are in `RUNS` of `site/scripts/build-grid-ask-examples.mjs`, newest first, each with its `grades` file and its session; `site/data/grid_ask_examples.json` is rebuilt and `--check` passes. The selection rule above is unchanged: the script on the three older runs alone writes the committed file of before byte for byte. Two rules are added, written in the script's head and held by `site/scripts/test-grid-ask.mjs` (349 tests):

- **`joinGrades`**: a run whose grade is in a file of its own has it joined by question id, and a grade row is used only when it is of that asking (its status, count of tool calls, seconds and cost equal the run's question). Graded right is the grade on the keys: `ok` with `grade.ok` (session 1114's set), `now_ok` with `grade_now.ok` (session 320's set).
- **`newestAskings`**: when two runs asked the same words, one asking is kept before the order: the panel's own route first, as before, then the latest asking by its time, then the later session.

On 24 October 2026, by grid (shown of usable): ERCOT 5 of 44 (was 5 of 23, the same five), CAISO 5 of 17 (was 5 of 10, all five now of 23 October), SPP 5 of 9 (was 5 of 5), the Lower 48 5 of 6 (was 3), MISO 2 (was 1: session 1133's paused-MISO refusal added); PJM 2, NYISO 4 and ISO-NE 4 unchanged.

Decisions (session 1187):

- **Right is the grade on the keys, not under the hold and not with session 320's rulings taken the answers' way.** An answer right only under the hold (a license refusal: g07, g08, d05, d07) or only with those rulings (b01 to b06, b08, b09, g03, g06, d10) is left out, and the data file says which: a license refusal is right only while the hold lasts, and the panel already puts the license words in place of a held answer on the day.
- **A grade row is used only when it matches the asking**: session 1133's grades file says "eval_s1113_run.json graded" in its `_about` (a wrapper's rename), and its rows match 1133's run, not 1113's.
- **The newest asking is kept by its full time, not its day**: the four runs were all asked on 23 October; the order of the five shown is the day rule as before.
- **Answers that name "EIA-930" stay out** (d01, d02, d08, d09, and 1133's d03): the number check reads 930 as a figure no tool returned. The rule is the site's own (`lib/chat/ask.ts`), so it is kept; 1113's d03 is shown in place of 1133's.
- **The run files are read from the branch**: `origin/main` was merged into the chain's branch (commit `f2b163cf`), so the script and CI's `--check` read them where they read the older ones, rather than the script pointing at main's files.

## The Ask column, by tab (chain 100, 24 October 2026)

Chain 100 in this note (sessions 1400 to 1409): session 1405 (this section); session 1406, "The Lower 48 on the Network tab", below; session 1404, "Every panel drawn, a render case each", after it; sessions 1402 and 1403 are in `generation_mix_hourly.md` (the hub's price beside the hourly mix, the cleanest hours live); sessions 1400, 1401 and 1407 changed no note (each blocked without a build); session 1408 wrote this line, session 1404's section and the two Decisions blocks marked as its own.

Session 1405. The Ask column's stored answers (`grid_ask_<grid>`, sessions 1157 and 1187 above) are now ordered by the tab on screen: the page gives the panel its tab (`<AskExamples grid={grid} tab={view} />`), and `lib/gridask.ts` `orderByTab` puts first the answers that read a table of that tab, then the rest, each part in the stored order. The five at most a grid are chosen as before, then ordered; no answer is added, dropped or changed, and each `<details>` stays closed. An answer's tab is read from the tables its tool calls read (its `sources`), through `ASK_TABLE_TAB`, built once from the tab lists of `lib/gridtables.ts` (`GRID_VIEW_TABLES`): a table of the Network tab's list that the Mix tab's does not name, or an interchange table, is the Network tab's (Gravity reads the same list, so it orders as Network); a table of the Clean tab's list that the Mix tab's does not name, or a carbon, emissions or clean energy table, is the Clean tab's; any other table of the Mix tab's list (generation, demand, prices, the mix, storage) is the Mix tab's; a table no tab lists has no tab.

On 24 October 2026 the order moves on four grids and two tabs: ERCOT on Clean (the carbon answer, q05, first), PJM on Clean (q29), ISO-NE on Clean (q18 and q26, its two public carbon answers, then the two held), the Lower 48 on Mix (p09, the hourly demand, first) and on Clean (p02 and q19, the carbon answers, first). CAISO, SPP, MISO and NYISO keep their order on every tab, and every grid keeps it on Network and Gravity: none of those answers reads a table a tab lists (the cost of power, merchant revenue, the battery stack, curtailment, day-ahead prices, the queue), or reads an interchange table.

Decisions (session 1405): the tab of a table is decided in the order network, clean, mix because the tab lists overlap (the Mix and Clean tabs draw the same files, and the Network tab's list names carbon, demand and hub price tables too), so membership alone would put a carbon table on three tabs; tables on no tab's list (`cost_of_power_monthly`, `iso_dam_hub_prices` and the rest) are given no tab rather than one by their names, so the map stays the lists' and cannot drift from them; an answer reading tables of two tabs is first on both; the selection of five comes before the order, so a tab never brings in a sixth answer; `tests/test_session1157.py`'s pin of the page's line now reads `<AskExamples grid={grid} tab={view} />` (both its assertions kept, one added: the panel drawn once).

Decisions (session 1405, the rest of its report, written by session 1408):

- **The order is computed in `gridAskExamples`** (`lib/gridask.ts`, a fourth argument, optional), so the panel and `site/scripts/test-grid-ask.mjs` share one function; without a tab the order is the stored one.
- **Two attributes, no words**: `data-ask-order` on the section (the tab used) and `data-ask-example-tab` on each answer (its tabs); neither is a `data-check` key.
- **The tables on no tab's list** (the cost of power, merchant revenue, day-ahead hub prices) are put to the owner: counting them as the Mix tab's would move CAISO's and SPP's answers there, and would need a list of their own in `lib/gridtables.ts`.
- **No figure moved**: `site/scripts/same-figures.mjs` on the four tabs of ERCOT and of the Lower 48, 592 figures, every page the same.

## The Lower 48 on the Network tab (chain 100, 24 October 2026)

Chain 100 in this note: session 1406 (and session 1405, the section above).

Session 1406. The Lower 48's Network panel (`grid_network_us48`, `site/components/grid/NetworkFigures.tsx`) listed the seven ISO grids' net exchange in the hour the network opens on, and nothing of the Lower 48 itself. Under that table, which stands as it was (its 14 figures, keys and file unchanged), it now draws, for the same hour and from the same reads (`site/components/grid/Lower48Demand.tsx`, the figures computed by `lower48Demand` in `site/lib/gridKeys.ts`):

- **Each of the seven grids' demand**, the grid in view's own figure, chosen and keyed as its own panel chooses it (`demandAt`): the hourly snapshot's `demand_recent` as `netsnap|<BA>|demand_mw|<hour>`, else the week's `eia930_all_demand` row as `series|eia930_all_demand|eia930:<BA>|demand_mw|<hour>`.
- **The Lower 48's own demand**, EIA-930's US48 (`series|eia930_all_demand|eia930:US48|demand_mw|<hour>`), from the rows of the week the page already reads (`app/network/data.ts` `liveExtras` now keeps US48 beside the seven, aligned the same way; the network draws no US48 node, so nothing on the map moves).
- **The seven's sum** (`calc|add|<D1>|...|<D7>`) and **its share of the Lower 48**, percent (`calc|addpct|<D1>|...|<D7>|<US48>`), each only when all seven grids hold a demand in the hour. `add` and `addpct` are two ops of `calc` (`site/scripts/check-calc.mjs`): the operands added left to right, and their sum over the last operand times 100. check-values recomputes every operand as before.
- **The seven's exchange, in words**: "the seven together sent out" or "took in", on net, the sum of their net exports over their reporting ties; a tie between two of the seven counts once for each and cancels, so the sum is what crossed to the grids around them. It is split by the operator at the other end: with the rest of the Lower 48, and with Canada's and Mexico's operators (`OUTSIDE_US48`: AESO, BCHA, CEN, HQT, IESO, MHEB, NBSO, SPC, the snapshot's nodes outside the Lower 48). Each of the three is written as a size with its direction in words, so each is keyed by the operands that give that size: a figure sent out by the seven's `net|export|<BA>|<hour>` and each tie to Canada or Mexico read from the far side (`net|tie|<outside>|<BA>|<hour>`), a figure taken in by `net|import|<BA>|<hour>` and the ties read from the seven's side; one operand is its own key, more are `calc|add|...`.

A failed read of `eia930_all_demand` takes the Lower 48's demand and the share, said "could not be read" (session 1181's rule); each grid's demand the hourly snapshot holds for the hour still stands, as on its own panel, and so does the sum. An empty read says "not held". The block's table and its three sentence figures are the panel's second file, `grid_network_us48_demand` (session 1182); its anchor is `#lower48-demand` (`LOWER48_DEMAND_ANCHOR`), and its method link is this section (`METHOD_NETWORK_US48`), beside the panel's own anchor and method, as sessions 1402 and 1403 placed theirs. On the committed snapshot (built 2026-10-23 14:36 UTC) and the week's rows, in the hour of 2026-10-21 23:00 UTC: the seven's demand sums to 327,272 MW, 65.77 percent of the Lower 48's 497,563 MW; the seven took in, on net, 12,246 MW, of it 7,190 MW from the rest of the Lower 48 and 5,056 MW from Canada's and Mexico's operators (`site/scripts/test-grid-lower48.mjs`).

Decisions (session 1406):

- **The rest of the Lower 48 is the sum of the net exports less the ties to Canada and Mexico**, not the sum alone: six of the seven grids hold ties to Ontario, Quebec, New Brunswick, Manitoba, Saskatchewan or Mexico, so the sum alone is the exchange with every grid around the seven, not with the Lower 48. Both are said, with the part abroad.
- **No new key kind**: two ops of `calc`, so check-values and check-methods read the operands as they read every calc key (check-methods names a calc key by its operands, all named above). The op is not called `sum`: session 1165's test holds `calc|sum` to no value.
- **A size and a direction in words, keyed by the operands that give the size**, rather than a signed figure, as the grid in view's own sentence writes its net ("sent out, on net," or "took in, on net,").
- **The sum and the share only when all seven grids hold a demand in the hour**: a sum over fewer would be a different figure under the same words.
- **The Lower 48's demand has no fallback**: the snapshot has no US48 node; where the week's rows lack the hour it is "not held".
- **The stand-ins of three tests now read `fixtures/grid_balance.json`'s week as the `[ts_utc, value]` rows it holds**: they had read each row as an hour's value, so six grids' demand and generation were NaN in `test-grid-files.mjs`, `test-grid-failed-reads.mjs` and `test-grid-render.mjs`. With the rows read, CAISO's and ISO-NE's balance draw their week and the gravity table its seven shares in the render test; those six cases' counts were raised to the figures drawn, and the render test now counts a NaN as a figure without a value.

Decisions (session 1406, the rest of its report, written by session 1408):

- **The block is its own file, `site/components/grid/Lower48Demand.tsx`**: `tests/test_session1153.py`, `1159` and `1182` count `<F `, `className="mt-10">` and `<PanelFile ` in `NetworkFigures.tsx`, which gains one line and one import. Its anchor and method stand outside `GRID_ANCHOR` and `GRID_METHOD` (`LOWER48_DEMAND_ANCHOR`, `METHOD_NETWORK_US48`); this section's heading is a link target, its id held by `site/scripts/test-grid-files.mjs` and `tests/test_session1406.py`: a rename is made with the constant.
- **The seven's share against the other balancing authorities** (the Lower 48 less the seven) is left to the reader, and put to the owner.
- **No figure that stood moved**: `same-figures.mjs` on 7 addresses (267 figures), the two Lower 48 Network addresses differing by the block's 16 figures only.

## Every panel drawn, a render case each (chain 100, 24 October 2026)

Chain 100 in this note: session 1404 (written by session 1408 from its report; 1404 changed no note).

Session 1404. `site/scripts/test-grid-render.mjs` draws `/grid` outside Next on the committed fixtures (`site/scripts/grid-render-standin.mjs`, session 1182's stand-in for PostgREST and Storage, with session 1180's and 1166's fixtures added) and holds each panel, a case a panel and a kind of grid (ERCOT; CAISO; a held grid, ISO-NE, and MISO on the Clean tab; the Lower 48; PJM where a panel has a line for no price held), to its block's name, its figures by key kind and count, each with a value, its rendered words, its held lines ("license needed" with the reason on hover), its anchor, its method link and its files. A family check fails when a `grid_<panel>_` family drawn on the fixtures' pages has no case, so **a session that adds a panel adds its case to `CASES`**, beside the panel's key, failed-read guard, file, anchor and method link (sessions 1181 to 1184). Session 1405 added an order check and four cases (72 in all), and session 1406 the Lower 48's demand rows to its Network case.

The python tests that pin the Grid tool's markup word for word stand: 63 of their assertions, in 19 files, carry the line `# also covered by site/scripts/test-grid-render.mjs: <case>` above them, and `tests/test_session1404.py` holds every such line to a case that exists and ran. No pin is retired: that is the owner's ruling.

Decisions (session 1404, written by session 1408):

- **A pin is covered only when every string it holds is drawn in one case's block** (a sentence, a key template's literal prefix longer than four characters, a panel name, an anchor, a method link); 467 pins are not covered, 413 of them lines of code no render shows.
- **The render's stand-in is a module of its own**, and the two older tests' stand-ins are left as they were, since python tests pin lines of `test-grid-files.mjs` and `test-grid-failed-reads.mjs`.
- **The counts follow the fixtures as drawn**: session 1406 found the stand-ins read `fixtures/grid_balance.json`'s week as one value an hour, raised six cases' counts to what is drawn, and made a NaN count as a figure without a value; that change of 1404's expected counts is put to the owner beside 1404's pins.

## The older blocks when a read fails (chain 107, 24 October 2026)

Chain 107 in this note (sessions 1410 to 1418): session 1411, the older blocks when a read fails (this section, with a second Decisions block written by session 1417 from its report). The chain's other sessions are in other notes: 1412 in `flex_alert_scorecard.md` (section 12, the small charts on hover); 1413, 1414 and 1416 in `generation_mix_hourly.md` ("The computed views, keyed", and its subsections on the Clean tab's tables and on "Yesterday" and the mix table); 1415 in `emissions.md` ("On the Grid tool's Clean tab, keyed") with its one function in `generation_mix_hourly.md`. Session 1410 changed no note (the next file, and the landing blocked); session 1417 wrote this line, the other notes' index lines and the Decisions blocks marked as its own; session 1418 writes the chain's note in `docs/state/`, no method note.

Session 1411. Session 1181's list of older blocks that said "not held", "not in the warehouse yet", "none" or nothing when their read failed, each now saying "could not be read" in the tool's one look (`Missing` of `components/mix/Now.tsx`: the table and the reason on hover) and drawing no figure of the read; with every read answered each is drawn as before:

- YourGrid's battery cycle (`storage_daily_cycle`): "EIA-930 has no battery series for this grid" on a failed read; now "ERCOT's daily battery cycle: could not be read" (`components/grid/YourGrid.tsx`, `Unread`);
- YourGrid's battery units (`storage_capacity`): "Not in the warehouse yet: battery units mapped to ERCOT"; now "Battery units in ERCOT's footprint: could not be read";
- the price board (`price_board_latest`): "Not in the warehouse yet: ERCOT's hub prices"; now "could not be read"; its peak and off-peak cells (`price_board_peak_offpeak`): "none"; now "could not be read", the latest days' prices beside them as before;
- the carbon intensity: the hour (`carbon_intensity_hourly`) "Not in the warehouse yet"; the months since 2018 (`carbon_intensity_monthly`) nothing; each now "could not be read", the other drawn as before;
- "Yesterday" (`components/grid/Conditions.tsx`): the station's temperatures (`weather_obs_hourly`) failed drew every day's degree days as "not computed (0 of 24 hours in weather_obs_hourly)"; now "Degree days at KDFW: could not be read" (`weatherError` in `loadConditions`);
- CAISO's daily series (`caiso_reliability_daily`, `components/grid/Reliability.tsx`): a failed peak read drew the two tables with no row and no word; now "The daily peaks could not be read" and "The latest days could not be read"; a failed ramp, battery or notice read drew "not held" or a blank cell; now that cell says "could not be read", every other cell as before (`RowUnread`);
- the table citations (`components/Cite.tsx`, every page's): a failed `catalogue` read left the source reports out without a word; now "(the source reports could not be read)", the reason on hover;
- the Flex Alert scorecard's notices column (`/grid/caiso/alerts`): blank on every day when `caiso_grid_emergencies` failed; now each day's cell "could not be read"; its 433 figures as before.

`site/scripts/test-grid-failed-reads.mjs` holds each (33 cases, 107 in all): the blocks are recorded under their Section's title beside the block they are drawn in, on a new committed fixture (`site/scripts/fixtures/grid_older_reads.json`, real rows read once with the anon key) and session 1180's `grid_units.json`; on the code before (the six source files stashed) 24 of the 33 failed. `site/scripts/same-figures.mjs` now also walks `/grid/caiso/alerts`.

Decisions (chain 107, session 1411):

- **An empty answer of CAISO's daily peaks is a failed read** (`lib/gridReads.ts` `wholeSeriesRead`, beside 1181's `wholeRead`, whose words name the events endpoint): `peak_demand_mw` holds every Pacific day since 2018, and an empty 200 is the one answer the hourly data cache could keep. The other daily reads, and every other block's empty answer, say what an empty answer is, as before ("not held", "not in the warehouse yet", "not computed (0 of 24 hours)", "none"); the scorecard's notices read is a window and stays blank on an empty answer (1181's rule).
- **The citation's words are written in `Cite.tsx`, not taken from `Missing`**: the component is every page's, and `tests/test_session473.py` keeps `Missing` to the Grid tool's files; the look is the same (dotted, italic, the reason on hover, `data-missing`). `Conditions.tsx` and the scorecard page take `Missing` and join that test's allowed list (no assertion removed).
- **When the hourly carbon intensity fails, the block says so and stops**, as it stopped with no hour held; the months are not drawn alone (the block's shape is unchanged).
- **The catalogue is answered only in the test's 1411 cases**: every case before them ran on a stand-in that answers it no row, so each draws as it did.
- **The page's HTML is byte for byte the same when every read succeeds** (`same-figures.mjs --sizes`); the flight payload grows by 5 to 60 bytes a page, the `null` of each new failure branch.

Decisions (chain 107, session 1411, the rest of its report, written by session 1417):

- **In CAISO's latest days, a failed read of the battery's MW at the evening peak leaves the battery's share drawn**: the share is its own read (`battery_share_pct`), so it is drawn with its figure and the MW beside it says "could not be read" (`battery_mw_evening_peak`); a failed read of the share says the whole cell could not be read, since the MW is written inside the share's cell.
- **A failed read can be shown on a running site only by hand**: production's reads cannot be made to fail, so the check at a build is `site/scripts/failing-read-proxy.mjs`, one table at a time (`storage_daily_cycle`, `price_board_latest`, `weather_obs_hourly`, `caiso_reliability_daily`, `catalogue`, `caiso_grid_emergencies`), with each block's words read in the browser; until then the node test is the proof.

## The older blocks' files, anchors, method links and render cases (chain 111, 24 October 2026)

Chain 111 in this note (sessions 1419 to 1426): the Grid tool's older blocks given what chains 091 and 100 gave the new panels, every session in this section: session 1420, their files; session 1421, their anchors and method links (with the subsection "Right now" and the mix in that hour, at the section's end); session 1422, their render cases; session 1423, the network component's words against its panels; session 1424, the Gravity tab's blocks at 390 pixels. Each has its paragraph and its Decisions, and where its report held a rule the first block left out, a second Decisions block written by session 1425 (1420, 1422, 1423, 1424). Session 1419 wrote the next file and changed no note; session 1425 wrote this line and the blocks marked as its own. No other note holds a chain 111 section: the sections session 1421's links open (`storage.md`, `price_board.md`, `energy_projects.md`, `datacenter_facilities.md`, `california_reliability.md`) stand as they were.

Session 1420, each older block's figures as a file. The blocks that stood before chain 077 and show a table of figures are named panels, each offering its figures as a CSV written into its link by session 1182's `components/grid/PanelFile.tsx` (the section "Each panel's table, to download" above), made from the same figure nodes the block draws:

- `grid_rightnow_<grid>` ("Right now: demand", `components/grid/YourGrid.tsx`): the latest hour's demand, the same hour a week earlier, the day's highest hour so far (`eia930_all_demand`); file `erw_grid_rightnow_<grid>.csv`;
- `grid_batteries_<grid>` ("Batteries"): the latest complete day's discharge, charge and hour of most discharge (`storage_daily_cycle`) and the battery units by status (`storage_capacity`); file `erw_grid_batteries_<grid>.csv`;
- `grid_cost_<grid>` ("What it costs"): the hub's day-ahead and real-time daily means, the peak and off-peak means and the 30-day average (`price_board_latest`, `price_board_peak_offpeak`); file `erw_grid_cost_<grid>.csv`;
- `grid_building_<grid>` ("What is being built"): the interconnection queue by kind (`energy_projects`) and the datacenter facilities mapped to the grid (`datacenter_facilities`) as `Figure:` lines; file `erw_grid_building_<grid>.csv`;
- `grid_reliability_caiso` ("Reliability", `components/grid/Reliability.tsx`): three files, `_days_per_year` (with the table's notice count and newest day as `Figure:` lines), `_highest_peaks` and `_latest_days` (`caiso_grid_emergencies`, `caiso_reliability_daily`);
- `grid_nowmix_<grid>` ("The mix in that hour", `components/grid/NowView.tsx`): the hour's net generation by fuel, the total as a `Figure:` line (`eia930_all_generation`); file `erw_grid_nowmix_<grid>.csv`.

"Yesterday" and the mix table had their files from session 1416, and the Clean tab's carbon blocks from session 1415 (`generation_mix_hourly.md`, `emissions.md`); nothing of theirs moved here. `site/scripts/test-grid-files.mjs` holds every figure of each block in its file and back on the committed fixtures, which now hold the older blocks' own rows (four tables of `fixtures/grid_older_reads.json`, CAISO's queue positions of `fixtures/caiso_queue_positions.json`); `site/scripts/test-grid-render.mjs` has 18 cases of the six families; `check-table-downloads.mjs` and `check-download.mjs --grid` read the new files (`scripts/grid-files.mjs` `GRID_FILE_PAGES`, a held grid's page among them) and fail a file whose held figures are not each written "license needed". `same-figures.mjs` on the Mix tab of ERCOT, CAISO and PJM: 704 figures the same, in order; only the panel names added.

Decisions (chain 111, session 1420): **a held block draws no figure and offers no file** (ISO-NE's prices and queue: their held lines only; a held figure inside a file, the datacenters' today, is written "license needed", never its value); **a block with no figure offers no file** (a failed read, a table not in the warehouse yet, California's mix withheld); **Reliability's batteries cell is two columns of the file** (their share in percent, their MW), one cell on the page, so each figure is a cell of its own; **the days per year write a blank where the page draws a dot**; **the blocks are wrapped in `data-grid-panel`, the `Section` lines the python tests pin unchanged** (Reliability names its own panel, `<Section id="reliability" ...>` as pinned), so session 1159's row rule now reaches their tables (rows about 33 px where they were about 29: a look, no figure); **CAISO's queue fixture rows are given stand-in ids** (`caiso_queue:standin-<n>`) for the read's prefix filter only, the four fields read real and no id drawn or keyed; anchors and method links of these blocks are session 1421's.

Decisions (chain 111, session 1420, the rest of its report, written by session 1425): **the figures are drawn once and filed**: a block's figures that were inline `Num`s are constants drawn once and handed to its file (Reliability's row cells through `dayParts`), so the file and the face share one node and the served HTML is the same (`same-figures.mjs`), and `YourGrid.tsx` still holds the 18 `check=` that session 473 counts; **the check scripts' default list also asks for sessions 1415's and 1416's files** (the Clean tab's carbon blocks, "Yesterday", the mix table) and for a held grid's page, ISO-NE's, where a held block must offer none; **a page's list holds what its fixtures draw**: ERCOT's queue is not in the fixtures, so ERCOT's "What is being built" file is not in `GRID_FILE_PAGES` until a build shows production draws it.

Session 1421, each older block's anchor and method link, by session 1183's and 1184's rules: one list, `site/lib/gridAnchors.ts` `OLDER_ANCHOR` and `OLDER_BLOCKS` (outside `GRID_ANCHOR` and `GRID_METHOD`, whose 17 panels sessions 1183 and 1184 pin, as sessions 1402 to 1416 placed theirs), each block's address with its anchor in `check-routes.mjs`'s `GRID_ANCHORS`, each fragment held by `site/scripts/test-grid-older-methods.mjs` to the id the site's renderer writes for the heading named there (`lib/markdown.ts` `headingSlugs`), and judged by `check-links.mjs`'s own logic:

- "Right now: demand": `#right-now`, on `/grid?grid=ercot`; method: this note, "Right now" and the mix in that hour (below, new);
- "Batteries": `#batteries`; method: `storage.md`, "The figures on the page and their keys" (the existing "Method" link now opens it);
- "What it costs": `#what-it-costs`; method: `price_board.md`, "The figures on the page and their keys" (the existing link);
- "What is being built": `#what-is-being-built`, on `/grid?grid=caiso`; methods: `energy_projects.md`, "The figures on the grid page and their keys", and `datacenter_facilities.md`, "Grid pages: which grid a facility belongs to (session 36A)" (the two existing links);
- Reliability: `#reliability` (the id its section always had), and one anchor a table, `#reliability-days`, `#reliability-peaks`, `#reliability-latest`, on `/grid?grid=caiso`; methods: `california_reliability.md`, "1. Every notice since 1998" (the days per year: the existing link "the method") and "2. How tight was it" (the two daily tables: one line under them, new);
- "The mix in that hour": `#now-mix` (the id its section always had), on `/grid?grid=ercot`; method: this note, the section below (one line, new).

"Yesterday" and the mix table (session 1416) and the Clean tab's carbon blocks (session 1415) had their anchors and method links already; nothing of theirs moved.

Decisions (chain 111, session 1421): **an existing method link opens its section, its words unchanged** (Batteries, What it costs, What is being built's two, Reliability's "the method"), as session 1184 did for the scarcity strip and CAISO's alerts, so the only new words are the two blocks' new lines and the daily tables' one; **the ids the blocks had are kept** (`reliability`, pinned by sessions 58 and 1420; `now-mix`), the new ones on each block's own `Section` (inside its panel's element, whose line session 1420's test pins) or on each Reliability table's heading; **Batteries opens the section of `storage.md` that names the block** ("a grid's block Batteries") rather than `storage_daily_cycle`'s, which defines the day's cycle alone (CAISO's block draws only the units); **one new section, below, where no note defined a block** (Right now and the mix in that hour), the others' sections as they stand; **the new method lines are drawn in every state of their block** (no data, CAISO's mix withheld), none in a failure's words (session 1184), and the existing links stay where they stood (What it costs' and the queue's only where their figures are drawn); **the `id` follows the `title` on each `Section`** (`tests/test_session137.py` reads the titles in order); **the older blocks' fragments are tested in a file of their own**, `site/scripts/test-grid-older-methods.mjs`, since `tests/test_session1184.py` counts `test-grid-methods.mjs`'s five tests; **no figure moved**: `same-figures.mjs --sizes` on the Mix tab of ERCOT, CAISO, ISO-NE and the Lower 48, 834 figures, every page the same, the panels the same, the pages 418 to 1,792 bytes larger.

Session 1422, each older block's render case. Session 1404's render test (`site/scripts/test-grid-render.mjs`) drew the older blocks only inside the tab around them, where a pinned test read them (`view_now`, `view_mix`, `view_clean`, `view_gravity`, `mixview_now`, ERCOT and ISO-NE). Every block of the page that stood before chain 077 and had no case of its own now has one, a case a grid kind where the block is drawn differently (ERCOT, CAISO, ISO-NE as the held grid, the Lower 48), on the committed fixtures, each checking its name, its own figures by kind and count, its words, its held line, its anchors, its method links and its files: the Now view's sentence, its three headline numbers and its source line; YourGrid's opening lines, "Who runs this grid", "In the news", "About <ISO>", "Where the power comes from" (the Mix tab) and "How clean" (the Clean tab); the energy mix view's "today so far", its hourly mix section (the chart and legend around the keyed panel) and "monthly mix since 2001", and the views "the records" and "Wind and solar forecasts"; the Clean tab's "The last 24 hours" (its chart around the keyed table), CAISO's break note and the tab's source line; the network component's server lines (the opening sentence, the age line, the live week, the newest hour and the source line) on the Network and Gravity tabs; and the page's header (its title, lead and the tables' licenses), the Ask panel beside every tab and the decisions block. Blocks of figures that chains 077 to 111 named already keep their cases (Right now, Batteries, What it costs, What is being built, Reliability, the mix in that hour, Yesterday, the mix table, the Clean tab's carbon blocks, the computed views). The page draws every block as it did: the older ones are named in the test's stand-in only (`site/scripts/grid-render-standin.mjs` `OLDER_MARKS` and `OLDER_COMPONENTS`, a `Section` or `ToolSection` by its title, a `<section>` by its id), each counting as its own the figures, ids, links and files not inside a named panel within it. One fixture is new, `site/scripts/fixtures/grid_mix_now.json` (`eia930_generation_latest` for ERCOT, ISO-NE and the Lower 48, and `state_generation_mix_monthly` for the United States, every row, read once with the anon key), so "today so far" and "monthly mix since 2001" draw their figures; the ERCOT mix view's case counts their 9 where it counted none.

Decisions (chain 111, session 1422): **the older blocks are named in the test's walk, not on the page** (no markup moved; a `data-grid-panel` would make each a panel family with its own file, anchor and method, which sessions 1420 and 1421 gave the blocks of figures); **a block drawn the same on every grid has one case** (the same words, figures and keys once the grid's name is set aside: "monthly mix since 2001", "The last 24 hours", the server lines on the Gravity tab, the records on the Lower 48, which open on ERCOT's); **a written block's rendered markdown is read as its words** (the stand-in reads `dangerouslySetInnerHTML` with its tags taken out, so "Who runs this grid" and "About <ISO>" are checked by their first sentence); **the source reports' line stays as the fixtures draw it** ("the source reports could not be read": no fixture holds the `catalogue` table, as in every case before); **a held line is the block's own** (ISO-NE's "license needed" inside a named panel is that panel's, not the block's around it); **a pin is annotated only where every string it holds is drawn in one case's block** (5 of the pins that read these blocks' files; the others hold markup or code a render does not show).

Decisions (chain 111, session 1422, the rest of its report, written by session 1425): **no pin is retired** (the 5 annotated carry one comment line each, as session 1404's did; retiring one is the owner's ruling, session 1404's line of the rulings list); **a later session that names an older block on the page** (a `data-grid-panel`) **moves its case to the panel's name**, and session 1404's family check then asks for that panel's case; **a case's words hold no clock** (no "this page was drawn"), so the test answers the same at any hour; **the fixture holds every row of the two reads the blocks make, not a sample** (the United States' monthly mix whole, three pages of at most 1,000 rows), so the share columns are the page's own; **a count of before is raised only to what is drawn** (the ERCOT mix view's 0 to 9), its other fields kept.

Session 1423, the network component's words against its panels. The component (`app/network/Network.tsx`, drawn in the browser) writes figures the server panels `grid_network_<grid>` and `grid_gravity_<grid>` key in the hour it opens on: the side panel of the picked grid (its ties, their net, its demand), the gravity shape's cards (net generation, net import, the import as a percent of generation) and the map's line cards (a tie's MW, session 1156). The side panel's MW words moved, their arithmetic unchanged, to `site/lib/networkSide.ts` (`sideTies`, `sideNet`, `sideFormat`, `sideNetLabel`, `sideNetMw`, `sideTieWords`, `liveDemand`); `site/scripts/test-network-words.mjs` computes, for the seven ISO grids and the Lower 48 on the committed snapshot (with the live week's demand and generation of session 1165's fixture, the same build), every MW those words, `gravityTip` and `edgeTip` would write, and compares each with the panel's figure for the same tie and hour as each writes it: 153 figures, all equal after the two fixes below. The words changed: the gravity cards' share was written to one decimal ("8.6 percent") where the panel writes two ("8.58"): the cards now write every figure through `lib/format.ts` `shown`, the panel's own; in the live week the side panel writes its MW the same way (whole MW on today's snapshot, so nothing moves there), and a net of exactly zero reads as an export ("Net exports this hour, 0 MW"), as the panel and `netValue` sign it.

Decisions (chain 111, session 1423): **the fix is in the component's words, never in a keyed figure** (`same-figures.mjs` on the Network and Gravity tabs of ERCOT, CAISO and the Lower 48: every page the same, 254 figures); **a story and a replayed day keep whole MW** (they are not the panel's hour: the day view's averages, "MW on average", are by design no panel figure, and `check-network-v3.mjs` reads them whole), so only the shared hour of the live week is compared; **the side panel's share of demand, hub price, carbon intensity, batteries, trace and twelve months are not compared** (no figure of these two panels: the share is computed from the net and the demand, both compared; carbon intensity keeps its own key); **the opening hour and the demand's check key stay in `Network.tsx`** (sessions 124 and 54 pin those lines): the test runs those two lines' own text, so it follows the component as it stands; **`gravityTip` and `netWords` take the formatter as an optional argument** (the component passes `shown`; without it, session 1153's words, which `test-gravity.mjs` pins); **at an exact zero the gravity card says "No net exchange (0 MW)" and gives no share**, where the panel writes 0 and 0 percent: no number differs, one is left unwritten; `check-network-v3.mjs`'s day-view sign reads `net > 0` for "imports", to match.

Decisions (chain 111, session 1423, the rest of its report, written by session 1425): **the comparison is tied to one build**: `test-network-words.mjs` reads the committed snapshot with session 1165's fixture of the live week, and its first test asks that both name the same `snapshot_built`, so when the snapshot is rebuilt the fixture is read again (light, with the anon key) before the test can pass; **the hour the component opens on equals `shownHour`**, the hour the server panels key, on every grid.

Session 1424, the Gravity tab's blocks at 390 pixels, from the code. Session 1158's rules (its report, `site/scripts/test-grid-390.mjs`) read on the blocks chains 078 to 100 added: the gravity table (`grid_gravity_<grid>`), the Exchange blocks under the shape (session 1167's seven-column ties table, the twelve months, the Lower 48's seven grids), the gravity day line (session 1170), the balance (session 1165, on the Network tab) and the replayed day's table, with their download lines (session 1182). Every one of their six tables is the shared `ToolTable`: a scroll frame a keyboard reaches, named by its caption (`lib/cells.ts` `scrollRegion`), a caption, header cells with a scope, the first cell of each row its header (the tie, the grid, the part of the balance); the widest, the ties table at 680 px, scrolls inside its frame, and no block sets a fixed width above 358 px outside one. One miss, mended in markup and classes only: a failed read's reason is drawn as written, and the database's answer in it (`{"code":"57014","details":null,...`) runs 60 characters or more without a space, past a 324 px column; the twelve months' "no data" on the Gravity tab and the network's line "The last twelve months could not be read" now break it (`break-words`, `data-reason-wraps`). Held where a reader meets it: the render test's Gravity cases, the balance's and the gravity day line's carry their tables (`tables` in `site/scripts/test-grid-render.mjs`, read by `grid-render-standin.mjs` from the markup as the server draws it: each table's caption, frame, header cells and row headers, and any fixed width outside a frame), and `site/scripts/test-gravity-390.mjs` holds the source.

Decisions (chain 111, session 1424): **the rules held already on every table of these blocks** (each is the shared `ToolTable`, which sessions 1152 and 1158 gave its frame, caption and header cells), so the only change to the page is the failed read's reason, which a visitor sees only when a read fails; **the wrapper is local** (`break-words` on a `div` around the twelve months' `NoData` and on the network's line), not in the shared `NoData`, so no other page's markup moves; **the 390 checks of these blocks are a file of their own**, `test-gravity-390.mjs`, since `tests/test_session1158.py` pins `test-grid-390.mjs`'s "5 tests passed"; **a case's `tables` lists every table of its block, in order**, so a table added later without its frame or caption fails its case; **the balance's cases are included** (the chain file names it with the Gravity tab's blocks; it is drawn on the Network tab); **no figure moved**: `same-figures.mjs --sizes` on the Gravity tab of ERCOT, CAISO and the Lower 48, 190 figures, every page the same, the panels the same, every page the same size (the new markup is drawn only on a failed read).

Decisions (chain 111, session 1424, the rest of its report, written by session 1425): **a fixed width is read as a phone at 390 px meets it**: a rem counts as 16 px, and a width behind a breakpoint (`sm:` and up) is not counted, since it applies above 390; an inline `width` or `minWidth` in px or rem, `w-[Npx]`, `min-w-[Npx]`, a `w-N` without a breakpoint and an svg's or img's width are; **session 1158's keyboard items stand open**: a keyboard route to each line of the map and the gravity shape, and through the shared charts' points, are the rulings list's lines of session 1158, not changed here.

### "Right now" and the mix in that hour, what each figure is (session 1421)

Two older blocks no section of a method note defined, both at the head of the Mix tab (the Now view's blocks, session 299), both from EIA-930's public hourly tables:

- **"Right now: demand"** (`grid_rightnow_<grid>`, `components/grid/YourGrid.tsx` `RightNow`, read by `site/lib/grid.ts` `load`, the seven ISO grids): `eia930_all_demand`, variable `demand_mw`, the grid's balancing authority (`eia930:<BA>`), the last nine days read. Three figures: the latest hour the table holds, "the latest hour EIA has published" (`series|eia930_all_demand|eia930:<BA>|demand_mw|<hour>`); the same hour seven days (168 hours) earlier, the same key on its hour, or "not held" when the table lacks that hour; and the highest hour of the grid's local day so far: the local day (the grid's time zone, `docs/grids/grids.json` `tz`) of the latest hour, from its first hour held to the end of the latest hour (`series_max|eia930_all_demand|demand_mw|<start>|<end>|eia930:<BA>`), its hour written in local time. The chart draws the local day so far and the same local day a week earlier, moved forward seven days so the two line up; their hours are not written in the block's file. No hour is filled.
- **"The mix in that hour"** (`grid_nowmix_<grid>`, `components/grid/NowView.tsx`, the seven ISO grids and the Lower 48): `eia930_all_generation`, the grid's balancing authority: the newest hour in the last 34 days that holds the total `net_generation_mw` (`site/lib/gridReads.ts` `latestHour`, session 1160), its total (`series|eia930_all_generation|eia930:<BA>|net_generation_mw|<hour>`) and each fuel's `net_generation_<fuel>_mw` row of that hour, largest first, each keyed the same way on its own variable. The bar groups the fuels as the Grid tool's colours (`site/lib/grid.ts` `FUELS`) and gives each group's MW and share of the fuels' sum on hover; the shares are not keyed. California's EIA-930 generation is not drawn (the session 118 ruling, `eia930_caiso_break.md`); a grid with no hour held in the 34 days says so in the tool's "no data" line.

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

## The figures on the page and their keys

Each number `/grid` shows carries its key (`site/components/Num.tsx`), which `site/scripts/check-values.mjs` checks against the live set and `site/scripts/check-methods.mjs` against this note (session 409). The keys the sections above do not name:

- `bsup|<BA>|share:pairs`, `bsup|<BA>|mwh:pairs`, `bsup|<BA>|days_held`: on the Gravity tab, under the gravity shape, the Exchange view's block "Over the last twelve months" (`components/grid/ExchangeView.tsx`): the grid's net imports as a percent of its demand, by the sum of its reported ties (`pairs`), the same net imports in MWh, and the days held, computed from `ba_supply_monthly` by `site/lib/basupply.ts` as "Who supplies a grid" above describes.
- `bsup|<BA>|neighbour_mwh:<ID>`, `bsup|<BA>|neighbour:<ID>`: the table of the grid's neighbours over the same twelve months: each neighbour's net import into the grid in MWh, and its percent of the grid's demand.
- `net|maxflow|<BA>|<hour>`: the Exchange view's headline "Largest flow": the largest flow, either way, over the grid's reporting ties in the hour shown, in MW, read from the network's snapshot of `eia930_all_interchange`.
- `net|topexport|<hour>`: the Exchange view of the Lower 48, in its first paragraph: the largest net export of any balancing authority in the hour shown, in MW, its reporting ties summed and signed from its side (`netExports` and `topExporter` in `site/lib/network.ts`), from the same snapshot; two authorities with the same net export give it to the first by its id.
- Chain 077 (23 October 2026), the server panels of the Network and Gravity tabs (the section "The Grid tool's panels, every figure keyed" above): `net|tie|<BA>|<other>|<hour>`, each reporting tie of the grid in view in the hour the network opens on, MW, signed from the grid's side; `net|export|<BA>|<hour>` and `net|import|<BA>|<hour>`, the sum of those ties as a net export or a net import; `net|ties|<BA>|<hour>`, how many ties reported; `netsnap|<BA>|demand_mw|<hour>`, the grid's demand in that hour where the hourly snapshot holds it (else the `series` key of `eia930_all_demand`, `demand_mw`); on the Gravity tab, `eia930_all_generation`, `net_generation_mw` (a `series` key) and `calc|pct|` of the import over it. On the Clean tab, `carbon_intensity_hourly`, `intensity_generation` (`series` keys, the latest, lowest and highest of the 24 hours).
- Chain 078 (24 October 2026), the Network tab's balance (the section "The balance, said where the figures are" above): `calc|bal|<G>|<D>|<X>`, the gap in the hour shown, net generation less demand less net export, from the `series` key of `eia930_all_generation` (`net_generation_mw`), the panel's demand key and `net|export|<BA>|<hour>`; `netbal|absmean|<BA>|<from>|<to>`, the mean size of the gap (its absolute value) over the snapshot's week, MW; `netbal|hours|<BA>|<from>|<to>`, the count of hours of the week that hold every tie, the net generation and the demand.
- Chain 078 (24 October 2026), session 1167, the Exchange blocks under the gravity shape (the section "The Exchange blocks under the gravity shape" above): `nettie|mean|<BA>|<other>|<from>|<to>`, one tie's mean flow over the snapshot's week, whole MW, signed from the grid's side; `nettie|min|...` and `nettie|max|...`, its lowest and highest flow, MW; `nettie|hours|...`, the count of hours of the week that hold a flow on the tie; `net|lag|<hour>|<refresh>`, the hour's age in hours before the snapshot's refresh, said once in the block.
- Chain 078 (24 October 2026), session 1170, a replayed day's figures (`grid_network_v3.md`, "The outside grids' demand in the replay"): `file|public/network/daily_<year>.json|demand.<BA>.@<day>`, behind `fmt|n0|`, a balancing authority's demand on the day picked, the day's average MW from the replay's committed file of `eia930_daily_demand`, on the Network tab for the balancing authority in the address and on the Gravity tab for the grid in view; `netday|export|<BA>|<day>` and `netday|import|<BA>|<day>`, behind `fmt|n0|`, its net export or net import that day over its ties with a flow, the day's average MW from the same file's `eia930_daily_interchange`; `netday|ties|<BA>|<day>`, how many ties held a flow that day.
- Chain 100 (24 October 2026), session 1406, the Lower 48 on the Network tab (the section "The Lower 48 on the Network tab" above): `series|eia930_all_demand|eia930:US48|demand_mw|<hour>`, the Lower 48's demand in the hour (EIA-930's US48); `calc|add|<D1>|...|<D7>`, the seven grids' demand summed; `calc|addpct|<D1>|...|<D7>|<US48>`, that sum as a percent of the Lower 48's; `calc|add|` of `net|export|<BA>|<hour>` or `net|import|<BA>|<hour>` keys and `net|tie|<A>|<B>|<hour>` keys, the seven's exchange with the grids around them, with the rest of the Lower 48 and with Canada's and Mexico's operators, each a size in MW whose direction the words give.
