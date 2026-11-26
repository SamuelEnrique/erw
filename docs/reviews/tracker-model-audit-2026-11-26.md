# The datacenter power tracker: the model audited as a hostile expert would

Session 10211, 26 November 2026, chain 710 (part D), the old laptop. Read as an AI lab's site-selection lead, who would use this page to find where load is landing and wants to find it wrong, and as a utility load forecaster, who would set its megawatts beside the load in a forecast. In the form of `docs/reviews/severance-model-audit-2026-11-26.md`.

- Nothing changed on main but this file and its folder of evidence (`docs/reviews/tracker-model-audit-2026-11-26/`). No table written, no lock taken, no default moved, no model called, no request to any service.
- Each finding's test is on its own branch, `wip/audit-tracker-<n>`. Branches that change only words are for landing (the rows at the foot); a branch whose fix would move a figure carries the test only and is not for landing.
- Not repeated: the cost page (`/cost-of-power`, `docs/reviews/datacenter-model-audit-2026-11-26.md`), whose flat-load arithmetic the power side borrows; datacenters in `/impact` (window C's tonight). Earlier reads of this page are cited: the faults of 11 November (`docs/reviews/datacenter-faults-2026-11-11.md`, "the faults file") and the five items of the method note's section 13, which wait for Samuel.
- **The hold.** `datacenter_facilities` is held whole ("license needed") since 21 October 2026, so a visitor today sees the hold's sentence, ERCOT's section, the power side, the view by grid and the decisions. The facility figures (counts, megawatts, rollups by state, grid, operator and status, the timeline, the charts) are drawn once the hold allows. Both are restated here: what a visitor sees, and what the page draws without the hold. No row of the held table is printed in this file or its folder, only sums and counts, as the replication does.

## In short

- **The arithmetic is right.** An independent restatement written from the method note (`docs/methods/datacenter_tracker.md`, sections 3 to 8), not from the page's code, gives every keyed figure of both views from the warehouse's own files to the digit: 454 of 454 equal to the page's functions run on the same rows (the largest gap 1.2e-15 relative). Facilities held 458, counted 274, no US state 180, cancelled 4; 28,254 MW stated by 21; by status planned 21,305, no status 6,766, under construction 108, operating 75; ERCOT's newest report 8,927 MW approved, 3,900 observed (44 percent); two queue sites asking 191.26 MW; eight ERCOT load zones' flat-load prices, USD 34.02 to 39.01 per MWh.
- **A third of the megawatts is one known wrong join, and the page never says so (finding 1).** 9,400 of the 28,254 MW stated (33.3 percent) is a 2025 story of a Utah datacenter joined to a 2026 story of a 9.4 GW campus on the word "Utah" alone; it also sets the planned chart's only bar before the fourth quarter of 2026 and one of the timeline's three US rows. The page's own sentence on joins ("same operator and place") is not the news extractor's rule. Fixed in words; leaving the row out of the sums (-33.3 percent) is a figure, for Samuel's ruling.
- **"The news since 2025-01-01" is a window with a hole (finding 2).** No story of May to September 2025 was scored (1,885 stories, 13 scored, none sent to the extractor); 136 of the 193 facilities with a first story were first reported in September to November 2026. The chart of planned megawatts by the quarter first reported measures what was read, not what was announced. Fixed in words.
- **The headline megawatts do not say what they measure (finding 3).** The sum adds IT load, a facility's total and figures whose basis no source states (20 of the 21 rows); the method note says the page says so beside the sum, and the top block does not. Read as IT load at the cost page's own overhead ratio of 1.56, the grid would see 9,998 MW more (+35.4 percent). Fixed in words.
- **Smaller.** The operator chart says "the operator, else the developer"; the code reads the operator alone, so the bar that would read 10,400 MW reads 1,000 (finding 4, words). The timeline counts every facility held, unlike every other section: 6 of its 9 rows state no US state (finding 5, words). The view by grid's price range sets a real-time zone beside a day-ahead one, unsaid (finding 6, words).
- **What a load forecaster's own number would hold:** stage-weighted megawatts (0.65 percent of the 28,254 is under construction or operating; three rows are 80.7 percent), grid draw rather than a mixed basis, and ERCOT's own queue beside the tracker's Texas rows (457 MW stated against 8,927 MW approved to energize: 5.1 percent).
- **Six branches fix words and move no figure (1 to 6); one shows a figure for ruling (7).** No data request: every measure was made from files on this machine. Two things need the key (re-extracting the news table; scoring the unscored months).

## The ground: each file and what it does

| File | What it does |
|---|---|
| `site/app/datacenters/page.tsx` | The page: the lead, two views (facilities, `?view=grids`), the hold's sentence where the facilities would be, the scope and method words (drawn under the hold too), the decisions, the downloads |
| `site/app/datacenters/Body.tsx` | The top block (facilities held, megawatts stated with what the sum counts by status, first reported this week), what changed this week, the bars by state and by operator, the list (`DatacentersTable.tsx`), the citation. Drawn only when the hold allows |
| `site/lib/dctop.ts` | The top block's arithmetic (`topBlock`, `topFigures`, `operatorGroups`): counted, the sums by state, operator (five largest) and status, the week. Pure |
| `site/app/datacenters/Held.tsx` | The hold's one sentence: how many rows, since when, why |
| `site/app/datacenters/LargeLoad.tsx`, `site/lib/largeload.ts`, `site/data/large_load_status.json` | ERCOT's Large Load Interconnection Status Update, the three figures each report states in words (approved to energize, the sum of each load's own peak, the peak of the loads together), the summary sentence, the share observed; beside it the facilities the ERW holds (`facilityCounts`) |
| `site/app/datacenters/Rollups.tsx`, `Timeline.tsx`, `DcCharts.tsx`, `site/lib/dcrollups.ts` | The rollups by grid and by operator, the timeline from first reported to energized, the three charts (planned MW by quarter and grid, operators by MW, the kind of power), and the facilities against each grid (`gridLoads`, `shareOfPeak`) |
| `site/app/datacenters/PowerSide.tsx`, `GridsView.tsx`, `FacilitiesVsGrid.tsx`, `site/lib/datacenter/bygrid.ts` | The queue positions that name a datacenter or a large load (of the queues not held), by grid and zone beside the grid's active queue; what a flat load paid at each load zone (the cost page's `regionCosts`); the facilities against each grid's peak hour, capacity and ERCOT's reserve margin (`site/data/siting/headroom.json`) |
| `site/lib/decisions.ts`, `DATACENTER_TRACKER_DECISIONS` | The 12 decisions at the foot, word for word the method note's section 12 |
| `warehouse/derived/datacenter_facilities.py` | The one table: news facilities (`datacenter_projects`), nine operators' site lists (`datacenter_operator_sites`) and the queue positions the pattern matches (`datacenter_queue_positions`), joined by operator plus place (25 km); MW from the operator's span, else the news; status from the news, else the operator; the grid named, else the queue's, else the state's |
| `warehouse/datacenters/extract.py` | The news extractor: a model reads scored `datacenter_power` stories; every value is checked against the story's title and summary; `same_as` joins a story to a facility already held (the rule of session 166) |
| `warehouse/derived/datacenter_tracker_rollups.py` | The rollups as a warehouse table (operator, else developer); no page reads it |
| `docs/methods/datacenter_tracker.md` ("the method note") and `datacenter_tracker_rollups.md`, `datacenter_facilities.md`, `datacenter_projects.md`, `datacenter_projects_evidence.md`, `datacenter_operator_sites.md` | The tool's note (every view, every key, the decisions, what waits) and the tables' notes |
| `replication/datacenter_tracker/` | `fetch_rows.py` (reads the live set: not run here), `replicate.py`, `replicate.do`, `page_figures.json` of 16 November (454 of 454) |
| The warehouse's CSVs read here, from the main copy, never written | `datacenter_facilities` (458 rows, built 25 November 2026 15:12 UTC), `datacenter_queue_positions` (3 rows, ERCOT's of 23 November), `ercot_interconnection_queue` (3 October 2026), `ercot_large_load_status` (restored 21 October), `news_stories` (26 November), `datacenter_projects_evidence` (read to identify the largest rows; nothing of it copied) |

