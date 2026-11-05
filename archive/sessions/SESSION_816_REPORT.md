# Session 816 report: the new why line, scored

22 October 2026, 12:05 to about 12:12 UTC (the landing is session 818's), unattended, on portable-laptop (the code machine), in the worktree `C:\Users\samen\Documents\erw-816` on `wip/816-periodicals` (cut from `wip/815-periodicals`). Chain `queue/done/061-day-22-october-code-periodicals-2.md`, session 816. Model Fable 5.1. Precheck 0. **Model spend USD 0.0520** (two scoring calls of `claude-haiku-4-5`, USD 0.0328 and USD 0.0192; cap USD 1; the first call scored the wrong 25, below). No warehouse data written: the scoring ran on a copy under `runs/`, with the ledger off (its table takes the data lock).

## Read these first

- **`docs/reviews/periodicals-whyline-2026-10-22.md`**: the 25 highest-scored stories of the 21 October window, each with the line the scheduled run scored (before session 801's prompt) and the line the scorer writes now, and `brief.why_check` on each. **Before: 13 of 25 lines fail the check** (11 on an adjective, 2 on two sentences or a figure). **After: 5 of 25** (one "massive", three "major", one "critical"); the other 20 say a consequence ("First new North Sea gas project approved since Iran war, adding supply to tight European market"; "Government releases strategic reserves to cool diesel prices ahead of midterms"). Under the chain's threshold of 10, the prompt is not changed; the brief's check mends the five (the adjective is cut).
- **The scorer's path was the real one** (`score.py --limit 25 --out-dir`, one batch, the reference list and the caps as in a scheduled run), on a copy of `news_stories.csv` holding the scored stories and the 25 unscored.

## Checks

| Check | Exit | Result |
|---|---|---|
| `scripts/precheck.py --what "session 816"` | 0 | on duty |
| `runs/periodicals/s816_rescore.py` (first run) | 0 | scored 25 other unscored stories the caps had left in the file (the copy held them too); the review read 1 of 25; USD 0.0328 |
| `runs/periodicals/s816_rescore.py` (the copy holding the scored stories and the 25 alone) | 0 | 25 of 25 scored; the review; USD 0.0192 |
| em and en dashes | 0 | none |

## The landing

LANDING_PENDING

## Decisions made without you

1. **The 25 are the window's highest-scored stories** (significance 6 or more), since those are the ones the Digest prints.
2. **The first run's 25 were the file's own unscored leftovers**, not the 25 chosen; the copy was cut to the scored stories and the 25, and the run made again. The first run's result is not in the review.
3. **The prompt stays**: 5 of 25 fail, under the threshold of 10 the chain set.

## For Samuel's ruling

- Nothing new.

## Files

- New: `docs/reviews/periodicals-whyline-2026-10-22.md`, this report. Not in git: `runs/periodicals/s816/`.
