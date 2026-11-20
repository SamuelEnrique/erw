# Chain of 19 November 2026, evening: sessions 8905 to 8999, samueloldlaptop (code role), one session, unattended: Samuel's one hour tonight made ready, then every ruling's two choices brought up to date so that his ruling lands in one step

machine: samueloldlaptop

Written by Claude in chat with Samuel on 19 November 2026 at about 18:00 PST and uploaded by him to `queue/next`. It is not a machine's successor file, and no machine writes a successor to it. Folder: `C:\Users\lossa\Documents\erw`. Model: Opus 5.5. Run it unattended, to its last session. Do not stop to ask questions. Model spend USD 0: call no model API. No heredocs or long inline scripts: use the Edit and Write tools, and put scripts in `runs/`.

## Why this chain

Samuel has one hour tonight, the first he has had all week, and three piles wait for it: 129 rulings that move a figure (now 54 switch, 48 keep, 27 his call alone), 40 findings that need his Stata run before he can approve one, and a day's worth of new pages he has not seen. An hour spent finding his place in those piles is an hour lost. Part A makes the hour: one page that tells him what to do minute by minute, and one Stata file that runs the findings for him. Part B is for the minute after he rules: the other choice of each ruling was built on 17 November as a branch (`wip/alt-*`, 113 of them), and main has moved a long way since. Brought up to date now, a ruling tonight lands in one step. Left as they are, each would be a morning's work of conflicts.

## Rules

