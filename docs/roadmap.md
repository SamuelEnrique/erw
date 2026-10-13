# Roadmap

Energy Research Warehouse (ERW). What the machines do next, in the owner's words. `scripts/planner.py` reads this file, and no other, to decide what to plan (`docs/machines.md`, "The planner"); it never edits it. Only a person writes here. Until a person writes `planner: on` under "Status", the planner is off and nothing is planned.

Version 2, 12 October 2026: Samuel's words from the review of Sunday 12 October, entered by session 201 from the chain prompt of that night. Version 2.1, 13 October 2026: session 209 put the Status lines in the planner's format (the owner's words of the chain prompt of 12 October, kept beside each), drafted the `machine:`, `where:` and `done:` lines of every item for Samuel's review (v3 Wednesday), added the Backlog and the battery rulings of that prompt.

## Status

What goes here, one line each: `planner: on` or `planner: off` (absent means off); `budget: N sessions a day per machine`; `earliest start: HH:MM UTC` and `latest start: HH:MM UTC`, the hours between which a session may start; `deploy cutoffs: HH:MM to HH:MM UTC` (several are separated by semicolons; `none` when there is none).

- planner: off (Samuel turns it on after reading session 197's report)
- budget: 99 sessions a day per machine: no limit; stop at the weekly Claude limit and resume at its reset (the planner reads a number, so the owner's "no limit" is written as one no machine reaches)
- earliest start: 00:00 UTC
- latest start: 23:59 UTC
- deploy cutoffs: 14:00 to 16:15 UTC; 22:30 to 23:45 UTC
- cutoff note: the first span is the daily run's (14:00 to 16:15 UTC daily); the second is the Sunday Roundup's (Sundays 22:30 to 23:45 UTC). The planner reads no weekday, so it holds the second span every day; a person's chain may name Sundays alone
- reviews: Sunday, Wednesday and Friday evenings
- public day: Monday 20 October 2026, gated by licenses and seven green days of every scheduled job

## This week

What goes here: numbered items, `N. [ ] title` while open and `N. [x] title` once closed, each followed by indented lines: `machine: code` or `data`; `where:` the page or table; `done:` what done means; `rulings:` a ruling already made, one a line; and, where wanted, `session:` one session's work (up to three), `cap: USD n` for model spend, `lands: yes` or `no`.

In priority order. The `machine:`, `where:` and `done:` lines are session 209's draft (13 October 2026) of the owner's bullets above them, for Samuel's review on Wednesday; the bullets are his words.

1. [ ] The loop runs itself
   - main green, planner on, queue never empty
   - machine: code
   - where: scripts/planner.py, scripts/chain_queue.py, queue/next/, .github/workflows/
   - done: main green on every scheduled job for seven days; planner: on in this file; queue/next/ never empty for a week, each planned chain run to its last step
2. [ ] Five tools sellable
   - battery, generator, datacenter: finishing (signed method docs, replications, cross-checks, decisions blocks)
   - Automated Analysis to its final form
   - Grid: network, energy mix and Ask merged into one tool
   - machine: code
   - where: /cost-of-power/battery, /cost-of-power/seller, /cost-of-power, /analysis, /network with /mix and /ask
   - done: each of the five has a method note signed by Samuel, a replication a reader can run, a cross-check table against published figures, and a decisions block; Automated Analysis in its final form; the Grid tool one page
   - rulings: the battery page asks three questions; its defaults are the rulings of 12 October (below)
3. [ ] Brand, full
   - `docs/brand.md`, direction A: Source Serif 4 display, IBM Plex Sans text, Plex Mono numbers
   - the E-in-cardinal-square mark upgraded, not replaced
   - white page with fog panels, FT-like charts
   - applied to every page after Samuel approves the battery, Grid and price board mockups
   - machine: code
   - where: docs/brand.md, site/app/tokens.css, every page under site/app/
   - done: the battery, Grid and price board mockups approved by Samuel from screenshots; then every page on the brand, landed with a snapshot, the mark upgraded
4. [ ] Tooling
   - installed and used: Impeccable, UI/UX Pro Max, frontend-design, Vercel web-design-guidelines and react-best-practices, chrome-devtools-mcp, AccessLint
   - evaluated: shadcn MCP and Bencium
   - machine: code
   - where: docs/tooling.md, the user-level skills of samueloldlaptop
   - done: each of the seven installed on the code machine and used in at least one session's checks, as docs/tooling.md says; shadcn MCP and Bencium evaluated in a written note under docs/reviews/
5. [ ] Licensing sweep
   - every table's license confirmed
   - permission letters to NYISO, SPP, PJM, MISO
   - costs into the LOI
   - machine: data
   - where: docs/licenses.md, warehouse/metadata/sources.csv, warehouse/metadata/coverage.csv
   - done: a verdict for every table in docs/licenses.md with the flag in coverage.csv agreeing; the four letters sent by Samuel and their answers logged; each publisher's price in the LOI
6. [ ] Reliability
   - root cause of every failed scheduled run, one alert policy, a visible green streak
   - machine: data
   - where: .github/workflows/, warehouse/health.py, docs/machines.md, /internal/health
   - done: every failed scheduled run of the last 14 days has its root cause written in queue/summary/; one alert policy in docs/machines.md; seven green days visible on /internal/health
7. [ ] Security closed, cookieless analytics live
   - machine: code
   - where: site/proxy.ts, site/lib/guard.ts, site/components/Usage.tsx, docs/security.md
   - done: every open item of the security review closed or ruled; the usage counts live on the pages the rulings allow, with no cookie and no identifier
8. [ ] First users ready
   - trader path (Pirro Prifti, Christian Mira) and the On.Energy walkthrough, feedback logged
   - machine: code
   - where: /cost-of-power/seller, /cost-of-power/battery, /board, docs/reviews/
   - done: the trader path and the On.Energy walkthrough written click by click under docs/reviews/, each walked by its user, the feedback logged there
9. [ ] Warehouse as citable record
   - Redivis under Ben's organization, first public release of public-licensed tables
   - machine: data
   - where: warehouse/redivis/, the Redivis dataset, docs/coverage.md
   - done: the dataset under Ben's organization; version 1 of the public-licensed tables released by a person's click, cited by its address on /data
10. [ ] LOI for the Stanford Sustainability Accelerator
   - draft for Samuel Monday night, Ben's input Wednesday
   - machine: code
   - where: docs/reviews/loi-stanford-sustainability-accelerator.md
   - done: a draft for Samuel on Monday night 13 October; Ben's input in by Wednesday 15 October; the licensing costs of item 5 in it

## Backlog

What goes here: what is wanted and not yet this week's, one line each, in the owner's words.

- Battery: stress slider (what if Uri happened again) as a scenario toggle.

## Rulings

What goes here: what Samuel has decided, one dated line each. The planner pastes this section into every chain it plans.

- 12 October 2026: the hurdle rate is 12 percent (Lazard's cost of equity) on battery and generator, 9.6 weighted on datacenter.
- 12 October 2026: the battery debt share is 20 percent (Lazard's storage cases), editable.
- 12 October 2026: every assumption shows its default in grey with its source and is editable in place.
- 12 October 2026: no usage count on tool pages.
- 12 October 2026: scenario A drives the headline.
- 12 October 2026: the battery headline counts whole months only.
- 12 October 2026: New York shows day-ahead first.
- 12 October 2026: "if perfectly foreseen" takes the rule's hour budget in a partial year.
- 12 October 2026: downloads (CSV, Stata, Python) stay public for public-licensed data.
- 12 October 2026: the ERCOT node price pull is approved, ceiling 500,000 rows, internal table.
- 12 October 2026: NYISO and SPP tables stay held until their licenses are answered.
- 12 October 2026: the menu is Economics (with the sub-group Infrastructure Economics: Batteries, Generators, Datacenters, What a battery saves a customer, The shoulder hours), Grid, Infrastructure, Analysis, Games, About (Data and methods, About, Terms), and Energy Digest, Roundup, Email at the right in grey.
- 12 October 2026: the datacenter tracker page is renamed "Datacenter tracker".
- 12 October 2026 (the chain prompt of sessions 208 and 209): the battery page is one page, three questions, nothing collapsed: "What did it earn?" (headline, three numbers, revenue chart, income table), "Is it worth building?" (scenarios A and B with contract share and contract price as scenario assumptions, default 0, and the results table), "What matters most" (the NPV sensitivity chart with one line on how to read it). The standalone contract section and panel, the "Other grids" table (one line under the grid picker instead) and the folds "Every month" (into the CSV download), "Stress days" and "What this model cannot see" (one sentence under the income table; the rest in the methods doc) go. At contract share 0 every number is identical to before.
- 12 October 2026 (the same prompt): docs/brand.md is the one design document; no PRODUCT.md or DESIGN.md.
- 12 October 2026 (the same prompt): no landing between 14:00 and 16:15 UTC, or Sunday 22:30 to 23:45 UTC; budget: no limit, stop at the weekly Claude limit.

## Holds

What goes here: what no session may touch, one line each. The planner pastes this section into every chain it plans.

- video/
- Thesis Builder v2
- The Grid merge's design (waits for the brand mockups)
- New sources
- The release gate

## Input from Ben and Khalid

What goes here: dated lines of what Ben and Khalid asked for or said. Read by people; the planner does not use it.

(Empty. Ben sees the roadmap and the LOI on Wednesday.)

## Review log

What goes here: one dated section per review of this roadmap, the newest last. Nothing here is ever deleted.

### 12 October 2026, review 1 (Sunday)

- v2 written with Samuel; v3 Wednesday.

### 13 October 2026, session 209 (not a review)

- v2.1: the Status lines in the planner's format; the `machine:`, `where:` and `done:` lines drafted for each item; the Backlog; the battery rulings of the chain prompt of 12 October. Nothing of Samuel's words removed.
