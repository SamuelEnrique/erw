# Chain of 19 November 2026: sessions 8900 to 8999, samueloldlaptop (code role), unattended, 17 hours and more: the audit finished, the findings review page made fit to approve from, new problem sets on the whole country, the tour brought up to date

machine: code

Written by Claude in chat with Samuel on 19 November 2026 at about 13:40 PST and pasted by him into this session. It is not a machine's successor file, and no machine writes a successor to it. Folder: `C:\Users\lossa\Documents\erw`. Model: Opus 5.5, high effort. One Claude Code session.

## Why this chain

Chain 506 audited all 549 findings drafts this morning and wrote the sheet of forty (`docs/reviews/findings-shortlist-2026-11-19.md`), then went quiet in the middle of its last part. Samuel approves a finding at `/internal/findings` after running its Stata, and that page shows him none of what the audit learned: he would be approving from a list of 549 with the audit in a separate file. Making that page carry the audit is what turns this morning's work into approved findings. Beyond that, the site gained a map of every balancing authority, thirteen regions, a resource map and two new pages in one night, and neither the problem sets nor the tour know any of it. Three of Stanford's schools back the ERW, the School of Education among them, and the problem sets are what a teacher can use on Monday.

## Rules

- **The owner's rules of 16 November 2026 hold word for word** as written in `queue/done/302-day-16-november-oldlaptop-large-load-on-the-site.md` (its rules 1 to 11), and the rules of `queue/done/506-day-19-november-oldlaptop-findings-audit-shortlist.md`, with these changes:
- **Session numbers** 8900 to 8999, each checked free on origin/main and every branch first.
- **This machine is short of memory.** It does not rebuild an hourly table, does not build the site, and does not run a script that reads more than one year of an hourly table at once. A step that needs any of these is one row marked requested in `docs/state/data_requests_done_line.md` for the data machine, and the next step is taken at once. Before a long script, the free memory is read and written in the report.
- **This machine cannot build the site**, as in `queue/done/304-day-16-november-oldlaptop-done-line-economics.md`: a page change is held by tests and by the component drawn to HTML with the site's own code; every change that needs a browser is one row in `docs/state/browser_reads_wanted.md`; code for landing is one row marked requested in `docs/state/landing_request_oldlaptop.md`, which the data machine's desk lands.
- **A draft stays a draft.** Nothing is approved by a machine, nothing reaches `/research`, nothing is sent or posted. No caption, no LinkedIn or Instagram work, no motion.
- **Add, never change.** No figure a page shows today moves. Every page stays in review. No ruling is taken for Samuel.
- **Its pages are `/internal/findings`, `/learn/problems` and `/tour`.** `/grid`, `/demand`, `/industry` and `/ai-energy` are the data machine's today (chain 505) and are not edited here.
- **Never end idle.** After part D, part E, until the weekly limit.

## Restart safety and the progress file

- The first session writes `queue/next/570-resume-chain-507.md`, committed alone and pushed. Its text is the lines between BEGIN and END below, without those two words. A session that takes a resume file first writes the same text under the next number up (to 579), its machine line unchanged. The chain's last session removes it.
- `docs/state/progress_c507.md`: one line a step, its state and session, pushed after each.

BEGIN
# Resume of chain 507

machine: samueloldlaptop

Chain 507 was interrupted. This file is the old laptop's: another machine leaves it where it is. First put this same text back in queue/next/ as the next number up to 579, named NNN-resume-chain-507.md, committed alone and pushed. Then read queue/done/507-day-19-november-oldlaptop-findings-review-page-problem-sets.md whole and docs/state/progress_c507.md, and continue chain 507 from the first step not marked done, under that file's rules, with the next free session number in its range. Write no other queue file.
END

## Part A: the audit's last part, finished (part E of chain 506, from where `docs/state/progress_c506.md` and its note leave it)

