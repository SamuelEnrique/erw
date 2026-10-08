# Session 155 report: measured wait times

Run on 8 October 2026 (UTC), unattended, in the chain 155 to 159. An agent built it in a working copy of its own to
a written brief (`runs/session155/BRIEF.md`); I ran the locked writes and the landing. The table is internal: on no
page, in no live set, in no public dataset. No NYISO request, name or megawatt is in any tracked file.

## Five things to know first

- **Two large loads could be followed from request to in service, both in New York: between 1,028 and 1,151 days,
  and between 1,270 and 1,339 days.** About three to three and a half years. Two requests is not a distribution.
  51 more New York requests are still waiting, each for at least 105 to 3,636 days.
- **A reading of yours I had to settle: "its load-project sheets".** NYISO's `Load Projects` sheet exists only in
  the 3 newest copies. The same requests stand in every older copy of the workbook as rows of type `L` with the
  same queue positions, and the agent followed those: 37 copies from September 2014 to September 2026. With the
  named sheet alone there are 3 copies and no measured wait. Yours to rule; one filter restricts it.
- **ERCOT's reports cannot be followed at all.** Its 11 large-load status reports give megawatts by stage and name
  no request. A stage's megawatts over time is not a request's wait, and none was made from them.
- **Grant County PUD's public queue holds one load request**, not yet energized: at least 2,659 days since its
  queue date. Two of its copies are pictures of the page; no number was read off a picture.
- **12 documents were fetched that are not copies of a queue** (the agent's link patterns were too wide): 5 Grant
  PUD tariff and agreement PDFs from the queue's folder and 7 documents of an ERCOT working group meeting. Public,
  plain requests, inside every ceiling, kept unread; the connector now asks only for the queue's own file.

## Verdict: a wait can be measured this way; tonight it is New York's stages, not a national figure

- **What the copies say well is the stages.** 22 system impact studies followed from pending to approved: a median
  of at least 414 and at most 680 days.
- **Against the stated expectations:** of the 107 held, only NYISO's can be put beside a measurement. Against its
  "nine months" for a system impact study: 20 of 22 measured studies were longer, counted from the first copy that
  shows the study pending. Counted as the time shown in progress alone: 5 longer, 4 shorter, 13 that cannot be told
  apart. The two measures differ because no copy shows the day NYISO's statement starts from. The other 104
  expectations are of entities with no request followed here.
- **What is left, exactly:**
  1. Your ruling on the older sheets' type `L` rows (above).
  2. **The Internet Archive's terms grant access "for scholarship and research purposes only"** and state no rule
     on automated requests; its terms page is drawn by a script today, so the words were read from the Archive's
     own capture of 1 June 2024. Yours to weigh.
  3. Grant County PUD states no terms of use for its documents; its footer reads "All Rights Reserved". Its one
     row is internal with the rest.
  4. **What more could be followed** (listings only; none opened): Bonneville's interconnection queue workbook (16
     dated copies from 2022 to 2026, 7 more from 2010 to 2013) and Alberta's monthly project list (535 copies;
     Canada). Whether either holds load requests with identifiers is not confirmed. Session 151's leads still
     stand: Pennsylvania's utilities' queues under the model tariff, ISO New England's posted queue if accepted.
  5. Keeping each new copy from this quarter on (a scheduled pull of the three addresses) is not built.

## The pull against its ceiling

| Pull | Ceiling | Read |
|---|---|---|
| Dated copies of the three queues, and the current copies | 3,000,000 rows; I added 1,500 requests and 3 GB | **975 rows** of requests; **96 requests**; 32.2 MB |

- The Internet Archive 75 requests (53 captures, 20 listings, 2 terms pages), ERCOT 11, Grant County PUD 9, NYISO
  1. One request every two seconds to the Archive at most; no 429 or 503 met. One listing failed (Bonneville's
  site, a reset) and was left.
- **Contact string: exactly "ERW research project, github.com/SamuelEnrique/erw". No address sent.** No MISO or
  PJM request. No model call.
- NYISO: 67 captures listed, 37 distinct, 37 fetched. Grant County PUD: 7 queue PDFs and the current one; 5 read.
  ERCOT: 11 reports read.
- **Terms quoted** (each page saved with its hash):
  - Internet Archive (as captured 1 June 2024, "Terms of Use 31 Dec 2014"): "Access to the Archive’s Collections is
    provided at no cost to you and is granted for scholarship and research purposes only." and "you certify that
    your use of any part of the Archive's Collections will be limited to noninfringing or fair use under copyright
    law."
  - NYISO (the notice session 149 saved): "Access to this Web site does not confer any license or ownership
    interest in either the form or content of the Web site" (in full in session 149's report). No license: internal.
  - Grant County PUD (its privacy statement, the one legal page): "All information collected at this Web site or
    through this Service becomes a public record that may be subject to inspection by the public unless an
    exemption in law exists."
  - ERCOT: "The publicly available contents of this website may be used, reproduced, and redistributed, provided
    that the contents are not modified and that you maintain all copyright and other notices contained in the
    contents, including this Agreement." (checked against the page today).

