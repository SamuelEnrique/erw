# What a utility sells to industry: Entergy Arkansas LLC in AR

Draft `scan-deep-cf8550f568c9` of the findings hunt over the whole warehouse (chain 502), 2026-11-19. State: draft, not reviewed. Review at `/internal/findings`.

**The finding.** The retail electricity sales to industrial customers of Entergy Arkansas LLC in AR was 12.06 TWh in 2025, against 7.53 TWh in 2017, the first full year the ERW holds.

![What a utility sells to industry, Entergy Arkansas LLC in AR](util-industrial-u861-814-ar.png)

**The figure by full year** (TWh): 2017: 7.53, 2018: 8.07, 2019: 7.76, 2020: 7.59, 2021: 8.51, 2022: 8.49, 2023: 9.07, 2024: 9.93, 2025: 12.06.

**The tables and rows.** `eia861m_utility_sales_monthly`; the rows for Entergy Arkansas LLC in AR, region key `u861_814_ar` (the card's `hunt.region`), years 2017 to 2025. The yearly values: `util-industrial-u861-814-ar.csv`.

**Its strength.** The change is 5.42 typical yearly moves (a typical move is 0.84 TWh, 1.4826 times the median absolute change between full years). Holds in more than one year: 8 of the 8 full years after 2017 lie above 2017's value. Survives a change of window: from 2018 to 2025 the change is 3.99, from 2017 to 2024 it is 2.40. Sample large enough: 2017 holds 12 and 2025 holds 12 observations; the floor is 12. Half the change remains without the first year: from 2018 to 2025 the change is 3.99, 88.0 percent of the change from 2017. At least one typical yearly move: the change is 5.42 typical yearly moves (0.84 TWh a year, the median move between full years); the floor is 1.

**Its limits.** EIA Form 861M as the utility filed it, in one state, its sales to the customers it serves; states with retail or community choice are not read; a utility that merged or changed its EIA number starts again under its new number; the latest year's months may be preliminary.

**Reproduce.** `python util-industrial-u861-814-ar.reproduce.py <the table's CSV>` and `do util-industrial-u861-814-ar.reproduce.do` (Stata) recompute the figures by year from the tables as the public downloads hold them; each names the expected values at its top.
