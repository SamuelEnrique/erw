# Coal from underground: the United States

Draft `scan-deep-df7d4d19e204` of the findings hunt over the whole warehouse (chain 164), 2026-11-06. State: draft, not reviewed. Review at `/internal/findings`.

**The finding.** The share of US coal mined underground was 40.2 percent of US coal production in 2024, against 33.8 percent of US coal production in 2001, the first full year the ERW holds.

![Coal from underground, the United States](underground-share-us-underground.png)

**The figure by full year** (percent of US coal production): 2001: 33.8, 2002: 32.7, 2003: 32.9, 2004: 33.1, 2005: 32.6, 2006: 30.9, 2007: 30.7, 2008: 30.5, 2009: 30.9, 2010: 31.1, 2011: 31.5, 2012: 33.7, 2013: 34.7, 2014: 35.5, 2015: 34.2, 2016: 34.6, 2017: 35.3, 2018: 36.4, 2019: 37.9, 2020: 36.5, 2021: 38.2, 2022: 37.4, 2023: 37.7, 2024: 40.2.

**The tables and rows.** `eia_coal_production_annual`; the rows for the United States, region key `us_underground` (the card's `hunt.region`), years 2001 to 2024. The yearly values: `underground-share-us-underground.csv`.

**Its strength.** The change is 5.64 typical yearly moves (a typical move is 1.1 percent of US coal production, 1.4826 times the median absolute change between full years). Holds in more than one year: 12 of the 23 full years after 2001 lie above 2001's value. Survives a change of window: from 2002 to 2024 the change is 7.6, from 2001 to 2023 it is 4.0. Sample large enough: 2001 holds 1 and 2024 holds 1 observations; the floor is 1. Half the change remains without the first year: from 2002 to 2024 the change is 7.6, 116.9 percent of the change from 2001. At least one typical yearly move: the change is 5.64 typical yearly moves (1.1 percent of US coal production a year, the median move between full years); the floor is 1.

**Its limits.** EIA's annual coal data as published, the latest year preliminary.

**Reproduce.** `python underground-share-us-underground.reproduce.py <the table's CSV>` and `do underground-share-us-underground.reproduce.do` (Stata) recompute the figures by year from the tables as the public downloads hold them; each names the expected values at its top.
