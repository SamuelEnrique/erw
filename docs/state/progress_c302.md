# Progress of chain 302: the large-load rules on the site (sessions 7200 to 7249, samueloldlaptop)

Energy Research Warehouse (ERW). The chain file: `queue/done/302-day-16-november-oldlaptop-large-load-on-the-site.md`. One line a step, with its state and the session. This file and the landing request rows are on main; the work is on two branches, each with its worktree beside the main copy. Model spend: USD 0 (rule 1).

States: `done` with the commit, `needs the key` with the cost, `ruling` with the default taken, `waiting` with what for, `open`.

| Branch | Worktree | Holds | Landing request row |
|---|---|---|---|
| `wip/7200-large-load` | `erw-7200` | goal 1 (and goal 4's fixes, stacked on it) | 15 |
| `wip/7202-key-refusal` | `erw-7202` | goal 3 | 16 |

## The ground

| Step | State | Session |
|---|---|---|
| Precheck, fetch, memory and disk | done (7200; again by 7201: precheck passed, 2.0 GB of memory free, 86 GB of disk) | 7200, 7201 |
| 284 and 300 parked in `queue/parked/` | done `57cc612a9` | 7200 |
| The resume file `queue/next/320-resume-chain-302.md` | done `9df728c03`; taken by session 7201 after an interruption, written again as 321 at `6d8d5a24f` | 7200, 7201 |
| This progress file | done `e83dd0e06` | 7201 |

## Goal 1: the large-load rules on the site

| Step | State | Session |
|---|---|---|
| The reader's questions (`docs/reviews/large-load-on-site/questions.md`) | done `eb8f17b87` | 7200 |
| The builder and the page file (`warehouse/derived/large_load_rules_page.py`, `site/data/siting/large_load_rules.json`) | done `eb8f17b87` | 7200 |
| The page file's tests (7 pass) | done `b55127e4f`: session 7200 left the file uncommitted with two failures; both corrected | 7201 |
| The library of the section (`site/lib/largeloadrules.ts`), 83 Node checks | done `be2c8422f`, `44503fdfc` | 7201 |
| On the tab: the Utility cell and the Time to connect cell open the utility's rule | done `be2c8422f`, `b121c1559`: of 48 rows, 21 open a utility's rule, 10 the state's rule alone, 6 say no rule found, 11 no rule read | 7201 |
| Under the tab: "Large-load rules by utility", sortable, filtered, A and B, downloads | done `be2c8422f`, `b273d37da` | 7201 |
| "What changed in the last 90 days" | done `be2c8422f` | 7201 |
| On `/policy`: the state laws in the monitor | done `44503fdfc` | 7201 |
| Internal rows and fields drawn blank with "license needed", counted in a test | done `b273d37da`: 228 blank cells in the rules table, 16 in the changes, 4 in the laws, counted in the drawn HTML; 251 held values searched for, none found | 7201 |
| The data's route | done: built on this machine from the tables as chain 267 wrote them; `docs/state/data_requests_large_load.md` rows 18 (the live set) and 19 (the file's rebuild), requested, at `1db286b6f` | 7201 |
| `check-values` entries | done `44503fdfc` (the `largeload|` keys and two pages in its list; each count is also held to the file by the render test) | 7201 |
| The hover and A and B exercised in a browser; 390 and 1280 read; axe | waiting: a site build, which this machine may make only with 2.5 GB of memory free (2.0 GB at most on 16 November). Stood in for by the components drawn to HTML without a build (52 checks: every tip with its target, every button named, A and B drawn, the filters set from the address). Asked of the desk's gate in landing row 15 | 7201 |
| The method notes (`docs/methods/siting.md` version 13, `docs/methods/large_load_research.md`) | done `bb02fffdb` | 7201 |
| The chat over the warehouse and the three tables | needs the key: about USD 4.80 to ask the 58 questions written for them (58 at about USD 0.082). Known without it: the three tables are not in the live set, and on 15 November the site's chat refused all 58 rightly, by the table's name | 7201 |
| The landing request row | done: row 15 (`46350007a`), moved to the stack's final head `d192de75c` by the last session; without screenshots (they wait for the build) | 7201, 7204 |
| The report | done `63affd96d` (`archive/sessions/SESSION_7201_REPORT.md`, on the branch) | 7201 |

