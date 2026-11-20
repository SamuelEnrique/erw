# Hours a region trades the other way: California (EIA's region), a net importer over 2019 to 2025

Draft `scan-deep-2529c550a4f6` of the findings hunt over the whole warehouse (chain 502), 2026-11-19. State: draft, not reviewed. Review at `/internal/findings`.

**The finding.** The share of the year's hours in which California, a net importer over 2019 to 2025, exported on net was 5.0 percent of hours in 2025, against 0.4 percent of hours in 2019, the first full year the ERW holds.

![Hours a region trades the other way, California (EIA's region), a net importer over 2019 to 2025](region-against-rn-cal.png)

**The figure by full year** (percent of hours): 2019: 0.4, 2020: 0.0, 2021: 0.4, 2022: 0.5, 2023: 9.2, 2025: 5.0.

**The tables and rows.** `eia930_region_hourly`; the rows for California (EIA's region), a net importer over 2019 to 2025, region key `rn_cal` (the card's `hunt.region`), years 2019 to 2025. The yearly values: `region-against-rn-cal.csv`.

**Its strength.** The change is 7.42 typical yearly moves (a typical move is 0.6 percent of hours, 1.4826 times the median absolute change between full years). Holds in more than one year: 4 of the 5 full years after 2019 lie above 2019's value. Survives a change of window: from 2020 to 2025 the change is 5.0, from 2019 to 2023 it is 8.8. Sample large enough: 2019 holds 8,664 and 2025 holds 8,664 observations; the floor is 8,000. Half the change remains without the first year: from 2020 to 2025 the change is 5.0, 108.5 percent of the change from 2019. At least one typical yearly move: the change is 7.42 typical yearly moves (0.6 percent of hours a year, the median move between full years); the floor is 1.

**Its limits.** EIA-930 as the balancing authorities report it, each region's figure summed from its authorities' reports; the ties between two regions can change over the years.

**Reproduce.** `python region-against-rn-cal.reproduce.py <the table's CSV>` and `do region-against-rn-cal.reproduce.do` (Stata) recompute the figures by year from the tables as the public downloads hold them; each names the expected values at its top.
