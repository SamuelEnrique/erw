# Roadmap

Energy Research Warehouse (ERW). What the machines do next, in the owner's words. `scripts/planner.py` reads this file, and no other, to decide what to plan (`docs/machines.md`, "The planner"); it never edits it. Only a person writes here. Until a person writes `planner: on` under "Status", the planner is off and nothing is planned.

Version 2, 12 October 2026: Samuel's words from the review of Sunday 12 October, entered by session 201 from the chain prompt of that night.

## Status

What goes here, one line each: `planner: on` or `planner: off` (absent means off); `budget: N sessions a day per machine`; `earliest start: HH:MM UTC` and `latest start: HH:MM UTC`, the hours between which a session may start; `deploy cutoffs: HH:MM to HH:MM UTC` (several are separated by semicolons; `none` when there is none).

- planner: off (Samuel turns it on after reading session 197's report)
- budget: no limit on sessions; stop at the weekly Claude limit; resume at its reset
- earliest start: 00:00 UTC
- latest start: 23:59 UTC
- deploy cutoffs: none this week except Sundays 15:30 to 16:45 Pacific (the Roundup)
- reviews: Sunday, Wednesday and Friday evenings
- public day: Monday 20 October 2026, gated by licenses and seven green days of every scheduled job

## This week

What goes here: numbered items, `N. [ ] title` while open and `N. [x] title` once closed, each followed by indented lines: `machine: code` or `data`; `where:` the page or table; `done:` what done means; `rulings:` a ruling already made, one a line; and, where wanted, `session:` one session's work (up to three), `cap: USD n` for model spend, `lands: yes` or `no`.

In priority order.

1. [ ] The loop runs itself
   - main green, planner on, queue never empty
2. [ ] Five tools sellable
   - battery, generator, datacenter: finishing (signed method docs, replications, cross-checks, decisions blocks)
   - Automated Analysis to its final form
   - Grid: network, energy mix and Ask merged into one tool
3. [ ] Brand, full
   - `docs/brand.md`, direction A: Source Serif 4 display, IBM Plex Sans text, Plex Mono numbers
   - the E-in-cardinal-square mark upgraded, not replaced
   - white page with fog panels, FT-like charts
   - applied to every page after Samuel approves the battery, Grid and price board mockups
4. [ ] Tooling
   - installed and used: Impeccable, UI/UX Pro Max, frontend-design, Vercel web-design-guidelines and react-best-practices, chrome-devtools-mcp, AccessLint
   - evaluated: shadcn MCP and Bencium
5. [ ] Licensing sweep
   - every table's license confirmed
   - permission letters to NYISO, SPP, PJM, MISO
   - costs into the LOI
6. [ ] Reliability
   - root cause of every failed scheduled run, one alert policy, a visible green streak
7. [ ] Security closed, cookieless analytics live
8. [ ] First users ready
   - trader path (Pirro Prifti, Christian Mira) and the On.Energy walkthrough, feedback logged
9. [ ] Warehouse as citable record
   - Redivis under Ben's organization, first public release of public-licensed tables
10. [ ] LOI for the Stanford Sustainability Accelerator
   - draft for Samuel Monday night, Ben's input Wednesday

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
