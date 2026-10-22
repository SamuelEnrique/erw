# Session 587 report: held figures that show, on an internal page

22 October 2026, from about 00:05 UTC, unattended, on samueloldlaptop (code role), in the worktree `C:/Users/lossa/Documents/erw-587` on `wip/587-s` (from `origin/wip/506-combined`, merged with origin/main). The chain `queue/done/034-night-22-october-code.md`, session 587. Model spend USD 0; no warehouse data written; no web request; no page a visitor reads changed; `site/lib/release.ts` untouched. Not landed: session 589 lands the chain.

## Summary

`/internal/holds` is new: the list `site/scripts/check-holds.mjs --csv` writes (`docs/licenses_holds.csv`, session 505), read when the site is built, one row a line of the file with each cell as the check wrote it (the page's address, linked; the check's count of held figures; the kinds; the tables; the grids; the day), and each table's status and verdict from `warehouse/metadata/license_status.csv`. It draws no figure of a held table. It is gated exactly as `/internal/waits` is: 404 to a visitor, the internal cookie only, no token in its address, never cached or indexed, linked from nothing.

## What was done

- `site/scripts/holds-content.mjs` (new): reads the two CSVs into the page's content. Rows are the file's lines in its order, cells as written; a table with no record is `null`, not filled. A missing file, a header other than the check's six columns, or a line of the wrong width is said (`unread`) and nothing is listed; a missing status record is said (`status_unread`). It prints the JSON when run alone (`node scripts/holds-content.mjs [holds.csv [status.csv]]`), which the tests use.
- `site/scripts/build-content.mjs`: calls it and writes `site/content/holds.json` (a file of its own, so no page for visitors imports it; gitignored). A missing list does not stop the build. `package.json` is unchanged (test 188 holds its prebuild line).
- `site/lib/holds.ts` (new, `server-only`): the types and the import.
- `site/app/internal/holds/page.tsx` (new): the page, as `/internal/waits` is built (`generateMetadata` names the page only to the internal view, `notFound()` without the cookie, `force-dynamic`, `<Brand noUsage>`, `data-no-usage`).
- `tests/test_session587.py` (new): the page's rows are exactly the CSV's rows, cell for cell and in order; each table carries its record; a scratch file is read cell for cell (a comma in a status note, a table with no record); a missing or misshapen file is said; the page is gated as the waits page is, draws one row a line, imports nothing that reads a figure (no `Num`, no `data-check`, no `lib/supabase`, no `lib/license`); no em dash. A class `Served` reads the page from a running build when `HOLDS_BASE` and `INTERNAL_COSTS_TOKEN` are set and compares its `data-hold-page` rows with the CSV.
- `tests/test_session408.py`: `/internal/holds` added to `EXEMPT` with its reason (it reaches `lib/supabase.ts` only through `lib/thesis/server.ts`'s `internalOk`, as `/internal/waits` does; it shows no warehouse figure).
- `docs/tools.md` and `docs/release-gate.md`: a line each for the page.

## Checks

Every gate redirected into `runs/` of the main checkout (outside git), never piped; the exit code read before the next step.

| Check | Exit | Result |
|---|---|---|
| `scripts/precheck.py --what "session 587"` | 0 | passed |
| `tests.test_session587` (before the build) | 0 | 10 tests, 1 skipped (`Served`, no build yet) |
| tests of the files touched: 102, 135, 147, 182_flow, 188_waits, 199, 232, 238, 267, 314, 315, 411, 471, 503, 408, 505 | 1, then 0 | first run: 2 failures, both mine (the page's comment named `/internal/waits`, which test 188 holds is named nowhere else; test 408 asked for `/internal/holds` to be read or exempt); after the fix 188, 408 and 587 pass (29 tests) |
| tests reading `docs/tools.md` and `docs/release-gate.md`: 146_page, 177, 186, 194, 202, 53, 55, 67 | 0 | 166 tests |
| `scripts/db_probe.py` (twice, its own command) | 0, 0 | 0.70 s and 0.63 s |
| `scripts/buildlock.py acquire s587` | 0 | waited for s578 from 00:11 to 00:20 UTC; released at the end |
| `npm ci` | 0 | |
| `npm run build` | 0 | `build-content: holds.json, 14 pages with held figures shown`; `/internal/holds` built as a dynamic route; no "statement timeout" in the log |
| `curl /internal/holds` as a visitor | 404 | none of the page's words in the 404's body |
| `tests.test_session587` with `HOLDS_BASE=http://localhost:3587` | 0 | 10 tests, none skipped: the served page's 14 `data-hold-page` rows equal the CSV's 14 lines in order |
| `node scripts/check-routes.mjs http://localhost:3587` | 0 | pass 1: 226 of 226 pages; pass 2: 225 in review and 1 live asked as a visitor, 0 failed |
| `CHECK_VALUES_PAGES=/data/licenses,/digest node scripts/check-values.mjs http://localhost:3587` | 1 | 107 of 107 values match Supabase; the one failure is `/digest`'s floor (0 checked numbers, floor 9). Not this change: at 00:20 UTC on Thursday 22 October `/digest` says "No Digest yet for Thursday 22 October 2026" (session 402's pending day, before the 14:00 UTC run), so it draws no number; `/digest/2026-10-21` carries its 18 keys and every value matches. A second run of `/digest` alone gave the same. `/data/licenses` (which reads `docs.json`, written by the script this session extends): 37 checked numbers, all match |
| `node scripts/shot.mjs` at 1280 and 390 | 0, 0 | `runs/s587_holds_1280.png`, `runs/s587_holds_390.png`; no before shot: the address did not exist (404 to everyone). At 390 the table scrolls sideways in its own box, as `/internal/health`'s does |

The page itself, with the internal cookie: 14 rows (`data-hold-row`), 26 table records, every one "license needed" from 2026-10-21 with the verdict "needs written permission"; no `data-check` key on it. The server was stopped by the PID on port 3587; no browser left running.

## Decisions made without you

- The list is read in `build-content.mjs` into its own `content/holds.json`, not a new prebuild script: test 188 holds `package.json`'s prebuild line word for word, and a file of its own keeps the list out of `docs.json`, which public pages import.
- A missing or misshapen `docs/licenses_holds.csv` is said on the page and does not fail the build (the list is a check's output; `scripts/licenses.py write` treats a missing file the same way).
- "Verdict" is shown as the table's record in `warehouse/metadata/license_status.csv`: its status and from-day, its `verdict` cell and its publishers. The check's count of figures is shown as written (a count, not a figure of a held table).
- `/internal/holds` is exempt in test 408's list, with its reason, as the other internal pages are.
- The "Checked on" date wraps in its narrow column at 1280; left as built (one build), a `whitespace-nowrap` for a later session.

## For Samuel's ruling

None. (Session 505's two items stay as they were: how a held panel is drawn, and whether `check-holds.mjs` joins the landing gate. This page decides neither.)

## To finish

Nothing for this session. For session 589's landing: `/digest`'s floor in check-values fails before the day's Digest is written (14:00 UTC); a landing run before then should read that line as the pending day, not as a regression (a resumed or later run clears it).

## Files changed

- `site/app/internal/holds/page.tsx` (new)
- `site/lib/holds.ts` (new)
- `site/scripts/holds-content.mjs` (new)
- `site/scripts/build-content.mjs`
- `site/.gitignore`
- `tests/test_session587.py` (new)
- `tests/test_session408.py`
- `docs/tools.md`, `docs/release-gate.md`
- `archive/sessions/SESSION_587_REPORT.md` (this report)
