# Session 5170 report: each database function open to the anon key checks its credential first, proven from the migrations

13 November 2026, unattended, `portable-laptop` window P2. Branch `wip/5166-security`, worktree `erw-p2-5150`. Model spend USD 0. No pull, no read of the database. Nothing built, nothing landed, no warehouse data written.

Clock: precheck 20:14 UTC, the tests by 20:17 UTC. Inside the long end of 1:00.

## Read these first

- **Something chain 237 asserted without proof is now proven.** Session 5156 listed the 23 database functions the anon key may execute and said each "asks for a credential". It did not show that each checks it before doing anything. Its own report said so under "Not verified".
- **All 19 that take a token check it first.** Read from each function's newest definition in the migrations: the token is compared and "not authorized" raised before any other statement. 13 use the shared check, 6 read the secret and compare (the older form, migrations 010 to 027).
- **The other four**: the two subscription functions compare the address's signed token first and change nothing on a wrong one; a thesis run's one-time key is compared, under a lock, before the run is written, and is cleared when used; the fourth is Supabase's own trigger function.
- **A test now holds each opening** (`tests/test_session5170.py`, 7 tests). A migration that redefines one of them without its check, or with a statement before it, fails the suite.
- **Waits, polled at 20:14 UTC:** landing row 23 not landed; the scan of the git history still running (39 minutes at 20:16 UTC).

## What to review

1. `tests/test_session5170.py`.
2. The paragraph "Session 5170" in `docs/reviews/security-faults-2026-11-13.md`.

## What was done

- `runs/s5170/functions.py`: for each name in the verifier's list, the last migration that creates it and the first statements of its body.
- The test: the 19 token functions by their two forms; each a definer's function with an empty search path; the shared check itself (a secret of 24 characters or more, equal); the subscription functions; the one-time key.
- One line in `warehouse/supabase/verify_rls.py`'s comment names the test.

## Checks, with exit codes

| Command | Exit | Result |
|---|---|---|
| `scripts/precheck.py --what "session 5170 (window P2)"` | 0 | on duty |
| `git merge origin/main` | 0 | merged |
| `runs/s5170/functions.py` | 0 | 22 definitions found, 1 the host's own |
| `pytest tests/test_session5170.py` with `5156`, first run | 1 | the test's own fault: "for update" in a read taken for a write |
| the same, corrected, with `5163` | 0 | 21 passed |

- **Not run:** the build, the whole suite, the verifier against the database (session 5156 ran it: exit 0).
- **Not verified:** that the database's definitions are the migrations' newest (a function changed by hand in the database would not be seen here). The verifier's step 4 calls nine of the read functions with a wrong token and each refuses; the write functions are not called.

## Decisions made without you

- **The six older functions left in their older form.** They are correct; rewriting them to the shared check is a migration, the owner's.
- **The subscription tokens are compared with `<>`**, not in constant time. The limits of this stack (60 and 120 an hour from one address) and the 64 hexadecimal characters of the token make a timing guess pointless; noted here and not a row.

## For Samuel's ruling

Nothing new.

## The prompt

`queue/done/247-day-15-november-portable-p2-security-continued.md`, "Sessions 5175 to 5178: a fresh pass" (taken early: the steps before it wait).
