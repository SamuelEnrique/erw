# Session 209 report: the roadmap in the planner's format, and session 201's patches

13 October 2026, from 00:08 UTC, unattended, on the old laptop (`samueloldlaptop`, a code machine). Branch `task/209-roadmap` from `origin/main` (session 208's work stays on `wip/203-brand-battery`, not landed). Model spend USD 0. Pulls: none. No warehouse table written. No em dash in anything written.

## Read these first

- **`docs/roadmap.md` is version 2.1.** The Status lines read in the planner's format (`scripts/planner.py check` now names no Status problem: only "planner: off", which is Samuel's to turn on). Every one of the ten items has `machine:`, `where:` and `done:` lines, drafted for Samuel's review on Wednesday, under his own bullets, which are unchanged. A Backlog section holds the battery stress slider. Three dated rulings of the chain prompt of 12 October are added. Nothing of Samuel's words was removed.
- **Two of the owner's lines could not be written as he said them and still be read by the planner.** "budget: no limit; stop at the weekly Claude limit" is written as `budget: 99 sessions a day per machine: no limit; ...` (the planner reads a number). "deploy cutoffs: 14:00 to 16:15 UTC daily; Sundays 22:30 to 23:45 UTC" is written as two spans the planner holds every day, with a `cutoff note` line saying the second is Sunday's. Decisions 1 and 2.
- **Both patches of session 201 are applied**, with the venv form: the `CLAUDE.md` bullet on the design and browser tools (extended by one sentence: `docs/brand.md` is the one design document, no `PRODUCT.md` or `DESIGN.md`), and twelve allow rules in `.claude/settings.json` (`python` and `.venv\Scripts\python.exe` forms of `precheck.py`, `chain_queue.py` and `duty.py`, for Bash and PowerShell).
- **The landing**: see "The landing" (the before snapshot, the push, the after snapshot and its comparison: expected 0 differences on the 25 pages, since no site file changes).

## What to review

- https://github.com/SamuelEnrique/erw/blob/main/docs/roadmap.md (Status; the three lines under each item; Backlog; the last three rulings; the review log)
- https://github.com/SamuelEnrique/erw/blob/main/CLAUDE.md ("Key conventions", the last bullet)
- https://github.com/SamuelEnrique/erw/blob/main/.claude/settings.json (the six allow rules in each list)

## What was done

1. **The roadmap.** Status: `budget`, `deploy cutoffs` and a `cutoff note`; the rest as it was. Items: the three lines each. Backlog: "Battery: stress slider (what if Uri happened again) as a scenario toggle." Rulings: the battery page's three questions, `docs/brand.md` as the one design document, the deploy cutoffs and the budget, each dated 12 October 2026 and marked as the chain prompt's words. Review log: a dated entry marked "not a review".
2. **The patches.** `git apply --ignore-whitespace runs/session201/claude_md.patch` (exit 0), then the venv rules and the one sentence by hand. `settings.json` parses (101 allow rules).
3. **Checks.** `scripts/planner.py check` on the new file; the seven test modules that read the three files; the whole suite in a clean copy before the push.

## Checks, with exit codes

| Command | Exit | Result |
|---|---|---|
| `scripts/precheck.py` (session 208's, 23:25 UTC; the same duty holds) | 0 | on duty until 13 October 15:25 UTC |
| `git apply --check` and `git apply --ignore-whitespace runs/session201/claude_md.patch` | 0, 0 | applied |
| `python -c "json.load(settings.json)"` | 0 | 101 allow rules |
| `scripts/planner.py check` | 0 | "planner: off" is the only refusal; the Status problems of before ("does not state the budget", "a deploy cutoff cannot be read", "no open item for samueloldlaptop") are gone |
| `python -m unittest` on the seven modules that read the roadmap, `CLAUDE.md` or the settings (`runs/session208/tests209.out`) | see "The landing" | |
| Whole suite, clean copy of the branch's commit | see "The landing" | |
| `scripts/freeze.py status` before the push | 0 | no freeze |

## The landing

- Freeze status: exit 0, no freeze; 00:xx UTC, outside both cutoffs (14:00 to 16:15; 22:30 to 23:45).
- Before snapshot: `node site/scripts/snapshot-live.mjs take s209-before`, its own command; then `git push origin task/209-roadmap`.
- Expected: 0 differences on the 25 pages (no site file in the change).
- The result (the after snapshot, the comparison, every line marked) is added by the branch `task/209-report`, as session 203 did, and in the chain's closing message.

## Decisions made without you

1. **`budget: 99 sessions a day per machine`** stands for "no limit": the planner refuses a Status without a number ("budget: N sessions a day per machine"), and the owner's words follow on the same line. Reversible: one line.
2. **The Sunday cutoff is held every day** (`deploy cutoffs: 14:00 to 16:15 UTC; 22:30 to 23:45 UTC`): the planner reads no weekday. A `cutoff note` line says which is which. The cost is 75 minutes of landing time a day, six days a week.
3. **The `machine:`, `where:` and `done:` lines are drafts**, said so in the section's lead and in the review log. Items 5, 6 and 9 are `data`, the rest `code`; item 10's `done:` names Monday 13 and Wednesday 15 October.
4. **The chain prompt's rulings were entered as dated lines**, as session 201 entered the review's; each says it is the chain prompt's.
5. **The venv rules carry both spellings for Bash** (`.venv/Scripts/python.exe` and `.venv\Scripts\python.exe`), since this machine's chains write the backslash form in a Git Bash.

## For Samuel's ruling

1. The ten items' `machine:`, `where:` and `done:` lines: keep, change or strike, on Wednesday.
2. Whether the planner should read a weekday in a deploy cutoff ("Sundays 22:30 to 23:45 UTC"), so that the Sunday span stops holding every day. One regex in `scripts/planner.py` and its test.
3. Whether "budget: no limit" should be a form the planner accepts as written, instead of 99.
4. `CLAUDE.md` still says three pages are live (`/cost-of-power/battery`, `/network`, `/storage`); none is since session 166 (session 201's ruling 5). Not changed here: the prompt named the two patches.

## The prompt

Chain of 12 October, session 209: "roadmap format and the 201 rulings. Long end 2:00. Model spend cap USD 0. Pulls: none. 1. docs/roadmap.md in the planner's format: 'budget: no limit; stop at the weekly Claude limit'; 'deploy cutoffs: 14:00 to 16:15 UTC daily; Sundays 22:30 to 23:45 UTC'; draft the items' machine:, where:, done: lines. 2. Apply both CLAUDE.md patches from session 201 plus the venv form. docs/brand.md is the one design document; no PRODUCT.md or DESIGN.md. 3. Backlog in docs/roadmap.md: 'Battery: stress slider (what if Uri happened again) as a scenario toggle.' Last step: python scripts/chain_queue.py next; exit 0 run the printed file; exit 3 say CHAIN DONE and stop."
