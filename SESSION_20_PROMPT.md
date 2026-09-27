Session 20 of the Energy Research Warehouse (ERW). Read CLAUDE.md, docs/platform-tools.md, package/llms.txt, warehouse/chat/eval/questions_s13.yaml and SESSION_19_REPORT.md first. Same non-negotiables; commit after each task; may push after merging origin/main; no model calls except Task 2; stop if API spend passes USD 3.

Human rulings on sessions 18 and 19: email_digest.py is the right name; subscribers get double opt-in and a tokened unsubscribe later, not now; SPP curtailment share, the ERCOT public API and the other ISOs' curtailment are deferred; the human is running the Supabase prune.

TASK 1. Site coherence. Update /about, /data and the home Explore grid so every page that exists is reachable and described in one line each (mix, curtailment, consumption, markets, weekly, deals, datacenters, map, grid, subscribe). Check the top nav fits on a phone width; group into at most six top-level items with the rest under them. Remove any leftover "no data" state that now has data. Take screenshots of every page, desktop and mobile.

TASK 2. Chat coverage of the new tables. Add 15 questions to the chat evaluation covering curtailment, energy mix, retail sales by sector, trader metrics, deals and datacenters, with answers computed independently with pandas. Run the full set (45 questions). Report accuracy beside sessions 12 to 14 and fix only outright bugs in tool routing, naming which.

TASK 3. A platform overview for reviewers. Write docs/OVERVIEW.md, one page: what the ERW is, the site, the counts from coverage (tables, rows, sources, licenses), the tools that are live with their pages, what refreshes when, the evaluation numbers to date (chat, digest, deals, datacenters), and the open gaps from STATUS.md. Every number from a file, none typed by hand. Link it from README.md.

TASK 4. SESSION_20_REPORT.md. Final commit and push.