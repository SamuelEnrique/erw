# What a utility sells to industry: Portland General Electric Co in OR

Draft `scan-deep-2712f475c08e` of the findings hunt over the whole warehouse (chain 502), 2026-11-19. State: draft, not reviewed. Review at `/internal/findings`.

**The finding.** The retail electricity sales to industrial customers of Portland General Electric Co in OR was 5.98 TWh in 2025, against 3.00 TWh in 2017, the first full year the ERW holds.

![What a utility sells to industry, Portland General Electric Co in OR](util-industrial-u861-15248-or.png)

**The figure by full year** (TWh): 2017: 3.00, 2018: 3.04, 2019: 3.25, 2020: 3.51, 2021: 3.80, 2022: 4.29, 2023: 4.66, 2024: 5.10, 2025: 5.98.

**The tables and rows.** `eia861m_utility_sales_monthly`; the rows for Portland General Electric Co in OR, region key `u861_15248_or` (the card's `hunt.region`), years 2017 to 2025. The yearly values: `util-industrial-u861-15248-or.csv`.

**Its strength.** The change is 6.08 typical yearly moves (a typical move is 0.49 TWh, 1.4826 times the median absolute change between full years). Holds in more than one year: 8 of the 8 full years after 2017 lie above 2017's value. Survives a change of window: from 2018 to 2025 the change is 2.93, from 2017 to 2024 it is 2.10. Sample large enough: 2017 holds 12 and 2025 holds 12 observations; the floor is 12. Half the change remains without the first year: from 2018 to 2025 the change is 2.93, 98.6 percent of the change from 2017. At least one typical yearly move: the change is 6.08 typical yearly moves (0.49 TWh a year, the median move between full years); the floor is 1.

**Its limits.** EIA Form 861M as the utility filed it, in one state, its sales to the customers it serves; states with retail or community choice are not read; a utility that merged or changed its EIA number starts again under its new number; the latest year's months may be preliminary.

**Reproduce.** `python util-industrial-u861-15248-or.reproduce.py <the table's CSV>` and `do util-industrial-u861-15248-or.reproduce.do` (Stata) recompute the figures by year from the tables as the public downloads hold them; each names the expected values at its top.
