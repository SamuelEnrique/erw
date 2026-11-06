# The wait, by type: solar projects in the United States

Draft `scan-deep-1e1ec3f4c6cf` of the findings hunt over the whole warehouse (chain 164), 2026-11-06. State: draft, not reviewed. Review at `/internal/findings`.

**The finding.** The median months from interconnection request to commercial operation of solar projects in the United States was 69.8 months in 2024, against 22.2 months in 2011, the first year this measure counts.

![The wait, by type, solar projects in the United States](months-by-type-us-type-solar-months.png)

**The figure by full year** (months): 2011: 22.2, 2012: 26.0, 2013: 43.2, 2014: 52.7, 2015: 49.1, 2016: 60.5, 2017: 38.4, 2018: 47.6, 2019: 43.6, 2020: 41.9, 2021: 51.9, 2022: 58.8, 2023: 58.2, 2024: 69.8.

**The tables and rows.** `lbnl_interconnection_queue`; the rows for solar projects in the United States, region key `us_type_solar_months` (the card's `hunt.region`), years 2011 to 2024. The yearly values: `months-by-type-us-type-solar-months.csv`.

**Its strength.** The change is 3.52 typical yearly moves (a typical move is 13.5 months, 1.4826 times the median absolute change between full years). Holds in more than one year: 13 of the 13 full years after 2011 lie above 2011's value. Survives a change of window: from 2012 to 2024 the change is 43.8, from 2011 to 2023 it is 36.0. Sample large enough: 2011 holds 1 and 2024 holds 1 observations; the floor is 1. Half the change remains without the first year: from 2012 to 2024 the change is 43.8, 91.9 percent of the change from 2011. At least one typical yearly move: the change is 3.52 typical yearly moves (13.5 months a year, the median move between full years); the floor is 1.

**Its limits.** Berkeley Lab's Queued Up as the ERW holds it (CC BY 4.0, Lawrence Berkeley National Laboratory and GridTracker); a request's dates are those its transmission provider published, and some providers list no withdrawal date. Only projects that came online are in the median, a year needs at least ten of them, and a hybrid counts as its first type.

**Reproduce.** `python months-by-type-us-type-solar-months.reproduce.py <the table's CSV>` and `do months-by-type-us-type-solar-months.reproduce.do` (Stata) recompute the figures by year from the tables as the public downloads hold them; each names the expected values at its top.
