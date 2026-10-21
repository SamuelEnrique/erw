# Session 534 report: the tests that pin a day

21 October 2026, about 18:30 to 20:25 UTC, unattended, on samueloldlaptop (the code machine), in the worktree `C:\Users\lossa\Documents\erw-534` on `wip/534-s` (from `origin/main` at `c8aa37ff`). Chain 024 (`queue/done/024-night-21-october-code.md`), session 534. Model spend USD 0; no pull from any publisher; no warehouse data written; nothing under `site/app`, `site/lib` or `site/components` changed, so no page moves and no screenshot was due.

## Read these first

- **Main fails ten tests in a clean copy since the data machine's run of today** (commit `c8aa37ff`, "Page files 2026-10-21", 18:28 UTC: its findings step recomputed every finding card and it rebuilt the page files). At its parent `4086d63c` the same six modules pass (83 tests, exit 0). The orchestrator (session 542) named the same ten, found by session 535, and asked this session to fix them: **all ten are fixed on `wip/534-s`** (commit `4b79b22a`), each reading its own fixture or the state it checks. The list, with what each pinned, is under "The tests that pinned the day's files".
- **`scripts/suite_shifted.py`** runs the suite with the clock moved forward (scripts/clock_shift/: a `sitecustomize` for every python process the suite starts, and a `Date` shim for every node process through `NODE_OPTIONS`; file times move with the clock), never patching a test. With it, at 7, 30 and 365 days ahead, **one test was found that fails only on a later day**: `test_session119.ThePick.test_too_little_past_falls_back_to_the_level_rule_and_says_so`, from 18 November 2026 (its fixture's weeks end on 4 October and the level rule keeps a headline 45 days). Fixed: the class reads the Sunday of 2026-W41 as today. After it, nothing fails only shifted, at 7, 30 or 365 days.
- **`test_session156` (node test 10) is not date-driven**: it fails the same at 0 and at 30 days. The recorded read of `newest_quarter_hours` has `market=like.ercot*` and the tool now sends `entity=like.ercot:*`, with no date in either: a filter change, not the clock. Its fixtures are chain 021's session 424's and were not touched.

## What to review

- The runner and its shim: `scripts/suite_shifted.py`, `scripts/clock_shift/sitecustomize.py`, `scripts/clock_shift/date_shift.cjs`; their test `tests/test_session534.py` (8 tests). On GitHub: `https://github.com/SamuelEnrique/erw/tree/wip/534-s/scripts/clock_shift`
- The eleven test fixes: `tests/test_session119.py`, `153.py` with `site/scripts/test-ask-tables.mjs`, `167.py`, `173.py`, `174.py`, `182.py`, `274.py`, `381.py`; the fixtures `tests/fixtures/session182/` and `tests/fixtures/session274/` (copied from `4086d63c`, real figures); one line in `.gitattributes` (the fixture CSV is read by its sha256: `-text`).
- To run it again: `.venv/Scripts/python.exe scripts/suite_shifted.py --copy <a clean worktree> --days 0 7 30 --out runs/<folder>`; `--tests test_sessionN ...` for a few modules. Exit 0 when nothing fails only shifted, 1 when something does, 2 when the shift could not be confirmed in a child.

## The tests that pinned the day's files

Each failed in a clean copy at `c8aa37ff` and passed at `4086d63c`; each passes at `4b79b22a`.

| Test | What it pinned | What it reads now |
|---|---|---|
| `test_session153` (node `test-ask-tables.mjs`, test 13) | the committed question p07's figure (14.66) against the day's `site/data/seller/capture.json` (14.69): the replay set a committed number against a page file the daily run rebuilds, which session 199's ruling forbids | the questions computed again from the copy's own files (`ercot_pages_expected.build`, nothing written), passed to the node test in `ASK_TABLES_DAY_SET`; run alone, a rebuilt page file's figure is held to be a number (as p14 was) and the resource layers are compared as before |
| `test_session167.TheFunctions.test_select_and_totals_are_the_files_own` | not a date: Python's `sum()` of floats is compensated since 3.12 and JavaScript's `+=` is not; the day's queue total sat near a half (762785 against 762786) | the test adds one by one in the file's order, as `lib/projectmap.ts` does |
| `test_session173.TheCards.test_the_three_cards_were_computed_on_the_data_machine_on_10_october` | `computed_at` starts with `2026-10-10T` | a UTC stamp on or after 10 October 2026 and not in the future; the CSV hash check is unchanged |
| `test_session174.TheCards.test_peak_hour_reads_the_ercot_shift_and_caiso_from_2024` | CAISO's first held year 2024 (held from 2023-07 since today) | the card's first held year is its first year read, no later than 2024, and a partial first year is not a line |
| `test_session182.C3TheDailyCardKeepsItsNumbers.test_every_old_number_is_unchanged` | the live card's 10 October numbers and stamp (n_days 405, now 417) | session 182's check on the card it was made against, `tests/fixtures/session182/batteries_curtailment_2026-10-10.json`; the day's card has the same set of figures |
| `test_session182.C3TheDailyCardKeepsItsNumbers.test_the_rows_are_the_rows_session_174_wrote` | the live CSV's rows hash (10 October's) | the fixture CSV against the fixture card and the rows hash; the day's CSV against the day's card's own `csv_sha256` and its r |
| `test_session182.TheGridsAndThePlaceholders182.test_a_panel_starts_where_its_prices_start` | CAISO's panel from 2024-09 (now 2023-07) | each panel's first value is its `first` and its title's "from" month; ERCOT and NYISO from 2019-01; the others no later than 2024-09; the peak-hour panels start in the same year |
| `test_session274.TheSpecs.test_every_number_is_the_charts` | the motion specs (rendered once, session 274) against the day's cards | the cards the specs were made from, `tests/fixtures/session274/cards_before_2026-10-21.json` |
| `test_session381.TheResearchReplication.test_it_runs_from_its_folder_without_the_cards` | three figures of 20 October as text (`-10.757`, `1081.24`, `3016.40`) | the replication's printed figure against the card JSON beside it |
| `test_session381.TheResearchReplication.test_a_planted_change_is_caught` | the cell `75.1796387567233` (now `75.17963875672332`) | the file's own "All technologies" withdrawn_pct, read and changed by 0.1 |

