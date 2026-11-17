# Ruling impact: /attention, the Attention and Friction indices (17 November 2026)

Session 7597 (samueloldlaptop). The one line marked "Changes a figure" under /attention in `docs/reviews/rulings-for-samuel-2026-11-17.md` (branch `wip/7560-six-reads`). No page and no default was changed.

- **Script:** `runs/ruling_impact/attention_impact.py`, its printout `attention_impact.out`. It reads the page's own file, `site/data/attention.json` (built 16 November 2026 09:24 UTC: 461 cells of a sector, a place and a week, each with its stories, opposition stories and Friction Index).
- **No model call** (spend USD 0); the classification behind the file is a model's, already done, and nothing was classified again.

| # | Line (the question) | Page and cells | Default | Other choice | Change |
|---|---|---|---|---|---|
| 1 | A cell with fewer than ten stories prints its counts and no Friction Index (Virginia's datacenters read 75.00 from 3 of 4 stories) | `/attention`, the headline Friction Index and every cell of the chart and table, by sector, place and week | Every index printed, its counts beside it | Counts only under ten stories | 363 of the 461 indices (78.7 percent) would go, every one of them a state's cell (no "all places" or "United States" cell has fewer than ten stories). Of the 363, 293 read 0 (no opposition story among a few), 26 read 100 and 18 read 50: the extremes a handful of stories gives. In the newest week (2 November 2026) 42 of the 60 indices go. The 16 "together" rows (each sector over every classified week) all hold ten stories or more and stay. The read's example, Virginia's 75.00 from 3 of 4 stories, is one of the cells that would print its counts alone |
