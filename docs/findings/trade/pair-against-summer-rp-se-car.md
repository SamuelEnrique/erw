# Summer hours a flow runs the other way: the Southeast to the Carolinas

Draft `scan-deep-690abcb5ea2a` of the findings hunt over the whole warehouse (chain 502), 2026-11-19. State: draft, not reviewed. Review at `/internal/findings`.

**The finding.** The share of June to August hours in which power flowed the other way to its usual direction, from the Southeast to the Carolinas was 7.9 percent of hours in 2025, against 39.2 percent of hours in 2019, the first full year the ERW holds.

![Summer hours a flow runs the other way, the Southeast to the Carolinas](pair-against-summer-rp-se-car.png)

**The figure by full year** (percent of hours): 2019: 39.2, 2020: 33.4, 2021: 25.5, 2022: 23.1, 2023: 23.2, 2024: 8.8, 2025: 7.9.

**The tables and rows.** `eia930_region_pair_hourly`; the rows for the Southeast to the Carolinas, region key `rp_se_car` (the card's `hunt.region`), years 2019 to 2025. The yearly values: `pair-against-summer-rp-se-car.csv`.

**Its strength.** The change is 5.13 typical yearly moves (a typical move is 6.1 percent of hours, 1.4826 times the median absolute change between full years). Holds in more than one year: 6 of the 6 full years after 2019 lie below 2019's value. Survives a change of window: from 2020 to 2025 the change is -25.5, from 2019 to 2024 it is -30.4. Sample large enough: 2019 holds 2,208 and 2025 holds 2,208 observations; the floor is 2,000. Half the change remains without the first year: from 2020 to 2025 the change is -25.5, 81.4 percent of the change from 2019. At least one typical yearly move: the change is 5.13 typical yearly moves (6.1 percent of hours a year, the median move between full years); the floor is 1.

**Its limits.** EIA-930 as the balancing authorities report it, each region's figure summed from its authorities' reports; the ties between two regions can change over the years; months are UTC months.

**Reproduce.** `python pair-against-summer-rp-se-car.reproduce.py <the table's CSV>` and `do pair-against-summer-rp-se-car.reproduce.do` (Stata) recompute the figures by year from the tables as the public downloads hold them; each names the expected values at its top.
