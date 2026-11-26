# Session 10205 report: the Grid tool audited as a hostile expert would

Chain 710, part D's first item, 26 November 2026, the old laptop, worktree `erw-c710-a`. Model spend USD 0; no live service asked; no table written.

## What was done

- `docs/reviews/grid-model-audit-2026-11-26.md`: the Grid tool (`/grid`) read as a grid operator's analyst and a carbon accountant would, in the form of the battery audit of 20 November. Evidence (scripts, outputs, the drawn pages): `docs/reviews/grid-model-audit-2026-11-26/`.
- The arithmetic is right: the Lower 48's default view and the Gravity tab's seven-grid table restated to the digit, by an independent script and again by the page's own library; the carbon formula to four decimals on every unrevised hour of six grids.
- Six findings: 2 Major, 2 Moderate, 2 Minor. Four fixes change words only (branches 1, 2, 4, 5, for landing); two move figures (branches 3 and 6, tests only, not for landing).
- Each words branch drawn to HTML with the site's own components (no build, reads answered from the main copy's tables, every other request refused) and read once more.

## Branches

| Branch | Kind | Test |
|---|---|---|
| `wip/audit-grid-1` | words: the Lower 48 is not the sum of its grids; its exchange is with Canada and Mexico | `tests/test_audit_grid_1.py` |
| `wip/audit-grid-2` | words: a grid's net export reads each tie from the code first in the alphabet | `tests/test_audit_grid_2.py` |
| `wip/audit-grid-3` | figure: two netting rules in one tool (test only) | `tests/test_audit_grid_3.py` |
| `wip/audit-grid-4` | words: the carbon figure is an average, one factor per fuel, imports at EIA's estimate (page and note) | `tests/test_audit_grid_4.py` |
| `wip/audit-grid-5` | words: the carbon hour is days older than demand's; the ranked table is each ISO's latest hour | `tests/test_audit_grid_5.py` |
| `wip/audit-grid-6` | figure: no plausibility screen on the snapshot's interchange (test only) | `tests/test_audit_grid_6.py` |

- Branches 1, 2, 4 and 5 merge together onto origin/main without a conflict (trial merge).

## Decisions made without you

- The default view was restated on the tables this machine holds (built 5 to 13 November) and the committed snapshot (built 25 November), not the live set: the brief allows no live request.
- Three carbon matters (average against marginal, one factor per fuel, imports' valuation) were made one finding (4), since they are the same sentence on the page; one branch, no overlap with the others.
- Branch 2's Now view words went on the sentence, not the card, so it does not touch the line finding 1 changes.
- Means of tie gaps were checked against the day-by-day reports: two SPP reports of about 2.2 million MW (4 and 6 October) inflate any mean over the MISO-SPP tie; the netting figures quoted are with reports above 20,000 MW set aside, and medians.
- No before and after snapshot of the live pages: this push to main is documents only and the brief forbids live requests. `scripts/freeze.py status`: no freeze.
- A junction `site/node_modules` in this worktree points at the main copy's, to draw components; git-ignored, nothing in the main copy written.

## For Samuel's ruling

- Finding 2: read each grid's ties from its own report first? Moves PJM's net export 990 MW in the median hour and turns its sign in 32 percent of hours. Default: left as it is.
- Finding 3: one netting rule for the grid tabs and the region trade tab? Moves MISO's net 451 MW, PJM's 503, CAISO's 258 in the median hour. Default: left as it is.
- Finding 6: screen the snapshot's interchange reports as `ba_supply.py` does? No figure moved in the seven weeks measured. Default: left as it is.

## Needs the key

- Nothing. (No measurement here needed a model or a live read; the live Storage snapshot and the newest hours of the live set were not read, by the brief's rule.)

## Problems

- `tests/test_session1898.py` (check-holds) and `tests/test_session137.py` (libuv assertion on Windows) fail on clean origin/main on this machine once `site/node_modules` is present; they skip without it. Not touched.
- `git fetch` prints "failed to delete .git/worktrees/erw-1425, erw-1600: Permission denied" on every call: stale worktree records of the main copy, harmless here.
