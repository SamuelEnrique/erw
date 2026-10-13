# Session 252 report: the 16 waiting findings, verified

13 October 2026, from 10:40 UTC, unattended, on lab-desktop (the data machine), the first of two sessions (252 and 253). Branch `task/252-findings-verified`. Model spend USD 0: no model call. Pulls: none, no request to any publisher. Writes: none to the warehouse, none to the live set, none to the review list (it was read twice with the service key; no row and no state changed).

## Read these first

- **All 16 drafts reproduce exactly, and 5 of them should still be dropped.** `docs/reviews/findings-verified-2026-10-13.md`: one block a draft, strongest first. Verdicts: 4 strong, 7 usable, 5 drop.
- **Strong (approve as drafted):** ERCOT's dearest hour moving into the evening (24.9 to 71.0 percent of days, 2019 to 2025, every year the same way); its mirror at midday (one finding told twice: publish them together); negative prices at ERCOT North (0.57 to 2.56 percent of hours); the fall of 46,041 contracts in managed-money long positions in NYMEX natural gas in the week to 29 September, the largest of the 611 weeks held since January 2015.
- **Drop:** the District of Columbia's industrial price record (the sector is one customer, by the same table's customers count); the hunt's three spike drafts and its USD 1,000 hours draft (one interval a year, strength under half a typical yearly move, and 69 to 89 percent of each claim is the fall from 2019 to 2020 alone).
- **Session 251's new drafts: there are none.** The list held 16 rows at 10:42 and again at 10:49 UTC, the newest raised at 05:08:13 UTC by session 233. No report, branch or run folder of a session 251 is on this machine or on GitHub. If it runs later, three commands verify what it adds (in the document's last section but one).
- **One thing to fix before any hunt draft is approved:** its source line names every table its finding read. For an ERCOT draft that includes tables marked "license needed" from 21 October for other grids' rows. None of those rows is in a draft; the line says otherwise.

## What to review

- `docs/reviews/findings-verified-2026-10-13.md` on GitHub: https://github.com/SamuelEnrique/erw/blob/main/docs/reviews/findings-verified-2026-10-13.md
  1. Read "Read these first" (six bullets).
  2. Open https://erw-flame.vercel.app/internal/findings beside it (the internal view is needed: the form at `/internal/open`). Each block names its draft's rule, table and flagged date, which the page prints above each draft.
  3. For each block, read the last line (the verdict and its reason), then rule on the page: Approve, Dismiss or Ask for a full card. Nothing was ruled by this session.
- No page changed. `/internal/findings` shows what it showed.

## How it was checked

- **A hunt draft (8):** its own `.py` run on its own `.csv`, both as downloaded from the list; then the claim, the three tests, the card's numbers, the fact line and the caption computed again from that CSV and compared with the stored ones (45 values a draft, words character by character): 0 differ in 8 drafts. Then the CSV computed again from today's tables by the finding's own code: 8 years a draft, 0 differ.
- **A scanner draft (8):** it carries no file, so its table is its data. The series read again from `warehouse/output/` by the scanner's own reader, cut at the draft's scan date (10 October), the rule run again: 29 to 34 stored values a draft, 0 differ.
- **Robustness:** the hunt's three tests again, and five it does not run (year-to-year steps, rank correlation with the year, two-year ends, the claim without its first and without its last year, the year under way). For the scanner, by rule: plain standard deviations, the calendar month and the season for a record; other windows and the days after for a spike; every week held and the week after for a weekly change.
- **License:** the table's flag in `coverage.csv`, its row (or none) in `license_status.csv`, and the publisher's sentence in `docs/licenses.md`.

## Checks

