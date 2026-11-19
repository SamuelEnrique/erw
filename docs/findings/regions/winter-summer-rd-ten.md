# Winter's peak against summer's: Tennessee (EIA's region)

Draft `scan-deep-31425ae0f32b` of the findings hunt over the whole warehouse (chain 502), 2026-11-19. State: draft, not reviewed. Review at `/internal/findings`.

**The finding.** The winter peak hour of Tennessee (EIA's region) as a percent of its summer peak hour was 109.2 percent in 2025, against 94.0 percent in 2019, the first full year the ERW holds.

![Winter's peak against summer's, Tennessee (EIA's region)](winter-summer-rd-ten.png)

**The figure by full year** (percent): 2019: 94.0, 2020: 94.7, 2021: 94.0, 2022: 105.1, 2023: 81.8, 2024: 111.1, 2025: 109.2.

**The tables and rows.** `eia930_ba_demand_hourly`; the rows for Tennessee (EIA's region), region key `rd_ten` (the card's `hunt.region`), years 2019 to 2025. The yearly values: `winter-summer-rd-ten.csv`.

**Its strength.** The change is 1.58 typical yearly moves (a typical move is 9.6 percent, 1.4826 times the median absolute change between full years). Holds in more than one year: 4 of the 6 full years after 2019 lie above 2019's value. Survives a change of window: from 2020 to 2025 the change is 14.5, from 2019 to 2024 it is 17.1. Sample large enough: 2019 holds 8,760 and 2025 holds 8,760 observations; the floor is 8,000. Half the change remains without the first year: from 2020 to 2025 the change is 14.5, 95.4 percent of the change from 2019. At least one typical yearly move: the change is 1.58 typical yearly moves (9.6 percent a year, the median move between full years); the floor is 1.

**Its limits.** EIA-930 as the balancing authorities report it; a region's demand is the sum of its authorities that file demand, an hour held only when all of them do; not adjusted for weather. A year's winter is its own January, February and December.

**Reproduce.** `python winter-summer-rd-ten.reproduce.py <the table's CSV>` and `do winter-summer-rd-ten.reproduce.do` (Stata) recompute the figures by year from the tables as the public downloads hold them; each names the expected values at its top.
