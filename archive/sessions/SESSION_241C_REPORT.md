# Session 241, batch C, report: the leftovers of the overnight chain

13 October 2026, unattended, one session of the overnight chain of 12 to 13 October, on the old laptop (`samueloldlaptop`, a code machine). Worktree `erw-188`, branch `wip/241c-leftovers`, from `3eeb47a7`. Nothing was pushed, no table was written, no model was called.

## Read these first

- **There is one datacenter tracker.** `/datacenters` draws what `/datacenters/v2` drew: ERCOT's large-load status (the sentence, three numbers, the chart, the table of 12 reports, the notes) and, beside it, the Texas sites the ERW holds. `/datacenters/v2` answers 308 to `/datacenters`, a query carried. The old page's file stands in `site/app/_retired/datacenters-v2/page.tsx`.
- **One sentence of the old page was false on the day and is corrected.** It wrote "No status update has been found on its meeting pages since March 2026" as fixed words. The table has grown since: its newest report is of 19 June 2026, the first row of the table right above the sentence. The month is now read from the table ("since June 2026"). The other words of the old page are as they were.
- **Every figure of the folded section carries a check key**, which the old page's had not: 38 of ERCOT's (the series key of `ercot_large_load_status`) and 11 of the facilities' sentence. `check-values` reads them from Supabase: 1,326 of 1,326 on `/datacenters`, `/board`, `/grid` and `/demand`, twice.
- **Two megawatt totals stand on the page and differ, and the page says why.** The top block's "Megawatts stated" is 18,347 MW (US rows not cancelled, session 166's rule). The old page's sentence counts every site held: 25,510 MW from 34 sites. I kept its figure and added words to it: "every site held counted, the cancelled and those with no US state among them, so more than the megawatts stated at the top of the page". See "For Samuel's ruling".
- **The color literals are tokens**, in the files the brief named and three more that the grep found. Two new ramps of grey are in `site/app/tokens.css` (`--color-year-1` to `7`, `--color-season-1` to `5`), with the values the charts drew. Four literals are not moved, with reasons, below.
- **Two of the three stale checks are rewritten and pass: `check-board-v4.mjs` (12 of 12) and `check-mix-v2.mjs` (46 of 46). `check-seller.mjs` is NOT done**: it still exits 1 on 12 of 33. What each of the 12 looks for and where it is today is under "To finish".
- **One of the 12 seller failures is not stale**: "no method prose on the page face (found "cannot see")". The page's link reads "What else the model cannot see". That is a question of words, for Samuel.
- **Task 3 is not met: three pages scroll sideways at 390.** `/demand?view=consumption` (448 px), `/deals` (534) and `/deals?tab=companies` (611). The first has a fix in the last commit that was not built or seen; the two of `/deals` are not diagnosed.
- **`check-routes` exits 1 on the last build**: one page, `/shoulder`, not this batch's, drew one "no data" block. It did not in cycle 1 or in a second ask, but that second ask was cut short, so no whole green run exists.
- **The last commit is not built** (one class on two elements, one test line).
- **I held the mutex three times, the third by accident, and cycle 1 lost three checks to my own script.** I exported `MSYS_NO_PATHCONV=1` for the whole script; it turned three scripts' own paths into `C:\c\...`, so the battery proof, the screenshots and the 390 px measurements did not start. They ran in cycle 2. A browser pass I had stopped was still alive and took the mutex for 2 minutes 15 seconds after cycle 2. See "Checks".
- **The session ran about 70 minutes, not 60.**

## What to review

Production is `https://erw-flame.vercel.app`, opened after `https://erw-flame.vercel.app/internal/open`. Nothing here is deployed; these are the addresses once the branch lands.

1. https://erw-flame.vercel.app/datacenters : under the three numbers and the two bars, the section "ERCOT: large load approved and energized, over time", then "Beside it: the facilities the ERW holds" (41 Texas sites), then "What this does not tell you" (folded), then the words about scope and the list by operator.
2. https://erw-flame.vercel.app/datacenters/v2?state=TX : lands on `/datacenters?state=TX`.
3. https://erw-flame.vercel.app/grid?grid=caiso&view=mix&mix=duck : the lines of the years, grey to cardinal, as before.
4. https://erw-flame.vercel.app/board : a row opened, "Prior years": the earlier years in five greys, as before.
5. https://erw-flame.vercel.app/deals?tab=tracker and https://erw-flame.vercel.app/storage?tab=owners : the bars and their labels, as before.
6. https://erw-flame.vercel.app/demand?view=consumption at a phone's width: the two tables under "Where industrial and commercial load is growing fastest" and the table of energy by source should scroll inside their own frame. On the build that was checked the pair still ran past the edge; the last commit's fix is not built (task 3).

