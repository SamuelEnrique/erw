# Session 1317 report: the general chat's chart in the Python loop

24 October 2026, 00:04 to 00:10 UTC, on samueloldlaptop, unattended. Chain `queue/done/096-day-29-october-code-ask-board-7.md`. Model spend USD 0.

- **Done**: `warehouse/chat/general_series.py`, the site's `lib/chat/generalseries.ts` (session 1142) with `lib/chat/series.ts`'s `chartPoints`, `pointsAreRows` and `keySeconds`, in Python. The base loop's `finish` (`warehouse/chat/ask.py` `Asker`: the general chat and a grid's) gives an answered record the series it rests on: the last query result grouped by time of a cited table, at least three rows, its rows the tool's own, at least two points. Ask ERCOT's profile keeps its own (`ercot.py` overrides `finish`).
- **Held equal to the site's**: session 1300's turn-by-turn test has a seventh scenario, `a_series` (ERCOT's hub average peak premium by year, over the twelve rows of `ercot_peak_premium_annual` recorded from the live set in `tests/fixtures/session143/tool_reads.json`, read from there at run time by both runners); both loops now report each answer's series (its table, title, group, unit, rows and check) and the test compares them: the same in all seven, one series of twelve rows in `a_series`, none elsewhere.
- **Found and fixed**: session 1194 moved `sourceHref` into `components/ask/AnswerSources.tsx`, and `site/scripts/test-ask-tables.mjs` (run by `tests/test_session153.py`) still read it from `AskPanel.tsx`: it failed. Its literal now reads the component, and the panel's import of it. Session 1194 had not run that test; the landing gate would have stopped on it.
- **Tests**: 45 test files that touch the chat: 367 passed, 52 skipped, the one failure above fixed (its file: 17 passed). Every node test that reads the files this chain changed passes (eight).
- On `wip/1314-ask`.

## Decisions made without you

1. The series in the base loop's `finish`, so a grid's chat carries it as the site's grid chats do; Ask ERCOT's profile untouched.

## For Samuel's ruling

None.
