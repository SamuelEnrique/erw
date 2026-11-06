# Chain of 10 November 2026: sessions 1551 to 1564, code machine (samueloldlaptop), unattended: chain 163's unfinished steps, then the faults its sessions leave open

machine: samueloldlaptop

Written by session 1523, the first session of `queue/done/163-day-7-november-code-continued.md` (chain 158's continuation), in that file's form. Numbered 173, the first queue number free on origin's main and every branch. Its sessions: chain 163 runs as 1523 to 1536, and `queue/next/172-day-9-november-code-periodicals-continued.md` (chain 161's continuation, which runs before this file, the queue taking the lower number first) takes 1537 to 1550; so this file takes 1551 to 1564. Session 1551 checks each is free on origin's main and every branch and skips a taken one upward, saying so. Model: Fable 5.1, high effort. One Claude Code window for this chain; a second window (`machine: samueloldlaptop-window2`) may run beside it, so a build needs 3 GB free. Session 1536 of chain 163 updates this file with what that chain did not finish and the faults left open before it is taken.

## Why this chain

Chain 163 took chain 158's three unfinished steps (the datacenter replication's one difference, AccessLint on the rest of the pages, the package's local tests) and the faults chain 158's reads left open. This chain takes what chain 163 leaves: first its unfinished steps, in its order; then the faults still open, one a session; then the records and the note.

## Rules for every session

