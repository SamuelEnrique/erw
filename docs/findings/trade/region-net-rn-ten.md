# Net exports and imports by region: Tennessee (EIA's region), a net importer over 2019 to 2025

Draft `scan-deep-522465acb129` of the findings hunt over the whole warehouse (chain 502), 2026-11-19. State: draft, not reviewed. Review at `/internal/findings`.

**The finding.** The year's net imports of Tennessee (EIA's region) as a share of its demand was 4.9 percent in 2025, against -1.1 percent in 2019, the first full year the ERW holds.

![Net exports and imports by region, Tennessee (EIA's region), a net importer over 2019 to 2025](region-net-rn-ten.png)

**The figure by full year** (percent): 2019: -1.1, 2020: 0.5, 2021: 2.3, 2022: 3.5, 2023: 1.9, 2024: 4.5, 2025: 4.9.

**The tables and rows.** `eia930_region_hourly`, `eia930_ba_demand_hourly`; the rows for Tennessee (EIA's region), a net importer over 2019 to 2025, region key `rn_ten` (the card's `hunt.region`), years 2019 to 2025. The yearly values: `region-net-rn-ten.csv`.

**Its strength.** The change is 2.47 typical yearly moves (a typical move is 2.4 percent, 1.4826 times the median absolute change between full years). Holds in more than one year: 6 of the 6 full years after 2019 lie above 2019's value. Survives a change of window: from 2020 to 2025 the change is 4.4, from 2019 to 2024 it is 5.6. Sample large enough: 2019 holds 8,759 and 2025 holds 8,759 observations; the floor is 8,000. Half the change remains without the first year: from 2020 to 2025 the change is 4.4, 72.7 percent of the change from 2019. At least one typical yearly move: the change is 2.47 typical yearly moves (2.4 percent a year, the median move between full years); the floor is 1.

**Its limits.** EIA-930 as the balancing authorities report it, each region's figure summed from its authorities' reports; the ties between two regions can change over the years; flows between two authorities of one region cancel only as far as both report them alike; a negative figure is a year the region traded the other way on net; demand is summed from the region's authorities that file it.

**Reproduce.** `python region-net-rn-ten.reproduce.py <the table's CSV>` and `do region-net-rn-ten.reproduce.do` (Stata) recompute the figures by year from the tables as the public downloads hold them; each names the expected values at its top.
