# Chain of 14 November 2026: sessions 5150 to 5165, portable-laptop window P2, unattended: security and the cookieless usage counts continued (roadmap item 7)

machine: portable-laptop-window2

Written first by session 5100 of chain 234 (`queue/done/234-day-13-november-portable-p2-security.md`) on 13 November 2026 at about 10:00 UTC, as that chain's rules ask, and to be updated by its session 5149 with what chain 234 did not finish. The first queue number free on origin's main and every branch was 236 (window P3 took 235 in the same minute). It takes sessions 5150 to 5165, sixteen numbers after chain 234's last (5149); session 5150 checks each is free on origin's main and on every branch, skips a taken one upward and says so. Model: Fable 5.2, high effort.

## Who else runs on this machine

- **P1**: the five tools, sessions 5000 to 5099. The only window that builds.
- **P2** (this window): sessions 5100 to 5199.
- **P3**: the AI chat, sessions 5200 to 5299.
- **This window never builds the site and never lands**: no `npm run build`, no `next start`, no `scripts/land_check.py`. Its proof is the Python and Node unit tests and reading the code. It never changes the main checkout's branch or working files (except the queue commits `scripts/chain_queue.py` makes, or the same move by hand where the script refuses the window's machine line); all its work happens in git worktrees beside `C:\Users\lossa\Documents\erw` named `erw-p2-<N>`, on `wip/5100-<topic>` or `wip/5150-<topic>` stacks, with `C:\Users\lossa\Documents\erw\.venv\Scripts\python.exe`.

## Rules for every session

The rules of `queue/done/234-day-13-november-portable-p2-security.md` hold word for word: precheck first; `git fetch origin` and `origin/main` merged before work; default-neutral; `site/lib/release.ts` untouched; nothing sent or posted; no warehouse data written; no layout redesign; no brand work; model spend under the owner's key at USD 2 a session and USD 20 the chain; the report in short bullets with "Decisions made without you" and "For Samuel's ruling"; no em or en dash; never stop to ask; the weekly limit the only stop; a stack ready to land gets a requested row in `docs/state/landing_request_portable.md` (port 5100 upward) and the desktop's landing window lands it; no step waits on a landing or on another window; the files this window owns are `site/proxy.ts`, `site/lib/guard.ts`, `site/components/Usage.tsx`, `docs/security.md` and their tests; the five tools' pages (P1's), the Ask engine (P3's), the Digest and the Roundup are not touched; the queue step is always by name.

The addition of chain 219 holds: if the two lists below are still empty when session 5150 starts, chain 234 stopped before its session 5149, and session 5150 rebuilds them from chain 234's reports (`archive/sessions/SESSION_5100_REPORT.md` onward, on its branches), its branches (`git branch -r | grep -E "wip/51"`), `docs/reviews/security-faults-2026-11-13.md` and `docs/state/landing_request_portable.md`, and says so.

Read first: chain 234's note (`docs/state/note_<date>_portable_p2.md`), `docs/reviews/security-faults-2026-11-13.md`, `docs/security.md`, `docs/reviews/2026-10-10-security.md`, `docs/state/landing_request_portable.md`, `CLAUDE.md`.

## Session 5150: the next file, the ground

Long end 1:00. The next file first (`queue/next/<first free number>-day-<day>-november-portable-p2-security-continued.md`, `machine: portable-laptop-window2`, at least 14 sessions, this chain's unfinished steps first), committed alone and pushed. Then the precheck, `git fetch`, `git worktree list` with every `erw-p2-<N>` worktree of a landed branch removed, whether each branch of chain 234 is an ancestor of `origin/main`, and each landing row of this window with its state, written to the report. Then the first unfinished step below.

## Sessions 5151 to 5158: chain 234's unfinished steps

Long end 1:00 each. One step a session, in the order session 5149 lists them below; each fix with a test, stacked on this window's newest unlanded branch; a row that needs the owner written as a ruling with a default.

### Unfinished steps (to be written by session 5149 of chain 234)

(empty until session 5149 writes it)

### Open rows of `docs/reviews/security-faults-2026-11-13.md` (to be written by session 5149 of chain 234)

(empty until session 5149 writes it)

## Sessions 5159 to 5162: a fresh pass

Long end 1:00 each. The same review (headers; the guard's checks on the internal view; input limits on every API route; secrets never in client code, the source scanned, nothing built; rate limits; `npm audit` and `pip-audit`; the usage counts' method against the code) run again against the code as it now stands on `origin/main` and on this window's unlanded stack; each new row added to the faults file and fixed the same way.

## Session 5163: the landing rows and the records

Long end 1:00. Each unlanded stack of this window with its requested row in `docs/state/landing_request_portable.md` (head, task name, port, the tests run); `docs/security.md` and the faults file agreeing with the code on the stack; roadmap item 7's state said in the report (the roadmap itself is a person's to write).

## Session 5164: the note

Long end 1:00. `docs/state/note_<date>_portable_p2.md` (its name checked free first), in short bullets: the security rows before and after, what waits in which landing row, the rulings waiting with their defaults.

## Session 5165: the next file, the queue

Long end 1:00. The next file (written by session 5150) updated with what this chain did not finish, pushed alone; then `.venv\Scripts\python.exe scripts\chain_queue.py next --file <that name>` (or the same move by hand where the script refuses the window's machine line, said so), and the file it names run the same way, starting with its precheck.
