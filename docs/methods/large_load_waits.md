# Large load waits: how a wait is measured from dated copies of a public queue

The table `large_load_waits` (internal: on no page, in no live set, in no public dataset), the connector
`warehouse/connectors/large_load_waits.py`, and the one-page summary
[`docs/accelerator/large_load_waits.md`](../accelerator/large_load_waits.md). Sessions 155 and 160 (New York ISO,
Grant County PUD, ERCOT) and session 165 (Bonneville Power Administration, the Alberta Electric System Operator,
ISO New England). Approved pulls: session 165's ceilings are 1,500,000 rows of requests (the owner's), 1,500 requests
and 3 GB, counted across all three sessions. No model call.

This note was first written in session 165. The rule, the labels and the terms of the Internet Archive, NYISO, Grant
County PUD and ERCOT are written out on the one-page summary and are not repeated here: this note points to them and
adds each source of session 165, its terms word for word, what was pulled and what could not be followed.

## The method, in five lines

- A list of requests that is published again and again says how long a request waited without being asked: the day
  it first stands in a dated copy, the day its status changes, the day it first reads energized.
- **A request is followed by the publisher's own identifier.** One seen in one copy only is not followed; neither is
  one whose identifier stands on two differing rows of one copy, or whose printed request date differs between copies.
- **A copy is dated by its publisher, never by the day the Internet Archive captured it.**
- **A duration is a range between copies, never a midpoint**: at least, from the later bound of the start to the
  earlier bound of the end; at most, from the earlier bound of the start to the later bound of the end. A request
  still waiting is a **lower bound** and is labeled one. Nothing is filled, interpolated or averaged over lower bounds.
- A stage is counted only where a copy shows it in the publisher's words. The words are kept beside the class.

## Bonneville Power Administration (United States)

- **The source.** The workbook `InterconnectionQueueOutput` that Bonneville's interconnection page links
  (`https://www.bpa.gov/energy-and-services/transmission/interconnection`), titled "Bonneville Power Administration
  Interconnection Request Queue". One sheet, one row a request.
- **Confirmed on the current copy before anything was followed.** Its columns begin "Request Number", "Request Date",
  "Project Name", "Requestor", "Comments", "Point Of Interconnection", "Status", "State", "County", "Connection Type".
  The Connection Type is `GI` (a generator) or `LL` (a line or load interconnection), and the Request Number of an
  `LL` row is the letter L and a number that stands in every copy. So it holds load requests with an identifier.
- **What a row is.** An `LL` request is a customer utility's request for a line or a load. No copy says which is a
  large load: every `LL` request is followed and none is called a large load.
- **The date of a copy** is the day and time the workbook prints above its header (a date cell, or text such as
  "03/19/2013 09:06").
- **Megawatts** are the cell "Max Summer MW" ("Max Outputs Summer" in the copies of 2010 to 2013) as written; blank
  where it is blank. For a line the figure may not be a load.
- **Status words and their classes** (the collecting agent's reading, not a person's review): `RECEIVED` is class 1;
  `STUDY` and `STUDY COMPLETED` class 2; `E&P EXECUTED` class 3; `CONST AGRMT EXE` class 4; `ENERGIZED` class 5 and
  in service; `WITHDRAWN` the request left. `CONFIRMED`, `COMPLETED` and `BPA COMPLETED` are explained in no copy: they
  are kept and placed on no class, and a request whose last copy shows one gives no lower bound to a milestone.
  Bonneville prints no construction status, so no "request to construction" is made.
- **What was pulled.** The Internet Archive lists 23 captures of the workbook under three addresses (7 of 2010 to
  2013, 16 of 2022 to 2026), 21 distinct files; each distinct file was fetched once, and the current file once from
  Bonneville. 22 dated copies read, 27 May 2010 to 8 October 2026; none between 19 March 2013 and 31 March 2022.
- **Followed.** 458 requests seen, 433 followed; 23 seen in one copy only; 2 whose printed request date differs
  between copies.
- **The limit that matters.** An end that fell in the nine years with no copy is "measured" by the rule, with a range
  as wide as the gap. The summary gives the durations whose end fell in those years apart from the others.
