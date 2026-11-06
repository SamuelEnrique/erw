# Session 425 report: the waits ledger reads to the newest report

21 October 2026, about 13:36 to 15:05 UTC, unattended, on portable-laptop (code role), in the worktree `C:\Users\samen\Documents\erw-425` on `wip/425-waits` (from `origin/wip/461-combined` at `2289156d`, chain 019's prepared and unlanded combined branch). The chain `queue/done/021-day-21-october-code.md` (written for samueloldlaptop, run here by the owner's instruction to run what the queue prints), "Session 425". Model spend USD 0. No pull, no warehouse data written. Not landed: no agent lands tonight (this machine's permission check refused an agent's landing).

## Read these first

- **`/internal/waits`'s ledger now reads sessions 351 to the newest report present at the build**, not 351 to 413: `LEDGER = { from: 351, to: "newest" }` in `site/scripts/build-waits.mjs`, resolved by a new `resolveRun` to the highest session number among the reports the build read. On this branch it reads **351 to 482: 104 reports, 244 lines, 228 items (16 merged)**; 401 to 415 and tonight's 441 to 473 are in it; no asked line sits in two items. A report that lands later joins at the next build with no change to the script.
- **Why the end is "newest" and not 430.** The chain allowed either: the newest report, or 351 to 430 with the test if session 414's test held the constant on purpose. 414's test pins the literal, but the reports of tonight's chains (441 to 482) are newer than 430, and a fixed 430 would leave them out on the next build, as 413 left out 414 on. 414's test now pins the new literal, with the old one in a comment.
- **A fault of `check-internal-waits.mjs` fixed**: its "newest report's first item" check failed on any item with punctuation after inline code (the page text reads "`wip/479-streak` , with" once tags are taken out). The newest report is session 479's (on main since 10:10 UTC), so the check fails on main's next build too; the page is right. It now drops the space before punctuation on both sides.

## What to review

- After the landing, in the internal view (`/internal/open`, then `/internal/waits`): the heading "Sessions 351 to 482: each ruling once" (the number moves with the reports).
- The shots: `docs/brand/review-425/` (`waits-desktop.png` at 1280, `waits-phone.png` at 390, with a README); before: session 414's `docs/brand/review-414/`.
- The code: `site/scripts/build-waits.mjs` (`LEDGER`, `resolveRun`, the first line of `ledger`, the build's fault path), `site/scripts/test-waits-ledger.mjs` (four new cases and the repository's run), `site/scripts/check-internal-waits.mjs` (one line), `tests/test_session425.py`, `tests/test_session414.py` (the pin), `docs/machines.md` ("Each ruling once").

## Checks

Every gate redirected to a file under `runs/chain_021/s425/` (git ignores `runs/`), never piped; the exit code read before the next step.

| Check | Exit | Result |
|---|---|---|
| `scripts/precheck.py --what "session 425"` | 0 | every check passed; the duty mark is the main checkout's, so this worktree did not mark it again (and `duty.py beat` answered 1: the mark is not this checkout's) |
| `node site/scripts/test-waits-ledger.mjs` | 0 | 771 of 771 held (written cases, the end of the run, a late report joining, and the repository's own reports) |
| `node site/scripts/test-waits.mjs` (session 188's reader) | 0 | 4,295 of 4,295 held |
| `tests.test_session425`, `tests.test_session414`, `tests.test_session188_waits` | 0 | 25 tests OK |
| `tests.test_session425` against the run put back at 413 | 1 | fails, as it should |
| `scripts/db_probe.py` | 1, then 0 | closed at 13:40 UTC (3.90 s); open at 14:30 (2.99 s) and at the build, 14:48 (2.96 s) |
| `npm run build` (under the build lock) | 0 | |
| `check-internal-waits.mjs` on the build, first run | 1 | 31 of 32: the newest item's words (the check's fault above) |
| the same, after the fix, on the same server | 1 | 31 of 32: "the browser drew every report" (89 drawn), which passed on the first run: the page was read before it had drawn |
| the same, on a fresh server | 0 | 32 of 32: the ledger drawn (351 to 482), its counts the file's (228 items, 244 lines, 104 reports), each item once, every item linked to each line that asks it, none of it sent to a visitor; no sideways scroll at 390 |

Impeccable is not installed on this laptop; not run. The whole suite was not run here (the other sessions of 021 hold the lock in turn; the combined landing runs it).

## Decisions made without you

1. **The run ends at the newest report present** rather than at 430 (above).
2. **The end is resolved inside `ledger()` and on the build's fault path**, so the page always names a number, and `build()`'s call stays as 414's test holds it.
3. **"Newest" counts the reports the build read**, after the answered marker, the same reports the ledger reads.
4. **The check's text match was fixed in the check**, not the page: the page draws the item's own words.
5. **The intermittent "drew every report" failure was rerun once on a fresh server**, not changed: it passed on the first run and on the third.

## For Samuel's ruling

- Nothing new; the ledger lists the items of the reports it reads.

## To finish

- Land `wip/425-waits` with chain 021's other branches (it holds chain 019's combined branch beneath it): freeze status; merge origin/main; the suite; `npm run build`; `node scripts/check-internal-waits.mjs <base>` (32 of 32 expected) and the full check-values; snapshot-live before and after; push to `task/`. The landing's commands are in chain 019's note, `docs/state/review_2026-10-22_code.md` (on `wip/475-note`).

## Files

- `site/scripts/build-waits.mjs`, `site/scripts/test-waits-ledger.mjs`, `site/scripts/check-internal-waits.mjs` (changed).
- `tests/test_session425.py` (new), `tests/test_session414.py` (the pin), `docs/machines.md` (one line).
- `docs/brand/review-425/` (two shots and a README).
- This report.
- Not in git: `runs/chain_021/s425/` (the probes, the build, the three check runs, the test outputs).
