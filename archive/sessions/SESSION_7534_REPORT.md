# Session 7534 report: the problem sets (/learn/problems) at the done line

Chain 304's second run (the owner's instruction of 16 November 2026), samueloldlaptop, code role, unattended. Branch
`wip/7534-learn-problems`, from origin/main `64da63865`. Model spend USD 0 (`ERW_SPEND_CAP_USD=0`; no model called).

## First: one thing that went wrong

- **Held rows were pushed once.** The first commit (`710c68ce5`, pushed) kept every row the live set's read returned,
  and the read of `cost_of_power_monthly` returns ISO-NE's, MISO's and NYISO's hub rows before the site's reader drops
  them: 702 rows a license holds, in `replication/problem_sets/live_rows.csv`. The next commit (`d2cad3257`) removed
  them and the recorder now drops them with the site's own rule (`licenseHeldRow`); a test holds that none is kept. The
  rows stay in the branch's history: no force push here. For Samuel's ruling below.
- Two shell commands of mine waited on standard input (a bare `python -`, then an empty heredoc); each was stopped at
  once, nothing ran.

## What was done (the five parts)

- **The method note completed** (`docs/methods/problem_sets.md`, extended, nothing removed): every view (index, a set,
  the edition's students' and teacher's copies, the CSV), every figure's table and rule in one table (31 rows), the
  15 decisions, what the sets do not hold, the replication and the cross-check.
- **The replication** (`replication/problem_sets/replicate.py`, standard library, from the note and each question's
  stated rule): on the reads the five sets made of the live set at 2026-11-16T22:51:27Z (kept: `live_reads.json`,
  `live_rows.csv`, with the hourly network snapshot), **146 of 146** checks (every figure by check key within half its
  last shown digit, and every answer given in words: days, months, hours, hubs, the neighbor, "different days"); the
  edition of 15 October from its own downloads, **89 of 92**, 3 named (its network hour is not kept). What the page
  shows comes from `site/scripts/problem-sets-figures.mjs`: the five live pages, both edition copies and the index
  drawn to HTML with the site's own code; every figure found in the HTML by key and text, or drawn "license needed"
  where the page holds it (47 occurrences, 13 figures). A replay of the kept reads through the page's code gives the
  kept figures again (the test). `replicate.do`: five headline figures in Stata (no Stata here; its five values checked
  in Python: 2.08, 47.74, 1.12, 24.88, 73.06).
- **The cross-check** (`docs/reviews/problem-sets-crosscheck-2026-11-16.md`, 13 rows): Uri's demand -0.9 percent
  against FERC's 69,871 MW; Elliott's PJM peak +32 MW against PJM's 135,296; ERCOT 2023 -32 MW against ERCOT's 85,464;
  CAISO 2020's highest day the same as CAISO's root cause report; Oncor's bill equal to EIA's July Texas average by
  construction; PG&E's default bill +28.6 percent over EIA's August California average (a definition: tier 3, no
  discount, all utilities in EIA's); the tax rules and the certified price against their quoted sources; the debt
  service formula against Lazard's own illustration. No new web request: the event documents were read today by
  session 7531 (robots first; nerc.com not read), cited as it read them.
- **The decisions block** (`site/app/learn/problems/Decisions.tsx`): 15 choices, each with default, source and session
  on hover; each set's page draws its own (2 to 7), the index all 15. No input, so nothing editable in place.
- **The faults** (`docs/reviews/problem-sets-faults-2026-11-16.md`, 9 rows): 4 site fixes (one with a ruling), 2 data
  machine, 2 rulings, 1 fixed on another branch.

## The site fixes (`site/lib/problems.ts`)

- Set D question 1 summed six days as "the seven latest days held" (a 12-day window over the live set's gap of 4 to 8
  November): now 45 days, seven days held (3 and 9 to 14 November), and the count said when fewer.
- Set B question 2 read "The table holds 4 hubs" of a table of seven: now "The table's public rows hold 4 hubs".
- Set D question 5 read "80 Mcf a day over 30 days" for August: now the month's own days (77.4 over 31).
- Set D question 4 typed New Mexico's rates and not their period: now read from the rules file with "the rates the
  rules file states for 2026-04-01 to 2026-08-31 (TRD table) (the newest it holds; 2026-10 is later)".

## Tests

- `tests/test_session7534_problem_sets.py` (8 passed: the replication, no held row kept, the do-file, the replay equal
  to the kept figures, the decisions block, the fixes, no em dash); `site/scripts/test-problem-sets-render.mjs` (ok: 5
  sets, 15 choices, the note's list equal).
- The 22 older test files that name the problem sets (`test_session121`, `149_checks`, `203`, `237`, `239`, `242`, `251`,
  `252`, `286`, `288`, `293`, `3650`, `369`, `4051`, `408`, `44`, `5160`, `5171`, `53`, `55`, `801`, `92`): 231 passed,
  34 skipped by their own rules, after one pin of `test_session288` moved to the new words of set B question 2 (its
  reason in the file). Not built (no memory); `check-values` and `check-routes` not run.

## What to review

- `https://erw-flame.vercel.app/learn/problems/storage-and-taxes`: question 1 reads "Over the seven latest days held
  (2026-11-03 to 2026-11-14)" (dates move with the data); question 5 "(77.4 Mcf a day over its 31 days)"; open question
  4's answer, the New Mexico step names the rules' period. At the foot, open "Decisions on this page (7)", hover an "i".
- `https://erw-flame.vercel.app/learn/problems/prices-and-your-bill`: question 2 starts "The table's public rows hold
  4 hubs". Foot: 4 decisions.
- `https://erw-flame.vercel.app/learn/problems`: at the foot, "Decisions on this page (15)".
- `https://erw-flame.vercel.app/learn/problems/when-the-grid-broke`: unchanged; seven figures still "license needed"
  (faults row 7, a ruling).

## Needs the key

- Nothing. No step of this tool calls a model.

## Decisions made without you

- The live page's figures were taken from the live set itself (read-only, the anon key), every read kept beside the
  replication, so the replication runs on any copy without the network and a test replays the page's code on the
  same rows.
- The bill fix (faults row 8) is session 7533's on `wip/7533-learn-bill`; not repeated here, to avoid two edits of
  `components/Num.tsx`.
- The EIA-930 hold on set C follows session 7531's ruling row (unchanged), so the two tools say one thing.
- A tax is the base tax, fees left out, as the page does; written as a decision (`tax`).

## For Samuel's ruling (each with the default taken)

1. **The held rows in the branch's history** (commit `710c68ce5`): rewrite the branch before it lands, or land it as it
   is. Default: not rewritten (no force push from a chain); the landing machine may squash.
2. **New Mexico's rates after 31 August 2026**: a session reads the Taxation and Revenue Department's table and extends
   `severance_rules.json`, or the page keeps saying which period it uses. Default: kept, the period said.
3. **EIA-930's figures of set C drawn "license needed"**: (a) name EIA-930's entities to their grids, (b) read them as
   rows of no grid, kept, (c) as now. Default: (c), as session 7531's row 1.
4. **An edition's students' download holds the answers of computed figures** (and no tie rows for the network
   questions): (a) from the next edition, leave an answer out and write its inputs; (b) as now. Default: (b).

## Rows for the coordinator

### (a) Landing request

| 32 | `wip/7534-learn-problems` | `94807c6a8` (the report on top) | `7534-learn-problems` | 7534 | 2026-11-16 | `tests/test_session7534_problem_sets.py` (8 passed) and `site/scripts/test-problem-sets-render.mjs` (5 sets, 15 choices, the note's list equal); the 22 older test files that name the problem sets: 231 passed, 34 skipped by their own rules (one pin of `test_session288` moved to the new words, its reason in the file); `replication/problem_sets/replicate.py` 146 of 146 live and 89 of 92 of the edition (3 named), exit 0; not built here (memory); `check-values` and `check-routes` not run | requested |

## Row 32: what it holds (chain 304, session 7534, the problem sets at the done line)

- **Stacked on** origin/main `64da63865`. Report: `archive/sessions/SESSION_7534_REPORT.md` on the branch.
- **What changes:** `site/lib/problems.ts` (set D question 1 reads 45 days and sums the seven latest days held; set B
  question 2's words "The table's public rows hold"; set D question 5's days of the month; set D question 4's New
  Mexico step from the rules file with its period); the new `site/app/learn/problems/Decisions.tsx`, mounted at the foot
  of `site/app/learn/problems/page.tsx` and `[slug]/page.tsx` (a fold, server-drawn words, no handler); the note, the
  replication folder, the two reviews, the scripts `site/scripts/problem-sets-*.mjs` and `test-problem-sets-render.mjs`,
  the test, and one pin of `tests/test_session288.py`.
- **What does not change:** every check key and figure of sets A, B, C and E; the editions' files; `site/lib/release.ts`;
  every table.
- **Before landing:** a build (the first of the three site files); `check-values` on the problem sets (set D question
  1's keys change with its window: `series_sum|storage_daily_cycle|...|<first of the seven days>|...`). Decide ruling 1
  (the held rows in the branch's history) before the merge; a squash keeps them off main.
- **Snapshot differences to expect:** none on the 25 addresses. With the review cookie: `/learn/problems` gains the
  fold; each set's page gains its fold; `storage-and-taxes` question 1 its days and figures, question 5 its words,
  question 4's New Mexico step; `prices-and-your-bill` question 2 its first words. **Tables:** none.
- **After the landing:** browser reads rows 106 to 110; data requests rows 79 and 80.

### (b) Browser reads

| 106 | 2026-11-16 | 7534 | `wip/7534-learn-problems` (row 32) | `https://erw-flame.vercel.app/learn/problems/storage-and-taxes` | The fold "Decisions on this page" at the foot; hover and tap an "i"; at 390 px | Closed to start; 7 lines; each tip shows Default, Source and Made in, stays inside the screen at 390 px, no sideways scroll | wanted |
| 107 | 2026-11-16 | 7534 | `wip/7534-learn-problems` (row 32) | `https://erw-flame.vercel.app/learn/problems` | The fold at the foot of the index | "Decisions on this page (15)"; 15 lines with tips; no sideways scroll at 390 px | wanted |
| 108 | 2026-11-16 | 7534 | `wip/7534-learn-problems` (row 32) | `https://erw-flame.vercel.app/learn/problems/storage-and-taxes` | Question 1's words; question 5's words; open question 4's answer | "Over the seven latest days held (<first> to <last>)" with seven days; "(<n> Mcf a day over its <d> days)" with the month's days; the New Mexico step names "the rates the rules file states for 2026-04-01 to 2026-08-31 (TRD table)" | wanted |
| 109 | 2026-11-16 | 7534 | `wip/7534-learn-problems` (row 32) | `https://erw-flame.vercel.app/learn/problems/prices-and-your-bill` | Question 2's first words; the fold at the foot | "The table's public rows hold 4 hubs: CAISO NP15, CAISO SP15, ERCOT hub average, SPP North hub."; 4 decisions | wanted |
| 110 | 2026-11-16 | 7534 | `wip/7534-learn-problems` (row 32) | `https://erw-flame.vercel.app/learn/problems/when-the-grid-broke` | The worked example and questions 2, 3, 4: hover "license needed" | Seven figures drawn "license needed" with the publishers on hover (unchanged, Samuel's ruling 3 of the report); the fold shows 2 decisions | wanted |

### (c) Data requests

| 79 | 2026-11-16 | 7534 (chain 304, samueloldlaptop; branch `wip/7534-learn-problems`) | `storage_daily_cycle` (`warehouse/derived/storage_daily_cycle.py` on `eia930_all_storage`) | ERCOT (`eia930:ERCO`), 2026-11-14: 3,755 MWh discharged and 24,833 MWh charged, round trip 0.151, against 26,495 to 32,528 MWh discharged on 9 to 13 November: a local day written before its hours were all in. Rebuild the day, and write no local day whose hours are not all held (or write the count of hours held, so a reader can tell). It moves the problem sets' know-your-grid questions 3 and 5 and storage-and-taxes question 1 and its worked example (faults row 5) | EIA-930 battery hours (`eia930_all_storage`); `docs/reviews/problem-sets-faults-2026-11-16.md` row 5 | requested |
| 80 | 2026-11-16 | 7534 (chain 304, samueloldlaptop; branch `wip/7534-learn-problems`) | `storage_daily_cycle` and `eia930_all_storage` | No ERCOT day of 4 to 8 November 2026 in the live set's `storage_daily_cycle` (session 4051 named the same gap in EIA-930). Check whether EIA-930 now holds ERCOT's battery hours of those days; if so, pull and rebuild them; if not, nothing to do | EIA, Hourly Electric Grid Monitor (Form EIA-930); faults row 6 | requested |

### (d) Progress line

| 14 | `/learn/problems` | done `94807c6a8` on `wip/7534-learn-problems` (landing row 32): the note `docs/methods/problem_sets.md` completed (every view, 31 figure rules, 15 decisions, what the sets do not hold); the replication 146 of 146 on the live sets' kept reads (figures by key and answers in words) and 89 of 92 of the edition of 15 October (3 network figures named: the hour is not kept), `replicate.do` five headline figures; the cross-check 13 rows (event peaks within 0.02 to 0.9 percent of FERC's, PJM's and ERCOT's own; bills against EIA's retail averages; tax rules and Lazard's illustration); the decisions block (15 choices on the index, 2 to 7 on each set's page); faults: 9 found, 4 fixed (one with a ruling), 2 data machine, 2 rulings, 1 fixed on `wip/7533-learn-bill` | 7534 |
