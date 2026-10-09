# How long large loads waited, measured from dated copies of public queues: one page

Session 155, 8 October 2026; Texas and Grant County PUD read again in Session 160 the same day (the section "Texas"
below). Bonneville Power Administration and Alberta's system operator (Canada, kept apart
below) were added in Session 165, 9 October 2026. Facts only. The table is **internal** and is not in this repository (which is public):
`warehouse/output/large_load_waits.csv` on the data machine, built by `warehouse/connectors/large_load_waits.py` from
the copies saved under `warehouse/raw/large_load_waits/`. No request is named here and no megawatt of a request is
given. It follows [`large_load_eighty.md`](large_load_eighty.md), which found that no utility, operator or regulator
publishes how long its large loads waited, and that successive copies of a queue are the one route to it.

## The rule

- **A request is followed by the publisher's own identifier**, from copy to copy. A request seen in one copy only is
  not followed. A copy is dated by its publisher (the day the workbook was last saved; the day printed on the PDF),
  never by the day the Internet Archive captured it: an old address can answer with a newer file.
- **A duration is a range between copies, never a midpoint.** An event came between the last copy that does not show
  it and the first that does. At least: the later bound of the start to the earlier bound of the end. At most: the
  earlier bound of the start to the later bound of the end. The queue date the copies print is used as printed.
- **Labels.** `measured`: the end lies between two copies that hold the request and the start is printed or bounded.
  `lower bound`: the end has not come, or one side is not bounded. `two copies only`: the request is seen in two
  copies, and only a lower bound is given. `upper bound`: the end had already come in the first copy that holds the
  request. Nothing is interpolated. Lower bounds are counted apart and never averaged.
- **A stage is counted only where a copy shows it** in the publisher's words; the words are kept beside the class
  (the five stages of `large_load_statements`). A figure on fewer than 5 requests is its values, not a median.
- **Session 165.** A status word that no copy of its publisher explains is kept as printed and placed on no stage;
  where it is the last word a copy shows, no lower bound is made to a milestone. A file saved again long after the
  month it is named for is not used: the day its list stood so is not known.

## What was followed, and the measured waits (days)

- **New York ISO**: 37 dated copies read, 2014-09-04 to 2026-09-11; load requests: 78 seen, **73 followed**, 5 not (seen in one copy only: 5); 4 in service and 17 withdrawn in the last copy.
- **Grant County Public Utility District**: 5 dated copies read, 2025-06-30 to 2026-07-30 (3 more could not be read); load requests: 1 seen, **1 followed**, 0 not (none); 0 in service and 0 withdrawn in the last copy.
- **Bonneville Power Administration**: 22 dated copies read, 2010-05-27 to 2026-10-08; load requests: 458 seen, **433 followed**, 25 not (the queue date printed for it differs between copies: 2; seen in one copy only: 23); 85 in service and 166 withdrawn in the last copy.
- **The table**: 2622 rows, one a request and stage interval: measured 1142, lower bound 1097, two copies only 47, upper bound 336.

