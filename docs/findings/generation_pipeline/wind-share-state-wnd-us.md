# Wind's share: the United States

Draft `scan-deep-f02c2bc8cd8a` of the findings hunt over the whole warehouse (chain 164), 2026-11-06. State: draft, not reviewed. Review at `/internal/findings`.

**The finding.** Wind's share of net generation in the United States was 10.4 percent of net generation in 2025, against 0.2 percent of net generation in 2001, the first full year the ERW holds.

![Wind's share, the United States](wind-share-state-wnd-us.png)

**The figure by full year** (percent of net generation): 2001: 0.2, 2002: 0.3, 2003: 0.3, 2004: 0.4, 2005: 0.4, 2006: 0.7, 2007: 0.8, 2008: 1.3, 2009: 1.9, 2010: 2.3, 2011: 2.9, 2012: 3.5, 2013: 4.1, 2014: 4.4, 2015: 4.7, 2016: 5.6, 2017: 6.3, 2018: 6.5, 2019: 7.2, 2020: 8.4, 2021: 9.2, 2022: 10.3, 2023: 10.1, 2024: 10.5, 2025: 10.4.

**The tables and rows.** `eia_state_generation_monthly`; the rows for the United States, region key `state_wnd_US` (the card's `hunt.region`), years 2001 to 2025. The yearly values: `wind-share-state-wnd-us.csv`.

**Its strength.** The change is 16.36 typical yearly moves (a typical move is 0.6 percent of net generation, 1.4826 times the median absolute change between full years). Holds in more than one year: 24 of the 24 full years after 2001 lie above 2001's value. Survives a change of window: from 2002 to 2025 the change is 10.2, from 2001 to 2024 it is 10.3. Sample large enough: 2001 holds 12 and 2025 holds 12 observations; the floor is 11. Half the change remains without the first year: from 2002 to 2025 the change is 10.2, 99.1 percent of the change from 2001. At least one typical yearly move: the change is 16.36 typical yearly moves (0.6 percent of net generation a year, the median move between full years); the floor is 1.

**Its limits.** EIA's monthly net generation as published, the latest months preliminary; a state's share counts what is generated in it, not what is used in it, and EIA withholds some plants' months.

**Reproduce.** `python wind-share-state-wnd-us.reproduce.py <the table's CSV>` and `do wind-share-state-wnd-us.reproduce.do` (Stata) recompute the figures by year from the tables as the public downloads hold them; each names the expected values at its top.
