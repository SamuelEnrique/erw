# Session 4258 report: Arizona held (chain 240, window 4)

13 November 2026, about 14:27 to 14:40 UTC. Branch `wip/4250-forecast`. Model spend USD 0.

- **Arizona** (azleg.gov; robots request 85 at 14:26:57, statute request 86 at 14:29:16, after the robots file's 120-second crawl delay): through 31 December 2040 the full cash value of renewable energy and storage equipment is 20 percent of its depreciated cost (Revised Statutes 42-14155). Held as the same rule kind as Florida's, on the reader's own rate: 80 percent of the base off through 2040, all of it after. Not modeled, and said in the tip and the method note: the cap on depreciation at 90 percent of cost, the department's useful lives, and the deduction of federal tax credits from the taxable cost (the tool's base is the capital cost before any credit).
- **Tested**: a node test of 2027 to 2041 (the last year at 20 percent, the first at the whole); the Python and Stata files follow the rule kind already written for Florida.
- **Built and read** under the build lock: Arizona solar at a 1 percent rate gives a taxable value of 20 percent of the cost and USD 477,816 the first operating year; without a rate, not held. check-values 785 of 785. After merging `origin/main`, the 180 related test files 2,221 passed, 0 failed.
- **Landing row 4** moved to `e6fa97ad8` on main; main merged back into `wip/4250-forecast` and pushed.

## Decisions made without you

- Arizona's assessment ratio and local rates are not in 42-14155, so no default rate is shown: the reader types one, as for Florida.

## For Samuel's ruling

- None new.