| Entity | Interval, or the stage as worded | Requests | Measured | Measured, days | Lower bounds, days at least | Two copies only | Upper bounds, days at most |
|---|---|---|---|---|---|---|---|
| Bonneville Power Administration | request to study | 268 | 75 | median at least 193, at most 449; all within 2 to 5127 | 4 (266 to 1245) | 0 | 189 (37 to 3214) |
| Bonneville Power Administration | request to agreement | 152 | 29 | median at least 1363, at most 1755; all within 492 to 4487 | 123 (232 to 7857) | 0 | 0 |
| Bonneville Power Administration | request to energized | 233 | 76 | median at least 2045.5, at most 3950.5; all within 43 to 6527 | 148 (232 to 7857) | 0 | 9 (393 to 3199) |
| Bonneville Power Administration | study to agreement | 145 | 27 | median at least 456, at most 1588; all within 64 to 4487 | 118 (0 to 5978) | 0 | 0 |
| Bonneville Power Administration | agreement to energized | 29 | 4 | 967 to 1588; 967 to 1588; 967 to 1588; 967 to 1588 | 25 (0 to 1196) | 0 | 0 |
| Bonneville Power Administration | request to withdrawal | 166 | 89 | median at least 606, at most 973; all within 14 to 6064 | 0 | 0 | 77 (254 to 3221) |
| Bonneville Power Administration | in stage: RECEIVED | 103 | 99 | median at least 213, at most 575; all within 2 to 4201 | 4 (266 to 1245) | 0 | 0 |
| Bonneville Power Administration | in stage: STUDY | 195 | 108 | median at least 513, at most 1588; all within 0 to 6527 | 87 (0 to 1652) | 0 | 0 |
| Bonneville Power Administration | in stage: STUDY COMPLETED | 47 | 15 | median at least 456, at most 3586; all within 456 to 4209 | 32 (0 to 1652) | 0 | 0 |
| Bonneville Power Administration | in stage: E&P EXECUTED | 3 | 2 | 513 to 1196; 513 to 1196 | 1 (1196 to 1196) | 0 | 0 |
| Bonneville Power Administration | in stage: CONST AGRMT EXE | 30 | 6 | median at least 967, at most 1588; all within 513 to 1588 | 24 (0 to 1196) | 0 | 0 |
| Bonneville Power Administration | in stage: BPA COMPLETED | 35 | 1 | 253 to 577 | 34 (0 to 742) | 0 | 0 |
| Bonneville Power Administration | in stage: COMPLETED | 1 | 1 | 521 to 3854 | 0 | 0 | 0 |
| Bonneville Power Administration | in stage: CONFIRMED | 18 | 18 | median at least 1027, at most 5554; all within 1027 to 6034 | 0 | 0 | 0 |
| Bonneville Power Administration | in stage, then withdrawn: RECEIVED | 31 | 31 | median at least 422, at most 930; all within 14 to 5699 | 0 | 0 | 0 |
| Bonneville Power Administration | in stage, then withdrawn: STUDY | 49 | 49 | median at least 456, at most 956; all within 0 to 6064 | 0 | 0 | 0 |
| Bonneville Power Administration | in stage, then withdrawn: STUDY COMPLETED | 3 | 3 | 456 to 2057; 456 to 2327; 456 to 3401 | 0 | 0 | 0 |
| Bonneville Power Administration | in stage, then withdrawn: BPA COMPLETED | 3 | 3 | 66 to 347; 253 to 574; 326 to 966 | 0 | 0 | 0 |
| Bonneville Power Administration | in stage, then withdrawn: CONFIRMED | 3 | 3 | 0 to 908; 1027 to 5168; 1027 to 5218 | 0 | 0 | 0 |
| Grant County Public Utility District | request to agreement | 1 | 0 |  | 0 | 0 | 1 (2264 to 2264) |
| Grant County Public Utility District | request to construction | 1 | 0 |  | 1 (2659 to 2659) | 0 | 0 |
| Grant County Public Utility District | request to energized | 1 | 0 |  | 1 (2659 to 2659) | 0 | 0 |
| Grant County Public Utility District | agreement to energized | 1 | 0 |  | 1 (395 to 395) | 0 | 0 |
| Grant County Public Utility District | in stage: Construction Agreement Signed | 1 | 0 |  | 1 (395 to 395) | 0 | 0 |
| New York ISO | request to study | 57 | 21 | median at least 26, at most 86; all within 1 to 782 | 1 (152 to 152) | 1 (57 to 57) | 34 (28 to 563) |
| New York ISO | request to agreement | 48 | 0 |  | 47 (105 to 2881) | 1 (57 to 57) | 0 |
| New York ISO | request to construction | 52 | 4 | 1153 to 1222; 1252 to 1321; 2270 to 2326; 2297 to 2366 | 47 (105 to 2881) | 1 (57 to 57) | 0 |
| New York ISO | request to energized | 56 | 2 | 1028 to 1151; 1270 to 1339 | 51 (105 to 3636) | 1 (57 to 57) | 2 (4330 to 5217) |
| New York ISO | study to agreement | 46 | 0 |  | 46 (30 to 2682) | 0 | 0 |
| New York ISO | request to withdrawal | 17 | 6 | median at least 322, at most 760.5; all within 28 to 915 | 0 | 0 | 11 (99 to 2171) |
| New York ISO | system impact study, pending or in progress to approved | 54 | 22 | median at least 414, at most 680; all within 0 to 1239 | 32 (30 to 522) | 0 | 0 |
| New York ISO | in stage: Scoping Meeting Pending | 23 | 21 | median at least 26, at most 86; all within 1 to 782 | 1 (152 to 152) | 1 (57 to 57) | 0 |
| New York ISO | in stage: FS Pending | 3 | 1 | 0 to 97 | 2 (851 to 851) | 0 | 0 |
| New York ISO | in stage: FS in Progress | 5 | 2 | 0 to 155; 276 to 664 | 3 (30 to 58) | 0 | 0 |
| New York ISO | in stage: Rejected Cost Allocation/Next FS Pending | 1 | 0 |  | 1 (0 to 0) | 0 | 0 |
| New York ISO | in stage: SRIS/SIS Approved | 19 | 15 | median at least 447, at most 670; all within 0 to 1431 | 4 (30 to 462) | 0 | 0 |
| New York ISO | in stage: SRIS/SIS Pending | 53 | 37 | median at least 159, at most 331; all within 0 to 935 | 16 (30 to 303) | 0 | 0 |
| New York ISO | in stage: SRIS/SIS in Progress | 38 | 22 | median at least 156, at most 364; all within 0 to 1040 | 16 (0 to 239) | 0 | 0 |
| New York ISO | in stage: Accepted Cost Allocation/IA in Progress | 4 | 0 |  | 4 (58 to 58) | 0 | 0 |
| New York ISO | in stage: Under Construction | 4 | 0 |  | 4 (58 to 1310) | 0 | 0 |
| New York ISO | in stage, then withdrawn: Scoping Meeting Pending | 3 | 3 | 28 to 54; 43 to 812; 68 to 313 | 0 | 0 | 0 |
| New York ISO | in stage, then withdrawn: SRIS/SIS Approved | 2 | 2 | 154 to 271; 176 to 342 | 0 | 0 | 0 |
| New York ISO | in stage, then withdrawn: SRIS/SIS Pending | 1 | 1 | 427 to 908 | 0 | 0 | 0 |

