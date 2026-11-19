# What a region burns: natural gas: Arizona and New Mexico (the core of EIA's Southwest region)

Draft `scan-deep-240ca67deccf` of the findings hunt over the whole warehouse (chain 502), 2026-11-19. State: draft, not reviewed. Review at `/internal/findings`.

**The finding.** Natural gas's share of the net generation of Arizona and New Mexico (the core of EIA's Southwest region) was 40.5 percent in 2025, against 14.4 percent in 2001, the first full year the ERW holds.

![What a region burns: natural gas, Arizona and New Mexico (the core of EIA's Southwest region)](gas-share-st-sw-ng.png)

**The figure by full year** (percent): 2001: 14.4, 2002: 16.6, 2003: 17.7, 2004: 22.7, 2005: 24.2, 2006: 27.4, 2007: 30.2, 2008: 29.9, 2009: 28.6, 2010: 25.8, 2011: 21.7, 2012: 26.5, 2013: 25.9, 2014: 25.1, 2015: 29.5, 2016: 31.2, 2017: 27.8, 2018: 33.7, 2019: 38.9, 2020: 43.8, 2021: 40.4, 2022: 38.5, 2023: 44.4, 2024: 42.9, 2025: 40.5.

**The tables and rows.** `eia_state_generation_monthly`; the rows for Arizona and New Mexico (the core of EIA's Southwest region), region key `st_sw_ng` (the card's `hunt.region`), years 2001 to 2025. The yearly values: `gas-share-st-sw-ng.csv`.

**Its strength.** The change is 6.21 typical yearly moves (a typical move is 4.2 percent, 1.4826 times the median absolute change between full years). Holds in more than one year: 24 of the 24 full years after 2001 lie above 2001's value. Survives a change of window: from 2002 to 2025 the change is 23.9, from 2001 to 2024 it is 28.5. Sample large enough: 2001 holds 12 and 2025 holds 12 observations; the floor is 12. Half the change remains without the first year: from 2002 to 2025 the change is 23.9, 91.4 percent of the change from 2001. At least one typical yearly move: the change is 6.21 typical yearly moves (4.2 percent a year, the median move between full years); the floor is 1.

**Its limits.** EIA's state net generation by fuel, all sectors; the states stand for the region and are not its footprint; the latest months are preliminary.

**Reproduce.** `python gas-share-st-sw-ng.reproduce.py <the table's CSV>` and `do gas-share-st-sw-ng.reproduce.do` (Stata) recompute the figures by year from the tables as the public downloads hold them; each names the expected values at its top.
