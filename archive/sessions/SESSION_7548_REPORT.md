# Session 7548 report: the problem sets (/learn/problems) read as their reader

Chain 304, part B form (this machine's own tool), samueloldlaptop, code role, unattended, 16 November 2026. Branch
`wip/7534-learn-problems-b` (the tool's own), worktree `C:\Users\lossa\Documents\erw-7534`, from `430032463` (the done
line). Model spend USD 0 (`ERW_SPEND_CAP_USD=0`; no model called). No web request, no table written, no data lock.

## First: what went wrong

- One shell command of mine was a bare `python -` (it waits on standard input). It was stopped at once; nothing ran.

## What was done

- **The read:** `docs/reviews/problem-sets-read-2026-11-16.md`. The reader: an undergraduate working problem set 3
  ("When the grid broke: four events") start to finish for a class on 17 November 2026, and the instructor who sets it.
  Five cases: the live page against the edition of 15 October; the worked example and Elliott from the table; Uri's
  price from the edition's download; set 3 against `/events`; questions of sets 2, 4 and 5 against `/learn/bill` and
  `/storage`. Every page drawn to HTML with the site's code on session 7534's kept reads (no network).
- **13 rows:** 6 site, fixed with a test; 1 data machine, already requested (data request 79); 3 browser (four rows,
  246 to 249); 3 rulings.
- **The site fixes:**
  - Each live question says its number in the edition of 15 October 2026, and each edition question its number on the
    live page: in every set the two orders differ (set 3's live question 1 is the edition's 3).
  - The decisions block names questions by their live numbers (five of eight lines named the ids' numbers); on the index
    each line names its set; the baseline line cited `docs/methods/event_window.md`, which does not exist.
  - Set 3 names each event's window (equal to `/events` and the events note, held by the test), names ERCOT's hub
    average in its price questions, and names the three CAISO days with no comparison.
  - Set 4: the seven days held are named when the table has a gap; the fleet of 10,000 homes is said in the question.
  - Set 5 question 5: "the same dates of earlier years", not "before the storm".
- **Shared figures:** set 3's four headline figures equal `/events`' cards; ERCOT's battery day equals `/storage`'s
  latest row; the bills' month and prices equal `/learn/bill`'s rule. All held by the test on the kept rows.
- **The method note** extended (two numberings); `replication/problem_sets/page_figures.json` replayed from the kept
  reads with the new words (no figure or key moved); `replicate.py` 146 of 146 live, 89 of 92 of the edition (3 named).

## Tests

- `site/scripts/test-problem-sets-read.mjs` (new): ok (5 sets, both numberings, 4 windows, 8 decision lines, 7 shared
  figures, 5,803 kept rows and 323 figure keys with none held by `licenseHeldRow`).
- `tests/test_session7548_problem_sets_read.py` (new) with the 23 test files that name the problem sets
  (`test_session121`, `149_checks`, `203`, `237`, `239`, `242`, `251`, `252`, `286`, `288`, `293`, `3650`, `369`, `4051`,
  `408`, `44`, `5160`, `5171`, `53`, `55`, `7534_problem_sets`, `801`, `92`): 236 passed, 34 skipped by their own rules.
- `node --test scripts/test-problemkit.mjs` 12 of 12; `test-problem-sets-render.mjs` ok. Not built (memory);
  `check-values` and `check-routes` not run (no check key changed).

## What to review

- `https://erw-flame.vercel.app/learn/problems/when-the-grid-broke`: under each question, "In the edition of 15 October
  2026 this is question N." (question 1: 3; question 4: 1); the questions name their windows and ERCOT's hub average;
  open question 2's answer: the first step names 2020-08-10, 2020-08-11 and 2020-08-23.
- `https://erw-flame.vercel.app/learn/problems/when-the-grid-broke/2026-10-15` and `.../teacher`: under each question,
  "On the live page this is question N." (question 1: 4).
- `https://erw-flame.vercel.app/learn/problems/storage-and-taxes`: question 4 says "fleet of 10,000 homes"; open question
  2: the first step names the days held. The fold: "Question 2 adds the seven latest days".
- `https://erw-flame.vercel.app/learn/problems/prices-and-your-bill`: the fold reads "Questions 2 and 3 take the default
  bills" and "Question 5 ranks the hubs".
- `https://erw-flame.vercel.app/learn/problems`: the fold, each line opens with its set ("Every set: ...").
- `https://erw-flame.vercel.app/learn/problems/networks-and-money`: question 5 ends "(the same dates of earlier years)?".

## Needs the key

- Nothing.

## Decisions made without you

- The edition's own order is kept (it is frozen, and a printed copy may be in a class's hands); each page says the
  other's number instead of reordering either.
- The windows are written once in `lib/problems.ts` and held equal to `/events`' cards by the test, not read from the
  event pages' code.
- No figure of set 3 is unblanked: the hold logic is not touched (row 7, the known fault).

## For Samuel's ruling (each with the default taken)

1. **Set 3's EIA-930 figures** (row 7): blank on the live page and on `/events`, drawn in the edition. Default: as now;
   an instructor uses the edition for set 3. The choices are session 7531's.
2. **The edition's downloads for a maximum** (row 8) hold the two answer rows, not the window's rows. Default: as now
   (frozen); the other choice: the next edition writes every row of the window.
3. **Numbered sets** (row 9). Default: none (sets are named). The other choice: "Set 1" to "Set 5".

## Rows for the coordinator

### (a) Landing request: no new row; row 32's head moves

- Row 32's head: `wip/7534-learn-problems-b` at the commit carrying this report (given in the session's return).
- One line to append to "## Row 32: what it holds":
  - **The read (session 7548):** `docs/reviews/problem-sets-read-2026-11-16.md`; six site fixes in `site/lib/problems.ts`, `site/lib/problemkit.ts`, `site/app/learn/problems/Decisions.tsx`, `[slug]/page.tsx` and the edition's two copies (the live and edition numbers on each question, the decisions' live numbers and set names, set C's windows and hub, set D's days held and fleet, set E question 5's words); `page_figures.json` replayed (words only). No check key changes. Tests: `site/scripts/test-problem-sets-read.mjs`, `tests/test_session7548_problem_sets_read.py`. Browser reads rows 246 to 249; no data request.