- **Two loads were followed from request to in service**, both in New York: between 1,028 and 1,151 days, and
  between 1,270 and 1,339 days. 51 more have waited at least 105 to 3,636 days and are not in service.
- "Request to study" ends at the first study status a copy shows. For most New York requests that is "SRIS/SIS
  Pending": the study is then waiting to begin, not begun.
- No copy shows a signed agreement for a New York load: those under construction or in service went there from a
  study status, so "study to agreement" holds lower bounds only. By size: in the table and the session's report, not
  here (a size is a megawatt figure of a request).
- **ERCOT: nothing can be followed.** Session 155 read 11 of its large load status reports and session 160 every one
  that could be found, 32 (26 April 2022 to 19 June 2026): each gives megawatts by stage for the whole system and
  names no request. A stage's megawatts over time is not a request's wait, and no wait was made from them.
- **Grant County PUD's public queue holds one load request.** Its large power queue (about 692 megawatts by its own
  resource plan) was not found published as a list. Two older copies are pictures of the page and were not read.
- **Bonneville's list is of line and load interconnections** (its Connection Type `LL`): a request of a customer
  utility for a line or a load. No copy says which is a large load, so every `LL` request is followed and none is
  called a large load here. 22 copies: 7 of 2010 to 2013 and 15 of 2022 to 2026, with none between 19 March 2013 and
  31 March 2022 (3,299 days). An end that fell in that gap is measured, by the rule, with a range as wide as the gap.
