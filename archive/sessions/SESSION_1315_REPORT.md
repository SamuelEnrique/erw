# Session 1315 report: one list of the evaluation's runs

24 October 2026, 00:01 to 00:03 UTC, on samueloldlaptop, unattended. Chain `queue/done/096-day-29-october-code-ask-board-7.md`. Model spend USD 0.

- **Done**: `warehouse/chat/eval/runs.json`, the one list of Ask's stored runs (eight: each its file, its grades and the field that says right, its label, its day's call limit, whether it carries a tool record, its row in the history), with the folder's other JSON files under `left_out`, each with why (the keys of the askings, the board's questions' keys, the list itself). `history.py`, `replay.py` and `refusals.py` read it; their three documents (`docs/reviews/ask-history.md`, `ask-replay.md`, `ask-refusals.md`) come out unchanged (each `--check` passes).
- **Tests**: `tests/test_session1315.py`, 3: every JSON file of the folder named once (a run, a run's grades, or left out); the scripts read the list (replay's runs, refusals' limit of 8); the documents unchanged. The scripts' earlier tests (sessions 1147, 1190, 1301, 1304) pass.
- A new run now needs one entry in `runs.json`, and the folder's test fails until it has one.
- On `wip/1314-ask`.

## Decisions made without you

1. `replay.py` keeps its name `RUNS` (now built from the list), so the tests that read it are unchanged.

## For Samuel's ruling

None.
