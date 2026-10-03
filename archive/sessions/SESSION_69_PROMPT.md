# Session 69 prompt: the storage build-out tracker

Energy Research Warehouse (ERW), session 69. Read CLAUDE.md, docs/datastandard.md, and the code behind `/storage` and `/cost-of-power/seller` first.

**Expected model spend: USD 0.00. Hard cap: USD 0.00.** No paid service, no pull, no force push. Expected wall time about 2 hours 30 minutes; no time cap.

## Where this runs (read carefully)

Sessions 67 and 68 are running right now in `C:\Users\samen\Documents\erw` and will merge to main and write to Supabase tonight. This session must not touch any of that.

1. Work only in this worktree, `C:\Users\samen\Documents\erw-build`, on the branch `wip/069-storage-buildout`. Push only to that branch. Never push to main or to any `task/` branch (a push there merges to main and deploys).
2. **No Supabase writes, no Redivis upload, no data lock, no pull.**
3. In `C:\Users\samen\Documents\erw` you may do exactly two things: call its Python interpreter by path (`.venv\Scripts\python.exe`), and, once at the start, copy the input tables you need out of its `warehouse\output` into this folder's `runs\session69\inputs\` (read-only copies; record each file's size and time). Never write there, never run git there. If a table you need is being rewritten at that moment (its size changes between two reads a few seconds apart), wait and copy again.
4. Do not edit `/storage` or any shared component: session 67 is changing them. Build your own small pieces for this page; the finish step swaps them for the shared ones.
5. Do not run the finish step (last section).
6. Never fill, never invent. A value that is not held is shown as not held, with the reason.

## Why this session

A credit investor asked whether battery deployment, and battery duration in particular, is keeping up with renewable build-out. A battery company's CFO is being shown the storage tools tomorrow. The site shows what batteries do hour by hour (`/storage`) and, after tonight, what one earns. It does not show how much storage has been built, where, of what duration, and how that compares with solar. This page does.

## Part A: the table (`storage_buildout_monthly`, built in scratch)

From the EIA-860M tables already held (operating and planned generators), for each of the seven ISO regions and the US total, by month:
- operating battery storage: power in MW and, where EIA-860M reports it, energy in MWh;
- the same split by duration bucket (energy divided by power): under 2 hours, 2 to under 4, 4 to under 6, 6 hours and more, and "energy not reported";
- operating solar in MW (utility-scale), for comparison;
- planned battery storage, by expected year online, MW and MWh.

First check what the held tables carry. If energy capacity (MWh) is not a column in the held tables but is in the raw EIA-860M files already saved under the main folder's `warehouse\raw`, parse it from those saved files (that is not a pull). If it is in neither, build the table on MW only, show duration as not held, and say what a person would need to approve to get it.

State how generators are assigned to an ISO region (the balancing authority code in EIA-860M) and count the ones that could not be assigned. Derived, public. Write it to `runs\session69\storage_buildout_monthly\` and pass the validator there. Tests: MW by bucket sums to the total; a generator with no energy value lands in "energy not reported" and nowhere else; the US total equals the sum of regions plus unassigned.

## Part B: the page (`/storage/buildout`, "How much storage has been built")

Same layout as the battery revenue page being built tonight: a fog beige panel on the left with the choices, the answer on the right; on a phone the panel stacks on top. Plain and usable. No gradients, no emoji, no decorative cards.

**Left panel:** Grid (the United States, then the seven ISOs); Measure (power in MW, or energy in MWh).

**Right side, top to bottom:**
1. **One summary sentence** from the numbers, about 25 words. Example shape (computed, not these words): "ERCOT has X MW of batteries holding Y MWh, an average of Z hours, up from W MW a year ago."
2. **Three headline numbers:** operating power (MW); operating energy (MWh) with the average duration in hours; added over the last twelve months.
3. **Chart 1: operating storage by year, stacked by duration bucket.** This is the chart that answers "is duration growing".
4. **Chart 2: storage against solar:** hours of storage (MWh) per MW of operating solar, by year. One line. Say in one sentence under it what the ratio means.
5. **One table by grid:** MW, MWh, average duration, added in the last twelve months, planned by year online. PJM is included: these are EIA's public generator data, not PJM's prices.
6. **Folded sections:** how generators are assigned to a grid, and how many were not; what EIA-860M covers and misses (utility-scale units of 1 MW and above; no behind-the-meter batteries; planned dates are developers' own estimates and slip); the newest month held.
7. **A grey source line.**

**Look:** Georgia in cardinal 8C1515 for the title and section headings; body text in Stanford black 2E2D29; fog beige F7F3EA for the panel and highlighted rows; a cardinal header row on the table; thin grey rules. Duration buckets use one hue from light to dark so longer duration reads as darker.

**Verifying without Supabase:** the page's real data path reads Supabase like every other page, and that table will not exist until the finish step. Verify the page locally against the scratch table through a fixture that the tests use, and make sure the production code path contains no fixture. Do not add the page to the navigation config in a way that conflicts with tonight's release gate; list in the finish step what must be added (a menu entry, a `review` status in the release gate's list, check-routes and check-values entries, `llms.txt`).

## The finish step (do NOT run it; document it)

At the top of the report, under "To finish", the exact commands for a later session or for Samuel: bring the branch up to date with main (sessions 67 and 68 will have landed); swap this page's own pieces for the shared components; take the data lock; sync; build the table into `warehouse/output`; validator and coverage; Redivis draft by table name; Supabase live set and load; add the menu entry and the release gate status (`review`); check-routes and check-values; push to a `task/` branch to merge; release the lock.

## Report: `archive/sessions/SESSION_69_REPORT.md`

"To finish" first, then "In plain words". Then: whether EIA-860M's energy capacity was held, parsed from saved files, or not available; the United States and each region: MW, MWh, average duration, twelve-month additions, planned; the duration buckets by year for the US, ERCOT and CAISO; storage hours per MW of solar by year; generators not assigned; tests; a description of the page as built; errors and decisions; "For Samuel" with only what needs a person. Flag anything implausible instead of smoothing it. No em dashes anywhere. Commit after every working step, push the wip branch, reply "REPORT READY" and stop.
