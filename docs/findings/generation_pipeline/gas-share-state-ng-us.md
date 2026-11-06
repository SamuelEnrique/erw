# Gas's share: the United States

Draft `scan-deep-9c2774360dec` of the findings hunt over the whole warehouse (chain 164), 2026-11-06. State: draft, not reviewed. Review at `/internal/findings`.

**The finding.** Natural gas's share of net generation in the United States was 40.9 percent of net generation in 2025, against 17.1 percent of net generation in 2001, the first full year the ERW holds.

![Gas's share, the United States](gas-share-state-ng-us.png)

**The figure by full year** (percent of net generation): 2001: 17.1, 2002: 17.9, 2003: 16.7, 2004: 17.9, 2005: 18.8, 2006: 20.1, 2007: 21.6, 2008: 21.4, 2009: 23.3, 2010: 23.9, 2011: 24.7, 2012: 30.3, 2013: 27.7, 2014: 27.5, 2015: 32.7, 2016: 33.8, 2017: 32.2, 2018: 35.2, 2019: 38.5, 2020: 40.6, 2021: 38.4, 2022: 39.9, 2023: 43.2, 2024: 43.4, 2025: 40.9.

**The tables and rows.** `eia_state_generation_monthly`; the rows for the United States, region key `state_ng_US` (the card's `hunt.region`), years 2001 to 2025. The yearly values: `gas-share-state-ng-us.csv`.

**Its strength.** The change is 10.95 typical yearly moves (a typical move is 2.2 percent of net generation, 1.4826 times the median absolute change between full years). Holds in more than one year: 23 of the 24 full years after 2001 lie above 2001's value. Survives a change of window: from 2002 to 2025 the change is 23.0, from 2001 to 2024 it is 26.3. Sample large enough: 2001 holds 12 and 2025 holds 12 observations; the floor is 11. Half the change remains without the first year: from 2002 to 2025 the change is 23.0, 96.6 percent of the change from 2001. At least one typical yearly move: the change is 10.95 typical yearly moves (2.2 percent of net generation a year, the median move between full years); the floor is 1.

**Its limits.** EIA's monthly net generation as published, the latest months preliminary; a state's share counts what is generated in it, not what is used in it, and EIA withholds some plants' months.

**Reproduce.** `python gas-share-state-ng-us.reproduce.py <the table's CSV>` and `do gas-share-state-ng-us.reproduce.do` (Stata) recompute the figures by year from the tables as the public downloads hold them; each names the expected values at its top.
