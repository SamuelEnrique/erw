# Session 199 report: a green main that stays green, and the landings

Old laptop (`samueloldlaptop`, a code machine), Sunday 11 October 2026 from about 18:42 Pacific (12 October, 01:42 UTC). Unattended. Branch `task/199-green-main`, from `main` at `fd079835`. Model spend USD 0, no model call. No pull, no request to a publisher. No warehouse data written, no data lock taken. Nothing of the repository deleted.

## Read these first

- **`main` failed for six reasons, not five. All six are repaired.** The sixth is newer than the prompt: tonight's Roundup (`391a8a42`, the first weekly run since session 119) wrote 31 lines of the chooser's watch list into the weekly gallery files, and session 182's flow tests failed on it (4 failures and 1 error). The whole suite on a clean copy: 3,340 tests, exit 0.
- **The ruling is applied as written, in three kinds.** Frozen files for the datacenter note and the Ask ERCOT questions; the seller's CSV held to the capture file of the build its own header names; session 149's role test skipped where no role file is.
- **Three small dated files are new, under `docs/methods/figures/`:** 12 KB, 67 KB and 211 KB. The third is larger than "a few kilobytes": "if perfectly foreseen" cannot be recomputed without the hourly prices of 2025 and 2026 (decision 1).
- **One page changed in what it would show, and it is in review:** `/analysis` offers its ten templates again and not the 31 watch lines. The weekly run is not changed; whether the gallery should hold those lines is yours (ruling 1).
- **Two things need the data machine** (rulings 2 and 3): the seller's CSV is exported by no scheduled run, and the weekly run writes the watch lines into the gallery.

## What to review

- The rule and the three files: https://github.com/SamuelEnrique/erw/blob/main/docs/methods/figures/README.md
- The note, the new paragraph "The files these figures are of", under "The default case": https://github.com/SamuelEnrique/erw/blob/main/docs/methods/datacenter_pays_algorithm.md
  - On the site, signed in to the review view: https://erw-flame.vercel.app/data/methods/datacenter_pays_algorithm
- The flow, signed in: https://erw-flame.vercel.app/analysis
  1. Scroll to "Ask for an analysis".
  2. Open the list of step one. Its last group holds ten templates, as last week. No entry named for a watched measure (Henry Hub natural gas, WTI crude oil, Brent crude oil) is in it.
- The frozen files:
  - https://github.com/SamuelEnrique/erw/blob/main/docs/methods/figures/2026-10-10/datacenter_pays_inputs.json
  - https://github.com/SamuelEnrique/erw/blob/main/docs/methods/figures/2026-10-09/ask_ercot_pages_inputs.json
  - https://github.com/SamuelEnrique/erw/blob/main/docs/methods/figures/2026-10-07/generator_capture_months.json
- The two lines on the interpreter: https://github.com/SamuelEnrique/erw/blob/main/docs/machines.md (after "Setup checks git") and https://github.com/SamuelEnrique/erw/blob/main/queue/CHAIN_TEMPLATE.md (above rule 1).
- GitHub's checks: https://github.com/SamuelEnrique/erw/actions/workflows/code-branch.yml

## What failed on main, and what each test does now

| Test | Why it failed | Now |
|---|---|---|
| `test_session190`, the note's figures (1) | The note says USD 29.72 "if perfectly foreseen", 109 hours off. The day's files, with eight more days of October 2026, give 29.80 and 105 | The page's own library recomputes every figure of the note from `2026-10-10/datacenter_pays_inputs.json`. No window, no skip |
| `test_session190_replication`, the note's example (1) | The same | The second implementation, in Python, on the frozen hours: 33.73, 31.46, 100 hours, 29.72, 109 hours, 57 percent |
| `test_session153`, the questions (1) | Three build stamps of 7 October against files rebuilt on 11 October | Recomputed from `2026-10-09/ask_ercot_pages_inputs.json`, which the questions name. All 20 compared, p14 and every stamp included |
| `test_session183_replication` (2) | The CSV holds 48 hours of October 2026, the day's `capture.json` 216 | Held to the exporter's record of the capture file's build that the CSV's header names (built 2026-10-07T21:50:35Z, sha256 `1fdade557e6edce3`) |
| `test_session149`, the refusal by role (1, clean copies only) | A clean copy has no `.venv`, so the script cannot read the role | Skipped where `.erw/machine.json` is absent, with the reason |
| `test_session182_flow` (4 and 1 error, since tonight's Roundup) | 40 entries in the gallery's index where the flow expects its 9 public templates | The flow offers its ten templates alone; the tests hold the templates' part of the weekly file and say the rest are watch lines |

## What was built

- `docs/methods/figures/`: the three files and a README with the rule, each file's writer, the document that names it and the test that reads it.
- Each frozen file was made from the page files git holds at the commit its document was written from, by the writer's own code: `6835d806` (the note), `5c7c7b56` (the questions), `b765f33d` (the capture file; its sha256 is the one the CSV states).
- `site/scripts/freeze-datacenter-note.mjs`: writes the note's file. It refuses unless the kept hours give, to the last digit, the whole files' figures for five flexible loads under the rule and foreseen (10 of 10 equal).
- `warehouse/chat/eval/ercot_pages_expected.py`: `--write` freezes the day's inputs first, computes the questions from the frozen file and names it in `built_from.inputs`. `--check` is as it was (the day's files).
- `warehouse/derived/generator_hourly_export.py`: writes the capture file's months of its build at each export. Not run here (it needs the tables).
- `docs/methods/datacenter_pays_algorithm.md`: one paragraph naming its frozen file. No figure changed.
- `site/lib/analysisflow.ts` (`ofTheFlow`), `site/app/analysis/page.tsx`, and the flow's two check scripts.
- `tests/test_session199.py` (7 tests). Tests changed, none removed: 149, 153, 182 (flow), 183 (replication), 190, 190 (replication).
- `.gitattributes`: the frozen files keep LF.

