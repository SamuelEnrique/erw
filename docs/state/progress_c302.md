# Progress of chain 302: the large-load rules on the site (sessions 7200 to 7249, samueloldlaptop)

Energy Research Warehouse (ERW). The chain file: `queue/done/302-day-16-november-oldlaptop-large-load-on-the-site.md`. One line a step, with its state and the session. The work is on `wip/7200-large-load` (worktree `C:\Users\lossa\Documents\erw-7200`); this file and the landing request rows are on main. Model spend: USD 0 (rule 1).

States: `done` with the commit, `needs the key` with the cost, `ruling` with the default taken, `waiting` with what for, `open`.

## The ground

| Step | State | Session |
|---|---|---|
| Precheck, fetch, memory and disk | done (session 7200; again by 7201: precheck passed, 2.0 GB of memory free, 86 GB of disk) | 7200, 7201 |
| 284 and 300 parked in `queue/parked/` | done `57cc612a9` | 7200 |
| The resume file `queue/next/320-resume-chain-302.md` | done `9df728c03`; taken by session 7201 after an interruption, written again as 321 at `6d8d5a24f` | 7200, 7201 |
| This progress file | done (this commit) | 7201 |

## Goal 1: the large-load rules on the site

| Step | State | Session |
|---|---|---|
| The reader's questions (`docs/reviews/large-load-on-site/questions.md`) | done `eb8f17b87` (on the branch) | 7200 |
| The builder and the page file (`warehouse/derived/large_load_rules_page.py`, `site/data/siting/large_load_rules.json`) | done `eb8f17b87` | 7200 |
| The page file's tests (`tests/test_session7200_large_load_rules_page.py`, 7 pass) | done `b55127e4f`: session 7200 left the file uncommitted with two failures (the table's own stamp, and a held row's words a public row also prints); both corrected | 7201 |
| The library of the section (`site/lib/largeloadrules.ts`) with its tests | open | |
| On the tab: the Utility cell and the Time to connect cell open the utility's rule | open | |
| Under the tab: "Large-load rules by utility", sortable, filtered, A and B, downloads | open | |
| "What changed in the last 90 days" | open | |
| On `/policy`: the state laws in the monitor | open | |
| Internal rows and fields drawn blank with "license needed", counted in a test | open | |
| The data's route: a row in `docs/state/data_requests_large_load.md` (the three tables into the live set) | open | |
| `check-values` entries, hover and A and B exercised, 390 and 1280 read, axe | open | |
| The method notes | open | |
| The chat over the warehouse and the three tables | needs the key (written in the report when goal 1 closes) | |
| The landing request row with its screenshots | open | |

## Goal 2: the site side of the data machine's fixes

| Step | State | Session |
|---|---|---|
| `docs/state/data_ready_c301.md` read at the start of the session | done: the file does not exist on origin/main at `6d8d5a24f` (nothing to do) | 7201 |

## Goal 3: the scheduled model steps fail soft when the key refuses

| Step | State | Session |
|---|---|---|
| The key's usage-limit refusal ends a scheduled model step as skipped; no issue on a day the scoring was refused; tests with a stubbed client | open | |

## Goal 4: the All grids tab read as the reader it is for

| Step | State | Session |
|---|---|---|
| Five cases read on the tab (`docs/reviews/allgrids-read-2026-11-16.md`) | open | |
| The same five on `/cost-of-power` | open | |

## The last session

| Step | State | Session |
|---|---|---|
| The note `docs/state/note_2026-11-17_oldlaptop_c302.md`, the final landing row, the resume file removed, the queue step | open | |
