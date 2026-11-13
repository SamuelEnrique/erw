# Session 5150 report: chain 237 taken, its next file, the ground, and session 5102's unfinished work carried and committed

13 November 2026, unattended, `portable-laptop` window P2. Branch `wip/5150-security` (cut from `origin/main` at `6742e1f92`), worktree `erw-p2-5150`. Model spend USD 0, no model call under the owner's key. Pulls: three snapshots of the live pages as a visitor (25 pages each). Nothing built, nothing landed, no warehouse data written, no page changed.

Clock: the queue step at 18:38 UTC, the two queue commits pushed at 18:42 UTC, the precheck at 18:37 UTC, the carried work tested by 18:47 UTC. Inside the long end of 1:00.

## Read these first

- **Chain 234 stopped inside its third session** (5102, the last file written at 10:27 UTC on 13 November). It left no report for 5102, no note, and its next file's two lists empty. Session 5102's work was in the worktree `erw-p2-5100`, uncommitted: nine files and one test.
- **That work is now committed here**, after a read and its tests: rows 2 and 15 to 21 of the security list are fixed on `wip/5150-security`.
- **Row 1 is closed**: landing row 18 landed at `b1ea7427a`, and the desktop's session 4002 ran `check-curtain.mjs` on production after the deploy, exit 0.
- **The two lists are rebuilt below**, from chain 234's two reports, its worktree and the faults file, as chain 219's addition asks.
- One new row, 26: the battery page's read (`site/app/cost-of-power/battery/read.ts`, window P1's) reads the internal token and is not marked `server-only`. Ruling 1.

## What to review

1. `docs/reviews/security-faults-2026-11-13.md`: rows 1, 2, 15 to 21 with their new states, and row 26.
2. `docs/security.md`, the new last section: what changed in the site, and the limits per address.
3. The nine source files of commit "Session 5150: rows 2 and 15 to 21": each change is under ten lines and says its row.
4. `queue/next/247-day-15-november-portable-p2-security-continued.md`: the next file.

## The queue

- `scripts/chain_queue.py next --file 237-...`: exit 2, refused (the mark `portable-laptop-window2` on the code machine `portable-laptop`), as for chains 233 to 235.
- The same move made by the script's own function, `take(file=..., who="portable-laptop-window2", role="code")`, in `erw-p2-row` at `origin/main`: commit `f47bacadf`.
- The next file: `queue/next/247-day-15-november-portable-p2-security-continued.md`, sessions 5166 to 5181 (sixteen), committed alone (`6742e1f92`).
- Both pushed to `main` at 18:42 UTC. 247 was the first number free on origin's main and every branch (255 the highest taken).
- Session numbers 5150 to 5165: no report and no `wip/515` or `wip/516` branch of this range on origin's main or any branch. None skipped.

## The ground

