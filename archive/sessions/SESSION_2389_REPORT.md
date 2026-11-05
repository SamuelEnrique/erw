# Session 2389 report: five held tables linked to the notes that describe them (the battery stack, the large-load verdicts, the hourly node prices)

24 October 2026, from 09:22 UTC to 09:25 UTC, on lab-desktop (the data machine), chain 113, unattended. Model spend USD 0. Pulls: none.

## Read these first

- **How the tables were chosen:** 62 tables have an empty Method cell on this branch, on main and on chains 110's and 112's branches. Both agents confirmed none of these five is theirs; chain 110's session 2361 took the FERC EQR seven.
- **Five `Tables:` lines,** in notes that describe each table, each checked against the table read past its header lines:
  - `battery_stack_monthly`, `battery_stack_review_monthly` and `battery_stack_stress_daily` in `docs/methods/battery_stack.md`, whose opening named two: 11,556, 3,744 and 1,890 rows. The note names the variables by pattern (`<strategy>_<N>h_<metric>`, `revenue_<product>_usd_per_mw`, the day counts), and every variable held fits one.
  - `large_load_document_verdicts` in `docs/methods/large_load_public.md`, which has a section of its own on it: 427 rows.
  - `ercot_node_prices_hourly` in `docs/methods/node_basis.md`: 499,728 rows over 236 storage settlement points, 19 July to 23 October 2026, under the owner's ceiling of 500,000. The note's section is extended with today's count and its `x_class`.
- **Not taken, said why:** `large_load_statements` and `large_load_rules`. Their notes name them but do not describe their worded columns (`quantity_as_written`, `status_as_worded`, the docket fields). They want notes of their own, not a `Tables:` line.
- **The five Method cells set** by `build_coverage.py`'s own `method_cell`.

## Contradictions found

- `node_basis.md` gives `ercot_node_prices_hourly` 498,360 rows (its session's count); today's is 499,728. The section now says so.

## Checks

- `tests.test_session674`, `1000` and `1001`: OK.

## Decisions made without you

- Five tables, not six: the sixth candidates' notes do not describe them in full.

## For Samuel's ruling

- None new.

## Files

- Changed: `docs/methods/battery_stack.md`, `large_load_public.md`, `node_basis.md`, `docs/coverage.md` (five Method cells). New: this report.
