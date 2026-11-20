# What a utility forecasts: net energy growth: PJM Interconnection, LLC (FERC 714 planning area 119)

Draft `scan-deep-ffab0457b6e0` of the findings hunt over the whole warehouse (chain 502), 2026-11-19. State: draft, not reviewed. Review at `/internal/findings`.

**The finding.** The yearly growth of its net energy that PJM Interconnection, LLC (FERC 714 planning area 119) forecast, from the first year of its filing to the tenth, was 5.54 percent a year in 2025, against 1.54 percent a year in 2006, the first filing the ERW holds.

![What a utility forecasts: net energy growth, PJM Interconnection, LLC (FERC 714 planning area 119)](energy-growth-pa-119.png)

**The figure by full year** (percent a year): 2006: 1.54, 2007: 1.46, 2008: 1.71, 2009: 1.76, 2010: 2.22, 2011: 1.47, 2012: 1.46, 2013: 1.07, 2014: 0.96, 2015: 0.74, 2016: 0.23, 2017: 0.37, 2018: 0.44, 2019: 0.75, 2020: 0.34, 2021: 0.76, 2022: 1.53, 2023: 2.37, 2024: 5.12, 2025: 5.54.

**The tables and rows.** `ferc714_planning_area_forecasts`; the rows for PJM Interconnection, LLC (FERC 714 planning area 119), region key `pa_119` (the card's `hunt.region`), years 2006 to 2025. The yearly values: `energy-growth-pa-119.csv`.

**Its strength.** The change is 6.77 typical yearly moves (a typical move is 0.59 percent a year, 1.4826 times the median absolute change between full years). Holds in more than one year: 6 of the 19 full years after 2006 lie above 2006's value. Survives a change of window: from 2007 to 2025 the change is 4.08, from 2006 to 2024 it is 3.58. Sample large enough: 2006 holds 1 and 2025 holds 1 observations; the floor is 1. Half the change remains without the first year: from 2007 to 2025 the change is 4.08, 102.1 percent of the change from 2006. At least one typical yearly move: the change is 6.77 typical yearly moves (0.59 percent a year a year, the median move between full years); the floor is 1.

**Its limits.** The planning area's own forecast as filed in FERC Form 714 (through PUDL), not an outcome; a filing's ten years start the year after its report year; areas overlap, so nothing is added across them; a filing whose tenth year is over three times or under half its first is left out.

**Reproduce.** `python energy-growth-pa-119.reproduce.py <the table's CSV>` and `do energy-growth-pa-119.reproduce.do` (Stata) recompute the figures by year from the tables as the public downloads hold them; each names the expected values at its top.