## What could be followed

| Publisher | Copies read | Load requests seen | Followed | Not followed |
|---|---|---|---|---|
| New York ISO | 37 (September 2014 to September 2026) | 78 | 73 | 5 (seen in one copy only) |
| Grant County PUD | 5 | 1 | 1 | 0 |
| ERCOT | 11 | none listed | 0 | system totals only |

- A request is followed by its own queue position. A copy is dated by the day its publisher saved it, not by the
  day it was captured: dated by capture, statuses appeared to go backwards; dated by the workbook's own date, none
  does.
- **The table, `large_load_waits`: 491 rows.** Measured 159; lower bound 279; two copies only 5; upper bound 48 (a
  fourth label the agent added, for an interval whose end is bounded and whose start is before the oldest copy).
  Each row holds the two copies that bound each end.
- A measured duration is a range, "at least" to "at most": never a midpoint. A median is given only on 5 or more.

## The measured waits, New York ISO (days)

| Interval | Requests | Measured | Measured, days | Lower bounds (at least) |
|---|---|---|---|---|
| Request to energized | 56 | 2 | 1,028 to 1,151; 1,270 to 1,339 | 51 (105 to 3,636) |
| Request to construction | 52 | 4 | 1,153 to 1,222; 1,252 to 1,321; 2,270 to 2,326; 2,297 to 2,366 | 47 (105 to 2,881) |
| Request to first study status | 57 | 21 | median at least 26, at most 86 | 1 (152) |
| System impact study, pending to approved | 54 | 22 | median at least 414, at most 680 | 32 (30 to 522) |
| Request to agreement | 48 | 0 | | 47 (105 to 2,881) |
| Request to withdrawal | 17 | 6 | median at least 322, at most 760.5 | 0 |

- **By size** (megawatts as written in the last copy): followed requests under 20 MW 3; 20 to under 100 MW 24; 100
  to under 300 MW 28; 300 MW and over 19.
  - System impact study, pending to approved: 20 to under 100 MW, 9 measured, median at least 365, at most 498;
    100 to under 300 MW, 8 measured, at least 516.5, at most 716.5; 300 MW and over, 5 measured, at least 381, at
    most 664.
  - All four requests followed to "Under Construction" are of 300 MW and over; the two followed into service are
    smaller (one of 20 to under 100 MW, one of 100 to under 300 MW).
- Grant County PUD: one request; request to agreement at most 2,264 days; agreement to energized at least 395 days
  and running.
- Every figure by stage and size (81) is beside the table in the raw store; the one-page summary is
  `docs/accelerator/large_load_waits.md`, and `large_load_eighty.md` points to it.

## Model spend: none

- No model or API call from code. No cap was set for this session.

## The landing

- No site file changes. Under the lock, nothing released and nothing loaded: `large_load_waits` 491 rows;
  validator, coverage, the archive, the internal Redivis draft: exit 0 each; the table and its sources are in the
  live set's hold lists.
- The landing follows with its snapshot; a line is added here.

## Checks

- `tests/test_session155.py` 34 tests and session 151's, on the main copy where nothing skips: passed. The whole
  suite in the working copy: 2,234 tests, passed.
- A request seen in two copies gives a lower bound and is labeled; no duration uses a midpoint; a figure on fewer
  than 5 is not a median; the summary's counts equal the table's (tests).

## Decisions made without you

1. The older sheets' type `L` rows followed (above).
2. A copy dated by its publisher's own saved date.
3. A fourth label, "upper bound".
4. Grant County PUD's row held internal, its terms being silent.
5. The 12 stray documents kept unread rather than deleted (nothing is deleted without you).

## The five most interesting numbers

1. **1,028 to 1,151 days, and 1,270 to 1,339 days**: the only two large loads followed from request to in service.
2. **20 of 22**: system impact studies that took longer than the nine months NYISO says to expect, counted from
   the first copy that shows the study pending.
3. **3,636 days**: the longest wait still running, a New York request of 300 MW and over, under construction for
   at least 1,310 of them.
4. **0**: requests that can be followed in ERCOT's reports.
5. **37 copies over 12 years, against 3**: what following the load rows through the older sheets gives, against
   the named sheet alone.
