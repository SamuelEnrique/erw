# Withdrawn, not built: PJM

Draft `scan-deep-93e08e83729d` of the findings hunt over the whole warehouse (chain 164), 2026-11-06. State: draft, not reviewed. Review at `/internal/findings`.

**The finding.** The share of the MW leaving the queue in PJM that was withdrawn rather than brought online was 93.4 percent of MW leaving the queue in 2024, against 72.1 percent of MW leaving the queue in 2005, the first year this measure counts.

![Withdrawn, not built, PJM](withdrawn-share-pjm-lbnl-wd.png)

**The figure by full year** (percent of MW leaving the queue): 2005: 72.1, 2006: 77.2, 2007: 89.7, 2008: 89.6, 2009: 95.5, 2010: 88.5, 2011: 74.5, 2012: 90.2, 2013: 97.1, 2014: 84.5, 2015: 77.9, 2016: 76.7, 2017: 73.8, 2018: 70.9, 2019: 88.5, 2020: 89.4, 2021: 77.9, 2022: 87.0, 2023: 82.6, 2024: 93.4.

**The tables and rows.** `lbnl_interconnection_queue`; the rows for PJM, region key `pjm_lbnl_wd` (the card's `hunt.region`), years 2005 to 2024. The yearly values: `withdrawn-share-pjm-lbnl-wd.csv`.

**Its strength.** The change is 2.07 typical yearly moves (a typical move is 10.3 percent of MW leaving the queue, 1.4826 times the median absolute change between full years). Holds in more than one year: 18 of the 19 full years after 2005 lie above 2005's value. Survives a change of window: from 2006 to 2024 the change is 16.2, from 2005 to 2023 it is 10.5. Sample large enough: 2005 holds 1 and 2024 holds 1 observations; the floor is 1. Half the change remains without the first year: from 2006 to 2024 the change is 16.2, 76.1 percent of the change from 2005. At least one typical yearly move: the change is 2.07 typical yearly moves (10.3 percent of MW leaving the queue a year, the median move between full years); the floor is 1.

**Its limits.** Berkeley Lab's Queued Up as the ERW holds it (CC BY 4.0, Lawrence Berkeley National Laboratory and GridTracker); a request's dates are those its transmission provider published, and some providers list no withdrawal date. A year's exits mix requests of many queue years; a year counts when both exits are held in it.

**Reproduce.** `python withdrawn-share-pjm-lbnl-wd.reproduce.py <the table's CSV>` and `do withdrawn-share-pjm-lbnl-wd.reproduce.do` (Stata) recompute the figures by year from the tables as the public downloads hold them; each names the expected values at its top.
