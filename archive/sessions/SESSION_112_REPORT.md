# Session 112 report: the state of the platform

**Written: `docs/state_2026-10-04.md`.** Every tool with its address, live or in review, what it answers, its data and how fresh it is, its weakest point, and what would make it ready to share; then the ten things most worth doing next, ranked, with reasons. It is on main (`6d1a85b`). One deploy; the live pages changed only where the clock moved them (the home page's 15-minute prices, the network page's hourly refresh). This is the last session of the chain.

## Read these first

1. **Found while writing it, and first in the ranked list: the battery page's daily refresh broke today.** The daily run of 4 October (14:45 UTC) could not pull ERCOT's reserve prices: `RuntimeError: NP4-181-ER zip holds ['rpt.00013091.0000000000000000.20261004.080005.DAMASMCPC_2026.xlsx'], expected one CSV` (`warehouse/metadata/run_status.csv`). The battery step then skipped ("inputs missing: ercot_as_prices"), so `battery_stack_monthly` was not rebuilt and the live battery page reads the build of 3 October, 17:09 UTC. Nothing on the page moved and nothing was filled. **Not mended:** finding out what ERCOT now posts needs a request to ERCOT, and the chain allowed three named pulls. Whether today was one day's file or the new form is not known. If it is the new form, the page falls a day further behind each day.
2. **Session 111's last fix went out with this push and is checked on production.** The end screen's replay could take the page down on its first frame, as the game could. On production after this deploy, with the case forced: 19 of 19 checks at a laptop's width and 19 of 19 at a phone's (`runs/112_game_prod_easy_laptop.out`, `runs/112_game_prod_easy_phone.out`). The ten full plays (91 of 91 at each width) were on the build before it; the replay's change is one line in the end screen.
3. **What the document is and is not.** The six open tools and the twenty pages built or rebuilt in sessions 91 to 111 were opened on production today, and the document says so. The older pages in review were not opened by this chain: they are described from `docs/platform-tools.md`, the release list, coverage and the route check, and the document says that too, under its own heading. A weak point given for one of them is the weak point on record, not one I looked for.
4. **Its figures were read again from the repository before it was committed,** and four were wrong in the first draft and are corrected: the faults held as published (14 of 26, not 12), the sources in the registry (210, not 209), two addresses that are not pages by themselves (`/data/methods`, `/reports`), and "rebuilt daily" for the battery table (item 1). One claim had no source and was removed (that the battery page is the most-read tool: the repository holds no count of readers).

## The document

Three tables and a list.

| Part | Rows | From |
|---|---|---|
| Open to visitors | 6 | the live pages, their tables' last day in `coverage.csv`, today's snapshots |
| In review, built or rebuilt in this chain | 19 rows, 20 addresses | sessions 91 to 111's reports and checks |
| In review, older pages not opened by this chain | 16 rows for about 40 addresses (the seven grid pages, the four problem sets and the first versions are grouped) | `docs/platform-tools.md`, the release list, coverage |
| The ten things most worth doing next | 10, each with its reason | the weak points above |

Counts read today: 71 addresses, 11 live; 132 tables (112 public, 20 internal), 16,048,958 rows; 26 known faults.

**The ten, in order:** mend the battery page's daily refresh; measure what real batteries were awarded (session 108's finding); rule on MISO's terms; apply the impossible-hours screen to the three tables behind live pages; put the seven hand-built copies on a schedule; open the six pages that are ready, the fault page first; fix California's carbon intensity for the months in the register; give Ask ERCOT a daily summary of hub prices; release a Redivis version; make the network's third version the live page. Each reason is in the document. Items 4 and 10 change what a visitor sees and need your word; item 9 is your click.

## Deploy and snapshots

Workflow run 37247251873 passed (tests, site build, route check) and merged as `6d1a85b`; Vercel accepted the deployment (00:28 UTC, 5 October). `before-112` (00:21 UTC) against `after-112` (00:28): **33 differences, all expected, none this session's.**

