# Progress of chain 503 (the old laptop, sessions 8400 on, 19 November 2026)

The chain file: `queue/done/503-day-19-november-oldlaptop-rulings-evidence-whole-country-pages.md`. One line an entry group, a page or a view: its state and the session. States: `done` with the commit, `in work`, `waiting` with what for, `ruling` with the default taken, `needs the key` with the cost.

## The ground

- The chain file saved as pasted, committed alone and pushed: done (`a37adf1af`), session 8400.
- The resume file `queue/next/530-resume-chain-503.md`: done (`b447803e2`), session 8400. No other resume file of this machine was in `queue/next/` (510 is the data machine's, 520 the desktop's second window's; both left).
- Precheck passed; no freeze; session numbers 8400 to 8599 free on origin/main and every branch (checked 19 November).

## Part A: the evidence behind the rulings

- A1 and A2, the 88 entries, five groups looked up side by side, each entry's block merged into the ranked list in the list's order as it arrives:
  - taxes (entries 17, 32, 34, 35, 36, 38, 42, 43, 45, 50, 51, 52, 54, 66, 88, 97, 112, 124): in work, session 8400 (the entries merged so far are in the list)
  - storage (6, 12, 13, 16, 18, 25, 46, 47, 67, 78, 83, 99, 106, 107, 109, 127): in work, session 8400
  - prices (7, 21, 44, 53, 73, 77, 86, 87, 89, 98, 105, 111, 113, 117, 118, 122): done, all 16 in the list (keep 5, switch 5, no basis 6), session 8400
  - grid (2, 23, 24, 26, 49, 59, 61, 62, 69, 82, 94, 95, 110, 116, 119, 129): done, all 16 in the list (keep 5, switch 5, no basis 6), session 8400
  - trackers (3, 5, 8, 14, 20, 28, 29, 31, 37, 48, 55, 57, 58, 64, 74, 75, 80, 81, 92, 120, 121, 128): in work, session 8400
  - The blocks are written one file an entry under `runs/c503/evidence/` on this machine and merged by `runs/c503/merge_evidence.py` (it skips an entry that already holds its block); a restarted session runs it first, then looks up only the entries its printout says wait for a file.
  - Still to do when all 88 are in: the wording faults the groups found in the entries themselves (entry 23 says EIA runs "above" the operator where it runs under; entry 77 gives ICE's fee as PJM's; entry 94 says load zones for weather zones; entry 7's line is older than its method note), each corrected with one line at the list's foot.
- A3, the 12 figures that do not agree: done (`86e038f0c`), session 8402. Each traced; entries 48, 118, 119 and 127 corrected in their own lines; one request to the data machine (row 320 of `docs/state/data_requests_done_line.md`).
- A4, the six screenshot faults (rows 341, 345, 357, 362, 363, 366): in work, session 8401 (one worktree a branch, `erw-c503-*`)
- A5, the sheet for one sitting: not started (after all 88 are in)

## Part B: the events pages for the whole country

- The section "The whole country" on the nine event pages and the line of regions on `/events`: done on `wip/8410-events-regions` (`bbefd6dd0`, pushed), session 8410. Tests: the pin 21 of 21 in both modes, the section 77 of 77. Landing requested: row 51 of `docs/state/landing_request_oldlaptop.md`. Browser reads: rows 377 to 382.
- The view waits for its files: `site/data/regions/events/<event>.json` was not on origin/main on 19 November (checked at the start and at the commit); until then the section reads "not built yet". When a file lands: draw the page with it (`site/scripts/events-pages.mjs`), read the section against the contract, and mend any difference of shape on the branch.

## Part C: `/demand` for the whole country

- not started

## Part D: `/supply` for the whole country

- not started

## Part E

- not started
