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

PLACEHOLDER

## Decisions made without you

- The list is read in `build-content.mjs` into its own `content/holds.json`, not a new prebuild script: test 188 holds `package.json`'s prebuild line word for word, and a file of its own keeps the list out of `docs.json`, which public pages import.
- A missing or misshapen `docs/licenses_holds.csv` is said on the page and does not fail the build (the list is a check's output; `scripts/licenses.py write` treats a missing file the same way).
- "Verdict" is shown as the table's record in `warehouse/metadata/license_status.csv`: its status and from-day, its `verdict` cell and its publishers. The check's count of figures is shown as written (a count, not a figure of a held table).
- `/internal/holds` is exempt in test 408's list, with its reason, as the other internal pages are.

## For Samuel's ruling

None. (Session 505's two items stay as they were: how a held panel is drawn, and whether `check-holds.mjs` joins the landing gate. This page decides neither.)

## To finish

PLACEHOLDER

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
