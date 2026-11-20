# Who sends power to whom: the Carolinas to the Mid-Atlantic

Draft `scan-deep-65c4a017ae13` of the findings hunt over the whole warehouse (chain 502), 2026-11-19. State: draft, not reviewed. Review at `/internal/findings`.

**The finding.** The mean hourly flow of power from the Carolinas to the Mid-Atlantic (EIA's regions) was 767 MW in 2025, against 363 MW in 2019, the first full year the ERW holds.

![Who sends power to whom, the Carolinas to the Mid-Atlantic](pair-flow-rp-car-mida.png)

**The figure by full year** (MW): 2019: 363, 2020: 37, 2021: 245, 2022: 343, 2023: 709, 2024: 824, 2025: 767.

**The tables and rows.** `eia930_region_pair_hourly`; the rows for the Carolinas to the Mid-Atlantic, region key `rp_car_mida` (the card's `hunt.region`), years 2019 to 2025. The yearly values: `pair-flow-rp-car-mida.csv`.

**Its strength.** The change is 1.69 typical yearly moves (a typical move is 239 MW, 1.4826 times the median absolute change between full years). Holds in more than one year: 3 of the 6 full years after 2019 lie above 2019's value. Survives a change of window: from 2020 to 2025 the change is 730, from 2019 to 2024 it is 461. Sample large enough: 2019 holds 8,760 and 2025 holds 8,735 observations; the floor is 8,000. Half the change remains without the first year: from 2020 to 2025 the change is 730, 180.5 percent of the change from 2019. At least one typical yearly move: the change is 1.69 typical yearly moves (239 MW a year, the median move between full years); the floor is 1.

**Its limits.** EIA-930 as the balancing authorities report it, each region's figure summed from its authorities' reports; the ties between two regions can change over the years; a mean of the hours held, not a metered annual total. A negative mean is a year power flowed the other way on balance.

**Reproduce.** `python pair-flow-rp-car-mida.reproduce.py <the table's CSV>` and `do pair-flow-rp-car-mida.reproduce.do` (Stata) recompute the figures by year from the tables as the public downloads hold them; each names the expected values at its top.