- **Bonneville, request to energized: 76 measured.** For the 30 whose end lies between two copies of 2022 to 2026 (at
  most 454 days apart): median at least 2,868 days, at most 3,243.5; all within 43 to 6,015. For the 46 whose end fell
  in the nine years with no copy: median at least 1,477.5, at most 4,776.5. 148 more are **lower bounds**, at least
  232 to 7,857 days, and are not energized.
- Bonneville, the ends outside those nine years only: request to study, 72 of the 75 measured, median at least 187
  days, at most 421; request to a construction agreement, all 29, median at least 1,363, at most 1,755; request to
  withdrawal, 70 of the 89, median at least 517, at most 848.5.
- Bonneville's words `CONFIRMED`, `COMPLETED` and `BPA COMPLETED` are explained in no copy: they are kept and placed on
  no stage, and a request whose last copy shows one gives no lower bound to a milestone (35 requests read `BPA
  COMPLETED` in the newest copy). Bonneville prints no construction status, so it has no "request to construction".
- **ISO New England: nothing can be followed.** Its posted queue, read once on 9 October 2026, lists 1,751 requests
  whose Type is G (1,569), ETU (170) or TS (12): generators, elective transmission upgrades and transmission service.
  No row is a load, and no wait was made from it (the section "What could be followed next" quotes its columns).

## Texas: what can be measured, beside what was stated

Session 160 asked the Internet Archive for every dated copy of ERCOT's large load status reports under the names its
task force and working group gave them, and ERCOT's own site for the reports it still lists (its meeting pages of
2022 to 2026). The table gained no row: there is no request to follow.

