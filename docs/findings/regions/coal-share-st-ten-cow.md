# What a region burns: coal: Tennessee (the state, the core of the Tennessee Valley Authority)

Draft `scan-deep-5d09ce2221a0` of the findings hunt over the whole warehouse (chain 502), 2026-11-19. State: draft, not reviewed. Review at `/internal/findings`.

**The finding.** Coal's share of the net generation of Tennessee (the state, the core of the Tennessee Valley Authority) was 23.9 percent in 2025, against 62.1 percent in 2001, the first full year the ERW holds.

![What a region burns: coal, Tennessee (the state, the core of the Tennessee Valley Authority)](coal-share-st-ten-cow.png)

**The figure by full year** (percent): 2001: 62.1, 2002: 62.1, 2003: 59.6, 2004: 59.5, 2005: 60.8, 2006: 64.4, 2007: 63.3, 2008: 62.9, 2009: 52.2, 2010: 53.0, 2011: 50.3, 2012: 45.6, 2013: 40.8, 2014: 45.1, 2015: 40.7, 2016: 39.3, 2017: 35.1, 2018: 25.7, 2019: 22.7, 2020: 17.7, 2021: 23.1, 2022: 20.4, 2023: 20.3, 2024: 22.9, 2025: 23.9.

**The tables and rows.** `eia_state_generation_monthly`; the rows for Tennessee (the state, the core of the Tennessee Valley Authority), region key `st_ten_cow` (the card's `hunt.region`), years 2001 to 2025. The yearly values: `coal-share-st-ten-cow.csv`.

**Its strength.** The change is 9.38 typical yearly moves (a typical move is 4.1 percent, 1.4826 times the median absolute change between full years). Holds in more than one year: 20 of the 24 full years after 2001 lie below 2001's value. Survives a change of window: from 2002 to 2025 the change is -38.2, from 2001 to 2024 it is -39.2. Sample large enough: 2001 holds 12 and 2025 holds 12 observations; the floor is 12. Half the change remains without the first year: from 2002 to 2025 the change is -38.2, 100.1 percent of the change from 2001. At least one typical yearly move: the change is 9.38 typical yearly moves (4.1 percent a year, the median move between full years); the floor is 1.

**Its limits.** EIA's state net generation by fuel, all sectors; the states stand for the region and are not its footprint; the latest months are preliminary.

**Reproduce.** `python coal-share-st-ten-cow.reproduce.py <the table's CSV>` and `do coal-share-st-ten-cow.reproduce.do` (Stata) recompute the figures by year from the tables as the public downloads hold them; each names the expected values at its top.
