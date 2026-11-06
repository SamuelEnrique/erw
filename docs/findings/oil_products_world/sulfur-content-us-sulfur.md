# How sour us refineries' crude is: the United States

Draft `scan-deep-1df42fc6e86d` of the findings hunt over the whole warehouse (chain 164), 2026-11-06. State: draft, not reviewed. Review at `/internal/findings`.

**The finding.** The average sulfur content of the crude oil run in US refineries was 1.299 percent sulfur by weight in 2025, against 0.912 percent sulfur by weight in 1985, the first full year the ERW holds.

![How sour us refineries' crude is, the United States](sulfur-content-us-sulfur.png)

**The figure by full year** (percent sulfur by weight): 1985: 0.912, 1986: 0.958, 1987: 0.989, 1988: 1.042, 1989: 1.060, 1990: 1.099, 1991: 1.135, 1992: 1.164, 1993: 1.147, 1994: 1.144, 1995: 1.126, 1996: 1.148, 1997: 1.254, 1998: 1.305, 1999: 1.327, 2000: 1.342, 2001: 1.417, 2002: 1.414, 2003: 1.427, 2004: 1.432, 2005: 1.420, 2006: 1.414, 2007: 1.430, 2008: 1.455, 2009: 1.410, 2010: 1.393, 2011: 1.399, 2012: 1.422, 2013: 1.438, 2014: 1.452, 2015: 1.397, 2016: 1.432, 2017: 1.409, 2018: 1.402, 2019: 1.284, 2020: 1.336, 2021: 1.267, 2022: 1.292, 2023: 1.333, 2024: 1.308, 2025: 1.299.

**The tables and rows.** `eia_crude_quality_monthly`; the rows for the United States, region key `us_sulfur` (the card's `hunt.region`), years 1985 to 2025. The yearly values: `sulfur-content-us-sulfur.csv`.

**Its strength.** The change is 11.62 typical yearly moves (a typical move is 0.033 percent sulfur by weight, 1.4826 times the median absolute change between full years). Holds in more than one year: 40 of the 40 full years after 1985 lie above 1985's value. Survives a change of window: from 1986 to 2025 the change is 0.342, from 1985 to 2024 it is 0.397. Sample large enough: 1985 holds 12 and 2025 holds 12 observations; the floor is 11. Half the change remains without the first year: from 1986 to 2025 the change is 0.342, 88.2 percent of the change from 1985. At least one typical yearly move: the change is 11.62 typical yearly moves (0.033 percent sulfur by weight a year, the median move between full years); the floor is 1.

**Its limits.** EIA's monthly figures as published, the latest months preliminary.

**Reproduce.** `python sulfur-content-us-sulfur.reproduce.py <the table's CSV>` and `do sulfur-content-us-sulfur.reproduce.do` (Stata) recompute the figures by year from the tables as the public downloads hold them; each names the expected values at its top.
