# Appalachia's coal: Appalachia

Draft `scan-deep-8435505023e3` of the findings hunt over the whole warehouse (chain 164), 2026-11-06. State: draft, not reviewed. Review at `/internal/findings`.

**The finding.** Appalachia's share of US coal production was 30.8 percent of US coal production in 2024, against 38.2 percent of US coal production in 2001, the first full year the ERW holds.

![Appalachia's coal, Appalachia](appalachia-share-app-coal.png)

**The figure by full year** (percent of US coal production): 2001: 38.2, 2002: 36.2, 2003: 35.1, 2004: 35.1, 2005: 35.1, 2006: 33.6, 2007: 32.9, 2008: 33.3, 2009: 31.8, 2010: 30.9, 2011: 30.7, 2012: 28.7, 2013: 27.4, 2014: 26.7, 2015: 24.6, 2016: 24.7, 2017: 25.5, 2018: 26.5, 2019: 27.4, 2020: 25.9, 2021: 26.9, 2022: 27.0, 2023: 28.6, 2024: 30.8.

**The tables and rows.** `eia_coal_production_annual`; the rows for Appalachia, region key `app_coal` (the card's `hunt.region`), years 2001 to 2024. The yearly values: `appalachia-share-app-coal.csv`.

**Its strength.** The change is 5.41 typical yearly moves (a typical move is 1.4 percent of US coal production, 1.4826 times the median absolute change between full years). Holds in more than one year: 23 of the 23 full years after 2001 lie below 2001's value. Survives a change of window: from 2002 to 2024 the change is -5.4, from 2001 to 2023 it is -9.6. Sample large enough: 2001 holds 1 and 2024 holds 1 observations; the floor is 1. Half the change remains without the first year: from 2002 to 2024 the change is -5.4, 72.9 percent of the change from 2001. At least one typical yearly move: the change is 5.41 typical yearly moves (1.4 percent of US coal production a year, the median move between full years); the floor is 1.

**Its limits.** EIA's annual coal data as published, the latest year preliminary.

**Reproduce.** `python appalachia-share-app-coal.reproduce.py <the table's CSV>` and `do appalachia-share-app-coal.reproduce.do` (Stata) recompute the figures by year from the tables as the public downloads hold them; each names the expected values at its top.
