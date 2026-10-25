# Session 2564 report: four held tables described (the news pair, a note of its own; the two large-load rules tables, linked to the note that describes them)

25 October 2026, about 00:40 to 00:48 UTC, on lab-desktop (the data machine), chain 126, unattended. Precheck passed (`runs/c126/pre2564.out`). Model spend USD 0. Pulls: none.

## Read these first

- **19 tables of coverage have no note on main or on this branch** (counted by code: no note of their name, none on a note's `Tables:` line). Four are this chain's own (sessions 2560 to 2563; their notes are session 2569's). **The unlanded chains (118 to 120, `wip/2448-2461-data` to `wip/2476-2489-data`) hold notes for eight:** `cost_of_power_monthly`, the policy monitor's `policy_actions`, `policy_reads`, `policy_reads_evidence` and `large_load_rule_reads`, and `ercot_all_hub_prices_history`, `iso_hub_prices_history`, `iso_rtm_hub_prices`. Left alone, as session 2550 left them.
- **Four described:**
  - **`news_index` and `news_stories`**, a note of their own (`docs/methods/news_index.md`), written from `warehouse/news/ingest.py`, `score.py` and `index.py` and checked against the tables by code: 23,108 stories from 80 outlets, 17,440 scored, 10,906 from the backfill; 17,447 index rows, each an id of the stories table, 16,815 with a headline, 15,859 clusters.
  - **`large_load_rules` and `large_load_rules_internal`**, whose headers name `docs/methods/datacenter_cost.md` as their method and whose section "Rules in motion" describes them: added to that note's `Tables:` line, with one dated line. Its counts were checked against the tables and stand (87 document sentences and 29 records, 4 untied docket numbers, 12 single-customer rows, 4 California drafts); the tables now hold 117 rows, the 116 of 8 October and one Texas order of 15 October 2026 added by the daily refresh, which the dated line names.
  - Their Method cells set in `docs/coverage.md` (`runs/c126/s2564/cells.py`).
- **Two findings, recorded in the note and not changed:** two stories of Data Center Knowledge's feed are dated 17 November and 1 December 2026, the feed's own publish times; and 7 rows of `news_index` carry scores that `news_stories` no longer holds (`scored_at` empty there).
- **Left (three):** `ai_power_regions`, `ba_supply_monthly` and `large_load_statements` (whose method is in `docs/accelerator/large_load_eighty.md`, not in a method note), each needing a note of its own.
- **Tests:** the 1,760 tests that read the notes, the cells or `docs/methods` pass but for test 705, the worktree artifact (`runs/c126/s2564/tests.out`).

## Decisions made without you

- **Tables the unlanded chains describe are not linked again here.**
- **Four, not six:** the three left need notes written from large builders, better a session each.

## For Samuel's ruling

- None.

## Files

- New: `docs/methods/news_index.md`, this report.
- Changed: `docs/methods/datacenter_cost.md` (its `Tables:` line and one dated line), `docs/coverage.md` (four Method cells).
- On the data machine only: `runs/c126/s2564/`.
