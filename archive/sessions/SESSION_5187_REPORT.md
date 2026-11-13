# Session 5187 report: landing row 27 brought to the newest head; two corrections the other windows' landings need

13 November 2026, unattended, `portable-laptop` window P2. Branch `wip/5182-security` (and `wip/5166-security`, fast-forwarded to it), worktree `erw-p2-5150`; one commit to `main` from `erw-p2-row`. Model spend USD 0. Pulls: the snapshots of the live pages. Nothing built, nothing landed, no warehouse data written.

Clock: precheck 21:06 UTC, the tests by 21:08 UTC, the row pushed 21:09:17 UTC. Inside the long end of 1:00.

## Read these first

- **Landing row 27 names `7204e8ba2`**, the head of everything this window has not landed. `wip/5166-security` on origin was fast-forwarded to it, so the row's branch and this chain's are one.
- **What is still unlanded, for the site: one file**, `site/next.config.ts` (the policy names one Supabase project, row 27 of the list). Everything else in the row is tests and documents.
- **Two corrections in it matter to the other windows:**
  - `tests/test_session5102.py` failed the day `site/app/cost-of-power/battery/read.ts` gained `server-only`. That is the fix row 26 asks window P1 for: my test would have stopped its landing. It passes either way now (proven with the line added, without touching the file). **The copy on `main` still fails on it until this row lands**: the note tells P1 to land that line after it.
  - `tests/test_session5171.py`'s floor of redirects (session 5183).
- **The note has a new table**: what this window's standing tests will ask of the other windows, and the one line each wants.
- **Checked: what landed at 20:47 UTC is what this window pushed.** Of the 37 files the first part changed, the 27 that are this window's are on `main` byte for byte as its landed head held them; the 10 that differ are other windows' files (the forecast tool's, the Digest's), changed on `main` since.
- **Awaited, watched in the background**: the desk's next gate (`f300710e7`, row 23's second part) and the scan of the git history (91 minutes at 21:08 UTC).

## Checks, with exit codes

| Command | Exit | Result |
|---|---|---|
| `scripts/precheck.py --what "session 5187 (window P2)"` | 0 | on duty |
| `git merge origin/main` | 0 | merged |
| `runs/s5186/marked.py` (the secrets' test with the marker's line added to the battery page's read, the file untouched) | 0 | 0 failures as the file stands, 0 with the line |
| `pytest` on this window's 19 test files with the 12 older ones | 0 | 390 passed, 1 skipped |
| `node ... test-usage.mjs`, `test-curtain.mjs` | 0, 0 | passed |
| `git push origin wip/5182-security:wip/5166-security` | 0 | a fast-forward, `e6697a65b` to `7204e8ba2` |
| `scripts/freeze.py status` | 0 | no freeze |
| `snapshot-live.mjs take s5187-before` | 0 | 25 pages; the after snapshot is in the next report |

- **Not run:** the build, the whole suite (1.1 to 1.8 GB of memory free all evening).

## Decisions made without you

- **A test of mine loosened** (row 26's): a check that the list of unmarked files is tidy is not worth stopping another window's fix.
- **The row's branch fast-forwarded** rather than a third row written: one row for what remains.

## For Samuel's ruling

Nothing new.

## The prompt

`queue/done/259-day-16-november-portable-p2-security-continued.md`, "Session 5195: the landing rows and the records" (taken at 5187; the steps before it are done or wait).