## How every number here was computed

- **The default view:** `/datacenters` and `/datacenters?view=grids` as drawn on 26 November 2026, the hold in force; and the facility views as they would be drawn without the hold, on the table of 25 November.
- **The independent restatement:** `restate.py` (standard library), written from the method note's sections 3 to 8 and the components' own words. It reads the CSVs as the warehouse writes them, not the live set.
- **The page's own code on the same rows:** `to_rows.py` writes the rows as the live set would serve them (the loader's rule: entity columns, every other column in `extra`, an empty value left out); `site/scripts/datacenter-tracker-figures.mjs` (the replication's own runner of the page's functions) computes every key from them. `compare.py` sets the two side by side.
- **The queues:** both sides read ERCOT's two matched positions of 23 November and the active positions of the queue CSV of 3 October 2026 (1,198 positions, 301,059 MW). The live set's queue is newer (the method note: 1,159 and 308,488 on 16 November), so those two figures are not the live page's to the digit; the rule is.
- **One rule at a time:** `measures.py`; the news window: `window.py` (`news_stories` and `warehouse/datacenters/checked.csv`).
- **The words branches drawn:** `draw_tracker.mjs` draws `page.tsx` whole, both views, with the site's own loaders (`register.mjs`; `brand-stub.mjs` for `components/Brand.tsx`, `table-stub.mjs` for the list's client component), the live set's requests answered from the rows on disk, and draws `Body`, `Rollups`, `Timeline` and `DcCharts` with the rows as the page would without the hold.
- Copies of every script and its printout: `docs/reviews/tracker-model-audit-2026-11-26/` (written to run from `runs/c10211/` of a worktree). The rows themselves are not copied.

