# Batteries in the queue: requests in the United States

Draft `scan-deep-1fd8bb1d1483` of the findings hunt over the whole warehouse (chain 164), 2026-11-06. State: draft, not reviewed. Review at `/internal/findings`.

**The finding.** Batteries' share of the MW requested in the United States was 29.7 percent of requested MW in 2024, against 0.0 percent of requested MW in 2005, the first year this measure counts.

![Batteries in the queue, requests in the United States](storage-share-us-req-battery-share.png)

**The figure by full year** (percent of requested MW): 2005: 0.0, 2006: 0.0, 2007: 0.0, 2008: 0.1, 2009: 0.1, 2010: 0.1, 2011: 0.0, 2012: 0.4, 2013: 0.3, 2014: 1.3, 2015: 4.1, 2016: 2.9, 2017: 1.8, 2018: 6.9, 2019: 12.7, 2020: 14.9, 2021: 26.8, 2022: 23.3, 2023: 29.8, 2024: 29.7.

**The tables and rows.** `lbnl_interconnection_queue`; the rows for requests in the United States, region key `us_req_battery_share` (the card's `hunt.region`), years 2005 to 2024. The yearly values: `storage-share-us-req-battery-share.csv`.

**Its strength.** The change is 19.14 typical yearly moves (a typical move is 1.6 percent of requested MW, 1.4826 times the median absolute change between full years). Holds in more than one year: 17 of the 19 full years after 2005 lie above 2005's value. Survives a change of window: from 2006 to 2024 the change is 29.7, from 2005 to 2023 it is 29.8. Sample large enough: 2005 holds 1 and 2024 holds 1 observations; the floor is 1. Half the change remains without the first year: from 2006 to 2024 the change is 29.7, 100.0 percent of the change from 2005. At least one typical yearly move: the change is 19.14 typical yearly moves (1.6 percent of requested MW a year, the median move between full years); the floor is 1.

**Its limits.** Berkeley Lab's Queued Up as the ERW holds it (CC BY 4.0, Lawrence Berkeley National Laboratory and GridTracker); a request's dates are those its transmission provider published, and some providers list no withdrawal date. Hybrids are counted by their first type, so batteries paired with solar are mostly counted as solar.

**Reproduce.** `python storage-share-us-req-battery-share.reproduce.py <the table's CSV>` and `do storage-share-us-req-battery-share.reproduce.do` (Stata) recompute the figures by year from the tables as the public downloads hold them; each names the expected values at its top.
