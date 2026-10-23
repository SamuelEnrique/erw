# Session 1144 report: the unit check, measured on the stored transcripts

23 October 2026, 21:37 to 21:40 UTC, on samueloldlaptop, unattended, on `wip/1144-ask` (cut from `wip/1143-ask`). Chain `queue/done/085-day-25-october-code-ask-board-3.md`. Model spend USD 0.

- **Measured first**: on the 119 stored answers that carry their tool records (sessions 267, 302, 1113, 1114), a check of percent, MW and MWh beside session 1110's money units judged 19 figures in percent, 17 in MW and 28 in MWh. It would have sent back four right answers, all MWh (b10 and g04 of session 1113's run wrote "200.34 MWh" before "per MW": a unit written apart), and none for percent or MW.
- **Extended to percent and MW** (`PHYS_AFTER`, `KNOWN_UNITS` in `warehouse/chat/ask.py` and `site/lib/chat/ask.ts`): a figure followed by percent, pct, % or MW (not MW-month, not MWh) must match a returned figure in that unit; it is judged only against tool numbers in a unit the check knows (session 161's replay showed an MW figure from a page's own file, whose unit the tools write their own way: without this it was sent back).
- **Held by tests**: every right stored answer passes the check; a figure in the other of the two units is sent back; session 1110's six answers give what they gave; the site's check returns the same as the Python one on six strings. `docs/methods/ask.md` says so.
- Checks: `tests.test_session1144` exit 0; the Ask tests (249): exit 0.
- Decisions made without you: 1. **MWh left unjudged** until a compound unit written apart can be read. Reversible. For Samuel's ruling: none new.
