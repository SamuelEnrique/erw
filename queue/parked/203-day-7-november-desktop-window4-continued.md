# Chain of 7 November 2026: lab-desktop, fourth window, unattended: the Attention and Friction indices continued, then their second pass

machine: lab-desktop-window4

Written by session 3400 (chain 202, `queue/done/202-day-6-november-desktop-window4-attention.md`) on 6 November 2026 as that chain's next file, before its other work; chain 202's last session updates it with what that chain did not finish. Like chains 164, 166, 183, 192, 197 and 200, the `machine:` line names no role and no machine on purpose: the chain worker and the desktop's first window never take this file; it is started by name in the desktop's fourth Claude Code window with `python scripts/chain_queue.py next --file 203-day-7-november-desktop-window4-continued.md`, never bare `next`. Its sessions are the first free block of twelve at or above 3420 (3400 to 3419 are chain 202's), which its first session finds on origin's main and on every branch and says. Model: Fable 5.1, high effort. Model calls under the owner's key: USD 3 a session, USD 20 the chain, every call's cost in the report.

## Why this chain

Chain 202 built the Attention Index and the Friction Index from the warehouse's own corpus (`news_stories`, `policy_reads`, `policy_actions`, the datacenter and deal records' places): the classification tested against a 200-story hand-labeled set in `tests/fixtures/attention/`, the three tables (`attention_index_weekly`, `friction_index_weekly`, `attention_story_links`), the method note `docs/methods/attention.md`, the page `/attention`, the two probe estimates (GDELT, local permitting) and the research memo `docs/reviews/attention-paper-notes-2026-11-06.md`. This chain finishes what chain 202 left, then runs the indices' second pass: the stories the cap left unclassified, the weeks the first run reached only in part, the classification re-tested on a fresh labeled sample, and the page's figures checked against the tables again.

## Rules for every session

The rules of `queue/done/202-day-6-november-desktop-window4-attention.md` hold word for word: never kill a process you did not start; every build through `scripts/buildlock.py`; every warehouse write under the data lock (`warehouse/lock.py`), waited for; every python command `.venv\Scripts\python.exe`; precheck first; `git fetch origin` and merge `origin/main` before work; worktrees beside the main checkout on `wip/<N>-attention`; no em or en dash in any file; nothing sent or posted; `site/lib/release.ts` untouched; no new foreign source (the GDELT and local permitting probes are estimates for the owner's ruling, and no pull begins without that ruling in the session's prompt). Also:

- **The indices are computed by code from the classified rows, never by the model.** The model classifies a story (opposition or not, the kind, the place); `warehouse/derived/attention_index.py` counts.
- **A held outlet's story keeps its title off the public files and its link on**, as `news_index` does; the model's own headline may stand.
- **The locked write script** of chain 202 (`runs/c202/write_table.sh`, `DIR=derived`) is the one way the three tables are rewritten: the data lock waited for, the writer, the validator, `build_coverage.py --only`, the archive, the metadata patch to the branch; `fail=` read before any commit.
- **Landings** through `scripts/land_check.py` (`--port 3340`), every printed command run as its own command with its exit read, the snapshots before and after, never between 14:00 and 16:15 UTC.
- **Its first session writes the next file first** (`queue/next/<first free number at or above 204>-day-8-november-desktop-window4-continued.md`, `machine: lab-desktop-window4`, at least twelve sessions), commits it alone and pushes it to main; its last session updates it.

Read first: chain 202's note (`docs/state/note_2026-11-07_desktop_window4.md`), `docs/methods/attention.md`, `docs/reviews/attention-paper-notes-2026-11-06.md`, the two probe estimates it names, `CLAUDE.md`.

## The first session: the next file, the ground

Long end 0:45. The next file. Then chain 202's note read; its unfinished steps ordered into the sessions below; the three tables' row counts and their last week read from `warehouse/output/`; the model spend of chain 202 read from `api_cost_ledger` so this chain's cap starts from the truth.

## The second to fourth sessions: chain 202's unfinished steps

Long end 1:30 each, in chain 202's note's order. What chain 202 left (session 3400, 6 November 2026, about 19:25 UTC; chain 202's last session replaces this list):

- Everything: chain 202 had run only its first session when this file was written. Its note says what landed and what did not.

## The fifth and sixth sessions: the stories the cap left

Long end 1:30 each. The stories `attention_story_links` does not hold (the oldest weeks first this time, since chain 202 ran the newest first), classified under the same prompt and schema, under USD 3 a session; the three tables rewritten through the locked write script; the coverage by week in the report.

## The seventh session: the classification re-tested

Long end 1:30. A fresh sample of 100 stories, drawn from the weeks the second pass classified, hand-labeled from their text into `tests/fixtures/attention/` beside chain 202's 200; the accuracy by class against the first set's; a class whose accuracy fell is named for the owner, with the prompt change that would fix it proposed, not made.

## The eighth session: the page's figures against the tables

Long end 1:00. `/attention` built locally through the build lock; every figure the page shows read back from the three tables by a script; check-values on the page; a difference fixed in the page, never in the table.

## The ninth session: the tracers and the cross-check again

Long end 1:00. The tracers (a week's index value to its stories, three weeks, three sectors) run again; the week's story count against the Digest's issue counts for the weeks the second pass added.

## The tenth session: the research memo's three findings re-run

Long end 1:30. The three candidate findings of `docs/reviews/attention-paper-notes-2026-11-06.md` computed again on the fuller tables; a finding that no longer holds is marked so in the memo, with its new figure; nothing approved.

## The eleventh session: the landing

Long end 1:30. `scripts/land_check.py --ref wip/<N>-attention --task attention --port 3340`, the snapshots, never between 14:00 and 16:15 UTC.

## The twelfth session: the note, the next file, the queue

Long end 1:00. `docs/state/note_2026-11-08_desktop_window4.md` in chain 202's note's form (what landed with commits, the classification's accuracy and cost, the indices' coverage by week, Decisions made without you, For Samuel's ruling, the cost); the next file updated and pushed alone; the queue step by name, `python scripts/chain_queue.py next --file <its name>`, never bare `next`.
