# Session 10400 report: chain 720, the start, part A and part B

Energy Research Warehouse (ERW). 26 November 2026, the portable laptop's first window (code role), unattended. Chain file: `queue/done/720-night-26-november-portable-forecast-equities-pages.md`.

## What was done

- **Stray work kept.** The folder held one uncommitted change, a screenshot of the 20 November browser read (`docs/reviews/browser-read-2026-11-20/congestion/after-choices-1280.png`). It is on `wip/c720-stray-2026-11-26` (`bd74e2d02`), pushed. Nothing was discarded. Main was then put at origin/main (350 commits forward).
- **The start.** Precheck passed; no freeze. The chain's file was taken (`07b7be27d`). The resume file `queue/next/721-resume-chain-720.md` was committed alone and pushed (`634b4f87a`). `docs/state/progress_c720.md` started. Session 10400 was free on origin/main and on every branch.
- **Memory.** 681 MB free of 15,974 MB at the start; 1.7 to 1.8 GB later in the session. No build was made.
- **Part A, rows 44 to 51 of `docs/state/landing_request_portable.md`.** Checked against main first, as the chain asks. All eight heads are ancestors of origin/main: the desktop's second window (session 9203) merged chain 620's ten fix branches as `wip/w2-c620-fixes`, built that stack and saw each fix in the build, and chain 601's desk landed it at `0fc82399d` (task/c601-desk10, 21 November 2026 00:10 UTC; row 4 of `docs/state/landing_request_window2.md`). Each fix's own test passes on main's tree today (ten test files, 56 passed). The rows' State cells now say landed. Nothing was left to build.
- **Part B, the ground.** `docs/reviews/pages-ground-2026-11-26.md`: what both pages reuse and from where (the tool page's frame; `CategoryChart`'s band; `TimeChart` with its second axis; the place picker and A beside B as GET forms; the board's rows, groups and held rows; the workbench's pure parts; the download routes with their Python and Stata readers; the release gate's rule that a path with no line is in review), what they do not reuse, what the contracts leave open, and five cases for each page.
- **Both contracts are on main already** (`docs/state/page_files_predict.md`, `docs/state/page_files_equities.md`), so parts C and D start at once.

## Decisions made without you

- **"This folder" was read as the working tree and the branch checked out in it.** The one uncommitted file went to the stray branch. Fourteen older local branches of earlier chains that hold commits not on their remote (`local/c305-*`, `local/c504-*`, `local/c620-build`, `wip/5100-security`, `wip/7600-*`, `wip/7601-*`, `wip/7602-*`) were left exactly as they are: nothing of them was pushed, moved or deleted.
- **Documents go to main, code goes to `wip/c720-*` branches,** as chains 303, 504 and 620 did on this laptop: no page is open to a visitor, so a push of documents and queue files changes nothing a visitor sees. Code reaches main only through a row in the landing request.
- **Rows 52 and 53 were marked landed with rows 44 to 51.** The chain names 44 to 51; the two after them stood in the same state for the same cause and landed in the same stack.
- **The main checkout stays on the code branch and a second small worktree (`Documents\erw-c720-docs`) holds main for the documents,** so the progress file can be pushed after each step without switching the branch a build stands on.
- **The board's workbench is not handed an equity series.** It reads its own files for a row of the board's file. `/equities` reuses its pure parts and the shared time chart. A row of the board's equities group opens `/equities` on that series.

## For Samuel's ruling

- None from this session.

## Needs the key

- Nothing. No model was called.

## What to review

- Nothing a visitor or a reviewer sees changed in this session. The ground: `docs/reviews/pages-ground-2026-11-26.md`.
