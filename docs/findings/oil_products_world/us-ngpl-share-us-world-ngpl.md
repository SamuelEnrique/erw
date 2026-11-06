# The us share of world ngpl: the United States

Draft `scan-deep-c17e0814cc1d` of the findings hunt over the whole warehouse (chain 164), 2026-11-06. State: draft, not reviewed. Review at `/internal/findings`.

**The finding.** The US share of world natural gas plant liquids production was 50.5 percent of world NGPL in 2025, against 28.4 percent of world NGPL in 1993, the first full year the ERW holds.

![The us share of world ngpl, the United States](us-ngpl-share-us-world-ngpl.png)

**The figure by full year** (percent of world NGPL): 1993: 28.4, 1994: 27.7, 1995: 27.3, 1996: 27.1, 1997: 26.4, 1998: 25.5, 1999: 26.0, 2000: 26.6, 2001: 25.4, 2002: 24.9, 2003: 26.2, 2004: 26.8, 2005: 24.9, 2006: 24.7, 2007: 25.3, 2008: 21.6, 2009: 22.7, 2010: 25.6, 2011: 26.3, 2012: 27.0, 2013: 28.7, 2014: 31.4, 2015: 33.6, 2016: 34.3, 2017: 34.1, 2018: 37.4, 2019: 39.8, 2020: 42.1, 2021: 43.4, 2022: 45.3, 2023: 47.6, 2024: 49.2, 2025: 50.5.

**The tables and rows.** `eia_world_oil_monthly`; the rows for the United States, region key `us_world_ngpl` (the card's `hunt.region`), years 1993 to 2025. The yearly values: `us-ngpl-share-us-world-ngpl.csv`.

**Its strength.** The change is 13.11 typical yearly moves (a typical move is 1.7 percent of world NGPL, 1.4826 times the median absolute change between full years). Holds in more than one year: 13 of the 32 full years after 1993 lie above 1993's value. Survives a change of window: from 1994 to 2025 the change is 22.8, from 1993 to 2024 it is 20.8. Sample large enough: 1993 holds 12 and 2025 holds 12 observations; the floor is 11. Half the change remains without the first year: from 1994 to 2025 the change is 22.8, 102.9 percent of the change from 1993. At least one typical yearly move: the change is 13.11 typical yearly moves (1.7 percent of world NGPL a year, the median move between full years); the floor is 1.

**Its limits.** EIA's monthly figures as published, the latest months preliminary.

**Reproduce.** `python us-ngpl-share-us-world-ngpl.reproduce.py <the table's CSV>` and `do us-ngpl-share-us-world-ngpl.reproduce.do` (Stata) recompute the figures by year from the tables as the public downloads hold them; each names the expected values at its top.
