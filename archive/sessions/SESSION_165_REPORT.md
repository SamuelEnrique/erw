# Session 165 report: more queues followed

Run on 9 October 2026 (UTC), 00:33 to 01:40, unattended, last of the chain 162 to 165. An agent built it in a
working copy of its own to a written brief (`runs/session165/BRIEF.md`); I ran the locked writes and the landing.
`large_load_waits` stays internal: on no page, in no live set, in no public dataset.

## Four things to know first

- **Two of the three queues were followed, not three.** Bonneville Power Administration and Alberta's operator
  (Canada, kept apart). The third could not be: ISO New England's posted queue holds 1,751 requests and none is a
  load, and no Pennsylvania utility was found to publish a queue of loads. No other lead was taken in its place.
- **Bonneville's list is of "line and load interconnections", not of large loads alone.** No copy says which
  request is a large load. And it has no copy between March 2013 and March 2022, so a wait that ended in those nine
  years has a range as wide as the gap.
- **Alberta's terms allow "non-commercial, personal or educational purposes" only.** Everything of Alberta's is
  held internal. Whether this project's use is non-commercial is yours to weigh.
- **Alberta's stage numbers (0 to 6) are explained in no copy**, and its guide was not in the approved pull. Its
  stages are kept as printed and placed on no class.

## Verdict: the method works on both new queues; the table grew from 491 rows to 2,622

What is left, exactly:

1. Your word on Alberta's terms, and on Bonneville's (its site links a privacy policy and no terms of use).
2. Alberta's guide to its list, one document, would place its stages: for you to approve.
3. Bonneville's own "5-6 years" (request to service) is set beside no measured figure: a range of years is not one
   figure. Yours to rule.
4. No scheduled pull keeps each new copy.
5. The one page under `docs/accelerator/` grew from 160 lines to 284 and was not trimmed.

## Measured waits by entity and stage, in days, with the count behind each

United States:

| Entity | Interval | Requests | Measured | Days | Lower bounds (at least) |
|---|---|---|---|---|---|
| New York ISO (held, unchanged) | request to energized | 56 | 2 | 1,028 to 1,151; 1,270 to 1,339 | 51 (105 to 3,636) |
| New York ISO (held) | system impact study | 54 | 22 | median at least 414, at most 680 | 32 (30 to 522) |
| Grant County PUD (held) | request to energized | 1 | 0 | | 1 (2,659) |
| Bonneville | request to energized | 233 | 76 | median at least 2,045.5, at most 3,950.5 | 148 (232 to 7,857) |
| Bonneville | the same, end between copies of 2022 to 2026 | | 30 | median at least 2,868, at most 3,243.5 | |
| Bonneville | the same, end in the nine years with no copy | | 46 | median at least 1,477.5, at most 4,776.5 | |
| Bonneville | request to study | 268 | 75 | median at least 193, at most 449 | 4 (266 to 1,245) |
| Bonneville | request to construction agreement | 152 | 29 | median at least 1,363, at most 1,755 | 123 (232 to 7,857) |
| Bonneville | request to withdrawal | 166 | 89 | median at least 606, at most 973 | 0 |

Canada, apart:

| Entity | Interval | Requests | Measured | Days | Lower bounds (at least) |
|---|---|---|---|---|---|
| Alberta | request to energized | 173 | 38 | median at least 540, at most 579 | 109 (98 to 3,038) |
| Alberta | request to withdrawal | 39 | 37 | median at least 629, at most 662 | 0 |

- Bonneville: 458 requests seen, 433 followed, from 22 copies (27 May 2010 to 8 October 2026).
- Alberta: 236 projects seen, 213 followed, from 97 monthly copies (26 September 2016 to 1 September 2026).
- Of Alberta's 109 lower bounds, 77 are still listed and 32 left the list with no word: those 32 are not waits
  still running, and the page says so.
- **Alberta's data centres, by its own mark:** 52 projects ever marked "Data Load", none shown energized; 38
  followed and still waiting, at least 186 to 876 days.
- The 491 rows held before come out byte for byte (a hash in a test).

## The pull against its ceilings

