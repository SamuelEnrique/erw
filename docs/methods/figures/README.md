# Frozen figures

Energy Research Warehouse (ERW), session 199, 11 October 2026.

**The rule (the owner's ruling of 11 October 2026).** A test that a landing must pass never compares a committed figure with the day's data files. The page files under `site/data/` are rebuilt by the data machine's run every day; a Method note, a problem set or a replication file is written once and says which day's files it quotes. On 11 October 2026 the day's page files moved and five tests on `main` failed, so no branch could land.

**What is here.** One folder a day, named for the day of the files quoted. Each file holds the few inputs that a dated document's figures need, in kilobytes, never the page files themselves. The test recomputes the figures from the frozen file and compares them with the document. The pages go on showing the day's data.

| File | What it freezes | Written by | Named in | Read by |
|---|---|---|---|---|
| `2026-10-07/generator_capture_months.json` | The months of `site/data/seller/capture.json` (ERCOT, the hub average, real time, solar) in the build that `site/public/seller/erw_2026_generator_hourly.csv` was checked against | `warehouse/derived/generator_hourly_export.py`, at each export | the CSV's own header (the build and its sha256) | `tests/test_session183_replication.py` |
| `2026-10-09/ask_ercot_pages_inputs.json` | What the 20 questions of `warehouse/chat/eval_ercot_pages.json` read of five page files, and each flat load's months | `warehouse/chat/eval/ercot_pages_expected.py --write`, just before the questions | the questions' `built_from.inputs` | `tests/test_session153.py` |
| `2026-10-10/datacenter_pays_inputs.json` | The default case of `docs/methods/datacenter_pays_algorithm.md`: a flat load's months, and the hours of 2025 and 2026 that a flexible load's figures need | `site/scripts/freeze-datacenter-note.mjs` | the note, under "The default case" | `tests/test_session190.py`, `tests/test_session190_replication.py` |

**When a document is written again from newer files,** its writer writes a new frozen file in a new day's folder and the document names it. The older file stays: it is the record of what the older text quoted. Nothing here is edited by hand.

**How the first three were made.** From the page files as git holds them at the commit each document was written from, by each writer's own code: `b765f33d` for the capture file (its sha256 is the one the CSV's header states), `5c7c7b56` for the questions (every build stamp the question file states is that commit's), `6835d806` for the note (the build of 10 October 2026, as the note says).
