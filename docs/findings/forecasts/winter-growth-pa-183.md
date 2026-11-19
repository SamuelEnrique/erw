# What a utility forecasts: winter peak growth: Georgia Power Company (FERC 714 planning area 183)

Draft `scan-deep-c5a4b3e84189` of the findings hunt over the whole warehouse (chain 502), 2026-11-19. State: draft, not reviewed. Review at `/internal/findings`.

**The finding.** The yearly growth of its winter peak that Georgia Power Company (FERC 714 planning area 183) forecast, from the first year of its filing to the tenth, was 5.44 percent a year in 2025, against 2.02 percent a year in 2007, the first filing the ERW holds.

![What a utility forecasts: winter peak growth, Georgia Power Company (FERC 714 planning area 183)](winter-growth-pa-183.png)

**The figure by full year** (percent a year): 2007: 2.02, 2008: 2.03, 2009: 1.84, 2010: 1.69, 2011: 1.54, 2012: 1.58, 2013: 1.80, 2014: 1.65, 2015: 0.70, 2016: 0.40, 2017: 0.54, 2018: 0.49, 2019: 0.76, 2020: 0.42, 2021: 0.33, 2022: 1.00, 2023: 4.32, 2024: 5.10, 2025: 5.44.

**The tables and rows.** `ferc714_planning_area_forecasts`; the rows for Georgia Power Company (FERC 714 planning area 183), region key `pa_183` (the card's `hunt.region`), years 2007 to 2025. The yearly values: `winter-growth-pa-183.csv`.

**Its strength.** The change is 11.15 typical yearly moves (a typical move is 0.31 percent a year, 1.4826 times the median absolute change between full years). Holds in more than one year: 4 of the 18 full years after 2007 lie above 2007's value. Survives a change of window: from 2008 to 2025 the change is 3.42, from 2007 to 2024 it is 3.08. Sample large enough: 2007 holds 1 and 2025 holds 1 observations; the floor is 1. Half the change remains without the first year: from 2008 to 2025 the change is 3.42, 99.8 percent of the change from 2007. At least one typical yearly move: the change is 11.15 typical yearly moves (0.31 percent a year a year, the median move between full years); the floor is 1.

**Its limits.** The planning area's own forecast as filed in FERC Form 714 (through PUDL), not an outcome; a filing's ten years start the year after its report year; areas overlap, so nothing is added across them; a filing whose tenth year is over three times or under half its first is left out.

**Reproduce.** `python winter-growth-pa-183.reproduce.py <the table's CSV>` and `do winter-growth-pa-183.reproduce.do` (Stata) recompute the figures by year from the tables as the public downloads hold them; each names the expected values at its top.
