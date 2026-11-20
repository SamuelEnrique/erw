# Chain of 19 November 2026: sessions 8200 to 8399, lab-desktop, second window, unattended, 24 hours and more: the findings hunt over everything the warehouse gained since 7 November, then two new pages (energy by industry, energy per AI query as published)

machine: lab-desktop-window2

Written by Claude in chat with Samuel on 19 November 2026 at about 02:25 PST and pasted by him into a SECOND Claude Code window on the desktop. It is not a machine's successor file, and no machine writes a successor to it. The `machine:` line names no role, on purpose: the chain worker and the first window never take this file or its resume file. Folder: `C:\Users\Shared\Documents\erw-w2` (a worktree of the desktop's repository). Model: Opus 5.5, high effort.

## Why this chain

The findings hunt of 6 to 9 November read the warehouse as it stood then. Since then it gained the large-load tables, the filed tariffs, and on 17 November 27 tables that hold all thirteen regions and every balancing authority hour by hour since July 2018. Nobody has read them for what they say. Findings are what Samuel posts from and what Automated Analysis shows, and he approves each one himself, so a deep stock of true, reproduced drafts is worth more to him than anything else this window can make without his review. This machine holds the data, which the laptops do not. The first window (chain 501) is writing page files for two pages Samuel asked for in October; this window builds those pages when the files land.

## Rules

- **The owner's rules of 16 November 2026 hold word for word** as written in `queue/done/301-day-16-november-desktop-open-faults.md` (its rules 1 to 10), with the changes below.
- **The second window's rules** are those of `queue/done/164-day-6-november-desktop-window2-findings-landings.md`: this window writes NO warehouse table and takes NO data lock; it never runs the daily run or a backfill; every site build goes through `scripts/buildlock.py`; it never kills a process it did not start.
- **This window works only in its own folder** and in worktrees it adds beside it. It never checks out, pulls, edits or builds in `C:\Users\Shared\Documents\erw`. Python is that folder's `.venv\Scripts\python.exe` by its full path; the warehouse's data files there are read, never written. Site packages are installed in this folder's own `site`.
- **This window does not land.** Code for landing is one row marked requested in `docs/state/landing_request_window2.md` (the form of `docs/state/landing_request_portable.md`), which the first window's desk lands. Records (drafts, reports, the progress file) are pushed to main directly.
- **Session numbers** 8200 to 8399, each checked free on origin/main and every branch first.
- **Its queue step is by name, never bare `next`.**
- **Nothing is published.** Every draft is marked draft and never approved; nothing reaches `/research`; nothing is sent or posted; no LinkedIn or Instagram work of any kind, no caption, no motion. Every new page stays in review.
- **The donor grids paper is Samuel's own work by hand.** No finding here runs a regression of imports on weather, estimates a share of a shock covered by imports, or builds a ledger of donors and takers. Descriptive findings on trade are in bounds: who sends to whom, how much, when, and how that changed.
- **Never end idle.** Part D follows part C until the weekly limit.

## Restart safety and the progress file

- The first session writes `queue/next/520-resume-chain-502.md`, committed alone and pushed. Its text is the lines between BEGIN and END below, without those two words. The chain's last session removes it. Nobody takes it by itself: Samuel restarts this window by name if it stops.
- `docs/state/progress_c502.md`: one line a family, a draft count or a page, its state and session, pushed after each.

BEGIN
# Resume of chain 502

machine: lab-desktop-window2

Chain 502 was interrupted. Read queue/done/502-day-19-november-desktop-window2-findings-industry.md whole and docs/state/progress_c502.md, and continue chain 502 from the first step not marked done, under that file's rules, in C:\Users\Shared\Documents\erw-w2, with the next free session number in its range. Leave this file in queue/next until the chain's last session. Write no other queue file.
END

## Part A: the findings hunt over what the warehouse gained since 7 November

