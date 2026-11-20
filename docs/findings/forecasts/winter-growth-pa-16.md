# What a utility forecasts: winter peak growth: Arizona Public Service Company (FERC 714 planning area 16)

Draft `scan-deep-43469004e647` of the findings hunt over the whole warehouse (chain 502), 2026-11-19. State: draft, not reviewed. Review at `/internal/findings`.

**The finding.** The yearly growth of its winter peak that Arizona Public Service Company (FERC 714 planning area 16) forecast, from the first year of its filing to the tenth, was 7.46 percent a year in 2025, against 3.26 percent a year in 2006, the first filing the ERW holds.

![What a utility forecasts: winter peak growth, Arizona Public Service Company (FERC 714 planning area 16)](winter-growth-pa-16.png)

**The figure by full year** (percent a year): 2006: 3.26, 2007: 2.59, 2008: 2.56, 2009: 1.52, 2010: 1.59, 2011: 2.10, 2012: 2.26, 2013: 2.56, 2014: 2.47, 2015: 1.73, 2016: 2.66, 2017: 2.49, 2018: 2.47, 2019: 3.33, 2020: 3.50, 2021: 2.64, 2022: 5.10, 2023: 5.24, 2024: 5.48, 2025: 7.46.

**The tables and rows.** `ferc714_planning_area_forecasts`; the rows for Arizona Public Service Company (FERC 714 planning area 16), region key `pa_16` (the card's `hunt.region`), years 2006 to 2025. The yearly values: `winter-growth-pa-16.csv`.

**Its strength.** The change is 9.47 typical yearly moves (a typical move is 0.44 percent a year, 1.4826 times the median absolute change between full years). Holds in more than one year: 6 of the 19 full years after 2006 lie above 2006's value. Survives a change of window: from 2007 to 2025 the change is 4.87, from 2006 to 2024 it is 2.22. Sample large enough: 2006 holds 1 and 2025 holds 1 observations; the floor is 1. Half the change remains without the first year: from 2007 to 2025 the change is 4.87, 116.1 percent of the change from 2006. At least one typical yearly move: the change is 9.47 typical yearly moves (0.44 percent a year a year, the median move between full years); the floor is 1.

**Its limits.** The planning area's own forecast as filed in FERC Form 714 (through PUDL), not an outcome; a filing's ten years start the year after its report year; areas overlap, so nothing is added across them; a filing whose tenth year is over three times or under half its first is left out.

**Reproduce.** `python winter-growth-pa-16.reproduce.py <the table's CSV>` and `do winter-growth-pa-16.reproduce.do` (Stata) recompute the figures by year from the tables as the public downloads hold them; each names the expected values at its top.
