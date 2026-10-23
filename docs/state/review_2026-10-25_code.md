# The chain of 23 October 2026 on the old laptop (062): the note for Samuel

Energy Research Warehouse (ERW), session 743, written on the old laptop (samueloldlaptop) on 22 October 2026. Chain 062 (`queue/done/062-day-23-october-code-allgrids-2.md`, sessions 722 to 743) was written by session 721 of chain 050 and taken by this machine at 14:47 UTC. It is the All grids tab's second pass: chain 050's open items, the lab's path walked again, a trader's and a utility planner's paths walked and fixed, the data machine's tables as they land, the replication, the brand, the reads and the rulings. Each session worked in its own worktree (`C:\Users\lossa\Documents\erw-7NN`). Model spend USD 0; no warehouse data written; no request to a publisher. The reads were the ERW's own archive bucket (two tables rebuilt into `runs/archive_restore/`), the live set with the anon key, and the site's own pages.

## First: what to know

1. **Read `docs/reviews/siting-rulings-2026-10-23.md` first**: the 19 items the tab waits on, chain 050's and this chain's, each with what it changes, the work, and a recommendation. Nothing in it is decided.
2. **Chain 062 landed in three pushes**, each through the full gate: 722 to 730 (merged 16:28 UTC, `21cec5d1`; Vercel refused to deploy it, "rate limited"), 731 to 740 (17:32, `b747b88d`; deployed at 17:35 with 722 to 730), and 741 to 743 with this note (`SESSION_743_REPORT.md`). Every comparison of the 25 snapshot pages: 0 differences (every page is in review).
3. **`datacenter_facilities` is held whole**, so the tracker shows no facility and 719's links show nowhere; nothing of the table is in the repository (729 counted the unplaced facilities on this machine only).
4. **Four sessions found their tables not landed** (729 a utility to place by, 731 reserve margins, 732 substations and lines, 733 a node's place) and said so. 730 wrote the large-load tariffs' side of the tab against the connector's shape, tested, not wired: the table waits on an `OPENEI_API_KEY` (rulings item 18).
5. **A past Digest's figure no longer matches Supabase**: the 21 October issue prints WTI for 14 October at USD 101.91, and `eia_fuel_spot_prices` now reads 96.34 (a source revision). Production fails the same check. It is the personal laptop's chain's page, and no past issue is rewritten; listed here for you.
6. **Nothing waited in `queue/next` for this machine**, so this session wrote the next file, `queue/next/063-evening-22-october-code-allgrids-3.md` (sessions 744 to 765), and it reaches main with this note's landing.

## What each session did

| Session | Branch | What it did | Address to open (internal view) | Shots |
|---|---|---|---|---|
| 722 | `wip/722-allgrids` | chain 050's end checked; the queue's move pushed; production serves 719 to 721 since 14:56; the replication 0 differ; the open items, one table | `docs/reviews/siting-open-2026-10-23.md` | none |
| 723 | `wip/723-allgrids` | a trader's path walked, 16 steps; five findings | `docs/reviews/siting-trader-path.md` | `docs/brand/review-723/` |
| 724 | `wip/724-allgrids` | the trader's fixes: the basis spread, the missing days named, a node as A or B, find by name, download | `/cost-of-power?view=allgrids&mw=1000&rows=nodes&nsort=spread&ndir=desc` | `review-724/` |
| 725 | `wip/725-allgrids` | a utility planner's path walked, 12 steps; the Utility column mixes three kinds | `docs/reviews/siting-utility-path.md` | `review-725/` |
| 726 | `wip/726-allgrids` | each utility figure names its kind; the A and B panel subtracts like from like | `&sort=utility&dir=asc&grid=pjm,caiso` | `review-726/` |
| 727 | `wip/727-allgrids` | the lab's path walked again: no step fails | `docs/reviews/siting-path.md`, last section | `review-727/` |
| 728 | `wip/728-allgrids` | a zone's own demand growth, NYISO's and ISO-NE's 19 zones (EIA-930 sub-regions, 2025 over 2024) | `&sort=headroom&grid=nyiso,isone` | `review-728/` |
| 729 | `wip/729-allgrids` | the tracker's unplaced facilities explained; none there for a utility rule | `docs/reviews/siting-open-2026-10-23.md`, line 25 | none |
| 730 | `wip/730-allgrids` | large-load tariffs: none there; the tab's side written and tested, not wired | `site/lib/siting.ts`, `tariffParts` | none |
| 731 | `wip/731-allgrids` | reserve margins: none there | | none |
| 732 | `wip/732-allgrids` | substations and lines near a node: none there | | none |
| 733 | `wip/733-allgrids` | a node's place: none there; the node table's unused intraday spread found | | none |
| 734 | `wip/734-allgrids` | the second card: what stepping off saves (USD 8.60 to 10.78 per MWh at ERCOT's rows) | `/research/card/siting_flexible` | `review-734/` |
| 735 | `wip/735-allgrids` | the replication extended (`--tables`): 89 figures, 77 beside the page, 0 differ | `docs/methods/siting.md`, "The replication" | none |
| 736 | `wip/736-allgrids` | AccessLint and 390 on the chain's addresses: 0 findings | `docs/brand/review-736/` | `review-736/` |
| 737 | `wip/737-allgrids` | the tip's box styled once: the hub table 1.86 to 1.58 MB, no word changed | any tip | `review-737/` |
| 738 | `wip/738-allgrids` | the brand pass: the node panel heading's links in sans | a node's panel | `review-738/` |
| 739 | `wip/739-allgrids` | the reads: the tab reads nothing; the slowest read 27 ms | `docs/reviews/siting-reads-2026-10-22.md`, last section | none |
| 740 | `wip/740-allgrids` | the method note v2; the gaps' state | `docs/methods/siting.md` | none |
| 741 | `wip/741-allgrids` | the rulings in plain words, 19 items | `docs/reviews/siting-rulings-2026-10-23.md` | none |
| 742 | `wip/742-allgrids` | the landing and the clean-up | | none |
| 743 | `wip/743-allgrids` | this note, the next file, the queue | this file | none |

Every address is on `https://erw-flame.vercel.app`, after `/internal/open`; the `&...` ones follow `/cost-of-power?view=allgrids&mw=1000`.

## Decisions made without you

Each report lists its own; the ones that shape the tab:

1. **The queue's move went to main at once** (722), with its snapshots, so a second code machine could not take the same file.
2. **The node list's spread is the 90th percentile less the 10th** (724), the panel's own figures; the missing days are named by month from the node file.
3. **The download is made in the browser** from the rows shown (724): no new route.
4. **"Not alike" instead of a difference** between a bundled price and a delivery revenue (726).
5. **A zone's growth only where EIA-930 names the same area** (728): NYISO's and ISO-NE's zones; a calendar year over the one before; the sort stays the grid's.
6. **No rule written for three holding-company names** (729), and no placeholder function where no table or shape exists (731, 732).
7. **The tariff functions keep a rate's parts apart** (730): which parts a column adds waits for the table.
8. **The second card ranks ERCOT's rows only** (734), where the four-peak charge, most of the saving, is held.
9. **Only markup moved for the page's weight** (737); no variant of shorter tips was built, since their words are a ruling.
10. **The gaps' state is a list after the table** (740), so the internal page's file is unchanged.

## Waiting for you

- **The 19 items of `docs/reviews/siting-rulings-2026-10-23.md`**: Grid by grid; the profiles' defaults; NYISO's and ISO-NE's prices; emergencies as interruptions; the transmission rate's license; capacity prices; annual carbon's basis; the band; fresh files; shorter tips; the brand shots; the wires utility (two items); a facility's name; real time in the sort; a 2026 sub-region table; the tracker's operating utility; the OpenEI key; migration 036.
- **The 21 October Digest's WTI** (above, item 5 of "First").
- **The map** (chain 050's item): nothing held places a hub or a node on a map; it waits on a node's place (rulings and gaps).

## The queue

- `python scripts/chain_queue.py list` at 17:40 UTC, on main as of `b747b88d`: 0 waiting in `queue/next/` (0 for samueloldlaptop).
- So this session wrote **`queue/next/063-evening-22-october-code-allgrids-3.md`**: 22 sessions, `machine: code`, numbered 744 to 765 (said so in the file). 744 to 749 were kept for this machine by chain 050; 750 to 799 are no other machine's, since a data-machine chain skips 700 to 849 and the personal laptop holds 800 to 849.
- **Its goal is the same, and its order is**: the rulings as they come (an item not ruled is left as it is); chain 062's open items; the node's intraday swing (`dam_spread_4h`, held and unused); the data machine's tables as they land (tariffs, reserve margins, a 2026 sub-region table, a node's place); the trader's and the utility's paths again; the replication, accessibility, the reads, the method note v3.
- **It carries two new rules from this chain's slips**: a build only on `db_probe`'s exit 0, and the push only on the ancestry check's exit 0.
- **It reaches main through this note's landing** (`task/741-743-allgrids`, with its gate and snapshots), not a push of its own, so the site deploys once. The queue step runs after main is pulled.
