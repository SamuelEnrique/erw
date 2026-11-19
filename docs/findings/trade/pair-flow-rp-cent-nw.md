# Who sends power to whom: the Central region to the Northwest

Draft `scan-deep-1ae83c196fbc` of the findings hunt over the whole warehouse (chain 502), 2026-11-19. State: draft, not reviewed. Review at `/internal/findings`.

**The finding.** The mean hourly flow of power from the Central region to the Northwest (EIA's regions) was 254 MW in 2025, against 7 MW in 2019, the first full year the ERW holds.

![Who sends power to whom, the Central region to the Northwest](pair-flow-rp-cent-nw.png)

**The figure by full year** (MW): 2019: 7, 2020: 55, 2021: 263, 2022: 222, 2023: 233, 2024: 189, 2025: 254.

**The tables and rows.** `eia930_region_pair_hourly`; the rows for the Central region to the Northwest, region key `rp_cent_nw` (the card's `hunt.region`), years 2019 to 2025. The yearly values: `pair-flow-rp-cent-nw.csv`.

**Its strength.** The change is 3.62 typical yearly moves (a typical move is 68 MW, 1.4826 times the median absolute change between full years). Holds in more than one year: 6 of the 6 full years after 2019 lie above 2019's value. Survives a change of window: from 2020 to 2025 the change is 199, from 2019 to 2024 it is 182. Sample large enough: 2019 holds 8,760 and 2025 holds 8,759 observations; the floor is 8,000. Half the change remains without the first year: from 2020 to 2025 the change is 199, 80.8 percent of the change from 2019. At least one typical yearly move: the change is 3.62 typical yearly moves (68 MW a year, the median move between full years); the floor is 1.

**Its limits.** EIA-930 as the balancing authorities report it, each region's figure summed from its authorities' reports; the ties between two regions can change over the years; a mean of the hours held, not a metered annual total. A negative mean is a year power flowed the other way on balance.

**Reproduce.** `python pair-flow-rp-cent-nw.reproduce.py <the table's CSV>` and `do pair-flow-rp-cent-nw.reproduce.do` (Stata) recompute the figures by year from the tables as the public downloads hold them; each names the expected values at its top.
