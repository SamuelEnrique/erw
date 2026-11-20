# Where power plants' coal comes from: coal from the Illinois Basin (EIA's mine basin)

Draft `scan-deep-e24be514fff5` of the findings hunt over the whole warehouse (chain 502), 2026-11-19. State: draft, not reviewed. Review at `/internal/findings`.

**The finding.** The share of coal from the Illinois Basin (EIA's mine basin) in the coal US power plants received was 14.1 percent in 2025, against 9.4 percent in 2008, the first full year the ERW holds.

![Where power plants' coal comes from, coal from the Illinois Basin (EIA's mine basin)](coal-basin-share-cb-illinois-basin.png)

**The figure by full year** (percent): 2008: 9.4, 2009: 9.8, 2010: 10.3, 2011: 11.0, 2012: 12.7, 2013: 14.0, 2014: 14.0, 2015: 14.4, 2016: 14.7, 2017: 13.9, 2018: 14.4, 2019: 14.4, 2020: 13.7, 2021: 13.2, 2022: 13.6, 2023: 14.4, 2024: 15.0, 2025: 14.1.

**The tables and rows.** `eia_coal_receipts_annual`; the rows for coal from the Illinois Basin (EIA's mine basin), region key `cb_illinois_basin` (the card's `hunt.region`), years 2008 to 2025. The yearly values: `coal-basin-share-cb-illinois-basin.csv`.

**Its strength.** The change is 5.87 typical yearly moves (a typical move is 0.8 percent, 1.4826 times the median absolute change between full years). Holds in more than one year: 17 of the 17 full years after 2008 lie above 2008's value. Survives a change of window: from 2009 to 2025 the change is 4.3, from 2008 to 2024 it is 5.6. Sample large enough: 2008 holds 1 and 2025 holds 1 observations; the floor is 1. Half the change remains without the first year: from 2009 to 2025 the change is 4.3, 91.3 percent of the change from 2008. At least one typical yearly move: the change is 5.87 typical yearly moves (0.8 percent a year, the median move between full years); the floor is 1.

**Its limits.** EIA's receipts of coal by power plants, mine to plant, as the table holds them; a share by tons, not by heat; shipments without a basin or mode are in the total only.

**Reproduce.** `python coal-basin-share-cb-illinois-basin.reproduce.py <the table's CSV>` and `do coal-basin-share-cb-illinois-basin.reproduce.do` (Stata) recompute the figures by year from the tables as the public downloads hold them; each names the expected values at its top.
