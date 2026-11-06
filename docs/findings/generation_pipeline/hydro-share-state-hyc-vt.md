# Hydro's share: Vermont

Draft `scan-deep-5498dfb70ce7` of the findings hunt over the whole warehouse (chain 164), 2026-11-06. State: draft, not reviewed. Review at `/internal/findings`.

**The finding.** Conventional hydro's share of net generation in Vermont was 49.7 percent of net generation in 2025, against 16.1 percent of net generation in 2001, the first full year the ERW holds.

![Hydro's share, Vermont](hydro-share-state-hyc-vt.png)

**The figure by full year** (percent of net generation): 2001: 16.1, 2002: 20.4, 2003: 19.1, 2004: 21.7, 2005: 21.2, 2006: 21.4, 2007: 11.1, 2008: 21.9, 2009: 20.4, 2010: 20.3, 2011: 21.0, 2012: 17.4, 2013: 18.7, 2014: 16.7, 2015: 57.5, 2016: 56.4, 2017: 59.8, 2018: 58.2, 2019: 58.4, 2020: 52.4, 2021: 51.8, 2022: 52.2, 2023: 62.1, 2024: 56.8, 2025: 49.7.

**The tables and rows.** `eia_state_generation_monthly`; the rows for Vermont, region key `state_hyc_VT` (the card's `hunt.region`), years 2001 to 2025. The yearly values: `hydro-share-state-hyc-vt.csv`.

**Its strength.** The change is 12.76 typical yearly moves (a typical move is 2.6 percent of net generation, 1.4826 times the median absolute change between full years). Holds in more than one year: 23 of the 24 full years after 2001 lie above 2001's value. Survives a change of window: from 2002 to 2025 the change is 29.3, from 2001 to 2024 it is 40.7. Sample large enough: 2001 holds 12 and 2025 holds 12 observations; the floor is 11. Half the change remains without the first year: from 2002 to 2025 the change is 29.3, 87.2 percent of the change from 2001. At least one typical yearly move: the change is 12.76 typical yearly moves (2.6 percent of net generation a year, the median move between full years); the floor is 1.

**Its limits.** EIA's monthly net generation as published, the latest months preliminary; a state's share counts what is generated in it, not what is used in it, and EIA withholds some plants' months. Hydro follows the year's water, so a dry last year moves the figure.

**Reproduce.** `python hydro-share-state-hyc-vt.reproduce.py <the table's CSV>` and `do hydro-share-state-hyc-vt.reproduce.do` (Stata) recompute the figures by year from the tables as the public downloads hold them; each names the expected values at its top.
