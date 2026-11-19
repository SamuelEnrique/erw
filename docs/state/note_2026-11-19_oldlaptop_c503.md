# Note of chain 503 (the old laptop, sessions 8400 to 8500, 19 November 2026)

Energy Research Warehouse (ERW). The chain file: `queue/done/503-day-19-november-oldlaptop-rulings-evidence-whole-country-pages.md`. Model spend USD 0. Nothing landed, no table written, no page opened to visitors, no hold lifted, no ruling taken. The step-by-step record is `docs/state/progress_c503.md`.

## Part A: the evidence behind the rulings

- **Read first:** `docs/reviews/rulings-one-sitting-2026-11-19.md`, one line for each of the 129 questions, each linked to its entry in `docs/reviews/rulings-ranked-2026-11-17.md`.
- **The counts.** Before (17 November): switch 26, keep 15, no basis to recommend 88. Each of the 88 was looked up in three places (published practice, Samuel's own rulings on a like question, the tool's method note): 33 came out keep, 28 switch, 27 still have no basis. **The list now: switch 54, keep 48, Samuel's call alone 27.**
- **The defaults list** (`docs/reviews/rulings-defaults-2026-11-17.md`): 227 questions, closed by one "defaults stand".
- **The twelve figures that did not agree, by cause:** a rate of the wrong year, 2 (entries 53 and 117: the commission's 2025 transmission rate where 2026's was approved); a partial month, 1 (entry 67); a rounding, 3 (entries 48, 89, 113); a count taken two ways, 2 (entries 78 and 119); a summary that miscounts its own printout, 1 (entry 6); a file rebuilt between the two readings, 1 (entry 18); other, 2 (entry 118: one printed range held two ways in a table; entry 127: solar's 35 years used for a peaker's 30). One cause is the data machine's: request row 320.
- **The six screenshot faults:** four fixed on their branches with a test and back to `wanted` (rows 341, 362, 363, 366); row 357 is a data fault (request row 321, with row 322 beside it); row 345 is the hold as it stands.
- **Five entries corrected in their own words** (23, 75, 77, 94, 107). The one that matters for money: entry 77 gave ICE's fee (USD 25,000 to 30,000 a year) as the price of either purchase; PJM's membership is USD 2,500 to 5,000 a year.
- **The hosts read:** `docs/reviews/rulings-evidence-hosts-2026-11-19.md`. Every host's robots file was read before a page. The terms of use were read for every host only afterwards, the same day. One host bars automated reading (`www.pge.com`): the one sentence taken from it was withdrawn from entry 61, whose recommendation did not rest on it. No recommendation moved.

## Parts B, C and D: the whole country on three pages

Each page's new views are on a branch, held by tests and by the page drawn to HTML with the site's own code. None was built, none was seen in a browser, and none has drawn a real figure yet: **the data machine's page files were not on origin/main** (only `site/data/regions/ba_boundaries.json` was), so each view reads "not built yet" until its file lands. Each was coded against the contract `docs/state/page_files_regions.md`, against a fixture whose values are made by a rule (not data, never shown on the site), and against the data machine's builder as read on its branch.

| Page | New views | Branch to land (row) | Held by | Browser reads wanted |
|---|---|---|---|---|
| `/events` and its nine event pages | "The whole country" on each event page: thirteen regions across the event against the baseline, generation by source, power between regions pair by pair, a region or two hour by hour; on `/events`, how many regions each event reached | `wip/8440-events-regions-done` (row 51) | the pin of ten pages in two draw modes, 21 of 21 each; the section 78 of 78; the replication 203 of 203 on the fixture | rows 377 to 382, 417 |
| `/demand` | a fourth view, `/demand?view=country`: any region or balancing authority, two side by side: demand by day, year by year, where the growth is, a region's weather view, a region beside its grid | `wip/8450-demand-regions-done` (row 52) | the pin of 50 addresses, 101 of 101; the view 93 of 93; the replication 19,191 of 19,191 on the fixture | rows 383 to 391, 410 to 414 |
| `/supply` | net imports by month and by neighbour with each side's report and the gap; who trades with whom by year; the generation mix by region; two regions side by side | `wip/8460-supply-regions-done` (row 53) | the pin of 103 addresses, 208 of 208; the section 109 of 109 and 20 of 20; the replication 33,132 of 33,132 on the fixtures | rows 393 to 400, 403 to 406, 417 |

