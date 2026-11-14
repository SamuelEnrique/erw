# Session 5263: the spend guard reads the whole ledger; session 5262's work committed

Energy Research Warehouse (ERW). portable-laptop, window P3, 14 November 2026 (08:27 to 08:58 UTC), Fable, unattended. The first step of window P3's close-out. Branch `wip/5200-ask-guard` (worktree `erw-p3-5200`), cut from `origin/main` at `85e5b2eeb`. Nothing built, nothing landed, no warehouse data written. Model spend USD 0.00: no model call was made in this session.

## Read these first

- **The fault is confirmed and fixed.** `warehouse/chat/eval/eval_s1113.py` `spent_today()` asked Supabase for the day's ledger rows in one request with `limit=5000`. Supabase answers with 1,000 rows at most. Read on 14 November at 08:31 UTC: 1,092 rows for 13 November, 1,000 returned (`Content-Range: 0-999/1092`), USD 18.01 of USD 19.4570.
- **No cap was passed on 13 November.** The twelve askings went through the site's loop, whose ceiling is counted on each session's own run file. The run files hold USD 19.4570; the whole ledger holds USD 19.4570 in 1,092 rows. Chain 238 ended under its USD 20 by USD 0.54.
- **No other spend helper has the limit.** Each was read: a sum the database makes, a file read whole, a sum in SQL, the run's own file, or pages. One is weaker than it should be and is not this window's file: see "For Samuel's ruling".
- **Session 5262 had finished its asking when the connection was lost.** Its files were whole (its own log ends "ask exit=0" at 21:17 UTC). Eleven questions asked once more on the final chat: 11 of 11 right, USD 1.3129. They are committed here with the final scores in the method note.
- **A landing is requested, marked URGENT:** row 29 of `docs/state/landing_request_portable.md`.

## What was done

- Precheck from the main checkout: exit 0.
- **Before any change, the fault measured** against the live ledger with the service key (reads only): one request with `limit=5000` returned 1,000 of 1,092 rows.
- **The fix** (`eval_s1113.py`):
  - The ledger is read a page at a time in the order of its key (`order=id.asc`, each page `id=gt.` the last row read) until a page comes back empty. It does not lean on the size of the server's page. A row written while it runs is counted once.
  - The server's exact count (`Prefer: count=exact`) is held against the rows read.
  - A day that cannot be counted stops the asking before the call (`LedgerNotWhole`): fewer rows than the server counts, a page that does not move on, an answer that stops part way, a call with no price, an answer with no count.
  - A ledger that cannot be asked at all (no keys, no answer) falls back to the run's own costs, as before, and a line says so.
- **Two commands added:**
  - `eval_s1113.py --spent`: the day's spend from the whole ledger. Reads only. Exit 3 when the day cannot be counted, 4 when the ledger cannot be asked.
  - `eval_site.py --day-cap <USD>`: every asking of the UTC day under one ceiling, read from the whole ledger first. The session's ceiling is cut to what the day has left. Nothing is asked when the day cannot be counted. Refused with `--no-ledger`.
- **The fix proved on the old code and on the live ledger:**
  - The old function, from main, against a stand-in server with 1,092 rows of USD 0.02: `(20.0, 1000)`. The day is USD 21.84.
  - The new function against the live ledger for 13 November: USD 19.4570 in 1,092 calls, in pages of 1,000, 92 and 0.
