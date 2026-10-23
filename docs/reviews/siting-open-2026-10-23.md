# The All grids tab: chain 050's open items, 23 October 2026

Session 722 (chain 062, `queue/done/062-day-23-october-code-allgrids-2.md`). One line per item still open from chain 050's reports (`archive/sessions/SESSION_700_REPORT.md` to `SESSION_721_REPORT.md`) and its note (`docs/state/review_2026-10-24_code.md`).

- **Kind**: a **ruling** is the owner's and no session decides it; a **gap** is data the warehouse does not hold; **work** is for this chain.
- **Closed by**: the session of chain 062 that names the line in its report, filled in as each closes.

| # | Item | From | Kind | Closed by |
|---|---|---|---|---|
| 1 | Whether "Grid by grid" should be retired now that All grids exists | 700 | ruling | |
| 2 | The profiles' open defaults: flexible compute's strike, the electrolyzer's 0.55 and its strike | 700 | ruling | |
| 3 | ISO-NE's, MISO's and NYISO's prices are "license needed" since 20 October, yet "Your load" and the tab draw NYISO's and ISO-NE's | 701 | ruling | |
| 4 | Whether a grid's emergency notices (CAISO's held) count as heavy industry's interruptions | 702 | ruling | |
| 5 | `texas_transmission_matrix` is internal in coverage, yet "Your load" and the tab show its rate | 703 | ruling | |
| 6 | Whether any capacity figure may be shown, and whether the computed ones belong in a private place a reviewer can read | 704 | ruling | |
| 7 | Large-load tariffs outside ERCOT (transmission for six grids, a delivery charge for every grid) | 705, 713 | gap | |
| 8 | A large load's own wait outside NYISO (utilities' and ISOs' large-load queues) | 705, 713 | gap | |
| 9 | A zone's own demand growth from `eia930_subba_demand_hourly` (held, not in the tab's files) | 706 | work | 728 (NYISO's and ISO-NE's 19 zones; ERCOT's and CAISO's rows keep the grid's) |
| 10 | Whether the annual carbon should be consumption-based too | 707 | ruling | |
| 11 | ERCOT's settlement point mapping and resource registration: a node's zone, hub, wires utility and county | 709, 711, 713 | gap | |
| 12 | Transmission projects near a node (substations, lines, CCN filings) | 711 | gap | |
| 13 | What "load band" means, if not an energy band | 710 | ruling | |
| 14 | Whether the tab's files should be rebuilt by the data machine's daily run, so the tab never lags the live set | 712 | ruling | |
| 15 | The capacity prices, shown: a permission from PJM, ISO-NE and NYISO, or MISO's terms reviewed | 713 | gap and ruling | |
| 16 | The page's weight: the hub table is about 1.7 MB of HTML; shorter tips would bring it under 1 MB | 714, 716 | ruling (tips), work (what shrinks without a word changed) | |
| 17 | The brand shots of the restyle, `docs/brand/review-715/` | 715 | ruling | |
| 18 | Whether Texas's wires utilities should be priced from their tariffs in the Utility column | 718 | ruling | |
| 19 | Whether the tab may name a tracked facility as A once `datacenter_facilities` is public again | 719 | ruling | |
| 20 | Reserve margins by zone, beside capacity above the peak | 713 (gaps) | gap | |
| 21 | The map: nothing held places a hub or node on a map | 721 | gap | |
| 22 | Migration 036 (session 580's indexes) written, not applied; the tab needs none | 716, 721 | ruling | |
| 23 | Production serves 719 to 721 (`0787ad72`, Vercel rate limited at 13:44 UTC on 22 October), and the second after snapshot | 721 | work | 722 |
| 24 | 721's landing record (`wip/721-records`) and the queue's taking of 062 (a local commit on main) reach main | 721, 722 | work | |
| 25 | The tracker's facilities not placed by county or state (281 of 422 on the warehouse's copy) | 719 | work | 729: explained, nothing placed (153 have no US state; 128 are in states no one grid holds at 85 percent; 3 name a utility, each a holding company's name) |

The walk of session 717 (`docs/reviews/siting-path.md`) left no item of its own beyond 7, 11, 15 and 16; session 727 walks it again.

## State after chains 062 to 065 (session 975, 23 October 2026 at about 00:15 UTC)

Each line above, read against chains 062 (722 to 743), 063 (744 to 765), 064 (766 to 787) and 065 (788 to 799, 970 to 977). A ruling's number in `docs/reviews/siting-rulings-2026-10-23.md` is given as "rulings 1"; none of them is answered (session 974). "Data chain 045" and "data chain 046" are the data machine's queue files of 22 October evening and night (`queue/done/045-evening-22-october-data-resumed.md`, `queue/next/046-night-22-october-data-sources-gaps.md`); neither has landed a table the tab waits on.

| # | State | Closed by, or what it waits on |
|---|---|---|
| 1 | open | a ruling (rulings 1) |
| 2 | open | a ruling (rulings 2) |
| 3 | open | a ruling (rulings 3) |
| 4 | open | a ruling (rulings 4) |
| 5 | open | a ruling (rulings 5) |
| 6 | open | a ruling (rulings 6) |
| 7 | open | a table, `utility_large_load_tariffs`, whose connector waits on the owner's key (`OPENEI_API_KEY`, rulings 18); the tab's side is written and tested, not wired (730) |
| 8 | open | a table: none held or queued gives a load's own wait outside NYISO, whose alone is drawn |
| 9 | closed | 728 (NYISO's and ISO-NE's 19 zones); ERCOT's and CAISO's rows keep the grid's figure, and a 2026 year waits on a table (rulings 16) |
| 10 | open | a ruling (rulings 7) |
| 11 | open | a table: ERCOT's settlement point mapping (`ercot_settlement_points`, data chain 046's session 850) for a node's zone and hub; its wires utility and county wait on the resource registration, which no chain has queued |
| 12 | open | tables: substations and lines (`hifld_substations`, `hifld_transmission_lines`, data chain 045's sessions 692 and 693, if its 691 allows), ERCOT's transmission projects (data chain 046's session 852) |
| 13 | open | a ruling (rulings 8); the energy band and the filter by kind stand meanwhile (710) |
| 14 | open | a ruling (rulings 9) |
| 15 | open | a ruling (rulings 6) and a permission from PJM, ISO-NE and NYISO, or MISO's terms reviewed |
| 16 | work closed, ruling open | the work by 737 (the hub table from 1.82 MB to 1.59 MB without a word changed; 777 made the node list a third lighter; 1.60 MB at 972 with 793's download); the tips' length waits on a ruling (rulings 10) |
| 17 | open | a ruling (rulings 11) |
| 18 | open | a ruling (rulings 12) |
| 19 | open | a ruling (rulings 14), and `datacenter_facilities` public again (held whole since 21 October) |
| 20 | open | a table: ERCOT's reserve margins (`ercot_cdr_reserve_margins`, data chain 046's session 851); the other grids' on a source not yet queued |
| 21 | open | a table: nothing held places a hub or node on a map; the settlement point mapping (11) and the substations (12) are its first steps |
| 22 | open | a ruling (rulings 19); the tab reads no database (972) |
| 23 | closed | 722 |
| 24 | closed | 722 (the queue's taking pushed at 14:52 UTC; 721's record landed with 722 to 730) |
| 25 | closed | 729 (explained; nothing placed) |

**Lines opened by chains 062 to 065**, each still open:

| # | Item | From | Kind | Waits on |
|---|---|---|---|---|
| 26 | A retailer named as the utility where a state's largest seller to industry is energy-only | 725 | ruling | rulings 13 |
| 27 | Real time in the sort (day-ahead less real time) | 723 | ruling | rulings 15 |
| 28 | A 2026 sub-region table, so a zone's growth takes the grid's twelve months | 728 | ruling and table | rulings 16, then the data machine |
| 29 | The tracker's operating utility | 729 | ruling | rulings 17 |
| 30 | Which parts of the personal laptop's run of chain 062 to take (its 728's ERCOT weather zones above all, 796) | 741, 796 | ruling | rulings 20 (`siting-rulings-answered.md`) |
| 31 | The shared time chart's month labels | 798 | ruling | rulings 21 |
| 32 | The shared card renderer's x labels on a narrow chart | 970 | ruling | rulings 22 |
| 33 | The 21 October Digest's WTI for 14 October: the issue prints 101.91 and `eia_fuel_spot_prices` now reads 96.34, a source's revision; check-values fails it on production and on every build since | 730 | not this tab's page | the owner of `/digest` (a note of the revision, or a check that knows of revisions) |

Of the 33 lines, 4 are closed (9, 23, 24, 25) and 29 open: 22 wait on a ruling (16 for its ruling part only; 15 on a permission too; 28 on a table after it), 6 on a table (7, 8, 11, 12, 20, 21; 7 through the owner's key), 1 on another page's owner (33).

## State after chain 071 (session 1039, 23 October 2026 at about 07:40 UTC)

Read against chain 071's sessions 1020 to 1038 (`queue/done/071-night-23-october-code-allgrids-packages.md`). No ruling is answered (1021). Two of the tables the open lines waited on have landed (`ercot_cdr_reserve_margins`, `ercot_transmission_projects`, the data machine's chain 046); the others have not (1025).

| # | State | Closed by, or what it waits on |
|---|---|---|
| 11 | open | a table: a node's zone and hub (`ercot_settlement_points`, not landed, 1026), or a node's county and zone from the data machine's chain 049 session 901 (chain 072, session 1048) |
| 12 | open | a node's county first (line 11), then ERCOT's transmission projects in that county (landed, by county, 1028) and the HIFLD substations and lines (not landed) |
| 20 | **closed for ERCOT** | 1027 (ERCOT's Capacity, Demand and Reserves report, summer 2027 at the peak load hour); the other grids wait on the data machine's chain 049 session 895 (EIA's margins by NERC assessment area; chain 072, session 1047) |
| 21 | open | a node's county (line 11), at the county's resolution (chain 072, session 1049) |

Every other line stands as session 975's table above says: 1 to 6, 10, 13 to 15, 17 to 19, 22 and 26 to 32 wait on their rulings, 7 on the owner's OpenEI key, 8 and 28 on a table, 16 on its ruling part, 33 on `/digest`'s owner (chain 072's session 1061 writes a proposal for it). Of the 33 lines, 4 are closed and 1 closed in part (20); 28 stay open.

## State after chain 072 (session 1060, 23 October 2026 at about 08:10 UTC)

| Line | State | Since |
|---|---|---|
| 11 | **closed in part** | 1048: a node's county and load zone for 569 of 873 nodes (`ercot_node_places`); its hub and wires utility stay open (`ercot_settlement_points` not landed; the CDR names no plant number) |
| 12 | **closed in part** | 1048: ERCOT's transmission project phases in a placed node's county, counted by status, the earliest named; substations and lines wait on the HIFLD tables (not landed) |
| 20 | **closed for ERCOT**; the rest wait on a ruling | 1047: the data machine's table is EIA-411's of 2016, named and not drawn; rulings item 23 |
| 21 | open, designed | 1049: a county map, no node as a point; rulings item 24 |
| 33 | open, proposed | 1061: `docs/reviews/digest-revisions-proposal.md` for `/digest`'s owner |

Every other line stands as session 1039's section says. Of the 33 lines, 4 are closed and 3 closed in part (11, 12, 20); 26 stay open.
