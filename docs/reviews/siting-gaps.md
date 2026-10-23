# The All grids tab: the cells the warehouse cannot fill

Started by session 703 and completed by session 713 (22 October 2026, chain 050). This file lists every kind of cell of `/cost-of-power?view=allgrids` that the warehouse cannot fill, one row each, by grid. Each row gives:

- the source that would fill it;
- its license, as far as the source registry (`warehouse/metadata/sources.csv`) and `docs/licenses.md` say, without a web request;
- the connector it resembles.

The method is `docs/methods/siting.md`. `/internal/siting-gaps` (internal view) reads this table when the site is built, through `site/data/siting/gaps.json`, which `warehouse/derived/siting_page.py` writes from it. "Held" means the warehouse holds the table, but under terms that keep its figures off the page.

| Grid | Column | What is not held | The source that would fill it | Its license, as recorded | The connector it resembles |
|---|---|---|---|---|---|
| CAISO | Transmission and 4CP | the transmission and delivery charge a large load pays | the large-load (transmission-voltage) tariffs of PG&E, SCE and SDG&E filed with the CPUC, and CAISO's transmission access charge | CPUC: "in general ... in the public domain" (`rules.json` sources); CAISO: free for public use with credit (licenses.md #3) | `texas_delivery_charges.py` (tariff lines, one row a charge) |
| NYISO | Transmission and 4CP | the same | the large-load service classifications of Con Edison, National Grid, NYSEG, RG&E, Central Hudson and O&R (PSC tariffs) | the utilities' tariffs: not read; NYISO: no license conferred (licenses.md #5) | `texas_delivery_charges.py` |
| ISO-NE | Transmission and 4CP | the same | the large-load rates of Eversource, National Grid and the other New England utilities, and ISO-NE's regional network service rate | ISO-NE: permission to request (licenses.md #4); the utilities: not read | `texas_delivery_charges.py` |
| SPP | Transmission and 4CP | the same | SPP's network integration transmission service rates by zone (its OATT), and the members' large-load tariffs | SPP: copy with citation, except within a commercial publication (licenses.md #6) | `texas_transmission_matrix.py` (a rate per zone from a filed document) |
| MISO | Transmission and 4CP | the same; the grid is paused | MISO's zonal transmission rates (attachment O) and the members' large-load tariffs | MISO: written permission needed; paused (licenses.md #7, `miso_pause.md`) | `texas_transmission_matrix.py` |
| PJM | Transmission and 4CP | the same | PJM's network integration transmission service rates by zone, and the utilities' large-load tariffs | PJM: non-members may not republish (licenses.md #15) | `texas_transmission_matrix.py` |
| ERCOT | Transmission and 4CP | the four peaks of summer 2026 | ERCOT's Four Coincident Peak calculation (NP9-83-M), published by 1 December 2026 | ERCOT: public (licenses.md #2) | `ercot_4cp.py` (already the table's connector) |
| ERCOT | Transmission and 4CP | the 2026 transmission rate, approved | the Commission's order in docket 59080 (the 2026 matrices are filed, not approved) | PUCT: restricted (asks permission to copy text; `rules.json` sources) | `texas_transmission_matrix.py` |
| ERCOT nodes | Energy, Transmission | a node's load zone and settlement hub | ERCOT's settlement point mapping (the Settlement Points List and Electrical Buses, NP4-160) | ERCOT: public | `ercot_rt_spp.py` (ERCOT's MIS reports) |
| ERCOT nodes | Utility | a node's wires utility (TSP) | ERCOT's resource registration (Resource Asset Registration Forms, as summarized in its public resource lists) | ERCOT: public | `ercot_dam_esr.py` (ERCOT's resource-level disclosures) |
| ERCOT nodes | Node panel | a node's county, so the planned generation near it | the same resource registration (county), or EIA-860's plant locations matched to the resource | ERCOT and EIA: public | `eia860.py` |
| ERCOT nodes | Node panel | transmission projects by county | the PUCT's certificate of convenience and necessity (CCN) filings, or ERCOT's Transmission Project and Information Tracking report (TPIT) | ERCOT: public; PUCT: restricted | `large_load_filings.py` (documents by docket) |
| ERCOT nodes | Node panel | a node's price in the four peak intervals | the 15-minute real-time settlement point prices of those intervals (NP6-905-CD), kept for the four intervals only | ERCOT: public | `ercot_rt_spp.py` |
| PJM, ISO-NE, MISO, NYISO | Capacity | the price, held | `iso_all_capacity_prices`, internal: shown only with each publisher's permission (NYISO's spot rows are marked public row by row, but NYISO's prices are license-held since 20 October 2026) | internal; PJM non-members may not republish; ISO-NE permission; MISO written permission; NYISO no license conferred | `iso_capacity_prices.py` (already the table's connector) |
| All but ERCOT, CAISO, SPP | Capacity, heavy industry | an interruptible load's capacity charge | each utility's interruptible (curtailable) service rider | the utilities' tariffs: not read | `texas_delivery_charges.py` |
| All | Utility | the row's own utility where the row's name is not a place (a hub with no city, most zones): no county to read. Filled since session 718 for the 18 rows whose name is a place, from `utility_service_territories` (the data machine's, chain 043) | a county for each such row (the zone's or hub's own footprint), or the grids' zonal maps | EIA: public domain (licenses.md #1) | `eia861_territories.py` (the data machine's) |
| ERCOT | Utility | a Texas wires utility's own revenue (CenterPoint in Harris County files no sales row in `eia861_utility_sales`) | EIA-861's delivery-only rows for Texas, or the wires utilities' own tariffs (`texas_delivery_charges` holds four) | EIA: public domain | `eia861_sales.py` |
| All but ERCOT | Time to connect | a large load's own wait, measured | the utilities' and ISOs' large-load queues (NYISO's is held and license-held; the others publish none in a table) | NYISO: no license conferred; others: not read | `nyiso_load_queue.py`, `large_load_waits.py` |
| All | Time to connect | connection timelines by utility | the utilities' large-load interconnection procedures and their stated timelines (tariff schedules, filings) | not read | `large_load_rules.py` (documents read for one sentence) |
| ERCOT | Time to connect | the rule for loads of 75 MW and more, as one held row | the PUCT's rule under SB 6 (16 TAC 25.194, project 58481) and ERCOT's planning guide revision (PGRR 115) | PUCT: restricted; ERCOT: public | `large_load_rules.py` |
| ERCOT | Time to connect | the faster path for a controllable load | ERCOT's Controllable Load Resource registration rules (Nodal Protocols section 3.8 and the large-load interconnection guide) | ERCOT: public | `large_load_rules.py` |
| ISO-NE | Time to connect | the median months to connect | Berkeley Lab's file has no ISO-NE request online from 2023 to 2025 with both dates; ISO-NE's own queue (`isone_interconnection_queue`, held) | Berkeley Lab: may be public (licenses.md #14, not read: HTTP 403); ISO-NE: permission | `lbnl_queues.py` |
| All | Headroom | capacity at the peak hour (solar, wind and storage at what they give then, imports, outages): filled since session 718 as net summer capacity over the peak for every grid (`grid_peak_vs_capacity`), which counts them at their ratings | each ISO's capacity, demand and reserves report; NERC's assessments (not pulled: NERC's terms unreadable, the data machine's session 666) | ERCOT CDR: public; NERC: not read | `grid_peak_vs_capacity.py` (the data machine's derived table) |
| All | Headroom | reserve margins by zone | each ISO's resource adequacy reports by zone; NERC's long-term reliability assessment | not read | `eia_state_capacity.py` |
| All | Headroom | demand growth of the row's own zone | EIA-930's sub-region demand (`eia930_subba_demand_hourly`, held: in the warehouse, not in the live set or the tab's files) | EIA: public domain | `eia930_subba.py` (already the table's connector) |
| All | Headroom | generation with a signed interconnection agreement | Berkeley Lab's `ia_date` (in `lbnl_interconnection_queue`); EIA-860M records no agreement | Berkeley Lab: may be public | `lbnl_queues.py` |
| PJM | Energy | every hub and zone price | a licensed source of PJM's prices (Data Miner 2) | PJM: non-members may not republish | `iso_prices.py` |
| MISO | Energy, Carbon (hourly) | every hub price drawn; the carbon over the hours run | MISO's prices are held and paused; with no price, no hours run | MISO: written permission needed; paused | `iso_prices.py` |
| ISO-NE | Energy | the eight load zones' twelve months | the zone history beyond the tables' recent window (`iso_zone_prices_history`, ISO-NE rows internal) | ISO-NE: permission | `iso_prices.py` |
| All | Substations and lines | the substations and high-voltage lines near a row | HIFLD's electric substations and transmission lines (now held by the data machine's chain, if it has landed) | HIFLD: not read here | `uswtdb.py` (a federal GIS layer) |

## State on 22 October 2026, evening (chain 062)

Each kind of row above, its state after chain 062's sessions 722 to 740 (`docs/reviews/siting-open-2026-10-23.md` holds the item-by-item list):

- **Large-load tariffs** (transmission rows, every grid but ERCOT): **open**. `utility_large_load_tariffs` has not landed; its connector waits on an `OPENEI_API_KEY`. The tab's side is written and tested, not wired (730).
- **Capacity prices shown** (PJM, ISO-NE, MISO, NYISO): **open**, a ruling (the rulings file, session 741).
- **A large load's own wait** (time to connect, every grid but NYISO): **open**.
- **Utility service territories**: **filled** for the rows named for a place (718); each figure now names its kind (726).
- **A zone's own demand growth**: **filled in part** (728): NYISO's eleven zones and ISO-NE's eight; ERCOT's and CAISO's rows keep the grid's.
- **Reserve margins**: **open** (731: no table, no connector).
- **A node's zone, hub, wires utility and county** (ERCOT's settlement point mapping and resource registration): **open** (733: `node_basis_daily` carries none of them).
- **Substations and transmission lines near a node**: **open** (732).

## State on 22 October 2026, night (chain 063)

Read again by sessions 751 to 756 at 18:35 UTC: **no row changed state.** Large-load tariffs, reserve margins, a load's own wait, a node's place, substations and lines stay open; capacity prices wait on a ruling; utility territories stay filled and a zone's demand growth filled in part. One thing found that was held and unused, now drawn: the node's intraday swing (`node_basis_daily`, `dam_spread_4h`, session 746).

## State on 22 October 2026, late (chain 064)

Read again by session 771 at 20:27 UTC: **no row changed state.** The tables chain 064 waited on have not landed.

## State on 23 October 2026, after midnight (chain 065)

Read again by session 792 at 22:28 UTC on 22 October and by session 973 at 00:12 UTC on 23 October: **no row changed state.** Coverage on main lists none of the tables the open rows wait on (`utility_large_load_tariffs`, reserve margins, substations and lines, a 2026 sub-region demand table, ERCOT's settlement point mapping or resource registration). Large-load tariffs, reserve margins, a load's own wait, a node's place, substations and lines stay open; capacity prices wait on a ruling; utility territories stay filled and a zone's demand growth filled in part. Chain 065 drew more of what is held (794's months of two nodes, 795's nodes that settle alike), which fills no gap row. The data machine's queue holds chain 046 (sessions 850 to 864, "sources and gaps"), written at 00:07 UTC: its sessions 850 and 851 are to land ERCOT's settlement point mapping (a node's load zone and hub) and ERCOT's reserve margins. What it lands is read by the next code chain.

## State on 23 October 2026, morning (chain 071)

Read again by session 1038 (chain 071) at about 07:35 UTC on 23 October: **one row changed state.** Reserve margins: **filled for ERCOT** (1027, `ercot_cdr_reserve_margins`, ERCOT's Capacity, Demand and Reserves report), open for the other grids (the data machine's chain 049, session 895, takes EIA's margins by NERC assessment area). ERCOT's transmission projects have landed (`ercot_transmission_projects`, by county) but no node has a county yet, so "a node's place" and "substations and lines" stay open; large-load tariffs, a load's own wait and a 2026 sub-region table stay open; capacity prices wait on a ruling.

## State on 23 October 2026, day (chain 072)

Read again by session 1059 (chain 072) at about 08:10 UTC on 23 October: **two rows changed state.** A node's county (row 23's first half): **filled for 569 of 873 nodes** (1048, `ercot_node_places`, the data machine's chain 049: the county and load zone ERCOT's CDR gives the units at the node's station); the planned generation near it stays open (the county is known; the sum by county is not built). Transmission projects by county (row 24): **filled for a placed node's county** (1048, `ercot_transmission_projects`, ERCOT's TPIT). A node's wires utility stays open (the CDR names no EIA plant number). Reserve margins by zone (row 36): ERCOT's own filled (1027); the other grids' **open, now for a ruling**: the data machine's table is EIA-411's last release (November 2016), whose 2027 figures are projections made then, so they are named and not drawn (1047, decision 30 of `docs/methods/siting.md`). Substations and lines, large-load tariffs, a 2026 sub-region table and a node's bus stay open (none landed, 1046). The table's rows are left as written; this section says what changed.

## State on 23 October 2026, morning (chain 051)

Read again by session 917 at 08:40 UTC. **The same row as a warehouse table:** "ERCOT nodes | Node panel | transmission projects by county", which chain 072's session 1048 draws on the tab from TPIT, is also held as `ercot_node_transmission` (derived, method `docs/methods/ercot_node_transmission.md`) for the 569 nodes `ercot_node_places` places: each node's county with ERCOT's TPIT project phases counted by status, their circuit miles, highest kV and next projected in-service date. Its counts equal the tab's (`site/data/siting/nodes.json`) in all 137 counties the tab lists; the other 11 have no TPIT phase (zeros in the table, absent from the tab). The other rows stay as chain 072 left them.

## State on 23 October 2026, mid-morning (chain 073)

Read again by session 1081 (chain 073) at about 09:55 UTC: **one row changed state.** A node's county, so the planned generation near it (row 23): **filled** for a placed node's county (1069, `eia860m_planned_generators` by county, ERCOT's generators due in the twelve months after the vintage). No table the other open rows wait on has landed (1068). The table's rows are left as written; this section says what changed.

## State on 23 October 2026, morning (chain 052)

Read again by session 931 at 10:20 UTC. **The same row as a warehouse table, wider:** "a node's county, so the planned generation near it", which chain 073's session 1069 draws on the tab from EIA-860M's generators due in the next twelve months, is also held as `ercot_node_planned_generation` (derived, method `docs/methods/ercot_node_planned_generation.md`) for the 569 nodes `ercot_node_places` places: ERCOT's active queue projects in the node's county (count, MW by solar, wind, storage, gas and other, the earliest proposed in-service date) and EIA-860M's planned generators there. The tab's twelve-month EIA-860M figure is within this table's all-planned figure in all 148 counties (session 936). A project in the county is not a project at the node. The other rows stay as chain 073 left them.

## State on 23 October 2026, midday (chain 053)

Read again by session 945 at 11:28 UTC, after the code machine's session 1086 (chain 074 withdrawn; no row of its changed). **One row filled in part, as a warehouse table:** a node's wires utility, which chain 072 left open because the CDR names no EIA plant number, is held by county as `ercot_node_wires_utilities` (derived, method `docs/methods/ercot_node_wires_utilities.md`) for the 569 nodes `ercot_node_places` places: the utilities EIA-861 lists in the node's county, the delivery-only companies among them (Oncor, CenterPoint, AEP Texas Central and North, Texas-New Mexico Power, Nueces and Lubbock) named apart, and those outside Texas RE. 517 nodes have a delivery-only company in their county, 287 exactly one; 52 (21 in Bexar) are served only by municipal utilities and cooperatives. A utility serving the county may not serve the node's site, and a transmission-only company is in no territory, so the owner of the line a generator ties into is still not given. Substations and lines, large-load tariffs, a 2026 sub-region table and a node's bus stay open.

## State on 23 October 2026, afternoon (chain 054)

Read again by session 959 at 12:58 UTC, after main's last state section (session 945's, chain 053); no code chain has moved a row since. **No row changed state, and none can without a ruling or a key:** a 2026 sub-region table waits on ruling 16 (`siting-rulings-2026-10-23.md`, not ruled); large-load tariffs outside ERCOT wait on `OPENEI_API_KEY`; substations and lines wait on a publisher of record for them (the standing question); a node's hub and bus need ERCOT's settlement point and bus mapping, which ERCOT serves only under `/misdownload`, a path its robots file disallows; a large load's own wait outside NYISO has no public source found. The wires utility stays held by county (`ercot_node_wires_utilities`, session 945).

## State on 23 October 2026, afternoon (chain 055)

Read again by session 986 at 14:13 UTC: no code chain has moved a row since session 959's section, and ruling 16 is not ruled. **No row changed state, and none can without a ruling or a key,** for session 959's reasons. Chain 055's tables (the world outlook, Berkeley Lab's hybrid plants, the National Inventory of Dams, EIA's fleet capacity factors and heat rates, eGRID's subregions) fill no open row.

## State on 23 October 2026, afternoon (chain 056)

Read again by session 2008 at 15:29 UTC: main has moved only by queue files since session 964 landed chain 054 (no code chain's commit), and ruling 16 is still "not ruled" (`siting-rulings-answered.md`). **No row changed state, and none can without a ruling or a key,** for session 959's reasons. Chain 056's tables (energy jobs by state, the NRC's new reactor applications, Reclamation's hydropower plants, population-weighted degree days, BOEM's offshore platforms) fill no open row; ERCOT's large load status, which could have informed a large load's wait in ERCOT, was not found as a data file (session 2002).

## State on 23 October 2026, evening (chain 059)

Read again by session 2051 at 19:20 UTC: main has moved only by the code and portable machines' review and queue sessions since session 2008's section (no commit touches this file or the tab), and ruling 16 is still "not ruled" (`siting-rulings-answered.md`). **No row changed state, and none can without a ruling or a key,** for session 959's reasons. Chain 059's tables fill no open row: NOAA's storm events, the NRC's event reports, DOE's LNG export applications, NOAA's statewide climate and Oak Ridge's transportation tables describe no node, zone, tariff or line; DOE's GRIP selections name states and recipients, not the counties or the ERCOT projects of the "transmission projects by county" row (ERCOT's TPIT or the PUCT's CCN filings). The SEC, which could have given the utilities' capital spending, refused the ERW's reader (session 2049).


## State on 23 October 2026, evening (chain 057)
## State on 23 October 2026, evening (chain 067)
Read again by session 2022 at 19:08 UTC: since session 2008's section main has moved by chain 056's landing (which carried that section), queue files and the code machine's chain 084 (sessions 2102 to 2105: the data-center tracker, the Digest, the deals' rulings), none of which changes a row; ruling 16 is still "not ruled" (`siting-rulings-answered.md`). **No row changed state, and none can without a ruling or a key,** for session 959's reasons. Chain 057's tables (ICE's hub indices, held internal; Tracking the Sun's distributed solar by state; EIA's manufacturing, commercial buildings and household surveys; EIA's LNG export projects) fill no open row: none is a large-load tariff, a zone's reserve margin, a substation or a large load's own wait.
Read again by session 2078 at 20:25 UTC, after main's newest section (chain 057's session 2022, landed with chain 057): ruling 16 is still "not ruled" (`siting-rulings-answered.md`). **No row changed state, and none can without a ruling or a key,** for session 959's reasons. Chain 067's tables fill no open row: Ontario's and Alberta's hourly loads are beside the U.S. grids, not in a row of the tab; EPA's GHGRP facilities and NOAA's billion-dollar disasters describe no node, zone, tariff or line. JODI (needs permission) and the Energy Institute (refused the reader) were not taken.