- **ERCOT**: 32 large load status reports read, 2022-04-26 to 2026-06-19 (20 held by the Internet Archive, 12 read from ERCOT); reports that name a request: 0; requests followed: 0; measured waits: none.
- What the reports do print, for the whole system (25 of the 32 write the sentence out): on 2023-05-31, 2,620 MW approved to energize and 2,072 MW observed consuming (the all-time non-simultaneous peak); on 2026-06-19, 8,927 MW and 3,900 MW (the month's non-simultaneous peak). A total over time is not a request's wait: no wait is made from it.
- **Oncor Electric Delivery** wrote "687 days" (measured; retail transmission interconnections placed in service (from initial submission to energizing the interconnection); 2025-08-25).
- **Oncor Electric Delivery** wrote "825 days" (measured; retail transmission interconnections placed in service (from initial submission to energizing the interconnection); 2025-08-25).
- **ERCOT** wrote "approximately 220 days" (measured; in-service (delay against the in-service date); 2025-05-01).
- **ERCOT** wrote "a few days to many weeks" (general statement; Under ERCOT Review; 2025-12-15).
- **ERCOT** wrote "ten Business Days" (expected; review of the preliminary study report; 2025-12-15).
- **ERCOT** wrote "13 weeks" (expected; Batch Zero study, step 1: Case Build; 2026-05-05).
- **ERCOT** wrote "14 weeks" (expected; Batch Zero study, step 4: FAC-002 Stability and Batch Refinement Study (after the developer commitment deadline); 2026-05-05).
- **ERCOT** wrote "15 weeks" (expected; Batch Zero study, step 2: Steady State Analysis; 2026-05-05).
- **ERCOT** wrote "16 weeks" (expected; Batch Zero study, step 3: Stability Screening Study and Final Report; 2026-05-05).
- **ERCOT** wrote "several months" (expected; Batch Zero study process (classification paused for the verification and audit); 2026-08-10).
- **Why no request is named, in ERCOT's words** (its reports of 2026, under the chart by transmission provider): "The
  Other category includes categories in which there are less than five customers and is aggregated to protect
  Customer data".
- The reports of 2025 and 2026 carry charts of megawatts by the date a project was submitted and by its in-service
  date. They are pictures in the files, and megawatts by transmission provider, not requests: no number was read
  off them.
- No status report was found on the working group's or the committee's meeting pages after 19 June 2026: the
  meetings of July to September 2026 list updates on the batch study instead.
- **So the only measured Texas wait held is Oncor's own**: an average of 825 days and a median of 687 days from
  first submission to energizing, for 79 retail transmission interconnections placed in service from 2022 through
  2024. It is Oncor's measurement, not one made here, and nothing here can confirm or contradict it. ERCOT's four
  batch study steps, as written, are 13, 15, 16 and 14 weeks; ERCOT wrote the steps, not their sum.
- **Grant County PUD, again**: its page links the same copy as in the morning (30 July 2026), so its one request's
  lower bound stands. A second listing of its site found no file of a large power queue: 158 captures of 22
  addresses, all pages about large power service and one rate schedule.

## Against what the same entities said to expect

`large_load_statements` holds 171 distinct wait figures, 107 of them expectations about a large load's wait. A
measured duration is a range: above the stated figure when even its least is longer, below when even its most is
shorter, otherwise the stated figure lies inside the range. No ranking across entities.

- **Bonneville Power Administration** said "180 Calendar Days" (LLI System Impact Study (SIS), 2026-09-09): no comparison: no interval measured here covers this step.
- **Bonneville Power Administration** said "7-8 years" (study of the transmission service request queue in batches, 2025-12-17): no comparison: no interval measured here covers this step.
- **Bonneville Power Administration** said "5-6 years" (request to service, 2025-07-09): no comparison: no interval measured here covers this step.
- **New York ISO** said "90-day" (System Impact Study (SIS), 2026-07-23), taken as 90 days. Measured, system impact study, pending or in progress to approved: 22 durations, 21 above, 0 below, 1 with the stated figure inside the measured range; 32 lower bounds, 30 already longer.
- **New York ISO** said "90-day" (System Impact Study (SIS), 2026-07-23), taken as 90 days. Measured, in stage: SRIS/SIS in Progress: 22 durations, 14 above, 0 below, 8 with the stated figure inside the measured range; 16 lower bounds, 10 already longer.
- **New York ISO** said "nine months" (System Impact Study (SIS), 2025-11-07), taken as 274 days. Measured, system impact study, pending or in progress to approved: 22 durations, 20 above, 0 below, 2 with the stated figure inside the measured range; 32 lower bounds, 18 already longer.
- **New York ISO** said "nine months" (System Impact Study (SIS), 2025-11-07), taken as 274 days. Measured, in stage: SRIS/SIS in Progress: 22 durations, 5 above, 4 below, 13 with the stated figure inside the measured range; 16 lower bounds, 0 already longer.
- **New York ISO** said "2 weeks" (project scoping call, 2025-11-07): no comparison: the statement runs from NYISO finding a request complete to its scheduling a scoping call, and no copy shows either day.
- **Grant County Public Utility District** states no expectation of a wait in the table: no comparison.
- The "nine months" runs from the customer's study selection, a day no copy shows: so two measures stand beside it.
  The "90-day" is a step of a procedure proposed in July 2026, not the one these requests went through. **ERCOT**
  states expectations (its study steps, in weeks) and nothing of its can be measured here: no comparison. The other
  101 expectations (104 before Bonneville was followed) are of entities with no request followed here, ERCOT's
  among them.
- Bonneville's three statements have no measured interval set beside them. Its "180 Calendar Days" is of a system
  impact study, and its copies show a study's status, not the day a study began or ended. Its "5-6 years" and "7-8
  years" are ranges of years, not one figure, and a range is not converted here. They stand as written.

## Canada: Alberta, apart from the United States

Canada is not the United States: no figure, median or table row above is Alberta's (the one count above that includes
Canada is the table's whole row count). The Alberta Electric System Operator posts a connection project list each month; one capture a month was read (the Internet Archive's latest of
each monthly file) and the newest file from the operator's own page. A load is a row the list itself marks so (MW
Type `Load`, and from 2024 `Data Load`, `Distribution Load` and `Industrial Load`); a generator listed with a load and
a change to an existing contract are not taken.