- **A finding** has the form chain 164 gives it: one sentence that states a fact of the energy system with its figure, unit, geography, period and comparison basis; its chart in the brand's chart style, drawn by the repository's chart code; the tables and rows it rests on; its strength; its limits in one sentence; `reproduce.py` and `reproduce.do` that recompute the figure (Samuel's Stata rules: no line continuation, one empty line between commands outside loops and none inside, every variable destringed with `force`). No finding states a cause.
- **One change from chain 164:** no model is called. This session writes each sentence itself, and every figure in a sentence is computed by code from the tables and pinned by the reproduction.
- **Where drafts go:** where the hunt already writes them (`docs/findings/<family>/`), each marked draft, listed at `/internal/findings`. A finding from an internal or held table carries "license needed" on its figure and names the table.
- **First, the ground (long end 0:30):** the tables added or widened since 7 November, from `warehouse/metadata/coverage.csv` and the notes in `docs/state/`, grouped into families with their spans and licenses, and the families the hunt of 6 to 9 November already read, written to `docs/reviews/findings-hunt-plan-2026-11-19.md`.
- **Then the families, in this order, at least twelve drafts a family, the best by consequence kept, duplicates of an existing draft folded:**
  1. Who trades with whom: the thirteen regions and the balancing authorities since 2018 (`eia930_region_pair_hourly`, the `eia930_ba_interchange_hourly_*` tables): the standing exporters and importers, how each pair's flow changed by year, the hours and seasons a flow reverses, where the two sides' reports disagree and by how much.
  2. The six regions the site has never shown (the Southeast, Florida, the Carolinas, Tennessee, the Northwest, the Southwest): their peaks and when they fall, winter against summer, growth by year, what they burn and how that moved (`eia930_region_hourly`, `eia930_ba_supply_hourly`).
  3. Demand against temperature by region (`region_weather_hourly`): each region's coldest and hottest hours and what demand did in them, described, not modeled beyond the method the `/demand` page already uses.
  4. The nine events of `/events` across all thirteen regions: what the seven grids' pages could not show.
  5. Balancing authorities one by one: the largest movers in demand, the ones whose mix changed most.
  6. Large loads: the filed tariffs, the connection rules, the waits and the statements (`utility_large_load_tariffs`, `large_load_connection_rules`, `large_load_waits`, `large_load_public`).
  7. Every other family the ground step lists, largest tables first.

## Part B: the page "Energy use by industry" (when `site/data/industry.json` is on main; checked at the start of each session, never waited on)

- Samuel's idea of September: energy consumption by industry, kept current. One page, in review: the industries ranked, by fuel, by state, over time; choose two industries or two states side by side; every figure with its source on hover; downloads as the other pages have them.
- The page standard is rule 9 of `queue/done/302-day-16-november-oldlaptop-large-load-on-the-site.md`: hover tips only, facts and no view, plain nouns, held values drawn blank, no sideways scroll at 390 px, dense, informative, usable, charts that answer to the mouse.
- To the done line in the form of `queue/done/303-night-16-november-portable-trackers-done-line.md`: method note, replication, cross-check against a published figure, decisions block. Seen in a browser at 1280 and 390 px before landing is requested.
- It joins no menu: it is listed on `/in-review`. Where it sits in the menu is one plain line under "For Samuel's ruling".

## Part C: the page "Energy per AI query, as published" (when the table `ai_energy_published` is on main; the same checks)

- One page, in review, same standard: every published figure as its publisher printed it, with its printed words, date and what it measures, sortable by publisher and by what is measured. No figure of the ERW's own, nothing averaged or summed across publishers, no ranking of companies.

## Part D: when parts A to C are done

The hunt goes on over the families of the whole warehouse that carry the fewest drafts, largest tables first, in part A's form, until the weekly limit stops it.

## The last session

- `docs/state/note_2026-11-19_window2_c502.md` in short bullets: drafts by family with the three strongest of each in one line apiece, the two pages' state, what waits for Samuel with the default taken.
- The resume file removed. `C:\Users\Shared\Documents\erw\.venv\Scripts\python.exe scripts\chain_queue.py next --file <a file named for lab-desktop-window2, if one waits>`. No such file: say CHAIN DONE and stop.
