# Session 1308 report: the stored answers' replay in the gate

23 October 2026, 23:55 to 23:58 UTC, on samueloldlaptop, unattended. Chain `queue/done/095-day-28-october-code-ask-board-6.md`. Model spend USD 0.

- **Done**: `scripts/land_check.py` has a step `ask_replay` after the suite and before `npm ci`: `python warehouse/chat/eval/replay.py --check` in the gate's clean copy. A failure (an answer graded right that the commit's checks would now send back, or `docs/reviews/ask-replay.md` not what the runs give) fails the gate and skips the build. A commit without `replay.py` passes the step and says so. The suite runs the same check through session 1301's test; the step gives it its own line in the gate's record and its own log.
- **Tests**: `tests/test_session1308.py`, 4, with session 579's scripted operations: the step's place, its command and its folder, a failure stopping the gate before `npm ci`, a commit without the script. Session 579's 27 pass as before.
- On `wip/1307-ask`.

## Decisions made without you

1. The step beside the suite's own run of the same check, not in place of it: the suite's failure says which test, the step's says the replay.

## For Samuel's ruling

None.
