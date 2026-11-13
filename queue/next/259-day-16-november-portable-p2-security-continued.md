# Chain of 16 November 2026: sessions 5182 to 5197, portable-laptop window P2, unattended: security and the cookieless usage counts continued (roadmap item 7)

machine: portable-laptop-window2

Written first by session 5166 of chain 247 (`queue/done/247-day-15-november-portable-p2-security-continued.md`) on 13 November 2026 at about 20:05 UTC, as that chain's rules ask, and to be updated by its session 5181 with what chain 247 did not finish. The first queue number never used on origin's main or any branch was 259 (258 was the highest used). It takes sessions 5182 to 5197, sixteen numbers after chain 247's last (5181); session 5182 checks each is free on origin's main and on every branch, skips a taken one upward and says so. **This window's range ends at 5199: the chain after this one needs a new range from the owner, and session 5197 says so in its next file instead of taking numbers outside the range.** Model: Fable 5.2, high effort.

## Who else runs on this machine

- **P1**: the five tools, sessions 5000 to 5099. The only window that builds.
- **P2** (this window): sessions 5100 to 5199.
- **P3**: the AI chat, sessions 5200 to 5299.
- **This window never builds the site and never lands**: no `npm run build`, no `next start`, no `scripts/land_check.py`. Its proof is the Python and Node unit tests, a type check, and reading the code. It never changes the main checkout's branch or working files; all its work happens in git worktrees beside `C:\Users\lossa\Documents\erw` named `erw-p2-<N>`, on `wip/5150-<topic>`, `wip/5166-<topic>` or `wip/5182-<topic>` stacks, with `C:\Users\lossa\Documents\erw\.venv\Scripts\python.exe`. Its commits for `main` (the queue's, a landing row) are made in `erw-p2-row`, detached at `origin/main`, and pushed from there.

## Rules for every session

The rules of `queue/done/247-day-15-november-portable-p2-security-continued.md` hold word for word (they are chain 237's, which are chain 234's: precheck first; `git fetch origin` and `origin/main` merged before work; default-neutral; `site/lib/release.ts` untouched; nothing sent or posted; no warehouse data written; no layout redesign; no brand work; model spend under the owner's key at USD 2 a session and USD 20 the chain; the report in short bullets with "Decisions made without you" and "For Samuel's ruling"; no em or en dash; never stop to ask; the weekly limit the only stop; a stack ready to land gets a requested row in `docs/state/landing_request_portable.md` (port 5100 upward) and the desktop's landing window lands it; no step waits on a landing or on another window; the files this window owns are `site/proxy.ts`, `site/lib/guard.ts`, `site/components/Usage.tsx`, `docs/security.md` and their tests; the five tools' pages (P1's), the Ask engine (P3's), the Digest and the Roundup are not touched; the queue step is always by name; the queue step by the script's own function in `erw-p2-row` under the window's name where the command refuses; a push to `main` has rule 8's snapshots).

Two additions of chain 237, from its own faults:

- **Code is edited by hand** (the editor), never by a scripted replacement of several lines: twice a scripted edit dropped a line.
- **The whole suite is not started on this machine under 2 GB of free memory**; the tests that name the touched files are the proof, and the landing desk's gate runs the suite.

The addition of chain 219 holds: if the two lists below are still empty when session 5182 starts, chain 247 stopped before its session 5181, and session 5182 rebuilds them from chain 247's reports (`archive/sessions/SESSION_5166_REPORT.md` onward, on its branches), its branches (`git branch -r | grep -E "wip/51"`), `docs/reviews/security-faults-2026-11-13.md`, `docs/state/note_2026-11-13_portable_p2.md` and `docs/state/landing_request_portable.md`, and says so.

Read first: chain 247's note if it wrote one (`docs/state/note_<date>_portable_p2.md`), else chain 237's (`docs/state/note_2026-11-13_portable_p2.md`); `docs/reviews/security-faults-2026-11-13.md`, `docs/security.md`, `docs/state/landing_request_portable.md`, `CLAUDE.md`.

## Session 5182: the next file, the ground

Long end 1:00. The next file first (or, the range being at its end, the line that says a new range is needed), committed alone and pushed. Then the precheck, `git fetch`, `git worktree list` with every `erw-p2-<N>` worktree of a landed branch removed, whether each branch of chains 234, 237 and 247 is an ancestor of `origin/main`, and each landing row of this window with its state, written to the report. Then the first unfinished step below.

## Sessions 5183 to 5190: chain 247's unfinished steps

Long end 1:00 each. One step a session, in the order session 5181 lists them below; each fix with a test, stacked on this window's newest unlanded branch; a row that needs the owner written as a ruling with a default. A step that waits on a landing or on a ruling that has not come is said in one line, and the next is taken.

### Unfinished steps (to be written by session 5181 of chain 247)

(empty until session 5181 writes it)

### Open rows of `docs/reviews/security-faults-2026-11-13.md` (to be written by session 5181 of chain 247)

(empty until session 5181 writes it)

## Sessions 5191 to 5194: a fresh pass

Long end 1:00 each. The same review (headers; the guard's checks on the internal view; input limits on every API route; secrets never in client code, the source scanned, nothing built; rate limits; `npm audit` and `pip-audit`; the usage counts' method against the code) run again against the code as it now stands on `origin/main` and on this window's unlanded stack. Chain 237's standing tests do most of the reading (`tests/test_session5102.py`, `5153`, `5155`, `5159` to `5163`): the pass reads what they cannot (a new page's words on privacy, a new workflow, a new kind of request). Each new row added to the faults file and fixed the same way.

## Session 5195: the landing rows and the records

Long end 1:00. Each unlanded stack of this window with its requested row in `docs/state/landing_request_portable.md` (head, task name, port, the tests run); `docs/security.md` and the faults file agreeing with the code on the stack; roadmap item 7's state said in the report (the roadmap itself is a person's to write).

## Session 5196: the note

Long end 1:00. `docs/state/note_<date>_portable_p2.md` (its name checked free first), in short bullets: the security rows before and after, what waits in which landing row, the rulings waiting with their defaults.

## Session 5197: the next file, the queue

Long end 1:00. The next file (written by session 5182, or the line that asks for a new range) updated with what this chain did not finish, pushed alone; then the queue step by name as above, and the file it names run the same way, starting with its precheck.
