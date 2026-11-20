# How a utility revises its forecast: summer peak: Nevada Power Company (FERC 714 planning area 99)

Draft `scan-deep-5cc217621bd8` of the findings hunt over the whole warehouse (chain 502), 2026-11-19. State: draft, not reviewed. Review at `/internal/findings`.

**The finding.** The revision Nevada Power Company (FERC 714 planning area 99) made to its forecast of its summer peak 5 years ahead, against its filing of the year before, was 14.4 percent in 2025, against -0.5 percent in 2007, the first filing that can be compared.

![How a utility revises its forecast: summer peak, Nevada Power Company (FERC 714 planning area 99)](summer-revision-pa-99.png)

**The figure by full year** (percent): 2007: -0.5, 2008: -11.3, 2009: -10.9, 2010: 0.9, 2011: -3.4, 2012: -4.4, 2013: 0.0, 2014: -1.7, 2015: 0.0, 2016: 6.4, 2017: -3.3, 2018: 5.6, 2019: -1.5, 2020: -0.9, 2021: 3.0, 2022: -0.1, 2023: -0.0, 2024: 4.2, 2025: 14.4.

**The tables and rows.** `ferc714_planning_area_forecasts`; the rows for Nevada Power Company (FERC 714 planning area 99), region key `pa_99` (the card's `hunt.region`), years 2007 to 2025. The yearly values: `summer-revision-pa-99.csv`.

**Its strength.** The change is 2.35 typical yearly moves (a typical move is 6.3 percent, 1.4826 times the median absolute change between full years). Holds in more than one year: 10 of the 18 full years after 2007 lie above 2007's value. Survives a change of window: from 2008 to 2025 the change is 25.7, from 2007 to 2024 it is 4.7. Sample large enough: 2007 holds 1 and 2025 holds 1 observations; the floor is 1. Half the change remains without the first year: from 2008 to 2025 the change is 25.7, 173.0 percent of the change from 2007. At least one typical yearly move: the change is 2.35 typical yearly moves (6.3 percent a year, the median move between full years); the floor is 1.

**Its limits.** The planning area's own forecast as filed in FERC Form 714 (through PUDL): each filing against the one a year before, for the same year 5 years after the filing; a revision of more than double or less than half is left out (a figure in the wrong unit).

**Reproduce.** `python summer-revision-pa-99.reproduce.py <the table's CSV>` and `do summer-revision-pa-99.reproduce.do` (Stata) recompute the figures by year from the tables as the public downloads hold them; each names the expected values at its top.