The six of 21 October named in the chain file (`166`, `446`, `448`, `132`, `442`'s issue table, the Digest numbers test) were fixed before this session (sessions 461 and 483, and the landing `7640c259`); none of them failed here.

## Checks

Every gate redirected to a file under `runs/chain_024/s534/`, never piped; the exit code read before the next step.

| Check | Exit | Result |
|---|---|---|
| `scripts/precheck.py --what "session 534"` | 0 | on duty until 2026-10-22 10:35 UTC |
| `tests.test_session534` | 0 | 8 tests |
| `suite_shifted.py --days 0 7 30` in a clean copy at `c2427b85` (`shift1/`) | 1 | 5,196 tests a run; base 10 failures; only shifted: `test_session119...level_rule` (+30) and `test_session321...mark_turns_failed_tables_into_gaps` (+7, +30; an artifact: file times were not yet shifted, fixed in the shim) |
| `suite_shifted.py --days 0 7 30 120 365 --tests test_session119 test_session321 test_session534` | 0 | after the fixes, nothing only shifted |
| `suite_shifted.py --days 0 7 30 365` in a clean copy at `e269e6f0` (`shift2/`) | 0 | 5,204 tests a run; nothing fails only shifted; the base's failures are the ten above and three `MemoryError`s (below) |
| `tests.test_session153` with the site's packages (a junction to the main copy's `node_modules`, gitignored) | 0 | 18 tests, the node test run with the day's questions: 14 of 14 |
| `node scripts/test-ask-tables.mjs` alone | 0 | 14 of 14 |
| `tests.test_session167`, `173`+`174`+`182`, `274`, `381` | 0, 0, 0, 0 | 59 + other modules, all pass |
| `node scripts/test-ask-ready.mjs` (session 156) at 0 and +30 days, in the main copy | 1, 1 | the same two failures both times: not date-driven |
| `suite_shifted.py --days 0 7 30` in a clean copy at `4b79b22a` (`shift3/`), the whole suite | 0 | 5,204 tests a run, OK (291 skipped) at 0, 7 and 30 days: the whole suite passes in a clean copy, today and on 28 October and 20 November |

