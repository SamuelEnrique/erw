# Session 7532 report: the Flex Alert scorecard (`/grid/caiso/alerts`) at the done line

Chain 304, second run (the owner's instruction of 16 November 2026), samueloldlaptop, code role. Branch
`wip/7532-caiso-alerts`, worktree `C:\Users\lossa\Documents\erw-7532`, from origin/main at `dd2dabe11`. Model spend USD 0
(`ERW_SPEND_CAP_USD=0`; no model called). Nothing built (memory), nothing landed, no table written, no data lock.

## What was done

- **Checked first:** no `replication/caiso_alerts/`, no `docs/methods/caiso_alerts.md` and no faults file on origin/main
  or any branch; `docs/methods/flex_alert_scorecard.md` is the analysis's method (with the page's keys), not a note of
  the page as a reader meets it, so a new note was written and the old one extended, not rewritten.
- **The method note** `docs/methods/caiso_alerts.md`: every view, every figure's table and rule, the rules a second
  implementation needs, what only the panel can rebuild, the decisions (11), what the tool does not hold. A dated line
  added to `flex_alert_scorecard.md`, section 3 (the report now runs to 2026-10-08, no alert day after 2024-07-24).
- **The page drawn without a build:** `site/scripts/caiso-alerts-figures.mjs` calls the page's own function, answers its
  three reads from the tables' files (the async source line drawn by a stream), and writes every figure it drew.
