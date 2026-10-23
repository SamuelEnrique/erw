# Session 1146 report: the CLI holds what the site holds

23 October 2026, 21:48 to 21:56 UTC, on samueloldlaptop, unattended, on `wip/1146-ask` (cut from `wip/1145-ask`). Chain `queue/done/085-day-25-october-code-ask-board-3.md`. Model spend USD 0.

- **The Python loop's general chat** (`warehouse/chat/ask.py`, what the CLI and `eval.py` run) now does as the site's: it holds the conversation (the last three turns, in Ask ERCOT's words, the first message unchanged with none; an earlier answer's numbers as given and its tables as read: `clean_turns`, `Asker.opening`, `extra_sources`, `known_tables`), records what each query read (`reads_of`, as `readsOf`), and names on a refusal up to three tables it looked at with what each holds (`tools.nearest_for`, `holds_line`, as the site's). Ask ERCOT's profile overrides these and is unchanged.
- **Not mirrored, on purpose**: the license hold and MISO's refusal stay the site's (`lib/supabase.ts`, `lib/chat/tools.ts`); the CLI reads this machine's own files under the reader's own license and says so (`ERWLicenseWarning`). Python's `compare` never read a missing `result` (it reads with `.get`), so session 1126's crash has no Python twin.
- **Held by a test** that runs the same conversation and the same query through both languages and compares the first message and the read line, and a scripted loop (no model) whose refusal records its reads and its nearest table.
- Checks: `tests.test_session1146` exit 0 (4 tests); the Ask tests (291): exit 0.
- Decisions made without you: 1. **The hold not mirrored in the CLI** (internal, the owner's own files). Reversible. For Samuel's ruling: none new.
