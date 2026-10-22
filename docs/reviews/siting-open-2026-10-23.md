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
| 25 | The tracker's facilities not placed by county or state (281 of 422 on the warehouse's copy) | 719 | work | |

The walk of session 717 (`docs/reviews/siting-path.md`) left no item of its own beyond 7, 11, 15 and 16; session 727 walks it again.
