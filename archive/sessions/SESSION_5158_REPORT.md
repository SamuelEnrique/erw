# Session 5158 report: the stack's landing row (row 23)

13 November 2026, unattended, `portable-laptop` window P2. Branch `wip/5150-security`, worktree `erw-p2-5150`. Model spend USD 0. Pulls: the snapshots of the live pages around the push of the row. Nothing built, nothing landed, no warehouse data written.

Clock: precheck 19:23 UTC, the tests by 19:27 UTC, the row after this report. Inside the long end of 1:00.

## Read these first

- **The stack is asked for as landing row 23** of `docs/state/landing_request_portable.md`: `wip/5150-security`, task `5158-security`, port 5101. The desktop's landing window lands it.
- **What a visitor sees does not change.** The stack changes six route handlers, three library files, one verifier, one pinned requirement, tests and documents. No page's text, no table, no number.
- **`wip/5157-retire-link` is not in the row.** It waits for your word (session 5157's report).
- **The whole suite was not run here**: 1.1 GB of memory was free (three windows on 16 GB), under the 2 GB the chains' rule asks before a gate. The gate on the desktop runs it.

## What the row holds (sessions 5150 to 5157)

| Session | What | Rows of the list |
|---|---|---|
| 5150 (carrying 5102) | `/internal/lock` refuses a cross-site request; four more limits; the standing tests of every route, of secrets and of the headers; the guards' own proof runs again | 2, 15 to 21 |
| 5151 | the write key on the host: what a read proves, pinned | 6 |
| 5152 | `certifi` 2026.10.18 pinned; the audits' table | 8, 9 |
| 5153 | the policy's inline scripts: the cost of a nonce; the site writes none, pinned | 22 |
| 5154 | `USAGE_VISITORS=off`: the count with no visitor value (default unchanged) | 23 |
| 5155 | `USAGE_TOOL_PAGES=off`: nothing recorded for the marked pages (default unchanged) | 24 |
| 5156 | the verifier's step 6: functions the anon key may execute | 7, 12 |
| 5157 | rows 3 and 4 name the retirement's branch | 3, 4 |

## Read before the gate, since this window cannot run it

- **The gate's own checks against the new limits.** Read in `site/scripts/`: `check-security.mjs` asks `/api/entity` and `/api/subscribe/confirm` once each with input that is refused before the limit is counted; `check-routes.mjs` and `play-battery.mjs` read `/api/play/top` a handful of times (the limit is 240 an hour); `check-csp.mjs` submits the sign-up form from a real browser (well under 8 kB). `test-battery-stack.mjs` goes to `/internal/lock` by a navigation of its own browser, which is not a cross-site request. None should meet a limit.
- **Two new settings, both unset everywhere**: `USAGE_VISITORS`, `USAGE_TOOL_PAGES`. Unset is the behaviour of today.

## Checks, with exit codes

| Command | Exit | Result |
|---|---|---|
| `scripts/precheck.py --what "session 5158 (window P2)"` | 0 | on duty |
| `git merge origin/main` | 0 | merged (`9755e5dff`) |
| `pytest` on the 26 test files that name a file the stack changed | 0 | 356 passed, 7 skipped |
| `node ... scripts/test-usage.mjs`, `scripts/test-curtain.mjs` (session 5157, the same tree for these files) | 0, 0 | 16 and 8 tests passed |
| `tsc` on the stack's nine changed site files (session 5157's run, which read them) | 0 | no error |

- **Not run:** the build, the whole suite (1,111 test files), every `check-*.mjs`.
- **Not verified:** the gate's checks against the new limits (read, above; not run).

## Decisions made without you

- **One row for the whole stack**, not one a session: the changes are small and of one subject.
- **The whole suite not started at 1.1 GB free**, as chain 224's rule says of a gate on a machine short of memory.
- **Port 5101** (row 18 used 5100).

## For Samuel's ruling

Nothing new. The rulings of sessions 5150 to 5157 stand, each with its default.

## The prompt

`queue/done/237-day-14-november-portable-p2-security-continued.md`, "Sessions 5151 to 5158: chain 234's unfinished steps", step 9 of the list session 5150 rebuilt.
