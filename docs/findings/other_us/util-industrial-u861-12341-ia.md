# What a utility sells to industry: MidAmerican Energy Co in IA

Draft `scan-deep-99bfc0c7e209` of the findings hunt over the whole warehouse (chain 502), 2026-11-19. State: draft, not reviewed. Review at `/internal/findings`.

**The finding.** The retail electricity sales to industrial customers of MidAmerican Energy Co in IA was 19.38 TWh in 2025, against 12.18 TWh in 2017, the first full year the ERW holds.

![What a utility sells to industry, MidAmerican Energy Co in IA](util-industrial-u861-12341-ia.png)

**The figure by full year** (TWh): 2017: 12.18, 2018: 12.83, 2019: 13.38, 2020: 13.87, 2021: 15.11, 2022: 15.73, 2023: 16.51, 2024: 16.99, 2025: 19.38.

**The tables and rows.** `eia861m_utility_sales_monthly`; the rows for MidAmerican Energy Co in IA, region key `u861_12341_ia` (the card's `hunt.region`), years 2017 to 2025. The yearly values: `util-industrial-u861-12341-ia.csv`.

**Its strength.** The change is 7.61 typical yearly moves (a typical move is 0.95 TWh, 1.4826 times the median absolute change between full years). Holds in more than one year: 8 of the 8 full years after 2017 lie above 2017's value. Survives a change of window: from 2018 to 2025 the change is 6.54, from 2017 to 2024 it is 4.81. Sample large enough: 2017 holds 12 and 2025 holds 12 observations; the floor is 12. Half the change remains without the first year: from 2018 to 2025 the change is 6.54, 90.9 percent of the change from 2017. At least one typical yearly move: the change is 7.61 typical yearly moves (0.95 TWh a year, the median move between full years); the floor is 1.

**Its limits.** EIA Form 861M as the utility filed it, in one state, its sales to the customers it serves; states with retail or community choice are not read; a utility that merged or changed its EIA number starts again under its new number; the latest year's months may be preliminary.

**Reproduce.** `python util-industrial-u861-12341-ia.reproduce.py <the table's CSV>` and `do util-industrial-u861-12341-ia.reproduce.do` (Stata) recompute the figures by year from the tables as the public downloads hold them; each names the expected values at its top.
