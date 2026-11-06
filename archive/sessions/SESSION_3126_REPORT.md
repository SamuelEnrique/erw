# Session 3126: chain 169's fifth session (its 3070): the figures left of class 3

Personal laptop, second window, 6 November 2026, 13:30 to 13:38 UTC (begun while session 3125's tests ran). Opus 5.5. Branch `wip/3126-policy` cut from `wip/3125-policy`.

## What it did

- `warehouse/policy/fields.py`: a third reading of the action's figure (where the title and the opening paragraph state none, a figure of the text's first 9,000 characters, only in a sentence stating the action's own total and after those words), and the money pattern fixed (below). Three tests (`test_the_figures_of_session_3126`).
- `site/data/policy/monitor.json` rebuilt; the audit's class 3 rows and a section "Session 3126"; r57 put in class 3 in the sample file.

## What it found

- Class 3: 16 held of 17 (r57's 0.55 MW total, missed by session 3055, found). r6 is left on purpose: a CPUC program's per-driver incentives are no total of the action.
- **A fault of my own since session 3056**: "$1.2 million," lost its scale (the guard against a cut number also fired after "million"), so 13 records of the archive's copy read a million times too small. Fixed and tested; 13 values corrected in the file; nothing of it had landed. The fixture's 30 were right before and after (none of their sums is followed by a comma).
- The second read's totals: 206 faults before, 30 left. Tests: `test_policy_fields.py` 15 passed; `check_policy.py` 288 of 288 ok.

## Decisions made without you

- **A "total" sentence only**: "total installed capacity", "total planned funding", "the ... project will receive up to"; anything else past the opening paragraph stays out, so no figure of context is taken.

## For Samuel's ruling

- None new.

## Cost

- Model: none (USD 0.00).
