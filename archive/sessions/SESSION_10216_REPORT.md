# Session 10216 report: the energy project map audited as a hostile expert would

Chain 710, part D (one more tool in the form of part B), 26 November 2026, the old laptop, worktree `erw-c710-b`, branch `wip/audit-map-doc`. The audit: `docs/reviews/map-model-audit-2026-11-26.md`, its evidence in `docs/reviews/map-model-audit-2026-11-26/`.

## What was done

- `/map`'s Projects tab drawn with the site's own code (`ProjectMap`, `MapDecisions`) on `site/data/map.json` (built 19 November 2026); every figure of the default view restated by a standard-library script written from the note: **142 of 142 to the digit**. The file's 31,073 units equal EIA's tables in eight fields; 3,400 of 3,400 county-placed queue positions sit at the gazetteer's internal point.
- Six findings: 1 ERCOT's "Completed" worded for one copy of the queue (Medium); 2 where a point is (Medium); 3 "Operating" holds standby and out-of-service units, the heavier ring marks built units (Low); 4 the transmission layer's status and date not said (Low); 5 "nothing since the inventory's month", the marks' size (Very low); 6 seven EIA points far from EIA's own county (Very low, a figure).
- Branches: `wip/audit-map-1` `039848841`, `-2` `2bc19f476`, `-3` `188639c7b`, `-4` `b6845e95c`, `-5` `0631f1ed9` (words, for landing, each drawn and read: pass); `wip/audit-map-words` `09b5862d0` (the five merged, conflicts resolved, 142 of 142 unchanged on its drawing); `wip/audit-map-6` `5b7abadbf` (a test only, not for landing).
- Tests: each words test fails on origin/main, each behaviour test passes; on the merge 147 passed, 10 skipped over the audit tests and every test file that reads the changed files; `test-map-read.mjs` 42 of 42, `test-map-sources.mjs` 37 of 37.
- Measured for the expert's number: a planned unit stands a median of 12.5 miles from its county's internal point; at 30 miles a county point loses 11.0 percent of truly near planned units; the point of interconnection (96.5 to 100 percent filled in the public queues) and the proposed in-service date (3,252 of 3,684 positions, in the file) reach no card; planned units of 100 MW or more stand a median of 1.5 miles from a line of 230 kV and above.

## Decisions made without you

- Finding 1's words follow the copy's queue vintage, with 17 November 2026 as the first day of ERCOT's milestones (session 7022 landed 16 November 19:58 UTC, after that Monday's pull): no builder or data change, the words are true of today's file and of the next.
- Finding 6 uses 200 miles from the own county's internal point, outside Alaska; a looser screen (121 units) caught sound plants in large border counties and was not used.
- The Queues tab (`QueuesView`) reads the live set and was not drawn; its one new sentence was read in the source.
- Evidence scripts were written to run from `runs/c10216/`; copies are in the audit's folder.

## For Samuel's ruling

- Finding 6 (`wip/audit-map-6`, not for landing): draw a unit whose EIA point is over 200 miles from its EIA county's point (outside Alaska) at the county's point, marked. Default "left as it is". Effect: 7 units, 1,469.2 MW (5 planned, 1,464.2 MW) move on the drawing and in "Near a point"; no count or sum changes.
- Still open from 16 and 17 November, not repeated: ISO-NE's queue positions (414, 21,901.8 MW) and the datacenters drawn while their tables are "license needed" (`wip/alt-map-1`).

## Data requests (rows for the desk)

- (a) `hifld_transmission_lines`: the 10,692 lines by `x_status`, by `x_inferred`, and by the year of `x_source_date` and `x_val_date` (counts and km, no rows): sizes finding 4.
- (b) `iso_queue_statistics` as the live set holds it, and `ercot_interconnection_queue` of 23 November: ERCOT's operating positions by entry year in each: says whether the Queues tab's ERCOT "Operating" is signed agreements or synchronized plants today (finding 1).

## Needs the key

- Nothing.

## Problems

- One test printout was first written to the parent folder of the worktree (`..\c10216_b1.out`) and moved into `runs/c10216/` at once; nothing else was written outside the worktree. No heredoc, no inline code, no model call, no live request.
