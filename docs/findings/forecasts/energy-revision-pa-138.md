# How a utility revises its forecast: net energy: Sierra Pacific Resources (FERC 714 planning area 138)

Draft `scan-deep-03ec44ef5f8b` of the findings hunt over the whole warehouse (chain 502), 2026-11-19. State: draft, not reviewed. Review at `/internal/findings`.

**The finding.** The revision Sierra Pacific Resources (FERC 714 planning area 138) made to its forecast of its net energy 5 years ahead, against its filing of the year before, was 66.8 percent in 2025, against 5.7 percent in 2007, the first filing that can be compared.

![How a utility revises its forecast: net energy, Sierra Pacific Resources (FERC 714 planning area 138)](energy-revision-pa-138.png)

**The figure by full year** (percent): 2007: 5.7, 2008: -11.9, 2009: -3.1, 2010: 0.0, 2011: 12.2, 2012: 6.6, 2013: -9.6, 2014: -1.5, 2015: -3.0, 2016: 5.2, 2017: 3.9, 2018: -16.1, 2019: 8.3, 2020: -1.0, 2021: 2.1, 2022: 1.2, 2023: 0.0, 2024: 40.7, 2025: 66.8.

**The tables and rows.** `ferc714_planning_area_forecasts`; the rows for Sierra Pacific Resources (FERC 714 planning area 138), region key `pa_138` (the card's `hunt.region`), years 2007 to 2025. The yearly values: `energy-revision-pa-138.csv`.

**Its strength.** The change is 4.85 typical yearly moves (a typical move is 12.6 percent, 1.4826 times the median absolute change between full years). Holds in more than one year: 5 of the 18 full years after 2007 lie above 2007's value. Survives a change of window: from 2008 to 2025 the change is 78.6, from 2007 to 2024 it is 35.0. Sample large enough: 2007 holds 1 and 2025 holds 1 observations; the floor is 1. Half the change remains without the first year: from 2008 to 2025 the change is 78.6, 128.7 percent of the change from 2007. At least one typical yearly move: the change is 4.85 typical yearly moves (12.6 percent a year, the median move between full years); the floor is 1.

**Its limits.** The planning area's own forecast as filed in FERC Form 714 (through PUDL): each filing against the one a year before, for the same year 5 years after the filing; a revision of more than double or less than half is left out (a figure in the wrong unit).

**Reproduce.** `python energy-revision-pa-138.reproduce.py <the table's CSV>` and `do energy-revision-pa-138.reproduce.do` (Stata) recompute the figures by year from the tables as the public downloads hold them; each names the expected values at its top.
