# Session 5173 report: the scheduler and the API's reach, read and brought into the verifier

13 November 2026, unattended, `portable-laptop` window P2. Branch `wip/5166-security`, worktree `erw-p2-5150`. Model spend USD 0. Pulls: read-only transactions on the catalog; with the anon key, eight reads of one row of a table by name and one question of the GraphQL address; `verify_rls.py --catalog` twice. Nothing built, nothing landed, no warehouse data written; no function called, nothing changed in the database.

Clock: precheck 20:25 UTC, the reads 20:26 to 20:29 UTC, the tests by 20:31 UTC. Inside the long end of 1:00.

## Read these first

- **Nothing found.** The parts of the database no pass had read are closed.
  - **The scheduler.** Six scheduled jobs (the daily run, the latest prices, the hourly network, the Roundup, the weekly vacuum, the chain watch). Each is one call of `public.erw_dispatch` with a workflow's name. No job's command holds text shaped like a key: the token that starts a workflow is in the vault.
  - **The dispatcher** cannot be executed by the anon key. Nor can the lock functions. The anon role holds no usage on `cron`, `vault` or `erw_private`.
  - **The API serves schema `public` alone.** The anon role does hold usage on `net`, the extension that makes HTTP requests from the database (the host's default). It cannot be reached: a read of a table of `net`, `cron`, `vault`, `erw_private`, `storage` or `extensions` is answered "Invalid schema".
  - **No second API**: GraphQL is not enabled on the project.
- **The verifier gains step 8** and now has eight. It passed against the live project at 20:31 UTC.
- **Waits, polled at 20:25 UTC:** landing row 23 not landed; the scan of the git history still running (54 minutes at 20:31 UTC).

## What to review

1. `warehouse/supabase/verify_rls.py`: `CLOSED_SCHEMAS`, `KEY_SHAPED`, `JOB_COMMAND`, `check_surface`.
2. `tests/test_session5173.py`: 9 tests, on stand-ins.

## What was done

- `runs/s5173/cron.py`: the jobs (name, schedule, the first words of the command, whether the secret scanner's patterns match it), the functions that read the vault or post over the network, the anon role's use of four schemas, the count of secrets in the vault (one; its name and value not read).
- With the anon key: one row of one table in each of seven schemas asked for by name (`public` answered, the six others "Invalid schema"); the GraphQL address asked for its list of fields ("pg_graphql extension is not enabled").
- Step 8 of the verifier, and its test.

## Checks, with exit codes

| Command | Exit | Result |
|---|---|---|
| `scripts/precheck.py --what "session 5173 (window P2)"` | 0 | on duty |
| `git merge origin/main` | 0 | merged |
| `runs/s5173/cron.py` | 0 | six jobs, none with key-shaped text |
| a first probe of the API's root with each schema | 0 | useless: the root answers "Invalid API key" to the anon key for every schema, `public` too. Replaced by a read of a table by name |
| `warehouse/supabase/verify_rls.py --catalog` with step 8, first run | 1 | **my pattern's fault**: two jobs pass their inputs as `'{...}'::jsonb`, and the pattern for "one call of the dispatcher" did not allow the cast. The commands were read in full (no key-shaped text in them) and the pattern corrected |
| the same, corrected | 0 | PASS, 0 mismatches, eight steps |
| `pytest` on `test_session5173`, `5172`, `5170`, `5156`, `5163` and the four that pin the verifier | 0 | 177 passed, 1 skipped |

- **Not run:** the build, the whole suite.
- **Not verified:** what the one secret in the vault is scoped to at GitHub (a token's own permissions are GitHub's to show; no session reads it).

## Decisions made without you

- **A third step added to the verifier in one evening** (functions, buckets, the API's reach). It only reads; no schedule runs it; each step is a check nobody made before.
- **The anon role's usage on `net` left as it is**: the host grants it by an event trigger of its own each time the extension is created; revoking it would be undone, and the API does not serve the schema.
- **The two jobs' commands printed in full** in `runs/s5173/jobs.out` (not in git), after the scanner's patterns found nothing in them: they hold a branch name and two switches.

## For Samuel's ruling

Nothing new. (The GitHub token in the vault: its scope should be the least that starts a workflow, "Actions: write" on this one repository. Yours to look at when you are next in GitHub's settings; no session can read it.)

## The prompt

`queue/done/247-day-15-november-portable-p2-security-continued.md`, "Sessions 5175 to 5178: a fresh pass" (taken early: the steps before it wait).
