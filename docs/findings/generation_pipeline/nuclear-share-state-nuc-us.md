# Nuclear's share: the United States

Draft `scan-deep-55e4412f65bd` of the findings hunt over the whole warehouse (chain 164), 2026-11-06. State: draft, not reviewed. Review at `/internal/findings`.

**The finding.** Nuclear's share of net generation in the United States was 17.7 percent of net generation in 2025, against 20.6 percent of net generation in 2001, the first full year the ERW holds.

![Nuclear's share, the United States](nuclear-share-state-nuc-us.png)

**The figure by full year** (percent of net generation): 2001: 20.6, 2002: 20.2, 2003: 19.7, 2004: 19.9, 2005: 19.3, 2006: 19.4, 2007: 19.4, 2008: 19.6, 2009: 20.2, 2010: 19.6, 2011: 19.3, 2012: 19.0, 2013: 19.4, 2014: 19.5, 2015: 19.5, 2016: 19.8, 2017: 19.9, 2018: 19.3, 2019: 19.6, 2020: 19.7, 2021: 19.0, 2022: 18.2, 2023: 18.5, 2024: 18.1, 2025: 17.7.

**The tables and rows.** `eia_state_generation_monthly`; the rows for the United States, region key `state_nuc_US` (the card's `hunt.region`), years 2001 to 2025. The yearly values: `nuclear-share-state-nuc-us.csv`.

**Its strength.** The change is 6.56 typical yearly moves (a typical move is 0.4 percent of net generation, 1.4826 times the median absolute change between full years). Holds in more than one year: 24 of the 24 full years after 2001 lie below 2001's value. Survives a change of window: from 2002 to 2025 the change is -2.5, from 2001 to 2024 it is -2.4. Sample large enough: 2001 holds 12 and 2025 holds 12 observations; the floor is 11. Half the change remains without the first year: from 2002 to 2025 the change is -2.5, 87.3 percent of the change from 2001. At least one typical yearly move: the change is 6.56 typical yearly moves (0.4 percent of net generation a year, the median move between full years); the floor is 1.

**Its limits.** EIA's monthly net generation as published, the latest months preliminary; a state's share counts what is generated in it, not what is used in it, and EIA withholds some plants' months.

**Reproduce.** `python nuclear-share-state-nuc-us.reproduce.py <the table's CSV>` and `do nuclear-share-state-nuc-us.reproduce.do` (Stata) recompute the figures by year from the tables as the public downloads hold them; each names the expected values at its top.