### (b) Browser reads

| 246 | 2026-11-16 | 7548 | `wip/7534-learn-problems-b` (row 32) | `https://erw-flame.vercel.app/learn/problems/when-the-grid-broke`, then `.../when-the-grid-broke/2026-10-15` and `.../2026-10-15/teacher` | Under each question: the line with the other copy's number; click the edition link; print preview of the teacher's copy | Live question 1 "In the edition of 15 October 2026 this is question 3.", question 4 "... question 1."; the link opens the students' copy; on it question 1 "On the live page this is question 4."; the line is in the teacher's print | wanted |
| 247 | 2026-11-16 | 7548 | `wip/7534-learn-problems-b` (row 32) | `https://erw-flame.vercel.app/learn/problems/when-the-grid-broke` | The questions' words at 390 px; open question 2's answer | Each question names its window ("2021-02-07 to 2021-02-24" and the others) and the price questions "ERCOT's hub average, HB_HUBAVG"; question 2's first step names 2020-08-10, 2020-08-11 and 2020-08-23; no sideways scroll | wanted |
| 248 | 2026-11-16 | 7548 | `wip/7534-learn-problems-b` (row 32) | `https://erw-flame.vercel.app/learn/problems/storage-and-taxes` and `.../networks-and-money` | Storage question 4's words and computation; open question 2; networks question 5 | "fleet of 10,000 homes" in the question and "times the fleet's 10,000 homes" in the computation; "the days held are <first> and <run>" when the table has a gap; "(the same dates of earlier years)?"; no sideways scroll at 390 px | wanted |
| 249 | 2026-11-16 | 7548 | `wip/7534-learn-problems-b` (row 32) | `https://erw-flame.vercel.app/learn/problems` and `.../prices-and-your-bill` | Open the fold "Decisions on this page" on each; hover an "i" | Index: each line opens with its set in bold ("Every set:", "Prices and your bill:", ...); the set page's lines have no set name and read "Questions 2 and 3 take the default bills", "Question 5 ranks the hubs"; tips inside the screen at 390 px | wanted |

### (c) Data requests

- None. Row 10 of the read is data request 79 (session 7534), not asked again. Reserved rows 219 to 228 unused.

### (d) Progress line (part C table form)

| /learn/problems (read) | samueloldlaptop | done `<head>` on wip/7534-learn-problems-b (landing row 32): the reader an undergraduate working problem set 3 (When the grid broke) start to finish and the instructor setting it from the edition of 15 October 2026; five cases (the live page against the edition, the worked example and Elliott from the table, Uri's price from the edition's download, set 3 against /events, sets 2, 4 and 5 against /learn/bill and /storage); rows: 13 (6 site fixed, 1 data machine already requested, 3 browser, 3 rulings); the shared figures agree with /events, /storage and /learn/bill | 7548 |
