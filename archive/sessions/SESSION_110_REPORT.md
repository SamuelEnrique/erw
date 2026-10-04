# Session 110 report: home and menu by audience

**Built and on the live site, in review at `/home/v2`.** Three ways in: investors and lenders, operators and developers, students and teachers. Each has its tools with the one question each answers, the live ones first and the ones in review greyed. One sentence says what the ERW is. A draft menu by audience is drawn inside the page and nowhere else. The live home page and the site's menu are untouched: the snapshot comparison shows only the 15-minute prices moving on the home page. One deploy.

## Read these first

1. **33 tools are listed, 5 open today and 28 in review.** That count is the page's own, read from the release list at the moment the page is built: when you open a tool, it moves above the line on this page without an edit here. No status is written on the page.
2. **Every way in opens on something a visitor can use,** but thinly: investors have the battery page and the seller tab; operators the network and storage; students only About. If this became the home page today, a student's column would be one live link and eight greyed ones. The game is the obvious first thing to open for them (session 111 checks it).
3. **The live home page already has an "Investors and lenders" section** and others by audience, lower down. This draft is that idea made the whole page, with the menu to match. It is a second design to compare, not a correction of the first.
4. **The one sentence:** "The Energy Research Warehouse is the live, citable record of the US energy system: prices, flows, projects, deals and policy, each number traced to the report it came from." It is the sentence the repository's own guide opens with, shortened.

## The page

`/home/v2`, in review. From the top: the draft menu (three audiences, each unfolding to its tools; "Draft menu, shown on this page only"); the name and the one sentence; one line of counts; three columns, one an audience, each with a line of what it is for, its live tools, then under "In review" its other tools greyed, each tool with its question; a closing line that says the page is a draft and the live home page and menu are unchanged.

| Way in | Open today | In review |
|---|---|---|
| Investors and lenders (11) | What a battery earns; What a generator earns | the seller tab's version 2, the price board (version 3), where power is cheap, the shoulder hours, storage build-out, who owns the batteries, power contracts, the datacenter tracker (version 2), deals |
| Operators and developers (13) | The network; Storage | the network's version 3, the project map (version 2), the interconnection queue, the energy mix (version 2), demand growth, curtailment (version 2), what a battery saves a customer, grid conditions, Ask ERCOT, known data faults, data and methods |
| Students and teachers (9) | About | the battery game, the tour, problem sets, your bill, events, emissions, Ask, the Energy Digest |

Where a tool has a newer version in review, the draft lists the newer one (and the seller tab both, since the older is the live one).

**What is not on it:** the older pages a newer version stands in for (the first price board, the first map, the first tracker, the first mix and curtailment pages), the markets, prices and peak-premium pages, consumption, the seven grid pages, companies, policy, the severance tools, the reports and the Roundup. They are in the site's menu as before. Whether they belong under an audience, or go, is the question this draft is for.

## Tests and checks

- `tests/test_session110.py`, 8 tests: three audiences, named as asked; **a tool's status is the release gate's and the live ones come first** in each list; every tool has a page and a question; **every live tool of the site is under some audience** (the home page, the terms and the methods notes aside); the sentence is one sentence; the counts are the lists'; the page is in review with the draft menu inside it; the live home page, the menu component, the layout and the page list do not import the draft and were not touched by this session.
- Every session's tests on this machine: 788 ran; one fails and is not this session's (the interchange ceiling).
- The workflow (run 37240871754) passed and merged (`9aa7921`); Vercel accepted the deployment.
- On production, internal view: the page renders (5 live tools, 28 in review) and is closed to a visitor.
- `before-110` (22:39 UTC) against `after-110` (22:47): 26 differences, all the home page's latest real-time prices. The other 24 pages: 0.

## Errors and decisions

1. **A tool is listed under one audience.** A lender also wants the queue and a developer the price board; one home was chosen for each, to keep the three columns short. The count says a tool under two audiences would be counted once, for when that changes.
2. **`check-review-pages.mjs` exited 127 once after printing a pass:** on Windows a forced exit while a request's handle closes trips an assertion in Node. The script now sets its exit code and lets Node end by itself.
3. **No model call, no pull, no table, no load. Model spend USD 0.00.**

## For Samuel

1. **Which tools to drop from the first screen** (the list under "What is not on it").
2. **The order within a way in:** today it is the order I wrote. Yours to set, in `site/lib/audience.ts`.
3. **To make it the home page:** move `site/app/home/v2/page.tsx` over `site/app/page.tsx` (the live page's price tiles and counts would go, unless they are carried over), and build the site's menu from `AUDIENCES`. A change to two live things: after the freeze, with its snapshots.

Energy Research Warehouse (ERW), session 110, on the old laptop (`samueloldlaptop`, data role), 2026-10-04 from about 22:33 to 22:50 UTC, unattended.
