# Session 311: the licensing sweep

19 October 2026, 12:05 to about 12:35 UTC, unattended, on lab-desktop (the data machine), the seventh session of the chain of 19 October. Model spend USD 0. Nothing was sent to anyone.

## Read these first

- **Every one of the 201 tables in coverage has a verdict in `docs/licenses.md`** (the prompt's 199, plus sessions 306's two). 137 agree with their coverage flag and 44 disagree. 19 are not settled, because a publisher on them was not read or its page states no terms of reuse. 1 is internal by the ERW's own choice. Before the sweep: 135, 42, 23 and 1.
- **38 publishers' pages were read in one request each** (reads 44 to 81, of a ceiling of 60), each after its host's robots file. 34 answered: 22 of them state a sentence on reuse, cut by code from the saved page (each checked as a literal part of the page), and give 24 verdicts (DOE's page serves its newsroom too, and the IMF's read 13 serves PortWatch); 12 state no terms of reuse. 4 did not answer: CME Group (no connection), Energy-Storage.news, FERC and OPEC (HTTP 403). The Virginia SCC is paused and was recorded as not asked, with no request.
- **Five tables' verdicts changed:** `battery_sourced_ranges` (not settled, now may be public: NLR's notice), `large_load_rules_internal` and `texas_delivery_charges` (not settled, now needs written permission: Oncor, CenterPoint and AEP allow personal use only; internal already, so they agree), `portwatch_chokepoint_transits` (not settled, now may be public through the IMF's terms; **flagged internal, the flag stricter**), and `grid_stress_days` (now needs written permission for its NYISO, ISO-NE and MISO prices, **the flag looser**, like the hub price tables it is built from).
- **The 42 permission tables and FRED stand as they were.** **No record of Samuel's emails of 14 October is in the repository** (searched: `docs/`, `archive/sessions/`, `warehouse/metadata/`), so none is noted against a table: for the morning note.
- From 21 October, `grid_stress_days` is the 41st table shown as "license needed" (`license_status.csv`, `site/data/license_status.json`, `docs/state/licenses_2026-10-21.md`, rebuilt by `licenses.py status`).

## What to review

1. `warehouse/metadata/license_verdicts.csv`, the 24 rows of session 311 (23 noted "Session 311.", and `IMF PortWatch`): the sentence, the verdict today and if the ERW sells anything. Two readings to check: Oncor's "without modification ... or reformatting of any kind" read as needs permission (ERCOT's like clause allows compilations of raw data and was read as public in session 205), and AESO's "not modified" read as public today.
2. `IMF PortWatch` takes the IMF's page (read 13), from a web search showing PortWatch's contact page sending terms questions to the IMF; PortWatch's own page was not read.
3. `scripts/licenses.py`: `nyiso mis` (a news feed of NYISO's notices) maps to NYISO; `grid_stress_days` names its six grids by hand.

## Pulls against their ceilings

- Terms pages: **38 requests of 60** (record rows 44 to 81; the record holds 80 requests in all across the sweeps of sessions 205, 307, 308 and 311).
- Robots files: 38 (one per host before its page; the paused host was not asked).
- The addresses came from a web search by a subagent (WebSearch only, no request to a publisher).

## The pages that state no terms of reuse

Read and kept, with no verdict (their tables stay "not settled"): the Arizona Corporation Commission (a 12-character page), BPA and the Illinois Commerce Commission (privacy statements), Oregon.gov, Pennsylvania's and Grant PUD's privacy pages, PUCO and the PUC of Texas (pages drawn by script; 4,000 characters of navigation), TNMP's privacy page, Texas.gov (linking only), Electrek (9to5's privacy page) and the Federal Register's policy page. Not read: CTVC, the Public Advocates Office, the Georgia PSC and T&D World (no address found), CME, Energy-Storage.news, FERC, OPEC.

## Checks

| What | Exit | Notes |
|---|---|---|
| `scripts/precheck.py --what "session 311"` | 0 | |
| `license_read.py --list runs/s311/to_read.csv --ceiling 102` | 0 | 38 requests |
| the verdicts' sentences against the saved pages | 0 | 0 not found |
| `licenses.py tables --headers warehouse/output`, `write`, `check`, `status` | 0, 0, 0, 0 | 201 tables, 66 publishers with a verdict, 0 problems |
| tests 205, 207, 215, 240, 248, 264, 306 | 0 | 91 tests; two pins of 207 follow (40 to 41 tables "license needed") |
| the whole suite (`unittest discover -s tests`) | 1 | 4,408 tests, 10 failures: the four standing (51, 125, 165, 267) and six that followed session 310's refreshes: the release package (275, twice: `grid_stress_days` now held), the site's copies of the mix and clean tables (94, 122: not rewritten by the builders' table runs), CAISO's first priced month (122: July 2023 since sessions 273 and 307) and the storage note's day count (120). Each fixed (below) |
| `mix_profile.py --snapshot-only`, `mix_clean.py --snapshot-only` | 0, 0 | the site's copies from the tables (no table written) |
| `release_v1.py`, `--check` | 0, 0 | 126 tables in v1, 41 held out |
| tests 94, 120, 122, 151, 205, 207, 275 | 0 | 123 tests |

## The landing

- freeze 0; before `s311-before` 12:24:42 UTC; merged origin/main; pushed 12:24:49 (`1bc96560`); deployment 7173700231 success 12:26:59; after `s311-after` 12:32:02; compare: **0 differences on 25 pages** (expected: every page is in review).

## Decisions made without you

1. **A page with no sentence on reuse gets no verdict**, so its tables stay "not settled" rather than public by default.
2. **`portwatch_chokepoint_transits` keeps its internal flag** although the verdict allows it: a stricter flag is the safe side, and opening a table is yours.
3. **`grid_stress_days` keeps its public flag** and joins the "license needed" list from 21 October, as its inputs do under the by-grid rule.
4. **`licenses.md`'s summary line names each sweep's ceiling** instead of session 205's 40 alone.

## For Samuel's ruling

- The weekly `dm_clean_energy` (session 271) and the new `dm_mix_profile` rebuild the tables without the site's copies (`--snapshot`), so the copies fall behind each week until a session rewrites them: add `--snapshot` to both steps, or keep the copies by hand.

- Which of the 42 permission tables your emails of 14 October covered: no record of them is in the repository.
- `portwatch_chokepoint_transits`: open it (the IMF's terms allow it with attribution), or keep it internal.
- The 19 tables not settled: write to the agencies whose pages state no terms, or accept public-records law as the ground.

## Files

- New: this report; `runs/s311/` (the lists, robots record, extracted sentences; not in git).
- Changed with the suite's follow-ups: `site/data/mix/`, `site/data/clean/` (the site's copies), `docs/methods/ercot_storage_realtime.md` (the 196 days), `docs/redivis/release-v1.md` and `docs/redivis/release-v1/` (126 tables, 41 held), `tests/test_session120.py`, `tests/test_session122.py`.
- Changed: `warehouse/metadata/license_reads.csv`, `license_verdicts.csv`, `license_tables.csv`, `license_status.csv`, `site/data/license_status.json`, `docs/licenses.md`, `docs/state/licenses_2026-10-21.md`, `scripts/licenses.py`, `tests/test_session207.py`; session 310's report (its landing).
