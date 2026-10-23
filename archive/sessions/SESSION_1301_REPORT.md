# Session 1301 report: the stored answers replayed through today's checks

23 October 2026, 23:44 to 23:47 UTC, on samueloldlaptop, unattended. Chain `queue/done/093-day-27-october-code-ask-board-5.md`. Model spend USD 0.

- **Done**: `warehouse/chat/eval/replay.py` runs every stored answer that the loop let through and that carries its tool record through the number check (with the name check inside it), the unit check and the citations of `warehouse/chat/ask.py` as they now stand, the sources being what the loop gave the check (the question, the day's line, every tool call's input and result). It writes `docs/reviews/ask-replay.md` and, with `--check`, fails when the file is not what the runs give or when an answer graded right would now be sent back.
- **The result**: 157 answers of six runs (sessions 267, 302, 1113, 1114 and 1149's two sets; session 320's first run has no tool record): none would now be sent back. So no check changed by chains 075 to 089 (the unit check's percent and MW, 1144; the hold, 1191) sends back an answer that passed when it was written.
- **Tests**: `tests/test_session1301.py`, 3: the file and the rule (`--check`); every run read, more than 150 answers; the replay is not blind (one stored answer with a figure moved by 7.13 is caught, one citing a table never read is caught, one citing nothing is caught).
- On `wip/1300-ask`. 095's session 1308 puts the replay in the landing gate.

## Decisions made without you

1. Only the answers the loop let through are replayed: a refused answer's draft is not stored, only the refusal's words.

## For Samuel's ruling

None.
