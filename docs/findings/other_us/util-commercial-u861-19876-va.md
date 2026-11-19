# What a utility sells to commercial customers: Virginia Electric & Power Co in VA

Draft `scan-deep-e7375da4bac2` of the findings hunt over the whole warehouse (chain 502), 2026-11-19. State: draft, not reviewed. Review at `/internal/findings`.

**The finding.** The retail electricity sales to commercial customers of Virginia Electric & Power Co in VA was 60.09 TWh in 2025, against 41.54 TWh in 2017, the first full year the ERW holds.

![What a utility sells to commercial customers, Virginia Electric & Power Co in VA](util-commercial-u861-19876-va.png)

**The figure by full year** (TWh): 2017: 41.54, 2018: 43.05, 2019: 44.68, 2020: 42.54, 2021: 44.64, 2022: 49.33, 2023: 53.09, 2024: 55.94, 2025: 60.09.

**The tables and rows.** `eia861m_utility_sales_monthly`; the rows for Virginia Electric & Power Co in VA, region key `u861_19876_va` (the card's `hunt.region`), years 2017 to 2025. The yearly values: `util-commercial-u861-19876-va.csv`.

**Its strength.** The change is 5.02 typical yearly moves (a typical move is 3.69 TWh, 1.4826 times the median absolute change between full years). Holds in more than one year: 8 of the 8 full years after 2017 lie above 2017's value. Survives a change of window: from 2018 to 2025 the change is 17.04, from 2017 to 2024 it is 14.40. Sample large enough: 2017 holds 12 and 2025 holds 12 observations; the floor is 12. Half the change remains without the first year: from 2018 to 2025 the change is 17.04, 91.8 percent of the change from 2017. At least one typical yearly move: the change is 5.02 typical yearly moves (3.69 TWh a year, the median move between full years); the floor is 1.

**Its limits.** EIA Form 861M as the utility filed it, in one state, its sales to the customers it serves; states with retail or community choice are not read; a utility that merged or changed its EIA number starts again under its new number; the latest year's months may be preliminary.

**Reproduce.** `python util-commercial-u861-19876-va.reproduce.py <the table's CSV>` and `do util-commercial-u861-19876-va.reproduce.do` (Stata) recompute the figures by year from the tables as the public downloads hold them; each names the expected values at its top.
