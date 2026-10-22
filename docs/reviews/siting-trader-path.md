# A power trader's path through the All grids tab, walked (22 October 2026)

Energy Research Warehouse (ERW), session 723 of chain 062, on samueloldlaptop. The walk ran on production (`https://erw-flame.vercel.app`, chain 050's sessions 700 to 721, served since 14:56 UTC) in the internal view, on 22 October 2026 at about 15:05 UTC. The load is **1 GW** (1,000 MW), the datacenter profile unless a step says otherwise.

The page is `/cost-of-power?view=allgrids`, and every input is in the address, so each step below is an address. Screenshots are in `docs/brand/review-723/` (`tNN_<step>_1280.png`, two at 390 by 844); the page's visible text at each step stayed on this machine (`runs/chain_062/walk723/`), since it carries figures still waiting on a ruling (NYISO's and ISO-NE's prices). Nothing was fixed in this session; session 724 fixes what lies in the chain's files.

## The questions

A trader asks where a load's energy is cheap, how it moves, and what the curtailment and the peaks are worth:

1. **Which ERCOT nodes are cheapest and dearest, and by how much against the hub?**
2. **Which nodes have the widest basis, and how much does it move from day to day?**
3. **One node in detail.**
4. **Two places side by side: a node against its hub, a hub against a hub.**
5. **What does a flexible load give up, and what does it save, at the peaks and above a strike?**
6. **What is the four-peak charge, and where does it apply?**
7. **Day-ahead against real time.**
8. **Can I take the numbers away?**

## The walk, step by step

| # | The address (after `/cost-of-power?view=allgrids&mw=1000`) | What the page showed | Answered? |
|---|---|---|---|
| 1 | `&rows=nodes&nsort=energy&ndir=asc` (t01) | BBREEZE_1_2 and ELSAUZ_ALL (wind) cheapest at USD 23.83 per MWh, basis -10.47, all-in 31.66, then PENA_ALL and TGW_T1_T2 at 24.90. The shared line above the list (the four-peak charge, no capacity market, 45.80 months, +5.41 percent, 332.87 kg) | **Yes** |
| 2 | `&rows=nodes&nsort=energy&ndir=desc` (t02) | PALACIOS_RN (storage) dearest at 52.48, basis +18.17, all-in 60.30; RUSSEKST_RN 52.31 | **Yes** |
| 3 | `&rows=nodes&nsort=basis&ndir=asc` and `desc` (t03, t04) | **The same order as steps 1 and 2.** Every node's energy is HB_HUBAVG's plus its basis, so the two sorts cannot differ. The basis's spread over days (10th to 90th percentile), which says how far a node moves, is in a node's panel only: no column, no sort | **No.** A trader cannot find the widest-moving nodes |
| 4 | `&rows=nodes&node=ercot%3ABBREEZE_1_2` (as session 711) | The panel: the three percentiles, twelve months, the items not held | **Yes** |
| 5 | Every node's "Days held" (t01 to t04) | **Every node reads "335 of 365".** `node_basis_daily` holds no day from 21 August to 19 September 2026 (30 days, every node; checked on the archive's copy). The column's tip does not say which days are missing | **In part.** The count is right; the gap is not named |
| 6 | Steps 1 and 3: two nodes with the same figures | BBREEZE_1_2 and ELSAUZ_ALL, PENA_ALL and TGW_T1_T2 read the same to the cent in every column. Nothing says so | **In part**: a fact the page could state, not an error |
| 7 | `&a=ercot%3AHB_WEST&b=ercot%3AHB_HOUSTON` (t06) | The headline (HB_WEST, USD 40.83, USD 321,907,123 a year) and the panel: energy +2.22 B less A, utility +15.82 | **Yes** |
| 8 | `&a=ercot%3ABBREEZE_1_2&b=ercot%3AHB_WEST` (t07): a node as A, typed into the address | **The tab answers**: the headline at BBREEZE_1_2, USD 31.66 all-in, USD 249,599,764 a year, and the panel against HB_WEST (+9.17). **But nothing on the page sets a node as A**: the box's A and B lists hold the 48 hub and zone rows only, so the A list shows "none" here, and pressing Show drops the node. The node panel has no "set as A" | **In part.** It works only for a reader who edits the address |
| 9 | `&profile=flexible&sort=allin&dir=asc` (t08) | HB_WEST all-in 30.64 against 40.83 flat (session 717's step 6), the hours lost in the tip | **Yes** |
| 10 | `&profile=flexible&strike=100&sort=allin&dir=asc` (t11) | HB_WEST 26.66, "off 214 h" at a strike of USD 100; the four-peak charge 0.00 off at the peaks, 8.02 firm | **Yes** |
| 11 | `&profile=flexible&rows=nodes&nsort=allin&ndir=asc` (t09) | BBREEZE_1_2 21.78 energy and all-in (no four-peak charge for a load off at the peaks) | **Yes** |
| 12 | `&sort=transmission&dir=asc` (t10) | ERCOT's rows 7.83 (firm 7.83, off 0.00); every other grid "not held" | **Yes** for ERCOT; elsewhere the gap is said |
| 13 | `&sort=energy&dir=asc` (t05) | CAISO's SP15 cheapest day-ahead at 28.94, "rt 28.59" beside it; SPP and ERCOT's rows likewise where real time is held. **No sort by real time** and no day-ahead less real-time figure; the node list has no real time at all (the node table is daily day-ahead basis) | **In part** |
| 14 | Any list | **No download.** The node list's 873 rows, or the hub table, cannot be taken away as a file; the research card (session 720) has a CSV, the tab has none | **No** |
| 15 | `&rows=nodes...` at 390 (t12) and the hub table at 390 (t13) | The box folds under "Your load"; the list scrolls inside its frame; no sideways scroll (390 wide) | **Yes** |
| 16 | Looking for a node by name in the list | **No search or filter**: the list is 873 rows, virtual, sorted by a column; a trader who knows a node's name scrolls, or types `&node=` in the address | **No** |

## What session 724 fixes (inside the chain's files)

1. **A spread column in the node list**: the basis's 10th to 90th percentile spread over the node's days (from `nodes.json`'s percentiles, the panel's own figures), sortable, with its key and tip (step 3).
2. **The missing days named**: the "Days held" tip and the list's header line say which days the node table lacks (step 5), from the node file's own days.
3. **A node as A or B from the page**: the node panel gains "Set as A" and "Set as B"; the box's A and B lists hold the current node when one is set, so Show keeps it (step 8).
4. **A name filter for the node list**, kept in the address (step 16).
5. **A download of the node list** as the visible rows, in the page's own figures (step 14). Session 724 decides its form: a CSV made in the browser from the rows already on the page needs no new route.

Left as found, each listed: two nodes with the same figures (step 6: a fact the page could state, noted for 733 where a node's place is read); a sort by real time (step 13: real time is held for some hubs only and for no node, a ruling on what the column means).

## For the data machine

- `node_basis_daily` holds no day from 2026-08-21 to 2026-09-19 for any node (30 days). The tab says "335 of 365"; the gap may be a source gap or a missed backfill.

## After session 724

The failed steps walked again on a local build of `wip/724-allgrids` (shots: `docs/brand/review-724/`).

| # | Before (723) | After (724) |
|---|---|---|
| 3 | Energy and basis sort the same; the spread only in a panel | A "Basis spread" column (90th percentile less 10th of the daily basis, the panel's own figures), keyed `allgrids|nodespread|<node>`, sortable. Widest: RUSSEKST_RN 57.55, OLNEYTN_AGR1 57.11, OLNEYTN_RN 55.74 (`after_t03_spread_widest_1280.png`). The basis column's tip says it sorts as Energy does |
| 5 | "335 of 365", the gap not named | The line above the list: "node_basis_daily lacks days in 2026-08 (20 of 31 days held), 2026-09 (11 of 30 days held), for every node", from the node file's own days by month (`after_t05_days_named_1280.png`) |
| 8 | A node as A only by editing the address | The node panel has "Set as A" and "Set as B"; the box's A and B lists keep a node set as A or B ("ERCOT BBREEZE_1_2 (node)"), so Show keeps it (`after_t08_panel_set_a_1280.png`, `after_t08_node_as_a_1280.png`) |
| 14 | No download | "Download these N rows (CSV)" above the list: the rows shown, in the page's own figures, with a header naming the tab, the load, the table and the method; made in the browser, no new route |
| 16 | No search | "Find a node by name", kept in the address (`nq`): `&nq=SOLAR` shows 3 of 873 nodes (`after_t16_find_1280.png`, and at 390) |

## Walked again (session 757, chain 063)

The sixteen steps again on production (chains 050, 062 and 063's 744 to 756 served), 22 October 2026 at about 19:22 UTC, with three steps for what 724 and 746 added. Shots: `docs/brand/review-757/`.

| # | Then (723) | Now (757) |
|---|---|---|
| 1, 2 | Cheapest and dearest nodes | The same (BBREEZE_1_2 23.83; PALACIOS_RN 52.48) |
| 3 | Energy and basis sorted the same; no spread | The basis column's tip says so; "Basis spread" and "Intraday swing" sort the nodes by how they move |
| 4 | A node's panel | The same, with its intraday swing and "Set as A" and "Set as B" |
| 5 | "335 of 365", the gap not named | The list's line names 2026-08 and 2026-09 |
| 6 | Two nodes with the same figures | The same, as left |
| 7 to 12 | Hub against hub; flexible at the peaks and above a strike; the four-peak charge | The same figures |
| 8 | A node as A only by the address | Set from the panel, kept by the box's lists |
| 13 | No sort by real time | As left (rulings item 15, not ruled) |
| 14 | No download | "Download these N rows (CSV)", with the swing |
| 15 | The 390 layout | The same |
| 16 | No search | "Find a node by name": `nq=RN` shows 406 of 873 |
| new | | **One fault**: the sort line read "Sorted by basis to hb_hubavg", the hub's name lowercased with the heading. Only the first letter is lowered now (test 757) |

## Walked again (session 778, chain 064)

The 17 steps (757's sixteen and the class filter) again on production (chain 064's 766 to 777 served since 21:30 UTC), 22 October 2026 at about 21:33 UTC. Shots: `docs/brand/review-778/`.

- **Every figure the walk reads is the same** as at session 757's walk: each step's figure lines compared, 0 differing.
- **757's fix is served**: "Sorted by basis to HB_HUBAVG". **772's class filter**: the storage nodes alone, 238 of 873, by their swing.
- **No step fails and no new fault was found.**
