# What a utility forecasts: summer peak growth: ERCOT (FERC 714 planning area 58)

Draft `scan-deep-65a2034813c5` of the findings hunt over the whole warehouse (chain 502), 2026-11-19. State: draft, not reviewed. Review at `/internal/findings`.

**The finding.** The yearly growth of its summer peak that ERCOT (FERC 714 planning area 58) forecast, from the first year of its filing to the tenth, was 5.56 percent a year in 2025, against 2.12 percent a year in 2006, the first filing the ERW holds.

![What a utility forecasts: summer peak growth, ERCOT (FERC 714 planning area 58)](summer-growth-pa-58.png)

**The figure by full year** (percent a year): 2006: 2.12, 2007: 1.83, 2008: 2.04, 2009: 1.73, 2010: 1.65, 2011: 2.51, 2012: 1.69, 2013: 1.31, 2014: 1.29, 2015: 1.08, 2016: 1.35, 2017: 1.71, 2018: 2.07, 2019: 1.64, 2020: 1.18, 2021: 1.15, 2022: 1.20, 2023: 1.68, 2024: 6.58, 2025: 5.56.

**The tables and rows.** `ferc714_planning_area_forecasts`; the rows for ERCOT (FERC 714 planning area 58), region key `pa_58` (the card's `hunt.region`), years 2006 to 2025. The yearly values: `summer-growth-pa-58.csv`.

**Its strength.** The change is 6.51 typical yearly moves (a typical move is 0.53 percent a year, 1.4826 times the median absolute change between full years). Holds in more than one year: 3 of the 19 full years after 2006 lie above 2006's value. Survives a change of window: from 2007 to 2025 the change is 3.74, from 2006 to 2024 it is 4.47. Sample large enough: 2006 holds 1 and 2025 holds 1 observations; the floor is 1. Half the change remains without the first year: from 2007 to 2025 the change is 3.74, 108.4 percent of the change from 2006. At least one typical yearly move: the change is 6.51 typical yearly moves (0.53 percent a year a year, the median move between full years); the floor is 1.

**Its limits.** The planning area's own forecast as filed in FERC Form 714 (through PUDL), not an outcome; a filing's ten years start the year after its report year; areas overlap, so nothing is added across them; a filing whose tenth year is over three times or under half its first is left out.

**Reproduce.** `python summer-growth-pa-58.reproduce.py <the table's CSV>` and `do summer-growth-pa-58.reproduce.do` (Stata) recompute the figures by year from the tables as the public downloads hold them; each names the expected values at its top.
