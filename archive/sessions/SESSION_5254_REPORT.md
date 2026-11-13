# Session 5254: the first half continued; a question two tables answer differently

Energy Research Warehouse (ERW). portable-laptop, window P3, 13 November 2026 (19:31 to 19:37 UTC), Fable, unattended. Chain 238. Branch `wip/5200-ask` (worktree `erw-p3-5200`), `origin/main` merged at 19:31 UTC. Nothing built, nothing landed, no warehouse data written. Model spend USD 1.82.

## Read these first

- **Asked so far: 63 of 134. Right: 61.** This session asked 17: 16 right. Twelve of the first half remain.
- **The wrong one, tx07, is the key's fault.** Asked how many MW of ERCOT's 2019 queue entrants are operating, the chat gave Berkeley Lab's figure, 9,451.88 MW, and said so. The key held 5,593.64 MW from `iso_queue_statistics`. Two tables, two figures, and the question named neither.
- **Under it is a fact about the data.** `iso_queue_statistics` says 8,443.64 MW entered ERCOT's queue in 2019. Berkeley Lab's table says 43,557.71 MW. ERCOT's own queue file, which the first is built from, lists no withdrawn project. For Samuel's ruling.

## What was done

- Precheck (main checkout) exit 0; `origin/main` merged (nothing of the chat changed); `platform_questions.py --check` exit 0.
- **Asked, at most USD 2.00 written before:** slice a from st03 to de03, 17 questions. USD 1.8169.
- All 17 answers read beside their keys. The 16 graded right are right.
- The review file: tx07's account; the spend row; the scores regenerated.

## What the answers showed

- Storage 5 of 5, projects 5 of 5, the two deals questions refused in the hold's words, MISO's queue refused as paused.
- tx01, tx03 and tx09 used all 12 calls and were right. `ba_supply_monthly` holds 21 variables and three measures of net imports; the chat read its way to the one the question named.
- tx07 listed tables under ERCOT's filter first (rule 3 asks for no filter first) and so never saw `iso_queue_statistics`.

## Checks run

- `tests/test_session5251_ask.py` and the four tests that pin the records: 50 passed.
- `history.py`, `replay.py`, `refusals.py`, `platform_scores.py`: `--check` of each exit 0.

## Model spend

- Estimate before: at most USD 2.00. Actual: 17 questions, USD 1.8169.
- Chain 238: USD 7.38 of USD 20.

## Decisions made without you

- **tx07 stays wrong in the count until it is asked again.** Session 5256 re-keys it to name its source (Berkeley Lab's table) and asks it again; this session's answer stays in this session's run as it was graded.

## For Samuel's ruling

- **`iso_queue_statistics` and Berkeley Lab's table disagree five to one on what entered ERCOT's queue in 2019** (8,443.64 MW in 46 positions against 43,557.71 MW in 245). The cause read from the tables: ERCOT's own file holds active and completed projects only (1,159 and 577 rows), so a withdrawn project is in no entry year's count, and ERCOT's rows have no `mw_withdrawn` at all. Default: nothing changed here (a derived table of the data machine's, in review); the chat question names its source. A reader of that table's "entered" would take it for the whole cohort.
