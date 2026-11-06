# Session 1458 report: fault 7, a why line that names nothing the headline lacks

Energy Research Warehouse (ERW), session 1458, chain 150 (`queue/done/150-day-6-november-code-periodicals-continued.md`, its first fault session: chain 149 left no unfinished step beyond its landing, which session 1457 finished), samueloldlaptop, 6 November 2026, about 04:30 to 05:10 UTC. Model: Claude Opus 5.5 (this window's). Model spend USD 0. No warehouse data written; nothing sent or posted; no web request. Branch `wip/1458-periodicals`, cut from `origin/main` at `c4f6e3489` (every branch of chain 149 an ancestor of main).

## The fault

Fault 7 of `docs/reviews/periodicals-faults-2026-11-05.md`, still there in session 1451's second runs:

- Faulted, under "US executives quit $25bn gas venture over claims of secret Russian control": "LNG or gas project faces executive departures and alleged Russian involvement claims; geopolitical risk to US energy sector." It shares 0.29 of its content words with the headline (the restatement line is 0.5) and holds no hollow verb, so it printed.
- Written instead: nothing; the item carries the headline alone (rulings item 16), until the scorer's prompt of session 1437 writes the story a line with a fact the title lacks.

## What it did, with commits

- `55d1a3990`: `brief.new_things(text, head)` lists what a line names that the headline does not: a number (an amount, or a year), a quantity in words ("Half of India's coal plants"), a month or a weekday, or a name (a capitalised word past the first, or a first word that is an acronym or has a capital inside, and not a generic word such as US, AI, LNG; a demonym is its country's: "Qatari" under "Qatar"). `why_check` adds "names nothing the headline lacks" when the list is empty and the line shares a quarter of its content words with the headline (`NOTHING_NEW_SHARE`) or strings two clauses on a semicolon. Named last: a line with another fault is named by that one. The method (`docs/methods/periodicals.md`) says the rule.
- Tests: `Session1458NothingNew` in `tests/test_periodicals.py` (the faulted line; four lines that name a new figure, party, quantity or month and pass; the demonym; the semicolon filler; a consequence line with little of the headline that stays; the 13 stored issues regenerated into the test's own temporary folder, 463 items, 324 lines printed before and 224 with the rule, each printed line passing the check). Five of the twenty saved lines of `tests/fixtures/periodicals/why_lines.json` re-pinned to the headline alone (three by the rule on the scorer's line, two whose adjectives were cut and whose line then named nothing new); four made-up lines of `test_session801.py` and `test_session807.py` given a place, so each tests what it tested (a year, an article, a fallback).
- The faults file: row 7's state, and a section for chain 150.

## Checks

| Check | Exit | Result |
|---|---|---|
| `pytest tests/test_periodicals.py test_session801 test_session807 test_session2206 test_session2207 test_session430` | 0 | 164 passed, 1 skipped |

## Found

- The rule as the faults file words it ("a line that names nothing the headline lacks fails") refuses 560 of the 784 lines of significance 7 and above in `news_stories` that passed the check; most of the scorer's old lines are a consequence in general words ("Grid emergency and price spike show real reliability stress from demand growth."). The rule landed with the share and the semicolon refuses 167 of 784; the sample of those refused is filler ("Large capital commitment to AI data center infrastructure buildout.", "Asset sale reshapes Gulf of Mexico oil ownership."), the sample of those kept carries a consequence ("Further attacks on crude and product tankers raise supply risk and shipping costs in a chokepoint.").
- "signaling" is not caught by the hollow verbs' pattern (`signals?`): "OPEC raises 2027 demand forecast, signaling stronger market outlook" passed it. Now refused by this rule; the pattern is left as session 1437 wrote it (a later fault session may add the -ing forms).

## Decisions made without you

- The rule's reach: the line names nothing new AND (a quarter of its words are the headline's OR it holds a semicolon), not every line naming nothing new; `NOTHING_NEW_SHARE = 0` gives the stricter form.
- Generic names (US, AI, LNG, EV, GW, MW, CEO, IPO, ISO, RTO, PPA, BESS, HVDC and a few more) name no one new; a first word with no inner capital is not a name.

## For Samuel's ruling

- The stricter form of fault 7's rule (560 of 784 lines refused, most items printing the headline alone until the new prompt's lines arrive) against the one landed (167 of 784).