Failures I did not cause, by the last line of their traceback:

- `test_session114.DealsPage.test_the_case_blind_reading_counts_every_tagged_deal`, `test_session114_part2.BuiltDate.test_each_page_prints_its_files_built_stamp` (`MemoryError`) and `test_session114_part2.Schedule.test_forcing_the_monthly_job_does_not_ask_whether_it_is_due` (`AssertionError: '' != 'yes'`): in the base run of `shift2` only, while the laptop was short of memory; they passed in the three shifted runs of the same copy.
- `test_session188_idle.TheGitHooks.test_a_machine_on_duty_in_a_marked_chain_sends_both_beats` (`AssertionError: Lists differ: ['beat', 'beat', 'chain'] != ['beat', 'beat', 'chain', 'chain']`): once, in the base run of `shift1`; a background hook's timing, passed in the five runs after.
- `test_session484` cannot import pyarrow's Parquet module ("An Application Control policy has blocked this file") on this machine, an environment block; it skips or fails as before, untouched.

## Decisions made without you

1. **The clock moves by whole days and keeps ticking**: "fixed dates seven and thirty days ahead" is read as the run's start plus 7 and 30 days (28 October and 20 November 2026), not a frozen instant, so a deadline loop in a test still ends.
2. **File times move with the clock** (`os.stat`, `os.lstat`, `os.fstat` add the shift, `os.utime` takes it off): the copy then behaves as one checked out on the shifted day, as GitHub's runner checks out a fresh copy. Without it `test_session321` failed only shifted for a reason no real day would give.
3. **pandas is imported first in every shifted python child**: its compiled classes subclass `datetime.datetime` when it is imported and the process dies (a stack overflow) if that is not the real type then; its `Timestamp.now`, `utcnow` and `today` are patched after. A string `"now"` given to pandas is not shifted; no code in the repository uses one.
4. **The suite's environment drops the keys that write** (the Supabase service key, the model's key, the mail key, GitHub's token), and runs in a clean copy with no `.env`, so a shifted test cannot write a row dated in the future or reach the model.
5. **A 365-day run was added** to the 7 and 30 the brief names, to find what breaks later: nothing more did.
6. **The ten state-pinned tests were fixed in this session** at the orchestrator's message; the six fixtures copied from `4086d63c` are the files as they stood, not values written for the tests.
7. **`test-ask-tables.mjs` run alone holds a rebuilt page file's figure to be a number**: the exact comparison is made by `tests/test_session153.py`, which computes the day's questions and passes them in; this follows session 199's ruling and session 159's p14.
8. **No landing**: the brief's "Land" is a push of `wip/534-s`; session 542 merges.

## For Samuel's ruling

- The motion proofs of session 274 (`motion/specs/`, `docs/research/motion/`) show the cards as they were before today's recompute; the test now holds them to those cards. Re-render them from the day's cards, or keep them as dated proofs.
- CAISO's prices on the finding cards now start in 2023-07 (they started 2024-09-01): the cards, their CSVs and their "why" text moved with it today, by the data machine's run; no page's text was checked against it in this session.

## Files

- `scripts/suite_shifted.py`, `scripts/clock_shift/sitecustomize.py`, `scripts/clock_shift/date_shift.cjs` (new); `tests/test_session534.py` (new).
- `tests/test_session119.py`, `153.py`, `167.py`, `173.py`, `174.py`, `182.py`, `274.py`, `381.py`; `site/scripts/test-ask-tables.mjs`; `tests/fixtures/session182/` and `tests/fixtures/session274/` (new); `.gitattributes` (one line).
- This report.
