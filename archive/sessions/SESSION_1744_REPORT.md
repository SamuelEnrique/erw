# Session 1744 report: Research's replication named in its method note, and a block to sign in

Energy Research Warehouse (ERW), session 1744, chain 195, samueloldlaptop, 6 November 2026, 21:33 to 21:34 UTC. Model: Claude Opus 5.5 (the file names Fable 5.1). Model spend USD 0. No warehouse data written; nothing sent or posted. Branch `wip/1743-records`, worktree `erw-1743`.

## What it did, with commits

- **`docs/methods/automated_analysis_findings.md`**: a "Replication" section and an empty "Sign-off" block, before "Cross-checks", in the form session 1743 gave the Grid's note. The section covers:
  - the ten current cards the mirror rebuilds, by name;
  - the eleventh, `batteries_lunch`, superseded and rebuilt only by its own do-file;
  - the commands;
  - why the cards' `.py` downloads are not the replication;
  - the record.
- **The mirror today**: `erw_2026_research_replication.py . --json ../../data/findings`, exit 0, **363 figures, 0 different** (session 381 had 304 over nine cards).
- **The cards' `.py` downloads**: `gas_sets_price.py` from its folder still stops on `ModuleNotFoundError: No module named 'findings_common'`, as in session 381.
- **`tests/test_session1744.py`**, 5 tests, among them the cards named against the mirror's `CARDS`. With the tests that read the note: 213 passed, 1 skipped. `check-methods.mjs`: exit 0, 553 of 553.

## Decisions made without you

- The Sign-off block lists what signing accepts from the note's own sections and the rulings it cites; it adds no rule.

## For Samuel's ruling

- Unchanged from the Research pack: the cards' `.py` downloads (ship `findings_common.py` beside them, or say on the card that the do-file and the mirror are the replication), and a decisions block on `/research`.
