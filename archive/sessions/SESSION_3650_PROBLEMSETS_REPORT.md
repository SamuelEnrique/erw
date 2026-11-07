# Session 3650: the problem sets, brought to a state an instructor can assign

Energy Research Warehouse (ERW). Personal laptop (portable-laptop), fifth window, 6 November 2026, Opus 5.5. Prompt: `queue/done/206-day-6-november-portable-problemsets.md`. Branch `wip/3650-problemsets`, head `3f48d6314`; landing request row 14 of `docs/state/landing_request_portable.md` (task `3650-problemsets`, port 3365). Session number 3650: the first free at or above 3650 on `origin/main` and every branch (no branch, report or commit message named it). Queue number 206: the highest taken was 205.

## What already held

- **(1), in part.** Every figure was computed by code from the live set or a committed file, each with its check key (`series|...`, `series_max|...`, `calc|...`, and so on), recomputed by `check-values.mjs`; no typed number in an answer (`tests/test_session44.py`). **Missing:** no figure had its source as a hover.
- **(2), in part.** Five questions per set, each answer on a click (a `<details>`), with a worked solution computed from the same keys. **Missing:** no worked example; the five were not in a rising order; no one-line computation.
- **(3)** did not hold: no line on what a student can do.
- **(4), in part.** The index listed the five, each with its line and its dated edition, and each edition had a CSV for each question (`site/public/problems/2026-10-15/`). **Missing:** grids, tables and skills on the index; a CSV of each set's data.
- **(5)** did not hold.

## What was done (`wip/3650-problemsets`)

- **`site/lib/problemkit.ts`** (new; imports nothing, so node tests it alone): `GUIDE` (for each set, the line on what a student can do, its grids, tables and skills, and the order of its five from the easiest to the hardest), `sourceOfKey` (the hover words of every key form the sets write: table, entity, variable, time, the table's citation from `data/table_citations.json`, the method note), `figureRows` and `csvOf` (the CSV), `instructorNote`.
- **(1)** Every figure on a set page carries its source as its `title` (`Num`'s `source`).
- **(2)** `lib/problems.ts`: each set opens with a **worked example**, its answer open, built from keyed figures by one of the five's methods on other figures, so it gives none of the five answers away (A: question 1 on the day before; B: question 1 on the complete month before; C: question 1's method on Uri's demand; D: question 1's method on one day; E: question 3 on the held month before). Each question and example has **`line`, its one-line computation**, from the same keyed figures. The five are asked in `GUIDE`'s **rising order**; their ids are unchanged.
- **(3)** "After this set a student can ..." under each set's title.
- **(4)** The index lists each set's grids, tables (linked to `/data`) and skills, and **"The set's data, CSV"**: new address `/learn/problems/<set>/data.csv`, every keyed figure of the live set with its key, table, value, unit and source. A figure of a row held for a license is left out (`heldBy`). In review, the address answers the internal view alone.
- **(5)** A hover beside the index's title holds each set's table keys and `docs/methods/problem_sets.md`. Nothing else is visible.
- The method note `docs/methods/problem_sets.md` has a section for all of this.
- **Tests:** `site/scripts/test-problemkit.mjs` (`node --test`, 12 of 12) and `tests/test_session3650.py`, which runs it. `test_session288`'s slice of question e5 now ends at set E's new end. The problem set Python tests: 38 run, 0 failed. Before that fix, the 21 test files that name the sets: 244 run, 19 skipped, 1 error (that slice). `tsc --noEmit` reported no error in the changed files; 15 others are files a build generates. Not built.

## The sixth set

- **Not written.** The prompt asks for it only "if the five are already whole", and they were not: points 2 to 5 were missing. Also, `iso_queue_snapshot_summary` holds **0 rows in the live set** today (read with the anon key: built today in session 2953, not yet loaded). So a set reading it live could not have its fuel figures. `interconnection_durations_summary` is loaded (by grid and year, no fuel), but it is on the live set's `review_hold`.

## Decisions made without you

- The worked examples use one problem's method on other figures, never the same figures, so they give no answer away. Set C's first try (ERCOT's 2023 peak demand) would have given away question 4's demand day, so it was replaced.
- The rising order is by the moves a question needs: read and compare, then a maximum or sum over a range, then a complete month, a local day, a rule file or a ranking. The question ids are kept, so the edition files keep their names.
- The set's CSV is the **figures** (key, value, unit, source), read live, not the rows behind them; the dated edition's per-question CSVs remain for the rows. A route was used because a static file would not move with the data, and building a new edition would have meant a full read of the live set.
- Set B's grids are ERCOT, CAISO and SPP. `cost_of_power_monthly`'s ISO-NE, MISO and NYISO rows are held for a license, and the reader returns public rows only.
- The instructors' hover is the site's `Tip` mark ("i") beside the title, with no visible label.
- The 15 October edition and its teacher's copy are unchanged: their order is the old one, and they have no example and no computation line.
- **Process:** the shared checkout `Documents\erw` was on another window's branch (`wip/3600-batterygame`, with uncommitted edits), so my first commit of the prompt landed there. It was never pushed. I took it back with a soft reset, leaving that window's files as they were. All my work then ran in two worktrees of my own, `Documents\erw-3650` (the branch) and `Documents\erw-3650-main` (main). For the type check, `site\node_modules` was a junction to `Documents\erw-2254`'s, removed afterwards. The main checkout's `site\node_modules` was empty.

## For Samuel's ruling

- Should the 15 October edition be rebuilt so that the printed teacher's copy follows the live set's new order, example and computation lines? A new edition is one command (method note, "Dated editions").
- The new address `/learn/problems/<set>/data.csv` may need adding to the route check's list.
- Should the sixth set (the interconnection queue) be written once `iso_queue_snapshot_summary` is loaded and `interconnection_durations_summary` leaves `review_hold`?
- Visible text added: the "After this set" line, the "Worked example" section, "Computation." inside each answer, and the facts line on the index. The owner's rule keeps explanatory text to hovers; these were read as content the prompt asked for, not explanations.
