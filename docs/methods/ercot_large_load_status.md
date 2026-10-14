# ERCOT's large-load status: what its monthly report states in words

The table `ercot_large_load_status`, the connector `warehouse/connectors/ercot_large_load_status.py`, and the review
page `/datacenters/v2`. Session 106. An approved pull: ceiling 20,000 rows, USD 0.

## What ERCOT publishes

ERCOT's Large Load Integration team presents a "Large Load Interconnection Status Update" to the Technical Advisory
Committee (TAC) and the Large Load Working Group (LLWG). It is a slide deck, posted as a PDF or a PowerPoint file on
the meeting's page, alone or inside a zip of the meeting's materials.

- **There is no request-level list.** Session 17 found that Nodal Protocol 3.2.7 has the report aggregate requests,
  customer data being confidential. That is still so.
- **The queue by status is a picture.** Each deck charts the queue by status: "No Studies Submitted", "Under ERCOT
  Review", "Planning Studies Approved", "Approved to Energize but Not Operational", "Observed Energized". The charts are
  images in the PDF and in the PowerPoint file alike (the file of 26 March 2026 holds 17 pictures and no chart data).
  **The ERW does not read a number off a picture,** so the load requested, by status, is not in the warehouse.
- **Three figures are stated in words in every deck,** and the table holds them.

## The table

`ercot_large_load_status`, series shape, entity `ercot:large_load`. One row per figure and report, dated the day on the
report's first page.

| Variable | ERCOT's sentence | What it is |
|---|---|---|
| `approved_to_energize_mw` | "Of the N MW that have received Approval to Energize" | Load ERCOT's operations have approved to take power |
| `observed_nonsimultaneous_peak_mw` | "ERCOT has observed a non-simultaneous monthly peak consumption of N MW in <month>" | "The sum of the maximum value for each individual load per month": "how much approved load ERCOT believes is now operational" |
| `observed_simultaneous_peak_mw` | "ERCOT has observed a simultaneous monthly peak consumption of N MW in <month>" | "The maximum value of the sum of all the individual loads per month": "the maximum amount of large load that ERCOT has had to serve at a single point in time" |
| `new_submissions_count`, `new_submissions_mw` | "ERCOT has recently received N new LLI submissions. Preliminary review indicates these total approximately M MW" | Stated once, in the report of 13 March 2026 |

`x_month_as_written` keeps the month the sentence names, as ERCOT wrote it; `x_document` the file; `source_url` the
file's address (a file inside a zip as `<zip address>#<file name>`).

**As pulled on 13 October 2026 (session 217): 38 rows from 12 reports, 28 May 2025 to 19 June 2026.** (As pulled on
4 October 2026: 29 rows from 9 reports, to 26 March 2026.)

| Report | Approved to energize, MW | Observed, each load's own peak, MW | Observed together, MW | Month as written |
|---|---|---|---|---|
| 2025-05-28 | 6,874 | 3,489 | 3,441 | May 2025 |
| 2025-07-30 | 7,150 | 3,820 | 3,632 | July 2025 |
| 2025-08-27 | 7,502 | 3,694 | 3,733 | August 2025 |
| 2025-10-17 | 7,502 | 4,126 | 3,800 | October 2025 |
| 2025-11-19 | 7,502 | 4,185 | 3,795 | November 2025 |
| 2026-01-21 | 8,786 | 3,977 | 3,765 | January 2025 |
| 2026-02-25 | 8,876 | 3,998 | 3,846 | February 2025 |
| 2026-03-13 | 9,042 | 3,883 | 3,801 | March 2025 |
| 2026-03-26 | 9,042 | 4,004 | 3,522 | March 2026 |
| 2026-04-24 | 9,042 | 4,008 | 3,701 | March 2026 |
| 2026-05-21 | 9,062 | 3,900 | 3,701 | May 2026 |
| 2026-06-19 | 8,927 | 3,900 | 3,675 | June 2026 |

The report of 24 April 2026 names its month as March 2026 (its data "is current as of April 22"); the approved figure
fell between May and June 2026 (9,062 to 8,927 MW), the first fall in the series.

