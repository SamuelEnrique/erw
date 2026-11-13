# Session 5156 report: rows 7 and 12 read again; a guard for new database functions

13 November 2026, unattended, `portable-laptop` window P2. Branch `wip/5150-security`, worktree `erw-p2-5150`. Model spend USD 0. Pulls: read-only transactions on the database's catalog, `verify_rls.py --catalog` twice (GETs with the anon key), one GET of the public auth settings. Nothing built, nothing landed, no warehouse data written, nothing changed in the database.

Clock: precheck 19:08 UTC, the reads 19:09 to 19:12 UTC, the tests 19:13 UTC. Inside the long end of 1:00.

## Read these first

- **Both rows are as they were on 20 October.** The default privileges still hand a new table, sequence and function to the anon key. Sign-ups in Supabase Auth are still on. Both stay your rulings, same defaults.
- **The guards for tables hold**: the trigger is enabled, all 25 tables have row-level security on, the anon key can write to none, the verifier passes.
- **One hole in those guards, now closed in the verifier: a new function.** Nothing covered it. The anon key may execute 23 functions today; each asks for a credential, so nothing is open. But the next function added would have been open with no check to say so.
  - `verify_rls.py --catalog` now lists those 23 with what each asks for, and fails on one that is not listed.
- **The verifier is run by sessions only.** No scheduled job runs it. Ruling 2.

## What to review

1. `warehouse/supabase/verify_rls.py`: `ANON_FUNCTIONS` (the list) and `check_functions` (step 6). Nothing else in the file changed.
2. `docs/security.md`, "The guards on new tables and functions, and sign-ups".
3. Rows 7 and 12 of `docs/reviews/security-faults-2026-11-13.md`.

## What was done

- **The catalog read** (`runs/s5156/guards.py`): `pg_default_acl`, the event triggers, row-level security table by table, the anon key's write privileges and write policies.
- **The functions read** (`runs/s5156/functions.py`): 33 functions of `public` that are not an extension's; the anon key may execute 23, may not execute 10 (the lock and scheduler functions, `site_ask_admit`, `thesis_token_ok`, `eqr_summary_store`).
- **The auth settings**: `disable_signup` false, email provider on, `mailer_autoconfirm` false.
- **Step 6 of the verifier**, with its test on a stand-in for the catalog (`tests/test_session5156.py`, 8 tests): the list passes; a new function fails; a listed function that no longer takes the token first fails; a function the anon key lost is said and is no failure.
- **The verifier run for real** with step 6: exit 0, 0 mismatches.

## Checks, with exit codes

| Command | Exit | Result |
|---|---|---|
| `scripts/precheck.py --what "session 5156 (window P2)"` | 0 | on duty |
| `git merge origin/main` | 0 | merged |
| `runs/s5156/guards.py` (catalog part) | 0 | as above (its last step, the auth settings, first failed: see below) |
| `warehouse/supabase/verify_rls.py --catalog`, before the change | 0 | PASS, 0 mismatches |
| the same, with step 6 | 0 | PASS, 0 mismatches, 23 functions |
| `pytest` on `test_session177`, `181`, `232`, `233` (they pin the verifier) | 0 | 137 passed, 1 skipped |
| `pytest` on `test_session5156`, `5155`, `5154`, `5152`, `5151`, `371`, `1501` | 0 | 53 passed |

- **Not run:** the build, the whole suite.
- **Not verified:** that each of the 19 token functions refuses a wrong token (the verifier's step 4 proves it for nine read functions; the others write, and a call of them is not a read).

## Faults of mine, corrected

- The first read of the auth settings asked the address in `.env` as it stands (it ends in `/rest/v1/`): HTTP 404. Asked again at the project's own origin: 200.
- The first run of the verifier found no settings (the worktree has no `.env`): exit 2. Run again with the three settings in the process's environment, never printed.
- My scripted edit joined two lines of the verifier (`def main` and its first statement): an `IndentationError` on the first run, corrected before the commit.

## Decisions made without you

- **A change in `warehouse/supabase/verify_rls.py`**, which is not one of the four files this window owns. It is the security review's own verifier (session 177), it only reads, and no schedule runs it.
- **The list names functions, not signatures.** An overload of a listed name would pass; the step checks that a `p_token` function still takes the token first.
- **No revoke written.** Every function open to the anon key asks for a credential; closing the default itself is row 7's choice (a), yours.

## For Samuel's ruling

1. Row 7 (M6). Default: (b) as today, now with step 6. (a) a migration that revokes the default privileges for `postgres` and `supabase_admin`.
2. Whether `verify_rls.py --catalog` runs on a schedule (the weekly vacuum's workflow, or the daily run). Default: no change; sessions run it. A schedule would catch a new open function within a day or a week, and would need `SUPABASE_DB_URL` where it runs.
3. Row 12 (L8), sign-ups. Default: (a) turn off "Allow new users to sign up" when you are next in the dashboard.

## The prompt

`queue/done/237-day-14-november-portable-p2-security-continued.md`, "Sessions 5151 to 5158: chain 234's unfinished steps", step 7 of the list session 5150 rebuilt.