## Checks run

Outputs under `runs/s199/` (not in git).

| Check | Exit | Result |
|---|---|---|
| `scripts/precheck.py --what "session 199"` | 0 | on duty |
| The four named modules on `main`, before, each its own command | 1, 1, 1, 1 | 1, 2, 1 and 2 failures (the second of 190's replication is this machine's stale tables, not GitHub's) |
| GitHub's failed run 38172045438, read | | the five of the prompt |
| `tests.test_session153`, clean copy | 0 | 18 tests, 2 skipped |
| `tests.test_session183_replication`, clean copy | 0 | 39 tests, 1 skipped |
| `tests.test_session190`, clean copy | 0 | 11 tests |
| `tests.test_session190_replication`, clean copy | 0 | 36 tests, 1 skipped |
| `tests.test_session149`, clean copy | 0 | 39 tests, 1 skipped (the role file) |
| `tests.test_session199` | 0 | 7 tests |
| Whole suite, clean copy, at `e75ae3d4` | 1 | 3,340 tests, 4 failures and 1 error, all `test_session182_flow`: the sixth cause, found here |
| `node scripts/test-analysis-flow.mjs` | 1, then 0 | 3 failed; then all passed, "31 lines" of the watch list counted |
| Whole suite, clean copy, at `10ebe03b` | 0 | 3,340 tests, OK, 237 skipped |
| Site build, at `e75ae3d4` and at `10ebe03b` | 0, 0 | no "statement timeout" line |
| `check-analysis-flow.mjs`, local build | 1, then 0 | the check itself looked for `watch_henry_hub`; then 227 of 227 |
| `scripts/freeze.py status` | 0 | no freeze |

- **Not run:** the generator's exporter and the questions' `--write` (both need the tables of a data machine). The Stata do-files (Stata is not on this machine).
- **Not verified:** `check-analysis-flow.mjs` was run against the build of `10ebe03b`; the commit after it (`7fa19e0d`) changes that check script alone.
- Still failing on this machine's main copy and nowhere else: `test_session116.Records.test_the_tables_on_this_machine_add_up` (this machine's own tables stopped on 10 October when it gave up the data role). It is skipped on a clean copy and on GitHub. Not changed.

## The landing

Added by the second push (the snapshot pair and GitHub's run are under "The landings").

## Decisions made without you

1. **The note's frozen file is 211 KB, not a few.** It holds the North load zone's real-time and day-ahead prices for 2025 and 2026 to 10 October, the 30 days before, and 142 months as sums. The year's 100 dearest hours cannot be chosen again from less. The page files it stands for hold 15 MB. Reversible: delete the hours and keep the months, and the flexible figures go unchecked.
2. **A sixth cause was repaired, outside the prompt's five,** because `main` cannot be green without it. I chose the reversible side: the page ignores the watch lines; the weekly run and its files are untouched.
3. **The two table questions of the Ask set (p04, p11) are compared as committed,** no longer recomputed from the tables on the machine: a table is a day's data file too. `--check` on the data machine still recomputes them.
4. **Session 149's role test now skips on GitHub as well** (the runner holds no role file). The refusal on the runner is the test before it and still runs there.
5. **Beyond the five, in the same modules, three more comparisons with the day's files were removed:** the mirror's pinned lines in 190's replication (now the lines' shape, any figure); the CSV against the tables (now a data machine, or tables named on purpose); 153's figures "of its file" (now the frozen copy).
6. **Left reading the day's files, on purpose:** the seller's CSV against `merchant_snapshot.json` (no scheduled run rebuilds it; last built 3 October); the datacenter CSV against the page's files (the data machine exports both in one run); the Texas delivery charges and the resource layers (a session writes them, no schedule).
7. **Date of each folder:** the day of the files quoted, which is the day of the newest build stamp read, not the day of writing.
8. **The exporter was changed but not run:** the next export writes its own record. The record of today's CSV was written by the exporter's function from the bytes git holds.

## For Samuel's ruling

1. The weekly run now writes the watch list's 31 lines into `docs/analysis/templates.json` and `docs/analysis/gallery/index.json` (session 119's loader, first run 11 October). Should the gallery hold them? Until you rule, `/analysis` leaves them out and `warehouse/analysis/run.py` is unchanged.
2. For the data machine: `site/public/seller/erw_2026_generator_hourly.csv` is exported by no scheduled run, so it stays at 2 October while `capture.json` moves daily. Add `generator_hourly_export.py` to `run_data_machine.sh` after `dm_capture_price`, as session 190 did for the datacenter CSV? Not added from this machine.
3. For the data machine: `eval_ercot_pages.json` is of 9 October. Before the next Ask evaluation, run `ercot_pages_expected.py --write` there (it writes the new frozen file with the questions).
4. `site/scripts/test-ask-tables.mjs` still sets the committed questions against the day's page files. It runs only where the site's packages are (not on GitHub's test step, not on a clean copy). It will fail there when November begins. Freeze it too?
5. The note's frozen file at 211 KB: keep (decision 1), or months only?
