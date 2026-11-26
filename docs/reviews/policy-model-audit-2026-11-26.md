# The policy and regulatory monitor: the model audited as a hostile expert would

Session 10217, 26 November 2026, chain 710 (part D), the old laptop. Read as a regulatory affairs lead at a developer or an AI lab, who would use `/policy` to know what binds a project and when, and as a state utility commission analyst, who would set its records beside the dockets. In the form of `docs/reviews/tracker-model-audit-2026-11-26.md`.

- Nothing changed on main but this file and its folder of evidence (`docs/reviews/policy-model-audit-2026-11-26/`). No table written, no lock taken, no default moved, no model called, no request to any service or host.
- Each finding's test is on its own branch, `wip/audit-policy-<n>`. Branches that change only words are for landing (the rows at the foot), and the six merge as `wip/audit-policy-words`; a branch whose fix would move a figure carries the test only and is not for landing.
- **Which view is "the default".** `/policy` as it opens is the first view, "Every action, scored": it reads `policy_actions` from the live set, which is held whole ("license needed" from 2026-10-21, the PUCT's news releases), so it draws the heading, the views and "license needed", and no figure. The week view reads the same held table for its actions and draws only the dockets of `site/data/policy/state_rules.json`. The view that prints figures is the monitor, `/policy?view=monitor`, drawn from `site/data/policy/monitor.json` and `site/data/siting/large_load_rules.json`. That view as it opens (significance 5 or more, any date, no state) on 26 November 2026 is the default audited here; the week view's dockets are restated too.
- Not repeated: the policy audits of 6 November (`policy-audit-2026-11-06*.md`, the fields against 240 documents), the faults read of 11 November (`policy-faults-2026-11-11.md`), the read of 16 November (`policy-read-2026-11-16.md`) and the rulings' alternatives and impacts of 17 November. They are cited where they bear.

## In short

- **The arithmetic is right.** An independent restatement written from the method note and the page's own hovers, not from its code, gives the monitor's figures from the page's own files to the digit: 534 of 538 keys equal to the page's functions run on the same files (295 shown of 1,568 records held; every count of the six filters; the calendar's 23 steps of the month ahead and 94 hidden; the first 50 rows with their next step and figure; the three charts; the laws block's 27 and 1 held, by status; the paused line; the week view's 3 dockets). The four that differ are all the calendar's week, which is eight days, not the seven its hover said (finding 4).
- **The monitor draws a table held whole (finding 1, Medium).** `policy_actions` is held "license needed" because it carries the PUCT's releases; the first view honours the hold, the monitor reads the same rows from its site file with no gate: 37 records are the PUCT's own pages (11 shown as it opens, 9 with a figure). Already line 1 of the rulings of 17 November; a test on `wip/audit-policy-7`.
- **The large-load orders that matter most left the monitor on 20 November (finding 2, Medium).** The fifteen orders and steps of FERC and the grid operators (PJM's large-load definition ER26-3515, SPP's CHILLS ER26-1323, ERCOT's Batch Zero, the show-cause dockets) are read only from `utility_large_load_rule_changes`; the daily run's file of 20 November dropped them and the note still says they join twelve records. Restored, they add 15 documents and 10 records, and none would show as the view opens, because they are never scored (finding 3). A data request.
- **Records with no score are hidden as the view opens, and the hover said otherwise (finding 3).** 56 records hold no score (44 of November); 18 of the 94 hidden steps are theirs, while the hover said "scored below significance 5". Fixed in words; opening on them too (295 to 351) is for ruling.
- **Smaller, each fixed in words.** The past week is eight calendar days, not seven (6 records, not 4; finding 4). "Changes in the last 90 days" counts every change of a file that ends on 13 November (Texas 13, against 10 in the 90 days to 26 November; finding 5). A status is its newest document's and a final rule stays "Final" after its effective date (96 of 126), while the note said it becomes effective (finding 6). The note says the charts sum MW and USD; they show the largest of each unit (finding 7). Three "enacted" laws print in their own cite a day they took effect before they were read (finding 8).
- **What an expert would hold that this does not:** the state commissions' own dockets as records (120 held for the week view, none in the monitor), FERC's orders that never reach the Register, the operators' stakeholder decisions, courts and Congress, and a status as of today. Sized below where the files allow.
- **Six branches fix words and move no figure (1 to 6, merged as `wip/audit-policy-words`); five show a figure for ruling or data (7 to 11).** Two data requests. Nothing needs the key.

## The ground: each file and what it does

| File | What it does |
|---|---|
| `site/app/policy/page.tsx` | The page and its three views by address: the first view (the live set's `policy_actions` and `policy_reads`, through the license gate: held, so "license needed"), the week view, and the monitor (`?view=monitor`), drawn from `data/policy/monitor.json` and `data/siting/large_load_rules.json` with no gate; the paused line; `countByState` of the utilities' rules and their changes for the laws block |
| `site/app/policy/MonitorView.tsx` | The monitor: six filters with counts, dates, the significance floor (opens at 5), the count line, the table (50 rows a page, a sort on every column, a row opens to its proceeding, history and sources), the CSV with its Python and Stata readers; draws the calendar, the charts and the laws |
| `site/app/policy/MonitorCalendar.tsx` | The past week's records and the month ahead's dated steps of the records the filters leave, with the count the floor hides and a click that lifts it |
| `site/app/policy/MonitorCharts.tsx` | Records by month and body (six bodies and "Other"), by sector and band of significance (twelve sectors), and the figures stated by month: the largest of each unit, no sum |
| `site/app/policy/StateLaws.tsx` | The states' laws on large loads (`state_large_load_laws`): counts by status, the table, the states searched with no row, and with a state chosen the link to that state's utilities' rules "(N changes in the last 90 days)" |
| `site/app/policy/WeekView.tsx`, `site/lib/policyweek.ts`, `site/lib/policyweekdata.ts`, `site/lib/rules.ts` | The week view: the live set's actions of 7 and 30 days (held) and the dockets of `state_rules.json`; the paused line's words and marks (`pausedLine`) |
| `site/app/policy/Paused.tsx` | The line "2 sources paused: MISO, paused since 4 Oct 2026; Virginia SCC, paused since 10 Oct 2026", from `data/policy/paused.json` (built from `warehouse/metadata/paused_sources.csv`) |
| `site/app/policy/PolicyTable.tsx`, `site/lib/policyreads.ts` | The first view's table and each read's citation line; not drawn while the table is held |
| `site/lib/policymonitor.ts` | The monitor's arithmetic: `filterRows`, `options`, `sortRows`, `calendarOf`, `floorHidden`, `nextOf`, `figureText`, `byBodyMonth`, `sigBySector`, `figureMonths`, `toCsv`; pure, counts and orders only |
| `site/lib/largeloadrules.ts` | The laws' and rules' words (`LAW_STATUS_TIP`, `STATUS_TIP`), `statesOf`, `lawSearchOf`, the CSVs, `largeLoadStat` |
| `warehouse/policy/monitor_site.py` | Writes `monitor.json` daily (soft step `policy_monitor_records`, never fewer records than held) from `policy_actions`, `policy_reads`, `impact_reads.csv` and, when present, the fifteen rows of `utility_large_load_rule_changes` (group `operators_federal`) |
| `warehouse/policy/records.py` | One record a proceeding: documents joined by a proceeding id (FERC docket without its sub-number, hydro project, NRC docket ID, agency docket, RIN, DOE LNG docket, OSMRE amendment), a same-day RIN split, a repeat of one body's title within 45 days; status, date and title the newest document's, significance the highest |
| `warehouse/policy/fields.py` | Body, instrument, status (as of the document's date), every dated step with its words, the next step, the figure with its words, by written rules; no model |
| `warehouse/connectors/policy_sources.py`, `warehouse/policy/score.py`, `reads.py`, `impact.py` | The Federal Register and four news pages; the significance score (the news rubric, a model's); the reads and the impact sentence (a model's, kept only where its words stand in the text) |
| `warehouse/derived/large_load_rules_page.py` | Writes `large_load_rules.json` from the three large-load tables (rules 100 public and 22 held; changes 94 and 4; laws 27 and 1) and the research's searches |
| `docs/methods/policy_monitor.md` ("the note"), `policy_action_tags.md`, `large_load_research.md`, `vascc_pause.md`, `miso_pause.md` | The method, sections 1 to 18 |
| The page's files read here | `monitor.json` (built 2026-11-25: 2,127 documents, 1,568 records, newest document 2026-11-25), `large_load_rules.json` (built 2026-11-16 17:10 UTC from tables retrieved 2026-11-16; laws read 13 and 14 November), `state_rules.json` (built 2026-11-12 22:45 UTC), `paused.json`, `refresh.json`, `grids.json`, `tag_rules.json`, `license_status.json` |
| The warehouse's CSVs read here, from the main copy, never written | `policy_actions` (2,057 rows to 2026-11-13), `policy_reads` (412), `utility_large_load_rule_changes` (94), `state_large_load_laws` (27), `utility_large_load_rules` (100): for the two trial builds only |

## How every number here was computed

- **The page's own functions:** `page_figures.mjs` imports `lib/policymonitor.ts`, `lib/largeloadrules.ts` and `lib/policyweek.ts` with the site's loaders and computes every figure the monitor prints as it opens on 26 November 2026, and the week view's docket rows, from the page's files.
- **The independent restatement:** `restate.py` (standard library), written from the note and the hovers' words. Where the words leave a rule open it takes the plainest reading and names it at its top ("the seven days to", "the last 90 days" counted to the page's day), so a difference is a difference between the words and the code. `compare.py` sets the two side by side: `compare.out`.
- **One rule at a time and the claims:** `measures.py`, `measures2.py` on the same files.
- **The fifteen large-load orders:** the builder itself (`warehouse/policy/monitor_site.py --in-dir ... --out runs/...`, a trial) run twice on the main copy's tables of 13 and 14 November, with and without `utility_large_load_rule_changes.csv` (`trial.out`, `trial_compare.py`, `trial_compare.out`). Those tables are older than the file of 25 November, so the trial measures what the fifteen add, not the live file's counts.
- **The words branches drawn:** `draw_policy.mjs` draws `MonitorView` whole (filters, calendar, table, charts, laws) with the site's own code, as it opens and with Texas chosen; `draw_note.mjs` draws the note with `lib/markdown.ts` as `/data/methods/policy_monitor` does; `read_words.py` looks for each new sentence in the drawn text.
- Copies of every script and its printout: `docs/reviews/policy-model-audit-2026-11-26/` (written to run from `runs/c10217/` of a worktree).

## The arithmetic re-done

| Figure, as the monitor opens on 26 November 2026 | The page's functions | Restated | Gap |
|---|---|---|---|
| The count line | 295 shown of 1,568 records held | the same | 0 |
| Body filter | FERC 97, NRC 83, DOE 49, EPA 18, BLM 17, BOEM 11, Texas Governor 9, CPUC 2, Interior 2, PUCT 2, BSEE, FWS, IRS, OSMRE, USGS 1 each, BIA 0, NPS 0 | the same, in the same order | 0 |
| Status filter | Issued 81, Announced 55, Filed 48, Scheduled 32, Proposed 27, Final 26, Open for comment 20, In effect 5, Withdrawn 1 | the same | 0 |
| Instrument filter | Environmental review 83, Application 47, Announcement 44, Proposed rule 24, Notice 23, Final rule 18, Order 15, Meeting 13, Award 11, Lease sale 11, Approval 2, Complaint 2, Decision 1, Guidance 1 | the same | 0 |
| Sector, grid and state filters | 18 sectors (Nuclear 71, Policy 67, Gas 55 ...); grids ERCOT 19, PJM 14, SPP 4, CAISO 3, MISO 3, NYISO 2, ISO-NE 1; 50 states (Texas 45, Louisiana 26, Alaska 17 ... five at 0) | the same | 0 |
| The calendar: the file's last week | 2026-11-18 to 2026-11-25, 6 records | **2026-11-19 to 2026-11-25, 4 records** ("the seven days to") | **2 (finding 4)** |
| The calendar: the month ahead | 2026-11-26 to 2026-12-26, 23 steps; 94 more below significance 5 | the same, each step's date, kind, record and document | 0 |
| The table | the first 50 rows (date, body, instrument, action, status, sector, significance, next step, figure, documents); over the 295: next step ahead 53, passed 143, none 99; 89 with a figure | the same | 0 |
| Records by month and body | 14 months, the last "2026-11 to the 25th"; FERC, NRC, DOE, EPA, BLM, CPUC and Other, month by month | the same | 0 |
| Records by sector and band | 12 sectors; 0 to 4, 5 to 6, 7 to 10 | the same | 0 |
| The figures by month | 60 month and unit cells, each count, largest and record (USD 18 billion, December 2025; 14,750 MW, May 2026 ...) | the same | 0 |
| The states' laws | 27 laws and bills: in effect 10, enacted 6, passed 3, passed one chamber 3, introduced 3, vetoed 1, died 1; 1 held; 28 of 28 shown and 1 read and not shown; 22 states searched with no row; 26 states with a row; each law's state, bill, status, date, effective date, smallest load and topics | the same | 0 |
| A chosen state's rules and changes | rules by state (Texas 11, Virginia 8, Washington 8 ...); changes by state (Pennsylvania 16, Texas 13, Florida 8 ...) | rules the same; changes the same counted over the file; **counted over the 90 days to the page's day, 14 of 94 fall out** | **finding 5** |
| The paused line | "2 sources paused: MISO, paused since 4 Oct 2026; Virginia SCC, paused since 10 Oct 2026" | the same | 0 |
| The week view's dockets | 7 days (from 2026-11-19): 0; 30 days (from 2026-10-27): 3 (Texas PUC 2, Pennsylvania PUC 1), none dropped | the same | 0 |

- **534 of 538 keys equal** (`compare.out`); the other four are the week's: its first day, its count and its two rows of 18 November, which only the page draws. The restatement's 30 keys of "the last 90 days" counted to the page's day have no page key: the page counts the whole file.
- **What a visitor sees today:** every page is in review. `/policy` as it opens draws "license needed" and no figure; the monitor draws the figures above. No em dash in any drawing.
- **The published replication** (`replication/policy/replicate.py`) rebuilds `monitor.json` from `policy_actions`; the main copy's table (13 November) is older than the file (25 November), so it was not run. The builder's trial builds stand in for the one question it bears on (finding 2).

## One rule changed at a time

Each line changes one choice and keeps every other. The base is `monitor.json` of 25 November, read on 26 November: 295 shown of 1,568.

| Choice the page makes | The other choice | Worth | Said on the page? |
|---|---|---|---|
| The past week runs from seven days before its last day to that day, both counted | seven calendar days | 6 records to 4 (-33 percent); over the thirty page days to 26 November, 1.2 records more on average, on 20 of 30 days, up to 4 | the dates are printed; the hover said "the seven days to" (finding 4) |
| The view opens at significance 5 or more; a record with no score is below every floor | a record with no score shown too | 295 to 351 (+56, +19.0 percent); the month ahead's hidden steps 94, 18 of them on records with no score | the Reset's hover named the floor alone; the lift's hover said "scored below" (finding 3) |
| A status is the newest document's, as of its date | as of the page's day | Final 126 to 30, In effect 70 to 166; as it opens Final 26 to 12, In effect 5 to 19 | yes: "as of its newest document" in the column's and the filter's hovers; the note said the opposite (finding 6) |
| Proposed and open-for-comment records keep that status after their comment dates | "Comments closed" after the last comment date | 133 of 175 have every comment date behind the page's day (35 as it opens) | asked of the data machine on 16 November (`docs/state/data_ready_c301.md`, row 7) |
| The laws block's change counts are of the whole file (18 August to 13 November) | the 90 days to the page's day (from 28 August) | 94 to 80; Texas 13 to 10, Michigan 3 to 1, Arkansas 7 to 6, Pennsylvania 16 to 15, Georgia, Delaware, Kentucky and Illinois 1 to 0 | "in the last 90 days" (finding 5) |
| The fifteen large-load orders are read when the table is there | (not a choice: the run's tables lack it since 20 November) | with them, on the tables of 13 and 14 November: documents 2,057 to 2,072, records 1,518 to 1,528 (ten of their own, two joined: EL26-71, EL26-67); as it opens 295 either way | the note says they join twelve records (finding 2) |
| The PUCT's rows drawn in a view of a table held for them | the monitor held as the first view is; or the PUCT's rows left out | 295 to none; or 1,568 to 1,531 records and 295 to 284 shown | no (finding 1) |
| "Enacted" as the research marked it | in effect where the text's own day has passed | in effect 10 to 13, enacted 6 to 3 | the hover said "its effective date is later, or the text read prints none" (finding 8) |

## Each claim against the code

| Claim, or question | Where | What the code does | Verdict |
|---|---|---|---|
| "Status: the record's status as of its newest document" (Proposed, Final, In effect, Filed, Open for comment ...) | the column's and the filter's hovers | `fields.status` reads the newest document's title and action line; "effective" only where an effective date is on or before that document's date | **Right as stated** on the page; the note's "(a final rule is effective once its effective date has come)" is not what the code does (**finding 6**). 96 of 126 Final records are in effect by their own dates |
| Laws: in effect "signed, and its effective date has passed"; enacted "its effective date is later, or the text read prints none" | the laws block's status hovers | The research table's status as read on 13 and 14 November; no date compared | In effect: no law marked in effect has an effective date after 26 November. Enacted: Maryland S.B. 937 prints 2025-06-01; Maryland H.B. 1532 and Minnesota H.F. 16 print in their cite a day before the read while their Effective column says "not published" (**finding 8**) |
| "The past week": "the seven days to" the file's last document | the calendar's heading hover, its empty line, the note | `weekFrom = day(weekTo, -7)`, both ends counted: eight days | **Finding 4** |
| "The month ahead": "from this page's day to thirty days on" | the calendar | today to today plus 30, both counted | **Right as stated** |
| "N more below significance 5": "steps on records scored below significance 5" | the calendar's lift | `floorHidden`: every step of a record failing the floor, a record with no score among them | 18 of 94 are on records with no score (**finding 3**) |
| "The first dated step any document of the record states on or after this page's day; else its last step, marked passed" | the Next step column | `nextOf`, the page's day | **Right**: 53 ahead, 143 passed, 99 none of the 295 |
| "Changes in the last 90 days" | the laws block, a state chosen | every change of the file, 18 August to 13 November 2026 | **Finding 5** |
| A docket counted twice through two sources | the records | One record a proceeding id, joined across documents; a repeat of a title within 45 days joined | **None found.** 69 groups of records share a body and a title (212 records), each a separate proceeding (the NRC's biweekly notices, each its own docket; one pipeline's blanket certificate requests); 0 pairs that the repeat rule should have joined; one docket split in two by its two RINs of one day, by design (EPA-HQ-OAR-2025-0124). The fifteen large-load orders join their FERC docket's record (EL26-71, EL26-67) when read |
| A state law counted twice | the laws block | One row a law; a held law counted once, its cells blank | **Right**: 27 and 1, 26 states |
| A step's date and a figure "as the document prints them" | the hovers of each date and figure | The words each stands in are kept beside it | **Right**: 2,108 of 2,108 steps hold their date in their own words (65 from the Register's record fields, said so); 299 of 299 figures hold their value in their words. Whether the words are the action's own figure is the audits of 6 November's (85 to 93 percent by class on fresh samples) |
| A law's fields as the text prints them | the laws block | Each value and its cite from the research table | 95 of 95 requirements and every threshold carry a cite; two Effective cells say "not published" where the cite prints the day (finding 8) |
| Paused publishers' items (MISO, the Virginia SCC) still shown, and how marked | the paused line; the Grid and State filters; the week view | No record's source is on misoenergy.org or scc.virginia.gov (0 of 2,127 addresses); 4 records name MISO (3 as it opens), all Federal Register documents; the week view's 18 Virginia SCC dockets (newest 9 September) are listed when in a window, marked "paused since 10 Oct 2026" | **Right**: nothing is read from a paused host, and the line names both. The monitor's Grid filter carries no pause mark beside MISO (the week view's chip does); the line above says it |
| Internal fields reaching a public cell | every cell and hover | Status, instrument, sector, step kind: every key the file holds has its words (none unmapped); the open row prints the table a record bears on as a link (by design) and document ids in hovers; the impact hover names the model (`claude-sonnet-5-5`, 53 records) | **Right as stated**: no machine key on the face of a cell |
| The first view's "this week in policy" and "N of M actions" | the first view | not drawn: the table is held | not restated |
| Time zones | every date | Calendar days with no zone: a Register publication day (Washington's), a release's day, a deadline's day (its hour, "5:00 p.m. Eastern", is in the hover only); the page's day is the UTC day | **Right in kind**. Between 00:00 and 05:00 UTC (19:00 to midnight in Washington) the page's day is a day ahead: a deadline of that evening has passed and the month ahead still lists it as the first day's. Not sized; no figure moves on the hour of the visit otherwise |
| The as-of date of each source | the count line's hover, the calendar, the laws hover | `monitor.json` built 2026-11-25 (newest document 2026-11-25, said when the page's day is later); the laws "written 2026-11-16" (read 13 and 14 November, said in the rows' hovers); `state_rules.json` built 2026-11-12 (said in the week view's foot) | **Right**: each is printed |
| "Scope: federal regulators, state commissions and grid operators only" | the note, the week view's lead | 17 records are the Texas governor's releases, listed on the PUCT's news page (body "Texas Governor"; 9 as it opens) | A governor is none of the three; the State filter's hover says "a release of one of four bodies". Noted, not a branch |
| "The issuing body at the level a reader filters by: a bureau, not its department" | the Body hover | `fields.body` | **Right** |
| "A record ... a release of one of four bodies: a state commission's own dockets are not records here" | the State filter's hover | PUCT and CPUC releases are records; the 120 state dockets are the week view's | **Right as stated** |

## What a regulatory affairs lead's or a commission analyst's own monitor would hold that this does not

| Item | Size | From |
|---|---|---|
| The state commissions' own dockets as records, with their deadlines | 120 dockets of 11 regulators are held for the week view (`state_rules.json`, 12 November: Texas PUC 21, Virginia SCC 18, FERC 16, CPUC 13, Pennsylvania 10, Ohio 10, Illinois 9, Indiana 7, Oregon 7, Arizona 5, Georgia 4) and none is a record of the monitor; the monitor's state-level bodies are the PUCT's and CPUC's news releases (59 records) and the Texas governor's (17) | the files |
| FERC's orders and filings that never reach the Register (rates, tariffs, complaints, large-load compliance) | not sized: no feed (FERC's pages answer a browser check, the note's section 7); the fifteen large-load orders of the research pass show the kind, and none of them is in the Register | finding 2 |
| The grid operators' stakeholder and board decisions (PJM, ERCOT revision requests, SPP) | not sized beyond the fifteen; MISO is paused | the note, section 16 |
| A status as of today ("in effect", "comments closed") | 96 Final records in effect by their own dates; 133 of 175 proposed or open with every comment date passed | finding 6; `data_ready_c301.md` row 7 |
| A significance an analyst would set | the score is a model's (the news rubric); the note's trial of a rescoring put 20 of 80 at 5 or more against 28 held (about 29 percent fewer on the default view) | the note, section 17 |
| Courts (stays, vacaturs) and Congress | none held | the note, section 16 |
| Every state's large-load law | rows for 26 states; 22 searched with none found or a site not read; Alaska and Hawaii not searched | `large_load_rules.json` |
| A fresh read | the laws read 13 and 14 November, the dockets file of 12 November, both two weeks old on the page's day | the files |

## Findings, largest effect first

| # | Severity | Finding | Effect | Fix | Branch |
|---|---|---|---|---|---|
| 1 | Medium | The monitor view draws `policy_actions`, held whole for the PUCT's releases, with no gate, while the first view honours the hold | 37 records of the PUCT's own pages, 11 as it opens, 9 with a figure | figure: for ruling (already line 1 of 17 November) | `wip/audit-policy-7` (`5f1dc28ab`) |
| 2 | Medium | The fifteen large-load orders of FERC and the grid operators left `monitor.json` on 20 November; the note says they join twelve records | 15 documents, 10 records of their own, 2 joined; none as it opens (unscored) | data request; a test, not for landing | `wip/audit-policy-8` (`4d3199094`) |
| 3 | Low | Records with no score are below every floor; the lift's hover said "scored below", the Reset's named the floor alone | 56 records, 18 of 94 hidden steps; 295 to 351 if shown | words; the figure for ruling | `wip/audit-policy-1` (`2f40d2786`); `wip/audit-policy-9` (`bd6fe58ca`) |
| 4 | Low | The past week is eight calendar days; the hover, the empty line and the note said seven | 6 records against 4 today | words | `wip/audit-policy-2` (`074d2c811`) |
| 5 | Low | "Changes in the last 90 days" counts every change of a file ending 13 November | 14 of 94 outside the 90 days to 26 November; Texas 13 against 10 | words | `wip/audit-policy-3` (`d745d7f6a`) |
| 6 | Low | The note said a final rule becomes effective once its date comes; the status is its newest document's and stays final | 96 of 126 Final records in effect by their dates | words; the figure for ruling | `wip/audit-policy-4` (`29bfb82b7`); `wip/audit-policy-10` (`2c78c83d4`) |
| 7 | Low | The note says the charts sum MW and USD by month, keyed `policysum`; the page shows the largest of each unit, no sum | words only | words | `wip/audit-policy-5` (`4d964ad94`) |
| 8 | Low | Three "enacted" laws print in their own cite a day they took effect before the read; the hover said the day is later or not printed | in effect 10 against 13, enacted 6 against 3 | words; data request; the figure for ruling | `wip/audit-policy-6` (`041381c7a`); `wip/audit-policy-11` (`14082788f`) |

## 1. The monitor draws a table held whole (Medium)

- **Where.** `site/app/policy/page.tsx`, the `view === "monitor"` branch: `monitorFile` read and drawn; `site/data/license_status.json`: `policy_actions` and `policy_reads` "license needed", hold "whole", from 2026-10-21, publisher the Public Utility Commission of Texas.
- **Why it matters.** The first view reads the table through the license gate and says "license needed". The monitor's file is built from the same rows, and every record of the PUCT's own pages (the PUCT 20, the Texas Governor's releases on the PUCT's page 17) is drawn with its title, its date, its figure where it states one, and its address. The hold exists for exactly these rows. The rulings of 17 November (`docs/reviews/ruling-impact-policy-2026-11-17.md`, line 1) asked whether the monitor is meant to be held; this audit adds the count of what it draws.
- **The test.** `tests/test_audit_policy_7.py` on `wip/audit-policy-7`: the hold, the branch with no gate, and the PUCT's records in the file (passes on main).
- **For Samuel's ruling.** Default "left as it is". The other choices: the monitor held as the first view is (295 shown to none), or the PUCT's rows left out of the file (1,568 to 1,531 records, 295 to 284 shown).

## 2. The large-load orders left the monitor (Medium)

- **Where.** `warehouse/policy/monitor_site.py`, `change_actions` (reads `utility_large_load_rule_changes.csv` beside `policy_actions.csv` when it is there); the daily run (`warehouse/run_daily.sh`, `policy_monitor_records`); `monitor.json`; the note, section 16 ("On 16 November they joined 12 records").
- **Why it matters.** These are the orders a large-load developer reads first: PJM's tariff definition of a large load and its registry (ER26-3515), SPP's Conditional High Impact Large Load Service (ER26-1323) and its provisional load process (ER26-3691), ERCOT's Batch Zero study (PGRR 145) and its planning guide order, the show-cause dockets of PJM and CAISO (EL26-67, EL26-71), Pennsylvania's model tariff. None is printed in the Federal Register. The file written by the daily run of 20 November 2026 (`98ccb4973`) has none of them (`git log -S llchange:`), nor has the file of 25 November (`fields_from` lacks the table). The run's tables hold no `utility_large_load_rule_changes.csv`; the step's guard counts records, and new Register documents kept the count above the file's.
- **Measured.** The builder run twice on the main copy's tables of 13 and 14 November: with the fifteen, 2,057 to 2,072 documents and 1,518 to 1,528 records; ten records of their own (FERC 5, ERCOT 2, the PA PUC 2, the PUCT 1, none scored) and two joined (EL26-71 gains CAISO's response, EL26-67 two steps). As the view opens, 295 either way: the fifteen are never scored (finding 3), so even restored they show only with the floor lifted.
- **The test.** `tests/test_audit_policy_8.py` on `wip/audit-policy-8`: the builder still reads such a row (passes); the page's file holds them (fails on main: the finding).
- **Data request** (below): the daily run reads the table, so the next file holds the fifteen again.

## 3. Records with no score are hidden as the view opens (Low)

- **Where.** `site/lib/policymonitor.ts`, `filterRows` (`(r.significance ?? -1) >= f.minSig`), `OPEN_FILTERS` (5); `MonitorCalendar.tsx`, the lift's hover; `MonitorView.tsx`, the Reset's hover.
- **Why it matters.** The scorer runs after the connector, so the newest documents carry no score for a while (44 of the 56 are of November), and the large-load orders are never scored. A record with no score is not a record "scored below 5", and nothing on the face says it is hidden. Of the 94 steps of the month ahead the lift counts, 18 are on records with no score; 13 such records hold a step in the month ahead.
- **The test.** `tests/test_audit_policy_1.py` on `wip/audit-policy-1`: records with no score exist and are below the floor (passes on main); the words test fails on main.
- **The fix on the branch, words only.** The lift's hover: "Steps on records scored below significance 5, or not scored at all (the newest documents, and the grid operators' and FERC's large-load orders, which are never scored)". The Reset's hover adds that a record not scored is below every floor and is shown only with Significance set to All. No figure moves.
- **For Samuel's ruling.** Default "left as it is". The other choice, records with no score shown at the opening floor (`wip/audit-policy-9`, a test only): 295 to 351 (+19.0 percent).

## 4. The past week is eight days (Low)

- **Where.** `site/lib/policymonitor.ts`, `calendarOf`; `MonitorCalendar.tsx`, the heading's hover and the empty line; the note, section 16.
- **Why it is wrong.** The week runs from seven days before its last day to that day, both counted. The dates printed in the heading are right (2026-11-18 to 2026-11-25); the hover said "the seven days to 2026-11-25", the empty line "these seven days", the note "the past seven days". Two records of 18 November are in the week that seven days would leave out.
- **The test.** `tests/test_audit_policy_2.py` on `wip/audit-policy-2`.
- **The fix on the branch, words only.** The hovers say "both days counted (eight calendar days ...)", the empty line "these eight days", the note "the past week (from seven days before the day to the day, both counted: eight calendar days)". Seven days (6 to 4 records today) is not built: the words now say what the page does.

## 5. "The last 90 days" is a fixed window (Low)

- **Where.** `site/app/policy/StateLaws.tsx`, the line a chosen state draws; `page.tsx`, `countByState(ll.changes ...)`; the note, section 18.
- **Why it is wrong.** The changes are the research pass's of 15 August to 13 November 2026 (first dated 18 August); the page counts all of them whatever its day. On 26 November, 14 of the 94 are older than 90 days: Texas reads "13 changes in the last 90 days", against 10. The All grids tab's own caption says "in the 90 days to 13 November 2026".
- **The test.** `tests/test_audit_policy_3.py` on `wip/audit-policy-3`; `site/scripts/test-large-load-render.mjs` follows the words.
- **The fix on the branch, words only.** "(N changes in the 90 days to 13 November 2026)", and the note says the same. No figure moves.

## 6. A status stays final after its effective date (Low)

- **Where.** `warehouse/policy/fields.py`, `status`; the note, section 14 ("a final rule is effective once its effective date has come").
- **Why it matters.** The page's hovers say "as of the newest document", which is what the code does. The note says the opposite, and an analyst reading "Final" for a rule that took effect in the spring reads it wrong: 96 of 126 Final records (14 of 26 as it opens) hold an effective date on or before 26 November, and the Status filter's "In effect" (70; 5 as it opens) leaves them out.
- **The test.** `tests/test_audit_policy_4.py` on `wip/audit-policy-4`: the builder's rule on a rule published before its date (passes on main); the note's words (fails on main).
- **The fix on the branch, words only.** The note says a rule is "effective" only when its effective date is on or before the document's own date and stays "final", on the page too, after that date has passed.
- **For Samuel's ruling.** Default "left as it is". The other choice, a status as of the page's day (`wip/audit-policy-10`, a test only): Final 126 to 30, In effect 70 to 166; as it opens Final 26 to 12, In effect 5 to 19.

## 7. The note describes charts the page no longer draws (Low)

- **Where.** The note, section 16, "The file and the page" and "The tracer"; `MonitorCharts.tsx`, `figureMonths`, `keysOf`.
- **Why it is wrong.** Since session 1876 (policy faults row 28) the table by month adds nothing: it shows the count and the largest figure of each unit, and no `policysum` key is drawn. The note still says the MW and USD are "summed by month" and that each sum carries a key.
- **The test.** `tests/test_audit_policy_5.py` on `wip/audit-policy-5`.
- **The fix on the branch, words only.** The note says what the table shows and that the sum key is no longer drawn (the checker keeps its sum check for an older file's keys).

## 8. Three enacted laws had taken effect when read (Low)

- **Where.** `site/lib/largeloadrules.ts`, `LAW_STATUS_TIP.enacted`; `large_load_rules.json` (the research table `state_large_load_laws`).
- **Why it matters.** "Enacted" read "its effective date is later, or the text read prints none". Maryland S.B. 937 is enacted with its Effective column 2025-06-01; Maryland H.B. 1532's cite prints "shall take effect July 1, 2026" for its main sections, and Minnesota H.F. 16's "effective the day following final enactment" (signed 14 June 2025), while both Effective cells say "not published". All three were read on 13 or 14 November 2026. Kansas S.B. 98 takes effect on its publication in the statute book, a day its text does not print.
- **The test.** `tests/test_audit_policy_6.py` on `wip/audit-policy-6`; `site/scripts/test-large-load-read.mjs` row 6 widened for the longer hover.
- **The fix on the branch, words only.** "Signed into law, as the ERW's read of the text marked it; the read did not mark it in effect. Where the text prints when it takes effect, the Effective column or the status's cite says so, and that day may already have passed."
- **For Samuel's ruling.** Default "left as it is". The other choice, the three marked in effect (`wip/audit-policy-11`, a test only): in effect 10 to 13, enacted 6 to 3. The statuses and the two Effective cells are the research table's (a data request).

## The words branches drawn and read

Each branch's words were drawn with the site's own code (`draw_policy.mjs`: `MonitorView` whole, as it opens and with Texas chosen; `draw_note.mjs`: the note as `/data/methods/policy_monitor` renders it) and read in the drawn text (`read_words.py`). No em dash in any drawing.

| Branch | Where the words are drawn | Read |
|---|---|---|
| `wip/audit-policy-1` | the calendar's "94 more below significance 5" hover; the Reset's hover | pass: both sentences |
| `wip/audit-policy-2` | the calendar's heading hover; the note, section 16 | pass: "Records whose newest document is dated from 2026-11-18 to 2026-11-25, both days counted (eight calendar days, ...)"; the empty line is drawn only when the week is empty and was read in its source |
| `wip/audit-policy-3` | the laws block with Texas chosen; the note, section 18 | pass: "11 in TX (13 changes in the 90 days to 13 November 2026)" |
| `wip/audit-policy-4` | the note, section 14 | pass |
| `wip/audit-policy-5` | the note, section 16 | pass: both sentences |
| `wip/audit-policy-6` | the laws block, every "enacted" hover (seven) | pass |
| `wip/audit-policy-words` (the six merged, `c46d60804`) | all of the above | pass: 10 of 10 sentences; the page's 538 figures equal to main's (no figure moves) |

- The six merge onto origin/main of 26 November (`6465239d0`) with no conflict. Their tests with every test file that reads the changed files (`test_policy_monitor_page`, `test_session157`, `157_page`, `164`, `172`, `241a`, `329`, `332`, `469`, `1876`, `7201_large_load_on_site`, `7204_policy_read`): 176 passed, 2 skipped, on the merge. The site's own `test-policy-monitor.mjs` 99, `test-large-load-rules.mjs` 92, `test-large-load-render.mjs` 58, `test-large-load-read.mjs` 54, all passing on the merge. `test-allgrids-read.mjs` row 10 fails on main and on the branches alike (a hover of the All grids tab, not touched here).

## Not covered, or left open

- **The live set's rows.** The first view and the week view's actions read `policy_actions` from the live set, held; not drawn, not restated.
- **The impact sentences and plain reads** are the model's; their words against their texts were audited on 6 and 11 November.
- **The replication** reads `policy_actions` (older here than the file); not run.
- **The pages in a browser:** drawn to HTML with the site's own code; no layout, no width of 390 px.

## Landing, rulings and data (returned to the chain's main session)

- **For landing (words only):** `wip/audit-policy-words` (`c46d60804`), the six merged onto `6465239d0`; or each alone: `wip/audit-policy-1` (`2f40d2786`), `-2` (`074d2c811`), `-3` (`d745d7f6a`), `-4` (`29bfb82b7`), `-5` (`4d964ad94`), `-6` (`041381c7a`). No figure moves.
- **For Samuel's ruling, default "left as it is":**
  - Finding 1, `wip/audit-policy-7`: hold the monitor as the first view is held (295 shown to none), or leave out the PUCT's rows (1,568 to 1,531 records, 295 to 284 shown).
  - Finding 3, `wip/audit-policy-9`: show records with no score at the opening floor (295 to 351).
  - Finding 6, `wip/audit-policy-10`: a status as of the page's day (Final 126 to 30, In effect 70 to 166).
  - Finding 8, `wip/audit-policy-11`: three enacted laws marked in effect (in effect 10 to 13, enacted 6 to 3).
- **Data requests:**
  - The daily run's `policy_monitor_records` step: its tables hold no `utility_large_load_rule_changes.csv` since 20 November 2026, so `monitor.json` lost the fifteen large-load orders (finding 2). Asked: the table on the run's machine, then `monitor.json`'s `fields_from` holds "utility_large_load_rule_changes" (`tests/test_audit_policy_8.py` passes).
  - `state_large_load_laws`: Maryland S.B. 937, Maryland H.B. 1532 and Minnesota H.F. 16 re-read for their status against their own effective days (and H.B. 1532's and H.F. 16's Effective cells, which their cites print), and Kansas S.B. 98's day of publication (finding 8).
- **Needs the key:** none.