- "Is it already known?" for every draft that passed the audit and has no answer yet, strongest first, each host's robots file and terms read before a page. The second route for any of the forty that lacks one.
- The sheet and the audit file brought up to date after every forty drafts. A finding on the sheet that turns out to be a publisher's own headline says so on its line.
- The drafts the audit could not check for want of memory (about 50 on the hourly EIA-930 tables) and the 47 on FERC 714: one data request row each group for the data machine, not tried again here.

## Part B: `/internal/findings` made fit to approve from

- **Each draft shows what the audit found:** its four checks (the sentence, the figure reproduced, the Stata file read, the chart), passed, fixed, not checked or withdrawn, with the reason; new, known or known in part, with who printed it; its second route where there is one; the tables it rests on and their license.
- **The sheet of forty opens first,** in the sheet's order, each with its sentence, its chart, the one thing that would make it wrong, and its `reproduce.do` one click away (to read and to download).
- **Finding the rest:** by family, by audit state, by the three readers the sheet names, by new or known, and a search of the sentences. The count in each state always visible.
- **Approving is unchanged:** the same control, the same rule (Samuel's own click after his Stata run). A withdrawn or not-checked draft cannot be approved, and says why.
- The audit reaches the page as one file a small script writes from `docs/reviews/findings-audit-2026-11-19/`, with a test that every draft of `docs/findings/` has a row.
- Internal page, behind the internal cookie as it is today. Hover tips only, plain nouns, no sideways scroll at 390 px.

## Part C: five new problem sets on the whole country (`/learn/problems`, in the form of the five sets it holds, each with its teacher page)

Each set: six to eight questions a student answers from an ERW page or its download, real figures from the page files on main, the worked answer on the teacher page, and a replication that recomputes every answer from the file. A figure is never typed by hand: the set reads it from the file, and a test pins it.

1. **Who trades with whom:** a region's imports by neighbor and month; where the two sides' reports disagree and what that means for a number you quote (`site/data/regions/trade/`, `trade_matrix.json`).
2. **A storm across the country:** the December 2022 storm in Tennessee and the Carolinas beside Texas in February 2021: demand, what ran, what moved between regions (`site/data/regions/events/`).
3. **Your own balancing authority:** what it owns, what is coming, how clean it is, whom it leans on (`site/data/regions/authority/`, on main since this morning).
4. **What is under the ground and in the wind:** reading the resource map's layers and their units; why a resource is not a power plant (`site/data/resources/`).
5. **Where energy goes:** energy by industry, by fuel and by state (`site/data/industry.json`).

For students of an introductory energy class, in plain words, with no advice and no view. A set whose file is not yet on main waits and the next is taken.

## Part D: the tour (`/tour`)

A stop for each thing the site gained since 17 November: the map of the balancing authorities and the regions in the Grid tool, the country views of `/events`, `/demand` and `/supply`, the resource map, energy by industry, energy per AI query as published. Each in the form of the stops the tour has. A stop for a page not yet landed is written and held back by a flag, with a test.

## Part E: after part D, until the weekly limit

- The reader's read of parts B to D (five real cases each: Samuel approving ten findings in a sitting; a teacher setting a problem set for Monday; a first-time visitor on the tour), on the pages drawn to HTML, every gap a numbered row, every fault fixed at its cause with a test.
- Then the done line for the five new sets, in the form of `queue/done/303-night-16-november-portable-trackers-done-line.md`.
- Then part A again for whatever drafts the data machine has since made checkable.

## The last session

- `docs/state/note_2026-11-19_oldlaptop_c507.md` in short bullets: the audit's final counts and how many of the forty are new; what `/internal/findings` now shows, with the rows that wait for a browser; the five sets with their addresses; the tour's new stops; what waits for Samuel with the default taken, in plain words.
- The resume file removed; `.venv\Scripts\python.exe scripts\chain_queue.py next`, and the file it prints run the same way. No file: part E goes on.
