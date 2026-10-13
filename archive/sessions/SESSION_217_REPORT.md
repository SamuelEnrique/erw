# Session 217 report: ERCOT's large-load series, brought current

13 October 2026, from 02:40 UTC, unattended, on lab-desktop (the data machine), the fourth session of the chain of 12 October, evening. Branch `task/217-large-load-status`. Model spend USD 0 (no model call). Pulls: ERCOT, through the existing connector `warehouse/connectors/ercot_large_load_status.py` under the data lock (ceiling 20,000 rows; 4 index pages, 47 meeting pages and 25 documents, one request a second: 76 requests, 02:50 to 02:53 UTC), and 5 probe requests before it (three LLWG Report decks and two TAC "ERCOT Reports" zips, to find the report; `runs/session214/ercot_probe/`). Writes to the stores: `ercot_large_load_status` (the validator, the coverage row, the archive, the Redivis draft, the live set) and `site/data/large_load_status.json`.

## Read these first

- **The series runs to ERCOT's report of 19 June 2026: 38 rows from 12 reports** (29 rows from 9 reports, to 26 March 2026, before). Three reports were added: 24 April, 21 May and 19 June 2026. Nothing newer is on ERCOT's LLWG and TAC meeting pages as of 13 October 2026 (the LLWG pages of 23 July, 21 August and 17 September carry no status update).
- **Why the series stopped: ERCOT moved and renamed the deck, and the connector was on no schedule.** Through March 2026 the Large Load Integration team's "Large Load Interconnection Status Update" was posted on TAC's meeting page as "<Month> TAC Report"; from April 2026 it is on the LLWG's meeting page as "<Month> <day> LLWG Report" (`April-24-LLWG-Report_042426.pptx`, `May-21-LLWG-Report.pptx`, `June-19-LLWG-Report.pptx`). The connector's document pattern named "TAC Report", "Status Update", "Large Load Interconnection" and "LLI Status", not "LLWG Report", so the pull of 4 October 2026 read those meeting pages (they are in its raw manifest) and passed the three decks by. And `warehouse/run_monthly.sh` said "a person pulls" this table: no run script named the connector.
- **The fix, two lines:** the pattern names "LLWG Report" too (a deck is still read only when its first page says "Large Load Interconnection Status Update", so the LLWG chair's own "LLWG Report" zips on TAC's pages give no row, as before); and the connector is the first step of the monthly job (`warehouse/run_monthly.sh`, a soft step before the six builders, so `large_load_snapshot` reads the table it has just extended). The monthly job runs on the GitHub runner with the first daily run on or after the third of each month; the runner reaches ERCOT (it pulls ERCOT's prices daily).
- **Every place that quoted the March figure now quotes June's, the March figure kept as history:** `docs/accelerator/evidence_pack.md` item 15 and its ERCOT row, `docs/methods/ercot_large_load_status.md` (the table of reports, and where the reports went), `site/lib/chat/pagefiles.ts` (Ask ERCOT's guide line), `docs/coverage.md` (rebuilt), `site/data/large_load_status.json` (rebuilt: the pages `/datacenters/v2` and `/cost-of-power` read it).
- **The landing:** with session 216, on the one branch `task/216-217-rulings-large-load` (session 216's decision 5), cut from `main` after session 215's merge (`81047142`); the before snapshot, the push and the result are under "The landing". 0 differences expected: no page is live, and `/datacenters/v2` and `/cost-of-power`, which read the rebuilt file, are in review.

## The series, month by month (MW)

Approved to energize against observed running (the non-simultaneous monthly peak: the sum of each approved load's own highest hour, "what ERCOT believes is now operational"), from `ercot_large_load_status` as pulled on 13 October 2026. The month is the one the report's sentence names, as ERCOT wrote it (three reports of early 2026 name their months as 2025; the register of known data faults holds them).

| ERCOT's report | Approved to energize, MW | Observed running, MW (each load's own peak) | Running as a share of approved | Observed together, MW | Month as written |
|---|---:|---:|---:|---:|---|
| 2025-05-28 | 6,874 | 3,489 | 51% | 3,441 | May 2025 |
| 2025-07-30 | 7,150 | 3,820 | 53% | 3,632 | July 2025 |
| 2025-08-27 | 7,502 | 3,694 | 49% | 3,733 | August 2025 |
| 2025-10-17 | 7,502 | 4,126 | 55% | 3,800 | October 2025 |
| 2025-11-19 | 7,502 | 4,185 | 56% | 3,795 | November 2025 |
| 2026-01-21 | 8,786 | 3,977 | 45% | 3,765 | January 2025 (sic) |
| 2026-02-25 | 8,876 | 3,998 | 45% | 3,846 | February 2025 (sic) |
| 2026-03-13 | 9,042 | 3,883 | 43% | 3,801 | March 2025 (sic) |
| 2026-03-26 | 9,042 | 4,004 | 44% | 3,522 | March 2026 |
| **2026-04-24** | **9,042** | **4,008** | **44%** | **3,701** | March 2026 ("current as of April 22") |
| **2026-05-21** | **9,062** | **3,900** | **43%** | **3,701** | May 2026 |
| **2026-06-19** | **8,927** | **3,900** | **44%** | **3,675** | June 2026 |

- The approved figure fell between May and June 2026 (9,062 to 8,927 MW), the first fall in the series; ERCOT's deck does not say why. On 3 August 2026 ERCOT paused approvals to energize datacenters and crypto facilities of 75 MW or more (its slides to TAC of 26 August 2026).
- The new submissions sentence (137 requests, about 140,000 MW) stands once, in the report of 13 March 2026; no later report states one.
- The share column is this report's arithmetic (observed over approved, rounded), not a figure of ERCOT's.

## What was done, in order

1. The probe: the raw manifest of the 4 October pull (`warehouse/raw/ercot_large_load_status/20261004T204155Z/`) showed the April to September LLWG and TAC meeting pages had been read and which documents were fetched; the saved meeting pages named the "LLWG Report" decks that were not. Five requests fetched three decks and two TAC zips; the connector's own functions read the three decks as status updates with the three figures each, and the zips as nothing.
2. The connector's `DOC` pattern: `LLWG[-_ .]*Report` added, with the reason in a comment.
3. The pull under the data lock: `lock.py run -- ercot_large_load_status.py` (`runs/session214/lls_pull.out`): 13 status updates found (the January deck twice, on a page and in a zip: one row), 38 rows, 9 new, 29 replaced in place with the same values.
4. The stores: `table_stores.py ercot_large_load_status` (validator, coverage row, archive, Redivis draft: each exit 0, `runs/stores_ercot_large_load_status_*.out`); the live set: `load.py --only ^ercot_large_load_status$ --no-vacuum` (match, 38 rows); the site's file: `large_load_snapshot.py` (12 reports, built 2026-10-13T02:54:16Z).
5. The schedule: `run_monthly.sh` (above). `tests/test_session114_part2` holds the six builders of the loop and that no step of `scheduled.py` runs a connector but EIA's two and the standing pull; the new line is a soft step of the connector itself, outside `scheduled.py` and before the loop, so both pins stand (41 tests of `test_session114_part2` and `test_session106` pass).
6. The quotes (above).

## Checks

| What | Exit | Notes |
|---|---|---|
| The connector (the pull) | 0 | 38 rows of 20,000, 12 reports |
| `table_stores.py ercot_large_load_status` | 0 | validate, coverage, archive, redivis each 0 |
| `load.py --only ^ercot_large_load_status$ --no-vacuum` | 0 | match, 38 rows |
| `large_load_snapshot.py` | 0 | |
| `bash -n warehouse/run_monthly.sh` | 0 | |
| `python -m unittest tests.test_session114_part2 tests.test_session106` | 0 | 41 tests |
| `python -m unittest tests.test_session153` (Ask ERCOT's guide) | see the closing lines | the guide line changed |

## Decisions made without you

1. **The connector is scheduled as a soft step of its own in `run_monthly.sh`, not as a job of `scheduled.py`.** `scheduled.py`'s rule (and `test_session114_part2`'s pin) is that its steps make no request but EIA-930's two and the one standing pull; a second named pull there would have meant changing that rule. The monthly job already runs where the cadence and the reach are right (the runner, the third of the month). What the step lacks: on the runner the table is not restored from the archive before the pull, so the runner's copy holds the reports of this year and last (the connector reads those two years of meeting pages); until 2027 that is the whole series, and the archive and Redivis keep every row.
2. **The report's share column is computed here** (observed over approved), rounded to the percent, so the evidence pack's "44 percent" has its arithmetic in the open; ERCOT states no share.
3. **The month as written is kept as ERCOT wrote it,** the April report's "March 2026" and the early-2026 "2025" months included (the known data faults register already holds the latter).
4. **The five probe requests were made before the pull,** to find the report rather than widen the pattern blindly; they are counted above.
5. **`docs/methods/ercot_large_load_status.md` keeps its line about the 3 August pause** and says the monthly pull will find the report where it reappears.

## For Samuel's ruling

1. Whether the connector should also run on the data machine's daily run as a guard (ERCOT's meeting pages are about 76 requests a run), or the monthly job on the runner is enough.
2. The approved figure's fall of 135 MW between the May and June reports: a footnote on `/cost-of-power` and `/datacenters/v2`, or left to the table.
3. Whether the status update has stopped with the 3 August pause (no deck since 19 June on either page): a person could ask ERCOT's Large Load Integration team, or the monthly pull simply waits.

## Files

- Changed: `warehouse/connectors/ercot_large_load_status.py`, `warehouse/run_monthly.sh`, `docs/methods/ercot_large_load_status.md`, `docs/accelerator/evidence_pack.md`, `site/lib/chat/pagefiles.ts`, `site/data/large_load_status.json`, `tests/test_session106.py` (the April report's month, "March 2026", joins the three reports of early 2026 the page flags as mismatched), and the stores' metadata (`warehouse/metadata/coverage.csv`, `docs/coverage.md`, `sources.csv`, `archive_manifest.csv`, `redivis_uploads.csv`; the connector's status rows go to `warehouse/metadata/status/ercot_large_load_status.json`, which the daily run folds into `run_status.csv`).
- `runs/session214/` (this machine, not in git): `ercot_probe/` (the saved page and the five documents), `lls_pull.out`, `lls_stores.out`, `lls_load.out`, `lls_snapshot.out`, `tests_217a.out`; `runs/stores_ercot_large_load_status_*.out`; `warehouse/raw/ercot_large_load_status/20261013T025017Z/` (the documents as read).
