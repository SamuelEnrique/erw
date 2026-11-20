# How coal reaches power plants: coal delivered by tramway or conveyor

Draft `scan-deep-d53eead8d129` of the findings hunt over the whole warehouse (chain 502), 2026-11-19. State: draft, not reviewed. Review at `/internal/findings`.

**The finding.** The share of coal delivered by tramway or conveyor in the coal US power plants received was 8.6 percent in 2025, against 6.9 percent in 2008, the first full year the ERW holds.

![How coal reaches power plants, coal delivered by tramway or conveyor](coal-mode-share-cm-tramway-conveyor.png)

**The figure by full year** (percent): 2008: 6.9, 2009: 5.9, 2010: 7.2, 2011: 7.1, 2012: 7.9, 2013: 9.1, 2014: 8.2, 2015: 9.2, 2016: 10.7, 2017: 10.2, 2018: 9.5, 2019: 9.1, 2020: 10.0, 2021: 10.3, 2022: 10.0, 2023: 9.0, 2024: 9.6, 2025: 8.6.

**The tables and rows.** `eia_coal_receipts_annual`; the rows for coal delivered by tramway or conveyor, region key `cm_tramway_conveyor` (the card's `hunt.region`), years 2008 to 2025. The yearly values: `coal-mode-share-cm-tramway-conveyor.csv`.

**Its strength.** The change is 1.29 typical yearly moves (a typical move is 1.3 percent, 1.4826 times the median absolute change between full years). Holds in more than one year: 16 of the 17 full years after 2008 lie above 2008's value. Survives a change of window: from 2009 to 2025 the change is 2.6, from 2008 to 2024 it is 2.7. Sample large enough: 2008 holds 1 and 2025 holds 1 observations; the floor is 1. Half the change remains without the first year: from 2009 to 2025 the change is 2.6, 155.1 percent of the change from 2008. At least one typical yearly move: the change is 1.29 typical yearly moves (1.3 percent a year, the median move between full years); the floor is 1.

**Its limits.** EIA's receipts of coal by power plants, mine to plant, as the table holds them; a share by tons, not by heat; shipments without a basin or mode are in the total only.

**Reproduce.** `python coal-mode-share-cm-tramway-conveyor.reproduce.py <the table's CSV>` and `do coal-mode-share-cm-tramway-conveyor.reproduce.do` (Stata) recompute the figures by year from the tables as the public downloads hold them; each names the expected values at its top.