| Page | Differences | What | Expected |
|---|---|---|---|
| `/` | 27 | the latest real-time prices of five hubs moved to their next interval (ERCOT 52.04 to 54.17, SP15 50.11 to 70.71, New York City 43.87 to 42.39, SPP North 526.07 to 278.02, ISO-NE 45.78 to 50.34 USD/MWh), with their interval lines | yes: the 15-minute refresh |
| `/network` | 6 | "refreshed 2026-10-04 23:05 UTC" became "2026-10-05 00:05 UTC"; demand's newest hour 21:00 became 22:00 UTC; the source line's build stamps the same | yes: the hourly refresh ran at 00:05 between the two snapshots |
| the other 23 pages | 0 | | |

The push carried two things: this session's document and its test, and session 111's replay fix (in the game, a page in review). No live page reads either.

## Tests

- `tests/test_session112.py`, 6 tests: every address the document gives is a page of the site (the first run of this test found the two that were not); the six open tools are in it under "Open to visitors"; each row carries the five things asked for; the ranked list is ten, each with a reason; it says what was looked at today and what was not; no em dash. The document is dated, so its figures are not held to tomorrow's tables.
- Every session's tests on this machine: 802 ran; one fails and is not this session's (the interchange ceiling of session 49, which GitHub does not run).
- On production after the deploy: `/play/battery`, `/home/v2`, `/data/faults` and `/network/v3` render with data in the internal view and are closed to a visitor.

## Errors and decisions

1. **The battery refresh was not mended** (read first, item 1). I judged a fourth pull outside what the chain allows, and a change to the connector that cannot be run against ERCOT's file is a guess. It is written first in the list so that it is the first thing done.
2. **The first draft was written from the day's work and then checked, not the other way round.** Four figures and one claim were wrong (read first, item 4). The script that reads them again is `runs/112_facts.py` (not in git, like the rest of `runs/`).
3. **A local server outlived its stop twice** (port 3111); each time it was stopped by its process number before the next build was served.
4. **No model call, no pull, no table, no load. Model spend USD 0.00.**

## The chain, sessions 102 to 112

| Session | What | Where | State |
|---|---|---|---|
| 102 | Sessions 91 to 101 landed | `SESSION_102_REPORT.md`, with the review list | on the live site, new pages in review |
| 103 | Known data faults | `/data/faults` | in review; 26 faults in the register |
| 104 | Price board, version 3 | `/board/v3` | in review |
| 105 | Project map, version 2 | `/map/v2` | in review; 41 of 41 in a browser |
| 106 | Datacenter tracker, version 2 | `/datacenters/v2` | in review; pull 1 of 3, 29 rows |
| 107 | Seller tab, version 2 | `/cost-of-power/seller/v2` | in review |
| 108 | What real batteries earned, scoping | `docs/methods/ercot_disclosure_scoping.md` | pull 2 of 3, a sample of 244,968 rows kept out of coverage |
| 109 | The network, version 3, finished | `/network/v3` | in review; pull 3 of 3, 190,512 rows; 30 of 30 in a browser |
| 110 | Home and menu by audience | `/home/v2` | in review |
| 111 | The battery game, checked | `/play/battery`, `docs/battery_game_demo.md` | in review; a first-frame fault found on production and fixed |
| 112 | State of the platform | `docs/state_2026-10-04.md` | on main |

**Live pages changed without being meant to, over the whole chain: three,** each found by the snapshot comparison and each in its session's report: the count of sources on `/terms` (session 102; put back the same hour), the home page's "Last refresh" stamp and row total (session 103's load; the stamp corrects itself with the next daily run), a section added to a live methods page (session 109; put back the same hour). **Vercel refused no deploy.** All three pulls stayed under their ceilings and MISO was not requested. Model calls: session 102's three questions, USD 0.2253; nothing else.

## For Samuel

1. **The battery page's refresh** (read first, item 1): look at tomorrow's daily run. If `ercot_as_prices` fails again the form has changed, and the connector's `parse_year` needs to read the Excel file or find the CSV beside it.
2. **The ranked list is mine;** the order is an argument, not a measurement. Items 2, 3 and 9 wait on you and unblock the most.
3. **The freeze:** it runs to 6 October. Items 4 and 10 of the list are for after it.

Energy Research Warehouse (ERW), session 112, on the old laptop (`samueloldlaptop`, data role), 2026-10-04 from about 23:20 UTC to 2026-10-05 00:40 UTC, unattended.
