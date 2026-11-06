# Session 1462 report: the scorer's new prompt read on 26 October's top ten; the hollow verbs' -ing forms (fault 42)

Energy Research Warehouse (ERW), session 1462, chain 150, samueloldlaptop, 6 November 2026, 04:46 to 05:10 UTC. Model: Claude Opus 5.5 (this window's). **Model spend USD 0.0119** (two calls of `claude-haiku-4-5` through `warehouse/llm.py`'s client, the ledger off as session 1451 ran it, `ERW_SPEND_CAP_USD=1`: USD 0.0031 for a first try that matched 2 of 10 stories, USD 0.0088 for the ten). No warehouse data written (`news_stories` read, not changed); nothing sent or posted. Branch `wip/1462-periodicals`, cut from `wip/1461-periodicals`.

## The fault

The second runs' note of session 1451 (not a numbered row): three of the five What moved items of 26 October print the headline alone with "One outlet has reported it so far.", because the stories' lines are the old prompt's and the new prompt (session 1437) writes only from the first scoring after the landing. This session asked the scorer's new prompt for those ten stories again (`runs/s1462/rescore.py`: `score.request_parts` and `score.SCHEMA` as `score.py` sends them; nothing written but `runs/s1462/`) and read its lines with the check.

- The new prompt's lines print for 4 of the 10 stories with the check of session 1461; two of the four lean on "signaling", the -ing form the check did not read (fault 42, new).
- Faulted: "Woodfibre LNG accelerates timeline while AECO spot curve softens, signaling weaker 2027 North American gas pricing."
- Written instead: "Woodfibre LNG accelerates timeline while AECO spot curve softens."

## What it did, with commits

- `5c388684d` (`brief.py`, `score.py`, `rubric.md`, tests): `HOLLOW` fails the -ing and past forms (signaling, signalling, signaled, demonstrating, reflecting, underscoring, highlighting, and the past forms); `HOLLOW_TAIL` cuts a trailing clause led by a comma and one of them in `why_line`, before the check, so the fact before it prints; the scorer's prompt and the rubric name the forms.
- Tests: `Session1462HollowForms`; `tests/test_session804.py`'s fixture story line given a party ("Houthi attacks on Red Sea tankers drive crude prices higher.", for "Geopolitical supply risk drives crude prices higher.", which session 1458's rule refuses: it names nothing the Brent headline lacks), so the test keeps testing that a reason prints only when a story names the price; the saved items' pinned problems (one now names "hollow verb: signaling"); the 13 issues' count of lines printed before the rule, 323 (324 before the tail cut).
- **Found by this session's whole suite: session 1458 had left `tests/test_session804.py` failing** (its fixture line above); 1458 to 1461 ran the periodicals' modules, not the suite. Fixed here.
- The faults file: row 42.

## Checks

| Check | Exit | Result |
|---|---|---|
| `pytest` over the 69 modules that import `brief` or `score` | 0 after the fixes | (first run: 2 failures, test_session804 and the saved items' problems) |
| `python -m unittest discover -s tests` (the whole suite, this tree) | 0 | Ran 7,689 tests in 631 s; OK (skipped=327), with the fixes |

## Found

- **With every rule, the new prompt's lines print for 3 of the 10 stories (the old lines: 3 of 10).** The seven others fail as: a line naming nothing the headline lacks (4), a figure the headline gives that cannot be taken out (2), a hollow verb, "signals" (1). The scorer runs `claude-haiku-4-5` at low effort (`score.NEWS_SCORE_MODEL`, session 206's choice for cost); its line, not the check, leaves What moved with headlines alone.
- `why_line` takes a headline's figure out of a line ("in a USD 25 billion venture" to "in a venture"); the result reads, but thinly.

## Decisions made without you

- The -ing clause is cut rather than the line refused when it trails a comma: the fact before it is the scorer's and the clause is the inference.

## For Samuel's ruling

- **The scorer's model for the why line.** At `claude-haiku-4-5`, low effort, 3 of 10 top stories of 26 October get a line that passes the check. Whether the one-line why should be written by a Sonnet-class model for the top stories only (a second call after the ranking, about twenty stories a day), or the check's rules eased, or the headline alone accepted for most items. Not changed: the scorer's model and cost are the daily run's.
