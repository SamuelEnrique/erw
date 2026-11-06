# Wyoming's coal: Wyoming

Draft `scan-deep-1073ac2d4c9f` of the findings hunt over the whole warehouse (chain 164), 2026-11-06. State: draft, not reviewed. Review at `/internal/findings`.

**The finding.** Wyoming's share of US coal production was 37.2 percent of US coal production in 2024, against 32.7 percent of US coal production in 2001, the first full year the ERW holds.

![Wyoming's coal, Wyoming](wyoming-share-wy-coal.png)

**The figure by full year** (percent of US coal production): 2001: 32.7, 2002: 34.1, 2003: 35.1, 2004: 35.7, 2005: 35.7, 2006: 38.4, 2007: 39.6, 2008: 39.9, 2009: 40.1, 2010: 40.8, 2011: 40.0, 2012: 39.5, 2013: 39.4, 2014: 39.6, 2015: 41.9, 2016: 40.8, 2017: 40.9, 2018: 40.2, 2019: 39.2, 2020: 40.8, 2021: 41.4, 2022: 41.2, 2023: 41.1, 2024: 37.2.

**The tables and rows.** `eia_coal_production_annual`; the rows for Wyoming, region key `wy_coal` (the card's `hunt.region`), years 2001 to 2024. The yearly values: `wyoming-share-wy-coal.csv`.

**Its strength.** The change is 4.86 typical yearly moves (a typical move is 0.9 percent of US coal production, 1.4826 times the median absolute change between full years). Holds in more than one year: 23 of the 23 full years after 2001 lie above 2001's value. Survives a change of window: from 2002 to 2024 the change is 3.1, from 2001 to 2023 it is 8.4. Sample large enough: 2001 holds 1 and 2024 holds 1 observations; the floor is 1. Half the change remains without the first year: from 2002 to 2024 the change is 3.1, 68.9 percent of the change from 2001. At least one typical yearly move: the change is 4.86 typical yearly moves (0.9 percent of US coal production a year, the median move between full years); the floor is 1.

**Its limits.** EIA's annual coal data as published, the latest year preliminary.

**Reproduce.** `python wyoming-share-wy-coal.reproduce.py <the table's CSV>` and `do wyoming-share-wy-coal.reproduce.do` (Stata) recompute the figures by year from the tables as the public downloads hold them; each names the expected values at its top.
