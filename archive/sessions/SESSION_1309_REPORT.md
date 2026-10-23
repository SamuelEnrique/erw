# Session 1309 report: the site's checks on the stored answers

23 October 2026, 23:55 to 23:57 UTC, on samueloldlaptop, unattended. Chain `queue/done/095-day-28-october-code-ask-board-6.md`. Model spend USD 0.

- **Done**: `tests/test_session1309.py` runs every answer `warehouse/chat/eval/replay.py` replays (157), with its sources built as the replay builds them, and a copy of each answer that holds a decimal figure with that figure moved by 7.13 (127 copies), through the number check and the unit check of both loops: `warehouse/chat/ask.py` (`unverified`, `unit_mismatches`) and `site/lib/chat/ask.ts` (`unverified`, `unitMismatches`, by `site/scripts/run-checks-1309.mjs`). 284 cases: the two loops' lists are the same in every one. The stored answers pass both; all 127 moved copies are caught by both.
- **Differences found**: none, so nothing fixed.
- On `wip/1307-ask`.

## Decisions made without you

1. The citations are not compared here: they are the loop's bookkeeping (the tables read), held alike by session 1300's turn-by-turn test.

## For Samuel's ruling

None.
