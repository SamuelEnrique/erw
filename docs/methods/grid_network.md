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

**Why the license has to be read per file.** The atlas is not one license. Of the 101 datasets its catalog listed, 41 say "This work is licensed under the Esri Master License Agreement", 40 carry only EIA's liability statement, 10 say "None (public use)", 7 say nothing, and one quotes EIA's own rule: "U.S. government publications are in the public domain and are not subject to copyright protection. You may use and/or distribute any of our data, files, databases, reports, graphs, charts, and other information products that are on our website". So a boundary layer on the atlas is used only after its own license statement has been read and says public domain or the equivalent, and the robots file of the host that serves the file (a feature service's host is not `atlas.eia.gov`) has been read as well.

**When the file is held: how it is made.** `warehouse/connectors/eia_ba_boundaries.py build` reads the publisher's GeoJSON as it came and writes the site's file. It is reference geometry, not a table: nothing of it goes through the validator, into `warehouse/output` or into the live set.

- **Matching is exact.** A shape is given to a grid only when the publisher's own code for it, in the property a person names after reading the file (`--code-field`), is the grid's EIA-930 code. No name is compared and nothing is guessed. The file records every grid with no shape (`nodes_without_shape`: Canada's and Mexico's operators at the least, which a file of US boundaries does not hold) and every shape with no grid (`shapes_without_node`). A grid with no shape is not on the map; its ties are not drawn there, and the Network view holds them.
- **The date.** The boundaries are the publisher's as of the vintage its file gives (`provenance.vintage`), one date for every hour and every year the page can show. A balancing authority that changed its footprint, or did not exist, on a day of the replay is still drawn with that one boundary.
- **Overlaps are real.** Some balancing authorities sit inside others. The file is ordered by area, largest first, and the page draws in that order, so a smaller one is on top of the larger one around it.
- **What is simplified.** A grid's parts are joined, then simplified with the Douglas-Peucker rule, topology kept (0.02 degrees by default, about 2 km), coordinates kept to three decimals (about 100 m), and parts smaller than the tolerance squared are dropped. Each shape is simplified on its own, so two neighbours' shared border may open or overlap by up to the tolerance. The file's `provenance` holds the source, the address, the retrieval time, the sha256 and size of the raw file, the publisher's license words and the tolerance; the builder refuses a raw file whose sha256 is not in the request log, and a result over 400,000 bytes.
- **The projection.** Albers for the lower 48 with Alaska and Hawaii inset (d3-geo's `geoAlbersUsa`, which the site's project map already uses).

**What the colors are not.** A region's color is one number for the whole balancing authority: the carbon intensity of what was generated inside it in the period shown. It is not the intensity of the power used at any place inside the boundary (imports are not in it), it does not vary within the region, and a large region is not a large number: area on the map is land, not load or generation. A boundary is a planning footprint as its publisher drew it, not a service-territory survey and not a line any wire follows.

## Not here

- The boundaries of the balancing authorities: not yet held (see "The map").
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
