# Roadmap (a sample for tests/test_planner.py and for a dry run; not the roadmap)

Energy Research Warehouse (ERW). A filled-in copy of `docs/roadmap.md`, so that `python scripts/planner.py draft --dry-run --roadmap tests/fixtures/roadmap_sample.md` has something to plan from. Nothing here is a real instruction.

## Status

- planner: on
- budget: 3 sessions a day per machine
- earliest start: 13:00 UTC
- latest start: 05:00 UTC
- deploy cutoffs: 22:30 to 23:45 UTC; 16:45 to 17:30 UTC

## This week

1. [x] The price board names its newest hour
   - machine: code
   - where: /board
   - done: the check script passes on production
2. [ ] The storage table gains its September rows
   - machine: data
   - where: storage_capacity
   - done: the validator passes and the coverage file lists September
3. [ ] The battery page says which strategy its headline is
   - machine: code
   - where: /cost-of-power/battery
   - done: check-battery-face.mjs passes on a local build and on production, and the face check at 1280 and 390 px reads the sentence from the page
   - rulings: the sentence states the strategy and the window; it recommends nothing (Samuel, 11 October 2026)
   - rulings: the page stays in review
   - session: write the sentence and its test, on a local build
   - session: the face check at two widths, the Method note, and the landing
4. [ ] The generator page lists its hubs by region
   - machine: code
   - where: /cost-of-power/seller
   - done: check-seller.mjs passes

## Backlog

- A page that says which strategy earned more in each month.

## Rulings

- 11 October 2026: a page states what the reader can decide with; it recommends nothing.
- 11 October 2026: every page stays in review until Samuel says otherwise.

## Holds

- video/ and the Roundup workflow.
- The scanner's thresholds.

## Input from Ben and Khalid

- 10 October 2026, Ben: the battery page should say which strategy the headline is.

## Review log

### 11 October 2026

- The sample was written for the planner's tests.