- **The rules of chain 507 hold word for word** (`queue/done/507-day-19-november-oldlaptop-findings-review-page-problem-sets.md`, and through it the owner's rules of 16 November as `queue/done/302-day-16-november-oldlaptop-large-load-on-the-site.md` has them), with these changes:
- **Session numbers** 8905 to 8999, each checked free on origin/main and every branch first.
- **This machine is short of memory.** It does not build the site, does not rebuild an hourly table, and starts no timer or sleep that waits: a thing not ready is skipped and returned to, never waited on. Before a long test run the free memory is read and written in the report; a test file that needs more than is free is run alone, or its name goes to the data machine as one data request row.
- **No ruling is taken for Samuel.** No default on main changes. No `wip/alt-*` or `wip/switch-*` branch is landed, merged to main or requested for landing. A recommendation is not a ruling, however strong its evidence.
- **The rule against a session whose only output is a record does not apply to part A:** the page and the Stata file are its product.
- **A draft stays a draft.** Nothing is approved, sent or posted. No caption, no LinkedIn or Instagram work.
- **Plain words, full addresses** (`https://github.com/SamuelEnrique/erw/blob/main/...` for a file, `https://erw-flame.vercel.app/...` for a page), no codes without their meaning, no em dashes.
- **Never end idle.** After part C, part D, until the weekly limit.

## Restart safety and the progress file

- The first session writes `queue/next/591-resume-chain-590.md`, committed alone and pushed. Its text is the lines between BEGIN and END below, without those two words. A session that takes a resume file first writes the same text under the next number up (to 599), its machine line unchanged. The chain's last session removes it.
- `docs/state/progress_c590.md`: one line a step, a tool or a branch, its state and session, pushed after each.

BEGIN
# Resume of chain 590

machine: samueloldlaptop

Chain 590 was interrupted. This file is the old laptop's: another machine leaves it where it is. First put this same text back in queue/next/ as the next number up to 599, named NNN-resume-chain-590.md, committed alone and pushed. Then read queue/done/590-evening-19-november-oldlaptop-tonight-pack-switches-ready.md whole and docs/state/progress_c590.md, and continue chain 590 from the first step not marked done, under that file's rules, with the next free session number in its range. Write no other queue file.
END

## Part A: Samuel's hour (done and pushed within this chain's first ninety minutes, before anything else)

1. **One page, `docs/reviews/tonight-2026-11-19.md` on main:** sixty minutes in three parts, each with what to open, what to do and what to write, in short bullets.
   - **Minutes 0 to 25, the rulings.** From `docs/reviews/rulings-one-sitting-2026-11-19.md`: the switches whose evidence is a publisher's own practice or his own earlier ruling, listed so that one line from him ("switch all of group 1") rules them together; the keeps the same way; then the questions that are his alone, at most twelve tonight, the ones that move the largest figures first, each with the two figures, the two screenshots' addresses and what he would weigh, in three lines. Then the defaults list, closed by one "defaults stand". At the end of the part, the exact words he can paste to Claude in chat to rule, as a template with blanks.
   - **Minutes 25 to 45, the findings.** How to run the Stata file of step 2 and what it prints; then the ten findings of the sheet of forty to look at first, each in two lines, and how to approve one at `/internal/findings`.
   - **Minutes 45 to 60, what was built today.** For each new page and view on production, in review (the map of the balancing authorities with its Price color and the panel of an authority's own facts; the thirteen regions in the Grid tool; the country views of the events, demand and supply pages; Forecast against actual; the resource map; energy by industry; energy per AI query; the findings review page; the five new tour stops; whatever the data machine has landed since): its full address, what to click, step by step, and what he should see. Only pages that are on production when the page is written: each address is checked against main first.
2. **One Stata file, `docs/findings/_top40/run_top40.do`, with its README:** it runs the forty findings' `reproduce.do` files one after another from a folder Samuel sets in one line at the top, catches a file that fails without stopping the rest, and ends by printing one table: the finding's short name, the figure the sheet gives, the figure Stata got, and whether they match within the draft's stated tolerance. Samuel's Stata rules throughout: no line continuation, one empty line between commands outside loops and none inside, every variable destringed with `force`. There is no Stata on this machine: the file is read line by line against each `reproduce.do` it calls, and the README says "read, not run" and what Samuel should do if a line fails. A second file, `run_top10.do`, for the ten of the page above.
3. The page's first line says when it was written and that Samuel can ask Claude in chat for anything on it.

## Part B: both choices of every ruling brought up to date with main

1. **The ground:** every `wip/alt-*` branch on origin listed with its tool, its entry in `docs/reviews/rulings-ranked-2026-11-17.md`, the recommendation that entry now carries (switch, keep, Samuel's call) and how far behind main it is. Written to `docs/reviews/switch-ready-2026-11-19.md`, one row a branch, which this part fills in.
2. **Order:** the recommended switches first, largest change first; then the questions that are Samuel's alone; the recommended keeps last (their other choice is the least likely to be asked for).
3. **Each branch:** `origin/main` merged into it in its own worktree; conflicts resolved by keeping main's new work and the branch's one change, and nothing else; the test that pins the figure under the other choice run and passing, with the figure it pins written in the row beside the figure of 17 November (a figure that moved because the data moved is said to be that, with both values); the tool's own tests run. Pushed to the same branch name. A branch that cannot be brought up to date without a decision is left, its row saying exactly what the decision is.
4. **One branch a tool for the recommended switches:** `wip/switch-<tool>`, cut from origin/main, holding that tool's recommended switches together, each as its own commit named by its entry, with the tool's tests passing. The row of each says which commit. Not requested for landing. Where two switches of one tool cannot both hold, both are kept apart and the row says why.
5. **For the data machine:** a branch whose other choice needs a builder run or a table rebuilt before its page is right has one line in its row saying which, so that the landing after a ruling carries the data step. No data request is filed for it now.
6. Push the rows after every five branches.

## Part C: what chain 507 left open

- "Is it already known?" for the 29 drafts that wait, in batches, no timer between them.
- The fifth problem set, "Your own balancing authority", now that `site/data/regions/authority/` is on main; the cross-checks of the four sets against the publishers' own figures.

## Part D: after part C, until the weekly limit

- The page of part A step 1 brought up to date whenever the data machine lands a new page (its part 45 to 60), until 23:00 PST; after that it is left as it is, with the time on its first line.
- Part B again for any branch main has since moved past.
- A reader's read of `docs/reviews/tonight-2026-11-19.md` as Samuel with sixty minutes and no patience: every line he would have to read twice is rewritten shorter.

## The last session

- `docs/state/note_2026-11-19_oldlaptop_c590.md` in short bullets: where the hour's page and the Stata files are; how many branches are up to date, how many switch branches are ready and for which tools, which wait on a decision and what it is; what waits for Samuel, in plain words.
- The resume file removed; `.venv\Scripts\python.exe scripts\chain_queue.py next`, and the file it prints run the same way. No file: part D goes on.