- **Terms.** Bonneville's site links one legal page, a privacy policy
  (`https://www.bpa.gov/about/who-we-are/privacy`, saved 9 October 2026 00:41:29 UTC, sha256
  `4877efd39c18215c22d16f1921312319bf4c390907c3d6f063cb342d6c45ef47`), and states no terms of use for its documents.
  It is an agency of the United States government. Quoted word for word:
  "When you visit our website to read pages or download information, we automatically collect and store the following information only:"
  "We use this information to measure the number of visitors to the different sections of our site, and to help make our site more useful to visitors."
  Nothing on the page speaks of automated requests or of reuse. Held internal until a person rules.

## Alberta Electric System Operator (Canada, not the United States)

- **Every row and every figure of Alberta's says Canada**: the entity is written "Alberta Electric System Operator
  (Canada)" on every row, and the summary gives its figures in a section of its own.
- **The source.** The monthly "Connection Project List", one workbook a month, each named for its month, linked from
  `https://www.aeso.ca/grid/transmission-projects/connection-project-reporting/`.
- **Confirmed on the current copy.** Its columns are "Status", "Project Name", "Planning Area", "Cluster", "Project
  Type", "MW Type", "Stage", "CA Modelled", "Inclusion", "Applied On", then megawatts and in-service dates for up to
  three energizations. A project's name begins with its project number (P and a number), which stands in every copy.
  The MW Type marks a load: `Load`, and from 2024 `Data Load`, `Distribution Load` and `Industrial Load`.
- **What is not taken.** A generator listed with a load (`Gas + Data Load`). The MW Types `DTS` and `STS`, of which
  the list says: "DTS and STS project types denote active contract change requests and are not governed by the
  Connection Process".
- **The date of a copy** is the day the workbook was last saved, by its own properties; for the `.xls` lists of 2016
  to 2018, the Last-Modified the publisher gave the file, as the Archive kept it. A day that is not near the month the
  file is named for (20 days before its first day to 45 days after) is the day the file was saved or posted again:
  the copy is then not used. Three were not used (February 2018, March 2026, April 2026).
- **Status.** `Recently Energized` and `Recently Cancelled` are the list's own words (a section's title from April
  2021, the column "Status" from 2025). Otherwise the status is the stage number as printed, `Stage 0` to `Stage 6`.
  **No copy says what a stage number stands for**, and the guide to the list is a separate document that was not in
  the approved pull: the numbers are placed on none of the five classes. So Alberta's intervals are request to
  energized, request to withdrawal, and the time shown in each numbered stage.
- **Megawatts** are the first load figure of the row as written ("Load MW", "DTS MW Change", the "DTS MW" of the
  first energization).
- **Phases.** The lists of 2016 to 2020 give a project one row a phase. Where its rows show one stage, the first row
  is read; where they differ, the project is not followed.
- **The sample.** The Archive lists 535 captures of 100 monthly files (September 2016 to September 2026). One capture
  a month was asked for, the latest of each file, the first month of each quarter first so that a pull stopped early
  would still hold one copy a quarter. All 100 were fetched, and the newest file (September 2026) once from the
  operator. 97 dated copies read, 26 September 2016 to 1 September 2026.
- **Followed.** 236 load projects seen, 213 followed; 22 seen in one copy only; 1 whose printed date differs between
  copies. 46 followed projects are in no later copy and no copy says why: each lower bound of theirs ends at the last
  copy that held the project and is not a wait still running.
- **Terms.** The page the site's footer links as Legal, "Terms and Conditions" (`https://www.aeso.ca/legal/`, saved 9
  October 2026 00:41:30 UTC, sha256 `43ac55d5dd8f91bc7872977f9e5bf5402719e2bc2f1a40ced1c6e37c179aa8f2`). Quoted
  word for word:
  "All material on this Web site is protected by copyright."
  "The material may be used and copied for non-commercial, personal or educational purposes, provided that the material is not modified and that copyright notices are not deleted."
  "Any other use of this material without the AESO's written permission is prohibited."
  Nothing on the page speaks of automated requests. The use here is research and nothing of Alberta's is published:
  held internal. Whether this project's use is "non-commercial" is the owner's to weigh.

## ISO New England: nothing can be followed

