# What a utility sells to commercial customers: Omaha Public Power District in NE

Draft `scan-deep-47f67551e2cc` of the findings hunt over the whole warehouse (chain 502), 2026-11-19. State: draft, not reviewed. Review at `/internal/findings`.

**The finding.** The retail electricity sales to commercial customers of Omaha Public Power District in NE was 7.88 TWh in 2025, against 3.67 TWh in 2017, the first full year the ERW holds.

![What a utility sells to commercial customers, Omaha Public Power District in NE](util-commercial-u861-14127-ne.png)

**The figure by full year** (TWh): 2017: 3.67, 2018: 3.75, 2019: 3.75, 2020: 3.55, 2021: 3.65, 2022: 3.80, 2023: 3.78, 2024: 6.42, 2025: 7.88.

**The tables and rows.** `eia861m_utility_sales_monthly`; the rows for Omaha Public Power District in NE, region key `u861_14127_ne` (the card's `hunt.region`), years 2017 to 2025. The yearly values: `util-commercial-u861-14127-ne.csv`.

**Its strength.** The change is 22.62 typical yearly moves (a typical move is 0.19 TWh, 1.4826 times the median absolute change between full years). Holds in more than one year: 6 of the 8 full years after 2017 lie above 2017's value. Survives a change of window: from 2018 to 2025 the change is 4.12, from 2017 to 2024 it is 2.75. Sample large enough: 2017 holds 12 and 2025 holds 12 observations; the floor is 12. Half the change remains without the first year: from 2018 to 2025 the change is 4.12, 97.9 percent of the change from 2017. At least one typical yearly move: the change is 22.62 typical yearly moves (0.19 TWh a year, the median move between full years); the floor is 1.

**Its limits.** EIA Form 861M as the utility filed it, in one state, its sales to the customers it serves; states with retail or community choice are not read; a utility that merged or changed its EIA number starts again under its new number; the latest year's months may be preliminary.

**Reproduce.** `python util-commercial-u861-14127-ne.reproduce.py <the table's CSV>` and `do util-commercial-u861-14127-ne.reproduce.do` (Stata) recompute the figures by year from the tables as the public downloads hold them; each names the expected values at its top.
