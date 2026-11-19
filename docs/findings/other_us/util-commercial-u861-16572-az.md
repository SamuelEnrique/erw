# What a utility sells to commercial customers: Salt River Project in AZ

Draft `scan-deep-077d3b859569` of the findings hunt over the whole warehouse (chain 502), 2026-11-19. State: draft, not reviewed. Review at `/internal/findings`.

**The finding.** The retail electricity sales to commercial customers of Salt River Project in AZ was 14.70 TWh in 2025, against 11.54 TWh in 2017, the first full year the ERW holds.

![What a utility sells to commercial customers, Salt River Project in AZ](util-commercial-u861-16572-az.png)

**The figure by full year** (TWh): 2017: 11.54, 2018: 11.67, 2019: 11.59, 2020: 11.45, 2021: 11.84, 2022: 12.40, 2023: 12.72, 2024: 13.77, 2025: 14.70.

**The tables and rows.** `eia861m_utility_sales_monthly`; the rows for Salt River Project in AZ, region key `u861_16572_az` (the card's `hunt.region`), years 2017 to 2025. The yearly values: `util-commercial-u861-16572-az.csv`.

**Its strength.** The change is 6.06 typical yearly moves (a typical move is 0.52 TWh, 1.4826 times the median absolute change between full years). Holds in more than one year: 7 of the 8 full years after 2017 lie above 2017's value. Survives a change of window: from 2018 to 2025 the change is 3.03, from 2017 to 2024 it is 2.22. Sample large enough: 2017 holds 12 and 2025 holds 12 observations; the floor is 12. Half the change remains without the first year: from 2018 to 2025 the change is 3.03, 95.9 percent of the change from 2017. At least one typical yearly move: the change is 6.06 typical yearly moves (0.52 TWh a year, the median move between full years); the floor is 1.

**Its limits.** EIA Form 861M as the utility filed it, in one state, its sales to the customers it serves; states with retail or community choice are not read; a utility that merged or changed its EIA number starts again under its new number; the latest year's months may be preliminary.

**Reproduce.** `python util-commercial-u861-16572-az.reproduce.py <the table's CSV>` and `do util-commercial-u861-16572-az.reproduce.do` (Stata) recompute the figures by year from the tables as the public downloads hold them; each names the expected values at its top.
