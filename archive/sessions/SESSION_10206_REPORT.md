# Session 10206 report (chain 710, part D, the old laptop, 26 November 2026)

Worktree `C:\Users\lossa\Documents\erw-c710-b`, branch `wip/audit-board-doc`. Model spend USD 0; no request to any live service; no table written; no site build.

## What was done

- **Part D, second bullet: the five words branches of the datacenter audit drawn.** `/cost-of-power` drawn with the site's own page and drawer on origin/main and on each branch (four cases), compared line by line and number by number: `wip/audit-datacenter-1`, `-2`, `-3`, `-5`, `-6` all pass (the new words appear, read plainly, no em dash, nothing else on the drawn view changes; every number the same, branch 3 adds "1 MW"). No branch edited.
- **Part D, first bullet: the price board's computed columns audited** (`docs/reviews/board-model-audit-2026-11-26.md`, evidence in `docs/reviews/board-model-audit-2026-11-26/`). The arithmetic is right: an independent restatement from the notes gives every computed figure from the page's own files (23,547 row figures, 266,809 from the hours, 166,601 spread figures, the week table where its hours are held), and the daily power means to the fourth decimal at full precision (1,566 days, four by 0.0001).
- **Five findings:** 1 High (rows kept from an earlier build older than the file's own prices: ERCOT's day-ahead tile 16.18 on 20 Nov, stale, beside the week table's 46.31 on 25 Nov; 98 public rows), 2 Medium (held grids' week lines and spikes after the hold in the public `board.json`; the week table's CAISO on-peak is Monday to Friday against the group's Monday to Saturday, and its 7 on-peak days are 7 weekdays), 2 Low (the strip's grid cells unmarked though 5 days old; the battery spread's top-bottom convention unsaid).
- **Branches:** `wip/audit-board-1` (test, figure), `-2` (test, builder), `-3`, `-4`, `-5` (words, for landing; they merge together cleanly).

## Decisions made without you

- The words fixes of findings 3 and 4 edit `site/components/board/BoardView.tsx` (3 also `Workbench.tsx`), not `site/app/board/`, `site/lib/board.ts` or `warehouse/derived/board_page.py`, which window E is likelier to touch tonight; the landing desk should land them after window E's board group.
- Finding 2's fix (the builder's `build_week` skipping held grids) and finding 5's formula words in the builder are returned as data requests, not edited, because `board_page.py` is window E's likely file and runs on the data machine.
- The table files for drawing `/cost-of-power` were cut to one year (`prep_tables.py`) to keep the memory rule; base and branch drew on the same files, so the comparison is fair, though some answer figures differ from the live page's.
- `site/node_modules` of the worktree is a junction to the main copy's (read only), so the site's code could be drawn without an install.

## For Samuel's ruling

- **The page keeper's rule (finding 1). Default: left as it is.** The other choice: append a shorter build's newer points to the held row's history. Measured: ERCOT Hub average's day-ahead tile 16.18 (20 Nov, stale) to 46.31 (25 Nov); 98 public rows current.

## Needs the key

- Nothing.

## Problems

- `git push` prints "failed to delete .git/worktrees/erw-1425 and erw-1600: Permission denied" on every push (the main copy's stale worktree folders); the pushes succeed.
- A first version of finding 5's test counted the daylight saving days as 24 hours (Python's subtraction of two times in one zone); corrected before its commit.