- Its terms were read first (`https://www.iso-ne.com/legal-privacy`, saved 9 October 2026 00:43:38 UTC, sha256
  `553276137bf1aeed92031e4b0b20d43634864d0696dbc302e7b48f5080982c72`). Quoted word for word:
  "By using this website, you signify your assent to these Terms and Conditions."
  "You are also hereby put on notice that the Content is protected by copyright under United States laws."
  "Any duplication of the Content or non-personal use may violate copyright, trademark, and other laws."
  Nothing on the page forbids an automated request.
- Its posted queue (`https://irtt.iso-ne.com/reports/external`) was then read once, by one plain request (saved, sha256
  `1f93220d5653001eece1c959efe193a504a71905802bd62d79dba2e36fa048bf`). Its columns: "Cluster", "QP", "Updated", "Type",
  "Requested", "Alternative Name", "Unit", "Fuel Type", "Net MW", "Summer MW", "Winter MW", "County", "ST", "Op Date",
  "Sync Date", "W/D Date", "POI", "Serv", "SIS", "I39", "TO Report", "Dev", "Zone", "FS", "SIS", "OS", "FAC", "IA",
  "Project Status", "Status", "Jurisdiction".
- It lists 1,751 requests, and the Type of every one is G (1,569), ETU (170) or TS (12): generators, elective
  transmission upgrades and transmission service. **No row is a load.** A queue of generators cannot say how long a
  load waited: no dated copy of it was asked for, and no wait was made from it.

## Pennsylvania's utilities: no queue found published

- Listings only, four requests to the Internet Archive, nothing of theirs fetched: every address of the sites of PPL
  Electric Utilities, PECO, Duquesne Light and FirstEnergy that names a large load or a queue.
- PPL Electric: one capture of one tariff rule about large load interconnections (August 2026): a rule, not a queue;
  not opened. FirstEnergy: Maryland's generator and community solar queues. Duquesne Light: style files of its site.
  PECO: nothing. A listing that returns nothing may be the listing's limit, not the Archive's holdings.
- No other lead was taken in its place: none of session 155's other listings names a queue of loads.

## The pull of session 165, against its ceilings

| Source | Requests | Bytes | Rows of requests read |
|---|---|---|---|
| Internet Archive: Bonneville's workbook, 21 distinct captures | 21 | 4,110,437 | 5,901 |
| Internet Archive: Alberta's monthly list, 100 captures | 100 | 5,996,029 | 3,371 |
| Internet Archive: 4 listings for Pennsylvania's utilities | 4 | 11,420 | 0 |
| Bonneville: its interconnection page, its privacy page, the current workbook | 3 | 469,425 | 458 |
| Alberta's operator: its project reporting page (twice), its Legal page (twice), the current list | 5 | 345,113 | 0 more (the current list is the same file as the Archive's capture of it: 95 rows, counted once) |
| ISO New England: its queue page, its Legal and Privacy page, the posted queue | 3 | 3,808,850 | 0 (1,751 generator and transmission rows seen, none a load) |
| **Session 165** | **136** | **14,741,274** | **9,730** |
| **All three sessions, against the ceilings** | **378 of 1,500** | **86,698,732 of 3,221,225,472** | **10,705 of 1,500,000** |

- The Archive was asked at most once every 2.5 seconds, by one process at a time. No 429 and no 503. Every answer was
  200. No login, CAPTCHA or browser check was met. No picture was met among these copies, and none was read.
- Every request carried the contact string "ERW research project, github.com/SamuelEnrique/erw" and no address of a
  person. No request to misoenergy.org; no PJM Data Miner or API request.
- Rows are counted as session 155 counted them: the rows of load requests read from each distinct copy. Counting
  every row of every copy read instead (generators too) gives 49,980 (Bonneville 23,007, Alberta 26,973), still far
  inside the ceiling.
- The Internet Archive's terms are quoted on the one-page summary ("The pull, and the terms") and are unchanged.
- Each saved file is listed in `warehouse/raw/large_load_waits/captures.csv` (not in git) with its address, sha256 and
  retrieval time; each request in `requests.csv` beside it.

## What stays internal, and what a tracked file may hold

No request, project name or megawatt of a request of any publisher here is in a tracked file: the summary and this
note give counts and days only. The table, the copies and the working files beside the table are on the data machine.
