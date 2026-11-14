# Session 5272: the fourth arm; a reply cut off at the output limit is no longer an error

Energy Research Warehouse (ERW). portable-laptop, window P3, 14 November 2026 (09:50 to 10:03 UTC), Fable, unattended. Chain 256. Branch `wip/5200-ask-close` (worktree `erw-p3-5264`). Nothing built, nothing landed, no warehouse data written. Model spend USD 1.5905.

## Read these first

- **Session 5270 blamed rule 11 for the cut-off. That was wrong, and is corrected.** The same question, at `medium` with the rule taken out, was cut off again. The cut-off comes with the rule and without it, at `high` and at `medium`.
- **What it is:** the model's thinking counts toward the 16,000 output tokens of a call. Three askings today spent the whole of one call thinking, each with its figure already in a tool result, and wrote nothing. Both loops threw: an error for the reader, USD 0.27 to 0.31 spent.
- **Both loops now handle it.** The cut-off reply is dropped; the model is told once to write from what it has, in a call that may ask no tool; cut off again, the question ends in plain words with no figure. Never an error.
- **The four arms are in:** the rule alone and `medium` alone each cut the cost of nine heavy figure answers by about four tenths; together by half. Every answer right in every arm.
- **The live proof is still owed.** po05 was asked twice more on the mended loop and answered both times.

## What was done

- Precheck from the main checkout: exit 0.
- **The fourth arm:** the twelve heavy figure questions at `medium` under a prompt of ten rules. The site's spec was changed for the asking alone and put back (`git status` clean; `check_spec.py` exit 0). Its run is kept under a name of its own, `eval_s5272_site_platform_ten_rules_run.json`, listed in `runs.json` under `left_out`: it is not one of the set's runs and no answer of it stands as a question's newest.
- **`warehouse/chat/eval/grade_arm.py`:** grades such an arm as `eval_site.py` grades a run (the same keys and rules, a held table's results struck out first) and gives its calls after the figure by class.
- **The cut-off, read:** po05 again, 17,010 output tokens, one thinking block, no text; it had its figure at the third call and had checked it three ways.
- **The model's documentation, read first** (the `claude-api` skill's guide for this model): thinking counts toward `max_tokens`; a truncated turn in a loop of tool calls is run again, not treated as an answer.
- **The mend, in both loops** (`warehouse/chat/ask.py`, `site/lib/chat/ask.ts`; the words in the exported spec as `cut_off`, `cut_off_answer`, `cut_off_why`):
  - the cut-off reply is not kept in the conversation;
  - once, the model is sent the cut-off's words and the next call may only write;
  - an answer written then is checked like any other (a wrong figure is still sent back);
  - a second cut-off ends the question with status `refused_unverified` and words that state no figure;
  - any other stop the loop does not know still raises.
- **An answer that had a cut-off says so** (`cut_off` in the answer and in the stored record).
- **po05 asked twice more** on the mended loop at `medium` with rule 11: answered in 7 calls and in 3, the figure of 13 November.

## The four arms, nine questions asked all four ways

| | Calls | After the figure | Cost |
|---|---:|---:|---|
| `high`, ten rules (13 November) | 105 | 78 | USD 1.769 |
| `high`, rule 11 | 60 | 34 | USD 1.126 |
| `medium`, ten rules | 54 | 34 | USD 1.039 |
| `medium`, rule 11 | 48 | 28 | USD 0.870 |

## Checks run

- `tests/test_session5272_ask.py`: 10 passed. `tests/test_session1300.py`, both loops turn by turn on 17 scenarios, the two new ones among them: passed.
- Every Node script of the chat on the main checkout's packages (21): each exit 0. The runner's own tests: 11 of 11.
- Type check of `ask.ts`, `tools.ts`, `window.ts`, `panel.ts`: no error in the four (two in `site/lib/supabase.ts`, not this stack's, as before).
- `check_spec.py` exit 0; `tests/test_session1315.py` (every file of the folder is a run or is left out): passed.
- The wide run is in session 5273's report.

## Model spend

| Run | Estimate before | Actual (the ledger) |
|---|---|---|
| The arm of ten rules | at most USD 1.95 | ten askings, USD 1.3316 (stopped at po05's cut-off) |
| po05 twice on the mended loop | at most USD 0.66 | USD 0.2590 |
| The session | under USD 2.00 | **USD 1.5905** |

- The ledger for the day: USD 5.8557 in 301 calls. Chain 256: USD 5.8557 of USD 20.

## Decisions made without you

- **The cut-off is mended in the loop, not by a larger limit.** A larger limit lets a call think longer and cost more (USD 0.64 at 64,000 tokens). Told to write, the chat writes.
- **A second cut-off ends in the status the page already draws** (`refused_unverified`), with its own words, not a new status: the reader's panel is another window's.
- **The arm's spec change was not committed.** The committed prompt has eleven rules throughout.
- **Session 5270's sentence is corrected where it stands**, with what was wrong said.

## For Samuel's ruling

- **The output limit of a call (16,000 tokens).** The model's documentation suggests more for long turns. **Default: unchanged**; the cut-off is handled, and the limit bounds what one call can cost.
- The choice of effort is put after the held-out askings (sessions 5273 to 5275).
