# Session 7610 report (portable-laptop, 17 November 2026)

Energy Research Warehouse (ERW). Part 1 of the prompt of 17 November (under the rules of `queue/done/305-night-16-november-portable-done-line-and-browser-reads.md`): every row marked `fault` in `docs/state/browser_reads_wanted.md` that is a site fault, fixed with a test, seen in a browser at 1280 and 390 px, marked fixed with its commit, with a landing request row. About 08:05 to 08:25 UTC. Model spend: USD 0 (no script that calls a model; the site built and served with no model key in its environment).

## What was done

- **17 rows were marked `fault`:** 16 site faults and 1 data fault (row 55, the battery page's awards snapshot; its data request 261 already stood, so the row stays `fault`).
- **Each of the 16 was already fixed at its cause with a test** by sessions 7600 to 7602; checked, not redone (rule 4): the shared "i" box kept in the window (`3ea3ce82d`, `82ab05cd0`, landed; rows 1, 7, 9, 12, 20, 24, 28), a headline's box above its figure (`9fcc1bd41`, landed; row 10), the shoulder line (`094b3de62`, reworded by `e41a8b656`, landed; row 11), the demand growth hover cards (`d1bdd1385`, landed; row 27), and on `wip/7602-landed-reads` (landing row 38, requested): the tall box widened (`5f4741557`; rows 52, 62), the one-point axis (`7210933ec`; row 63), the event-day table's frame (`5c2e5b889`; rows 80, 82), the supply links line (`3b636ad76`; row 179).
- **Seen in a browser:** `wip/7610-fault-rows` (`wip/7602-landed-reads` merged with main `026b040b9`, no conflict) built in the foreground and read with `site/scripts/read-rows-c305.mjs` at 1280 and 390 px in the internal view. Every box inside the window at both widths; no page scrolls sideways; row 11's line reads "the batteries' output in those shoulders is not held"; row 27's cards draw "+33.34 percent"; row 63's share axis runs 0.55 to 0.75. 42 pictures and the reader's output in `docs/reviews/browser-reads-2026-11-16/s7610/` on that branch (`f00c708c8`, pushed).
- **Tests on the branch:** 9 pytest files, 69 passed; `node --import ./scripts/tsx-register.mjs scripts/test-large-load-read.mjs`, 54 of 54.
- **Rows marked `fixed`** with commit, test and what was seen (the earlier words kept after "Earlier:"); the file's list of states gains `fixed`. Landing request row 40 (`wip/7610-fault-rows`, which holds row 38).
- **Snapshots:** `c310-7610-a` before, `c310-7610-b` after: 0 differences in all (no live page; docs only).

## Not as the rules expected

- A `next start` server left running since 16 November by this chain's session 7602 (port 3761, worktree `erw-c305-b`) held memory; stopped before the build (2,191 MB free then).

## Decisions made without you

- The 16 site faults were already fixed with tests on branches: the session read them again in a browser and marked them, rather than writing new fixes (no redundant work).
- A new landing row (40) was written for the stack read here, though row 38 holds the same four site fixes: row 40 adds only the read's pictures and is current with main; either may land.

## Needs the key

- Nothing.

## For Samuel's ruling

- Row 62's ruling stands as it was: on a phone the long box of "Demand at the grid is not sales to customers" still scrolls inside itself (default: left so).