- **Alberta Electric System Operator (Canada)**: 97 dated copies read, 2016-09-26 to 2026-09-01 (3 more could not be read); load requests: 236 seen, **213 followed**, 23 not (seen in one copy only: 22; the queue date printed for it differs between copies: 1); 50 in service and 39 withdrawn in the last copy.
- **Canada's rows in the table**: 617 of the 2622.

| Entity | Interval, or the stage as worded | Requests | Measured | Measured, days | Lower bounds, days at least | Two copies only | Upper bounds, days at most |
|---|---|---|---|---|---|---|---|
| Alberta Electric System Operator (Canada) | request to energized | 173 | 38 | median at least 540, at most 579; all within 28 to 4527 | 109 (98 to 3038) | 15 (83 to 996) | 11 (41 to 1664) |
| Alberta Electric System Operator (Canada) | request to withdrawal | 39 | 37 | median at least 629, at most 662; all within 46 to 4759 | 0 | 0 | 2 (37 to 902) |
| Alberta Electric System Operator (Canada) | in stage: Stage 1 | 113 | 92 | median at least 69.5, at most 156; all within 0 to 821 | 19 (43 to 594) | 2 (28 to 57) | 0 |
| Alberta Electric System Operator (Canada) | in stage: Stage 2 | 91 | 44 | median at least 121.5, at most 411.5; all within 0 to 1789 | 45 (0 to 761) | 2 (0 to 0) | 0 |
| Alberta Electric System Operator (Canada) | in stage: Stage 3 | 62 | 43 | median at least 59, at most 390; all within 0 to 1891 | 15 (0 to 1839) | 4 (0 to 0) | 0 |
| Alberta Electric System Operator (Canada) | in stage: Stage 4 | 35 | 26 | median at least 106, at most 349; all within 0 to 1575 | 2 (235 to 425) | 7 (0 to 0) | 0 |
| Alberta Electric System Operator (Canada) | in stage: Stage 5 | 52 | 22 | median at least 378.5, at most 592.5; all within 0 to 4527 | 19 (0 to 1709) | 11 (0 to 247) | 0 |
| Alberta Electric System Operator (Canada) | in stage: Stage 6 | 15 | 5 | median at least 31, at most 90; all within 0 to 489 | 9 (0 to 33) | 1 (0 to 0) | 0 |
| Alberta Electric System Operator (Canada) | in stage, then withdrawn: Stage 1 | 10 | 10 | median at least 64, at most 183.5; all within 0 to 1090 | 0 | 0 | 0 |
| Alberta Electric System Operator (Canada) | in stage, then withdrawn: Stage 2 | 19 | 19 | median at least 427, at most 662; all within 21 to 2285 | 0 | 0 | 0 |
| Alberta Electric System Operator (Canada) | in stage, then withdrawn: Stage 3 | 4 | 4 | 22 to 122; 364 to 1552; 1003 to 1622; 1036 to 1080 | 0 | 0 | 0 |
| Alberta Electric System Operator (Canada) | in stage, then withdrawn: Stage 5 | 4 | 4 | 1739 to 2133; 1772 to 4712; 1772 to 4712; 1772 to 4759 | 0 | 0 | 0 |

- **Alberta Electric System Operator (Canada)**: 46 of its 213 followed requests are in no later copy and no copy says why (not shown in service, not shown withdrawn): each lower bound of theirs ends at the last copy that held the request and is not a wait still running.
- **Alberta Electric System Operator (Canada)** states no expectation of a wait in the table: no comparison.
- **The list numbers its stages 0 to 6 and no copy says what a number stands for.** The guide to the list is a
  separate document and was not in the approved pull. The numbers are kept as printed and placed on none of the five
  stages, so Alberta has no "request to study" or "request to agreement" here. Energized and cancelled are the list's
  own words (`Recently Energized`, `Recently Cancelled`), printed from April 2021; before then a project that left
  the list left with no word.
