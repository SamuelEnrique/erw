# Progress of chain 503 (the old laptop, sessions 8400 on, 19 November 2026)

The chain file: `queue/done/503-day-19-november-oldlaptop-rulings-evidence-whole-country-pages.md`. One line an entry group, a page or a view: its state and the session. States: `done` with the commit, `in work`, `waiting` with what for, `ruling` with the default taken, `needs the key` with the cost.

## The ground

- The chain file saved as pasted, committed alone and pushed: done (`a37adf1af`), session 8400.
- The resume file `queue/next/530-resume-chain-503.md`: done (`b447803e2`), session 8400. No other resume file of this machine was in `queue/next/` (510 is the data machine's, 520 the desktop's second window's; both left).
- Precheck passed; no freeze; session numbers 8400 to 8599 free on origin/main and every branch (checked 19 November).

## Part A: the evidence behind the rulings

- A1 and A2, the 88 entries, five groups looked up side by side, each entry's block merged into the ranked list in the list's order as it arrives:
  - taxes (entries 17, 32, 34, 35, 36, 38, 42, 43, 45, 50, 51, 52, 54, 66, 88, 97, 112, 124): done, all 18 in the list (keep 10, switch 6, no basis 2), session 8400
  - storage (6, 12, 13, 16, 18, 25, 46, 47, 67, 78, 83, 99, 106, 107, 109, 127): done, all 16 in the list (keep 2, switch 6, no basis 8), session 8400
  - prices (7, 21, 44, 53, 73, 77, 86, 87, 89, 98, 105, 111, 113, 117, 118, 122): done, all 16 in the list (keep 5, switch 5, no basis 6), session 8400
  - grid (2, 23, 24, 26, 49, 59, 61, 62, 69, 82, 94, 95, 110, 116, 119, 129): done, all 16 in the list (keep 5, switch 5, no basis 6), session 8400
  - trackers (3, 5, 8, 14, 20, 28, 29, 31, 37, 48, 55, 57, 58, 64, 74, 75, 80, 81, 92, 120, 121, 128): done, all 22 in the list (keep 11, switch 6, no basis 5), session 8400
  - All 88 are in the list (`27e616d3a`): keep 33, switch 28, still no basis 27. The whole list: switch 54, keep 48, no basis 27 (before: 26, 15, 88).
  - The wording faults the groups found in the entries themselves (23, 75, 77, 94, 107): done, corrected with a section at the list's foot (`27e616d3a`).
  - The terms of use of every host a page was read from (the rule asks for them as well as the robots file; the taxes group read none): in work, session 8403, `runs/c503/terms_check.md`. An entry that rests alone on a host whose terms forbid automated access goes back to "no basis to recommend"; then the hosts record goes to `docs/reviews/rulings-evidence-hosts-2026-11-19.md`.
- A3, the 12 figures that do not agree: done (`86e038f0c`), session 8402. Each traced; entries 48, 118, 119 and 127 corrected in their own lines; one request to the data machine (row 320 of `docs/state/data_requests_done_line.md`).
- A4, the six screenshot faults (rows 341, 345, 357, 362, 363, 366): done (`c0668e4e2`), session 8401. Four fixed on their branches with a test, pushed, back to `wanted` (341 `e313c0d4f`, 362 `e0d5fc2ac`, 366 `9b4d3f1c8`, 363 `3858e0432`); 357 is a data fault (request row 321; a second small one, row 322); 345 is the hold as it stands. Report: `archive/sessions/SESSION_8401_REPORT.md`.
- A5, the sheet for one sitting: done (`1bd09b3cb`), `docs/reviews/rulings-one-sitting-2026-11-19.md`, session 8400. Built by `runs/c503/build_sheet.py` from the list; run it again if a recommendation moves (the terms check).
- Reports: `archive/sessions/SESSION_8400_REPORT.md`, `SESSION_8402_REPORT.md`.

## Part B: the events pages for the whole country

- The section "The whole country" on the nine event pages and the line of regions on `/events`: done on `wip/8410-events-regions` (`bbefd6dd0`, pushed), session 8410. Tests: the pin 21 of 21 in both modes, the section 77 of 77. Landing requested: row 51 of `docs/state/landing_request_oldlaptop.md`. Browser reads: rows 377 to 382.
- The view waits for its files: `site/data/regions/events/<event>.json` was not on origin/main on 19 November (checked at the start and at the commit); until then the section reads "not built yet". When a file lands: draw the page with it (`site/scripts/events-pages.mjs`), read the section against the contract, and mend any difference of shape on the branch.

## Part C: `/demand` for the whole country

- in work, session 8420: worktree `C:\Users\lossa\Documents\erw-8420`, branch `wip/8420-demand-regions` (made from `wip/8410-events-regions`, which holds the shared library `site/lib/countryfiles.ts`). Brief: `runs/c503/brief_build.md`. Hand-back: `runs/c503/8420/handback.md`. Rows kept for it: browser reads 383 to 392, landing row 52.

## Part D: `/supply` for the whole country

- in work, session 8430: worktree `C:\Users\lossa\Documents\erw-8430`, branch `wip/8430-supply-regions` (from the same branch). Hand-back: `runs/c503/8430/handback.md`. Rows kept for it: browser reads 393 to 402, landing row 53.

## Part E

- The events pages' new views, session 8440, branch `wip/8440-events-regions-done` (`59a1f2e76`, pushed; made from `wip/8410-events-regions`):
  - the replication `replication/events/replicate_regions.py` with `site/scripts/events-regions-figures.mjs`: done, 203 of 203 on the fixture; on the site as it stands it says no file is there.
  - the reader's five cases written (`docs/reviews/events-regions-read-2026-11-19.md` on the branch); three gaps found before any file.
  - waiting for the files `site/data/regions/events/<event>.json` (not on origin/main): the read of the five cases on the page, the replication's count on real files, the Stata do-file's expected values, the cross-check against published figures. First step when a file lands: merge origin/main into the branch, run the two commands the method note gives, then read the five cases.
- `/demand` and `/supply`: after parts C and D hand back.
