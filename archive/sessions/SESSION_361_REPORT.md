# Session 361 report: Research's statistics

20 October 2026, from 10:36 UTC, unattended, on lab-desktop (the data machine), the fifth session of the chain of 20 October, night. Model spend USD 0. Pulls: none.

## Read these first

- **The three statistics are in the engine, and no card's figure moved.** Every key the eleven library cards had is as it was (compared key by key with the commit before; the only lines git shows removed are the last key of each card gaining a comma). Each card gains one key, `statistics`, which the code machine's session 355 reads (its shape: `docs/methods/automated_analysis_findings.md`, "Session 361: the statistics a card carries").
- **Newey-West beside HC1** (`findings_common.ols_hc1`: `se_nw`, `t_nw`, `p_nw`, `nw_lag`; the lag `floor(4 (n / 100) ^ (2 / 9))`, the Bartlett kernel, HC1's `n / (n - k)`), equal to `impact_study`'s own Newey-West to 12 places. On the cards: ERCOT's battery-spike multiple, HC1 2.316 (p 0.00001), Newey-West 2.692 (p 0.0001); CAISO's, HC1 1.024 (p 0.34), Newey-West 0.653 (p 0.15); the daily curtailment card's charging coefficient, HC1 73.5, Newey-West 115.9. Every HC1 figure was recomputed from the card's own CSV and equals the card's before anything was written.
- **The claims of a round:** the library holds 26 tested claims (a test on two cards counted once), 15 under p 0.05; every card carries the count and its own claims' Benjamini-Hochberg q-values. The hunt (version 1.3.0) writes the same for its round: in a dry run today, 143 claims, 88 tested, 25 passing, 70 with a trend p-value. A caveat, never a gate.
- **A step, not a trend:** one step against a straight line by the Bayesian information criterion. On session 251's seven usable drafts it flags exactly the five that session's verification called a step or a hump (break years 2024, 2020, 2021, 2023, 2021) and neither of the two it called trends.
- **The daily recompute** (`dm_findings_recompute`, after the scan and `dm_publisher_figure` in `warehouse/run_data_machine.sh`): every finding computed again from the day's tables, the statistics added again, a record line a card in `warehouse/metadata/findings_recompute.csv`. It first runs at 17:00 UTC today; its record is the first line of that file. It was not run by hand tonight, since a recompute would move the cards' numbers in this commit, which the prompt forbade.

## What to review

1. `docs/methods/automated_analysis_findings.md`, the new section (the keys and the reproduction).
2. `warehouse/analysis/findings/findings_common.py` (`ols_hc1`, `nw_lag`, `bh_q`, `trend_p`, `step_or_trend`), `card_statistics.py`, `hunt.py` (the claim's `p_trend` and `shape`, the round's q-values, the draft's footnote).
3. `docs/reviews/packs/research.md`, items 2, 4 and 5 of section 6, rewritten.
4. `tests/test_session361.py` (10 tests).

## Checks

| What | Exit | Notes |
|---|---|---|
| `card_statistics.py --check`, then the write | 1, 0 | the check names the 11 cards it would change; the write: HC1 equal on 22 regressions, 11 cards written |
| every old key of the 11 cards against the commit before | 0 | all equal; one key added |
| the hunt as a dry run into `runs/s361/hunt` (no draft loaded, no state written) | 0 | 20 patterns, 143 claims, 25 pass, 12 drafts built in the scratch folder, the round's line in its `hunt.json` |
| `tests.test_session361` | 0 | 10 tests (the first run: 1 failure, a float compared exactly; now relative) |
| `bash -n warehouse/run_data_machine.sh` | 0 | |

## Decisions made without you

1. **A round of the library is the cards as they stand**, its claims every number ending in `_p` (a regression's coefficient test); a test on two cards (the grid card's ERCOT rows) counted once. The visual cards test nothing and say so.
2. **The hunt's q-values are over each claim's straight-line trend p-value**, since its five tests give no p-value; the tests and the drafting are as they were.
3. **Newey-West on the daily curtailment card too**, not only the monthly ones: its days are in order, with gaps between held days counted as neighbours (said in the note).
4. **The recompute commits only the cards git already holds** (`git add -u`): this working copy holds a card run by hand with other inputs (`queue_divorce__first_year-2010`, untracked, not this chain's), which would otherwise be committed by the daily run and fail test 267.
5. **A hump is reported as a step to its higher level**; the words give the two levels, so a page shows the years.

## For Samuel's ruling

- Whether a card should state the Newey-West error in its sentence where it moves the verdict's p across 0.05 (none does today), or keep HC1 as the card's figure and Newey-West beside it.
- Whether the step flag should keep a draft from the review list, or stay a flag (today: a flag).

## Files

- New: `warehouse/analysis/findings/card_statistics.py`, `tests/test_session361.py`, this report.
- Changed: `warehouse/analysis/findings/findings_common.py`, `hunt.py`, `warehouse/run_data_machine.sh`, the 11 cards in `site/data/findings/`, `docs/methods/automated_analysis_findings.md`, `docs/reviews/packs/research.md`.
