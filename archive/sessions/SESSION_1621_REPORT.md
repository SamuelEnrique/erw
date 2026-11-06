# Session 1621 report: the second read, part two

6 November 2026, on samueloldlaptop's second window, chain 165. Branch `wip/1621-board`, cut from `wip/1620-board` with `origin/main` merged. Model spend USD 0.

## What it did

- The keys other readers take from the board, checked (audit rows 37 and 38):
  - the Digest's day move (`brief.day_move`, through `board_page.stats`) is the same move and percent after this chain's changes, in four cases (a rise, a fall from a positive base, a rise from a negative base, no move a week apart), and its fallback formula agrees;
  - every key Ask's board panel reads is still written under its name; this chain renamed none.
- The new keys (`ytd`, `avg365`, `ext`, `basis`) offered in the method note for the Roundup and Ask, not wired (their code is other chains').
- `tests/test_board_1621.py` (3 tests). Ask's own panel test (`site/scripts/test-ask-panel.mjs`) run: exit 0.

## Proof

- `tests.test_board_1621`: 3 passed (`brief` imports here, so the Digest's comparison ran).

## Decisions made without you

- **Offer, not wire**: the chain's rule leaves Ask's code and the periodicals to their chains; the note names each new key and the Roundup's use of `ext.w.peak`.

## For Samuel's ruling

- None new.
