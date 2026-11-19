# What a region generates: solar: Arizona and New Mexico (the core of EIA's Southwest region)

Draft `scan-deep-0193ea025da7` of the findings hunt over the whole warehouse (chain 502), 2026-11-19. State: draft, not reviewed. Review at `/internal/findings`.

**The finding.** Utility-scale solar's share of the net generation of Arizona and New Mexico (the core of EIA's Southwest region) was 14.0 percent in 2025, against 0.0 percent in 2001, the first full year the ERW holds.

![What a region generates: solar, Arizona and New Mexico (the core of EIA's Southwest region)](solar-share-st-sw-sun.png)

**The figure by full year** (percent): 2001: 0.0, 2002: 0.0, 2003: 0.0, 2004: 0.0, 2005: 0.0, 2006: 0.0, 2007: 0.0, 2008: 0.0, 2009: 0.0, 2010: 0.0, 2011: 0.1, 2012: 0.9, 2013: 1.7, 2014: 2.5, 2015: 2.8, 2016: 3.2, 2017: 4.4, 2018: 4.5, 2019: 4.5, 2020: 5.3, 2021: 5.9, 2022: 6.2, 2023: 6.7, 2024: 9.7, 2025: 14.0.

**The tables and rows.** `eia_state_generation_monthly`; the rows for Arizona and New Mexico (the core of EIA's Southwest region), region key `st_sw_sun` (the card's `hunt.region`), years 2001 to 2025. The yearly values: `solar-share-st-sw-sun.csv`.

**Its strength.** The change is 48.30 typical yearly moves (a typical move is 0.3 percent, 1.4826 times the median absolute change between full years). Holds in more than one year: 22 of the 24 full years after 2001 lie above 2001's value. Survives a change of window: from 2002 to 2025 the change is 14.0, from 2001 to 2024 it is 9.7. Sample large enough: 2001 holds 12 and 2025 holds 12 observations; the floor is 12. Half the change remains without the first year: from 2002 to 2025 the change is 14.0, 100.0 percent of the change from 2001. At least one typical yearly move: the change is 48.30 typical yearly moves (0.3 percent a year, the median move between full years); the floor is 1.

**Its limits.** EIA's state net generation by fuel, all sectors; the states stand for the region and are not its footprint; the latest months are preliminary. Small rooftop systems are not in this figure.

**Reproduce.** `python solar-share-st-sw-sun.reproduce.py <the table's CSV>` and `do solar-share-st-sw-sun.reproduce.do` (Stata) recompute the figures by year from the tables as the public downloads hold them; each names the expected values at its top.