The rules of `queue/done/149-day-5-november-code-periodicals-excellent.md` hold word for word (one window; `.venv\Scripts\python.exe`; precheck first; `git fetch origin` and `origin/main` merged before work, generated lines as the union; worktrees beside `C:\Users\lossa\Documents\erw`, removed once landed; landings through `scripts/land_check.py` with every printed command run and its exit read, 2 GB free enough with this the only session, never between 14:00 and 16:15 UTC, the snapshots the only touch of production; the model under caps, USD 2 a session and USD 15 the chain; default-neutral: `site/lib/release.ts` untouched, nothing sent or posted, no warehouse data written, no brand or motion work, no design change to any page's layout; the report in short bullets with "Decisions made without you" and "For Samuel's ruling"; no em or en dash; the weekly limit the only stop). Also:

- **Never stop.** No session ends by stopping to ask; any wait over 20 minutes is stopped and the step done directly; no sleeping until a time of day.
- **Session 1485 writes the next file first** (`queue/next/<first free number at or above 161>-day-7-november-code-continued.md`, `machine: samueloldlaptop`, at least fourteen sessions: this chain's unfinished steps first, then the faults each read below leaves open), commits it alone and pushes it; session 1508 updates it.
- **Files other chains own, not touched:** the periodicals (`warehouse/news/`, `site/app/digest/`, `site/app/roundup/`, `docs/digest/`, `docs/roundup/`: chain 154's, which may still be running its last sessions when this chain starts; this chain waits for nothing, it simply does not touch them); the deals and datacenter extraction and pages (the personal laptop's chain 156); the large-load tables, the derived tables and the All grids tab's wiring (the desktop's chains 155 and 157); the Grid branches `wip/1400-grid` to `wip/1425-grid` (the hold).
- **A replication package** lives under `replication/<tool>/`: `replicate.py` (standard library plus pandas, nothing else) and `replicate.do` (the owner's Stata rules: no line continuation operators; one empty line between commands outside loops and none inside; every variable destringed with `force`), both reading only the tool's public downloads (`/data` CSVs) and the tool's own assumptions file, recomputing the page's headline figures and printing them beside the page's keyed figures with the difference; a test runs the Python one and asserts the difference within the tool's stated tolerance; the method note's "Replication" section says how to run both. Where a figure needs a held table, the package prints "license needed" for it and replicates the rest, and the method note says which.
- **The owner's standing rules for every tool page hold** (the key assumptions editable in place with their default and source as hover tips; inputs left, results right; scenarios A and B; no point of view; charts answer hover). This chain changes no layout.

In the rules above, read "Session 1485" as session 1551 and "session 1508" as session 1564 (the rules are chain 158's, carried word for word).

Read first: chain 163's note in `docs/state/` (session 1536 names it), `docs/state/note_2026-11-07_code_c158.md` (chain 158's), `docs/state/roadmap_item2_state_2026-11-07.md`, chain 163's session reports under `archive/sessions/` (1523 to 1536), `queue/done/163-day-7-november-code-continued.md`, `docs/roadmap.md`, `docs/security.md`, `docs/reviews/packages-open.md`, `CLAUDE.md`.

## Session 1551: the next file, the ground, chain 163's first unfinished step

Long end 1:00. The next file in `queue/next/`, numbered with the first queue number free on origin's main and every branch, in this file's form (`machine: samueloldlaptop`, at least fourteen sessions, this chain's unfinished steps first, then the faults its reads leave open), committed alone and pushed. Then: precheck, `git fetch origin`, worktrees of landed branches removed, memory and disk, `scripts/freeze.py status`, whether every branch of chain 163 is an ancestor of `origin/main`; then the first step chain 163's note lists as not finished.

## Sessions 1552 to 1557: chain 163's other unfinished steps

Long end 1:30 each. One step a session, in chain 163's order, as session 1536 lists them below. A step that was a landing is a landing here (the gate, the snapshots, the branches deleted once ancestors). When the list is shorter than six sessions, the free sessions take the faults below, in order.

### Unfinished steps (written by session 1536 of chain 163)

1. Session 1526 (the scenario block's two scrolling tables reachable by keyboard; landing of session 1531): **the landing of `wip/1526-a11y`** (`47ca0b302` on origin). Its gate passed at 13:36 UTC on 6 November: suite 7867 tests OK; `check_values` 7812 of 7812, with only the `/deals` and know-your-grid floors failing; routes, cross-checks and CSP passed by hand. It was held only by the 14:00 to 16:15 UTC window. Not between 14:00 and 16:15 UTC:
   - `git -C ../erw-1526 fetch origin`, then `git -C ../erw-1526 merge --no-edit origin/main`, then `git -C ../erw-1526 push origin wip/1526-a11y`.
   - If main brought code since `47ca0b302`, run the gate again: `.venv/Scripts/python.exe scripts/land_check.py --ref wip/1526-a11y --task 1526-a11y --port 3526 --lock-as s1551 --keep-worktree`. If the gate fails only on those two floors, run `node scripts/check-routes.mjs`, `check-cross-checks.mjs` and `check-csp.mjs` against the kept build. If main brought documents only, the earlier gate holds.
   - `node site/scripts/snapshot-live.mjs take s1551-before`.
   - Push `task/1526-a11y` only after `git merge-base --is-ancestor origin/main <sha>`, after trial-merging the other `task/` branches.
   - Wait by sha (`runs/s1523/wait_merge.sh` with the branch name changed), then `take s1551-after` and `compare s1551-before s1551-after`.
   - Delete `wip/1526-a11y` on origin, and remove `../erw-1526`.

## Sessions 1558 to 1562: the faults chain 163 left open

Long end 1:30 each. One fault a session, as session 1536 lists them below: the fault quoted with the page, the figure or the line it faults and what the fix writes instead; the fix with a test; its branch cut from the newest unlanded branch of this chain. **Sessions 1559 and 1562 end by landing the stack through the gate**, the snapshots, the branches deleted once ancestors.

### Open faults (written by session 1536 of chain 163)

- `site/components/board/` (the price board; the second window's chains 165, 175 and 177 own it today): `/board`'s scrolling region not reachable by keyboard (`#other > details > div > div`, session 1504's AccessLint). The fix is `lib/cells.ts`'s `scrollRegion` on that div. Take it only once the board's stack has landed (no `wip/16xx-board` or `task/1600-*-board` branch on origin); otherwise leave it and say so.
- `site/app/research/card/` and `site/public/findings/` (the siting cards, the desktop's): 6 picture downloads and 2 links ("Python", "Stata do-file") answer 404 (session 1504). Not this machine's; a line in the report only.
- `site/app/internal/open/page.tsx` line 31: the token field's `autocomplete="off"` (AccessLint, WCAG 3.3.8). For Samuel's ruling (chain 163's note, question 3); not changed until he rules.
- The battery page's decisions block (roadmap item 2): for Samuel's ruling (chain 163's note, question 2); a page change, not made until he rules.

Fewer than five are this chain's to fix, so the free sessions take the next item of `docs/roadmap.md` that needs no ruling and no design, saying which. Session 1529 of chain 163 found none left on 6 November (its report).

## Session 1563: the records and the clean-up

Long end 1:00. Worktrees and branches of this chain: every landed branch deleted on origin, every worktree of a landed branch removed; the tests green on main; the package's and the site's records rebuilt if this chain changed a table they read (`python package/tools/build_tables.py --check`).

## Session 1564: the note, the next file, the landing, the queue

Long end 1:00. A note in `docs/state/` (its name checked free first) in chain 149's note's form; the next file (written by session 1551) updated with what this chain did not finish and the faults left open, pushed alone; what is unlanded landed through the gate, not between 14:00 and 16:15 UTC, the snapshots; then `python scripts/chain_queue.py next`, and run the file it prints the same way.
