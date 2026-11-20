# Summer hours a flow runs the other way: Canada to New York

Draft `scan-deep-dddea4d22ef3` of the findings hunt over the whole warehouse (chain 502), 2026-11-19. State: draft, not reviewed. Review at `/internal/findings`.

**The finding.** The share of June to August hours in which power flowed the other way to its usual direction, from Canada to New York was 49.8 percent of hours in 2025, against 0.0 percent of hours in 2019, the first full year the ERW holds.

![Summer hours a flow runs the other way, Canada to New York](pair-against-summer-rp-can-ny.png)

**The figure by full year** (percent of hours): 2019: 0.0, 2020: 0.0, 2021: 0.0, 2022: 0.0, 2023: 14.7, 2024: 3.8, 2025: 49.8.

**The tables and rows.** `eia930_region_pair_hourly`; the rows for Canada to New York, region key `rp_can_ny` (the card's `hunt.region`), years 2019 to 2025. The yearly values: `pair-against-summer-rp-can-ny.csv`.

**Its strength.** The change is 6.16 typical yearly moves (a typical move is 8.1 percent of hours, 1.4826 times the median absolute change between full years). Holds in more than one year: 3 of the 6 full years after 2019 lie above 2019's value. Survives a change of window: from 2020 to 2025 the change is 49.8, from 2019 to 2024 it is 3.8. Sample large enough: 2019 holds 2,208 and 2025 holds 2,208 observations; the floor is 2,000. Half the change remains without the first year: from 2020 to 2025 the change is 49.8, 100.0 percent of the change from 2019. At least one typical yearly move: the change is 6.16 typical yearly moves (8.1 percent of hours a year, the median move between full years); the floor is 1.

**Its limits.** EIA-930 as the balancing authorities report it, each region's figure summed from its authorities' reports; the ties between two regions can change over the years; months are UTC months.

**Reproduce.** `python pair-against-summer-rp-can-ny.reproduce.py <the table's CSV>` and `do pair-against-summer-rp-can-ny.reproduce.do` (Stata) recompute the figures by year from the tables as the public downloads hold them; each names the expected values at its top.
