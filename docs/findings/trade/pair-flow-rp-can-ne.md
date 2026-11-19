# Who sends power to whom: Canada to New England

Draft `scan-deep-67ed24112ca7` of the findings hunt over the whole warehouse (chain 502), 2026-11-19. State: draft, not reviewed. Review at `/internal/findings`.

**The finding.** The mean hourly flow of power from Canada to New England (EIA's regions) was 432 MW in 2025, against 1,945 MW in 2019, the first full year the ERW holds.

![Who sends power to whom, Canada to New England](pair-flow-rp-can-ne.png)

**The figure by full year** (MW): 2019: 1,945, 2020: 1,843, 2021: 1,830, 2022: 1,774, 2023: 1,430, 2024: 697, 2025: 432.

**The tables and rows.** `eia930_region_pair_hourly`; the rows for Canada to New England, region key `rp_can_ne` (the card's `hunt.region`), years 2019 to 2025. The yearly values: `pair-flow-rp-can-ne.csv`.

**Its strength.** The change is 5.56 typical yearly moves (a typical move is 272 MW, 1.4826 times the median absolute change between full years). Holds in more than one year: 6 of the 6 full years after 2019 lie below 2019's value. Survives a change of window: from 2020 to 2025 the change is -1,411, from 2019 to 2024 it is -1,248. Sample large enough: 2019 holds 8,760 and 2025 holds 8,760 observations; the floor is 8,000. Half the change remains without the first year: from 2020 to 2025 the change is -1,411, 93.2 percent of the change from 2019. At least one typical yearly move: the change is 5.56 typical yearly moves (272 MW a year, the median move between full years); the floor is 1.

**Its limits.** EIA-930 as the balancing authorities report it, each region's figure summed from its authorities' reports; the ties between two regions can change over the years; a mean of the hours held, not a metered annual total. A negative mean is a year power flowed the other way on balance.

**Reproduce.** `python pair-flow-rp-can-ne.reproduce.py <the table's CSV>` and `do pair-flow-rp-can-ne.reproduce.do` (Stata) recompute the figures by year from the tables as the public downloads hold them; each names the expected values at its top.
