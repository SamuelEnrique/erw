# What a region burns: coal: Georgia and Alabama (the core of EIA's Southeast region)

Draft `scan-deep-8b404ff9c84f` of the findings hunt over the whole warehouse (chain 502), 2026-11-19. State: draft, not reviewed. Review at `/internal/findings`.

**The finding.** Coal's share of the net generation of Georgia and Alabama (the core of EIA's Southeast region) was 14.4 percent in 2025, against 60.2 percent in 2001, the first full year the ERW holds.

![What a region burns: coal, Georgia and Alabama (the core of EIA's Southeast region)](coal-share-st-se-cow.png)

**The figure by full year** (percent): 2001: 60.2, 2002: 58.2, 2003: 59.4, 2004: 58.6, 2005: 60.2, 2006: 59.0, 2007: 58.2, 2008: 56.8, 2009: 46.0, 2010: 47.1, 2011: 41.6, 2012: 31.4, 2013: 32.1, 2014: 33.6, 2015: 27.9, 2016: 26.2, 2017: 23.9, 2018: 23.3, 2019: 19.1, 2020: 13.8, 2021: 17.2, 2022: 15.7, 2023: 13.4, 2024: 13.7, 2025: 14.4.

**The tables and rows.** `eia_state_generation_monthly`; the rows for Georgia and Alabama (the core of EIA's Southeast region), region key `st_se_cow` (the card's `hunt.region`), years 2001 to 2025. The yearly values: `coal-share-st-se-cow.csv`.

**Its strength.** The change is 19.86 typical yearly moves (a typical move is 2.3 percent, 1.4826 times the median absolute change between full years). Holds in more than one year: 24 of the 24 full years after 2001 lie below 2001's value. Survives a change of window: from 2002 to 2025 the change is -43.7, from 2001 to 2024 it is -46.5. Sample large enough: 2001 holds 12 and 2025 holds 12 observations; the floor is 12. Half the change remains without the first year: from 2002 to 2025 the change is -43.7, 95.5 percent of the change from 2001. At least one typical yearly move: the change is 19.86 typical yearly moves (2.3 percent a year, the median move between full years); the floor is 1.

**Its limits.** EIA's state net generation by fuel, all sectors; the states stand for the region and are not its footprint; the latest months are preliminary.

**Reproduce.** `python coal-share-st-se-cow.reproduce.py <the table's CSV>` and `do coal-share-st-se-cow.reproduce.do` (Stata) recompute the figures by year from the tables as the public downloads hold them; each names the expected values at its top.
