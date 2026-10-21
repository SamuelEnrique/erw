# Chain of 20 October 2026, afternoon and evening: sessions 401 to 415, code machine (samueloldlaptop), unattended

machine: code

Fifteen sessions for the rest of 20 October on the code machine, taken after 014. Samuel's standing instruction: the machines run 24 hours a day; a chain that ends with nothing waiting writes the next file before it idles. Session numbers 401 to 415 are reserved for this file so that the data machine's self-written chains (384 onward) do not collide with it; a session that finds a number taken uses the next free one above 415 and says so. Every change is default-neutral and needs no ruling: no page's default figure moves (check-values proves it); new pages open in review, not public; nothing is posted or sent anywhere. Rulings in force: docs/roadmap.md "Rulings" and the chains of 20 October (queue/done/010, 012, 014). Read docs/state/review_2026-10-20_day_code.md and sessions 365 to 383's reports first; do not redo their work.

## Rules for every session

Every python command uses .venv\Scripts\python.exe. Precheck first (exit 1: stop). Unattended: do not stop to ask; reversible choices under "Decisions made without you"; irreversible ones under "For Samuel's ruling", undone. A failed session stays on a pushed wip/ branch and the next starts. A job stopped for low memory is started again once with CLAUDE_CODE_DISABLE_BG_SHELL_PRESSURE_REAP=1 in the environment (the chain worker sets it); if it stops twice, the session goes to wip/ with its "To finish" commands and the next session starts. Landing on main when green: freeze status, snapshot before and after, check-values, pull and merge origin/main first (the data machine lands today too); trial-merge remote task/ branches. NO LANDING 14:00 to 16:15 UTC; the 22:30 to 23:45 UTC cutoff is Sundays only. No warehouse data written; pulls only where a session's part names them; model spend USD 0 (the session's own work is not model spend). One heavy process at a time (runs/build.lock); python scripts/duty.py beat before each build. tokens.css and the shared components only; Impeccable once per page touched; screenshots at 1280 and 390. No em dashes. Reports as the chain of 20 October's, with "For Samuel's ruling" one item a line so /internal/waits lists it. Last step of the last session: the evening note, then the queue step; if nothing waits for this machine, write the next file first (rule in session 415).

## Session 401: the five tool pages through the installed tools

Long end 1:30. Roadmap item 4 says each of Impeccable, UI/UX Pro Max, frontend-design, the Vercel guidelines and AccessLint is used in at least one session's checks. Run every one of them on the five tool pages (/cost-of-power/battery, /cost-of-power/seller, /cost-of-power, /analysis, the Grid page), record each finding in docs/reviews/tooling-pass-2026-10-20.md with the tool that found it, fix what needs no ruling within docs/brand.md (spacing, contrast, focus order, a label), list the rest. docs/tooling.md gets the date of each tool's first use. Every value unchanged. Land.

## Session 402: the Digest audited, every number traced

Long end 1:30. The Energy Digest page (the route the menu names) and its numbers section: every figure on today's page traced to a warehouse table with its key, added to check-values where it is not; a day without a brief says so in one line and shows no stale brief; the archive of past days reachable and each day's page checked the same way; the method note current. A fault found is fixed with its test; a fault that needs a ruling is listed. Land.

## Session 403: the ERCOT peak premium explorer

Long end 2:00. Master plan tool 5, the first signature explorer: /explore/ercot-peak-premium, in review (not in the menu), from ercot_peak_premium_annual and ercot_peak_premium_monthly as they stand (stale since 29 September is stated on the page with the newest date held): the thesis chart made live, filterable by year, month and hub, with the figure's definition in one line, the shared charts only, the downloads line, a method note (docs/methods/ercot_peak_premium.md if absent), check-values keys with a floor, shots at 1280 and 390. Land.

## Session 404: the demand growth explorer

Long end 2:00. The second explorer: /explore/demand-growth, in review, from eia930_demand_growth (its newest date stated): growth by grid and by window, the thesis chart live, the same standard as 403 (definition, downloads, method note, keys, shots). Land.

## Session 405: the interconnection explorer

Long end 2:00. The third explorer: /explore/interconnection, in review, from iso_queue_statistics (the method note names the ERCOT queue-date fault until the data machine rebuilds the table; the page states it in one line and shows the counts it has, never a corrected guess): the six queues by entry year and status, the same standard as 403. Land.

## Session 406: the first newsletter issue, from the warehouse

