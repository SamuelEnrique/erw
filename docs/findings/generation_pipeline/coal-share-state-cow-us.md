# Coal's share: the United States

Draft `scan-deep-c7c053517090` of the findings hunt over the whole warehouse (chain 164), 2026-11-06. State: draft, not reviewed. Review at `/internal/findings`.

**The finding.** Coal's share of net generation in the United States was 16.6 percent of net generation in 2025, against 51.0 percent of net generation in 2001, the first full year the ERW holds.

![Coal's share, the United States](coal-share-state-cow-us.png)

**The figure by full year** (percent of net generation): 2001: 51.0, 2002: 50.1, 2003: 50.8, 2004: 49.8, 2005: 49.6, 2006: 49.0, 2007: 48.5, 2008: 48.2, 2009: 44.4, 2010: 44.8, 2011: 42.3, 2012: 37.4, 2013: 38.9, 2014: 38.6, 2015: 33.2, 2016: 30.4, 2017: 29.9, 2018: 27.5, 2019: 23.4, 2020: 19.3, 2021: 21.9, 2022: 19.7, 2023: 16.1, 2024: 15.1, 2025: 16.6.

**The tables and rows.** `eia_state_generation_monthly`; the rows for the United States, region key `state_cow_US` (the card's `hunt.region`), years 2001 to 2025. The yearly values: `coal-share-state-cow-us.csv`.

**Its strength.** The change is 15.68 typical yearly moves (a typical move is 2.2 percent of net generation, 1.4826 times the median absolute change between full years). Holds in more than one year: 24 of the 24 full years after 2001 lie below 2001's value. Survives a change of window: from 2002 to 2025 the change is -33.5, from 2001 to 2024 it is -35.8. Sample large enough: 2001 holds 12 and 2025 holds 12 observations; the floor is 11. Half the change remains without the first year: from 2002 to 2025 the change is -33.5, 97.5 percent of the change from 2001. At least one typical yearly move: the change is 15.68 typical yearly moves (2.2 percent of net generation a year, the median move between full years); the floor is 1.

**Its limits.** EIA's monthly net generation as published, the latest months preliminary; a state's share counts what is generated in it, not what is used in it, and EIA withholds some plants' months.

**Reproduce.** `python coal-share-state-cow-us.reproduce.py <the table's CSV>` and `do coal-share-state-cow-us.reproduce.do` (Stata) recompute the figures by year from the tables as the public downloads hold them; each names the expected values at its top.