- **Session 5262's files, read and committed:** `eval_s5262_site_platform_run.json` and its grades, `runs.json`, the three records (`ask-history.md`, `ask-replay.md`, `ask-refusals.md`) and the scores block of `docs/reviews/ask-eval-2026-11-13.md`. `platform_scores.py` run again: no change.
- **The final scores written** into `docs/methods/ask.md` (the platform set's section, the evaluations table, a section on the spend guard, two decisions) and into `docs/reviews/ask-eval-2026-11-13.md` (the sample of eleven with each question's first asking, the spend guard, the spend row of session 5262, the chain's total against the whole ledger).

## Every spend helper, and what it reads

| Helper | What it reads | The 1,000-row cut |
|---|---|---|
| `warehouse/chat/eval/eval_s1113.py` `spent_today` | `site_api_calls` over REST, the day's rows | **had it; fixed** |
| `site/lib/chat/limits.ts` `admit` | `site_ask_admit`: a sum in the database | no |
| `site/lib/chat/limits.ts` `admitEvaluation` | `internal_ask_spend`: sums by day and step, one JSON value | no |
| `site/scripts/eval-ask-site-loop.mjs`, `eval_site.py` `spent` | the run's own file, superseded answers included | no |
| `warehouse/chat/eval/eval_loop.py` | each response's usage block | no |
| `warehouse/llm.py` `session_total`, `check_cap` | the ledger file on the machine, whole | no |
| `warehouse/thesis/run.py` `spent_today` | `sum(usd)` in SQL | no |
| `warehouse/health.py` `ledger_remote` (the daily cap, the precheck) | Supabase's copy over REST, pages of 1,000 | no, with a weakness (below) |
| `site/app/internal/costs`, `site/app/internal/ask` (pages, not guards) | `internal_costs`, `internal_ask_spend`: one JSON value each | no |

## Checks run

- `tests/test_session5263_ask.py`: 21 passed. It holds the fault's mechanism, the whole reading, a smaller server page, a row written meanwhile, the refusals, the cap held against the whole day in `ask()`, the day's ceiling, and what each other helper reads.
- The 16 test files that name the evaluation's runners: 162 passed, 1 skipped.
- The 130 test files that touch the chat, the license hold or the docs tree: 1,778 passed, 126 skipped, 1 failed in 11 minutes. The one failure is `tests/test_session1011.py` `test_the_copy_is_byte_for_byte`, on an ignored build file an earlier session left in this worktree (`site/content/llms.json`, older than today's `package/llms.txt`): not this stack's, skipped in a clean checkout, and named in row 28 before.
- No em or en dash in the files changed.
- Not run: the whole suite, a build, a lint (this window never builds).

## Model spend

- Estimate before: USD 0.00. Actual: USD 0.00. The ledger for 14 November (UTC) held 0 rows at 08:35 UTC.
- Session 5262's asking, committed here: USD 1.3129 under a cap of USD 1.60. Chain 238 in all: USD 19.4570 of USD 20.

## Decisions made without you

- **A fresh branch from main, not the landed one.** Row 28 landed at `f44d37628`; `wip/5200-ask-guard` is cut from `origin/main` and carries session 5262's files.
- **Session numbers.** Chain 238's 5263 and 5264 were never run; this close-out uses them for its first two steps. Chain 256 keeps 5265 to 5279.
- **Paging by key, not by offset.** A row written between two pages cannot shift a later page, and the end is an empty page, not a short one.
- **A day that cannot be counted stops the asking.** Before, a call with no price fell back to the run's own costs, a smaller number. The site's own ceiling already closes on it.
- **The fallback kept for a ledger that cannot be asked.** The module's own words promise it, and the route holds its ceiling in the database.
- **`--day-cap` is an option, not a default.** A stored command reads as before. This close-out passes it on every asking.
- **Session 5262's estimate is its cap.** It wrote no report; its run's first line names USD 1.60.

## For Samuel's ruling

- **`warehouse/health.py` `ledger_remote` (the daily cap of the scheduled steps).** It reads in pages, so it has no 1,000-row cut. Two weaknesses: it names no order, so two pages are not promised to be disjoint; and it ends on a page shorter than 1,000, so a smaller server page would end it early. Right today on both counts. Not this window's file. **Default: left as it is**, for the data window: an `order` on `event_id` and an end on an empty page.
- **The findings scanners ask for the drafts in one request with `limit=5000`** (`warehouse/analysis/findings/hunt.py`, `findings_scanner.py`, `deep/builder.py`). Not spend. `scanner_drafts` holds 252 rows today, so nothing is cut. Past 1,000 rows a known flag would look new. **Default: left as it is**, named here for the window that owns the findings.
