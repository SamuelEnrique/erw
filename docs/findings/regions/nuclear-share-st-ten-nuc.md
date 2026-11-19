# What a region generates: nuclear: Tennessee (the state, the core of the Tennessee Valley Authority)

Draft `scan-deep-5f80e7755fda` of the findings hunt over the whole warehouse (chain 502), 2026-11-19. State: draft, not reviewed. Review at `/internal/findings`.

**The finding.** Nuclear's share of the net generation of Tennessee (the state, the core of the Tennessee Valley Authority) was 38.9 percent in 2025, against 29.7 percent in 2001, the first full year the ERW holds.

![What a region generates: nuclear, Tennessee (the state, the core of the Tennessee Valley Authority)](nuclear-share-st-ten-nuc.png)

**The figure by full year** (percent): 2001: 29.7, 2002: 28.7, 2003: 26.2, 2004: 29.3, 2005: 28.6, 2006: 26.3, 2007: 30.2, 2008: 29.8, 2009: 33.8, 2010: 33.7, 2011: 33.2, 2012: 32.3, 2013: 35.8, 2014: 34.8, 2015: 33.2, 2016: 37.3, 2017: 40.3, 2018: 44.4, 2019: 43.4, 2020: 45.5, 2021: 44.7, 2022: 45.7, 2023: 48.8, 2024: 42.3, 2025: 38.9.

**The tables and rows.** `eia_state_generation_monthly`; the rows for Tennessee (the state, the core of the Tennessee Valley Authority), region key `st_ten_nuc` (the card's `hunt.region`), years 2001 to 2025. The yearly values: `nuclear-share-st-ten-nuc.csv`.

**Its strength.** The change is 2.75 typical yearly moves (a typical move is 3.3 percent, 1.4826 times the median absolute change between full years). Holds in more than one year: 19 of the 24 full years after 2001 lie above 2001's value. Survives a change of window: from 2002 to 2025 the change is 10.2, from 2001 to 2024 it is 12.6. Sample large enough: 2001 holds 12 and 2025 holds 12 observations; the floor is 12. Half the change remains without the first year: from 2002 to 2025 the change is 10.2, 111.0 percent of the change from 2001. At least one typical yearly move: the change is 2.75 typical yearly moves (3.3 percent a year, the median move between full years); the floor is 1.

**Its limits.** EIA's state net generation by fuel, all sectors; the states stand for the region and are not its footprint; the latest months are preliminary.

**Reproduce.** `python nuclear-share-st-ten-nuc.reproduce.py <the table's CSV>` and `do nuclear-share-st-ten-nuc.reproduce.do` (Stata) recompute the figures by year from the tables as the public downloads hold them; each names the expected values at its top.
