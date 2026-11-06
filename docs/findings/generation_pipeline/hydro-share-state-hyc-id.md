# Hydro's share: Idaho

Draft `scan-deep-5b3aa3ba26bb` of the findings hunt over the whole warehouse (chain 164), 2026-11-06. State: draft, not reviewed. Review at `/internal/findings`.

**The finding.** Conventional hydro's share of net generation in Idaho was 43.6 percent of net generation in 2025, against 77.3 percent of net generation in 2001, the first full year the ERW holds.

![Hydro's share, Idaho](hydro-share-state-hyc-id.png)

**The figure by full year** (percent of net generation): 2001: 77.3, 2002: 89.6, 2003: 80.2, 2004: 77.9, 2005: 78.9, 2006: 84.0, 2007: 78.6, 2008: 78.2, 2009: 79.6, 2010: 76.1, 2011: 80.9, 2012: 70.6, 2013: 55.8, 2014: 59.3, 2015: 55.9, 2016: 57.7, 2017: 61.3, 2018: 60.7, 2019: 56.1, 2020: 53.8, 2021: 47.5, 2022: 51.4, 2023: 47.0, 2024: 45.7, 2025: 43.6.

**The tables and rows.** `eia_state_generation_monthly`; the rows for Idaho, region key `state_hyc_ID` (the card's `hunt.region`), years 2001 to 2025. The yearly values: `hydro-share-state-hyc-id.csv`.

**Its strength.** The change is 6.32 typical yearly moves (a typical move is 5.3 percent of net generation, 1.4826 times the median absolute change between full years). Holds in more than one year: 15 of the 24 full years after 2001 lie below 2001's value. Survives a change of window: from 2002 to 2025 the change is -46.0, from 2001 to 2024 it is -31.6. Sample large enough: 2001 holds 12 and 2025 holds 12 observations; the floor is 11. Half the change remains without the first year: from 2002 to 2025 the change is -46.0, 136.6 percent of the change from 2001. At least one typical yearly move: the change is 6.32 typical yearly moves (5.3 percent of net generation a year, the median move between full years); the floor is 1.

**Its limits.** EIA's monthly net generation as published, the latest months preliminary; a state's share counts what is generated in it, not what is used in it, and EIA withholds some plants' months. Hydro follows the year's water, so a dry last year moves the figure.

**Reproduce.** `python hydro-share-state-hyc-id.reproduce.py <the table's CSV>` and `do hydro-share-state-hyc-id.reproduce.do` (Stata) recompute the figures by year from the tables as the public downloads hold them; each names the expected values at its top.
