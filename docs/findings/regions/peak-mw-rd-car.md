# The year's peak hour: the Carolinas (EIA's region)

Draft `scan-deep-d4403f54182e` of the findings hunt over the whole warehouse (chain 502), 2026-11-19. State: draft, not reviewed. Review at `/internal/findings`.

**The finding.** The highest hour of demand in the Carolinas (EIA's region) was 47,130 MW in 2025, against 41,648 MW in 2019, the first full year the ERW holds.

![The year's peak hour, the Carolinas (EIA's region)](peak-mw-rd-car.png)

**The figure by full year** (MW): 2019: 41,648, 2020: 42,008, 2021: 42,154, 2022: 44,630, 2023: 43,307, 2024: 44,816, 2025: 47,130.

**The tables and rows.** `eia930_ba_demand_hourly`; the rows for the Carolinas (EIA's region), region key `rd_car` (the card's `hunt.region`), years 2019 to 2025. The yearly values: `peak-mw-rd-car.csv`.

**Its strength.** The change is 2.61 typical yearly moves (a typical move is 2,099 MW, 1.4826 times the median absolute change between full years). Holds in more than one year: 6 of the 6 full years after 2019 lie above 2019's value. Survives a change of window: from 2020 to 2025 the change is 5,122, from 2019 to 2024 it is 3,168. Sample large enough: 2019 holds 8,758 and 2025 holds 8,711 observations; the floor is 8,000. Half the change remains without the first year: from 2020 to 2025 the change is 5,122, 93.4 percent of the change from 2019. At least one typical yearly move: the change is 2.61 typical yearly moves (2,099 MW a year, the median move between full years); the floor is 1.

**Its limits.** EIA-930 as the balancing authorities report it; a region's demand is the sum of its authorities that file demand, an hour held only when all of them do; not adjusted for weather.

**Reproduce.** `python peak-mw-rd-car.reproduce.py <the table's CSV>` and `do peak-mw-rd-car.reproduce.do` (Stata) recompute the figures by year from the tables as the public downloads hold them; each names the expected values at its top.