- **Alberta, request to energized: 38 measured**, each between two monthly copies: median at least 540 days, at most
  579. 77 more still stand in the newest copy (1 September 2026) and are **lower bounds**, at least 98 to 2,609 days.
- **Data centres, by the list's own mark** (MW Type `Data Load`): 52 projects were ever so marked and 45 stand in the
  newest copy. None is shown energized. 38 are followed and still wait: 37 **lower bounds** and 1 seen in two copies
  only, at least 186 to 876 days since each applied; of the 37, 26 stand at `Stage 2` and 11 at `Stage 1`. 10 more
  were cancelled, all within 46 to 769 days of applying.
- 3 of the 100 monthly files could not be used: each was saved again long after the month it is named for (February
  2018, March 2026, April 2026). The lists of 2016 to 2020 give a project one row a phase: where its rows show one
  stage the first is read, and where they differ the project is not followed.

## What could be followed next

Session 155 listed three queues to follow next; session 165 followed them. Listings of other queues so far: 20 of
the 60 allowed.

| Publisher | What was found | Followed |
|---|---|---|
| Bonneville Power Administration, `InterconnectionQueueOutput` | 23 captures, 21 distinct files, and the current file: 22 dated copies read | yes: 433 requests |
| Alberta Electric System Operator, monthly project list (Canada) | 535 captures of 100 monthly files; one capture a month and the current file: 97 dated copies read | yes: 213 projects, kept apart |
| ISO New England, posted queue (`irtt.iso-ne.com/reports/external`) | one current copy read: 1,751 requests of Type G, ETU or TS | no: it lists no load |
| Pennsylvania's utilities (PPL Electric, PECO, Duquesne Light, FirstEnergy) | listings only: no address of a load queue | no: none is published |

- **ISO New England's columns, as its page prints them:** "Cluster", "QP", "Updated", "Type", "Requested", "Alternative
  Name", "Unit", "Fuel Type", "Net MW", "Summer MW", "Winter MW", "County", "ST", "Op Date", "Sync Date", "W/D Date",
  "POI", "Serv", "SIS", "I39", "TO Report", "Dev", "Zone", "FS", "SIS", "OS", "FAC", "IA", "Project Status", "Status",
  "Jurisdiction". The Type column holds G, ETU and TS and nothing else. It was taken before Pennsylvania because its
  queue page answered first, with a queue that has an identifier (QP) and dated captures; what it lacks is a load.
- **Pennsylvania:** the Internet Archive lists, for PPL Electric, one capture of one tariff rule about large load
  interconnections (August 2026: a rule, not a queue; not opened); for FirstEnergy, Maryland's generator and community
  solar queues; for Duquesne Light, style files of its site; for PECO, nothing. No queue of load requests under the
  model tariff was found published. No other lead was taken in its place: none of session 155's other listings names
  a queue of loads.
- No capture by session 155's listings: SPP, Western Area Power Administration, Tri-State, Salt River Project, and the
  OASIS folders of Avista, Puget Sound Energy, Bonneville and Grant County PUD. A listing that returns nothing may be
  the listing's limit, not the Archive's holdings.
