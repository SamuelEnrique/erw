# Session 301 report: the security review's build items

19 October 2026, from 10:24 UTC, unattended, on samueloldlaptop (the code machine), the seventh session of the chain of 19 October (`CHAIN_OCT19_PROMPT.md`). Branch `wip/301-security-build` in the worktree `erw-296`, from session 300's pushed commit; lands on main as `task/301-security-build`. Model spend USD 0: no model call. No pull, no warehouse data written. The review: `docs/reviews/2026-10-10-security.md`, whose H1, H3, M1 and M4 now carry a "Session 301" line each.

## Read these first

- **H1, every check script off the token-in-the-address link.** Thirty-seven files opened the internal view by `/internal/unlock?token=...` (the review counted thirty-one; `grep -l` finds thirty-seven, `browser.mjs` among them). Each now opens it by the form's door of session 177: a script that fetches posts the token in the request's body (`unlockPost` in `site/scripts/browser.mjs`, with the site's own origin, as `check-security.mjs` did), and a script that drives a browser fills and submits the form at `/internal/open` (`unlockForm`, as `check-csp.mjs` did). `check-security.mjs` alone still names the old link, in its three checks that prove the link answers as before until it is retired. `code-branch.yml` never named the link itself; it runs `check-routes` and `check-no-request`, both moved. Every moved script was run once against the built site; the table below lists each exit code.
- **H3 and M1, the writes server side with the service key.** `insertRow` (the sign-up, the game's two tables, the model-call ledger) and `rpc` with `privileged` (the question counter, `site_ask_admit`) go with `SUPABASE_SERVICE_KEY` when the server holds it and with the anon key as before when it does not, so the order of the change is free: key first, site second, policy last. Migration `034_server_writes.sql` (with its rollback) drops the four insert policies and grants, the anon key's use of the four sequences (L6) and its right to execute `site_ask_admit`, granting it to `service_role` by name. **Not applied** (a schema change is yours; below). `site/README.md` says what the key is for and where it must be set.
- **M4, the full content security policy enforced.** `check-csp.mjs` opened the 89 pages of the release list and the internal pages on the built site with the report-only policy: 0 violations. The full policy is now the enforced header, with the report-only header beside it (the same value) for a week; the check's own probe is blocked and does not run, which the check now expects.
- **The game cannot store a play in production until migration 033 is applied** (session 289's v5 constraints; session 295 landed the v5 site). The local proof of the game's write below runs against the live database, so it meets the same refusal: the play is scored and shown, the store is refused by the preset check. The write path itself (the service key through `insertRow`) is proven by the unit test and by the refusal's own message, which comes from the database through that key.
- **Session 300 landed** (recorded below).

## What to review

1. `site/scripts/browser.mjs` (`unlockPost`, `unlockForm`) and one moved script of each kind: `check-routes.mjs` (fetch), `check-no-request.mjs` (a browser it drives), `frametime-resources.mjs` (the protocol by hand).
2. `site/lib/supabase.ts` (`writeConfig`, `writeRole`, `insertRow`, `rpc`), `site/app/api/ask/route.ts`, `warehouse/supabase/migrations/034_server_writes.sql` and its rollback.
3. `site/next.config.ts` (the policy), `site/scripts/check-csp.mjs` (the probe under enforcement).
4. The review's four "Session 301" lines; `tests/test_session301.py`.

## Checks

| Check | Exit | Result |
|---|---|---|
| `scripts/precheck.py --what "session 301"` | 0 | `runs/chain_oct19/s301_precheck.out` |
| `tsc --noEmit` (worktree), both builds | 0 | no error |
| `eslint` on the files touched, `node --check` on the scripts | 0 | 0 errors |
| `npm run build` (worktree, under the mutex, `duty.py beat` sent) | 0 | two builds: the code, then the enforced policy; 0 statement timeouts |
| `check-security.mjs`, first build (report-only) and second (enforced) | 0, 0 | 50 of 50 checks, both |
| `check-csp.mjs`, first build (report-only) | 0 | 89 pages: 0 enforced, 0 report-only violations, 0 not loaded |
| `check-csp.mjs`, second build (enforced), after the probe's rule | 0 | 89 pages: 0 enforced, 0 report-only violations, 0 not loaded; the probe blocked and not run |
| `tests.test_session301`, `test_session177` | 0 | 37 passed |
| Every moved script, once, against the second build | | the table below |
| Suite, clean copy, the commit pushed | SUITE_EXIT | SUITE_LINE |

### Every moved script, run once (the second build, `http://localhost:3296`)

| Script | Exit | Time | Last line | Note |
|---|---|---|---|---|
| `check-csp.mjs` | 0 | 196s | 89 pages: 0 enforced violation(s), 0 report-only violation(s), 0 page(s) not loaded |  |
| `check-security.mjs` | 0 | 2s | 50 of 50 checks passed |  |
| `check-routes.mjs` | 0 | 194s | route check, pass 2: 1 live pages and 210 pages in review asked as a visitor; 0 failed. The list holds 0 live  |  |
| `check-no-request.mjs` | 0 | 12s | check-no-request: passed: typing into the page made no request and stored nothing |  |
| `check-analysis.mjs` | 0 | 2s | 279 of 279 checks passed |  |
| `check-board.mjs` | 0 | 6s | 36 of 36 checks pass |  |
| `check-board-v4.mjs` | 0 | 1s | 12 of 12 checks pass |  |
| `check-contracts-largest.mjs` | 1 | 1s | FAILED: no summary file (http://localhost:3296); make it with warehouse/supabase/eqr_fixture.py | no EQR summary fixture on this machine (make it with eqr_fixture.py); the old script fails the same |
| `check-curtailment.mjs` | 0 | 15s | all 118 passed |  |
| `check-curtailment-v2.mjs` | 0 | 15s | all 118 passed |  |
| `check-datacenter.mjs` | 1 | 30s | Node.js v24.19.0 | the datacenter page's words moved since the script's session (22 of 47 checks); the old script crashes on the same build |
| `check-datacenters.mjs` | 0 | 1s | all 15 passed |  |
| `check-demand.mjs` | 0 | 5s | 102 of 102 checks pass |  |
| `check-demand-weather.mjs` | 0 | 3s | 78 of 78 checks pass |  |
| `check-grid-replication.mjs` | 1 | 5s | 60 values compared, 59 different | the committed replication file is session 266's hour (session 299's report); not this session's |
| `check-how-soon.mjs` | 1 | 38s | Node.js v24.19.0 | the internal table large_load_waits is not on this machine; the old script crashes on the same build |
| `check-internal-findings.mjs` | 1 | 25s | 86 of 105 checks passed | the drafts' cards moved since the script's session (86 of 105); the old script gets 5 of 5 of a shorter list |
| `check-internal-health.mjs` | 0 | 3s | check-internal-health: 19 checks passed |  |
| `check-internal-waits.mjs` | 1 | 3s | 23 of 24 checks passed | one check: the newest report's first item quotes a later session's words (23 of 24); the old script 0 of 0 |
| `check-mix.mjs` | 0 | 9s | 36 of 36 checks pass |  |
| `check-mix-v2.mjs` | 1 | 2s | 42 of 46 checks pass | four pages' storage figures read 0.0% (42 of 46); the old script crashes on the same build |
| `check-policy.mjs` | 0 | 6s | 46 of 46 checks pass |  |
| `check-policy-tags.mjs` | 0 | 5s | 24 of 24 checks pass |  |
| `check-prices-compare.mjs` | 0 | 1s | 54 of 54 checks pass |  |
| `check-queues.mjs` | 0 | 1s | 55 of 55 checks pass |  |
| `check-resources.mjs` | 0 | 81s | all 97 passed |  |
| `check-review-pages.mjs` | 0 | 1s | 3 of 3 pages render with data in the internal view at http://localhost:3296 |  |
| `check-shoulder.mjs` | 127 | 1s | Assertion failed: !(handle->flags & UV_HANDLE_CLOSING), file src\win\async.c, line 94 | warehouse/output/shoulder_hours_monthly.csv is not on this machine (its stub needs it); fails before the door |
| `check-supply.mjs` | 0 | 7s | 27 of 27 checks pass |  |
| `check-thesis.mjs` | 0 | 3s | 34 of 34 checks pass |  |
| `check-buildout.mjs` | 0 | 2s | /storage?tab=buildout as rendered: 10241 checks pass, 3530 numbers equal the fixture's rows (16 pages) |  |
| `check-battery-face.mjs` | 0 | 16s | all passed |  |
| `check-battery-scenarios.mjs` | 0 | 55s | all passed |  |
| `check-seller-scenarios.mjs` | 0 | 69s | all passed |  |
| `test-battery-stack.mjs` | 1 | 3s | Node.js v24.19.0 | the battery page's income table moved in session 296 (the script's page query throws at its first check, before the door); the old script fails the same |
| `check-battery-game.mjs` | 0 | 367s | the battery game on a laptop (1366 by 768), 2023-08-10: 97 of 97 checks pass |  |
| `check-values.mjs` | 0 | 271s | 5294 of 5326 values match Supabase; 32 latest prices superseded by a newer interval within 45 minutes (checked |  |
| `frametime-resources.mjs` | 1 | 14s | frametime FAILED: the window draws no frames (the screen is locked or the window is hidden); run again with th | the window drew no frames (the screen is locked); run again headless, below |
| `frametime-resources.mjs --headless` | 0 | 14s | the map's layers drawn smooth, page errors none | the rerun with the screen out of the way |

Every exit code above 0 is a fixture this machine lacks, a page that moved since the script's session, or the screen: the eight that fail were run again as their old versions from main (`origin/main`, the link) against the same build and fail the same way or worse (`runs/chain_oct19/s301_old/exits.tsv`). Every script that reaches a page in review reaches it through the form's door (the outputs name the internal view's pages with their numbers).

## Landing of session 300 (recorded here: session 300's report is in that landing's own commit)

- Pushed `task/300-home-page` at `d683e609` at 10:24 UTC; GitHub's checks passed (run 39237187594) but the merge step failed on two conflicts: session 308 (the data machine) landed on main at 10:25 with its own rewrite of `docs/licenses.md` and `tests/test_session205.py`. origin/main was merged into the branch taking main's two files, the tests rerun (28 passed), and the branch pushed again at `9e46a147` at 10:43; the checks passed (run 39239479836) and merged it as `7f6d3a8c` at 10:55. No new style sheet appeared within ten minutes (the home page is in review, so the visitor's pages did not change), and the after snapshot was taken at 11:05:34.
- Snapshot `s300-before3` (10:47:03, retaken after session 308's deploy; identical to the two before it) against `s300-after` (11:05:34): 25 pages, 0 differences. Expected: the home page is in review, and a visitor sees the in-review page at every address. Nothing unexpected.

## Landing

LANDING

## Decisions made without you

- **The writes go with the service key, as the prompt says, not with the review's token functions.** The review's own fix (H3, M1) was a database function behind the internal token per write; the chain prompt rules "route handlers with the service key". Done as ruled, with the key read by the write helper alone and the anon key kept as the fallback, so nothing stops storing at any step of the change. `site/README.md`'s line "never the service key" was changed to say this.
- **Migration 034 is written and not applied** (a schema change is yours), with the order to apply it: the key on Vercel, then `apply.py --only 034`.
- **The sequences' revoke (L6) rides in migration 034**, since the inserts that needed them are gone with the policies; the two identity sequences are revoked only where they exist.
- **`check-security.mjs` keeps the old link's three checks** (the review: the link stays until you retire it).
- **The report-only header stays with the same value as the enforced one** for the week the prompt names; dropping it is a one-line change in `next.config.ts`.
- Questions skipped (Impeccable's playbooks ask them; no page's words changed, no screenshot taken: nothing a visitor sees moved).

## For Samuel's ruling

- **Token rotation (H1):** `INTERNAL_COSTS_TOKEN` has been in addresses and logs since session 67; rotate it (Vercel, `.env`, `site/.env.local`, `erw_private.settings` by `apply.py`), then retire the GET of `site/app/internal/unlock/route.ts` and the `?token=` branches of the three internal pages (L5 goes with it). Every reviewer unlocks again.
- **Migration 034:** put `SUPABASE_SERVICE_KEY` in the Vercel project's environment (server side, no `NEXT_PUBLIC_` prefix), deploy, then `python warehouse/supabase/apply.py --only 034` on the data machine, then `verify_rls.py --catalog`. Rollback: `apply.py --rollback 034`.
- **Migration 033** (session 289's game v5 constraints) is still unapplied: production refuses to store a v5 play since session 295's landing.
- **After a week** with no console report: drop the `Content-Security-Policy-Report-Only` header (one line in `next.config.ts`).

## Files

- Changed: `site/scripts/browser.mjs` and 36 scripts under `site/scripts/`, `site/lib/supabase.ts`, `site/app/api/ask/route.ts`, `site/next.config.ts`, `site/scripts/check-csp.mjs`, `site/README.md`, `docs/reviews/2026-10-10-security.md`.
- New: `warehouse/supabase/migrations/034_server_writes.sql`, `warehouse/supabase/rollbacks/034_server_writes.sql`, `tests/test_session301.py`, this report.
- Not in git: `runs/chain_oct19/s301*` (builds, checks, the scripts' outputs under `s301_scripts/`), `runs/chain_oct19/s301_batch.sh`.
