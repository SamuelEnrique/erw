# Session 1143 report: Ask ERCOT on the general chat's rules

23 October 2026, 21:36 to 21:37 UTC, on samueloldlaptop, unattended, on `wip/1143-ask` (cut from `wip/1142-ask`). Chain `queue/done/085-day-25-october-code-ask-board-3.md`. Model spend USD 0.

- **The limit Ask ERCOT states is the limit it has**: its prompt said "at most 8 tool calls" while the loop it shares allows 12 since session 1111; `warehouse/chat/ercot.py` rule 6 and its docstring now say 12, and `site/lib/chat/spec_ercot.json` is exported again (two lines change; the tests that hold the spec to its export pass).
- **The rest reaches it through the shared loop**, checked and held by a test: its fixed refusal is the general one (session 1110's words and session 1111's why), and the read lines under an answer (session 1115) come from the loop's `base()`. Its own nearest tables (session 121) stand.
- Checks: `tests.test_session1143` exit 0; Ask ERCOT's tests (sessions 92, 121, 137, 143, 148, 153, 156, 161, 168): exit 0, 194 tests.
- Decisions made without you: none new. For Samuel's ruling: none new.
