# Session 9601 report (portable-laptop, 20 November 2026)

Energy Research Warehouse (ERW). The second session of chain 620: the fixes, parts C and D, and the rest of part B. About 11:25 to 12:30 UTC. Model spend USD 0; no model was called. Nothing published; `site/lib/release.ts` not touched; every page in review. No build was made (see below).

## Read these first

- **Nine fixes are on branches and none is landed or requested.** The chain asks that a fix be seen in a build first, and for 2 GB of memory free before a build. This laptop had 1.0 to 1.9 GB free through the session. Rows 44 to 52 of `docs/state/landing_request_portable.md` read "ready, not requested", each with what is left to do.
- **One command of mine hung and was stopped.** A stray heredoc into Python (which the chain forbids and which hangs on this machine) ran for two minutes in the background at about 12:05 UTC; it was stopped and left no process. Nothing was written by it.
- **The menu's "Policy" opens a page of two words.** Found in part D; mended on a branch.

## What was done

- **Nine fix branches,** each cut from origin/main, each with a test, each pushed:
  - `wip/9601-back-button-lists` (`dc046acff`): the shared list reads what the page shows after the back button.
  - `wip/9601-findings-phone` (`4971346fa`): `/internal/findings` fits 390 px.
  - `wip/9601-resource-set-legend` (`9632634e5`): the resource problem set gives the legend the map draws; its replication 0 of 142 differ.
  - `wip/9601-authority-facts-words` (`225e96ed8`): an authority that sends out more than it takes in is said to send out.
  - `wip/9601-tour-headings` (`bff5d765a`): no stop quotes words its page no longer shows (but the Digest stop, left for a ruling).
  - `wip/9601-policy-held-page` (`e029f90aa`): `/policy` keeps its heading and views when its list is held.
  - `wip/9601-price-map-window` (`58d119d6d`): the Grid map's price over a window names its days.
  - `wip/9601-line-ends-unnamed` (`5416bba3e`): a line's end HIFLD marks "UNKNOWN" is said to be unnamed.
  - `wip/9601-method-pages-phone` (`c6263da57`): a method page's long word breaks at 390 px.
- **Seen without a build:** the back button's cause and cure on a plain page in a real browser (the browser puts a form's state back after the page's load and before its showing); the findings page and six method pages 390 px wide with the branch's style put on production's page; `check-back-button.mjs` (4 of 16 fail) and `check-tour.mjs` (89 of 96) failing on production as they should before the mends.
- **Part B, the rest:** the project map's two line layers and a planned unit's date; the dated edition (twenty pages, 198 figures, 59 questions); 101 addresses of pages already read once, at both widths; all 609 method pages at 390 px.
- **Part C:** seven pairs of the same number in two places (three agree, three are different things and say so, one mended).
- **Part D:** the first minute as a stranger and as a reviewer; the menu under a mouse, a finger and the keyboard; the ways in to the new pages; the tour.
- **Data request 567** (the dated edition of the resource set); **the note** `docs/state/note_2026-11-20_portable_c620.md`.

## Tests

- Each branch's own test with the older tests that name what it changes: 32, 36, 9 (and the sets' tests), 10, 27, 90, 13, 11 and 48 passed.
- One older test fails on `wip/9601-resource-set-legend` and on main alike: `tests/test_session8901_problem_sets_country.py::TheNodeTests::test_each_figure_is_pinned_to_its_file_and_drawn` ("FAIL 16": it expects that no dated edition holds the five sets, and the edition of 20 November does).
- Two older tests were amended on `wip/9601-tour-headings`: `tests/test_session292.py` (the fourth stop's address; a quoted fold) and `tests/test_session8902_tour.py` (a quoted fold).
- The whole suite was not run: memory.

## Decisions made without you

- The tour's fourth stop opens `/grid?grid=ercot` (its words say "ERCOT first"; `/grid` opens on the Lower 48). To put it back: one line of `site/lib/tour.ts` and the address in `tests/test_session292.py`.
- The tour's first stop says "Assumptions" (the box's name since the ruling of 15 October).
- The landing rows are written "ready, not requested" and not left out, so that the desk and a later session see what is waiting and why.
- The words of one decision of the problem sets (`layer-by-id`) and one line of its method note follow the mend: the legend's range is the one the map draws.

## Needs the key

- Nothing.

## For Samuel's ruling (each left as it is)

- Six new pages have no way in from the menu: `/states`, `/industry` and `/ai-energy` only from the tour; `/queues/places`, `/storage/places` and `/curtailment/where-when` from no page. Default: left.
- The tour's Digest stop opens a page with no Digest (none since 12 November). Default: left.
- A stranger at the home address sees the heading "/". Default: left.
- On the Grid map an authority outside the seven ISOs reads "Demand: not held for this hour" at every hour. Default: left.

## To finish (when the laptop has 2 GB of memory free)

- In `C:\Users\lossa\Documents\erw-c504` the branch `local/c620-build` holds origin/main with the nine branches merged. `powershell -File runs\c504_rebuild.ps1 -Site C:\Users\lossa\Documents\erw-c504\site -Port 3620 -Out runs\c620\build.out`, then serve it (`runs\c7610_build.ps1 -Mode start -Port 3620`).
- Against `http://localhost:3620`: `node scripts/check-back-button.mjs` (expect 16 of 16), `node scripts/check-tour.mjs` (expect every check but the Digest stop's two), and each row's own look (rows 44 to 52). Stop the server.
- The whole suite on the build branch: `ERW_LOCK_EXEMPT=1 .venv\Scripts\python.exe scripts\suite_batches.py --batch 40`. Then mark rows 44 to 52 requested.
