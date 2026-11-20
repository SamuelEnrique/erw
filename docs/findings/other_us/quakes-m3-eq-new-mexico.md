# Earthquakes in the oil and gas states: New Mexico

Draft `scan-deep-851387f08db6` of the findings hunt over the whole warehouse (chain 502), 2026-11-19. State: draft, not reviewed. Review at `/internal/findings`.

**The finding.** The count of earthquakes of magnitude 3 and above that USGS places in New Mexico was 83 earthquakes in 2025, against 5 earthquakes in 2010, the first full year the ERW holds.

![Earthquakes in the oil and gas states, New Mexico](quakes-m3-eq-new-mexico.png)

**The figure by full year** (earthquakes): 2010: 5, 2011: 3, 2012: 2, 2013: 4, 2014: 2, 2015: 7, 2016: 2, 2017: 3, 2018: 6, 2019: 7, 2020: 32, 2021: 122, 2022: 119, 2023: 96, 2024: 69, 2025: 83.

**The tables and rows.** `usgs_comcat_earthquakes_south_central`; the rows for New Mexico, region key `eq_new_mexico` (the card's `hunt.region`), years 2010 to 2025. The yearly values: `quakes-m3-eq-new-mexico.csv`.

**Its strength.** The change is 17.54 typical yearly moves (a typical move is 4 earthquakes, 1.4826 times the median absolute change between full years). Holds in more than one year: 9 of the 15 full years after 2010 lie above 2010's value. Survives a change of window: from 2011 to 2025 the change is 80, from 2010 to 2024 it is 64. Sample large enough: 2010 holds 1 and 2025 holds 1 observations; the floor is 1. Half the change remains without the first year: from 2011 to 2025 the change is 80, 102.6 percent of the change from 2010. At least one typical yearly move: the change is 17.54 typical yearly moves (4 earthquakes a year, the median move between full years); the floor is 1.

**Its limits.** USGS's ComCat as of 23 October 2026, magnitude 2.5 and above in the box of Oklahoma, Kansas, Texas and New Mexico, by the state the catalog's place names; a count, not a cause.

**Reproduce.** `python quakes-m3-eq-new-mexico.reproduce.py <the table's CSV>` and `do quakes-m3-eq-new-mexico.reproduce.do` (Stata) recompute the figures by year from the tables as the public downloads hold them; each names the expected values at its top.
