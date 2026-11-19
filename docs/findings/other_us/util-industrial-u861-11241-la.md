# What a utility sells to industry: Entergy Louisiana LLC in LA

Draft `scan-deep-9069dd42f5a2` of the findings hunt over the whole warehouse (chain 502), 2026-11-19. State: draft, not reviewed. Review at `/internal/findings`.

**The finding.** The retail electricity sales to industrial customers of Entergy Louisiana LLC in LA was 35.98 TWh in 2025, against 29.75 TWh in 2017, the first full year the ERW holds.

![What a utility sells to industry, Entergy Louisiana LLC in LA](util-industrial-u861-11241-la.png)

**The figure by full year** (TWh): 2017: 29.75, 2018: 29.25, 2019: 29.80, 2020: 28.88, 2021: 29.87, 2022: 31.74, 2023: 31.51, 2024: 34.52, 2025: 35.98.

**The tables and rows.** `eia861m_utility_sales_monthly`; the rows for Entergy Louisiana LLC in LA, region key `u861_11241_la` (the card's `hunt.region`), years 2017 to 2025. The yearly values: `util-industrial-u861-11241-la.csv`.

**Its strength.** The change is 4.40 typical yearly moves (a typical move is 1.42 TWh, 1.4826 times the median absolute change between full years). Holds in more than one year: 6 of the 8 full years after 2017 lie above 2017's value. Survives a change of window: from 2018 to 2025 the change is 6.73, from 2017 to 2024 it is 4.77. Sample large enough: 2017 holds 12 and 2025 holds 12 observations; the floor is 12. Half the change remains without the first year: from 2018 to 2025 the change is 6.73, 108.0 percent of the change from 2017. At least one typical yearly move: the change is 4.40 typical yearly moves (1.42 TWh a year, the median move between full years); the floor is 1.

**Its limits.** EIA Form 861M as the utility filed it, in one state, its sales to the customers it serves; states with retail or community choice are not read; a utility that merged or changed its EIA number starts again under its new number; the latest year's months may be preliminary.

**Reproduce.** `python util-industrial-u861-11241-la.reproduce.py <the table's CSV>` and `do util-industrial-u861-11241-la.reproduce.do` (Stata) recompute the figures by year from the tables as the public downloads hold them; each names the expected values at its top.
