# What a utility sells to commercial customers: Florida Power & Light Co in FL

Draft `scan-deep-51da98ad4331` of the findings hunt over the whole warehouse (chain 502), 2026-11-19. State: draft, not reviewed. Review at `/internal/findings`.

**The finding.** The retail electricity sales to commercial customers of Florida Power & Light Co in FL was 54.17 TWh in 2025, against 47.49 TWh in 2017, the first full year the ERW holds.

![What a utility sells to commercial customers, Florida Power & Light Co in FL](util-commercial-u861-6452-fl.png)

**The figure by full year** (TWh): 2017: 47.49, 2018: 47.87, 2019: 48.56, 2020: 46.65, 2021: 47.37, 2022: 52.44, 2023: 52.85, 2024: 53.59, 2025: 54.17.

**The tables and rows.** `eia861m_utility_sales_monthly`; the rows for Florida Power & Light Co in FL, region key `u861_6452_fl` (the card's `hunt.region`), years 2017 to 2025. The yearly values: `util-commercial-u861-6452-fl.csv`.

**Its strength.** The change is 6.43 typical yearly moves (a typical move is 1.04 TWh, 1.4826 times the median absolute change between full years). Holds in more than one year: 6 of the 8 full years after 2017 lie above 2017's value. Survives a change of window: from 2018 to 2025 the change is 6.30, from 2017 to 2024 it is 6.09. Sample large enough: 2017 holds 12 and 2025 holds 12 observations; the floor is 12. Half the change remains without the first year: from 2018 to 2025 the change is 6.30, 94.3 percent of the change from 2017. At least one typical yearly move: the change is 6.43 typical yearly moves (1.04 TWh a year, the median move between full years); the floor is 1.

**Its limits.** EIA Form 861M as the utility filed it, in one state, its sales to the customers it serves; states with retail or community choice are not read; a utility that merged or changed its EIA number starts again under its new number; the latest year's months may be preliminary.

**Reproduce.** `python util-commercial-u861-6452-fl.reproduce.py <the table's CSV>` and `do util-commercial-u861-6452-fl.reproduce.do` (Stata) recompute the figures by year from the tables as the public downloads hold them; each names the expected values at its top.
