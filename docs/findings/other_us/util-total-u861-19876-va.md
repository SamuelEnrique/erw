# What a utility sells: Virginia Electric & Power Co in VA

Draft `scan-deep-2c8308a5a95a` of the findings hunt over the whole warehouse (chain 502), 2026-11-19. State: draft, not reviewed. Review at `/internal/findings`.

**The finding.** The retail electricity sales of Virginia Electric & Power Co in VA was 94.56 TWh in 2025, against 76.62 TWh in 2017, the first full year the ERW holds.

![What a utility sells, Virginia Electric & Power Co in VA](util-total-u861-19876-va.png)

**The figure by full year** (TWh): 2017: 76.62, 2018: 80.66, 2019: 80.66, 2020: 77.69, 2021: 79.78, 2022: 84.36, 2023: 84.56, 2024: 89.04, 2025: 94.56.

**The tables and rows.** `eia861m_utility_sales_monthly`; the rows for Virginia Electric & Power Co in VA, region key `u861_19876_va` (the card's `hunt.region`), years 2017 to 2025. The yearly values: `util-total-u861-19876-va.csv`.

**Its strength.** The change is 3.45 typical yearly moves (a typical move is 5.20 TWh, 1.4826 times the median absolute change between full years). Holds in more than one year: 8 of the 8 full years after 2017 lie above 2017's value. Survives a change of window: from 2018 to 2025 the change is 13.90, from 2017 to 2024 it is 12.42. Sample large enough: 2017 holds 12 and 2025 holds 12 observations; the floor is 12. Half the change remains without the first year: from 2018 to 2025 the change is 13.90, 77.5 percent of the change from 2017. At least one typical yearly move: the change is 3.45 typical yearly moves (5.20 TWh a year, the median move between full years); the floor is 1.

**Its limits.** EIA Form 861M as the utility filed it, in one state, its sales to the customers it serves; states with retail or community choice are not read; a utility that merged or changed its EIA number starts again under its new number; the latest year's months may be preliminary.

**Reproduce.** `python util-total-u861-19876-va.reproduce.py <the table's CSV>` and `do util-total-u861-19876-va.reproduce.do` (Stata) recompute the figures by year from the tables as the public downloads hold them; each names the expected values at its top.
