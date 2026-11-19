# What a utility forecasts: winter peak growth: Sierra Pacific Resources (FERC 714 planning area 138)

Draft `scan-deep-e4e6ad904e51` of the findings hunt over the whole warehouse (chain 502), 2026-11-19. State: draft, not reviewed. Review at `/internal/findings`.

**The finding.** The yearly growth of its winter peak that Sierra Pacific Resources (FERC 714 planning area 138) forecast, from the first year of its filing to the tenth, was 5.88 percent a year in 2024, against 0.54 percent a year in 2006, the first filing the ERW holds.

![What a utility forecasts: winter peak growth, Sierra Pacific Resources (FERC 714 planning area 138)](winter-growth-pa-138.png)

**The figure by full year** (percent a year): 2006: 0.54, 2007: 1.19, 2008: 1.24, 2009: 0.58, 2010: -0.02, 2011: 0.53, 2012: 1.52, 2013: 1.21, 2014: 0.07, 2015: 0.49, 2016: 0.88, 2017: -0.03, 2018: 1.13, 2019: 1.82, 2020: 1.58, 2021: 3.32, 2022: 3.51, 2023: 2.63, 2024: 5.88.

**The tables and rows.** `ferc714_planning_area_forecasts`; the rows for Sierra Pacific Resources (FERC 714 planning area 138), region key `pa_138` (the card's `hunt.region`), years 2006 to 2024. The yearly values: `winter-growth-pa-138.csv`.

**Its strength.** The change is 5.51 typical yearly moves (a typical move is 0.97 percent a year, 1.4826 times the median absolute change between full years). Holds in more than one year: 13 of the 18 full years after 2006 lie above 2006's value. Survives a change of window: from 2007 to 2024 the change is 4.69, from 2006 to 2023 it is 2.10. Sample large enough: 2006 holds 1 and 2024 holds 1 observations; the floor is 1. Half the change remains without the first year: from 2007 to 2024 the change is 4.69, 87.8 percent of the change from 2006. At least one typical yearly move: the change is 5.51 typical yearly moves (0.97 percent a year a year, the median move between full years); the floor is 1.

**Its limits.** The planning area's own forecast as filed in FERC Form 714 (through PUDL), not an outcome; a filing's ten years start the year after its report year; areas overlap, so nothing is added across them; a filing whose tenth year is over three times or under half its first is left out.

**Reproduce.** `python winter-growth-pa-138.reproduce.py <the table's CSV>` and `do winter-growth-pa-138.reproduce.do` (Stata) recompute the figures by year from the tables as the public downloads hold them; each names the expected values at its top.
