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

## State on 23 October 2026, morning (chain 051)

Read again by session 917 at 08:40 UTC. **One row filled for the nodes placed:** "ERCOT nodes | Node panel | transmission projects by county" is filled by `ercot_node_transmission` (derived, method `docs/methods/ercot_node_transmission.md`) for the 569 nodes `ercot_node_places` places: each node's county with ERCOT's TPIT project phases counted by status, their circuit miles, highest kV and next projected in-service date. Not yet drawn on the tab. Chain 049 has landed since chain 071's reading above: `ercot_node_places` gives 569 nodes a county and zone, the base of this table, and `eia411_capacity_margins_annual` gives reserve margins by NERC assessment area, to 2016 actual. The other rows stay as chain 071 left them.
