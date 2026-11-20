# What a region burns: coal: Arizona and New Mexico (the core of EIA's Southwest region)

Draft `scan-deep-31ba19ff68cb` of the findings hunt over the whole warehouse (chain 502), 2026-11-19. State: draft, not reviewed. Review at `/internal/findings`.

**The finding.** Coal's share of the net generation of Arizona and New Mexico (the core of EIA's Southwest region) was 11.2 percent in 2025, against 55.4 percent in 2001, the first full year the ERW holds.

![What a region burns: coal, Arizona and New Mexico (the core of EIA's Southwest region)](coal-share-st-sw-cow.png)

**The figure by full year** (percent): 2001: 55.4, 2002: 52.2, 2003: 52.6, 2004: 50.2, 2005: 51.3, 2006: 49.6, 2007: 46.1, 2008: 45.3, 2009: 45.4, 2010: 46.8, 2011: 48.4, 2012: 44.1, 2013: 45.3, 2014: 43.6, 2015: 38.8, 2016: 34.4, 2017: 35.7, 2018: 30.5, 2019: 25.5, 2020: 18.5, 2021: 18.7, 2022: 18.4, 2023: 12.9, 2024: 11.7, 2025: 11.2.

**The tables and rows.** `eia_state_generation_monthly`; the rows for Arizona and New Mexico (the core of EIA's Southwest region), region key `st_sw_cow` (the card's `hunt.region`), years 2001 to 2025. The yearly values: `coal-share-st-sw-cow.csv`.

**Its strength.** The change is 18.09 typical yearly moves (a typical move is 2.4 percent, 1.4826 times the median absolute change between full years). Holds in more than one year: 24 of the 24 full years after 2001 lie below 2001's value. Survives a change of window: from 2002 to 2025 the change is -41.0, from 2001 to 2024 it is -43.7. Sample large enough: 2001 holds 12 and 2025 holds 12 observations; the floor is 12. Half the change remains without the first year: from 2002 to 2025 the change is -41.0, 92.7 percent of the change from 2001. At least one typical yearly move: the change is 18.09 typical yearly moves (2.4 percent a year, the median move between full years); the floor is 1.

**Its limits.** EIA's state net generation by fuel, all sectors; the states stand for the region and are not its footprint; the latest months are preliminary.

**Reproduce.** `python coal-share-st-sw-cow.reproduce.py <the table's CSV>` and `do coal-share-st-sw-cow.reproduce.do` (Stata) recompute the figures by year from the tables as the public downloads hold them; each names the expected values at its top.