| What | Exit | Notes |
|---|---|---|
| `python scripts/precheck.py --what "sessions 252 and 253"` | 0 | six of six; on duty |
| `python scripts/freeze.py status` | 0 | no freeze |
| `fetch_drafts.py` (twice: 10:42 and 10:49 UTC) | 0, 0 | 16 rows, all in state draft, both times |
| `verify_scanner.py`, first run | 1 | 7 of 8 exact; the CFTC draft was not raised again, because the table has gained a week since the scan. Not a fault of the draft: see decision 2 |
| `verify_scanner.py`, final | 0 | 8 of 8 exact |
| `verify_hunt.py`, first run | 1 | 1 of 8 exact by my first comparison, which was wrong: see decision 3 |
| `verify_hunt.py`, final | 0 | 8 of 8 exact from their own CSV, 8 of 8 rebuilt exactly from today's tables |
| `look_more.py`, `look_cftc.py` | 0, 0 | the customers count behind the District's price; Cleveland's weeks; the CFTC contract's two names |
| `build_doc.py` | 0 | 16 blocks |
| `python -m unittest tests.test_session252` | 0 | 7 tests |
| `python -m unittest discover -s tests` | 1 | 3,794 tests, 3 failures, 45 skipped, 472 s in the foreground: the three this machine always has (`test_session51`, `test_session125`, `test_session165`, which compare tables on this machine with committed files and are skipped on GitHub's runner); none in what this session wrote |

## Decisions made without you

1. **"Its own CSV" for a scanner draft is its table.** The scanner's drafts carry no CSV and no Python file (only the hunt's do). I rebuilt each from the table it names, with the scanner's own reader and rule. I did not write a second, separate implementation of the scanner's rules; the document says so under "Not done".
2. **The CFTC draft was run on its table as it stood at the scan.** Today's table holds the week of 6 October, which it did not hold on 10 October, so the newest change is no longer the flagged one. Cut after 29 September, all 34 stored values are equal. The block says this in its "Reproduced" line.
3. **One column reads back at 15 digits.** The row's own `value` column (double precision) comes back through the API as, for example, `46.027397260274`, where the card and the flag hold `46.02739726027397`. I compared that one column at 15 significant digits and say so in each block it touches (7 of the 8 hunt drafts). Every number in the card, the flag and the files is equal in full.
4. **The verdicts are mine, with the rule stated.** Strong: holds whichever way it was cut. Usable: true, with a limit the block names. Drop: with the reason. Where a draft passed the hunt's three tests and still fails (the four spike drafts), the block shows the numbers that fail it.
5. **The scripts and their results are in git beside the document** (`docs/reviews/findings-verified-2026-10-13/`), because `runs/` is not, and the document says "run again". They find the repository root from either folder.
6. **A test holds the document to its result files** (`tests/test_session252.py`): 16 blocks, the same ids, strongest first, the counts, every draft reproduced.
7. **No do-file was run:** there is no Stata on this machine (session 233 said the same).
8. **Sessions 252 and 253 land separately,** each with its own snapshots. Session 252's landing result is in session 253's report.

## For Samuel's ruling

1. The 16 drafts, with a verdict each: approve the four strong ones (the evening and midday drafts as one), dismiss the five to drop?
2. A floor on the hunt's strength of one typical yearly move (session 233's ruling 2): it would have kept exactly the four hunt drafts dropped here off the list.
3. A fourth test for the hunt: at least half of the change must remain when the first year is left out.
4. A guard for the scanner: a retail price series of a sector with fewer than five customers is not scanned (the District of Columbia's industrial sector is one customer).
5. The scanner splits a series when its node is renamed: the CFTC natural gas contract was compared over 241 weeks where 611 are held. Join on the contract code alone?
6. A hunt draft's source line should name only the tables its region's rows come from. Today it names tables that need a license from 21 October for other grids.
7. EIA asks for the line "Source: U.S. Energy Information Administration" with the date; the scanner's source line names the ERW table and EIA's route instead. Change the scanner's source line for EIA tables?
8. Session 251 left no trace on either machine by 10:49 UTC: was it run?

## Files

- New: `docs/reviews/findings-verified-2026-10-13.md`; `docs/reviews/findings-verified-2026-10-13/` (six scripts, what five of them printed, and the two result files); `tests/test_session252.py`; this report.
- Changed: none.
- On this machine, not in git: `runs/session252/` (the 16 drafts as downloaded, with their files and pictures).

## The landing

- Freeze: `python scripts/freeze.py status` exit 0, no freeze.
- The before snapshot, the push, the check run, the merge, the deployment and the after snapshot with its comparison are in session 253's report, under "The landing of session 252". Expected: 0 differences on the 25 pages (a document, six scripts and a test; no page, no table, no load).