Long end 2:00. Master plan tool 9, the draft only, nothing sent: docs/reviews/newsletter/issue-001.md, about 1,200 words, in the project's voice (data first, then the reading; no hype; no em dashes), on one question the warehouse answers better than anything public today, chosen by the session from what the pages already show with checked figures (the price years, the node basis, the 4CP saving, the battery's income by stream are candidates). Every figure in it carries its check-values key in a footnote and the page address; three charts rendered to PNG from the shared components into docs/reviews/newsletter/issue-001/. A second file, issue-001-notes.md, lists every claim with its source and what a sceptical reader would push back on. Push with the next landing.

## Session 407: ten LinkedIn posts, drafted, not posted

Long end 1:30. docs/reviews/linkedin/posts-001-010.md: ten posts, each one checked number from the warehouse with its chart (PNG at 1200 by 627 from the shared components, into docs/reviews/linkedin/), under 150 words, the figure first, the reading second, the page address and the source last, no hashtags beyond three, no em dashes, nothing posted anywhere. Each post names its check-values key. A one-page posts-notes.md says which three to post first and why, for Samuel's ruling. Push with the next landing.

## Session 408: every page's floor, every number's key

Long end 1:30. site/scripts/check-values.mjs: the list of pages it reads against the site's routes (every page under site/app that shows a warehouse figure); a page not in it, or a page with no floor, listed and added with CHECK_VALUES_WRITE_FLOOR=1 once it passes in full; a test that fails when a route that shows a figure is missing from the check. Every value unchanged. Land.

## Session 409: the method notes against the pages

Long end 2:00. For every page with a method note under docs/methods/: a script (site/scripts/check-methods.mjs) that lists each figure the page shows (its check-values keys) and whether the note names it; the missing lines written into the notes from the page's own code, in the notes' voice, no new claims; the script in the landing checks. Land.

## Session 410: the /data catalogue and coverage agree

Long end 1:30. /data against warehouse/metadata/coverage.csv and sources.csv: every public table listed with its license, refresh, row count, newest timestamp, download and Redivis address where released; a table in one and not the other listed in the report and fixed where the fix needs no ruling (a missing line, a stale count); a test that fails when they disagree. Land.

## Session 411: performance on the 25 visitor pages

Long end 2:00. Lighthouse (the installed chrome-devtools-mcp or the CLI) on every visitor page at 1280 and 390 on the local production build: the four scores recorded in docs/reviews/performance-2026-10-20.md; what needs no ruling fixed (font preload, image sizes, a chart that renders twice, an unused import), scores before and after; what needs a ruling listed. Every value unchanged. Land.

## Session 412: accessibility on every page

Long end 1:30. AccessLint and the browser's accessibility tree on every visitor page: every finding in docs/reviews/accessibility-2026-10-20.md; labels, roles, contrast within docs/brand.md's tokens, keyboard order and focus fixed; the shared components first so a fix lands everywhere; findings that need a ruling listed. Land.

## Session 413: the competitors, read against coverage

Long end 2:00. docs/reviews/competitors/2026-10-20.md: Ask the Grid (askthegrid.com: its public catalog, MCP and about pages, no account), Grid Status, Yes Energy and Enverus from their public pages only, each against coverage.csv table by table: what they show that the ERW holds, what they show that it does not (with the public source that could fill it and its license as far as the source's own terms say), and what the ERW holds that they do not (fuels, deals, policy, the economics models, the citable record). Pulls: their public pages, ceiling 40 requests in all, robots and terms read first, nothing from a page that forbids it. No recommendation to cut anything: the facts in tables, and one paragraph on where each overlaps. Push with the next landing.

## Session 414: /internal/waits made ready for the review

Long end 1:30. /internal/waits and /internal/open: every "For Samuel's ruling" line from sessions 351 to 413 listed once (duplicates merged, each with its session links), grouped by what it blocks (a public page, a data pull, a ruling on a figure, money), with a count at the top and the three highest-value items first as the notes rank them; a test. Land.

## Session 415: the evening note, the next file, and the queue

Long end 1:00. docs/state/review_2026-10-20_evening_code.md: one line a session with its address, every screenshot folder, every decision made without Samuel, every item waiting for him, the state of queue/next for this machine. Then python scripts/chain_queue.py list: if nothing waits for this machine, write the next file before the queue step, at least ten sessions, default-neutral, machine: code, numbered from the next free session above this chain, from docs/roadmap.md "This week" and the open items of the notes of 20 October (the explorers' next charts, the replications 381 left unbuilt, the method notes, the Digest's archive, the security items that need no ruling), commit and push it to main; say so in the note. Push, then python scripts/chain_queue.py next.
