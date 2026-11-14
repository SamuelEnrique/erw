# Session 5174 report: a signed-in user may do no more than the public key, proven and brought into the verifier

13 November 2026, unattended, `portable-laptop` window P2. Branch `wip/5166-security`, worktree `erw-p2-5150`. Model spend USD 0. Pulls: read-only transactions on the catalog; `verify_rls.py --catalog` once. Nothing built, nothing landed, no warehouse data written; no account made, nothing changed in the database.

Clock: precheck 20:32 UTC, the read 20:33 UTC, the tests by 20:35 UTC. Inside the long end of 1:00.

## Read these first

- **Sign-ups are on in Supabase Auth** (row 12, your dashboard setting). So anyone may make an account and hold a signed-in token.
- **Every check so far proved what the public key may do. None proved what a signed-in user may do.** `docs/security.md` has said since 20 October that such a user "reads nothing the anon key cannot". That was a reading, not a proof.
- **It is true, and now proven.** From the catalog: on the 31 tables, views and sequences of `public`, the signed-in role holds no privilege the public role lacks; no policy is for it alone; no function is for it alone.
- **No account has ever been made** (`auth.users` is empty).
- **The verifier gains step 9** and passed with all nine at 20:35 UTC. A grant or a policy for signed-in users, added later by a migration or by hand, now fails it.
- So row 12 is less urgent than it read: turning sign-ups off removes a door that opens onto nothing. The default stands.
- **Waits, polled at 20:32 UTC:** landing row 23 not landed; the scan of the git history still running (58 minutes at 20:35 UTC).

## What to review

1. `warehouse/supabase/verify_rls.py`: `check_signed_in`.
2. `tests/test_session5174.py`: 8 tests, on a stand-in.
3. Row 12 of `docs/reviews/security-faults-2026-11-13.md`.

## What was done

- `runs/s5174/authenticated.py`: the two roles' privileges on every relation of `public`, side by side; the policies of `public` and `storage` that name the signed-in role or every role; the functions; three schemas; the count of accounts.
- Step 9 of the verifier and its test.
- The verifier run for real: exit 0, 0 mismatches, nine steps.

## Checks, with exit codes

| Command | Exit | Result |
|---|---|---|
| `scripts/precheck.py --what "session 5174 (window P2)"` | 0 | on duty |
| `git merge origin/main` | 0 | merged |
| `runs/s5174/authenticated.py` | 0 | nothing more for the signed-in role; 0 accounts |
| `warehouse/supabase/verify_rls.py --catalog` with step 9 | 0 | PASS, 0 mismatches |
| `pytest` on `test_session5174`, `5173`, `5172`, `5170`, `5156`, `5163` and the four that pin the verifier | 0 | 185 passed, 1 skipped |

- **Not run:** the build, the whole suite. No account was made to try a signed-in request: the catalog is the proof, and making an account writes to the project.

## Decisions made without you

- **No test account made.** A signed-in request would have been one more proof; it needs an account in the project's Auth, which is a write, and an email.
- **Row 12 stays a ruling with its default**, now with what it guards against said.

## For Samuel's ruling

Nothing new.

## The prompt

`queue/done/247-day-15-november-portable-p2-security-continued.md`, "Sessions 5175 to 5178: a fresh pass" (taken early: the steps before it wait).
