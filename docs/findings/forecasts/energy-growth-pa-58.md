# What a utility forecasts: net energy growth: ERCOT (FERC 714 planning area 58)

Draft `scan-deep-b47116558e70` of the findings hunt over the whole warehouse (chain 502), 2026-11-19. State: draft, not reviewed. Review at `/internal/findings`.

**The finding.** The yearly growth of its net energy that ERCOT (FERC 714 planning area 58) forecast, from the first year of its filing to the tenth, was 8.23 percent a year in 2025, against 2.10 percent a year in 2006, the first filing the ERW holds.

![What a utility forecasts: net energy growth, ERCOT (FERC 714 planning area 58)](energy-growth-pa-58.png)

**The figure by full year** (percent a year): 2006: 2.10, 2007: 1.81, 2008: 2.09, 2009: 1.73, 2010: 1.67, 2011: 2.48, 2012: 1.70, 2013: 1.78, 2014: 1.76, 2015: 1.41, 2016: 1.77, 2017: 2.31, 2018: 2.88, 2019: 2.32, 2020: 2.00, 2021: 1.92, 2022: 2.14, 2023: 2.62, 2024: 9.71, 2025: 8.23.

**The tables and rows.** `ferc714_planning_area_forecasts`; the rows for ERCOT (FERC 714 planning area 58), region key `pa_58` (the card's `hunt.region`), years 2006 to 2025. The yearly values: `energy-growth-pa-58.csv`.

**Its strength.** The change is 11.64 typical yearly moves (a typical move is 0.53 percent a year, 1.4826 times the median absolute change between full years). Holds in more than one year: 8 of the 19 full years after 2006 lie above 2006's value. Survives a change of window: from 2007 to 2025 the change is 6.42, from 2006 to 2024 it is 7.61. Sample large enough: 2006 holds 1 and 2025 holds 1 observations; the floor is 1. Half the change remains without the first year: from 2007 to 2025 the change is 6.42, 104.7 percent of the change from 2006. At least one typical yearly move: the change is 11.64 typical yearly moves (0.53 percent a year a year, the median move between full years); the floor is 1.

**Its limits.** The planning area's own forecast as filed in FERC Form 714 (through PUDL), not an outcome; a filing's ten years start the year after its report year; areas overlap, so nothing is added across them; a filing whose tenth year is over three times or under half its first is left out.

**Reproduce.** `python energy-growth-pa-58.reproduce.py <the table's CSV>` and `do energy-growth-pa-58.reproduce.do` (Stata) recompute the figures by year from the tables as the public downloads hold them; each names the expected values at its top.
