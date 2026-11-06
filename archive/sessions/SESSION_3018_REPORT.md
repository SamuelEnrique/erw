# Session 3018 report: the drafts checked, the second part: the review page, and a fix landed

6 November 2026, about 13:05 to 13:52 UTC, on lab-desktop, second window, chain 164 (the owner's), unattended. Model spend USD 0. Pulls: none.

## Read these first

- **Found: `/internal/findings` showed only 100 of the review list's 222 rows.**
  - `scanner_drafts_list` (migration 029) returns 100 rows unless asked for more, at most 500, and the page asked for no limit.
  - This chain's 156 drafts, the newest, therefore pushed the scanner's 66 older rows off the page, among them the one approved spike.
  - Found on a local build of main and the board, read with the internal cookie: 100 of the chain's 156 drafts on the page.
- **Fixed and landed: `task/3018-drafts-list` merged as `b86a54119`** (run 42226698598, Vercel success).
  - `site/lib/scanner.ts`'s `listDrafts` now asks for `LIST_LIMIT = 500`, the function's most. `tests/test_session3018.py` (2 tests) ties the number to the migration's cap. The function was also called read-only with the site's own key: 222 rows with the limit, 100 without.
  - The gate on `a471d49a`: the suite passed (7,866 tests), and npm ci, the build and serve passed. check-values matched 7,815 of 7,815, with main's two known floors.
  - **By hand on a build of the same commit:**
    - check-routes: 225 pages, 0 failed
    - check-cross-checks: 92 passed
    - check-csp: 0 violations
    - `/internal/findings` read locally with the internal cookie: **222 draft ids on the page**, all 156 of this chain's with their files and five tests
  - Snapshots `s3018-land-before` and `s3018-land-after`: **0 differences** (the page is internal, and every public page is in review).
  - It was landed alone, before 14:00 UTC, rather than with this chain's branch at session 3023: the fault was this chain's doing, and the owner may open the page today.
- **The old laptop's request rows 3 to 8 are marked "landed at 6331a953a"** (`b9fa7b573`, snapshots `s3018-land-after` and `s3016-mark-after`: 0 differences).
- **The charts' hover:** the cards are drawn by the site's own `lib/discoverychart.ts`, whose `flag_line` option carries an axis tooltip with a formatter. The page itself loads every card with its chart spec (the local read above).

## Decisions made without you

- **The fix was landed outside this chain's own branch** (above).

## For Samuel's ruling

- None new.
