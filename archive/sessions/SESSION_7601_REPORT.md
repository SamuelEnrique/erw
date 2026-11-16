# Session 7601 report: the old laptop's rows 15 to 31, and `/map` to the done line

Energy Research Warehouse (ERW). Chain 305 (`queue/done/305-night-16-november-portable-done-line-and-browser-reads.md`), portable-laptop (code role), 16 November 2026, about 12:17 to 13:05 UTC. Model spend: USD 0 (`ERW_SPEND_CAP_USD=0`; no script that calls a model was run).

## Part A again: rows 15 to 31 of `docs/state/browser_reads_wanted.md`

- Four more of the old laptop's branches (`wip/7506-impact`, `wip/7507-peak-premium`, `wip/7508-demand-growth`, `wip/7509-interconnection`), none landed, merged locally with the first four for one build; read at 1280 and 390 px. A chart's hover was read by moving the mouse across it at 59 places and three heights.
- **13 rows seen as written.** `/impact`'s figures (515 jobs, USD 41 million, USD 876,642, "Minnesota is 4 of 51"); the peak premium's 25.00 and -251.00, its 202 card figures each found in the page's tables; demand growth's "+8.00 percent" and "not held"; the queue's two decimals and its year selects.
- **3 rows the shared mark's fault** (the folds of the three explorers at 390 px), fixed for every page on `wip/7600-large-load-read`.
- **1 fault of its own, on production too:** `/explore/demand-growth`, the second chart's hover card drew no figure: every line read "percent" with no number. The page's test read the SVG's own title, which holds the figures, so it passed. Fixed on `wip/7601-demand-growth-read` (cut from `wip/7508-demand-growth`; its faults row 20), landing row 36; read again: "+33.34 percent".
- Index and 48 screenshots: `docs/reviews/browser-reads-2026-11-16/` on `wip/7600-large-load-read`.
- The old laptop has since added rows 32 to 52; they are read at the start of the next session.

## Part B, tool 1: `/map`

- **Checked first:** `/map` is this machine's in `docs/state/done_line_claims.md`; no branch holds a `replication/map`.
- **The note:** `docs/methods/map.md`, new, fifteen sections: the three tabs, what each reads, each figure's table and rule, eleven choices with default and source, what the tool does not hold. It points to the tables' notes and repeats none.
- **The replication** (`replication/map/`): the Projects tab's 6,094 figures over 123 views, computed by the page's own functions on the page's own file (`site/scripts/map-figures.mjs`) and again from the rows by the note's rules. The generating units are read from **EIA's own workbook** of September 2026 (robots read first: allowed), not from an ERW table.
  - **The units: 3,790 of 3,790 figures inside half a megawatt or half a row.** 31,071 of 31,073 units carry the same seven fields on both sides; the other two differ in their id alone (below).
  - The 278 datacenters: the same on both sides.
  - The queue positions: the page's copy is of 26 October, the live set's of 5 November: 301 figures differ for that reason alone and are named, each with both sides.
  - A Stata do-file for the five headline figures, expected values at its top (not run: no Stata here; `replicate.py --headline` prints the same five lines).
- **The cross-check:** EIA's Electric Power Monthly, Table 6.1 (in service at the end of August 2026), beside the same operating units' net summer capacity in the September workbook: 18 of 27 technologies the same to the tenth of a megawatt; the rest a month of change (solar 2,967.1 MW more, batteries 1,610.8 more); together 1,324,124.6 against 1,318,801.0 MW, 0.40 percent. The map's own measure, nameplate, is 1,423,491.7 MW. No figure adjusted.
- **The decisions block** on the page: 11 choices, each with its default, its source and its session on hover; no grey text.
- **In the browser** at 1280 and 390 px, on a build with the hover placer: ten addresses, 424 figures drawn at each width, none differs from the figures file; every control used; a unit's card opened from the drawing (one request, to `/map/card`); the Queues and Resources tabs; 18 marks, none past an edge; no sideways scroll; axe, no rule broken on the three tabs. 18 screenshots in `docs/reviews/map-done-line/`.
- **Faults:** `docs/reviews/map-faults-2026-11-16.md`, 8 rows: 3 fixed (the count of units with no balancing authority is 727 blank and 246 that EIA marks "NA", said in the note and on the page; a card wrote "685 MW" where its hover wrote "685.0 MW"; the shared mark), 3 for the data machine (rows 32 to 34 of `docs/state/data_requests_done_line.md`), 2 rulings.

## Tests

- `tests/test_session7601_map.py`: 17 pass (the replication's own rules on rows made for the test; the committed figures; the note against the page). `site/scripts/test-map-sources.mjs`: 37 of 37.
- The 71 test files that name a changed module or enumerate the notes, the reviews and the replication folders, each in its own process: 865 tests pass. No full suite and no landing gate here.
- `wip/7601-demand-growth-read`: `tests/test_session7601_demand_growth_read.py`, 7 pass; the eight test files that name the page, 52 pass.

## What to review (the page is in review; after the landing)

1. `https://erw-flame.vercel.app/map`: scroll to the foot of the Projects tab and open "Decisions on this page (11)"; hover the mark of the fifth line: "Default: EIA's balancing authority code. Source: ... 973 units have none: EIA leaves 727 blank and writes "NA" for 246."
2. `https://erw-flame.vercel.app/map?kind=operating&tech=nuclear`: point at a dot (Monticello, in Minnesota): "Nuclear, 685.0 MW"; click it: the card's MW line reads "685.0 MW" too.
3. On your own machine: `python replication/map/fetch_rows.py --units-only`, then `python replication/map/replicate.py --headline`: 28,712 operating units, 1,423,491.7 MW; 2,361 planned, 290,264.2 MW; 1,640 batteries.

## Needs the key

- Nothing in this session.

## Decisions made without you

- The units are replicated against EIA's own workbook, fetched at run time into a folder git ignores; the queue's and the tracker's rows are read from the live set as the site reads them and only counts and sums are committed.
- The decisions block is in the tool's own folder (`site/app/map/Decisions.tsx`), in the form of the old laptop's newest blocks (default, source and session inside the hover), not in the shared list, which other branches are editing.
- The Queues tab's figures are rows of `iso_queue_statistics`, which the interconnection explorer's replication (the old laptop's `wip/7509-interconnection`) already recomputes: not done twice. The Resources tab computes nothing.
- One view (`?state=PR`) was in the figures list twice in the first commit of the stack; the list holds 123 views.

## For Samuel's ruling

- **The map draws 3,709 queue positions and 278 datacenters from tables its own last line calls "held: license needed".** It is row 7 of the datacenter faults of 11 November, still open, and now the same question for ISO-NE's 415 queue positions. Default taken: nothing changed.
- **No A and B on the map** (two states or two grids side by side). Default taken: not built.

## Commits

- `wip/7601-map`: `ab3ab0119` and the commit that holds this report.
- `wip/7601-demand-growth-read`: `d1bdd1385`. `wip/7600-large-load-read`: `cc2504275` (the index and pictures of rows 15 to 31).
- main: `ce9be9911` (rows 15 to 31 marked, landing row 36), the three data requests, and the state files that follow this report.
