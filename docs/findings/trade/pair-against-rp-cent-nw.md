# Hours a flow runs the other way: the Central region to the Northwest

Draft `scan-deep-3ed027c1bddb` of the findings hunt over the whole warehouse (chain 502), 2026-11-19. State: draft, not reviewed. Review at `/internal/findings`.

**The finding.** The share of the year's hours in which power flowed the other way to its usual direction, from the Central region to the Northwest was 15.7 percent of hours in 2025, against 50.7 percent of hours in 2019, the first full year the ERW holds.

![Hours a flow runs the other way, the Central region to the Northwest](pair-against-rp-cent-nw.png)

**The figure by full year** (percent of hours): 2019: 50.7, 2020: 43.8, 2021: 12.5, 2022: 17.5, 2023: 16.7, 2024: 19.4, 2025: 15.7.

**The tables and rows.** `eia930_region_pair_hourly`; the rows for the Central region to the Northwest, region key `rp_cent_nw` (the card's `hunt.region`), years 2019 to 2025. The yearly values: `pair-against-rp-cent-nw.csv`.

**Its strength.** The change is 5.45 typical yearly moves (a typical move is 6.4 percent of hours, 1.4826 times the median absolute change between full years). Holds in more than one year: 6 of the 6 full years after 2019 lie below 2019's value. Survives a change of window: from 2020 to 2025 the change is -28.1, from 2019 to 2024 it is -31.3. Sample large enough: 2019 holds 8,760 and 2025 holds 8,759 observations; the floor is 8,000. Half the change remains without the first year: from 2020 to 2025 the change is -28.1, 80.2 percent of the change from 2019. At least one typical yearly move: the change is 5.45 typical yearly moves (6.4 percent of hours a year, the median move between full years); the floor is 1.

**Its limits.** EIA-930 as the balancing authorities report it, each region's figure summed from its authorities' reports; the ties between two regions can change over the years; an hour at exactly zero counts as neither way.

**Reproduce.** `python pair-against-rp-cent-nw.reproduce.py <the table's CSV>` and `do pair-against-rp-cent-nw.reproduce.do` (Stata) recompute the figures by year from the tables as the public downloads hold them; each names the expected values at its top.
