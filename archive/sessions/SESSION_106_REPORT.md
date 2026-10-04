# Session 106 report: the datacenter tracker, version 2

**Built and on the live site, in review at `/datacenters/v2`.** The approved pull was made: `ercot_large_load_status`, 29 rows of the 20,000 ceiling, USD 0. The page shows ERCOT's large load approved and energized over time, with its source and date, beside the facilities already held, and says plainly that a request is not a built facility. **It does not show load requested over time, because ERCOT does not publish that as a number** (first point). One deploy and one load; the 25 live pages differ only in `/network`'s hourly stamps.

## Read these first

1. **"Load requested" is not in the table, and I did not get it another way.** ERCOT publishes no list of requests: its monthly "Large Load Interconnection Status Update" is a slide deck, and the queue by status (no studies submitted, under ERCOT review, planning studies approved, approved to energize, observed energized) is a picture of a chart in the PDF and in the PowerPoint file alike (the file of 26 March 2026 holds 17 pictures and no chart data). Reading the bars off a picture would be an estimate, and it would take a model. So the table holds what each report states in words, which is three figures: the MW approved to energize, and the peak ERCOT has observed from those loads, measured two ways. The page says "Load requested is not held" and why. The one figure for requests that a report states in words is on the page as a quotation: 137 new submissions, "approximately 140,000 MW of new Large Load by 2036" (13 March 2026).
2. **What the figures say.** By ERCOT's report of 26 March 2026, 9,042 MW of large load had its approval to energize and ERCOT had observed 4,004 MW of it running, 44 percent. On 28 May 2025 the two were 6,874 and 3,489 MW. Approvals rose by 2,168 MW in ten months; the load observed running rose by 515 MW.
3. **The series stops in March 2026.** No status update is on the meeting pages of TAC or the working group after 26 March. ERCOT's own slides to TAC of 26 August 2026 say that on 3 August it "issued a Market Notice pausing the Batch Zero study process" and "paused approvals to energize data centers or virtual currency mining facilities (crypto facilities) that are 75 MW or greater". Whether the monthly report has stopped or moved I do not know. The page says both things.
4. **ERCOT's reports hold two things that cannot be right, and both are now in the register of known faults** (26 faults). The report of 27 August 2025 states a simultaneous peak (3,733 MW) above the non-simultaneous one (3,694 MW), which its own definitions rule out. And the reports of 21 January, 25 February and 13 March 2026 name their months as "January 2025", "February 2025" and "March 2025"; the report of 26 March says "March 2026" and gives other figures for the month. The table dates each figure by its report's day and keeps the month as ERCOT wrote it beside it.
5. **`/shoulder` on production is right now.** At 21:10 UTC its own check passes, 3,470 of 3,470: the hour of cache turned. Sessions 103 to 105 reported it as still showing the earlier table; that was the cache and nothing else.

## The pull

