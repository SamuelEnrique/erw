# Ruling alternatives: /attention, the Attention and Friction indices (17 November 2026)

Session 7624 (portable-laptop, code role). The one line of `docs/reviews/ruling-impact-attention-2026-11-17.md` (it removes figures), built on its own branch from origin/main with a test that pins it. **No branch asks to land; no default on main changed.** Model spend USD 0; nothing was classified again.

- **Build:** the worktree `erw-alt` (3,491 MB free before the build), served on port 3320 with the repository's `.env` and no model key, read with the internal cookie at 1280 px.
- **Tests:** the new test, and every test file that names the changed file. `tests/test_session1880.py` (`test_the_node_tests_pass`: the week file's build Monday and its partial week) fails on origin/main as well: not this work's.

| # | Line | Branch | Figure before (origin/main) | Figure after (the other choice) | Files touched | Test | Screenshot |
|---|---|---|---|---|---|---|---|
| 1 | A cell with fewer than ten stories prints its counts and no Friction Index | `wip/alt-attention-1` (`2212f2e8a`) | Data centers, Virginia, week of 12 October 2026: Friction Index 75.00 percent (3 of 4 stories); every one of the 461 cells' indices printed | "3 of 4 stories report opposition: fewer than 10, so no index": **363 of the 461 indices go (78.7 percent)**, every one a state's cell (293 of them read 0, 26 read 100, 18 read 50); the line chart draws no point for such a week and its hover gives the counts; on the Friction Index map such a state is not colored and its hover says why; the states' table writes "fewer than 10 stories". The Attention Index, the story counts and the opposition counts do not move | `site/app/attention/AttentionView.tsx`, `tests/test_session7624_alt_attention_small_cells.py` | On `site/data/attention.json` (built 16 November 2026): 461 cells, 363 under ten stories, all states', 293, 26 and 18 at 0, 100 and 50; the view's code applies the rule in the five places | `docs/reviews/ruling-alternatives/attention-1-small-cells-1280.png` |

## Seen while reading the build, not this branch's

- With Virginia and the week of 2 November 2026 chosen, the page says "No story of data centers named Virginia in the week of 2024-12-30": the week named is not the week chosen. The line comes from `noCellLine` in `site/lib/attention.ts`, which this branch does not touch, so origin/main draws it too (not read on a build of main here). A site fault for the tool's faults file.

## Decisions made without you

- **Ten stories is a constant (`MIN_STORIES`) on the branch**, the number the ruling's line names.
- **The map leaves a small state uncolored on the Friction Index** rather than color it by a count; on the Attention Index every state is drawn as before.