## The arithmetic re-done

| Figure | The page's functions | Restated | Gap |
|---|---|---|---|
| Facilities held; counted; no US state stated; cancelled | 458; 274; 180; 4 | the same (274 + 180 + 4 = 458) | 0 |
| Megawatts stated; stated by; state none | 28,254 MW; 21; 253 | the same | 0 |
| By status | planned 21,305, no status 6,766, under construction 108, operating 75 | the same | 0 |
| First reported this week (20 to 26 November); with a first story | 0; 193 | the same | 0 |
| Stated MW by state (14 states) | OH 10,418, UT 9,400, AK 3,000, WV 1,200, KY 1,000, MI 937, GA 674, NV 495, TX 457, CA 400, AR 108, ND 75, SC 50, AL 40 | the same | 0 |
| Top operators by MW | Anthropic 1,000, Switch 882, Applied Digital 75, ThisWay Global 73, ChronoScale 50 (a tie with Nebius, by name) | the same | 0 |
| Beside ERCOT: sites in a US state; in Texas; stating MW; their MW; Texas stating MW, MW; by source | 278; 47; 58; 41,921.9; 4, 457; operator lists 264, news 191, queues 3 | the same | 0 |
| Rollups by grid (counted, MW) | PJM 60, 11,618; ERCOT 46, 457; MISO 16, 937; CAISO 34, 400; SPP 10; NYISO 5; ISO-NE 3; no grid 100, 14,842 | the same, and every operator's | 0 |
| Timeline | 9 rows, all with no grid; median 2 years; by year 2025: 1, 2026: 8 (median 2) | the same | 0 |
| Charts | planned by quarter (2025-Q1 9,400 other; 2026-Q4 PJM 10,400, MISO 700, ERCOT 235, other 678); ten operators; power: none 260 (94.9 percent), gas 8 (2.9), other 4 (1.5), nuclear 1 (0.4), gas on the site 1 (0.4) | the same | 0 |
| Facilities against each grid | ERCOT 46 (4 with MW, planned 235, 0.3 percent of an 83,597 MW peak); PJM 60 (3, 10,400, 6.5 percent of 160,560); MISO 16 (2, 700, 0.6 percent of 120,343); peaks, capacities, ERCOT's reserve margin 11.43 percent | the same | 0 |
| ERCOT's large loads, 12 reports, 28 May 2025 to 19 June 2026 | 36 stated figures and one count of submissions (137, 140,000 MW); newest 8,927 approved, 3,900 observed, 3,675 at one moment; 44 percent; one report that contradicts itself; four months written otherwise | the warehouse's CSV, not the site's copy: the same | 0 |
| The power side and the view by grid | 2 sites (133 and 58.26 MW asked, 191.26 in all); 1,198 active positions, 301,059 MW (the 3 October queue); eight ERCOT zones over November 2025 to October 2026: Houston 34.02, North 34.07, South 34.17, West 35.35 (real time), Rayburn 35.98, LCRA 38.64, CPS 38.99, Austin Energy 39.01 (day-ahead); each zone's complete years 2018 to 2025 | the same | 0 |

- **454 of 454 keys equal** (`compare.out`), to 1e-9 relative (the largest gap 1.2e-15). The four keys of ERCOT's months as written were first missed by the restatement and found by the comparison; the page was right.
- **The published replication** reads the live set (`fetch_rows.py`), which this machine does not call: not run. Its runner of the page's functions is the one used above.
- **What a visitor sees today**, drawn with the site's code: the hold's sentence ("Every row of `datacenter_facilities` is held from 2026-10-21"), ERCOT's section with its figures, the two queue sites and the eight zones, and on the view by grid the queue table, the yearly prices and the grids' peak, capacity and margin, the facility cells "license needed". No em dash in any drawing.

## One rule changed at a time

Each line changes one choice and keeps every other. The base is the table of 25 November: 28,254 MW stated by 21 of 274 counted facilities.