| Source | Requests | Bytes | Rows of requests |
|---|---|---|---|
| Internet Archive, Bonneville's workbook, 21 captures | 21 | 4.1 MB | 5,901 |
| Internet Archive, Alberta's list, one capture a month | 100 | 6.0 MB | 3,371 |
| Internet Archive, 4 listings for Pennsylvania utilities | 4 | 11 KB | 0 |
| bpa.gov (its page, its privacy page, the current workbook) | 3 | 0.5 MB | 458 |
| aeso.ca (its pages, the current list) | 5 | 0.3 MB | 0 more |
| iso-ne.com (its queue page, its terms, the posted queue) | 3 | 3.8 MB | 0 (no load) |
| **Session 165** | **136** | **14.1 MB** | **9,730** |
| **Sessions 155, 160 and 165 together** | **378 of 1,500** | **82.7 MB of 3 GB** | **10,705 of 1,500,000** |

- Every answer was 200: no 429, no 503, no login, no CAPTCHA, no browser check. Nothing was refused.
- The Archive was asked at most once every 2.5 seconds, one process at a time.
- Contact string exactly "ERW research project, github.com/SamuelEnrique/erw". No address of a person sent. No
  MISO request, no PJM request. No picture was read.

## Terms quoted (each page saved with its hash and retrieval time)

- **Bonneville** (its privacy page, the one legal page its footer links; no terms of use for its documents): "When
  you visit our website to read pages or download information, we automatically collect and store the following
  information only:" Held internal until you rule.
- **Alberta Electric System Operator** (`aeso.ca/legal`): "All material on this Web site is protected by copyright."
  "The material may be used and copied for non-commercial, personal or educational purposes, provided that the
  material is not modified and that copyright notices are not deleted." "Any other use of this material without the
  AESO's written permission is prohibited." Nothing on automated requests. Held internal.
- **ISO New England** (`iso-ne.com/legal-privacy`): "You are also hereby put on notice that the Content is protected
  by copyright under United States laws." "Any duplication of the Content or non-personal use may violate copyright,
  trademark, and other laws." Nothing of its queue is in the table.
- The Internet Archive's terms are quoted in session 155's report and in the method note.

## Model spend: USD 0 of 0

- No code of the session calls a model.

## Locked writes and checks

- Under the lock, one command each, exit 0: the table's write (2,622 rows), coverage, the archive, the internal
  Redivis draft (nothing released). The validator: exit 0. Two lines were added to `sources.csv`, both internal.
- The loader's dry run answers "no live-set table matches": the table is in no live set, as intended.
- On the main copy, where nothing skips: 78 tests of sessions 155, 160 and 165, passed.
- **Tests of earlier sessions changed on purpose:** session 155's ceiling (2,000,000 to your 1,500,000), its pattern
  for entity names, its count of pages asked (9 to 11); session 160's ceiling.
- No request, name or megawatt of Bonneville's or Alberta's is in a tracked file (a test holds it).
- New: `docs/methods/large_load_waits.md`. No method note of this table stood there before.

## The landing and the snapshot (one landing for sessions 162 to 165)

- Pushed 01:30:08 UTC as `task/162-165-chain` (`1aa3d3c`): checks passed (run 37870073120), merged as `717ae0f`.
  **Vercel: "Deployment has completed"** at 01:37:50 UTC. No freeze. No force push.
- **Snapshot before** (`162_before`, 01:29:27) **and after** (`162_after`, 01:37:57), 25 addresses: **0 differences**;
  no checked number moved (3,357 keys). The charts of `/storage`: 0 differences. Nothing was reverted.
- The whole suite in a clean copy of the landed commit: 2,610 tests, passed. This session changed no site file.

## Decisions made without you

1. ISO New England tried first for the third queue, then Pennsylvania by four listings; no replacement lead.
2. Alberta sampled at one capture a month, all 100 monthly files.
3. Every Bonneville line-and-load request followed, none called a large load.
4. An interval whose start is first shown after its end is not a row (one Bonneville request).
5. Alberta's current copy was pulled: its terms do not forbid automated access, and it is held internal.

## The five most interesting numbers

1. **2,868 to 3,243.5 days**: Bonneville's median from request to energized, for the 30 whose end lies between
   copies of 2022 to 2026. About eight to nine years.
2. **540 to 579 days**: Alberta's median from request to energized, on 38 projects. Canada.
3. **0 of 52**: Alberta projects marked "Data Load" that are shown energized; 38 still wait.
4. **0 of 1,751**: requests in ISO New England's posted queue that are a load.
5. **491 to 2,622**: rows of the table, the first 491 unchanged to the byte.