## Goal 2: the site side of the data machine's fixes

| Step | State | Session |
|---|---|---|
| `docs/state/data_ready_c301.md` read at the start of each session | done: the file does not exist on origin/main (read at `6d8d5a24f` by 7201, at `1db286b6f` by 7202, at `c275c702f` by 7203 and at `f6b80e815` by 7204): nothing to do | 7201 to 7204 |

## Goal 3: the scheduled model steps fail soft when the key refuses

| Step | State | Session |
|---|---|---|
| The refusal known once in the shared client; no further call, no retry | done `65b730b5f` | 7202 |
| Every scheduled model step ends as skipped, one row of `erw_health` with "the key's limit" and the date access returns | done `59a4d5acc` | 7202 |
| No Digest and no Roundup on a day the scoring was refused | done `59a4d5acc` | 7202 |
| Tests with a stubbed client (21); the touched test files (131 files, 2,530 tests, all pass) | done `dbdbbe72e` | 7202 |
| The method note (`docs/methods/api_cost_ledger.md`) and the report | done `19af50579`, `b793f3c7f` | 7202 |
| The landing request row | done: row 16 (`46350007a`), head `b793f3c7f`; it does not depend on row 15 and should land first | 7202 |
| Whether a day under the key's limit sends the owner one line | ruling: default, nothing is sent | 7202 |

## Goal 4: the All grids tab read as the reader it is for

| Step | State | Session |
|---|---|---|
| Five cases read on the tab (`docs/reviews/allgrids-read-2026-11-16.md`, 17 rows) | done `1c92bffad`: read from the tab drawn to HTML (no build); only ERCOT West has rows of its own | 7203 |
| The site faults fixed, each with a test (6 rows) | done `05504493d` (25 checks on the drawn tab) | 7203 |
| The data faults asked of the data machine | done: `docs/state/data_requests_large_load.md` rows 20 to 25 (`c275c702f`), requested | 7203 |
| What only a license or a ruling closes | ruling: PJM's prices stay "license needed"; the all-in's transmission part stays the Commission's rate; Evergy Kansas South is not matched | 7203 |
| The same five on `/cost-of-power` | done `05504493d`: "Your load" run through its own model: the flat price agrees with the tab in both markets for both ERCOT West rows; it holds no PJM and nothing outside the seven grids | 7203 |
| "Your load"'s four-peak block and its three answers against the tab | waiting: they read the live set, which a worktree with no build does not reach; the value checker holds each to its own source at the gate | 7203 |
| The five bullets on what a lab's reader still cannot get | done `2763f4c50` (the review and `archive/sessions/SESSION_7203_REPORT.md`) | 7203 |

## After goal 4: the policy monitor read as a regulator's staffer

| Step | State | Session |
|---|---|---|
| Texas, Virginia, Arizona, Ohio, Georgia (`docs/reviews/policy-read-2026-11-16.md`, 11 rows) | done `fe1e78b75` | 7204 |
| The next five by the megawatts the tracker holds: Utah, Alaska, West Virginia, Kentucky, Michigan | done `fe1e78b75` (in the same review) | 7204 |
| The site faults fixed, each with a test (5 rows) | done `51ebc79cf`, `078c0ce84`, `fe1e78b75` | 7204 |
| The data faults asked of the data machine | done: rows 26 to 29 (`f6b80e815`), requested | 7204 |
| PJM-wide records under a state; Michigan's row | ruling: both left as they are | 7204 |

## The last session

| Step | State | Session |
|---|---|---|
| The progress file complete | done (this commit) | 7204 |
| The note `docs/state/note_2026-11-17_oldlaptop_c302.md` | done (this commit) | 7204 |
| The landing request row for the final stack | done (this commit): row 15 at `d192de75c`; the last sweep, 190 test files and 2,130 tests, all pass but `tests/test_session705.py`, which fails on clean main too | 7204 |
| The resume file removed from `queue/next/` | done in the commit after this one | 7204 |
| The queue step | done after it; its answer is in the commit's message that follows | 7204 |
