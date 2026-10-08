# How long large loads waited, measured from dated copies of public queues: one page

Session 155, 8 October 2026; Texas and Grant County PUD read again in Session 160 the same day (the section "Texas"
below). Facts only. The table is **internal** and is not in this repository (which is public):
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

## What was followed, and the measured waits (days)

- **New York ISO**: 37 dated copies read, 2014-09-04 to 2026-09-11; load requests: 78 seen, **73 followed**, 5 not (seen in one copy only: 5); 4 in service and 17 withdrawn in the last copy.
- **Grant County Public Utility District**: 5 dated copies read, 2025-06-30 to 2026-07-30 (3 more could not be read); load requests: 1 seen, **1 followed**, 0 not (none); 0 in service and 0 withdrawn in the last copy.
- **The table**: 491 rows, one a request and stage interval: measured 159, lower bound 279, two copies only 5, upper bound 48.

| Entity | Interval, or the stage as worded | Requests | Measured | Measured, days | Lower bounds, days at least | Two copies only | Upper bounds, days at most |
|---|---|---|---|---|---|---|---|
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

- **New York ISO** said "90-day" (System Impact Study (SIS), 2026-07-23), taken as 90 days. Measured, system impact study, pending or in progress to approved: 22 durations, 21 above, 0 below, 1 with the stated figure inside the measured range; 32 lower bounds, 30 already longer.
- **New York ISO** said "90-day" (System Impact Study (SIS), 2026-07-23), taken as 90 days. Measured, in stage: SRIS/SIS in Progress: 22 durations, 14 above, 0 below, 8 with the stated figure inside the measured range; 16 lower bounds, 10 already longer.
- **New York ISO** said "nine months" (System Impact Study (SIS), 2025-11-07), taken as 274 days. Measured, system impact study, pending or in progress to approved: 22 durations, 20 above, 0 below, 2 with the stated figure inside the measured range; 32 lower bounds, 18 already longer.
- **New York ISO** said "nine months" (System Impact Study (SIS), 2025-11-07), taken as 274 days. Measured, in stage: SRIS/SIS in Progress: 22 durations, 5 above, 4 below, 13 with the stated figure inside the measured range; 16 lower bounds, 0 already longer.
- **New York ISO** said "2 weeks" (project scoping call, 2025-11-07): no comparison: the statement runs from NYISO finding a request complete to its scheduling a scoping call, and no copy shows either day.
- **Grant County Public Utility District** states no expectation of a wait in the table: no comparison.
- The "nine months" runs from the customer's study selection, a day no copy shows: so two measures stand beside it.
  The "90-day" is a step of a procedure proposed in July 2026, not the one these requests went through. **ERCOT**
  states expectations (its study steps, in weeks) and nothing of its can be measured here: no comparison. The other
  104 expectations are of entities with no request followed here, ERCOT's among them.

## What could be followed next

Listings only (16 of the 60 allowed): no copy of these was fetched, and none was opened.

| Publisher | The Archive's captures of the queue file | First | Last | A request's identifier |
|---|---|---|---|---|
| Bonneville Power Administration, `InterconnectionQueueOutput.xlsx` (bpa.gov) | 16 captures, 14 distinct files, 2 addresses | 2022-04-01 | 2026-02-22 | to be confirmed on the first copy |
| The same workbook on its earlier site (transmission.bpa.gov) | 7 captures, 7 distinct, 3 addresses | 2010-05-27 | 2013-03-19 | to be confirmed |
| Alberta Electric System Operator, monthly project list (Canada) | 535 captures, 164 distinct, 167 addresses | 2017-07-07 | 2026-10-01 | to be confirmed; not the United States |

- No capture by these listings: SPP, Western Area Power Administration, Tri-State, Salt River Project, ISO New
  England, and the OASIS folders of Avista, Puget Sound Energy, Bonneville and Grant County PUD. A listing that
  returns nothing may be the listing's limit, not the Archive's holdings. One wider listing of bpa.gov failed and
  was left.
- **Keep every new copy of the two queues followed here** (New York ISO's workbook each month, Grant County PUD's
  PDF), and of the queues [`large_load_eighty.md`](large_load_eighty.md) names as coming.

## The pull, and the terms

Session 155: 96 requests of a ceiling of 1,500; 32.2 MB of 3 GB; 975 rows of requests of 3,000,000. Session 160
(ERCOT and Grant County PUD only; New York's workbook was not asked for): 146 more requests (24 to the Archive, 121
to ERCOT, 1 to Grant County PUD), 36.4 MB, no new row of a request, against the owner's ceiling of 2,000,000 rows;
242 requests and 68.6 MB in all. One capture was refused by the Archive (403) and left; the same report was read
from ERCOT. One request every 2.5 seconds to the Archive. Every request carried "ERW research project, github.com/SamuelEnrique/erw" and no address of a
person. MISO and PJM were not requested. Each terms page is saved with its hash (`captures.csv`).

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
