# The All grids tab: chain 050's open items, in one table (23 October 2026)

Energy Research Warehouse (ERW), session 722 of chain 062 (`queue/done/062-day-23-october-code-allgrids-2.md`), written on portable-laptop on 22 October 2026 at about 13:30 UTC. Chain 050 (`queue/done/050-night-23-october-code-allgrids.md`, sessions 700 to 721) built the All grids tab of `/cost-of-power`. This file lists every item its reports (`archive/sessions/SESSION_700_REPORT.md` to `SESSION_721_REPORT.md`), its note (`docs/state/review_2026-10-24_code.md`), the lab's walk (`docs/reviews/siting-path.md`) and the reads review (`docs/reviews/siting-reads-2026-10-22.md`) left open, one a line, so that each later session of chain 062 names the line it closes.

Three kinds:

- **ruling**: a question only the owner answers. Chain 062 decides none of these; session 741 writes each in plain words with what each answer would change (`docs/reviews/siting-rulings-2026-10-23.md`).
- **gap**: a cell the warehouse cannot fill until a table lands (`docs/reviews/siting-gaps.md`); the data machine's chains 043 and 044 pull them. A session whose table has not landed says "none there" and moves on.
- **work**: something a session of this chain does from what is already held.

"Closes" names the session of chain 062 whose section takes the item; "none" means no session of this chain is written for it. The "State" column is kept by the sessions that touch an item.

## The table

