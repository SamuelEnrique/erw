# What a utility sells to commercial customers: Arizona Public Service Co in AZ

Draft `scan-deep-a980d2a74e65` of the findings hunt over the whole warehouse (chain 502), 2026-11-19. State: draft, not reviewed. Review at `/internal/findings`.

**The finding.** The retail electricity sales to commercial customers of Arizona Public Service Co in AZ was 17.34 TWh in 2025, against 12.42 TWh in 2017, the first full year the ERW holds.

![What a utility sells to commercial customers, Arizona Public Service Co in AZ](util-commercial-u861-803-az.png)

**The figure by full year** (TWh): 2017: 12.42, 2018: 12.53, 2019: 12.44, 2020: 12.35, 2021: 12.84, 2022: 13.64, 2023: 14.33, 2024: 16.07, 2025: 17.34.

**The tables and rows.** `eia861m_utility_sales_monthly`; the rows for Arizona Public Service Co in AZ, region key `u861_803_az` (the card's `hunt.region`), years 2017 to 2025. The yearly values: `util-commercial-u861-803-az.csv`.

**Its strength.** The change is 5.62 typical yearly moves (a typical move is 0.88 TWh, 1.4826 times the median absolute change between full years). Holds in more than one year: 7 of the 8 full years after 2017 lie above 2017's value. Survives a change of window: from 2018 to 2025 the change is 4.81, from 2017 to 2024 it is 3.65. Sample large enough: 2017 holds 12 and 2025 holds 12 observations; the floor is 12. Half the change remains without the first year: from 2018 to 2025 the change is 4.81, 97.7 percent of the change from 2017. At least one typical yearly move: the change is 5.62 typical yearly moves (0.88 TWh a year, the median move between full years); the floor is 1.

**Its limits.** EIA Form 861M as the utility filed it, in one state, its sales to the customers it serves; states with retail or community choice are not read; a utility that merged or changed its EIA number starts again under its new number; the latest year's months may be preliminary.

**Reproduce.** `python util-commercial-u861-803-az.reproduce.py <the table's CSV>` and `do util-commercial-u861-803-az.reproduce.do` (Stata) recompute the figures by year from the tables as the public downloads hold them; each names the expected values at its top.
