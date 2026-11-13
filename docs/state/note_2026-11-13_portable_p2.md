# Note: security and the usage counts, 13 November 2026 (chains 234 and 237, portable-laptop window P2)

Energy Research Warehouse (ERW). Written by session 5164 of chain 237 (`queue/done/237-day-14-november-portable-p2-security-continued.md`), roadmap item 7. It covers chain 234 too (`queue/done/234-day-13-november-portable-p2-security.md`), which stopped inside its third session and wrote no note. Chain 234 ran sessions 5100 to 5102 from 09:35 to 10:27 UTC; chain 237 ran sessions 5150 to 5165 from 18:36 UTC on the same day. This window never builds and never lands: its proof is unit tests, type checks and reading the code.

## The list, before and after (`docs/reviews/security-faults-2026-11-13.md`)

| | When the list was written (session 5101) | After chain 237 (session 5163) | After chain 247 (session 5177) |
|---|---:|---:|---:|
| Rows | 25 | 32 | 34 |
| Open (a session's to take) | 12 | 0 | 0 |
| Fixed, waiting on a landing | 1 | 10 | 10 |
| Closed (fixed and live) | 0 | 1 | 1 |
| Rulings, each with a default | 8 | 13 | 15 |
| Noted | 4 | 8 | 8 |

- **Closed:** row 1. A visitor could read a page in review at its transport addresses. Fixed by session 5101, landed at `b1ea7427a`, proven on production after the deploy.
- **Fixed, on `wip/5150-security`:** `/internal/lock` refuses a cross-site request; limits on the email's two token doors, the map's card and the leaderboard; standing tests of every route's body and address, of secrets, of the headers, of the internal view; the policy names this site's own Supabase project; `certifi` without the compromised root; the guards' own proof runs again.
- **Nothing is open.** What remains is yours.
- **Landed since this note was first written** (session 5185, chain 259): the desktop's landing window landed the stack's first part, sessions 5150 to 5158, at `ad7f16ca6` on 13 November at 20:47 UTC (every check of the gate passed; snapshots 0 differences). Rows 2 and 15 to 21 are now closed: 9 closed, 2 fixed and not yet live (row 27, in the desk's next gate, and the `certifi` pin, which is in the file on `main`), 15 rulings, 8 noted. `/internal/lock` was read on production at 20:57 UTC: a cross-site request clears nothing.

## What waits, and where

| What | Where | What it needs |
|---|---|---|
| The stack: rows 2, 15 to 21, 27, row 8's `certifi`, the tests and the records | landing row 23 of `docs/state/landing_request_portable.md`: `wip/5150-security`, task `5158-security`, port 5101 | the desktop's landing window. `check-csp.mjs` on its build is the proof for row 27 |
| Chain 247's work (it holds the stack whole): the verifier's steps 7 to 9, seven more test files, rows 33 and 34 | landing row 27: `wip/5166-security`, task `5176-security`, port 5102 | the desktop's landing window; nothing in the site beyond row 23 |
| The old unlock link's retirement (rows 3 and 4) | `wip/5157-retire-link` (`3118c0a7a`), in no landing row | your word, after you have used `/internal/open` once on production |
| The count with no visitor value (row 23) | in the stack, off | `USAGE_VISITORS=off` on Vercel, if you choose it |
| Nothing recorded for the seven marked tool pages (row 24) | in the stack, off | `USAGE_TOOL_PAGES=off` on Vercel, if you choose it |

## The rulings waiting, with their defaults

1. **Rows 3 and 4, the old link.** Default: it stays until you say "land `wip/5157-retire-link`".
2. **Row 5, the token's rotation.** Default: after the link is retired, by you (Vercel, the two `.env` files, `erw_private.settings`).
3. **Row 6, the write key on the host.** Default: ask Ask one question on production in the internal view; an answer proves `SUPABASE_SERVICE_KEY` is there.
4. **Row 7, the default privileges.** Default: keep the trigger, the sweep and the verifier, which now also lists the functions the anon key may execute.
5. **Row 8, Python packages.** Default: a session on the data machine tries gridstatus 0.37.0 (it lifts the pins that hold the runner's `lxml`, `cryptography` and `certifi`) and the four major versions (`pillow`, `virtualenv`, `filelock`, `soupsieve`) on a branch.
6. **Row 9, the linter's `minimatch`.** Default: leave it until `typescript-eslint` moves.
7. **Row 10, the internal cookie's lifetime.** Default: keep the fixed digest; the rotation resets every browser.
8. **Row 11, `search_path`.** Default: leave the lock and scheduler functions as they are.
9. **Row 12, sign-ups in Supabase Auth.** Default: turn off "Allow new users to sign up" when you are next in the dashboard. Still on at 19:10 UTC.
10. **Row 22, inline scripts in the policy.** Default: keep the word. A nonce makes all 104 pages render on each request.
11. **Row 23, "no identifier".** Default: the daily code as today, deleted with its salt when the day is over.
12. **Row 24, "no usage count on tool pages".** Default: as today (seven marked pages count the page view and nothing after; 29 pages count in full).
13. **Row 26, the battery page's read without `server-only`.** Default: window P1 adds the one line.
14. **Row 33, Dependabot alerts are off** (chain 247). Default: you turn them on (GitHub, the repository, Settings, Advanced Security) and look that secret scanning and push protection are on; no session's token can.
15. **Row 34, a public repository and a fault written before its fix lands** (chain 247). Default: a High row's landing request says "an urgent security fix" and no more until it has landed.

Smaller ones, in the sessions' reports: the words of `/privacy` on limits (5162), the confirm route's "busy" words (5150), an internal address that names the write key's role (5151), whether the verifier runs on a schedule (5156), `connect-src 'self'` alone and `Cross-Origin-Opener-Policy` (5159), the browser checks and Do Not Track (5162), the comment in `site/lib/release.ts` after the retirement (5157), the queue script and a window's machine line (5150).

## What chain 247 added (sessions 5166 to 5178, 13 November 2026 from 19:56 UTC)

Its steps waited (the landing, the rulings, a scan of the git history), so it read what chain 237's fresh pass had not reached. No fault found; two rulings (rows 33 and 34); each part now has a standing test.

- **The workflows** (their permissions, the actions they run, how an input reaches a command) and **what a build offers** (no server action, no source map): `tests/test_session5169.py`.
- **Each of the 23 database functions the anon key may execute checks its credential first**, read from the migrations: `tests/test_session5170.py`.
- **Redirects and file reads**: every redirect to a path the code names; sixteen files read the disk, each by a name the site holds: `tests/test_session5171.py`.
- **The database verifier went from five steps to nine** (`warehouse/supabase/verify_rls.py --catalog`, exit 0 at 20:35 UTC): the functions (chain 237), the storage buckets (the 26 GB archive is private and closed), the API's reach and the scheduler (six jobs, no secret in a command), a signed-in user (holds nothing the anon key does not; no account was ever made).
- **A flaw in chain 237's own tests corrected**: their comment stripper left 4,680 characters of three files unread. Read now, those parts hold nothing forbidden.
- **The repository at GitHub**: public, one collaborator, Dependabot alerts off (row 33).

## For the next session of this window

- Chain 234's design and browser tools are on this laptop at the user level (session 5100's report). No run of them was needed by a chain that does not build.
- `erw-p2-5100` is removed; its `runs/` folders are in `erw-p2-5150\runs\from-erw-p2-5100\`.
- Worktrees: `erw-p2-5150` (`wip/5150-security`), `erw-p2-5157` (`wip/5157-retire-link`), `erw-p2-row` (detached, for commits to `main`). Remove the first when row 23 lands, the second when the retirement lands.
- This machine's venv still holds `certifi` 2026.7.22; the file pins 2026.10.18.
- Do not script multi-line edits of code in PowerShell: twice in this chain a comma bound tighter than a plus and a line was lost (caught before a commit both times). Edit by hand.
- The whole suite was never run here: 0.9 to 2.4 GB of memory free with three windows on 16 GB.
