# Session 973 report: the method note v5 and the gaps

23 October 2026, from 00:11 UTC, on samueloldlaptop, unattended, in the worktree `C:\Users\lossa\Documents\erw-973` on `wip/973-allgrids` (cut from `wip/972-allgrids`). Chain `queue/done/065-late-22-october-code-allgrids-5.md`, session 973. Model spend USD 0. No warehouse data written; no request to a publisher.

## Read these first

- **`docs/methods/siting.md` is version 5**, with "What version 5 changed":
  - 793's hub table download;
  - 794's two nodes as A and B;
  - 795's nodes that settle alike;
  - 799's replication;
  - 970's card labels;
  - the reads that changed nothing (797, 798, 971, 972);
  - nothing ruled, nothing landed.
- **Three decisions added**: 26 (the pair's figures), 27 ("alike" is exact equality, no reason inferred) and 28 (the card's labels). "The screen" names the pair and the two downloads; "The replication" names 799's run.
- **The gaps file's state, dated anew** ("State on 23 October 2026, after midnight"): **no row changed state.**
  - Coverage on main lists none of the awaited tables.
  - New since 792: the data machine's queue holds chain 046 (sessions 850 to 864, written at 00:07 UTC). Its 850 and 851 are to land ERCOT's settlement point mapping and ERCOT's reserve margins, two of the tab's open rows. Nothing of it has landed yet.
- **Two times corrected**: 971's and 972's reports gave their start as about 00:35 and 00:42 UTC; they began at about 00:05 and 00:09.

## What to review

1. `docs/methods/siting.md`, "What version 5 changed" and decisions 26 to 28.
2. `docs/reviews/siting-gaps.md`, the last section.

## Checks

| Check | Exit | Result |
|---|---|---|
| precheck | 0 | |
| every test that reads the method note or the gaps file (85) | 0 | OK (1 skipped) |

## The landing

With 970 to 977, in session 977.

## Decisions made without you

1. **Decision 28 dated 23 October**, the day 970 ran (UTC); the others of this chain are dated 22 October, as their sessions ran.
2. **The data machine's chain 046 named in the gaps file** as what may fill two rows, without counting it as landed.

## For Samuel's ruling

- Nothing new.

## Files

- Changed: `docs/methods/siting.md`, `docs/reviews/siting-gaps.md`, `docs/reviews/siting-reads-2026-10-22.md` (972's time), `archive/sessions/SESSION_971_REPORT.md` and `SESSION_972_REPORT.md` (their times), `tests/test_session712.py` (a comment).
- New: this report.