- **Keep every new copy of the queues followed here** (New York ISO's workbook, Grant County PUD's PDF, Bonneville's
  workbook, Alberta's monthly file), and of the queues [`large_load_eighty.md`](large_load_eighty.md) names as coming.
  Alberta's guide to its list would place its stage numbers on the five stages: one document, for a person to approve.

## The pull, and the terms

Session 155: 96 requests of a ceiling of 1,500; 32.2 MB of 3 GB; 975 rows of requests of 3,000,000. Session 160
(ERCOT and Grant County PUD only; New York's workbook was not asked for): 146 more requests (24 to the Archive, 121
to ERCOT, 1 to Grant County PUD), 36.4 MB, no new row of a request, against the owner's ceiling of 2,000,000 rows;
242 requests and 68.6 MB in all. One capture was refused by the Archive (403) and left; the same report was read
from ERCOT. One request every 2.5 seconds to the Archive. Every request carried "ERW research project, github.com/SamuelEnrique/erw" and no address of a
person. MISO and PJM were not requested. Each terms page is saved with its hash (`captures.csv`).

Session 165 (Bonneville, Alberta, ISO New England, and listings for Pennsylvania): 136 more requests (125 to the
Archive: 121 captures and 4 listings; 5 to Alberta's operator, 3 to Bonneville, 3 to ISO New England), 14.1 MB, and
9,730 more rows of requests (Bonneville 6,359, Alberta 3,371), against the owner's ceiling of 1,500,000 rows; 378
requests of 1,500, 82.7 MB of 3 GB and 10,705 rows in all. No 429 or 503, no refusal, no login or check met. The same
contact string and no address of a person. Every file fetched as a copy is the queue's own; no picture was met or read.

- **Internet Archive** (its Terms of Use of 31 Dec 2014, read in its own capture of 1 June 2024, since the page
  today is drawn by a script and a plain request returns no text): "Access to the Archive’s Collections is provided at no cost to you and is granted for scholarship and research purposes only."
  "You agree to abide by all applicable laws and regulations, including intellectual property laws, in connection with your use of the Archive."
  "In particular, you certify that your use of any part of the Archive's Collections will be limited to noninfringing or fair use under copyright law."
  "In addition, we request that, according to standard academic practice, if you use the Archive's Collections for any research that results in an article, a book, or other publication, you list the Archive as a resource in your bibliography."
- **NYISO** (its legal notice, saved by session 149): "Access to this Web site does not confer any license or ownership interest in either the form or content of the Web site, including any confidential or proprietary information or intellectual property of any kind or nature, and the NYISO hereby expressly reserves such rights and property in its entirety."
  "Downloading, republishing, retransmitting, reproducing, or other use of any image or video on this website as a stand-alone file is strictly prohibited"
  No license: everything of NYISO's stays internal.
- **Grant County PUD** (its site links one legal page, a privacy statement, and states no terms of use for its
  documents): "All information collected at this Web site or through this Service becomes a public record that may be subject to inspection by the public unless an exemption in law exists."
  "© Public Utility District No. 2 of Grant County, WA, All Rights Reserved" Held internal until a person rules.
- **ERCOT** (the sentences session 144 quoted, in the page as it reads today): "The publicly available contents of this website may be used, reproduced, and redistributed, provided that the contents are not modified and that you maintain all copyright and other notices contained in the contents, including this Agreement."
  "Notwithstanding the foregoing, raw data provided in public portions of this website may be used, reproduced, and redistributed in compilations, charts, and analyses without maintaining such notices."
- **Bonneville Power Administration** (its site links one legal page, a privacy policy, and states no terms of use for
  its documents; it is an agency of the United States government): "When you visit our website to read pages or download information, we automatically collect and store the following information only:"
  "We use this information to measure the number of visitors to the different sections of our site, and to help make our site more useful to visitors."
  Held internal until a person rules.
- **Alberta Electric System Operator, Canada** (its Legal page, Terms and Conditions): "All material on this Web site is protected by copyright."
  "The material may be used and copied for non-commercial, personal or educational purposes, provided that the material is not modified and that copyright notices are not deleted."
  "Any other use of this material without the AESO's written permission is prohibited."
  The use here is research and nothing of Alberta's is published: held internal. Whether this project's use is
  "non-commercial" is the owner's to weigh.
- **ISO New England** (its Legal and Privacy page, read before its queue): "By using this website, you signify your assent to these Terms and Conditions."
  "You are also hereby put on notice that the Content is protected by copyright under United States laws."
  "Any duplication of the Content or non-personal use may violate copyright, trademark, and other laws."
  Nothing of its queue is in the table.
- The Internet Archive's terms are the ones quoted above, unchanged.
