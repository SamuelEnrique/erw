# Session 5075 report: chain 243, Automated Analysis's weekly run, end to end, as a dry run

Energy Research Warehouse (ERW). Chain 243, portable laptop window P1, 13 November 2026, about 19:32 to 19:55 UTC. Opus 5.5. Model spend USD 0 (no model called: every run here is `--no-model` or `--dry-run`, with the API key removed from the environment). Branch `wip/5072-analysis` (on `wip/5072-parity`).

- **What runs by itself** (the note's "Final form", session 5004) was already automatic: the Sunday workflow (pg_cron, the workflow's schedule the fallback), the daily chart, the scanner and the findings worker. What it lacked was a way to run the whole week without writing to the repository or calling a model: `--dry-run` (session 152) stops after the choice.
- **New: `warehouse/analysis/run.py --out-dir <folder>`.** The whole weekly run (every template and watch line, the rule's choice, the three charts, the caption, `chart_of_the_week.json`, `results.json`, the history, `templates.json`, `tables.json`) into a folder outside the repository; no model, no status row, nothing under `docs/` or `warehouse/` moves; the history starts as a copy of `docs/analysis/history.csv`, so changes are scored against the same earlier weeks as the Sunday run. A folder inside the repository, or the flag with `--dry-run`, `--gallery-only` or `--tables-only`, is refused.
- **The dry run, on the live set's public tables** (`ERW_BACKEND=live`, the anon key), for 2026-W46: exit 0; 17 measures ran, 24 skipped with their reasons (a table held for its license, or not in the live set); the rule chose Brent's weekly mean, 100.41 USD per barrel in the week of 2 to 8 November, down 20.76, "the largest week-to-week move of the last 105"; the chart, the two social images, the caption and the two JSON files were made in the scratch folder; the worktree's `git status` showed only this session's own edits. The chart was looked at: title, subtitle, axis, the marked week and the source line are drawn.
- **The same rule for 2026-W45** (`--dry-run`, choosing only) chose Brent too, where the Sunday run of 8 November chose the Lower 48's battery discharge (92.2, third today). The published `results.json` shows why: on 8 November Brent's newest week was 26 October to 1 November (121.17, up 0.15); its week of 2 to 8 November was not yet held. Same rule, data that arrived after the run.
- **The note** (`docs/methods/automated_analysis.md`, "Final form") says how to run the dry run and what it gave.
- **Tests:** `tests/test_session5075.py` (new, 6 tests: the folder refused inside the repository and with the other modes; every path under the folder and the history copied; a failed run writes its log there and nothing else, no status row; the note; and, with `ERW_LIVE_TESTS=1` and the anon key, the whole week on the live set: the five files, `results.json`'s pick equal to the chart's template, no model, every field the last published week carries, the caption and the history row). Run here: 5 passed and the live one passed with the key (228 s). The 10 test files that read `run.py` or the note: 266 tests, OK, 2 skipped.
- **Corrected:** the times in reports 5073 (19:10 to 19:24 UTC) and 5074 (19:24 to 19:32 UTC); both had been written ahead of the clock.

## Decisions made without you

- The whole-week test on the live set is skipped unless asked for (`ERW_LIVE_TESTS=1`): it reads Supabase for about four minutes, and the landing gate's suite should not depend on the network.

## For Samuel's ruling

- **Research's final form.** Default, as the note has it: final, everything on its clock with no person, a deeper finding published after your approval.
