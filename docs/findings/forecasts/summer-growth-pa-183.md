# What a utility forecasts: summer peak growth: Georgia Power Company (FERC 714 planning area 183)

Draft `scan-deep-e117f130cc0c` of the findings hunt over the whole warehouse (chain 502), 2026-11-19. State: draft, not reviewed. Review at `/internal/findings`.

**The finding.** The yearly growth of its summer peak that Georgia Power Company (FERC 714 planning area 183) forecast, from the first year of its filing to the tenth, was 5.14 percent a year in 2025, against 2.07 percent a year in 2007, the first filing the ERW holds.

![What a utility forecasts: summer peak growth, Georgia Power Company (FERC 714 planning area 183)](summer-growth-pa-183.png)

**The figure by full year** (percent a year): 2007: 2.07, 2008: 2.18, 2009: 2.04, 2010: 1.55, 2011: 1.29, 2012: 1.69, 2013: 1.73, 2014: 1.61, 2015: 1.08, 2016: 0.81, 2017: 0.40, 2018: 0.41, 2019: 0.57, 2020: 0.37, 2021: 0.20, 2022: 0.83, 2023: 4.31, 2024: 4.97, 2025: 5.14.

**The tables and rows.** `ferc714_planning_area_forecasts`; the rows for Georgia Power Company (FERC 714 planning area 183), region key `pa_183` (the card's `hunt.region`), years 2007 to 2025. The yearly values: `summer-growth-pa-183.csv`.

**Its strength.** The change is 9.05 typical yearly moves (a typical move is 0.34 percent a year, 1.4826 times the median absolute change between full years). Holds in more than one year: 4 of the 18 full years after 2007 lie above 2007's value. Survives a change of window: from 2008 to 2025 the change is 2.96, from 2007 to 2024 it is 2.90. Sample large enough: 2007 holds 1 and 2025 holds 1 observations; the floor is 1. Half the change remains without the first year: from 2008 to 2025 the change is 2.96, 96.4 percent of the change from 2007. At least one typical yearly move: the change is 9.05 typical yearly moves (0.34 percent a year a year, the median move between full years); the floor is 1.

**Its limits.** The planning area's own forecast as filed in FERC Form 714 (through PUDL), not an outcome; a filing's ten years start the year after its report year; areas overlap, so nothing is added across them; a filing whose tenth year is over three times or under half its first is left out.

**Reproduce.** `python summer-growth-pa-183.reproduce.py <the table's CSV>` and `do summer-growth-pa-183.reproduce.do` (Stata) recompute the figures by year from the tables as the public downloads hold them; each names the expected values at its top.
