# The consumption page: its figures audited as a hostile expert would

Session 10214, chain 710 part D, 26 November 2026, the old laptop. Platform tool 23, "who uses the power, and where load is growing": `/demand` and its four views. Read as a utility load forecaster and an AI lab's siting team asking where load is growing.

Work in progress: the default view's arithmetic is re-done (below); the claims, the rules changed one at a time and the findings follow.

## The default view re-done, to the digit

- `extract.py` streams EIA-930's eight workbooks of 3 October 2026 (the main copy's raw folder, read only) to the hour's start, EIA's Demand and EIA's Adjusted demand.
- `restate.py` (standard library, none of the warehouse's or the site's code) rebuilds every value of `site/data/demand_growth.json` from those hours, one UTC year at a time in memory.
- `draw_demand.mjs` draws `/demand` with the page file's own default export and collects the 91 figures it marks (`main_default_figures.json`); `compare.py` sets each beside the restatement.
- Result so far: 87 of 91 marked figures equal from the hours; the four others are explained in `compare.out`.