- **The replication** `replication/caiso_alerts/replicate.py` (standard library, from the notes and tables): 634 figures
  of the page; **471 rebuilt from the public tables, 467 inside half the last shown digit, 4 differ and are named, 0
  fail; 163 named as rebuildable only from the panel** (bootstrap intervals, the four other specifications, the error
  over hours, each day's temperature). The alert days rebuilt from CAISO's notices by the method's rule: 39, the 38
  scored and 2021-07-12. Runs again without the warehouse on `public_rows.csv` and `notices_rows.csv` beside it.
  `replicate.do`: five headline figures, expected values at its top (not run: no Stata here).
- **The cross-check** `docs/reviews/caiso-alerts-crosscheck-2026-11-16.md`: CAISO's Grid Emergencies History Report
  (revision 10/09/2026, read today, robots and terms first): 66 of 71 year-kind counts equal; CAISO's own summary says 5
  EEA 2 days in 2022 where its record pages list 4; the page's alert days by year against CAISO's Flex Alert days, each
  difference explained; the U.S. EIA's account of 6 September 2022 against the page's estimate for that day.
- **The decisions block** `site/app/grid/caiso/alerts/Decisions.tsx`, mounted at the foot: 11 fixed choices, default,
  source and session on hover; the note's section 6 holds the same list (tested).
- **Faults** `docs/reviews/caiso-alerts-faults-2026-11-16.md`: 11 rows: 3 site fixed (whole dollars under a million;
  the title's years and the last caution from the rows, the notices read to the day drawn; the unscored alert day on
  hover), 2 notes completed, 1 data machine, 5 rulings.
- **Tests:** `tests/test_session7532_caiso_alerts.py` 15 passed; `site/scripts/test-caiso-alerts-render.mjs` 30 of 30;
  the test files naming the page or its libraries (`test_session58`, `60`, `118`, `241a`, `246`, `254`, `310`, `322`):
  116 run, OK (8 skipped by their own rules); the note sweeps `test_session142`, `147`, `158`, `160`: OK; `tsc` with the
  site's settings on `page.tsx` and `Decisions.tsx`: exit 0.

## What to review

1. `https://erw-flame.vercel.app/grid/caiso/alerts` (in review: with the review cookie). The title reads "CAISO, 2018 to
   2024" (now from the rows).
2. "Every alert day, ranked": the "i" after "from July 2018 to 2024-07-24": the tip names 2021-07-12 as not scored and
   the 2021 difference. The row 2023-07-20, "Value, USD": "-479,791" (it read "-479,791.004").
3. "What the estimate can and cannot say", the last but one point: "runs to 2026-10-08; it lists no Flex Alert or
   emergency notice after 2024-07-24, so the seasons since have none here" (it said the report ran to 2025-04-30).
4. The foot of the page: the fold "Decisions on this page (11)"; open it, hover or tap each "i".
5. The row 2020-10-01: "CAISO's notices" reads "Alert" (row 3, data machine: the Flex Alert for that day is dated 30
   September in the table).

## Needs the key

Nothing. No step of this tool calls a model.

## Decisions made without you

- A new note for the page (`caiso_alerts.md`) beside the analysis's method, which is extended by a dated line, not
  rewritten.
- The replication counts as rebuilt only what the public tables can rebuild; the 163 figures that need the scorecard's
  panel (NOAA weather is not on this machine) are named one by one with their reason, never counted as agreeing.
- The last caution is computed from the notices the page reads (now to the day it is drawn): how far they run, and any
  alert-kind day after the last scored day, named as not yet held. If the notices cannot be read, it says so.
- The unscored alert day is a fixed hover, dated to the run of 2 October 2026, because the 2020-09-30 dating fault (row
  3) would make a computed list name a wrong day until the data machine fixes it.
- CAISO's record pages are taken over its summary table where they disagree (2022 EEA 2: 4, not 5).

## For Samuel's ruling

- **Double rounding** (faults row 6): two cells are one off in their last digit (-0.18 for -0.17497; -16,893.33 for
  -16,893.3249) because the table stores three decimals and the page rounds again. Default: no change. The other
  choice: the builder writes four decimals (a data request).
- **Grey text** (row 8): 13 grey and 13 small-type marks on the page, against the standard of hover tips only.
  Default: no change until a session with a browser can move them.
- **390 px** (row 9): the ranked table and the table of models scroll sideways inside their frames. Default: no change;
  browser read 86 asks what a phone shows. The other choice: four columns at 390 px, the rest on tap.
- **CAISO's EEA 2 count** (row 10): default, the records (4 days), as the table has it.
- **One clause takes a view** (row 11): "the size a statewide conservation call might plausibly have". Default: kept.
  The other choice: drop the clause and keep the fact (the hot-day error).

## Rows for the coordinator

### (a) The landing request (row 30)

| 30 | `wip/7532-caiso-alerts` | `<head of the branch>` | `7532-caiso-alerts` | 7532 | 2026-11-16 | `tests/test_session7532_caiso_alerts.py` (15 passed) and `site/scripts/test-caiso-alerts-render.mjs` (30 of 30, the whole page drawn to HTML with its own function, without a build); the older test files that name the page or its libraries, `test_session58`, `60`, `118`, `241a`, `246`, `254`, `310`, `322` (116 run, OK, 8 skipped by their own rules); the note sweeps `test_session142`, `147`, `158`, `160`: OK; `tsc` with the site's settings on `page.tsx` and `Decisions.tsx`, exit 0; `replication/caiso_alerts/replicate.py` on this machine's tables and again on the rows beside it: 471 rebuilt, 467 agree, 4 named, 0 fail, 163 named as panel-only, exit 0; not built here (memory); `check-values` and `check-routes` not run | requested |

## Row 30: what it holds (chain 304, session 7532, the Flex Alert scorecard at the done line)

- **Stacked on** origin/main at `dd2dabe11`. Report: `archive/sessions/SESSION_7532_REPORT.md` on the branch.
- **What changes:** `/grid/caiso/alerts` (`site/app/grid/caiso/alerts/page.tsx`, the new `Decisions.tsx`): a dollar
  figure under a million in whole dollars (2023-07-20 read "-479,791.004"); the title's years from the rows; the last
  caution says how far CAISO's notices run and whether any alert day follows the last scored one, from the rows (it
  said "runs to 2025-04-30"), and the notices are read to the day the page is drawn (they stopped at 2025-10-31); a
  hover beside the ranked table's lead names 2021-07-12 as not scored; the fold "Decisions on this page" (11 choices,
  server-drawn words, no handler, no state, no new request). New: `docs/methods/caiso_alerts.md`,
  `replication/caiso_alerts/`, `docs/reviews/caiso-alerts-faults-2026-11-16.md`,
  `docs/reviews/caiso-alerts-crosscheck-2026-11-16.md`, `site/scripts/caiso-alerts-figures.mjs`,
  `site/scripts/test-caiso-alerts-render.mjs`, `tests/test_session7532_caiso_alerts.py`; a dated line in
  `docs/methods/flex_alert_scorecard.md`.
- **What does not change:** every figure the page draws from the two tables (the 433 checked numbers are the same rows
  and keys), the charts, the sections, `site/lib/flexalerts.ts`, `site/lib/reliability.ts`, `site/lib/release.ts`, every
  table.
