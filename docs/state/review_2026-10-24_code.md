# The chain of 23 October 2026 on the old laptop (050): the note for Samuel

Energy Research Warehouse (ERW), session 721, written on the old laptop (samueloldlaptop) on 22 October 2026 at 13:15 UTC. Chain 050 (`queue/done/050-night-23-october-code-allgrids.md`, sessions 700 to 721) built the **All grids** tab of `/cost-of-power` ("What a datacenter pays"). It answers what a large load pays, when it connects and how clean the power is, for every grid, hub and zone the warehouse holds (48 rows) and every ERCOT node (873), with "Your load"'s own model and keys. Each session worked in its own worktree (`C:\Users\lossa\Documents\erw-7NN`) on `wip/7NN-allgrids`, one cut from the other. Model spend USD 0 for the whole chain; no warehouse data written; no request to a publisher. The only reads were the ERW's own archive bucket (tables rebuilt into `runs/archive_restore/`), the live set with the anon key and the site's own pages.

## First: what to know

1. **Three landings, every one with 0 differences on the 25 snapshot pages** (every page is in review):
   - 700 to 705 at 10:09 UTC (`b25a5c66`);
   - 706 to 712 at 11:24 (`8a54e3b4`; Vercel said "rate limited" and deployed 30 minutes later);
   - 713 to 718 at 13:01 (`e39de81a`).
   - 719 to 721 land with this note, in one push (721's report).
2. **`datacenter_facilities` is held whole** (license needed since 21 October 2026). Session 719 learned this at its checks, after its first version had written the counties of tracked facilities, and then their names, operators and MW, into a site file. Neither version was ever pushed: the branch was recut over 718's tip.
   - The tracker's link to the tab is now built from public tables only (`eia861_utility_sales`, `utility_service_territories`).
   - While the hold stands the tracker shows no facility, so no link shows.
3. **The tab reads no database** (session 716, `tests/test_session716.py`). The capacity prices are computed where held and drawn as "license needed" in place (session 408's rule). ISO-NE's, NYISO's and MISO's energy prices are drawn as "Your load" draws them (701, for your ruling).
4. **Nothing waits in `queue/next` for this machine**, so session 721 wrote the next file, `queue/next/062-day-23-october-code-allgrids-2.md` (sessions 722 to 743, below), committed it and pushed it to main.

## What each session did

| Session | Branch | What it did | Address to open (internal view) | Shots |
|---|---|---|---|---|
| 700 | `wip/700-allgrids` | the tab, its 48 rows and 873 nodes, the four profiles, the column heads, the method note v0 | `/cost-of-power?view=allgrids` | `docs/brand/review-700/` |
| 701 | `wip/701-allgrids` | energy: twelve months day-ahead (real-time beside), a node as hub plus basis, the sparkline | the same, the Energy column | `review-701/` |
| 702 | `wip/702-allgrids` | the profiles' math: hours run, the four peaks, the strike, hours lost | `&profile=flexible` | `review-702/` |
| 703 | `wip/703-allgrids` | transmission: ERCOT's four-peak charge, firm against curtailing; the all-in column | the Transmission column | `review-705/` |
| 704 | `wip/704-allgrids` | capacity: "no capacity market" or "license needed" in place | the Capacity column | none of its own (705's show the column) |
| 705 | `wip/705-allgrids` | time to connect: queue months, the large-load rules and approvals | the Time to connect column | `review-705/` |
| 706 | `wip/706-allgrids` | headroom: demand growth, planned MW, capacity over peak | `&sort=headroom` | `review-706/` |
| 707 | `wip/707-allgrids` | carbon: annual (eGRID) and over the load's hours (EIA-930) | `&sort=carbon` | `review-707/` |
| 708 | `wip/708-allgrids` | the utility: industrial revenue per MWh and its growth | `&sort=utility` | `review-708/` |
| 709 | `wip/709-allgrids` | the ERCOT node set: a virtual list, the shared figures drawn once | `&rows=nodes` | `review-709/` |
| 710 | `wip/710-allgrids` | the screen, A against B, the headline, the year's cost | `&sort=allin&a=ercot%3AHB_HUBAVG&b=nyiso%3AN.Y.C.` | `review-710/` |
| 711 | `wip/711-allgrids` | a node's panel: basis percentiles, twelve months | `&rows=nodes&node=ercot%3A7RNCHSLR_ALL` | `review-711/` |
| 712 | `wip/712-allgrids` | the method note v1; the replication (81 figures, 0 differ) | `/data/methods/siting` | none of its own (it took 706 to 711's on its build) |
| 713 | `wip/713-allgrids` | the gaps, complete (29 rows), and their internal page | `/internal/siting-gaps` | `review-713/` |
| 714 | `wip/714-allgrids` | 390 pixels, AccessLint (7,460 findings to 0), tips by keyboard | the tab at 390 | `review-714/` |
| 715 | `wip/715-allgrids` | the brand pass: words sans, figures mono, tips in fog | the tab, any tip | `review-715/` |
| 716 | `wip/716-allgrids` | the reads: the tab makes none; 1.7 MB of HTML listed | `docs/reviews/siting-reads-2026-10-22.md` | none |
| 717 | `wip/717-allgrids` | the lab's path, walked in ten steps; the sorted column first | `docs/reviews/siting-path.md` | `review-717/` |
| 718 | `wip/718-allgrids` | the data machine's tables wired in: durations, capacity over peak for every grid, the county's utility | `&sort=utility` | `review-718/` |
| 719 | `wip/719-allgrids` | the tracker links each facility to its row, its MW as the load (public tables only) | `&mw=1400&a=ercot%3ALZ_NORTH` | `review-719/` |
| 720 | `wip/720-allgrids` | the research card: where a gigawatt pays least (ERCOT HB_WEST, USD 40.83 per MWh) and most (LZ_CPS, 46.69) | `/research/card/siting_gigawatt` | `review-720/` |
| 721 | `wip/721-allgrids` | this note, the next file, the landing, the queue | this file | none |

Every address is on `https://erw-flame.vercel.app`, after `/internal/open`; the `&...` ones follow `/cost-of-power?view=allgrids`.

## Decisions made without you

Each report lists its own; the ones that shape the tab:

1. **All grids is a third view** of `/cost-of-power`; "Grid by grid" stays (700). The profile dropdown is in the tab's own box, so no default of "Your load" moves (700); `site/scripts/check-existing-tab.mjs` proved it every session.
2. **PJM is one row ("the grid")**, since no PJM hub or zone price is held; MISO's 8 hubs are rows with the existing tab's words (700).
3. **A node's price is its hub's twelve-month mean plus its mean daily basis** (700, 701); a node is charged transmission on its hub's hours (703).
4. **The profiles' defaults the prompt left open**: flexible compute's strike USD 1,000, the electrolyzer's 0.55 and its strike as the row's k-th cheapest hour (700, 702). Heavy industry runs every hour; "interruptible" moves capacity, not energy (702).
5. **Transmission is "Your load"'s newest approved rate**, matrix A (703). CAISO and SPP have no all-in figure: their transmission is not held (703).
6. **No internal price in the public repository**: capacity computed where held, drawn "license needed" (704). NYISO's load queue not drawn (705).
7. **Time to connect is a generator's months, request to operation**, 2023 to 2025 online (705); since 718 from `interconnection_durations`.
8. **Carbon is generation-based annually (eGRID) and consumption-based by hour (EIA-930)**, each tip says which (707).
9. **A hub takes a state for its utility** (708), and since 718 a row named for a place takes its county's utilities inside its grid.
10. **"Load band" is read as an energy band** (710).
11. **The replication reads the tab's own files** for the tables the live set does not hold (712); the hourly carbon was rebuilt from the archive's newer copy.
12. **The page weight is listed, not trimmed** (716): shortening the tips changes the words.
13. **The tracker places a facility by county, else state at 85 percent, else not at all**, and the tab names no facility (719).
14. **The card's figures come from the site's own library**, ranked among the 14 rows with every part held (720).

## Waiting for you

One item a line; each is in its session's report under "For Samuel's ruling".

- **The map**: no map of the rows or nodes was drawn; nothing held places a hub or node on a map (ERCOT's resource registration, the gaps file's row 3, would).
- **Migration 036** (session 580's two partial indexes) stays written and not applied: the tab reads no database, so it needs none (716).
- **The five gaps** (`docs/reviews/siting-gaps.md`, 713):
  1. large-load tariffs outside ERCOT;
  2. the capacity prices, shown (a permission from PJM, ISO-NE and NYISO, or MISO's terms reviewed);
  3. ERCOT's settlement point mapping and resource registration;
  4. utility service territories (now held and wired in, 718);
  5. a large load's own wait outside NYISO.
- **The brand screenshots**: `docs/brand/review-715/` for the restyle as a whole, and each session's folder above.
- Whether "Grid by grid" should be retired now that All grids exists (700).
- The profiles' open defaults: flexible compute's strike, the electrolyzer's 0.55 and its strike (700).
- ISO-NE's, MISO's and NYISO's prices are "license needed" since 20 October, yet "Your load" and so this tab still draw NYISO's and ISO-NE's (701).
- Whether a grid's emergency notices (CAISO's are held) should count as heavy industry's interruptions (702).
- `texas_transmission_matrix` is internal in coverage, yet "Your load" and this tab show its rate (703).
- Whether any capacity figure may be shown, and whether the computed ones belong in a private place a reviewer can read (704).
- Sub-region demand for a zone's own growth (706): held, not yet in the tab's files (chain 062's session 728).
- Whether the annual carbon should be consumption-based too (707).
- Whether the tab's files should be rebuilt by the data machine's daily run, so the tab never lags the live set (712).
- The page's weight: the hub table is about 1.7 MB of HTML; shorter tips would bring it under 1 MB (714, 716).
- Whether Texas's wires utilities should be priced from their tariffs in the Utility column (718).
- Whether the tab may name a tracked facility as A once `datacenter_facilities` is public again (719).

## The queue

- `python scripts/chain_queue.py list` at 13:10 UTC: 0 waiting in `queue/next/` (0 for samueloldlaptop). The personal laptop's 061 was taken by it this morning.
- So this session wrote **`queue/next/062-day-23-october-code-allgrids-2.md`**: 22 sessions, `machine: code`, numbered 722 to 743, with 744 to 749 kept for this machine. Its goal is the same as this chain's: the open items of these reports, the walk of session 717 again, the data machine's tables as they land (large-load tariffs, reserve margins, substations, transmission lines, sub-region demand), and the trader's and the utility's paths through the tab.
- It was committed and pushed to main on its own, before this note's landing. The next `python scripts/chain_queue.py next` on this machine takes it.
