# Chain of 7 November 2026: lab-desktop, third window, unattended: the company database's unfinished steps, then the company pages' faults

machine: lab-desktop-window3

Written by session 3300 (chain 200) on 6 November 2026 as that chain's next file, before its other work; chain 200's last session updates it with what that chain did not finish. The `machine:` line names no role and no machine on purpose: the chain worker and the desktop's first and second windows never take this file; it is started by name in the desktop's third Claude Code window, with `.venv\Scripts\python.exe scripts/chain_queue.py next --file <this file's name>`, never bare `next`.

## Why this chain

Chain 200 began tool 10 of the master plan, the energy company database (`companies`, `company_aliases`, `company_links`, the `/companies` index and the company page), and tool 11's first view, `/capital`, with a probe of SEC EDGAR's Form D index files for the owner's approval. This chain finishes what chain 200 did not, then finds and fixes the company pages' faults: a wrong merge or a missed one, a figure that does not trace to its row, a page slow on a large company, a chart or a hover that fails at 390 pixels.

## Rules for every session

The rules of `queue/done/200-day-6-november-desktop-window3-companies.md` hold word for word. Also:

- **Its first session writes the next file first** (`queue/next/<first free number at or above 202>-day-8-november-desktop-window3-continued.md`, `machine: lab-desktop-window3`, at least twelve sessions), commits it alone and pushes it to main with the snapshots; its last session updates it and takes it by name.
- **Sessions** numbered from the first free number at or above chain 200's last session plus one, on origin main and every branch (said in the first report).
- **Branches:** `wip/<N>-companies` cut from the newest unlanded branch of chain 200 or of this chain, else `origin/main`; `origin/main` merged before work.
- **Model calls** under the owner's key: USD 2 a session, USD 15 the chain, every call's cost in the report.
- **Nothing pulled from SEC EDGAR** unless the owner's approval of chain 200's Form D estimate is written in a ruling or in this chain's prompt.

Read first: chain 200's note (`docs/state/note_2026-11-07_desktop_window3.md`), `docs/methods/companies.md`, `CLAUDE.md`.

## The first session: the next file, the ground

Long end 0:45. The next file. Then chain 200's note read; its unfinished steps ordered into the sessions below; the owner's rulings on chain 200's questions listed with what each asks this window to do.

## The second to sixth sessions: chain 200's unfinished steps

Long end 1:30 each, in its note's order. A landing never between 14:00 and 16:15 UTC, through `scripts/land_check.py --port 3330`, every printed command run as its own command with its exit read, the snapshots before and after.

What chain 200 left (session 3300, 6 November 2026, about 19:10 UTC; its last session replaces this list):

- Everything: chain 200 had just begun.

## The seventh and eighth sessions: the resolution's faults

Long end 1:30 each. The hundred largest companies by footprint read by hand against their links: a merge of two companies that are not one, a company split in two, a parent named as a subsidiary; each fault fixed in the rules or in the reviewed-aliases file with its evidence, a test for each, the three tables written again under the data lock, the match rates by source before and after.

## The ninth and tenth sessions: the pages' faults

Long end 1:30 each. Every figure on twenty company pages (the ten largest, ten drawn at random with a stated seed) traced to its table and row; the pages at 390 and 1280 pixels with the internal cookie, screenshots, AccessLint, check-values on the local build; the slowest company page's read timed and brought under one second; each fault fixed with a test.

## The eleventh session: the landing

Long end 1:30. As chain 200's landings.

## The twelfth session: the note, the next file, the queue

Long end 1:00. `docs/state/note_2026-11-08_desktop_window3.md` in chain 200's note's form (what landed with commits, the three tables' rows and the match rates by source, the faults found and fixed, Decisions made without you, For Samuel's ruling, the cost); the next file updated and pushed alone; the queue step by name.