| # | Item | Session | Kind | Closes | State |
|---|---|---|---|---|---|
| 1 | Sessions 719 to 721 never landed: `wip/721-allgrids` on the remote, no `task/` branch, 721's report says "Below, once done" | 721 | work | 722 | see 722's report |
| 2 | The old laptop's worktrees `erw-719` to `erw-721` and its branch `wip/721-allgrids` are removed once the branch lands (its machine; this one cannot reach them) | 721 | work | none (the old laptop's next session) | open |
| 3 | Whether "Grid by grid" should be retired now that All grids exists | 700 | ruling | 741 | open |
| 4 | The profiles' open defaults: flexible compute's strike (USD 1,000), the electrolyzer's 0.55 and its strike (the row's k-th cheapest hour) | 700 | ruling | 741 | open |
| 5 | ISO-NE's and NYISO's prices are "license needed" since 20 October 2026 in `site/data/license_status.json`, yet "Your load" and so this tab draw them; both views change together if they should be held | 701 | ruling | 741 | open |
| 6 | Whether a grid's emergency notices (CAISO's are held) count as heavy industry's interruptions where held | 702 | ruling | 741 | open |
| 7 | `texas_transmission_matrix` is internal in coverage, yet "Your load" and this tab show its rate | 703 | ruling | 741 | open |
| 8 | Whether any capacity figure may be shown (NYISO's spot rows are marked public row by row, its prices held since 20 October) | 704 | ruling | 741 | open |
| 9 | Whether the computed capacity figures belong in a private place a reviewer can read under the internal cookie | 704 | ruling | 741 | open |
| 10 | The gaps file gains connection timelines by utility, ERCOT's 75 MW rule as a held row, a controllable load's path | 705 | work | closed by 713 | closed |
| 11 | A zone's own demand growth from `eia930_subba_demand_hourly` (held, with its yearly tables; not in the tab's files) for NYISO's and ISO-NE's zones and ERCOT's weather zones | 706, the walk's step 4 | work | 728 | open |
| 12 | Whether the annual carbon figure should be consumption-based too (EIA-930's monthly intensity, as "Your load" draws it), so both figures are of one measure | 707 | ruling | 741 | open |
| 13 | Service territories, so a row names its own utility | 708, 713's gap 4 | gap | closed by 718 (`utility_service_territories`) | closed |
| 14 | A node's zone and settlement hub: ERCOT's settlement point mapping (NP4-160) | 709, 713's gap 3, the walk's step 7 | gap | 733 | open |
| 15 | A node's wires utility and county: ERCOT's resource registration | 709, 711, 713's gap 3 | gap | 733 | open |
| 16 | The transmission projects by county near a node (the PUCT's CCN filings or ERCOT's TPIT) | 711 | gap | 732 (lines and substations where held; the projects stay a gap) | open |
| 17 | What "load band" means, if not an energy band | 710 | ruling | 741 | open |
| 18 | Whether the tab's files should be rebuilt by the data machine's daily run, so the tab never lags the live set | 712 | ruling | 741 | open |
| 19 | The large-load tariffs outside ERCOT (transmission, six grids), the first of the five gaps | 713's gap 1, the walk's steps 1, 2 and 6 | gap | 730 | open |
| 20 | The capacity prices, shown: a permission from PJM, ISO-NE and NYISO, or MISO's terms reviewed, the second of the five gaps | 713's gap 2 | ruling | 741 | open |
| 21 | A large load's own wait outside NYISO (the utilities' and ISOs' large-load queues), the fifth of the five gaps | 713's gap 5, the walk's step 3 | gap | none (no table of it is in chain 043's or 044's plan) | open |
| 22 | The page's weight: the hub table is about 1.7 MB of HTML; whether to shorten the tips to bring it under 1 MB | 714, 716, the walk | ruling | 737 (prepares the variant on `wip/737-tips-variant`, not landed; 741 names it) | open |
| 23 | What can shrink without changing a word (repeated markup, an attribute, a duplicate payload) | 716 | work | 737 | open |
| 24 | The brand screenshots of the restyle (`docs/brand/review-715/`) and of each session's folder, for the owner to rule from | 715 | ruling | 741 (listed, not decided) | open |
| 25 | Whether Texas's wires utilities (CenterPoint, Oncor, AEP Texas, TNMP) should be priced from their tariffs in the Utility column for ERCOT rows, in place of a retail seller | 718 | ruling | 741 | open |
| 26 | A Texas wires utility's own revenue (CenterPoint files no sales row in `eia861_utility_sales`) | 718's gaps row | gap | none | open |
| 27 | Whether the tab may name a tracked facility as A once `datacenter_facilities` is public again (one read of the live set, or a site file built from the public rows) | 719 | ruling | 741 | open |
| 28 | The tracker's facilities placed by their utility where the tracker names one (141 of 422 were placed by county or state) | 719 | work | 729 | open |
| 29 | The map: nothing held places a hub or node on a map (ERCOT's resource registration would) | the note | gap | none (733 names what a node's place would allow) | open |
| 30 | Migration 036 (session 580's two partial indexes) written and not applied: the tab reads no database, so it needs none | 716, the note | ruling | 739 (an index a read needs goes into the file, not applied) | open |
| 31 | Reserve margins by zone | 706's "not held", the gaps file | gap | 731 | open |
| 32 | Substations and transmission lines near a node (HIFLD, the data machine's chain) | the gaps file's last row | gap | 732 | open |
| 33 | ISO-NE's median months to connect (no request online 2023 to 2025 with both dates in Berkeley Lab's file) | 705, the gaps file | gap | none | open |
| 34 | The four peaks of summer 2026 (ERCOT publishes them by 1 December 2026) and the 2026 transmission rate (docket 59080, filed, not approved) | 703, the gaps file | gap | none (the data machine's connectors, when published) | open |
| 35 | "Your load"'s paging asks one page past the end of two tables (the hourly carbon at offsets 11,000 and 12,000, the adders at 2,000 to 4,000): not the tab's, listed for whoever next touches `lib/datacenter/answers.ts` | 716 | work | none (outside this chain's files) | open |
| 36 | The lab's path again on production with 718's tables, 719's link and 720's card in place | 717 | work | 727 | open |
| 37 | The replication extended to every figure a later session adds | 712 | work | 735 | open |

## How this file is kept

- A session that closes a line writes "closed by N" in its State column and says so in its report under "Read these first".
- A session whose table has not landed leaves the line open and writes "none there (session N)" in State.
- No line of kind ruling is decided by a session: session 741 writes each in plain words for the owner.