- **Before landing:** a build on the landing machine (the first build of the page's two files; `tsc` passed here), and
  `check-values` on `/grid/caiso/alerts` (the same keys as before). The notices read now ends on the day drawn instead
  of 2025-10-31: 320 rows instead of 314 on this machine's table.
- **Snapshot differences to expect:** none on the 25 addresses (the page is not among them; every page is in review).
  With the review cookie: `/grid/caiso/alerts` differs by the title's words (the same years), the 2023-07-20 value cell,
  the hover by the ranked lead, the last caution's words, and the fold at the foot; `/data/methods/caiso_alerts` is new.
  **Tables:** none.
- **After the landing:** rows 86 to 89 of `docs/state/browser_reads_wanted.md`; data request row 59.

### (b) Browser reads (rows 86 to 89)

| 86 | 2026-11-16 | 7532 | `wip/7532-caiso-alerts` (row 30) | `https://erw-flame.vercel.app/grid/caiso/alerts` | "Every alert day, ranked" and the table of models under "The answer, pooled", at 390 px | Whether either table scrolls sideways inside its frame (the page standard says it should not); a screenshot of each at 390 px for the ruling of faults row 9 | wanted |
| 87 | 2026-11-16 | 7532 | `wip/7532-caiso-alerts` (row 30) | `https://erw-flame.vercel.app/grid/caiso/alerts` | The "i" after "from July 2018 to 2024-07-24" in the lead of "Every alert day, ranked": hover, tap and keyboard focus, at 1280 and 390 px | A tip naming 2021-07-12 as not scored and the 2021 difference (2021-07-29 counted, a Warning only); it stays inside the screen at 390 px | wanted |
| 88 | 2026-11-16 | 7532 | `wip/7532-caiso-alerts` (row 30) | `https://erw-flame.vercel.app/grid/caiso/alerts` | The fold "Decisions on this page (11)" under the source line; open it, hover and tap each "i", at 1280 and 390 px | Closed to start; 11 lines; each tip shows Default, Source and Made in; no grey text in the lines; no sideways scroll | wanted |
| 89 | 2026-11-16 | 7532 | `wip/7532-caiso-alerts` (row 30) | `https://erw-flame.vercel.app/grid/caiso/alerts` | The title; the row 2023-07-20 of the ranked table, column "Value, USD"; the last but one point of "What the estimate can and cannot say", on the live set | "CAISO, 2018 to 2024"; "-479,791"; "runs to 2026-10-08; it lists no Flex Alert or emergency notice after 2024-07-24, so the seasons since have none here" (the date the live set's latest notice) | wanted |

### (c) Data request (row 59)

| 59 | 2026-11-16 | 7532 (chain 304, samueloldlaptop; branch `wip/7532-caiso-alerts`) | `caiso_grid_emergencies` (`warehouse/connectors/caiso_emergencies.py`) | The Flex Alert for Thursday 1 October 2020 is dated 2020-09-30, the day it was issued (`event_id` `caiso_awe:2020-09-30:flex_alert:21b382e6b2`, time frame "10/1/2020 15:00:00 through 22:00:00", text "effective Thursday, October 1, 2020"), against the table's rule of a row per day covered. Read the text's day for the form "M/D/YYYY HH:MM:SS through HH:MM:SS" as `warehouse/derived/flex_alert_scorecard.py` does (`window()`), rewrite the table and load it; the event id changes with the day. The scorecard's tables need nothing. Then `/grid/caiso/alerts` shows "Alert, Flex Alert" on 2020-10-01 and `/grid?grid=caiso` counts the Flex Alert on 1 October | `docs/reviews/caiso-alerts-faults-2026-11-16.md`, row 3 | requested |

### (d) The progress line (part A, tool 12)

| 12 | `/grid/caiso/alerts` | `wip/7532-caiso-alerts` | done `<head>` on `wip/7532-caiso-alerts` (landing row 30): the note `docs/methods/caiso_alerts.md` (new, the page as a reader meets it) and a dated line in `flex_alert_scorecard.md`; the replication 467 of 471 rebuilt figures inside half the last digit, 4 named differences (two double roundings, one tie, one dating fault), 0 failed, 163 named as panel-only, the alert days rebuilt from CAISO's notices (39 by the rule, 38 scored); the cross-check against CAISO's Grid Emergencies History Report of 9 October 2026 (66 of 71 year-kind counts equal; CAISO's summary says 5 EEA 2 days in 2022, its records 4) and the EIA's account of 6 September 2022; the decisions block, 11 choices; faults: 11 found, 3 fixed, 1 data machine, 2 notes completed, 5 rulings | 7532 |
