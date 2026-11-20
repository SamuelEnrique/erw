# How coal reaches power plants: coal delivered by truck

Draft `scan-deep-eae8b433cacc` of the findings hunt over the whole warehouse (chain 502), 2026-11-19. State: draft, not reviewed. Review at `/internal/findings`.

**The finding.** The share of coal delivered by truck in the coal US power plants received was 7.6 percent in 2025, against 9.9 percent in 2008, the first full year the ERW holds.

![How coal reaches power plants, coal delivered by truck](coal-mode-share-cm-truck.png)

**The figure by full year** (percent): 2008: 9.9, 2009: 12.8, 2010: 11.0, 2011: 9.4, 2012: 10.2, 2013: 10.4, 2014: 10.1, 2015: 9.2, 2016: 8.8, 2017: 8.5, 2018: 8.9, 2019: 9.2, 2020: 9.8, 2021: 9.2, 2022: 8.2, 2023: 6.1, 2024: 7.9, 2025: 7.6.

**The tables and rows.** `eia_coal_receipts_annual`; the rows for coal delivered by truck, region key `cm_truck` (the card's `hunt.region`), years 2008 to 2025. The yearly values: `coal-mode-share-cm-truck.csv`.

**Its strength.** The change is 2.37 typical yearly moves (a typical move is 1.0 percent, 1.4826 times the median absolute change between full years). Holds in more than one year: 12 of the 17 full years after 2008 lie below 2008's value. Survives a change of window: from 2009 to 2025 the change is -5.2, from 2008 to 2024 it is -2.0. Sample large enough: 2008 holds 1 and 2025 holds 1 observations; the floor is 1. Half the change remains without the first year: from 2009 to 2025 the change is -5.2, 225.3 percent of the change from 2008. At least one typical yearly move: the change is 2.37 typical yearly moves (1.0 percent a year, the median move between full years); the floor is 1.

**Its limits.** EIA's receipts of coal by power plants, mine to plant, as the table holds them; a share by tons, not by heat; shipments without a basin or mode are in the total only.

**Reproduce.** `python coal-mode-share-cm-truck.reproduce.py <the table's CSV>` and `do coal-mode-share-cm-truck.reproduce.do` (Stata) recompute the figures by year from the tables as the public downloads hold them; each names the expected values at its top.
