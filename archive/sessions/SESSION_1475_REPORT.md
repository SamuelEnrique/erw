# Session 1475 report: fault 53, the Roundup's subject

Energy Research Warehouse (ERW), session 1475, chain 154, samueloldlaptop, 6 November 2026, 07:19 to 07:22 UTC. Model: Claude Opus 5.5 (this window's). Model spend USD 0. No warehouse data written; nothing sent or posted; no web request. Branch `wip/1475-periodicals`, cut from `wip/1474-periodicals`.

## The fault

Row 53 of `docs/reviews/periodicals-faults-2026-11-05.md` (session 1468's dry run of W45):

- Faulted: "ERW Weekly | AEP and Google advance a $4 Billion, 702 MW Bloom Energy fuel-cell...; Brent down 13.1% on the week"
- Written instead: "ERW Weekly | Brent down 13.1% on the week; AEP and Google advance a USD 4 billion, 702 MW Bloom Energy fuel-cell..."

## What it did, with commits

- The commit before this report: `roundup.subject_line` puts the week's move first when the opening number is that move, and writes the headline's sums in the issue's money style (`brief.money_style`) before the cut at a word. Without a move the subject is the headline alone, as before.
- Tests: the subject tests of `test_periodicals.py` re-pinned (the move first) and one added (the money style). Session 1474's report's clock time corrected.
- The faults file: row 53 fixed.

## Checks

| Check | Exit | Result |
|---|---|---|
| pytest over the 36 modules that name the Roundup | 0 | 711 passed, 9 skipped |

## Decisions made without you

- The Digest's subject (the opening number alone, "ERW Daily | Henry Hub natural gas: ...") already leads with the opening; it is not changed.

## For Samuel's ruling

- None.
