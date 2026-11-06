# Session 3306 report (chain 200, session 10 of the plan, moved up): /capital, capital flows' first view

lab-desktop, 6 November 2026, 20:17 to 20:21 UTC. Branch `wip/3300-companies`. Moved up while the build lock was held by two landing gates of other windows (from 19:40 and 20:05 UTC).

## What was done

- **`warehouse/derived/capital_page.py`** writes `site/data/capital.json`: for the capital rows of `energy_deals` (project finance, M&A, debt, equity raise), by quarter and type the rows, the USD stated and the rows without USD; by segment; by the kind of the buyer (from the company database); the disclosed share; the twenty largest with their stories. Nothing filled in.
- **The hold:** `energy_deals` is held whole, so the committed file holds `held: true` and the table's 529 rows' count only; `/capital` shows the deals page's held block with that count, and a hover on what the view draws once a permission is recorded. The full view is written and type-checked with the build; its computation is tested on fixtures.
- **A private trial** (the scratchpad, never published) of the unheld computation: 289 capital rows, 204 (70.6%) stating USD; kept only to see the view is not empty when it opens.
- **`/capital`** in the Infrastructure menu (six of eight); tests 203 and 239 updated; `tests/test_session3306_capital.py` (6 tests); method note sections "The pages" and "Capital".

## Decisions made without you

- `/capital` goes under Infrastructure beside Deals and Companies (its rows are the deal tracker's).
- While held, not even counts by type or quarter are shown: only the table's row count, as `/deals` shows.

## For Samuel's ruling

- `/capital` is empty of figures until `energy_deals` has a permission or a row license (see session 3304).

## Cost

- No model call. USD 0.00.