The footnote (session 271, the owner's ruling of 14 October 2026). Where the approved figure falls from one report to
the next, the site's copy (`site/data/large_load_status.json`, `warehouse/derived/large_load_snapshot.py`) carries a
`note` on the later report, computed from the two rows: today one, on the report of 19 June 2026, "Approved to
energize fell by 135 MW from ERCOT's report of 2026-05-21 (9,062 MW) to this one (8,927 MW)." The note says nothing of
why: ERCOT's deck does not state a reason. The pages that read the file (`/cost-of-power`, `/datacenters/v2`) show it
once their code reads the field (`Report.note` in `site/lib/largeload.ts`). The guard (the same session): the connector
also runs on the data machine's daily run, so a new report is read within a day of ERCOT posting it; the monthly job on
the runner and the Monday watch of ERCOT's large-load page are kept.

The report of 13 March 2026 also states 137 new submissions totalling approximately 140,000 MW "of new Large Load by
2036", which "will be reflected in future reports".

## Rules

- A document is read only when its first page says both "Large Load Interconnection" and "Status Update".
- A figure is taken from the first sentence that matches its pattern. A deck that states one figure with two values
  fails the run. A report that does not hold a sentence gives no row for it. Nothing is filled.
- A figure is dated by the day on its report's first page, never by the month its sentence names.
- The same report found twice (on a meeting's page and in a zip) is one row.
- The run stops before writing past 20,000 rows.

## Where the reports are found

The meeting pages linked from ERCOT's pages for the LLWG (`/committees/tac/llwg`) and for TAC (`/committees/tac`),
this year and last. On each page: a document whose name says TAC Report, status update or large load, and any zip
whose name says large load or LLWG, opened and searched the same way. On 4 October 2026: 4 index pages, 47 meeting
pages and 22 documents, one request a second; 10 status updates found, one of them twice.

**Where the reports went after March 2026 (session 217, 13 October 2026).** Through March 2026 the Large Load
Integration team's deck was posted on TAC's meeting page as "<Month> TAC Report" (`March-TAC-Report.pdf`,
`March-TAC-Report-Updated_03262026.pptx`). From April 2026 it is posted on the LLWG's own meeting page as
"<Month> <day> LLWG Report" (`April-24-LLWG-Report_042426.pptx`, `May-21-LLWG-Report.pptx`,
`June-19-LLWG-Report.pptx`), each with the same first page, "Large Load Interconnection Status Update, Large Load
Integration Team". The connector's document pattern named "TAC Report" and not "LLWG Report", so the pull of 4 October
2026 read those meeting pages and passed the decks by; the pattern names both since session 217, and the connector
runs with the monthly job (`warehouse/run_monthly.sh`, the first daily run on or after the third of each month). The
LLWG's "LLWG Report" zips on TAC's pages hold the working group chair's own update, not the status update, and give no
row (a deck is read only when its first page says "Large Load Interconnection Status Update"). The LLWG meeting pages
of 23 July, 21 August and 17 September 2026 carry no status update as of 13 October 2026: ERCOT's own slides to TAC of
26 August 2026 say that on 3 August 2026 it "issued a Market Notice pausing the Batch Zero study process" and "paused
approvals to energize data centers or virtual currency mining facilities (crypto facilities) that are 75 MW or
greater". Whether the monthly report paused with them is not known; the monthly pull will find it where it reappears
on those pages.

## What the reports hold that cannot be right

Both are in the register of known data faults (`known_data_faults`):

- **27 August 2025:** the simultaneous peak (3,733 MW) is above the non-simultaneous one (3,694 MW). By the report's own
  definitions it cannot be.
- **Early 2026:** the reports of 21 January, 25 February and 13 March 2026 name their months as 2025. The report of
  26 March says "March 2026" and gives other figures for the month than the report of 13 March.

The table holds each figure as the report states it.

## License

Public. ERCOT's terms (`https://www.ercot.com/help/terms`, read 4 October 2026): "The publicly available contents of
this website may be used, reproduced, and redistributed, provided that the contents are not modified and that you
maintain all copyright and other notices contained in the contents, including this Agreement. Notwithstanding the
foregoing, raw data provided in public portions of this website may be used, reproduced, and redistributed in
compilations, charts, and analyses without maintaining such notices."

## The page

`/datacenters/v2`, in review: ERCOT's section (the three figures over time, a table of the reports, what is not held
and why) and, beside it, the datacenter sites the ERW already holds (`datacenter_facilities`), each with its source
and its date. The two are never added: one is megawatts ERCOT has approved, with no customer named; the other is sites
by name, most with no size. The page says plainly that a request is not a built facility. It reads the site's copy of
the table (`site/data/large_load_status.json`, `warehouse/derived/large_load_snapshot.py`).

## To keep it current

`python warehouse/connectors/ercot_large_load_status.py`, then `python warehouse/derived/large_load_snapshot.py`, once
a month. About 75 requests. It is not in the daily run.

## Tests

`tests/test_session106.py`: each sentence on text made for the test; a figure stated twice with two values fails; a
document that is not a status update is not read; the day on the first page; the same report twice is one row; the
ceiling; the site's copy is the table turned on its side; the page's sentence and counts.
