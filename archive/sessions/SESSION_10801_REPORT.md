# Session 10801 report (chain 740, lab-desktop window 3): part B, the announced datacenters

- **What a reader of the page sees:** nothing changed yet (no page reads the new files).
- **Built:** `warehouse/forecast/datacenter_announced_rows.json` (22 rows: one named project and one public document each, every figure with the phrase that states it and the sentence around it), `warehouse/forecast/datacenter_announced.py` (checks each phrase is inside its quote and parses to the value; with `--verify-reads`, each quote is inside the kept text of its request; then the defaults), `site/data/forecast/datacenter_announced.json`, `warehouse/forecast/datacenter_wages.py` and `site/data/forecast/datacenter_wages.json` (CBP 2023 payroll per job: 518210 for operations, 2362 and 238 for construction, 51 states).
- **The defaults (medians, with their ranges):** investment per MW USD 8.33 million in 2025 dollars (6 rows, 3.0 to 46.8); permanent jobs per MW 0.208 (5 rows, 0.05 to 0.333); permanent jobs per USD billion 56.25 (16 rows, 9.3 to 121.8); construction jobs as announced per USD billion 325 (6 rows, 63 to 1,218).
- **Requests read:** 114 to 130 of `runs/c740/probe/probe.csv` (robots files first; www.michigan.gov, ir.digitalbridge.com and georgia.org refuse at their robots file; gov.texas.gov disallows ClaudeBot by name).
- **Rows:** part B done; requests 6 (`datacenter_announced`) and 7 (CBP construction wages) for window A, requested.
- **Commits:** part B (one commit, pushed to main).
- **Needs the key:** nothing.
- **Decisions made without you:**
  - The default of each ratio is the median of the rows that state both figures, never the mean; its count, lowest and highest travel with it.
  - Construction jobs are kept as announced (a headcount at peak, or a count with no period), never turned into job-years; rows of both kinds enter one ratio, each row saying which.
  - Two documents of the same campus (Meta in Richland Parish, 2024 and 2026) are both rows and both enter the ranges.
  - The DOE Paducah figure includes 2 GW of gas generation and 2.6 GW of batteries: it enters no investment ratio. Starwood's 1,500 jobs are of no stated kind: they enter no jobs ratio. xAI's "nearly 2 gigawatts" is the company's computing, not the site's MW: not held.
  - A 2026 announcement's dollars are taken as 2025 dollars (the deflator holds no 2026 index), as the cross-check takes an unstated dollar year.
  - Where a release names a city and not its county, the row holds the place and no county (no county taken from memory).
  - The parameter files and their builders were pushed to main with part B: no page reads them yet. Code that a page reads goes to a `wip/c740-*` branch and a landing request from here on.
- **For Samuel's ruling:** nothing new.
