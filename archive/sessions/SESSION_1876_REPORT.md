# Session 1876: the policy monitor's sixteen open faults fixed (chain 214, 12 November 2026)

Energy Research Warehouse (ERW). Chain 214, session 1876, samueloldlaptop, unattended, Opus 5.5. Worktree `C:\Users\lossa\Documents\erw-1876`, branch `wip/1876-policy` cut from the unlanded stack head `ddb6ac89a`. Nothing built, served, sent or written to the warehouse; no push to main or to a `task/` branch.

## What it did

- **Every open row of `docs/reviews/policy-faults-2026-11-11.md` fixed** in `site/lib/policymonitor.ts`, `site/app/policy/MonitorView.tsx`, `MonitorCalendar.tsx` and `MonitorCharts.tsx` (commit `2da59710`); the faults file updated to `fixed (2da59710, wip/1876-policy)` on rows 1, 2, 3, 4, 6, 9, 14, 16, 17, 19, 21, 22, 23, 26, 28 and 29 (commit `6768c140`).
- Row 1: `min-w-0` on the records section and the filters aside, so the table scrolls in its own box at 390 px.
- Row 2: `options(rows, f)` counts the rows the other filters leave (the list's own choice excluded); on the file of 6 November BSEE now reads 1 and FERC 97 at the opening filters. Every choice stays listed, at 0 where nothing is left.
- Row 3: `SECTOR_WORDS` ("LNG", "Grid conditions", ...) in the filter, the cell and the sector chart.
- Row 4: the calendar's week runs to the file's newest document when the file stops before today (heading "The file's last week", "2026-10-29 to 2026-11-05", the build date and the page's day in the hover); the month ahead still runs from today.
- Row 6: `floorHidden()` counts the month ahead's steps the significance floor hides; the empty line reads "None at significance 5 or more; 5 below it" with a link that lifts the floor (the other filters kept), and a non-empty list gets "N more below significance 5".
- Row 9: `whitespace-nowrap` on the Date cell and on the Next step's date.
- Row 14: `impactText()` cuts the final "; it bears on <table> (/data#...)" clause in the cell and the CSV; the hover names the document and the table.
- Rows 16 and 17: `nextOf(r, today)`: the first step on or after the page's day, else the last step, drawn "..., passed"; the cell carries the step's `stepKey` as `data-check` and its document in the hover; the Next step sort reads it, steps ahead before passed ones either way. At the opening filters 9 rows draw a step, 8 of them passed (the file's steps are few: row 7, the data machine's).
- Row 19: the figure sort tiers by unit (USD, then MW with GW and kW put in MW for the order only, then the others by unit name), values within a unit.
- Row 21: the Docs count is a `<button aria-expanded aria-controls>` that opens the row; the row's click stays.
- Row 22: the open row's proceeding ids as words ("FERC docket CP26-581", "RIN 2060-AW55", "FERC project 2538-106"; the id in the hover), each history line as date, instrument and status words and each document as a link to its own page (all 1,752 Register documents by their number in the address; the 268 others where the record has exactly one such document and one address left, which is every one in this file; otherwise no link is guessed), and the news as numbered links.
- Row 23: the table draws 50 rows, with a "Next 50 (50 of 293 drawn)" button; the CSV keeps every row shown.
- Row 26: the chart's last month reads "2026-11 to the 5th" when the file's last document is before the month's end.
- Row 28: the sums are gone. The table lists, by month and unit, the count of records stating a figure and the largest, with its record, words, document and `policyfig` key. `keysOf` gives no `policysum` key now; `scripts/check_policy.py`'s docstring says so and keeps `check_sum` for an older file's keys (no other change was needed: the largest figures are traced through their records' figure keys). `site/scripts/check-policy.mjs` checked no sum, so it is unchanged.
- Row 29: the CSV gains `plain_read`, `impact_quote`, `impact_model`, `impact_document`, `figure_document`, `steps` (kind=date@document, ";" joined) and `next_step_passed`; the `impact` column is the sentence without its clause, the next step is the page's; the Python and Stata readers list the columns.
- **Tests:** `site/scripts/test-policy-monitor.mjs` existed (session 3060), so it was extended rather than replaced: one block a row, 106 checks, numbers of the file of 6 November checked only on that file. `tests/test_session1876.py` (new) runs it and reads the components for each row. `tests/test_policy_monitor_page.py` follows rows 1 and 28 (two asserted strings changed with the classes and the key). Node test exit 0 (106 of 106); `pytest tests/test_session1876.py tests/test_session157_page.py tests/test_policy_monitor_page.py tests/test_check_policy.py` exit 0 (45 passed, 1 skipped).
- **Type check:** `npx tsc --noEmit` under the build lock, exit 2: 15 errors, every one `PageProps`, `LayoutProps` or `@/content/*.json`, which a build generates and this fresh worktree has not; none in the policy files. The lock was released.
- `site/node_modules` is a junction to the main copy's, left for the next session.

## Decisions made without you

- Row 28 took the first of the two fixes the file offered (the largest of each unit, no sum), for every unit the file holds, not only MW and USD; nothing is converted on the face.
- Row 6 took the link that lifts the floor, not a calendar without the floor, so the calendar still follows the filters.
- Row 4 kept the month ahead from today, since a deadline's date does not move with the file's build; only the week follows the file's last document.
- Row 16 draws a record whose steps are all past with its last step and the word "passed", as the faults file asked, rather than leaving the cell empty.
- The open row labels a document that is not in the Federal Register by its host ("nrc.gov"), the id in the hover.

## For Samuel's ruling

- None new. Rows 6 and 16 now say what the file holds, but the file holds few steps until the data machine widens the date rule (row 7).
- To finish: the gate's build and the snapshot of the page at 1280 and 390 (the scroll width probe for row 1), and a landing of `wip/1876-policy` through a `task/` branch.
