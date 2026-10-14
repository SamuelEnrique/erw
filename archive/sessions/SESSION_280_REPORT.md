# Session 280 report: the datacenter page reads its two new tables

14 October 2026, 18:55 to 19:30 UTC, unattended, on samueloldlaptop (the code machine), the second session of the daytime chain of 14 October. Branch `task/280-datacenter-tables`, landed. Model spend USD 0: no model call. Pulls: none (the live set read with the anon key). No warehouse data written.

## Read these first

- **"Will the power be there?" now sets two counts side by side at the grid's hub** from `scarcity_hours_by_grid`, for ERCOT and CAISO, each beside the hours the table holds: ERCOT's `HB_HUBAVG` at or above USD 1,000 in 1 of 8,760 hours, its reserve adder above zero in 44 of the 1,558 hours held (1 October to 4 December 2025); CAISO's SP15 in 1 of 8,735, its own signal (an EEA or a flex alert) in 0 of 8,760. Any other grid keeps the lines it had.
- **"How soon?" now lists every statement of `large_load_public` for the grid**, each with its date, figure, stage and document link, no quoted text, never a sum, in a closed "Every public figure ..." panel under the paragraph session 265b wrote: ERCOT 43 as operator and 24 of utilities and the Commission, plus 24 elsewhere in Texas (El Paso Electric 21, AEP 3); CAISO 48; NYISO 5 and 6 elsewhere in New York. A grid with no row keeps the plain line.
- **check-values: 907 of 907 on the /cost-of-power pages**, now with CAISO's address too (124 statement figures and 12 hub counts among them).
- **For the data machine: nothing stale.** An early read of mine seemed to show CAISO's `own_signal` writing two hours twice; that was my own paging on an unstable sort, not the table. Read again ordered by hour and variable: no hour twice.

## What to review

- The page (in review): https://erw-flame.vercel.app/cost-of-power?grid=ercot#there and #soon, then `?grid=caiso` and `?grid=nyiso`.
  1. "Will the power be there?": the new table under "The two counts".
  2. "How soon?": open "Every public figure on large loads for ERCOT and elsewhere in Texas: 91".
- The pack's parts 2 and 4: https://github.com/SamuelEnrique/erw/blob/main/docs/reviews/packs/datacenter.md (steps 11 and 13; four new cross-check rows).

## What was done

- `site/lib/datacenter/answers.ts`: `byGrid()`, a bounded read of `scarcity_hours_by_grid` (the page's twelve months, ordered by hour and variable), stats `sbg:rt:hours|held` and `sbg:own:hours|held`.
- `site/lib/datacenter/statements.ts`: `GRID_STATE`, `listsOf()`, `rowStat()`; `site/app/cost-of-power/LoadAnswers.tsx`: `ByGridCounts` and `StatedList`; `page.tsx` reads the grid's rows once and, for a grid in one state, every row.
- The download (`tables.csv`) carries the hub counts; the source line names both tables.
- `scripts/check-values.mjs`: `dcll|<grid>|row:<id>:mw|wait`, one read a grid; the address `/cost-of-power?grid=caiso` added.
- Tests: `tests/test_session280.py` (by node: the counts with an hour outside the months and an hour twice; the lists and the row figures); `tests/test_session265.py` brought to today's reads (it held that the page does not read the scarcity table).
- `docs/methods/scarcity_hours_by_grid.md` names its reader.

## Checks

| Check | Exit | Notes |
|---|---|---|
| `precheck.py` | 0 | at the chain's start |
| `npm ci`, `npm run build` (twice) | 0 | no "statement timeout" |
| `eslint` on the changed files | 1 | 7 errors, all already on main in session 265b's `StatedLine` (the same 7 on main's file); none in the new code |
| `check-values`, `/cost-of-power` pages, before the last fix | 1 | 243 of 251: my keys on waits written with words first and on megawatts with decimals; fixed |
| `check-values`, `/cost-of-power` pages | 0 | 907 of 907 |
| the five datacenter test modules | 0 | 55 tests |
| the whole suite, clean copy of `5d14ecfb` | 0 | 4,220 tests, 243 skipped |
| `freeze.py status` | 0 | no freeze |

## The landing

- Before `s280-before` 19:11:45 UTC; pushed 19:11:57 (`task/280-datacenter-tables`, `5d14ecfb`); check run 38621631513 success 19:19:42; merged `2a934a1e`; no new style sheet (the change adds none), so the after snapshot was taken at 19:29:59, ten minutes after the merge; after `s280-after` 19:30:20; `compare`: **0 differences** on the 25 pages. Expected: no page is live.
- Production serves the change: at 19:32 UTC the internal view of `/cost-of-power?grid=ercot` holds both new parts (`data-by-grid`, `data-stated-lists`).
- The other machine's `task/286-findings-round-two` was on GitHub at the push; a trial merge with this branch was clean (exit 0). Seen after the push, not before: the check came in the same command as the push. Nothing was lost.
- This report lands with session 281.

## Decisions made without you

- **"The chosen state"** read as the state a grid lies in, where it lies in one (ERCOT Texas, CAISO California, NYISO New York): the page's address names a zone, not a state. Multi-state grids list their own rows only.
- **The list is a closed panel** under the paragraph, so the section reads as it did until opened; no section added or moved.
- **A wait written with words before its number** ("within 18 months", "approximately 220 days") stands as written with no check key; a megawatt figure with decimals is shown with them.
- **The operator** is any row the table classes "grid operator" or "operator".

## For Samuel's ruling

- Whether the list should also show the measured waits' rows by stage beside it (today they stay in "How long a large load waits").
- Some rows' "wait" is a span of dates as written ("filed June 29, 2023 and resolved July 11, 2024", CAISO): the table's own words; whether the data machine should class these.
