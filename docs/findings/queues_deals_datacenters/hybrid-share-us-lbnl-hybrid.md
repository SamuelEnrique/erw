# Solar paired with batteries: the United States

Draft `scan-deep-55cf9c67bd30` of the findings hunt over the whole warehouse (chain 164), 2026-11-06. State: draft, not reviewed. Review at `/internal/findings`.

**The finding.** The share of the solar MW requested in the United States whose request also lists a battery was 37.0 percent of solar MW requested in 2024, against 0.0 percent of solar MW requested in 2005, the first year this measure counts.

![Solar paired with batteries, the United States](hybrid-share-us-lbnl-hybrid.png)

**The figure by full year** (percent of solar MW requested): 2005: 0.0, 2006: 15.4, 2007: 3.8, 2008: 3.7, 2009: 2.3, 2010: 5.0, 2011: 3.7, 2012: 10.3, 2013: 10.5, 2014: 4.0, 2015: 25.9, 2016: 12.0, 2017: 15.8, 2018: 25.2, 2019: 32.9, 2020: 38.4, 2021: 53.2, 2022: 49.3, 2023: 67.4, 2024: 37.0.

**The tables and rows.** `lbnl_interconnection_queue`; the rows for the United States, region key `us_lbnl_hybrid` (the card's `hunt.region`), years 2005 to 2024. The yearly values: `hybrid-share-us-lbnl-hybrid.csv`.

**Its strength.** The change is 3.82 typical yearly moves (a typical move is 9.7 percent of solar MW requested, 1.4826 times the median absolute change between full years). Holds in more than one year: 19 of the 19 full years after 2005 lie above 2005's value. Survives a change of window: from 2006 to 2024 the change is 21.6, from 2005 to 2023 it is 67.4. Sample large enough: 2005 holds 1 and 2024 holds 1 observations; the floor is 1. Half the change remains without the first year: from 2006 to 2024 the change is 21.6, 58.3 percent of the change from 2005. At least one typical yearly move: the change is 3.82 typical yearly moves (9.7 percent of solar MW requested a year, the median move between full years); the floor is 1.

**Its limits.** Berkeley Lab's Queued Up as the ERW holds it (CC BY 4.0, Lawrence Berkeley National Laboratory and GridTracker); a request's dates are those its transmission provider published, and some providers list no withdrawal date. A request counts as paired when Berkeley Lab lists a battery as its second or third type; its MW is the solar part.

**Reproduce.** `python hybrid-share-us-lbnl-hybrid.reproduce.py <the table's CSV>` and `do hybrid-share-us-lbnl-hybrid.reproduce.do` (Stata) recompute the figures by year from the tables as the public downloads hold them; each names the expected values at its top.
