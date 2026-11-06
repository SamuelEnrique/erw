# Solar's share: the United States

Draft `scan-deep-74babf6df9f2` of the findings hunt over the whole warehouse (chain 164), 2026-11-06. State: draft, not reviewed. Review at `/internal/findings`.

**The finding.** Utility-scale solar's share of net generation in the United States was 6.8 percent of net generation in 2025, against 0.0 percent of net generation in 2001, the first full year the ERW holds.

![Solar's share, the United States](solar-share-state-sun-us.png)

**The figure by full year** (percent of net generation): 2001: 0.0, 2002: 0.0, 2003: 0.0, 2004: 0.0, 2005: 0.0, 2006: 0.0, 2007: 0.0, 2008: 0.0, 2009: 0.0, 2010: 0.0, 2011: 0.0, 2012: 0.1, 2013: 0.2, 2014: 0.4, 2015: 0.6, 2016: 0.9, 2017: 1.3, 2018: 1.5, 2019: 1.7, 2020: 2.2, 2021: 2.8, 2022: 3.4, 2023: 4.0, 2024: 5.1, 2025: 6.8.

**The tables and rows.** `eia_state_generation_monthly`; the rows for the United States, region key `state_sun_US` (the card's `hunt.region`), years 2001 to 2025. The yearly values: `solar-share-state-sun-us.csv`.

**Its strength.** The change is 31.13 typical yearly moves (a typical move is 0.2 percent of net generation, 1.4826 times the median absolute change between full years). Holds in more than one year: 19 of the 24 full years after 2001 lie above 2001's value. Survives a change of window: from 2002 to 2025 the change is 6.8, from 2001 to 2024 it is 5.1. Sample large enough: 2001 holds 12 and 2025 holds 12 observations; the floor is 11. Half the change remains without the first year: from 2002 to 2025 the change is 6.8, 100.0 percent of the change from 2001. At least one typical yearly move: the change is 31.13 typical yearly moves (0.2 percent of net generation a year, the median move between full years); the floor is 1.

**Its limits.** EIA's monthly net generation as published, the latest months preliminary; a state's share counts what is generated in it, not what is used in it, and EIA withholds some plants' months.

**Reproduce.** `python solar-share-state-sun-us.reproduce.py <the table's CSV>` and `do solar-share-state-sun-us.reproduce.do` (Stata) recompute the figures by year from the tables as the public downloads hold them; each names the expected values at its top.
