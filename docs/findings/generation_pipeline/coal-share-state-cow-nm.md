# Coal's share: New Mexico

Draft `scan-deep-fc5e1d762a8e` of the findings hunt over the whole warehouse (chain 164), 2026-11-06. State: draft, not reviewed. Review at `/internal/findings`.

**The finding.** Coal's share of net generation in New Mexico was 20.7 percent of net generation in 2025, against 84.5 percent of net generation in 2001, the first full year the ERW holds.

![Coal's share, New Mexico](coal-share-state-cow-nm.png)

**The figure by full year** (percent of net generation): 2001: 84.5, 2002: 87.7, 2003: 88.0, 2004: 88.8, 2005: 85.2, 2006: 80.1, 2007: 76.7, 2008: 73.0, 2009: 73.4, 2010: 70.7, 2011: 71.1, 2012: 68.2, 2013: 67.3, 2014: 63.0, 2015: 62.5, 2016: 55.8, 2017: 54.8, 2018: 41.0, 2019: 41.8, 2020: 37.5, 2021: 35.6, 2022: 32.5, 2023: 18.8, 2024: 21.2, 2025: 20.7.

**The tables and rows.** `eia_state_generation_monthly`; the rows for New Mexico, region key `state_cow_NM` (the card's `hunt.region`), years 2001 to 2025. The yearly values: `coal-share-state-cow-nm.csv`.

**Its strength.** The change is 15.40 typical yearly moves (a typical move is 4.1 percent of net generation, 1.4826 times the median absolute change between full years). Holds in more than one year: 20 of the 24 full years after 2001 lie below 2001's value. Survives a change of window: from 2002 to 2025 the change is -67.0, from 2001 to 2024 it is -63.3. Sample large enough: 2001 holds 12 and 2025 holds 12 observations; the floor is 11. Half the change remains without the first year: from 2002 to 2025 the change is -67.0, 105.1 percent of the change from 2001. At least one typical yearly move: the change is 15.40 typical yearly moves (4.1 percent of net generation a year, the median move between full years); the floor is 1.

**Its limits.** EIA's monthly net generation as published, the latest months preliminary; a state's share counts what is generated in it, not what is used in it, and EIA withholds some plants' months.

**Reproduce.** `python coal-share-state-cow-nm.reproduce.py <the table's CSV>` and `do coal-share-state-cow-nm.reproduce.do` (Stata) recompute the figures by year from the tables as the public downloads hold them; each names the expected values at its top.
