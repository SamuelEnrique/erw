# Session 1437 report: the why lines

Energy Research Warehouse (ERW), session 1437 (chain 149's "1434"), `queue/done/149-day-5-november-code-periodicals-excellent.md`, samueloldlaptop, 6 November 2026, about 01:41 to 01:58 UTC. Model Fable 5.1, high effort. Model spend USD 0. No warehouse data written; nothing sent or posted; no web request. Branch `wip/1437-periodicals` over `wip/1436-periodicals`.

## What it did, with commits

- **`41f12b20f`**: the why line says a fact or nothing (faults 7 to 11, 32, 33 of `docs/reviews/periodicals-faults-2026-11-05.md`):
  - `brief.why_check` fails a line with a hollow verb (`HOLLOW_VERBS`: signals, demonstrates, reflects, underscores, highlights) and a line that restates the headline (`brief.restates`: the share of the line's content words the headline holds, `RESTATES_SHARE` 0.5; `content_words` lowers, styles money, drops STOP words and a plural's s). Measured first over the 160 top-ten items of the 13 issues and the dry run: lines at 0.5 and above restate ("Cost and regulatory hurdles threaten AI sector's plans to use nuclear power" under "AI's nuclear power push runs into cost and regulatory hurdles"), lines under it add a fact (0.46: "Awards fell short of the 800-MW target, showing PJM capacity strain").
  - `brief.norm_headline` compares headlines through `why_fallback` (money in the one style, the publisher's suffix off), so "Oil dips but holds above USD 100" is "Oil dips but holds above $100" (fault 10) and "..., Reuters reports" is the headline. A failing line now always prints nothing, the headline alone: rulings item 16's default as the owner's rule reads it ("nothing is invented and nothing is said twice"); session 807's test had pinned the clause printed when a suffix differed.
  - The scorer's prompt (`score.SYSTEM`) and `warehouse/news/rubric.md`: no hollow verb; one fact the story gives that the title does not (a counterparty, a place, a date, a quantity with its unit, what a rule changes).
  - Tests: `tests/test_periodicals.py` `Session1437WhyLines` (five tests on the dry run's lines); `tests/test_session801.py` and `tests/test_session807.py` re-pinned to the rule; the fixture `tests/fixtures/periodicals/why_lines.json` recomputed (three of the twenty said "signals" and now print nothing; a note in the file).
- The faults file: rows 7, 8, 9, 10, 11, 32, 33 marked fixed.

## Measured, before and after (`runs/s1437/counts.md`; the top-ten items of the 13 issues and the dry run of 26 October, 160 items)

| | adjectives of the list | hollow verbs | restatements | items with no why line |
|---|---|---|---|---|
| before (the lines as printed, or as the dry run printed them) | 46 | 25 | 8 | (not counted) |
| after (`why_line` over the same lines with their headlines) | 0 | 0 | 0 | 42 |

The dry run of 26 October: 5 of its 10 top items said "signals" and 1 restated; after, 7 of 10 print the headline alone. The gain is in truth, the loss in lines: the scored `why` fields of the stories held are the old prompt's, so the second dry run (session 1451, the same stories) shows the check's effect only; the prompt's effect shows from the first scheduled scoring after this lands (Friday's run, read by session 1454).

## Checks

| Check | Exit | Result |
|---|---|---|
| `scripts/precheck.py --what "session 1437"` | 0 | |
| `tests.test_periodicals`, `test_session801`, `807`, `802`, `803`, `470`, `577`, `2206`, `804`, `805`, `806` | 0 | 224 passed before the new tests; 62 in `test_periodicals` after |
| em dashes in the files changed | | none of this session's (`score.py` line 121 holds one on main: the `nodash` helper's own replacement character) |

## Decisions made without you

- The fallback never prints (above): item 16's default read as the rule's letter. Before, the headline's clause was printed again whenever a money style or a publisher's suffix made it differ from the headline (faults 10 and 33, and session 807's pinned case).
- The restatement line is 0.5 of the line's content words, from the measurement over 160 items; a line at 0.46 passes.
- "signals" as a noun ("price signals") fails too; none of the 160 lines uses it so.
- The scorer's prompt changed in the one sentence of `one_line_why`; no story is re-scored (the owner approves backfills).

## For Samuel's ruling

- Whether 42 of 160 top items printing the headline alone (until the scorer's new prompt has written the lines) is the right trade, or whether a weaker fallback (the title's own clause) should return for the archive's issues.
