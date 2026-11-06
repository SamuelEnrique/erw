# Wind's share: South Dakota

Draft `scan-deep-169f53d4acf2` of the findings hunt over the whole warehouse (chain 164), 2026-11-06. State: draft, not reviewed. Review at `/internal/findings`.

**The finding.** Wind's share of net generation in South Dakota was 58.2 percent of net generation in 2025, against 0.0 percent of net generation in 2001, the first full year the ERW holds.

![Wind's share, South Dakota](wind-share-state-wnd-sd.png)

**The figure by full year** (percent of net generation): 2001: 0.0, 2002: 0.1, 2003: 0.6, 2004: 2.1, 2005: 2.4, 2006: 2.1, 2007: 2.4, 2008: 2.0, 2009: 5.1, 2010: 13.6, 2011: 22.2, 2012: 20.5, 2013: 26.6, 2014: 21.2, 2015: 25.9, 2016: 32.2, 2017: 27.1, 2018: 22.5, 2019: 19.2, 2020: 39.2, 2021: 53.8, 2022: 57.5, 2023: 53.8, 2024: 57.8, 2025: 58.2.

**The tables and rows.** `eia_state_generation_monthly`; the rows for South Dakota, region key `state_wnd_SD` (the card's `hunt.region`), years 2001 to 2025. The yearly values: `wind-share-state-wnd-sd.csv`.

**Its strength.** The change is 10.59 typical yearly moves (a typical move is 5.5 percent of net generation, 1.4826 times the median absolute change between full years). Holds in more than one year: 24 of the 24 full years after 2001 lie above 2001's value. Survives a change of window: from 2002 to 2025 the change is 58.1, from 2001 to 2024 it is 57.8. Sample large enough: 2001 holds 12 and 2025 holds 12 observations; the floor is 11. Half the change remains without the first year: from 2002 to 2025 the change is 58.1, 99.9 percent of the change from 2001. At least one typical yearly move: the change is 10.59 typical yearly moves (5.5 percent of net generation a year, the median move between full years); the floor is 1.

**Its limits.** EIA's monthly net generation as published, the latest months preliminary; a state's share counts what is generated in it, not what is used in it, and EIA withholds some plants' months.

**Reproduce.** `python wind-share-state-wnd-sd.reproduce.py <the table's CSV>` and `do wind-share-state-wnd-sd.reproduce.do` (Stata) recompute the figures by year from the tables as the public downloads hold them; each names the expected values at its top.
