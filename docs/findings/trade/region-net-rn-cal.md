# Net exports and imports by region: California (EIA's region), a net importer over 2019 to 2025

Draft `scan-deep-21bfe2511e0e` of the findings hunt over the whole warehouse (chain 502), 2026-11-19. State: draft, not reviewed. Review at `/internal/findings`.

**The finding.** The year's net imports of California (EIA's region) as a share of its demand was 15.6 percent in 2025, against 22.6 percent in 2019, the first full year the ERW holds.

![Net exports and imports by region, California (EIA's region), a net importer over 2019 to 2025](region-net-rn-cal.png)

**The figure by full year** (percent): 2019: 22.6, 2020: 25.4, 2021: 23.2, 2022: 21.9, 2023: 13.4, 2025: 15.6.

**The tables and rows.** `eia930_region_hourly`, `eia930_ba_demand_hourly`; the rows for California (EIA's region), a net importer over 2019 to 2025, region key `rn_cal` (the card's `hunt.region`), years 2019 to 2025. The yearly values: `region-net-rn-cal.csv`.

**Its strength.** The change is 2.10 typical yearly moves (a typical move is 3.3 percent, 1.4826 times the median absolute change between full years). Holds in more than one year: 3 of the 5 full years after 2019 lie below 2019's value. Survives a change of window: from 2020 to 2025 the change is -9.8, from 2019 to 2023 it is -9.2. Sample large enough: 2019 holds 8,452 and 2025 holds 8,504 observations; the floor is 8,000. Half the change remains without the first year: from 2020 to 2025 the change is -9.8, 141.0 percent of the change from 2019. At least one typical yearly move: the change is 2.10 typical yearly moves (3.3 percent a year, the median move between full years); the floor is 1.

**Its limits.** EIA-930 as the balancing authorities report it, each region's figure summed from its authorities' reports; the ties between two regions can change over the years; flows between two authorities of one region cancel only as far as both report them alike; a negative figure is a year the region traded the other way on net; demand is summed from the region's authorities that file it.

**Reproduce.** `python region-net-rn-cal.reproduce.py <the table's CSV>` and `do region-net-rn-cal.reproduce.do` (Stata) recompute the figures by year from the tables as the public downloads hold them; each names the expected values at its top.