Screenshots: `docs/brand/review-241c/` (README there).

## Task 1: the inventory of `/datacenters/v2`

Placed between the tracker's top block (the three numbers, "What changed this week", the two bars) and the words about scope and method that introduce the list. A reader meets the facilities first, then what Texas has approved, then the list.

| Block of the old page | Where it is now |
|---|---|
| Title "The datacenter tracker" and the line "Version 2, in review. The tracker as it was: /datacenters" | Not drawn: the page is the tracker, with its own title, "Datacenter power tracker" |
| The lead: "How much large load Texas has approved ... A request is not a built facility ... less than half has been observed running" | First paragraph of the section "ERCOT: large load approved and energized, over time" (`data-load-lead`) |
| The summary sentence (`data-load-summary`) | The same section, second paragraph |
| Three headline numbers: approved to energize 8,927 MW, observed running 3,900 MW, served at one moment 3,675 MW (the report of 19 June 2026) | The same section, a `HeadlineRow`; each now with a check key |
| The chart "MW, by report", three lines | The same section, same three series, same order, same tokens |
| The table by report (12 reports), with the month as ERCOT wrote it | The same section; each of its 36 figures now with a check key |
| The notes: load requested is not held; the one figure of new submissions (137, about 140,000 MW); the report that contradicts itself; the pause of 3 August 2026 | The same section, as a list; the four figures inside them now with check keys; "since March 2026" is now the newest report's month |
| The section's source note | The same section's note |
| Section "Beside it: the facilities the ERW holds": the sentence (380 sites, 257 in a named US state, 41 in Texas, 123 with no US state stated; 34 state a size; 275, 102 and 3 by source) | Its own section under ERCOT's, same title (`id="texas-sites"`; the old id `facilities` would have read as the list's); each figure now with a check key |
| The table "The Texas sites held" (41 rows) | The same section |
| The link "Every site, with its sources: the tracker as it was" | "Every site, with its sources: the list below", to `#every-site` on the same page |
| The fold "What this does not tell you" (four points) | Under the Texas section, folded as it was |
| The source line: the two tables, ERCOT's terms, the built stamp of the site's copy | At the end of the page, above "Related". The words "This page is in review;" are not carried (the release gate says a page's status) |

Files: `site/app/datacenters/LargeLoad.tsx` (new), `page.tsx`, `DatacentersTable.tsx` (the anchor), `site/next.config.ts` (the line session 239 left as a comment), `site/lib/release.ts` (the line stays, with a note, as for the other retired addresses), `site/lib/audience.ts` (the draft home's link).

The checks: `check-datacenters.mjs` had 11 assertions and has 15; the three that read `/datacenters/v2` read `/datacenters`, and four are new (ERCOT's section with its keys, the table's rows, the redirect with and without a query). `check-values.mjs` learned eight keys. `check-routes.mjs` asks `/datacenters/v2` through its redirect.

## Task 2: the color literals

| File | Was | Is |
|---|---|---|
| `site/components/board/Workbench.tsx` | five grey hex values | `token("season-1")` to `5` |
| `site/lib/mixpage.ts`, `yearShade` | seven greys and the accent, as hex | `var(--color-year-1)` to `7`, then `var(--color-accent)`; the same step for the same year |
| `site/app/network/Network.tsx` | the palette's eight hex fallbacks | each entry starts as its token, `var(--color-...)`; `readPalette` puts the values in before a scene is built, as before |
| `site/app/deals/v2/view.tsx` | six hex values in the chart of deals by month, and `#fff` on the chosen view | `var(--color-ink)`, `rule`, `muted`, `accent`, `surface` |
| `site/app/storage/owners/view.tsx` | `#2E2D29` twice | `var(--color-ink)` |
| `site/app/resources/ResourceMap.tsx` | `rgba(184,178,167,0.6)` and a fallback `#888888` | the token `--color-not-reported` at the same opacity; the shared reader's fallback |
| `site/app/map/ProjectMap.tsx` | `rgba(0,0,0,0)` | `transparent` |
| `site/components/mix/Charts.tsx` (the heat chart) | `#FBF8F2` and `#fff` | `token("panel")`, `token("surface")` |

Not moved, and why:

- `site/app/research/card/render.css`, four values (`#ffffff`, `#1a1a1a` twice, `#6b6b6b`): the frame of the finding cards' photographs, drawn outside the brand's wrapper on purpose; `tests/test_session182_flow.py` holds that "the photographs do not change". Moving them is a ruling on the cards' look.
- `site/app/network/Network.tsx`: the interpolation `rgb(...)` between two tokens is computed, not written; and the six numbers in `rgbOf`'s fallbacks stand for the tokens `--color-down` and `--color-up` until the page is in a browser. A canvas cannot read a variable, and the server has no document.
- `site/components/tool/ToolPage.tsx`, `#fff` in the hatched legend swatch: a shared component of the battery page, outside the brief's list. One line when wanted: `var(--color-surface)`.
- `site/lib/resources.ts`, `css()`: builds an `rgb()` string from numbers read from tokens; computed.

## Task 3: at 390 px

**Not met.** Three pages of the list scroll sideways at 390 on the build that was checked (`docs/brand/review-241c/facts.txt`, 23 pages and tabs measured at both widths; the other 20 do not):

| Page | Page width in a window of 390 | State |
|---|---|---|
| `/demand?view=consumption` | 448 | The two tables that stood outside a frame (the pair under "growing fastest", and energy by source) are inside `<div className="overflow-x-auto">`, the frame the brand's rule is written for. That was not enough for the pair: they stand in a grid, and a grid item takes the width of its content, so the frame never scrolls (`demand-consumption-390.jpg` shows the tables past the right edge). The last commit adds `min-w-0` to the two items. **Not built, not seen in a browser** |
| `/deals` | 534 | Not diagnosed. No table stands outside a frame |
| `/deals?tab=companies` | 611 | Not diagnosed. No table stands outside a frame |

`/datacenters` with the folded section is 390 wide at 390.

## Checks, with exit codes

Cycle 1 (build of `790966e7`), under the mutex 10:55 to 11:05 UTC:

| Check | Exit | Result |
|---|---|---|
| `npm run build` | 0 | no "statement timeout" line |
| `npx tsc --noEmit` | 0 | |
| `check-values`, restricted to `/datacenters`, `/board`, `/grid`, `/demand`, run 1 and run 2 | 0, 0 | 1,326 of 1,326 each |
| `check-datacenters.mjs` | 0 | all 15 passed |
| `check-board.mjs` | 0 | 36 of 36 |
| `check-mix.mjs` | 0 | 36 of 36 |
| `check-network-v3.mjs` | 0 | 33 checks pass |
| `check-demand.mjs` | 0 | 102 of 102 |
| `check-routes.mjs` | 0 | 1 live and 203 in review asked as a visitor, 0 failed |
| the battery proof, the screenshots | 1, 1 | did not start: my script's path error (above). Run in cycle 2 |
| `check-seller.mjs`, `check-mix-v2.mjs`, `check-board-v4.mjs`, as they stood | 1, 1, 1 | 12, 67 and 6 failures: the baseline before the rewrite |

Without the mutex, fetch only (no browser; `next start` on the build of cycle 1): the two rewritten checks, `check-board-v4.mjs` exit 0 (12 of 12) and `check-mix-v2.mjs` exit 0 (46 of 46).

Python: the 114 modules that read a file this session changed, three at a time, 38 batches, exit 0 each (`runs/session241c/tests1.status`), before the last three commits; after them `tests.test_session215`, `tests.test_session241c`, `tests.test_session106`: exit 0. `tests/test_session241c.py`: 12 tests, exit 0. On the head, after the last commit: `tests.test_session241c`, `test_session239`, `test_session240` (exit 0, 47 tests) and `test_session238`, `test_session106`, `test_session114_part2` (exit 0). The whole suite was not run (the orchestrator's clean copy runs it). No em dash in the 53 files changed or added.

Cycle 2 (build of `bd780021`, the head but for the last commit), under the mutex 11:23 to 11:33 UTC:

| Check | Exit | Result |
|---|---|---|
| `npm run build` | 0 | no "statement timeout" line |
| `npx tsc --noEmit` | 0 | |
| `check-values`, the same four pages, run 1 and run 2 | 0, 0 | 1,326 of 1,326 each |
| `check-datacenters.mjs` | 0 | all 15 passed |
| `check-board.mjs`, `check-mix.mjs`, `check-network-v3.mjs`, `check-demand.mjs` | 0, 0, 0, 0 | 36 of 36, 36 of 36, 33, 102 of 102 |
| `check-board-v4.mjs`, `check-mix-v2.mjs` (rewritten) | 0, 0 | 12 of 12, 46 of 46 |
| **`check-routes.mjs`** | **1** | one failure in pass 1: `/shoulder` drew 1 "no data" block (0 on production). Not a page of this batch. Cycle 1's run had it at 0, and a second ask on this same build had it at 0 too, but that second run is not a pass: it was cut at page 205 of 211 when the server under it was stopped (below). **There is no whole green run of `check-routes` on this build** |
| the battery page, `runs/session208/capture.mjs` at 1280 | 0 | 51 checked numbers; `diff` with `runs/session211/shots/after_nums.txt`: 0 lines; height 5016 |
| `/datacenters/v2` as a visitor | | 308 to `/datacenters`; with `?state=TX`, 308 to `/datacenters?state=TX` |
| the screenshots and the 390 px measurements, `runs/session241c/shots.mjs` | 1 | 46 page loads, none failed; **3 pages scroll sideways at 390** (task 3, above) |

**The last commit is not built.** It adds one class (`min-w-0`) to two elements of `site/app/consumption/view.tsx` and one assertion to the new test. Every check above is of the commit before it.

**The mutex: three holds, and the third was not meant.** Cycle 1, 10:55 to 11:05. Cycle 2, 11:23 to 11:33. Between them I had queued a browser-only pass (`pass2.sh`), then replaced it with cycle 2 and stopped its task; the stop ended the task's wrapper and not the shell under it, which went on waiting, took the mutex the second cycle 2 gave it back, and held it from 11:33:13 to 11:35:28 for a battery proof and screenshots that cycle 2 had just made. It started its own server and stopped it, gave the lock back itself, and left no process and no listener on port 3245 (checked). It cost session 242 two minutes and fifteen seconds. Its stopping the server is what cut my second ask of `check-routes`.

Also without the mutex, fetch only: `next start` on the build of cycle 1 from 11:06 to 11:10, to save pages' HTML and to run the two rewritten checks. No browser was opened outside a hold.

## Pins moved (each with a "session 241" note)

- `tests/test_session106.py`: the page's strings are pinned in `site/app/datacenters/LargeLoad.tsx` (the page and its header in `page.tsx`); the no-em-dash list names the new file and the retired one.
- `tests/test_session114_part2.py`: the built stamp of `/datacenters/v2` is printed by `LargeLoad.tsx`.
- `tests/test_session239.py`: `/datacenters/v2` joins the versioned addresses that redirect.
- `tests/test_session240.py`: the whole-megawatt rule of `check-values.mjs` names two more sums.
- `tests/test_session238.py`: its block of `tokens.css` ends where another session's begins (it ran to the end of the file, so any block appended after it was held to session 238's rules; batches A and B append too).

## Decisions made without you

- The folded section stands between the top block and the list, not after the list (380 rows) and not as a tab.
- The Texas section's id is `texas-sites`, not `facilities`.
- The words "This page is in review;" of the old source line are not carried.
- "since March 2026" became the newest report's month, read from the table.
- Words added to the old sentence's megawatts, so that two totals on one page do not read as a contradiction.
- The new tokens are written at `:root`, in my block at the end of `tokens.css`, because a chart reads a token at the page's root.
- `/datacenters/v2` stays in `release.ts` as `review`, as the other retired addresses do.
- `check-seller.mjs` was left for another session rather than half rewritten.
- A second hold of the mutex with a build, for one sentence, rather than a hand-back with a false sentence on the page.

## For Samuel's ruling

1. **Two megawatt totals on `/datacenters`** (18,347 MW counted by session 166's rule; 25,510 MW of every site held, from the old page's sentence). Keep both with the words added, or make the sentence count as the top block does.
2. **"What else the model cannot see"**, the link on "What a generator earns": `check-seller.mjs` reads "cannot see" as method prose on the page face. Reword the link, or let the check allow it.
3. **The finding cards' render frame** (`render.css`): four colors of its own. On the brand, or as it is.
4. **The title "Beside it: the facilities the ERW holds"** was written for a page whose subject was ERCOT. On the tracker it sits under ERCOT's section and above the list of all facilities. It may want "The Texas sites the ERW holds".

## To finish

1. Build the head and look at `/demand?view=consumption` at 390 (one hold of the mutex):
   `cd site && npm run build > ../runs/x_build.out 2>&1; echo "exit=$?"`, `npx next start -p 3245`, then
   `node C:/Users/lossa/Documents/erw/runs/session241c/shots.mjs http://localhost:3245 C:/Users/lossa/Documents/erw/runs/session241c/shots3; echo "exit=$?"` (exit 0 only when no page scrolls sideways at 390; do not export `MSYS_NO_PATHCONV` around it).
2. `/deals` and `/deals?tab=companies` at 390: find what is wider than the window (in a browser: the elements whose right edge is past `clientWidth`), and frame it.
3. `node scripts/check-routes.mjs http://localhost:3245; echo "exit=$?"` once, whole, on that build.
4. `check-seller.mjs`, below.

`check-seller.mjs`: 21 of 33 pass. The 12, and what the page shows today (read from the built page; `runs/session241c/probe3.mjs` prints it):

| Assertion | Today |
|---|---|
| the layout: sections capture, capture-years, hub-years, spans, contract, hybrid, profile, months, coverage | three sections: `earned`, `scenarios`, `matters`; `data-summary` and three `data-question` are there |
| no method prose (found "cannot see") | not stale: see "For Samuel's ruling" |
| what the seller's tab showed: the median month, the worst three months, coverage over trailing months, the stress days, every month | on the face: "Debt coverage, last twelve months"; the months are the file behind "Every month, CSV" (`data-months-csv`); the stress days and the hybrid are named as being in "the other tables, CSV" |
| each of the model's numbers equals the library's, more than 50 keys (four addresses) | two `mr` keys a page; the capture table's 154 `cap` keys (solar, wind) or 168 `data-model-cap` cells (battery, peaker) |
| New York: "not modeled for this grid" in the hybrid section | no hybrid section; `data-seller2-none` and 21 `data-missing` cells are there |
| the battery: "Energy, MWh", "Energy alone", "With your contract not held yet" | the first two are there; the contract line is not |
| the hybrid figures, ERCOT and CAISO; "for another asset the hybrid section points to solar" | no hybrid section on the page; the inputs `data-hybrid-inputs` and `data-duration` remain for solar and wind |

Its browser half (lines 175 to 215) was not looked at.

## The landing

- Landed in one push with session 242's final pass, on `task/242-final`: `main` as of 11:36 UTC, batch C (`wip/241c-leftovers`), the final pass (`wip/242-final`), the reports of sessions 241 and 242. `tokens.css` is our file plus batch C's own block (what stood before the block in its branch was identical to the base, checked).
- The whole suite in a clean worktree at `87534c41`: exit 0, 3,937 tests OK, 237 skipped.
- `npm run build`: exit 0, no "statement timeout" line. `check-values` on every page: a first run 4,635 of 4,637 (two interchange figures of MISO at the Grid tool's Exchange view: the run crossed 12:00 UTC and met the network snapshot's revision, as session 237's report said it can); a second run on the same build 4,637 of 4,637, exit 0. `check-routes`: exit 0, 204 pages as a visitor, 0 failed. Exit 0 each: `check-no-request`, `check-datacenters` (15 of 15), `check-board` (36 of 36), `check-demand` (102 of 102), `check-mix` (36 of 36), `check-network-v3` (33 of 33), `check-datacenter-scenarios` (119 of 119).
- On the same build the 18 addresses batch C changed were shot again for `docs/brand/review-final/` (12:18 UTC) and the folder's README rewritten from the measurements: `/demand?view=consumption` no longer scrolls sideways at 390; `/deals` (534 px) and `/deals?tab=companies` (611 px) still do; `/datacenters/v2` ends on `/datacenters`.
- `python scripts/freeze.py status`, the before snapshot (its own command), the push, GitHub's check, the merge, the after snapshot and the comparison: in the chain's closing message and, if a further push follows, in a line added here. Expected: 0 differences on the 25 pages (every page is in review; the menu does not change; `/datacenters/v2` is not one of the 25).