| Choice the page makes | The other choice | Worth | Said on the page? |
|---|---|---|---|
| The known wrong join (one row, 9,400 MW, Utah) stays in every sum until the news table is rebuilt | left out of the sums | 28,254 to 18,854 MW (-33.3 percent); planned 21,305 to 11,905; Utah's bar goes; the planned chart's 2025-Q1 bar goes; the timeline's US rows 3 to 2 | no (finding 1); the method note, section 4 |
| The views by operator read the operator alone | the operator, else the developer (as the warehouse's rollup table does) | the top five operators hold 2,080 MW (7.4 percent of the sum) against 22,082 (78.2 percent); the largest bar 1,000 against 10,400; 13 rows with no operator hold 26,124 MW, 9 of them (20,704 MW) with a developer | yes (decision 9); the operator chart's note says the opposite (finding 4); the owner's item 5 |
| The timeline counts every facility held | the counted ones only (a named US state, not cancelled) | 9 rows to 3; the median 2 years to 3; the year 2026 median (2) goes, 2 rows | no (finding 5) |
| One sum of every basis | grid draw, reading a figure of unstated basis as IT load at the cost page's overhead ratio, 1.56 | +9,998 MW (+35.4 percent): 17,854 MW of the 28,254 is of unstated basis, 10,400 a facility's total | in the decisions (3) and beside the rollups and charts; not beside the headline (finding 3) |
| "Planned" holds announced, applied and permitted | the stage a source states | of the 28,254 MW: announced 21,193, applied 112, no status 6,766, under construction 108, operating 75; under construction or operating 183 MW (0.65 percent) | yes, by status beside the headline; the share of peak adds planned and building (decision 6, the column's note) |
| The share of peak: planned and building MW over the peak hour | the same without the one row that makes it | PJM 6.5 percent to "none stated": its 10,400 MW is one announced facility | "what the facilities state, not what they will draw" |
| The price cell of the view by grid: cheapest and dearest zone, each in its own market | one market for every zone (day-ahead, the only one held for four zones) | the low end USD 34.02 (Houston, real time) to 34.87 (South, day-ahead); the high end 39.01 (Austin Energy, day-ahead) in both | the year chart's note says "real time where held, else day-ahead"; the table's bullet does not (finding 6) |
| ERCOT's "observed running" is the sum of each load's own peak | the peak of the loads together | 43.7 percent of approved against 41.2 | yes: each label says which |
| The news window: every story scored since 2025-01-01 | (not a choice: what was scored) | May to September 2025: 1,885 stories, 13 scored, none sent; October to December 2025 and June to August 2026: 39 to 62 percent scored a month; September to November 2026, the daily feed: 3,371 to 11,914 stories a month against 351 to 656 before. 695 of the 1,076 stories sent (64.6 percent), 136 of the 193 first stories (70.5 percent) and 51 of the 55 news rows that state MW are of September to November 2026 | no (finding 2) |

## Each claim against the code

| Claim, or question | Where | What the code does | Verdict |
|---|---|---|---|
| Announced against built against energized MW | the top block's note, decision 6, the share of peak | One sum of every status; by status beside it as the table has it; "planned" is announced, applied, permitted or Google's development flag; no stage is weighted | **Right as stated**: the split is printed and decision 6 says the megawatts by status are not a measure of what is running. Its size is in the table above |
| IT load against grid draw | the top block, the rollups' and charts' notes, decision 3 | One sum of every basis (`mw_basis`: 20 of the 21 counted rows unstated, one a total) | Rollups and charts **right as stated**; the headline does not say it (**finding 3**) |
| A campus and its phases | the list's phase column | An operator's separately listed sites are never merged; a news row keeps one MW (the campus's or a phase's, as the words give it) | No double count found among the 21 rows that state MW: no two share a state and a county or city. A phase's MW stands for the campus where the story gives only a phase (one row of 222 MW names itself the first phase) |
| One project in two sources | the scope words: "A facility found by several stories, or by the news and an operator's list (same operator and place), is one row" | The builder joins news to an operator's site by operator and place; the extractor joins stories by operator or developer, or site name, or county or city in a state (session 166); a row with no operator and no county is never joined by the builder | The news join rule is misstated, and the one row joined on a state alone before session 166 is in every sum (**finding 1**) |
| A project with no MW | the top block, decision 2 | Counted beside the sum, never added as zero | **Right as stated**: "Stated by 21 of the facilities counted; 253 state no MW" |
| How status and dates are decided, from what evidence | decision 6, "What changed this week" | Status from the news (dated), else the operator's page; only where a source states it; `status_date` empty on every row (checked: 0 of 458); the one date is the first story's | **Right as stated**: "its status date is empty on every row", "a change of status or of megawatts: not held" |
| A "pipeline" total that adds speculative and firm | the headline sum; the share of peak | Adds announced, applied, no status, under construction and operating | Printed with its split, and the share's note says it is not what the facilities will draw: **right as stated**. Three rows are 80.7 percent of it (a utility's statement of one contracted load, the wrong join, a proposal a state is weighing) |
| Internal or licensed rows reaching a public figure | the hold; the downloads; the power side | The facility figures are not drawn under the hold; the downloads say "held: license needed"; the power side reads only the queues not held (ERCOT's, CAISO's, SPP's) | **Right**. Known and the owner's: the map draws the held table's placed rows (the method note, section 13, item 3); the scope words link to it |
| The window and the as-of date | the lead, the scope words, the top block, "Beside it" | "The energy news since 2025-01-01"; the table's vintage is printed beside ERCOT's section, not in the top block; ERCOT's newest report is 19 June 2026 and the pause of 3 August is said | The news window has a five-month hole, and a month since September 2026 holds up to eighteen times the stories of a month before (**finding 2**). ERCOT's dates **right** |
| "Who runs or builds them, where, how many megawatts and how they will be powered" | the lead | `power_kind` for 14 of 274 counted facilities; MW for 21 | **Right in kind**; the charts say "most state none" (94.9 percent) |
| ERCOT: "of the load ERCOT has approved to energize, less than half has been observed running" | ERCOT's section | 3,900 of 8,927 (43.7 percent; 41.2 at one moment) | **Right**; both peaks are labelled |
| "A queue position's megawatts are the generation or storage it asks to connect, not the site's load" | the power side, the view by grid, decision 5 | Never summed with the facilities | **Right**: the 133 MW position is a battery behind the meter, the 58.26 MW one a combined cycle |
| "What a flat load paid at that grid's load zones" | the power side, the view by grid | The cost page's rule: real time where twelve complete months are held, else day-ahead; energy only | **Right** per zone, the market shown a row; the view by grid's range mixes the two markets unsaid (**finding 6**). Four of the eight zones are the territories of municipal utilities and a cooperative (below) |
| The operator chart: "The operator, else the developer" | `DcCharts.tsx` | `operatorMw` reads `rollups(rows, "operator")`, the operator alone | **Finding 4** |
| The timeline: "Only the facilities whose sources state both" | `Timeline.tsx` | Every facility held, of any country and status | **Finding 5** |
| "A news facility is extracted ... by a model, and every value was checked against the text" | the scope words | Each value checked against the story's title and summary; a failing value is left empty | **Right** (`datacenter_projects.md`) |

## What a site-selection lead's or a load forecaster's own number would hold that this does not

| Item | Size | From |
|---|---|---|
| Megawatts weighted by stage (a forecaster counts a signed load or a site under construction, discounts an announcement) | under construction or operating: 183 of 28,254 MW (0.65 percent); announced 21,193 (75.0) | the table's status and `project_status` |
| Grid draw, not a mixed basis | +9,998 MW (+35.4 percent) if the unstated rows are IT load at an overhead ratio of 1.56; nothing if they are totals | `mw_basis`; the cost page's default ratio |
| ERCOT's own queue beside the tracker's Texas rows | the tracker states 457 MW in Texas; ERCOT had approved 8,927 MW to energize (19 June 2026) and received 140,000 MW of new requests (March 2026): the tracker's Texas MW is 5.1 percent of the approved | `ercot_large_load_status` |
| The utilities' own large-load books (contracted load by utility) | not sized: one row of the table is itself a utility's statement of a contracted load; the utilities' books are not a table here | the cross-check note, `docs/methods/crosschecks/datacenter_tracker.md` |
| A news window read evenly | not sized: the unscored months need the key (a scoring run) | `window.py` |
| The price a load in a municipal or cooperative zone pays | not sized: Austin Energy, CPS Energy, LCRA and Rayburn are zones of utilities outside ERCOT's retail choice, where a load buys at its utility's tariff, not at the zone price; the page shows their day-ahead zone price like any other | the zones' names in `site/data/datacenter/index.json` |
| The existing fleet's load (the 264 operator-list sites, 3 of which state MW) | not sized: no MW for most; no floor area held | `datacenter_operator_sites` |
| A load zone or node for a Texas site | not held: the queue names a county; ERCOT's zones are a picture of a map (the page says so) | the power side's note |

## Findings, largest effect first

| # | Severity | Finding | Effect | Fix | Branch |
|---|---|---|---|---|---|
| 1 | Medium | One known wrong join is 9,400 of the 28,254 MW stated and the page never says so; the scope words misstate the news join rule | 33.3 percent of the headline, Utah's bar, the planned chart's only early bar, one of three US timeline rows | words; the figure for ruling | `wip/audit-tracker-1` (`90b505b52`); `wip/audit-tracker-7` (`ebac9af65`) |
| 2 | Medium | "The news since 2025-01-01": no story of May to September 2025 was scored; 70.5 percent of first stories are of the last three months; the planned chart by quarter shows what was read | the chart's quarters are not comparable; not a figure moved | words | `wip/audit-tracker-2` (`9afb8380d`) |
| 3 | Low | The headline megawatts do not say they add every basis; the method note says the page says so beside the sum | +35.4 percent if the unstated figures are IT load | words | `wip/audit-tracker-3` (`9559aa905`) |
| 4 | Low | The operator chart says "the operator, else the developer"; the code reads the operator alone | its largest bar 1,000 MW, where the words promise 10,400 | words | `wip/audit-tracker-4` (`5add2ae58`) |
| 5 | Low | The timeline counts every facility held; 6 of its 9 rows state no US state; the note does not say | median 2 years, 3 on the counted rows | words | `wip/audit-tracker-5` (`302f7ccaa`) |
| 6 | Low | The view by grid's price range sets a real-time zone beside a day-ahead one, unsaid | the low end USD 34.02, or 34.87 in one market | words | `wip/audit-tracker-6` (`cad2f31db`) |

## 1. One known wrong join is a third of the megawatts (Medium)

- **Where.** `site/app/datacenters/page.tsx`, the scope words ("A facility found by several stories, or by the news and an operator's list (same operator and place), is one row with every source linked"); `site/app/datacenters/Body.tsx`, the top block and the line under the bars; `docs/methods/datacenter_facilities.md`, "The news extractor's merge rule"; the method note, section 4.
- **Why it is wrong.** Two stories are joined by the extractor when they name the same operator or developer, the same site, or the same county or city in the same state (since session 166); the builder joins a story to an operator's site by operator and place. "Same operator and place" is neither rule for news joins. Before session 166 a 2025 story of a USD 2 billion Utah datacenter (no operator, no county) was joined to a 2026 story of a proposed 9.4 GW campus in Utah on the state alone; the rule does not split a row already joined, so the row stands until `--reextract`, a model run. It holds 9,400 of the 28,254 MW stated, all of Utah's bar, 9,400 of the 21,305 MW planned, the planned chart's only bar before the fourth quarter of 2026 (2025-Q1, dated by the unrelated 2025 story), and a timeline row of 3 years measured from that story. The method note says so; the page, which a reader meets without the note, does not.
- **The test.** `tests/test_audit_tracker_1.py` on `wip/audit-tracker-1`: through `lib/dctop.ts`, a stateful row that states MW is in the sum whatever its join (passes on main); the words test fails on main.
- **The fix on the branch, words only.** The scope words state the two join rules and say that one row joined on its state alone, before that rule, stays until the news table is rebuilt; the line under the bars (drawn once the hold allows) says the same of the sums. No figure moves.
- **For Samuel's ruling.** Default "left as it is". The other choice: the row's MW left out of every sum until the re-extraction (`wip/audit-tracker-7`, a test only): 18,854 MW (-33.3 percent), planned 11,905. Splitting the row needs the key (`warehouse/datacenters/extract.py --reextract`).

## 2. The news window has a hole (Medium)

- **Where.** `site/app/datacenters/page.tsx`, the lead ("the energy news since 2025-01-01 (the stories the ERW scores)") and the scope words ("Scope: the news since 2025-01-01"); `DcCharts.tsx`, "Planned and building MW, by the quarter first reported and by grid".
- **Why it is wrong.** The extractor reads the scored stories of sector `datacenter_power`. By month of publication (`news_stories`, `warehouse/datacenters/checked.csv`): January to April 2025, every story scored; May to September 2025, 1,885 stories and 13 scored, none sent to the extractor; October to December 2025, 790 of 1,935 scored; January to May 2026, every one; June to August 2026, 863 of 1,819; since September 2026 the daily feed, 3,371 to 11,914 stories a month, against 351 to 656 a month before. So 136 of the 193 facilities with a first story were first reported in September to November 2026, and 51 of the 55 news rows that state MW. "Since 2025-01-01" reads as a window read evenly; the quarter a facility was first reported says as much about which stories were scored as about when it was announced.
- **The test.** `tests/test_audit_tracker_2.py` on `wip/audit-tracker-2`: the words test fails on main; the chart's quarters are read from the first story (`plannedByQuarter`, passes on main).
- **The fix on the branch, words only.** The scope words add that the stories read are not even over that span (none of May to September 2025 scored, part of October to December 2025 and of June to August 2026, and the daily feed since September 2026 many times the earlier months'), as of 26 November 2026; the planned chart's note says its quarters show what was read. No figure moves.
- **Needs the key.** Scoring the unscored months, then the extractor (both model runs).

## 3. The headline megawatts do not say what they measure (Low)

- **Where.** `site/app/datacenters/Body.tsx`, "Megawatts stated" and its note; the method note, section 4 ("A sum adds MW of every basis, and the page says so beside it").
- **Why it is wrong.** Beside the rollups and the charts the page says a sum is "of any basis (IT load, total, a tenant's share, a phase)"; beside the headline sum, the one a reader quotes, it does not. Of the 21 counted rows that state MW, 20 state no basis and one is a facility's total. A forecaster reads a datacenter's MW as IT load and multiplies by an overhead ratio to get the grid's draw; at the cost page's own default ratio (1.56) the 17,854 MW of unstated basis would draw 9,998 MW more.
- **The test.** `tests/test_audit_tracker_3.py` on `wip/audit-tracker-3`: the sum adds a total and an unstated row alike (passes on main); the words test fails on main.
- **The fix on the branch, words only.** The note beside the headline adds "A sum of any basis: IT load, a facility's total, a tenant's share or a phase, and for most a figure whose basis the words do not say." No figure moves.

## 4. The operator chart names a rule the code does not use (Low)

- **Where.** `site/app/datacenters/DcCharts.tsx`, the note of "The operators with the most MW stated" ("The operator, else the developer"); `site/lib/dcrollups.ts`, `operatorMw` (reads `rollups(rows, "operator")`, `operatorOf` the operator alone); decision 9.
- **Why it is wrong.** Decision 9 says the views by operator read the operator alone, and the warehouse's rollup table is the one that falls back to the developer. The chart's note says the opposite. With the fallback the chart's largest bar would be 10,400 MW, not 1,000, and the top five would hold 78.2 percent of the MW stated, not 7.4.
- **The test.** `tests/test_audit_tracker_4.py` on `wip/audit-tracker-4`: through `lib/dcrollups.ts`, a row with a developer and no operator is not on the chart (passes on main); the words test fails on main.
- **The fix on the branch, words only.** The note reads "The operator a source names, as every view by operator reads it; a facility whose sources name only a developer is not here (decision 9); the MW its counted facilities state." Whether the views should read the developer is the owner's item 5.

## 5. The timeline counts what no other section counts (Low)

- **Where.** `site/app/datacenters/Timeline.tsx`, the note; `site/lib/dcrollups.ts`, `timeline` (every row, no `counted` filter); the method note, section 7.6 ("Every facility held").
- **Why it matters.** Every other section of the page counts "the facilities in a named US state and not cancelled", and says so. The timeline counts every facility held and does not say so: 6 of its 9 rows state no US state (sites abroad among them). On the counted rows the median wait is 3 years, not 2, and the year 2026 has two rows, no median.
- **The test.** `tests/test_audit_tracker_5.py` on `wip/audit-tracker-5`: through `lib/dcrollups.ts`, a row with no state and a cancelled row are on the timeline (passes on main); the words test fails on main.
- **The fix on the branch, words only.** The note adds "Unlike the sums above, it counts every facility held, those with no US state stated and the cancelled among them." The other choice, the counted rows only (median 3, 3 rows), is a figure: for Samuel's ruling, default "left as it is".

## 6. The view by grid's price range mixes markets (Low)

- **Where.** `site/app/datacenters/GridsView.tsx`, the bullet "The price is the cheapest and the dearest load zone ... at the calculator's defaults, over its last twelve complete months. Energy only."; `zoneCosts` (the cost page's `regionCosts`).
- **Why it matters.** The calculator's default buys in real time where twelve complete months of real-time prices are held, else day-ahead. No real-time price is held for four of ERCOT's eight zones (Austin Energy, CPS Energy, LCRA, Rayburn), so the range sets Houston's real-time USD 34.02 beside Austin Energy's day-ahead 39.01. Day-ahead ran above real time at every zone holding both (by 0.70 to 1.90 per MWh), so part of the spread is the market, not the place. In one market the low end is South's 34.87. The table under the power side shows each zone's market; the bullet of the view by grid does not.
- **The test.** `tests/test_audit_tracker_6.py` on `wip/audit-tracker-6`: through `lib/datacenter.ts` on the page's files, the cheapest ERCOT zone is bought in real time and the dearest in day-ahead (passes on main); the words test fails on main.
- **The fix on the branch, words only.** The bullet adds "Each zone is in its own market, real time where twelve complete months are held, else day-ahead, so the two ends can be in different markets; the power side of the facilities view names each zone's market." No figure moves.

## The words branches drawn and read

Each branch's page was drawn to HTML with the site's own code (`draw_tracker.mjs`: `page.tsx` whole, both views, as a visitor meets it under the hold, and `Body`, `Rollups`, `Timeline` and `DcCharts` with the table's rows as the page draws them once the hold allows), and its new sentences read in the drawn text. No em dash in any drawing.

| Branch | Where the words are drawn | Read |
|---|---|---|
| `wip/audit-tracker-1` | the scope words (both under the hold and without it); the line under the bars | pass: "Stories are one facility when they name the same operator or developer, the same site, or the same county or city in a state; a story and an operator's list are one when they share an operator and a place." and "One row was joined from two stories on their state alone, before that rule, and stays as it is until the news table is rebuilt." between "blank." and "Placed facilities"; under the bars, "One facility joined from two stories on their state alone ... (the tracker's method note, section 4)." after "so it is never summed." |
| `wip/audit-tracker-2` | the scope words; the planned chart's note | pass: the sentence follows "This is not a census of every facility."; the chart's note ends "(the scope, above the list)." |
| `wip/audit-tracker-3` | the headline megawatts' note | pass: "A sum of any basis: ..." between "253 state no MW." and "By status, as the table has it:" |
| `wip/audit-tracker-4` | the operator chart's note | pass: "The operator a source names, as every view by operator reads it; a facility whose sources name only a developer is not here (decision 9); the MW its counted facilities state." |
| `wip/audit-tracker-5` | the timeline's note | pass: the sentence follows "A median needs three facilities with both." |
| `wip/audit-tracker-6` | the view by grid, the bullet on the price | pass: the sentence follows "Energy only." |
| the six merged (a local trial, not pushed) | both views and the facility components | pass: all nine new sentences drawn |

- The six words branches merge together onto origin/main of 26 November (`c868c6418`) with no conflict. Their tests with every test file that reads the changed files (`test_session105`, `106`, `167`, `203`, `240`, `241c`, `329`, `421`, `467`, `468`, `497`, `500`, `1855`, `2201`, `2243_deals` to `2246_deals`, `7400_trackers`, `7402_trackers`, `land461_whole_mw`) pass on the merge: 175 passed, 5 skipped. On origin/main each branch's words test fails (6 failed) and each behaviour test passes (7 passed).

## The decisions block, line by line

1. A sum counts a named US state, not cancelled: **right**; the timeline does not follow it (finding 5).
2. Megawatts only as stated, never zero, never estimated: **right**.
3. One sum of every basis: **right as stated**; not beside the headline (finding 3).
4. One number where the words give a range: **right as stated** (the method note's word search: 8 of 55 put "to" before the figure).
5. A queue position's MW never summed with the facilities: **right**.
6. A status only where a source states it: **right as stated**; Google's development flag is read as planned (21 rows).
7. The grid named, else the queue's, else the state's: **right as stated**; no story names a grid today (175 rows by state, 3 by queue, 280 none).
8. Two rows one facility by operator and place, 25 km: **right** for the builder; the news joins follow the extractor's rule (finding 1).
9. The views by operator read the operator: **right**; the operator chart says otherwise (finding 4).
10. ERCOT's figures as stated in words: **right**.
11. The wait as a difference of years, a median from three: **right as stated**; of which rows, finding 5.
12. Held whole from 21 October 2026: **right**.

## Not covered, or left open

- **The live set's rows.** The CSV of 25 November was read, not the live set (no request to any service). The rule is restated to the digit; the live page's figures move with the table every day.
- **The map's datacenter layer** draws the held table's placed rows: the owner's item 3, not restated here.
- **The list's rows** (each facility's own fields) are the table's rows: not restated, as the replication does not.
- **`grid_peak_vs_capacity`** (each grid's peak and capacity, `site/data/siting/headroom.json`): its figures are restated as the page reads them; the table's own method was not audited.
- **"253 state no MW"** in the top block's note is printed without a check key (a bare number in `Body.tsx`), so the site's value check does not read it; it equals the restatement. Not a branch: it moves no figure and changes no word.
- **The pages in a browser**: drawn to HTML with the site's own code; no layout, no width of 390 px.

## Landing, rulings and data (returned to the chain's main session)

- **For landing (words only):** `wip/audit-tracker-1` (`90b505b52`), `-2` (`9afb8380d`), `-3` (`9559aa905`), `-4` (`5add2ae58`), `-5` (`302f7ccaa`), `-6` (`cad2f31db`). They merge together cleanly onto origin/main of 26 November; each was drawn and read (pass). The page's figures do not move.
- **For Samuel's ruling, default "left as it is":**
  - Finding 1, `wip/audit-tracker-7` (`ebac9af65`), not for landing: the one row joined on a state alone is left out of every sum until the news table is rebuilt; the megawatts stated 28,254 to 18,854 (-33.3 percent), planned 21,305 to 11,905, Utah's bar and the planned chart's 2025 bar gone. No visitor sees it today (the hold).
  - Finding 5, no branch (the measure is in `measures.json`): the timeline counts only the facilities the sums count; 9 rows to 3, the median wait 2 years to 3.
- **Data requests:** none. Every measure was made from the files on this machine.
- **Needs the key:** `warehouse/datacenters/extract.py --reextract` (a model run) to split the old join; scoring the stories of May to September 2025 and the rest of October to December 2025 and June to August 2026, then the extractor, to make the news window even.
