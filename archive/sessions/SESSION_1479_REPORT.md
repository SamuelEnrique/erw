# Session 1479 report: fault 56, the money in the model's headlines

Energy Research Warehouse (ERW), session 1479, chain 154, samueloldlaptop, 6 November 2026, 07:30 to 07:36 UTC (while session 1478's gate ran). Model: Claude Opus 5.5 (this window's). Model spend USD 0. No warehouse data written; nothing sent or posted; no web request. Branch `wip/1479-periodicals`, cut from `wip/1478-periodicals` (the landing branch).

## The fault

Row 56 of `docs/reviews/periodicals-faults-2026-11-05.md` (session 1477's dry run):

- Faulted: "AEP and Google advance a 4 billion USD fuel-cell project, 702 MW, for Cheyenne data centers" (and "a $4 Billion, 702 MW ..." in session 1468's run of the same stories).
- Written instead: "AEP and Google advance a USD 4 billion fuel-cell project, 702 MW, for Cheyenne data centers".

## What it did, with commits

- `a305ed25e`: `brief.headline_style`: a headline the model writes is passed through `money_style`, with a code after the number ("4 billion USD") read as before it. `_headline_call` returns every headline so; the literal-number check reads the same digits. The publisher's own titles (`own_titles`, the no-model path) are not rewritten. The Roundup takes its headlines from the same call.
- Tests: `Session1479HeadlineMoney` (the forms; the model call's return through a stub client; the no-model titles unchanged).
- The faults file: row 56 fixed.

## Checks

| Check | Exit | Result |
|---|---|---|
| `pytest tests/test_periodicals.py -k 1479` | 0 | 2 passed |
| the whole suite | | the next landing's gate (session 1481) |

## Decisions made without you

- None.

## For Samuel's ruling

- None.
