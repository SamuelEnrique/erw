# Session 9602 report (portable-laptop, 20 November 2026)

Energy Research Warehouse (ERW). The third session of chain 620: part E. From 12:30 UTC; this report is written at 13:16 UTC and the session goes on (part E has no end of its own). Model spend USD 0; no model was called. Nothing published; `site/lib/release.ts` not touched; every page in review. No build was made.

## Read these first

- **The nine fixes are still not landed and not requested.** Memory stayed at 1.7 to 1.9 GB free, under the 2 GB the chain asks before a build. A watcher on this laptop (`runs/c620/watch.sh`) says when 2 GB is free, when a commit touching `site/` reaches main, and when a browser row is wanted; the build, the checks and the request follow the first.
- **Two of the fixes were tried against production's real pages without a build, and hold.** The back button: with the mend's logic put into each page as it loads, 6 of 6 pages keep their lists true after back and forward; as production is, 0 of 6. The tour: the branch's stops and check against production's pages pass 94 of 97 (89 of 96 before); the three left are the Digest stop's two headings and the tour's own fourth page, which changes on landing.

## What was done

- **Part A again:** no row of `docs/state/browser_reads_wanted.md` is wanted but 418 to 422 (not landed, as session 9600 found); nothing has landed in `site/` since 10:20 UTC; `/congestion` and `/conditions` are not on main.
- **The queue:** `chain_queue.py list` shows no file for this laptop but chain 620's own resume file, so part E goes on.
- **Part E, a first pass at 390 px with a finger:** the five sellable tools, then 22 more pages of the menu. For each: load time, quiet faults, every "i" mark on the screen, every switch, every list, every chart, the page's width after each step. No fault on any of the 27.
- **Part E, the keyboard alone at 1280 px on the five tools:** every stop seen, with a focus mark, to the foot.
- **Part E, figures:** the battery page's averaged years against the years it lists (agree); six older pages that draw from page files screened at 390 px (no wrong figure); each region's Mix tab against its mix file.
- **For the nine branches together** (`local/c620-build` in `C:\Users\lossa\Documents\erw-c504`): the 79 test files that walk the whole site (1,134 tests) show the same four failures as main on this laptop, none new; the changed files and what they import type-check (0 errors).

## Not as the chain expected

- The chain's last session is to remove the resume file and take the next queue file. No other file waits for this laptop and part E has no end, so the resume file `queue/next/621-resume-chain-620.md` is kept: a session that starts again finds the chain and its open step (the build).
- "Seen fixed in a build" could not be met tonight for any fix. What was seen instead is said fix by fix in `docs/reviews/browser-read-2026-11-20.md` ("The fixes, and what has been seen of them").

## Decisions made without you

- The whole suite is not run here (rule 6 of 16 November: the desk's gate runs it). The tests that walk the whole site were run on the nine branches together, since a grep for a changed file misses them (chain 504's row 43 failed the desk's gate on two such tests).
- A type check of the changed files alone was run in place of the build's own (5 seconds, light on memory).

## Needs the key

- Nothing.

## For Samuel's ruling

- Nothing new in this session. The seven that wait are in `docs/state/note_2026-11-20_portable_c620.md`, each with its default taken.

## To finish

- As session 9601's report says: when 2 GB of memory is free, build `local/c620-build`, serve it, run `check-back-button.mjs` and `check-tour.mjs` against it, look at each of rows 44 to 52 of `docs/state/landing_request_portable.md`, stop the server, and mark the rows requested.