`warehouse/connectors/ercot_large_load_status.py`. One run: 4 index pages (the working group's and TAC's, this year and last), 47 meeting pages and 22 documents, one request a second, all to `ercot.com`; 10 status updates found, one of them twice (on a meeting's page and in a zip). Before it, to find where the reports are: about 45 requests to the same site by hand (the Large Load Integration page, the data products page, the meeting pages, three documents, the terms). No other publisher was asked for anything. ERCOT is not paused; the connector asks the pause list first.

| | |
|---|---|
| Table | `ercot_large_load_status`, series, entity `ercot:large_load` |
| Rows | 29, of a ceiling of 20,000 |
| Reports | 9: 28 May, 30 July, 27 August, 17 October, 19 November 2025; 21 January, 25 February, 13 March, 26 March 2026 |
| Variables | `approved_to_energize_mw` (9), `observed_nonsimultaneous_peak_mw` (9), `observed_simultaneous_peak_mw` (9), `new_submissions_count` (1), `new_submissions_mw` (1) |
| Each row | dated the day on its report's first page; `source_url` is the document's address (a file in a zip as the zip's address and the file's name); `x_month_as_written`; `x_document` |
| Validator | exit 0, no warning |
| Records | in coverage (131 tables), the archive and the public Redivis draft; nothing released |

**License: public.** ERCOT's terms (`https://www.ercot.com/help/terms`, read today): "The publicly available contents of this website may be used, reproduced, and redistributed, provided that the contents are not modified and that you maintain all copyright and other notices contained in the contents, including this Agreement. Notwithstanding the foregoing, raw data provided in public portions of this website may be used, reproduced, and redistributed in compilations, charts, and analyses without maintaining such notices."

Rules of the reading: a document is read only when its first page says "Large Load Interconnection" and "Status Update"; a figure stated twice with two values fails the run; a report that lacks a sentence gives no row for it; nothing is filled. Method: `docs/methods/ercot_large_load_status.md`.

## The page

`/datacenters/v2`, in review, in the battery page's layout.

- **ERCOT's section, with its source and date:** a sentence, three headline numbers (approved to energize, observed running, served at one moment), a chart of the three by report, a table of the nine reports each linked to its document, and four plain notes: load requested is not held and why; the one figure for requests in words; the report that contradicts itself; the pause of 3 August 2026.
- **Beside it, the facilities already held, with their source and date:** 359 datacenter sites, 39 in Texas, a size stated for 24 (20,370 MW), one of them in Texas (1,400 MW); 275 from operators' lists, 81 from news, 3 from queues; the Texas sites in a table; a link to the tracker as it was for every site.
- **Never added.** One is megawatts ERCOT has approved, with no customer named; the other is sites by name, most with no size. The page says so.
- **"A request is not a built facility"** is in the page's lead, in bold, and again under "What this does not tell you", with: an approval is not one either.

The older tracker, `/datacenters`, is untouched.

## The deploy and the load

| Step | Result |
|---|---|
| `task/106-datacenters-v2`, run 37234497541 | passed, merged (`c73cac0`), deployed; Vercel accepted it |
| `before-106` against `after-106` | 6 differences, all `/network`'s hourly stamps |
| Load of `ercot_large_load_status` (29) and `known_data_faults` (26), under the lock | both matched; both under `review_hold`, their sources held off `/terms`; the database 807.1 MB before and after |
| `after-106` against `after-106-load` | **0 differences** |
| On production, internal view | `/datacenters/v2` renders with data (111 figures), `/datacenters` and `/data/faults` as before; all closed to a visitor |

## Tests and checks

- `tests/test_session106.py`, 13 tests: each sentence on text made for the test (no document of ERCOT's is in the repository); the simultaneous sentence is not taken for the non-simultaneous one; a figure stated twice with two values fails; only a status update is read; the day is the first page's; the same report twice is one row; a meeting still to come is not asked for; the ceiling, the license and the pause check; the site's copy is the table turned on its side, figure for figure; the page's sentence and what it flags (the one impossible report, the three with the wrong year); the page; the hold.
- Every session's tests on this machine: 758 ran; one fails and is not this session's (`test_interchange_ceiling`, as before).
- The site: `tsc` exit 0, the build exit 0, the route check on this machine's build 0 failed.

## Errors and decisions

1. **A first rebuild from the saved documents lost each row's address** (it wrote the saved file's name in its place). The reader now takes each document's address from the raw store's own list, and the table was rebuilt; every `source_url` begins with `https://www.ercot.com/`.
2. **The vintage was a bare date** and the validator warned; it is a full timestamp now.
3. **ERCOT's own definitions of the two observed peaks are quoted, not paraphrased.** "A load facility of 75 MW or greater" is quoted from ERCOT's Large Load Integration page as it reads today; I did not find the definition the 2025 reports used and do not claim it.
4. **The page reads a site copy of the table,** like the other new pages (`site/data/large_load_status.json`, `warehouse/derived/large_load_snapshot.py`); a connector writes CSV only.
5. **No model call. Model spend USD 0.00.** No force push. MISO stays paused.

## For Samuel

1. **Load requested over time** needs one of three things: ERCOT to publish the status report's numbers as a file (Protocol 3.2.7 has it make the report; I found it only as slides); your word that the bars may be read off the pictures, with the error that carries; or another publisher's count. I would ask ERCOT (LargeloadInterconnection@ercot.com is on the report's last slide).
2. **The series after March 2026.** Worth one look at the next TAC meeting (28 October 2026) for a status update; the connector will find it if it is posted under a name like the others.
3. **The older connector `ercot_large_load.py`** still fails each week with "ERCOT publishes no request-level large-load list". That is true and it is noise in the run status; it could be retired in favour of this one.

Energy Research Warehouse (ERW), session 106, on the old laptop (`samueloldlaptop`, data role), 2026-10-04 from about 20:40 to 21:15 UTC, unattended.