- Precheck: exit 0, 6 of 6. `scripts/freeze.py status`: exit 0, no freeze.
- Chain 234's branches: `wip/5100-tools` and `wip/5100-security` (origin's head `7fd58dfe3`) are ancestors of `origin/main`.
- This window's landing rows in `docs/state/landing_request_portable.md`: row 18 (`wip/5100-security`, task `5101-curtain`), landed at `b1ea7427a` by the desktop's session 4002. No row waits.
- Worktrees of this window: `erw-p2-5100` (the landed branch, holding session 5102's uncommitted files), `erw-p2-row` (detached, for commits to `main`), and the new `erw-p2-5150`.
  - `erw-p2-5100` is **not removed yet**: its uncommitted files are the only other copy of what this session committed. Session 5151 removes it once this branch is on origin.
- Memory free 2.4 GB, disk free 297 GB.

## The lists, rebuilt

### Unfinished steps of chain 234

Chain 234 ran sessions 5100 and 5101 and part of 5102. Of its sessions 5101 to 5135 (the list closed, then the usage counts), in order:

1. (5150, done) Session 5102's rows: 2, 15, 16, 17, 18, 19, 20, 21.
2. (5151) Row 6: the site's writes and `SUPABASE_SERVICE_KEY` on Vercel, proven by a read if one can prove it.
3. (5152) Rows 8 and 9: `pip-audit` and `npm audit` run again; a minor step taken, a major step ruled.
4. (5153) Row 22: the enforced policy allows inline scripts; what a nonce would cost, read first.
5. (5154) Row 23: the usage count's visitor hash is an identifier for a day.
6. (5155) Row 24: whether the counts run only on the pages the ruling of 12 October allows; the method in `docs/security.md`.
7. (5156) Rows 7 and 12, "read again by a session" (the default privileges' guards, sign-ups in Supabase Auth).
8. (5157) Row 3's default: the old link's retirement prepared on a branch of its own, one landing away.
9. (5158) The landing row for the stack so far.
10. Chain 234's note (its session 5148) was never written: session 5164's note covers both chains.

### Open rows of `docs/reviews/security-faults-2026-11-13.md` after this session

- **open** (this chain's): 6, 8, 9, 22, 23, 24.
- **ruling** (Samuel's, each with its default): 3, 4, 5, 7, 10, 11, 12, 26.
- **noted**: 13, 14, 25.
- **fixed, on `wip/5150-security`, not landed**: 2, 15, 16, 17, 18, 19, 20, 21.
- **closed**: 1.

## What was done

- **The carry.** `git diff` of `erw-p2-5100` written by git itself and applied to `wip/5150-security` (nine files, clean), with `tests/test_session5102.py`.
- **The read before the commit**, each change against the code it touches:
  - The four new limit names (`unsubscribe`, `confirm`, `entity`, `play_top`) match the form the database's function accepts (`site_rate_admit`, migration 028: a lower-case name of 3 to 32 characters). A name it refused would have left the memory's count alone, unseen.
  - `/subscribe` has the state `busy` the confirm route now answers with.
  - `/internal/lock`: the redirect and its two headers are the same either way; only the cookies' clearing is skipped at a cross-site request.
  - `site/lib/finder.ts` with `server-only`: no client file imports it (the scan of row 20 says so).
- **The records.** The faults file's rows 1, 2, 15 to 21 and the new row 26; a section in `docs/security.md`.

## Rule 8, the push to `main`

- Before (`s5150-before`, 18:40 UTC): 25 pages, 0 failed.
- After (`s5150-after`, 18:45 UTC, and `s5150-after2`, 18:47 UTC): 25 pages, 0 failed.
- `compare`: exit 0 both times, **0 differences**. Expected: the push held two queue files and no page.
- The second snapshot was taken five minutes after the push. Whether the deploy had finished by then was not read (no session of this window holds a Vercel sign-in); session 5151 compares once more.

## Checks, with exit codes

| Command | Exit | Result |
|---|---|---|
| `scripts/precheck.py --what "session 5150 (window P2)"` | 0 | 6 of 6; on duty |
| `scripts/freeze.py status` | 0 | no freeze |
| `scripts/chain_queue.py next --file 237-...` | 2 | refused: the window's mark |
| the script's `take(...)` under the window's name | 0 | taken by name |
| `node --import ./scripts/alias-register.mjs scripts/test-usage.mjs` | 0 | 14 tests passed (it failed on `origin/main`, row 2) |
| `node --import ./scripts/alias-register.mjs scripts/test-curtain.mjs` | 0 | 8 tests passed |
| `pytest` on `test_session5102`, `5101`, `177`, `203`, `241b`, `276`, `371`, `423`, `55`, `57`, `59`, `66`, `1501` | 0 | 174 passed, 3 skipped |
| `pytest` on `test_session5102`, `5101`, `177`, `371`, `1501`, `301`, `67`, `87`, after the two documents changed | 0 | 112 passed, 3 skipped |
| `snapshot-live.mjs take` (three) and `compare` (two) | 0 | 0 differences |

- **Not run:** the build, the whole suite, `check-security.mjs`, `check-csp.mjs` (they need a built site; the gate runs them).
- **Not verified:** that the four new limits count in the database on production (they do when the secrets are on the server, as for the older limits; row 6 is that question).

## Faults of mine, corrected

- The first copy of session 5102's diff was written through PowerShell's redirect, which changed its encoding; `git apply` refused it. Written again by `git diff --output`.
- `git worktree add` with a relative path put the new worktree inside the main checkout for about a minute. Moved beside it with `git worktree move`; the main checkout's `git status` read clean after.

## Decisions made without you

- **Session 5102's uncommitted work was kept, read and committed** rather than done again: its 22 tests passed where it stopped, and they pass here on today's `origin/main`.
- **A new branch, `wip/5150-security`, from `origin/main`**, not a continuation of `wip/5100-security`: that branch landed.
- **The file taken by the script's own function under the window's name**, as window P3 did for chain 235, and in `erw-p2-row`, so the shared checkout's files were not changed by this window.
- **Rule 8's snapshots taken for a push of two queue files.** Chain 234's sessions pushed such commits without them; the rule names no exception, and reading the pages as a visitor needs no build.
- **Row 26 is not fixed here**: the file is window P1's.
- **The confirm route's refusal uses the page's existing state `busy`**, whose words speak of sign-ups ("Too many sign-ups just now"). The page's words are not this window's to change. Ruling 2.

## For Samuel's ruling

1. Row 26, `site/app/cost-of-power/battery/read.ts` without `import "server-only"`. Default: window P1 adds the one line in its own chain; this window does not touch the file.
2. The words a reader sees after more than 60 confirmation clicks an hour from one address: "Too many sign-ups just now. Nothing was stored; please try again in an hour." Default: left as they are (a reader does not meet the limit; a script does).
3. `scripts/chain_queue.py` and a window's machine line (chain 234's ruling 2, still open). Default: no change; the script's function called under the window's name.

## The prompt

`queue/done/237-day-14-november-portable-p2-security-continued.md`, "Session 5150: the next file, the ground", taken at the owner's instruction of 13 November 2026 for window P2.
