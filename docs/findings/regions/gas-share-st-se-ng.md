# What a region burns: natural gas: Georgia and Alabama (the core of EIA's Southeast region)

Draft `scan-deep-118efafef19d` of the findings hunt over the whole warehouse (chain 502), 2026-11-19. State: draft, not reviewed. Review at `/internal/findings`.

**The finding.** Natural gas's share of the net generation of Georgia and Alabama (the core of EIA's Southeast region) was 42.2 percent in 2025, against 5.5 percent in 2001, the first full year the ERW holds.

![What a region burns: natural gas, Georgia and Alabama (the core of EIA's Southeast region)](gas-share-st-se-ng.png)

**The figure by full year** (percent): 2001: 5.5, 2002: 8.8, 2003: 6.3, 2004: 8.4, 2005: 8.6, 2006: 11.6, 2007: 13.6, 2008: 12.7, 2009: 19.2, 2010: 21.8, 2011: 26.4, 2012: 35.7, 2013: 32.0, 2014: 32.4, 2015: 37.8, 2016: 40.1, 2017: 39.5, 2018: 40.4, 2019: 42.7, 2020: 44.4, 2021: 41.6, 2022: 45.0, 2023: 45.4, 2024: 43.0, 2025: 42.2.

**The tables and rows.** `eia_state_generation_monthly`; the rows for Georgia and Alabama (the core of EIA's Southeast region), region key `st_se_ng` (the card's `hunt.region`), years 2001 to 2025. The yearly values: `gas-share-st-se-ng.csv`.

**Its strength.** The change is 10.48 typical yearly moves (a typical move is 3.5 percent, 1.4826 times the median absolute change between full years). Holds in more than one year: 24 of the 24 full years after 2001 lie above 2001's value. Survives a change of window: from 2002 to 2025 the change is 33.4, from 2001 to 2024 it is 37.5. Sample large enough: 2001 holds 12 and 2025 holds 12 observations; the floor is 12. Half the change remains without the first year: from 2002 to 2025 the change is 33.4, 91.1 percent of the change from 2001. At least one typical yearly move: the change is 10.48 typical yearly moves (3.5 percent a year, the median move between full years); the floor is 1.

**Its limits.** EIA's state net generation by fuel, all sectors; the states stand for the region and are not its footprint; the latest months are preliminary.

**Reproduce.** `python gas-share-st-se-ng.reproduce.py <the table's CSV>` and `do gas-share-st-se-ng.reproduce.do` (Stata) recompute the figures by year from the tables as the public downloads hold them; each names the expected values at its top.
