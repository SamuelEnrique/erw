# Session 10404 report: chain 720, part E goes on (the value check, a problem set, the second window's rows 5 and 6)

Energy Research Warehouse (ERW). 26 November 2026, the portable laptop's first window (code role), unattended. Kept current while part E goes on.

## Found before the landing: the site's value check would have failed on both new pages

- **What the check is:** `site/scripts/check-values.mjs` reads every figure a page draws with its key, reads the same figure again from the file or the table, and wants the text on the page to be that figure written its way (two decimals, or a whole number).
- **`/forecast` failed 70 figures.** The page writes a megawatt of demand whole ("54,040"); the check wanted two decimals of 54039.5. All 70 are hours of tomorrow's table.
- **`/equities` failed 21 of its 43 figures.** The page writes a rise with its sign ("+0.32%"); the check wanted "0.32".
- **Neither is a wrong number.** Both are the page's way of writing a right one. Left alone, the first full value check after the landing would have failed on both pages.
- **Mended in the check, not on the pages,** as earlier sessions did for other pages that write megawatts whole: one rule for each page, each on its own line, each pinned in the page's test. The pages are unchanged.
- **After:** 1,797 of 1,797 figures pass on `/forecast` (two addresses), `/equities`, `/board` and the problem set, in a build of everything that is to land with the files read from `site/data` as production will.
- **Why it was missed until now:** the check was never run on these pages. It needs a served build and the files in the site's own folder; until 14:16 UTC the files were only in the other windows' branches. This window's own checks compared figures with files (60,474 and 1,092 figures, none differing) and not the text's form.
- **Rows 54 and 55 moved one commit each** (`abdf999f2`, `b06045762`). The desk's next gate held the earlier heads; the rows ask it to take the commits past them.

## A problem set for the forecast page (row 56)

- **"A forecast's report card"**, at `/learn/problems/a-forecasts-report-card`: a worked example and six questions, every figure read from `site/data/predict/scores.json` by its key.
- **What it asks:** how far the ERW forecast of Texas's demand was from what happened, beside the operator's own forecast and two rules that need no model; in percent and in megawatts; by hour of the day; on the ten highest-demand days; and the same difference for California.
- **It takes no side.** For Texas the operator's forecast has the smaller error in every question that sets the two side by side (5.86 percent against 2.39 over the whole backtest), and the set says so in figures. In California the ERW forecast's is the smaller (4.09 against 4.68). Its test refuses a word that ranks or advises.
- **Held out of the dated edition:** it is a waiting set. It has its page; the index does not list it, it has no `data.csv`, and the edition builder cannot freeze it. `site/lib/release.ts` and the menu are not touched.
- **Tests:** 475 checks in Node (83 keyed figures recomputed from the file, each found again by the row its question names, each found on the drawn page); 6 Python tests. Built and seen at 1280 and 390 px.
- **The equities page has no set yet.** The chain asks for "a segment beside an energy price", and no segment has a line (every one is held, license needed). It is not written with made-up values.

## The second window's rows 5 and 6

- Seen in one build of main with both branches, at 1280 and 390 px, and marked requested.
- **The back button on three forms** (`/companies`, `/prices/compare`, `/conditions`): after a choice, the form's button and the back button, 8 of 8 fields read what the page shows. On production, as the control: 0 of 8.
- **The companies form's six fields are named** in the accessibility tree (Name, Kind, Segment, State, Grid, Has). On production five of the six have no name.

## Tests before the heads were named

- Every test file that walks the site's folders or names a changed file, on one local branch holding everything that is to land: 340 files, 4,299 passed, 178 skipped, 11 failed.
- **None of the 11 is this window's.** Each fails the same way on the desk's branch `task/c701-desk-3` (`7328439cf`) without this window's work, on this laptop: sessions 143, 148, 156, 161, 1116, 1880, 7534, 8410 (two), 8430, 8901.

## Decisions made without you

- **The value check was changed, not the pages.** A megawatt of demand stays whole and a rise keeps its sign. The other way was to write "54,039.50 MW" and "0.32%".
- **A waiting set is a new kind of thing in the problem sets' code** (a short list beside the listed sets). The chain asks for a set "held out of the dated edition until Samuel approves it"; the listed sets are frozen by the edition builder whenever it next runs, so a set that must not be frozen cannot be in that list.
- **The set's place is Texas and its second is California:** the place `/forecast` opens on, and the first region in the file's order. Neither was chosen by its score.
- **The problem set's branch was rebuilt on the forecast branch alone** before it was pushed, so it carries none of the desk's commits.
- **Rows 5 and 6 were seen in one build of both,** not one build each (they touch different forms and merge with no conflict).

## For Samuel's ruling

- **Whether the forecast's problem set joins the listed sets.** Today: it waits, on its own page, in no index and no edition.
- **Whether a set that shows the ERW forecast scoring worse than the operator's in Texas is wanted as it is.** Today: written as the file holds it.

## Needs the key

- Nothing. No model was called.
