# Session 8209 report (chain 502, lab-desktop second window)

19 November 2026, 12:13 to 12:17 UTC (read from the clock). Opus 5.5. Model spend: USD 0. Parts B and C checked at the start: both still waiting.

## Part D, second pass: other_us, 17 drafts (EIA-861M)

- `eia861m_utility_sales_monthly` (1,051,488 rows, the largest table of the power sector no draft had read): each utility's retail sales by sector in each state, years with all twelve months, utilities that sold at least 2 TWh to commercial customers in 2017; the largest movers in TWh kept (`deep/utilities861.py`).
- States with retail or community choice are not read (CA, NY, TX, IL, OH, PA, MD, NJ, MA, CT, RI, NH, ME, DE, DC, MI): there a utility's sales count only the customers it still fully serves, so customers moving to another supplier read as a fall. The first dry run showed it: Pacific Gas and Electric's commercial sales "fell" from 22.97 to 7.36 TWh.
- The three strongest:
  - Omaha Public Power District's sales to commercial customers: 7.88 TWh in 2025 against 3.67 TWh in 2017.
  - Virginia Electric and Power's (Dominion Energy Virginia) sales to commercial customers: 60.09 TWh in 2025 against 41.54 TWh in 2017.
  - MidAmerican Energy's sales to industrial customers in Iowa: 19.38 TWh in 2025 against 12.18 TWh in 2017.
- 17 of 17 reproduce from their own scripts; 17 of 17 do-files hold.

## A fault of this chain's own reports, corrected

- The headers of the reports of sessions 8207 and 8208 gave times that were not read from the clock (8207 "to 12:20", 8208 "12:20 to 12:40"). Corrected from the commands' own timestamps: 8207 12:02 to 12:09, 8208 12:08 to 12:14.

## Code

- `warehouse/analysis/findings/deep/utilities861.py` on `wip/8202-findings` (`28b5704b1`).

## Needs the key

- Nothing.
