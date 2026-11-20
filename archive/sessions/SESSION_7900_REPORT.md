# Session 7900 report (17 November 2026, samueloldlaptop, code role): chain 402, the rulings in two lists

The chain: `queue/done/402-day-17-november-oldlaptop-rulings-ranked.md`, pasted by Samuel, run in one session. Model spend USD 0: no model API was called. No page, no default, no warehouse table and no landing was changed or requested.

## Rule 8, the live pages before and after

- Before: `runs/snapshots/c402-before`, 25 pages, 0 failed, 21:43 UTC. After: `runs/snapshots/c402-after`, 25 pages, 0 failed, 22:30 UTC.
- The comparison: **0 differences in all** (expected: every push to main of this session holds queue, state, review and session files only, no site file).
- No freeze (`scripts/freeze.py status`, exit 0). Precheck passed.

## What was done

- **The ground:** the chain file saved as pasted and pushed alone; the resume pointer `queue/next/420-resume-chain-402.md`; sessions 7900 to 7999 checked free on origin/main and every branch; the progress file `docs/state/progress_c402.md`.
- **Part 0, the severance tax tool:** every line of its measurement checked against the record. Line 3 (gas priced at 1.034 MMBtu a thousand cubic feet) was half written in a worktree: finished, with a test (8 of 8), on `wip/alt-severance-3`. Line 2 (the Texas Comptroller's collections in a hover) built on `wip/alt-severance-2` (7 of 7). Lines 4 to 7 are under 1 percent and add no figure. Claim marked done.
- **Part 0, the electricity bill page:** line 3 (the wholesale price over a meter-read span) finished on `wip/alt-bill-3` (6 of 6). Line 4's losses half built on `wip/alt-bill-4` (4 of 4; the replication and its committed page figures follow on the branch). Lines 2, 7 and 8 and line 4's load-zone half need data not held; lines 5 and 6 are under 1 percent. Claim marked done.
- **Part 0, tests run:** on each branch the page's own node tests, the python test files that name the page or its library, and a type check (15 errors, none in the files touched, the same count on each).
- **Part A, the ranked list:** `docs/reviews/rulings-ranked-2026-11-17.md`. All 40 measurement files and all 40 records of the branches read. 129 entries: 31 change a headline figure, 36 another figure, 62 add or remove one. Keep 15, switch 26, no basis 88. Pushed five times as it grew; the first push held the ten largest headline changes.
- **Part A, the pass over the first 30:** each number of each entry looked for in the measurement script's printout and in the branch's own tests (`runs/c402/check30.py`): all found there, but for a few percents and differences that are the measurement file's arithmetic on printed figures, and the subsidiaries' figures of one entry, which are the build's. One figure this session had derived was removed.
- **Part B, the defaults list:** `docs/reviews/rulings-defaults-2026-11-17.md`. 227 questions by page; 41 held by a license or a publisher and 3 needing the key listed apart; 31 signature lines.
- **The last session's steps:** the note `docs/state/note_2026-11-17_oldlaptop_c402.md`; the resume file removed; the queue step.

## What to review

- **The ranked list:** https://github.com/SamuelEnrique/erw/blob/main/docs/reviews/rulings-ranked-2026-11-17.md . Read the table of the first 30, then each entry; write after `Ruling:`. Each entry links its branch and, where the desktop has pushed them, the two pictures.
- **The defaults list:** https://github.com/SamuelEnrique/erw/blob/main/docs/reviews/rulings-defaults-2026-11-17.md . Rule "defaults stand", or strike lines. The three groups at its foot (licenses, the key, signatures) are not covered by a ruling on method.
- **The four new branches of part 0** (none asks to land): https://github.com/SamuelEnrique/erw/tree/wip/alt-severance-2 , https://github.com/SamuelEnrique/erw/tree/wip/alt-severance-3 , https://github.com/SamuelEnrique/erw/tree/wip/alt-bill-3 , https://github.com/SamuelEnrique/erw/tree/wip/alt-bill-4 . No page of production changed, so there is nothing to click on the site.

## Needs the key

- Nothing in this chain. USD 0.
- The defaults list sums what the open questions need: about USD 3.0 to 3.1 (up to about USD 10.7), and about USD 4.80 more for the chat's check on the large-load tables.

## Decisions made without you

- **What a headline figure is:** a number the page puts first (headline tiles, the first sentence, a calculator's result as it opens), in any view the page's own menu reaches. A figure that moves only after the reader types is in the second section.
- **The order:** by the largest percent the measurement gives for the question; points of a share ranked as percent; a choice that shows other figures and computes none differently ranked as 100 percent; the third section by the count of figures added or removed.
- **Four entries cover two lines each** (the event pages' held figures, the held grids' figures, the exchange's price indices, the map's copy of two held tables): the rulings list asks each twice.
- **Lines left out of the ranked list and put in the defaults list**, each with its reason on its line: under 1 percent; no change today (the data moved or main already does it); could not be measured.
- **"Figures that do not agree":** an entry is listed there whenever the measurement file and the record of the branch give one figure of it differently, also where the record explains why and where the two differ only by rounding. Twelve entries; none carries a recommendation, as the chain rules, and each says what would otherwise bear on it.
- **Not listed there:** the interconnection explorer's Texas counts (55 in the page's table, 44 in the newer queue file): the measurement's own printout gives both, and the branch's test agrees with it.
- **The grounds of the recommendations:** besides the two rulings files, the owner's rules of 16 November (a hold is never lifted or worked around) and the page standard were used as rulings already made. Where a method note records "(a ruling)" the entry says so. One recommendation (a month's average from the whole-month table, in the chat) rests on the nearest ruling, not an exact one, and says so.
- **Part 0, severance line 3:** the branch moves the calculator only, the cell the measurement names; the Lease tab and the finder still price one thousand cubic feet as one MMBtu on the branch.
- **Part 0, bill line 4:** the 5 percent is the question's own round figure; the page calls it an assumption, since no utility's loss factor is held.
- **The defaults list:** 23 lines that repeat another are given once; 3 lines that ask a question the ranked list holds are named at the foot; the page addresses inside a line are written as page names, and codes (request rows, session numbers) as their meaning.
- **The working files stay in `runs/c402/`** (not in git): the chain's product is the two lists.
- **A slip against the chain's rule on inline scripts:** two early commands held an inline script (a `printf` of the four browser rows; a short python edit of two entries). No prompt stopped the run. Everything after used Edit, Write and scripts under `runs/`.

## For Samuel's ruling

- The rulings themselves: 129 in the ranked list, 227 defaults.
- Whether "no recommendation where two sources differ" should bind where they differ only by rounding (three entries). Default taken: it binds.
- Whether the entries and the two scripts should be committed, so another machine can redraw the ranked list as pictures arrive. Default taken: not committed; this machine redraws.

## Faults seen, not fixed here

- The desktop found that the build of `wip/alt-events-1` draws one section of the December 2022 storm page as "license needed" only (in the record of the event pages).
- California's later large-load document prints "60 to 90 days" on its page 25 and the table's length is blank: a reading fault for the data machine (in the record of the datacenter cost page).
- Tests that fail the same on clean origin/main are named in the records of the branches; none was touched.
