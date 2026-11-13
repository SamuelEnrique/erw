# What a battery earns (`/cost-of-power/battery`): faults of 13 November 2026

Energy Research Warehouse (ERW). Chain 233, window P1 of the portable laptop, sessions 5001 to 5008. The tool read as a reader on a local production build in the internal view at 1280 and 390 (the pattern of `docs/reviews/five-tools-read-2026-11-11.md`), and its done line for roadmap item 2 read against the method note, the replication and the cross-check table. Each fault: what is wrong, where, and what the fix writes instead. States: `fixed` (on `wip/5000-battery`, waiting for its landing row), `open`, `ruling` (the owner's), `not a fault`.

| # | Where | Fault | Fix | State |
|---:|---|---|---|---|
| 1 | The page's foot | No list of the page's decisions, as the generator's (`GENERATOR_DECISIONS`, session 463) and the datacenter's (`DATACENTER_DECISIONS`, session 462) pages carry; roadmap item 2's done line asks for a decisions block (session 1527's recommendation) | `BATTERY_DECISIONS` in `site/lib/decisions.ts`, 17 lines, each with its session and ruling, drawn by the shared `DecisionsBlock` with a new `open` option, because the battery page has nothing collapsed (the owner's ruling of 12 October 2026); the note's new section 12 is the same list word for word, and the sign-off names it (`tests/test_session5001.py`) | fixed (session 5001) |
| 2 | Method note, sections 4.1, 4.3 and 11.1 | The default case is computed at the 60 percent debt share of sessions 67 to 207 (USD 6,783,357 a year, coverage 0.88) with no sign beside the figure that the page's default has been 20 percent since session 208 (USD 2,261,119, coverage 2.63); only the note's third paragraph says so, and a reader signing section 4 meets the old figure first | Each old figure keeps its place as the record of sessions 67 to 207, with the default since session 208 written beside it (4.1: `1,110 x 1000 x 0.2 x 0.1018522 x 100 = 2,261,119`; 4.3: `(8,140,219 - 2,200,000) / 2,261,119 = 2.63`; 11.1: 22.61 per kW) | fixed (session 5001) |
| 3 | Method note, section 3.2; `warehouse/derived/battery_stack.py`'s docstring | CAISO's days are said to run from 1 September 2024; the derivation starts CAISO on 1 August 2023 since session 273, and the page's grid list says "from August 2023" | Both say 1 August 2023 since session 273, the note keeping September 2024 as the date before it | fixed (session 5001) |
| 4 | The page, "Is it worth building?" | The section's first line sends the reader to the assumptions "set in the box on the left, under Financing", and "Financing" is a fold of the settings column that starts closed (as do "Charts" and "Sensitivity"), against "nothing collapsed" | Not changed here: the settings column's folds are its layout (session 297), and the chain does no layout work. Default: leave them closed; the alternative is "Financing" open to start | ruling |
| 5 | The page, under the income table | A fold "Each month: days held; the storage nodes' four-hour spread at the 10th percentile, median and 90th" starts closed; the ruling of 12 October moved the monthly rows to the CSV and took the folds away | Not changed here (the fold came with the node band, session 355, after the ruling). Default: leave it; the alternative is its rows in the CSV alone | ruling |
| 6 | The page, "What matters most" | "The chart as a table" is a fold that starts closed | Not a fault: it is the chart's accessible text, the same on the three economics pages | not a fault |

## The read (session 5001)

Local production build of `wip/5000-battery` at `6c44c559` plus the note's fixes (exit 0, TypeScript included), `next start -p 5001`, the internal view opened by `/internal/open`, read at 1280 and 390 by window P1's reader (`read.json` and the screenshots kept in the session's scratchpad, not in git).

| View | 1280: width, keys, errors | 390: width, keys, errors | Decisions block |
|---|---|---|---|
| `/cost-of-power/battery` | 1265, 188, 0 | 390, 188, 0 | `5001`, open, 17 lines |
| `?grid=caiso` | 1265, 62, 0 | 390, 62, 0 | the same |
| `?grid=nyiso` (in review, internal) | 1265, 40, 0 | 390, 40, 0 | the same |

- No "NaN", "undefined", "null%", "license needed%", "Infinity" anywhere. The wide income table scrolls inside its own box at 1280 (1955 px inside a 1265 px page); nothing scrolls sideways at 390.
- The headline at the defaults: USD 81.40 per kW, 33 percent from ancillary services, covered 2.63 times, a bad month of USD 475,477 (December 2024): the replication's figures to the cent (`replication/battery/replicate.py`, 22 of 22).

## The done line after session 5001

| Item | State |
|---|---|
| Method note | complete for signature (sections 1 to 12, the sign-off block naming section 12); unsigned: the owner signs |
| Replication | `replication/battery/replicate.py` from the public CSV, 22 of 22; the do-file never run (no Stata on this laptop) |
| Cross-check table | `docs/methods/crosschecks/battery.md`, current (its debt payment is 2,261,119) |
| Decisions block | on the page and in the note (row 1) |
