# What a region burns: natural gas: North and South Carolina (EIA's Carolinas region)

Draft `scan-deep-7d8c7c828717` of the findings hunt over the whole warehouse (chain 502), 2026-11-19. State: draft, not reviewed. Review at `/internal/findings`.

**The finding.** Natural gas's share of the net generation of North and South Carolina (EIA's Carolinas region) was 32.4 percent in 2025, against 1.3 percent in 2001, the first full year the ERW holds.

![What a region burns: natural gas, North and South Carolina (EIA's Carolinas region)](gas-share-st-car-ng.png)

**The figure by full year** (percent): 2001: 1.3, 2002: 3.6, 2003: 1.5, 2004: 2.8, 2005: 3.7, 2006: 4.1, 2007: 4.5, 2008: 4.4, 2009: 6.7, 2010: 8.3, 2011: 10.9, 2012: 15.8, 2013: 18.0, 2014: 17.8, 2015: 23.6, 2016: 24.4, 2017: 25.2, 2018: 27.9, 2019: 28.1, 2020: 29.4, 2021: 31.0, 2022: 35.3, 2023: 33.2, 2024: 33.3, 2025: 32.4.

**The tables and rows.** `eia_state_generation_monthly`; the rows for North and South Carolina (EIA's Carolinas region), region key `st_car_ng` (the card's `hunt.region`), years 2001 to 2025. The yearly values: `gas-share-st-car-ng.csv`.

**Its strength.** The change is 14.55 typical yearly moves (a typical move is 2.1 percent, 1.4826 times the median absolute change between full years). Holds in more than one year: 24 of the 24 full years after 2001 lie above 2001's value. Survives a change of window: from 2002 to 2025 the change is 28.8, from 2001 to 2024 it is 31.9. Sample large enough: 2001 holds 12 and 2025 holds 12 observations; the floor is 12. Half the change remains without the first year: from 2002 to 2025 the change is 28.8, 92.5 percent of the change from 2001. At least one typical yearly move: the change is 14.55 typical yearly moves (2.1 percent a year, the median move between full years); the floor is 1.

**Its limits.** EIA's state net generation by fuel, all sectors; the states stand for the region and are not its footprint; the latest months are preliminary.

**Reproduce.** `python gas-share-st-car-ng.reproduce.py <the table's CSV>` and `do gas-share-st-car-ng.reproduce.do` (Stata) recompute the figures by year from the tables as the public downloads hold them; each names the expected values at its top.
