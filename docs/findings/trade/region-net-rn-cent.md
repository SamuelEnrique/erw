# Net exports and imports by region: the Central region (EIA's region), a net exporter over 2019 to 2025

Draft `scan-deep-7aafd49adf1e` of the findings hunt over the whole warehouse (chain 502), 2026-11-19. State: draft, not reviewed. Review at `/internal/findings`.

**The finding.** The year's net exports of the Central region (EIA's region) as a share of its demand was 2.4 percent in 2025, against 3.8 percent in 2019, the first full year the ERW holds.

![Net exports and imports by region, the Central region (EIA's region), a net exporter over 2019 to 2025](region-net-rn-cent.png)

**The figure by full year** (percent): 2019: 3.8, 2020: 3.3, 2021: 3.3, 2022: 3.9, 2023: 2.8, 2024: 1.8, 2025: 2.4.

**The tables and rows.** `eia930_region_hourly`, `eia930_ba_demand_hourly`; the rows for the Central region (EIA's region), a net exporter over 2019 to 2025, region key `rn_cent` (the card's `hunt.region`), years 2019 to 2025. The yearly values: `region-net-rn-cent.csv`.

**Its strength.** The change is 1.60 typical yearly moves (a typical move is 0.8 percent, 1.4826 times the median absolute change between full years). Holds in more than one year: 5 of the 6 full years after 2019 lie below 2019's value. Survives a change of window: from 2020 to 2025 the change is -0.8, from 2019 to 2024 it is -1.9. Sample large enough: 2019 holds 8,760 and 2025 holds 8,758 observations; the floor is 8,000. Half the change remains without the first year: from 2020 to 2025 the change is -0.8, 62.5 percent of the change from 2019. At least one typical yearly move: the change is 1.60 typical yearly moves (0.8 percent a year, the median move between full years); the floor is 1.

**Its limits.** EIA-930 as the balancing authorities report it, each region's figure summed from its authorities' reports; the ties between two regions can change over the years; flows between two authorities of one region cancel only as far as both report them alike; a negative figure is a year the region traded the other way on net; demand is summed from the region's authorities that file it.

**Reproduce.** `python region-net-rn-cent.reproduce.py <the table's CSV>` and `do region-net-rn-cent.reproduce.do` (Stata) recompute the figures by year from the tables as the public downloads hold them; each names the expected values at its top.
