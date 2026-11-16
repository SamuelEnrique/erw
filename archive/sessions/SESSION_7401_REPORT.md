# Session 7401 report: the datacenter tracker's method note

Energy Research Warehouse (ERW). Chain 303, portable-laptop, 16 November 2026, about 09:30 to 09:38 UTC. Model spend: USD 0.

## What was done

- **Checked first:** `docs/methods/datacenter_tracker.md` was on no branch of origin (the five tables' notes exist and were read whole; none is rewritten).
- **The note** (`docs/methods/datacenter_tracker.md`): one note for the tool as a reader meets it, pointing to the tables' notes. Thirteen sections and a sign-off block: the two views; what a facility is; what a sum counts; megawatts (stated only, the basis, a range or a ceiling, a queue's megawatts); status, and why "operating" is not a count of what runs; the grid of a facility; every figure with its key and rule, in the page's order; how ERCOT's section is built; what the tracker does not hold; the replication; the cross-checks; the decisions; what waits for the owner.
- **How megawatts are read from a range, as the code does it:** the table keeps one number, which must be one of the numbers in the quoted words; no midpoint, and no rule for the lower or upper end. A word search of the evidence sentences of the 55 news facilities that state megawatts (13 November's table, no model): 36 put no qualifying word before the figure, 8 put "to" before it, and for 11 the figure is in another sentence than the one kept.
- **Two facts the note now says plainly:** 26,124 of the 28,254 MW stated are of facilities with no operator named (for 20,704 MW of it a developer is named and not read by the by-operator views); five rows carry 25,000 of the 28,254 MW.
- **The note's figures are held to the day's figures** by `tests/test_session7402_trackers.py`.

## For Samuel's ruling

- **The views by operator read the operator alone** (faults row 17). The warehouse's own rollup table reads the operator, else the developer. Default taken: the page unchanged, the choice said in its decisions.

## Decisions made without you

- The note holds counts and sums only: no facility is named in it, since every note of `docs/methods/` is drawn at `/data/methods/`.

## Needs the key

- Nothing run. See session 7403's report for the rows whose correction needs a re-extraction.

## Commit

- `wip/7400-trackers`: `8ae74bfef` (with session 7402's work).
