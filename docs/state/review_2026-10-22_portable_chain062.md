# Chain 062 on portable-laptop (sessions 722 to 730): the note for Samuel

Energy Research Warehouse (ERW), written on portable-laptop on 22 October 2026 at 15:40 UTC. This machine took `queue/next/062-day-23-october-code-allgrids-2.md` at 13:19 UTC and ran its sessions 722 to 730. The old laptop (samueloldlaptop, the machine the file names) took the same file at 14:48 UTC, its checkout not having pulled the take, and ran its own sessions 722 to 730 on `origin/wip/730-allgrids`. **This machine's run stops here and lands nothing**; the old laptop's run is landing. Every branch of this run stays on the remote for you to compare. Model spend USD 0 on this machine; no warehouse data written; no request to a publisher (the ERW's own archive bucket, the live set with the anon key and the site's own pages only).

## The two runs, session by session

| Session | This machine's branch | What this machine did | What the old laptop did (its commit subject) |
|---|---|---|---|
| 722 | `wip/722-allgrids` (`f1360ea7`) | chain 050's end checked; 719 to 721 found unlanded and deferred; the replication against production (0 differ); the open items in one table, `docs/reviews/siting-open-2026-10-23.md` (37 lines) | the same, with 719 to 721 landed by it first (`c1833c31`) |
| 723 | `wip/723-allgrids` (`87472b39`) | the trader's path walked on production, 14 steps at 1280 and 390, every tip read; `docs/reviews/siting-trader-path.md`; seven faults inside the chain's files, four gaps, one ruling | 16 steps; five fixes for 724 (`1abe5319`) |
| 724 | `wip/724-allgrids` (`c7f70c81`) | a node as A or B from its panel (Set as A, Set as B; the box's lists hold the chosen node), the headline and panel in the node view, Close keeps the screen, the status line's words, **a basis spread column keyed `allgrids|nodespread`**, the transmission sort's words, the shared tip's table; real time at the nodes in the gaps; check-values 2,705 of 2,705 | the basis spread, the missing days named, a node as A or B, **find by name, download** (`a5f695a6`) |
| 725 | `wip/725-allgrids` (`e726182d`) | the utility planner's path walked on production, 12 steps; `docs/reviews/siting-utility-path.md`; three faults | the same walk (`765c1785`) |
| 726 | `wip/726-allgrids` (`f311b096`) | each utility figure's basis under it (bundled, energy only, delivery only; the county's seller or the state's stand-in) and in the sort line; the rule's document as a link; the A and B panel's utility row tip | the Utility column names each figure's kind; the panel subtracts only like from like (`9f926ffb`) |
| 727 | `wip/727-allgrids` (`2bc23ed2`) | the lab's path walked again on a build with 718 to 726 in place; no step fails; the Now column | on production; two more steps answered by 718's tables (`a11b956c`) |
| 728 | `wip/728-allgrids` (`0287d9d9`) | **27 zones** (ERCOT's eight by weather zone, NYISO's 11, ISO-NE's 8) draw their own demand growth, 2025 over 2024 until the grid's twelve months are held; `ZONE_SUBBA` with reasons; the builder's `--subba` mode; keyed `allgrids|zdemand`; the replication follows; the gaps row filled in part | **19 zones** (NYISO's and ISO-NE's) (`6c578b33`) |
| 729 | `wip/729-allgrids` (`22df066e`) | the utility rule built and tested: a facility placed by the utility the tracker names, EIA-861's exact name after a written normalisation, inside one grid; the file's `utilities` part (2,072 names); 141 of 422 placed before and after (3 rows name a utility, none exact) | the unplaced facilities explained, "none there for a utility rule" (`f16b7c43`) |
| 730 | `wip/730-allgrids-portable` | `largeLoadTariff` against the connector's documented shape, tested, not wired; the landing yielded | the builder's step and the tab's functions against the connector's shape, tested, not wired; its landing (`ea7b9172`) |

Each of this machine's sessions has its report on its branch (`archive/sessions/SESSION_72N_REPORT.md`; 730's is `SESSION_730_REPORT_portable.md`), its shots under `docs/brand/review-72N/`, and its checks (check-values on every cost-of-power address, check-existing-tab against production, the replication where a figure was added) in the report.

## What to take from this machine's run, if anything

Reversible, yours to choose; none of it is on `main`:

- **728's ERCOT zones** (the weather-zone mapping with its reasons, the 90 percent month rule, the `--subba` builder mode) if the old laptop's 728 leaves ERCOT's zones without their own growth.
- **729's utility rule** (the normalisation in both languages with a test that they agree, the wires-utility rule, the `--facilities` builder mode), since the chain asked for the rule and the old laptop found "none there".
- **724's spread column and node A and B from the panel**, and **726's basis words and document links**, against the old laptop's versions of the same sessions: the walks' files (`siting-trader-path.md`, `siting-utility-path.md`) on each branch say what each found.

## Decisions made without you

1. **This machine yields** (session 730's report, decision 1).
2. **Nothing of this run is pushed to `main`**: a push there deploys, and its reports share names with the old laptop's.

## Waiting for you

- Which run of chain 062 lands, session by session (730's report, the ruling).
- The queue's double take: a take should pull first (730's report, the ruling).
- Every ruling item of this machine's reports 722 to 730: the delivery-only utility figure's sort (727), a 2026 yearly table of the sub-region demand (728), the tracker's utility names as EIA writes them (729).