- **Add, never change:** outside what was added, every address of the three pages is byte for byte what it was; each page has its pin test. Every page stays in review.
- **Land row 51 first** (rows 52 and 53 stand on its branch), then 52 and 53 in either order. A site build is needed on the landing machine: a type check passed here and a build may still refuse.
- **One thing a build must carry:** `site/next.config.ts` now names `data/regions` for `/events`, `/demand` and `/supply` (on row 51's branch, with a test). Without it the pages would not find the files on Vercel.
- **The six regions the site never showed** (the Southeast, Florida, the Carolinas, Tennessee, the Northwest, the Southwest) are named on each page, each with a hover saying so.
- **Not on any page, as the chain asks:** no estimate of a share of a shock covered by imports, no ledger of regions that gave and took; a test on each page holds it.

## Part E: the done line of the new views, as far as it goes without the files

- **Done for each page:** the method note; the replication, written from the note and the contract and tested on the fixture; the reader and five real cases written; the gaps a reader would meet that need no real figure (events 4 rows, demand 11, supply 15), ten of them fixed on the branches with tests.
- **Waiting for the files, for each page:** the five cases read start to finish; the replication's count on real files; the Stata do-file's five headline figures (none was written with made-up values); the cross-check against published figures. The first steps are in the progress file, page by page.
- **Found for the data machine before its files land** (rows of `docs/state/data_requests_done_line.md`): **328, a fault of its builder: a record's first and last local day are written as whole days on however many hours the record holds**; 323, 324 to 327 and 329: keys the builder writes that the contract does not list, names for authorities across the border, the months a pair's year holds, how the seven grids' authority files stand against `demand_growth.json`.

## Part E on the real files (sessions 8470, 8480, 8490; written at the chain's last session)

- **The page files landed on origin/main** in `af1962719` (the data machine's chain 501), byte for byte the copies the three pages were first read against. Each branch merged origin/main; none commits a page file of its own.
- **Each page's pin still holds** (run again by the main session from each branch's head): no figure the three pages show today for the seven grids moved.

| Page | Branch, head (landing row) | Replication on the real files | Five cases | Gaps found on the real files, fixed with a test | Stata do-file | Cross-check |
|---|---|---|---|---|---|---|
| events | `wip/8440-events-regions-done`, `c7a96eea1` (51) | 2,434 of 2,434 over the nine events | all five answered on the page | rows 5 to 18 of the read; five fixes (the Northwest's sources over Uri, the pairs against net imports on hover, the 21-day switch's hover, ERCOT as Texas's one authority, storage before July 2024) | written; its five steps done in Python give each expected value to the last digit (Stata not on this machine) | Texas over Uri: 69,215 MW against ERCOT's preliminary 69,222 MW (ERCOT's settled 69,812 MW came later); California, 6 September 2022: 63,622 MW against CAISO's 52,061 MW, because EIA's California region holds four authorities beside CAISO; Tennessee and the Mid-Atlantic: no public figure could be read (TVA's robots file answered 403; PJM's terms not found, so nothing read) |
| `/demand` | `wip/8450-demand-regions-done`, `34c53f280` (52) | 449,440 of 449,440 over 783 views of 71 places; the seven grids as authorities against the as-metered file: 47 of 49 yearly averages equal (CAISO 2023 and 2025 differ by 0.1 and 0.4 MW) | 1, 2, 3 and 5 answered; **4 (the Southeast beside Florida, weather taken out) cannot be:** only 53 of 256 regional weather figures are in the files | rows 12 to 25; 12 to 21 fixed (a day counts as whole only on every hour of its local day: request 328 holds for two days, LGEE's 1 July 2018 and MISO's 16 November 2026) | written with five figures (the Southeast's 2025 average stands in for the weather figure the files lack) | ERCOT and EIA's Today in Energy within 0.4 percent; SRP's records 1.8 and 2.8 percent below the page in 2024 and 2025, and 12 percent below its 2023 peak hour (request 548); TVA, Duke Energy and APS refused |
| `/supply` | `wip/8460-supply-regions-done`, `1e3a9e95b` (53) | 43,552 of 43,552 over 27 files with `--same-flow`; the same flow in two files 375 of 375 | all five answered | rows 16 to 27; six fixes (the months a pair's year holds, the storage hover, "0.0" for a figure rounding to zero, the mean's hover, the hours behind a percent, a mix month left out drawn as "not held yet") | written with five figures (needs Stata 16 with Python, the files being JSON) | Texas's 2025 shares within 0.4 points of ERCOT's fact sheet; September 2024 within 0.5 percent; EIA's Short-Term Energy Outlook puts ERCOT's solar 14 percent below ours, wind within 1.4 percent; trade with Canada and Mexico differs from Form EIA-111 by definition, Mexico's sign opposite (cause named, not confirmed) |

- **New rows for the data machine:** 545 (both sides' report a pair in the event files: the Midwest's pairs give +9,619 MW against net imports of +5,427 MW over Uri), 546 (the regions' weather hours), 547 (Seminole's 2019), 548 (SRP's hours of 22 and 23 July 2023), 549 (mix months left out, by region), 550 (the Mid-Atlantic's 7,098 hours with the Carolinas against 8,735).
- **New browser reads wanted:** rows 418 to 422, one or two a page, each at 1280 and 390 px.
- **No screenshot was taken:** this machine cannot build the site.
- **Hosts read for the cross-checks:** each page's read document holds its table of hosts with robots and terms cells. Not asked: FERC, NERC, CAISO (on `/supply`) and the paused hosts. Not read: SPP (its terms point to an acceptable use policy not read), PJM (terms page not found).

## What waits for Samuel, each with the default taken

- **From the reads on the real files:** charts of the event pages in each region's own time (default UTC: the chart is shared by every page); a peak hour set against the baseline at that hour, not the baseline days' own peak (default that hour); the 95 percent rule for the regions' weather figures (default kept, which leaves most of them blank); a region's hour needs every one of its authorities, which leaves Florida without a whole 2019 (default kept); the screen of hours that let SRP's 2023 hour through (default the 25 percent rule kept); "12 of 12 months" beside a report holding 81 percent of the hours (default months on the face, hours on hover); Texas's 2025 solar share over the 11 months held (default the share over the months held, the count shown).

- **The rulings themselves:** the sheet for one sitting. Default: nothing changes until he rules.
- **Berkeley Lab's two addresses.** The lab's programme site answered HTTP 403; its queue report was read at the lab's publications address, which the repository's own method note gives. Default: used. If that is a second door to a host that refused, entries 20 and 92 go back to "no basis to recommend".
- **Entry 42 (Louisiana) reads "switch" on a license question,** by ruling 4 of 6 November read as deciding the like case. If that ruling covers the large-load table only, it is his call alone.
- **Entry 36:** how the Texas Comptroller's robots file is read. Default: the standing refusal, no page asked.
- **Terms of use not settled:** three hosts whose terms could not be read, fourteen with no terms page (Potomac Economics, cited in 22 entries, is one), three that limit reuse to non-commercial use. Default: a fact or one short phrase, cited, from a host that does not bar it.
- **EIA's regional figures for New England, New York and the Midwest on the three pages.** The files are public by the contract; the older sections of the event pages are under the hold of 21 October. Default: drawn. `REGIONS_HELD` on each page blanks them with "license needed".
- **"Reached" on `/events`: 5 percent** from the baseline, either way. No publisher's threshold stands behind it.
- **A "large" gap between two sides' reports on `/supply`: 10 percent** of the mean size of the two. The same.
- **The places drawn first:** on the event pages each page's own (Tennessee and the Carolinas for Winter Storm Elliott); on `/demand` Tennessee and the Carolinas; on `/supply` California and the Carolinas, and the year 2025.
- **On `/demand`:** the tab's name ("The whole country") and its place as fourth; two charts of days with two scales; generation-only authorities listed.
- **On `/supply`:** no sorting of the pairs; each authority's net imports as a share of its demand is in the file and is not drawn.
- **The event pages now read their address** (for the choice of region), so they are drawn at each request, as `/demand` and `/supply` are.
- **`wip/alt-events-1` has a fault of its own** (its whole estimates section reads "license needed"), described and not fixed: the fix decides what a refused read draws under a hold.

## Needs the key

- Nothing in this chain called a model or needed to.

## Mistakes of this chain, said plainly

- **A file written over in a worktree:** `site/lib/regions.ts` (session 18's) was overwritten by a new library of the same name, seen at once, restored from git before any commit; the new library is `site/lib/countryfiles.ts`.
- **Terms of use read late:** the research agents read robots files and not every host's terms; a check the same day read them (above).
- **One commit made before its check finished:** the config line was committed while a scratch check of it had failed on its own pattern; the file was then parsed and found whole (15 keys, no error).
- **A session's agents stopped by the harness:** the session of 13:16 UTC started the three pages' agents in the background and ended its own turn; the harness stops background agents 10 minutes after the last turn, so the three were cut off at 13:30 UTC with small edits uncommitted. The next session ran them in the foreground, and they finished the uncommitted edits first. Twice before that, sessions were closed by the chain worker after 30 minutes with no commit.

## Where the chain stopped

- **Finished (session 8500, 19 November about 14:20 UTC).** Part E is done on the real files for all three pages; the resume file `queue/next/533-resume-chain-503.md` is removed and the queue step run. What is left is landing rows 51, 52 and 53 (row 51 first), the browser reads, the data requests, and Samuel's rulings.
- **What stood earlier in the day:** it was not finished. Every step that needs no file of the data machine is done; what is left of part E waits for the files. A watch for them was stopped by the harness when the machine ran low on memory and was not started again. The resume file `queue/next/530-resume-chain-503.md` is left in place and the queue step was not run. `docs/state/progress_c503.md` says, step by step, how a session continues once a file is on origin/main.

## On this machine

- Worktrees of this chain, each clean and at its remote: `erw-8410`, `erw-8420`, `erw-8430`, `erw-8440`, `erw-8450`, `erw-8460`, and six `erw-c503-*` of the screenshot faults. None was removed.
- `runs/c503/` (not in git) holds the evidence files, the hosts files, the saved robots and terms pages, and every script of the chain.
